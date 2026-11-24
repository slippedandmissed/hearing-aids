//! Live mode: the default microphone through the chain to the default output, for listening to a profile.
//!
//! Wear HEADPHONES. With loudspeakers the sound feeds back into the microphone and howls (the limiter caps the
//! level, the system volume decides how loud that is). The delay of this path is not the delay of the real device:
//! it adds the audio drivers' buffers and two resampling filters.
use crate::resample::Stream;
use cpal::traits::{DeviceTrait, HostTrait, StreamTrait};
use cpal::{Error, ErrorKind};
use hearing_dsp::{Config, Ear, SAMPLE_RATE};
use std::collections::VecDeque;
use std::sync::{Arc, Mutex};
use std::time::{Duration, Instant};

/// Never let the playback queue hold more than this much audio: if the output falls behind, drop old samples.
const MAX_QUEUE_MS: f32 = 60.0;

#[derive(Default)]
struct Stats {
    in_sq: [f64; 2],
    in_n: u64,
    peak: [f32; 2],
    underruns: u32,
    dropped: u32,
}

struct Shared {
    /// Interleaved output frames waiting to be played.
    queue: VecDeque<f32>,
    stats: Stats,
}

fn err_fn(err: Error) {
    match err.kind() {
        ErrorKind::DeviceChanged | ErrorKind::Xrun | ErrorKind::RealtimeDenied => eprintln!("{err}"),
        _ => eprintln!("stream error: {err}"),
    }
}

pub fn run(cfg: &Config, seconds: f32, stereo_input: bool) -> Result<(), String> {
    let mut cfg = *cfg;
    // The loop through headphones is not the exciter-to-microphone path; the canceller has nothing to measure.
    cfg.feedback = hearing_dsp::FeedbackCfg::OFF;

    let host = cpal::default_host();
    let input = host.default_input_device().ok_or("no input device (is microphone access allowed for this terminal?)")?;
    let output = host.default_output_device().ok_or("no output device")?;
    let in_cfg = input.default_input_config().map_err(|e| format!("input device config: {e}"))?;
    let out_cfg = output.default_output_config().map_err(|e| format!("output device config: {e}"))?;
    let (in_conf, out_conf): (cpal::StreamConfig, cpal::StreamConfig) = (in_cfg.into(), out_cfg.into());
    let (in_ch, out_ch) = (in_conf.channels as usize, out_conf.channels as usize);
    let (in_rate, out_rate) = (in_conf.sample_rate as f32, out_conf.sample_rate as f32);
    println!("input : {} ({in_ch} ch, {in_rate} Hz)", input.id().map_err(|e| format!("input device id: {e}"))?);
    println!("output: {} ({out_ch} ch, {out_rate} Hz)", output.id().map_err(|e| format!("output device id: {e}"))?);
    println!(
        "ceiling {:.1} dBFS; band gains {:?} dB. WEAR HEADPHONES: loudspeakers will howl.",
        cfg.limit_dbfs,
        cfg.bands.map(|b| b.gain_db)
    );

    let shared = Arc::new(Mutex::new(Shared { queue: VecDeque::new(), stats: Stats::default() }));
    let max_queue = (MAX_QUEUE_MS * 1e-3 * out_rate) as usize * out_ch;

    let mut ears = [Ear::new(&cfg), Ear::new(&cfg.for_right_ear())];
    let mut down = [Stream::new(in_rate, SAMPLE_RATE), Stream::new(in_rate, SAMPLE_RATE)];
    let mut up = [Stream::new(SAMPLE_RATE, out_rate), Stream::new(SAMPLE_RATE, out_rate)];
    println!(
        "resampling adds about {:.1} ms (in) + {:.1} ms (out), not present on the device",
        down[0].delay_ms(),
        up[0].delay_ms()
    );

    let sh_in = Arc::clone(&shared);
    let mut chan = [Vec::new(), Vec::new()];
    let (mut dsp_in, mut dsp_out) = ([Vec::new(), Vec::new()], [Vec::new(), Vec::new()]);
    let (mut play, mut play_r) = (Vec::new(), Vec::new());
    let input_stream = input
        .build_input_stream::<f32, _, _>(
            in_conf,
            move |data: &[f32], _| {
                // Ear L = channel 0; ear R = channel 1 if asked for and present, else the same microphone.
                for c in 0..2 {
                    let src = if stereo_input && in_ch > 1 { c } else { 0 };
                    chan[c].clear();
                    chan[c].extend(data.chunks(in_ch).map(|f| f[src]));
                    dsp_in[c].clear();
                    down[c].push(&chan[c], &mut dsp_in[c]);
                    dsp_out[c].clear();
                    dsp_out[c].resize(dsp_in[c].len(), 0.0);
                    ears[c].process(&dsp_in[c], &mut dsp_out[c]);
                }
                play.clear();
                play_r.clear();
                up[0].push(&dsp_out[0], &mut play);
                up[1].push(&dsp_out[1], &mut play_r);
                let n = play.len().min(play_r.len());
                let mut sh = sh_in.lock().unwrap();
                for c in 0..2 {
                    sh.stats.in_sq[c] += dsp_in[c].iter().map(|x| (*x as f64).powi(2)).sum::<f64>();
                    sh.stats.peak[c] = dsp_out[c].iter().fold(sh.stats.peak[c], |m, y| m.max(y.abs()));
                }
                sh.stats.in_n += dsp_in[0].len() as u64;
                for i in 0..n {
                    for ch in 0..out_ch {
                        sh.queue.push_back(match (out_ch, ch) {
                            (1, _) => 0.5 * (play[i] + play_r[i]),
                            (_, 0) => play[i],
                            (_, 1) => play_r[i],
                            _ => 0.0,
                        });
                    }
                }
                while sh.queue.len() > max_queue {
                    sh.queue.pop_front();
                    sh.stats.dropped += 1;
                }
            },
            err_fn,
            None,
        )
        .map_err(|e| format!("opening the input stream: {e}"))?;

    let sh_out = Arc::clone(&shared);
    let output_stream = output
        .build_output_stream::<f32, _, _>(
            out_conf,
            move |data: &mut [f32], _| {
                let mut sh = sh_out.lock().unwrap();
                let mut short = false;
                for s in data.iter_mut() {
                    match sh.queue.pop_front() {
                        Some(v) => *s = v,
                        None => {
                            *s = 0.0;
                            short = true;
                        }
                    }
                }
                if short {
                    sh.stats.underruns += 1;
                }
            },
            err_fn,
            None,
        )
        .map_err(|e| format!("opening the output stream: {e}"))?;

    input_stream.play().map_err(|e| format!("starting the input: {e}"))?;
    output_stream.play().map_err(|e| format!("starting the output: {e}"))?;
    println!("running{} (Ctrl-C to stop); levels are per second, dBFS", if seconds > 0.0 { format!(" for {seconds} s") } else { String::new() });

    let start = Instant::now();
    let dbfs = |p: f64| 10.0 * p.max(1e-12).log10();
    loop {
        std::thread::sleep(Duration::from_secs(1));
        let mut sh = shared.lock().unwrap();
        let n = sh.stats.in_n.max(1) as f64;
        println!(
            "in L {:6.1} R {:6.1} rms | out peak L {:6.1} R {:6.1} | underruns {} dropped {}",
            dbfs(sh.stats.in_sq[0] / n),
            dbfs(sh.stats.in_sq[1] / n),
            20.0 * (sh.stats.peak[0] as f64).max(1e-6).log10(),
            20.0 * (sh.stats.peak[1] as f64).max(1e-6).log10(),
            sh.stats.underruns,
            sh.stats.dropped
        );
        sh.stats = Stats { underruns: sh.stats.underruns, dropped: sh.stats.dropped, ..Stats::default() };
        if seconds > 0.0 && start.elapsed().as_secs_f32() >= seconds {
            break;
        }
    }
    Ok(())
}

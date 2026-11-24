//! Run the hearing-dsp chain over a WAV file, the same way the XIAO firmware runs it over the microphones.
//!
//! usage:
//!   hearing-desktop process IN.wav OUT.wav [--preset passthrough|conductive] [--gain-db DB] [--limit-dbfs DB]
//!   hearing-desktop feedback [--scenario damped|ringy] [--coupling-db DB] [--input noise|voiced] [--taps N --delay N --mu X]
//!   hearing-desktop live [--seconds N] [--stereo-input] [options]   (microphone to headphones; WEAR HEADPHONES)
//!   hearing-desktop profile [--preset NAME | --profile FILE]     (prints every setting as TOML)
//!   hearing-desktop latency [--preset passthrough|conductive]
//!   hearing-desktop response [--preset passthrough|conductive] [--gain-db DB] [--limit-dbfs DB]
//!
//! Wherever a preset is accepted, `--profile FILE.toml` (see `profiles/device.toml`) works too.
//! `--gain-db` is added to every band. `response` prints the gain of the chain for sine tones at several levels.
//!
//! The input is resampled to the device rate (16.129 kHz), mono is duplicated to both ears, the chain runs in
//! 16-frame blocks like the firmware, and the output is a 16-bit stereo WAV at the device rate.
mod feedback_sim;
mod latency;
mod live;
mod resample;
mod response;

use hearing_dsp::{Config, Ear, SAMPLE_RATE, from_i16, to_i16};
use std::process::ExitCode;

/// Frames per block; matches the firmware (about 1 ms).
const BLOCK: usize = 16;

fn read_wav(path: &str) -> Result<(Vec<Vec<f32>>, f32), String> {
    let mut r = hound::WavReader::open(path).map_err(|e| format!("{path}: {e}"))?;
    let spec = r.spec();
    let ch = spec.channels as usize;
    let interleaved: Vec<f32> = match (spec.sample_format, spec.bits_per_sample) {
        (hound::SampleFormat::Float, _) => r.samples::<f32>().collect::<Result<_, _>>(),
        (hound::SampleFormat::Int, b) if b <= 16 => r
            .samples::<i16>()
            .map(|s| s.map(|s| s as f32 / (1i32 << (b - 1)) as f32))
            .collect::<Result<_, _>>(),
        (hound::SampleFormat::Int, b) => r
            .samples::<i32>()
            .map(|s| s.map(|s| s as f32 / (1i64 << (b - 1)) as f32))
            .collect::<Result<_, _>>(),
    }
    .map_err(|e| format!("{path}: {e}"))?;
    if ch == 0 || ch > 2 {
        return Err(format!("{path}: need a mono or stereo file, got {ch} channels"));
    }
    let mut chans = vec![Vec::with_capacity(interleaved.len() / ch); ch];
    for (i, s) in interleaved.into_iter().enumerate() {
        chans[i % ch].push(s);
    }
    Ok((chans, spec.sample_rate as f32))
}

const USAGE: &str = "usage: hearing-desktop process IN.wav OUT.wav [options] | hearing-desktop response [options] | hearing-desktop feedback [options] | hearing-desktop latency [options] | hearing-desktop profile [options] | hearing-desktop live [options]\n\
options: --preset passthrough|conductive | --profile FILE.toml  --gain-db DB (added to every band)  --limit-dbfs DB";

fn parse_options(args: &[String]) -> Result<Config, String> {
    parse_options_with(args, &mut |_, _| Ok(false))
}

/// `extra` gets first refusal on each flag (and the iterator, to take its value): `Ok(true)` if it used the flag.
fn parse_options_with(
    args: &[String],
    extra: &mut dyn FnMut(&str, &mut std::slice::Iter<String>) -> Result<bool, String>,
) -> Result<Config, String> {
    let (mut cfg, mut gain_offset, mut limit) = (Config::PASSTHROUGH, 0.0, None);
    let mut it = args.iter();
    while let Some(flag) = it.next() {
        if extra(flag, &mut it)? {
            continue;
        }
        let mut value = || it.next().ok_or(format!("{flag} needs a value"));
        match flag.as_str() {
            "--preset" => cfg = hearing_profile::preset(value()?)?,
            "--profile" => cfg = hearing_profile::load(value()?)?,
            "--gain-db" => gain_offset = value()?.parse::<f32>().map_err(|e| format!("--gain-db: {e}"))?,
            "--limit-dbfs" => limit = Some(value()?.parse::<f32>().map_err(|e| format!("--limit-dbfs: {e}"))?),
            other => return Err(format!("unknown option {other:?}")),
        }
    }
    for b in &mut cfg.bands {
        b.gain_db += gain_offset;
    }
    // A WAV file has no exciter-to-microphone loop, so a canceller would only have its own calibration noise to
    // listen to. (`hearing-desktop feedback` is where the canceller is exercised.)
    cfg.feedback = hearing_dsp::FeedbackCfg::OFF;
    if let Some(l) = limit {
        cfg.limit_dbfs = l;
    }
    Ok(cfg)
}

fn run(args: &[String]) -> Result<(), String> {
    match args {
        [cmd, rest @ ..] if cmd == "live" => {
            let (mut seconds, mut stereo) = (0.0f32, false);
            let cfg = parse_options_with(rest, &mut |flag, it| match flag {
                "--seconds" => {
                    seconds = it.next().and_then(|v| v.parse().ok()).ok_or("--seconds needs a number")?;
                    Ok(true)
                }
                "--stereo-input" => {
                    stereo = true;
                    Ok(true)
                }
                _ => Ok(false),
            })?;
            live::run(&cfg, seconds, stereo)
        }
        [cmd, rest @ ..] if cmd == "profile" => hearing_profile::to_toml(&parse_options(rest)?).map(|t| print!("{t}")),
        [cmd, rest @ ..] if cmd == "latency" => latency::print(&parse_options(rest)?),
        [cmd, rest @ ..] if cmd == "feedback" => feedback_sim::report(rest),
        [cmd, rest @ ..] if cmd == "response" => response::print(&parse_options(rest)?),
        [cmd, input, output, rest @ ..] if cmd == "process" => process(input, output, &parse_options(rest)?),
        _ => Err(USAGE.into()),
    }
}

fn process(input: &str, output: &str, cfg: &Config) -> Result<(), String> {
    let cfg = *cfg;
    let (chans, rate) = read_wav(input)?;
    let left = resample::to_rate(&chans[0], rate, SAMPLE_RATE);
    let right = if chans.len() > 1 { resample::to_rate(&chans[1], rate, SAMPLE_RATE) } else { left.clone() };

    // Quantise to i16 first, exactly what the PDM peripheral hands the firmware.
    let quant = |v: &[f32]| -> Vec<f32> { v.iter().map(|&x| from_i16(to_i16(x))).collect() };
    let (left, right) = (quant(&left), quant(&right));

    let (mut ears, mut peak) = ([Ear::new(&cfg), Ear::new(&cfg.for_right_ear())], [0.0f32; 2]);
    let spec = hound::WavSpec {
        channels: 2,
        sample_rate: SAMPLE_RATE.round() as u32,
        bits_per_sample: 16,
        sample_format: hound::SampleFormat::Int,
    };
    let mut w = hound::WavWriter::create(output, spec).map_err(|e| format!("{output}: {e}"))?;
    let mut out = [[0.0f32; BLOCK]; 2];
    for (l, r) in left.chunks(BLOCK).zip(right.chunks(BLOCK)) {
        let len = l.len();
        ears[0].process(l, &mut out[0][..len]);
        ears[1].process(r, &mut out[1][..len]);
        for i in 0..len {
            for c in 0..2 {
                peak[c] = peak[c].max(out[c][i].abs());
                w.write_sample(to_i16(out[c][i])).map_err(|e| e.to_string())?;
            }
        }
    }
    w.finalize().map_err(|e| e.to_string())?;
    let dbfs = |p: f32| 20.0 * p.max(1e-9).log10();
    let pct = |e: &Ear| 100.0 * e.limiter_engaged() as f32 / left.len().max(1) as f32;
    println!(
        "{input} ({rate} Hz) -> {output} ({} Hz): {} frames, peak L {:.1} dBFS, R {:.1} dBFS, ceiling {:.1} dBFS; \
         limiter knee reached on {:.1}% (L) and {:.1}% (R) of samples",
        spec.sample_rate,
        left.len(),
        dbfs(peak[0]),
        dbfs(peak[1]),
        cfg.limit_dbfs,
        pct(&ears[0]),
        pct(&ears[1])
    );
    Ok(())
}

fn main() -> ExitCode {
    let args: Vec<String> = std::env::args().skip(1).collect();
    match run(&args) {
        Ok(()) => ExitCode::SUCCESS,
        Err(e) => {
            eprintln!("error: {e}");
            ExitCode::FAILURE
        }
    }
}

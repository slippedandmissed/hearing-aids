//! Closed-loop feedback simulator: the real `hearing-dsp` chain with a synthetic exciter-to-microphone path
//! around it. The true path is unknown until there is hardware, so this measures how much the canceller helps
//! for assumed paths, not what the hardware does.
use hearing_dsp::{Biquad, Config, Ear, FeedbackCfg, SAMPLE_RATE};
use std::f32::consts::PI;

/// An assumed path from the exciter to the microphone.
#[derive(Debug, Clone, Copy)]
pub struct Scenario {
    pub name: &'static str,
    /// Pure delay in samples between the output and the first arrival at the microphone (buffering + decimation).
    pub delay: usize,
    /// Structural resonances as (Hz, Q, weight).
    pub modes: &'static [(f32, f32, f32)],
    /// Weight of a broad low-pass component (direct coupling through the earring).
    pub direct: f32,
}

pub const SCENARIOS: [Scenario; 2] = [
    Scenario { name: "damped", delay: 24, modes: &[(1200.0, 2.0, 1.0), (2600.0, 3.0, 0.6)], direct: 0.5 },
    Scenario { name: "ringy", delay: 24, modes: &[(1200.0, 8.0, 1.0), (2600.0, 8.0, 0.7), (4100.0, 10.0, 0.5)], direct: 0.3 },
];

pub const PATH_LEN: usize = 512;

/// The path's impulse response, scaled so its peak magnitude over 100 Hz..7 kHz is `peak_db`.
pub fn path_fir(s: &Scenario, peak_db: f32) -> Vec<f32> {
    let mut modes: Vec<Biquad> = s.modes.iter().map(|&(f, q, _)| Biquad::bandpass(f, q)).collect();
    let mut direct = Biquad::lowpass(1500.0, 0.707);
    let mut h = vec![0.0f32; PATH_LEN];
    for i in 0..PATH_LEN {
        let x = if i == s.delay { 1.0 } else { 0.0 };
        let mut y = s.direct * direct.process(x);
        for (m, &(_, _, w)) in modes.iter_mut().zip(s.modes) {
            y += w * m.process(x);
        }
        h[i] = y;
    }
    let peak = (0..200)
        .map(|k| {
            let w = 2.0 * PI * (100.0 + 6900.0 * k as f32 / 199.0) / SAMPLE_RATE;
            let (re, im) = h.iter().enumerate().fold((0.0, 0.0), |(re, im), (n, v)| {
                (re + v * (w * n as f32).cos(), im - v * (w * n as f32).sin())
            });
            (re * re + im * im).sqrt()
        })
        .fold(0.0f32, f32::max);
    let scale = 10f32.powf(peak_db / 20.0) / peak;
    h.iter().map(|v| v * scale).collect()
}

/// Deterministic noise source.
pub struct Rng(u32);
impl Rng {
    pub fn new(seed: u32) -> Self {
        Self(seed.max(1))
    }
    /// Uniform in -1..1.
    pub fn next(&mut self) -> f32 {
        self.0 ^= self.0 << 13;
        self.0 ^= self.0 >> 17;
        self.0 ^= self.0 << 5;
        (self.0 as f32 / u32::MAX as f32) * 2.0 - 1.0
    }
    /// Roughly Gaussian (sum of four uniforms), unit variance.
    pub fn gauss(&mut self) -> f32 {
        (self.next() + self.next() + self.next() + self.next()) * (3.0f32).sqrt() / 2.0
    }
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum Input {
    /// Broadband noise (a quiet room).
    Noise,
    /// Voiced, speech-like: harmonics of a wandering 100-140 Hz pitch under a 4 Hz syllable envelope.
    Voiced,
}

/// Scales the voiced waveform to unit long-term RMS (measured, see the `sources_have_the_requested_level` test).
const VOICED_NORM: f32 = 1.16;

pub struct Source {
    kind: Input,
    amp: f32,
    rng: Rng,
    phase: f32,
    t: usize,
}

impl Source {
    /// `rms_dbfs` is the long-term RMS level.
    pub fn new(kind: Input, rms_dbfs: f32) -> Self {
        Self { kind, amp: 10f32.powf(rms_dbfs / 20.0), rng: Rng::new(12345), phase: 0.0, t: 0 }
    }

    pub fn next(&mut self) -> f32 {
        self.t += 1;
        match self.kind {
            Input::Noise => self.amp * self.rng.gauss(),
            Input::Voiced => {
                let t = self.t as f32 / SAMPLE_RATE;
                let f0 = 120.0 + 20.0 * (2.0 * PI * 0.7 * t).sin();
                self.phase = (self.phase + f0 / SAMPLE_RATE).fract();
                let env = 0.5 + 0.5 * (2.0 * PI * 4.0 * t).sin().max(-0.2);
                // 30 harmonics up to f0 * 30 < Nyquist; spectral tilt 1/h with two formant bumps.
                let mut s = 0.0;
                for h in 1..=30 {
                    let f = f0 * h as f32;
                    if f > SAMPLE_RATE * 0.45 {
                        break;
                    }
                    let formant = 1.0 + 3.0 * (-((f - 700.0) / 250.0).powi(2)).exp() + 2.0 * (-((f - 1800.0) / 400.0).powi(2)).exp();
                    s += formant / h as f32 * (2.0 * PI * self.phase * h as f32).sin();
                }
                self.amp * env * s * VOICED_NORM
            }
        }
    }
}

/// The chain under test, with the synthetic path closing the loop.
pub struct Rig {
    pub ear: Ear,
    path: Vec<f32>,
    /// `hist[k]` is the output `k + 1` samples ago.
    hist: Vec<f32>,
}

impl Rig {
    pub fn new(cfg: &Config, path: Vec<f32>) -> Self {
        let n = path.len();
        Self { ear: Ear::new(cfg), path, hist: vec![0.0; n] }
    }

    /// One sample: the outside sound plus the feedback of the recent output goes in, the new output comes out.
    pub fn step(&mut self, outside: f32) -> f32 {
        let fb: f32 = self.hist.iter().zip(&self.path).map(|(o, h)| o * h).sum();
        let mut y = [0.0f32];
        self.ear.process(&[outside + fb], &mut y);
        self.hist.rotate_right(1);
        self.hist[0] = y[0];
        y[0]
    }

    pub fn set_path(&mut self, path: Vec<f32>) {
        self.path = path;
    }
}

/// How far the canceller's estimate is from the true path, dB (energy of the difference over energy of the path
/// inside the window the canceller covers; lower is better, 0 dB means no better than an empty filter).
pub fn misalignment_db(ear: &Ear, path: &[f32]) -> f32 {
    let (w, delay) = ear.feedback_path();
    if w.is_empty() {
        return 0.0;
    }
    // +1: the filter's tap 0 is the output `delay + 1` samples back, which is `path[delay]`.
    let (mut err, mut tot) = (0.0f32, 0.0f32);
    for (k, wk) in w.iter().enumerate() {
        let h = path.get(delay + k).copied().unwrap_or(0.0);
        err += (wk - h) * (wk - h);
        tot += h * h;
    }
    10.0 * (err.max(1e-30) / tot.max(1e-30)).log10()
}

fn rms_db(v: &[f32]) -> f32 {
    10.0 * (v.iter().map(|x| x * x).sum::<f32>() / v.len().max(1) as f32).max(1e-20).log10()
}

/// A linear (no compression) chain at `gain_db` in every band, limiter out of the way, with the given canceller.
pub fn linear_config(gain_db: f32, feedback: FeedbackCfg) -> Config {
    let mut c = Config::PASSTHROUGH;
    for b in &mut c.bands {
        b.gain_db = gain_db;
    }
    c.limit_dbfs = 0.0;
    c.fade_in_ms = 0.0;
    c.feedback = feedback;
    c
}

pub const SIM_SECONDS: f32 = 12.0;
/// Input level of the quiet room (RMS, dBFS) that excites the canceller.
pub const INPUT_DBFS: f32 = -70.0;

/// What the loop is fed and what path it sits in.
#[derive(Clone, Copy)]
pub struct Trial<'a> {
    pub path: &'a [f32],
    /// If set, the path changes to this one half way through (a hand on the glasses, the arm shifting).
    pub drift: Option<&'a [f32]>,
    pub input: Input,
    pub in_dbfs: f32,
}

pub struct Outcome {
    /// Output RMS over the last two seconds, dB.
    pub tail_db: f32,
    /// Misalignment at the end (see `misalignment_db`), measured against the path in force at the end.
    pub misalignment_db: f32,
}

pub fn run(cfg: &Config, t: &Trial) -> Outcome {
    let n = (SIM_SECONDS * SAMPLE_RATE) as usize;
    let mut rig = Rig::new(cfg, t.path.to_vec());
    let mut src = Source::new(t.input, t.in_dbfs);
    let mut tail = Vec::new();
    for i in 0..n {
        if i == n / 2 {
            if let Some(d) = t.drift {
                rig.set_path(d.to_vec());
            }
        }
        let y = rig.step(src.next());
        if i >= n - 2 * SAMPLE_RATE as usize {
            tail.push(y);
        }
    }
    let end_path = t.drift.unwrap_or(t.path);
    Outcome { tail_db: rms_db(&tail), misalignment_db: misalignment_db(&rig.ear, end_path) }
}

/// How faithfully the loop reproduces the wanted sound: the output of the no-feedback chain (the ideal) against the
/// output of the closed loop with this canceller, as signal-to-error in dB over the last two seconds. Higher is
/// better; 20 dB means the loop's output differs from the ideal by 10 % in amplitude.
pub fn fidelity_db(gain_db: f32, fb: FeedbackCfg, t: &Trial) -> f32 {
    let n = (SIM_SECONDS * SAMPLE_RATE) as usize;
    let tail = n - 2 * SAMPLE_RATE as usize;
    let mut ideal = Rig::new(&linear_config(gain_db, FeedbackCfg::OFF), vec![0.0; t.path.len()]);
    let mut real = Rig::new(&linear_config(gain_db, fb), t.path.to_vec());
    let mut src = Source::new(t.input, t.in_dbfs);
    let (mut sig, mut err) = (0.0f64, 0.0f64);
    for i in 0..n {
        if i == n / 2 {
            if let Some(d) = t.drift {
                real.set_path(d.to_vec());
            }
        }
        let x = src.next();
        let (a, b) = (ideal.step(x), real.step(x));
        if i >= tail {
            sig += (a * a) as f64;
            err += ((a - b) * (a - b)) as f64;
        }
    }
    10.0 * (sig / err.max(1e-30)).log10() as f32
}

/// The highest whole-dB gain at which the loop's output stays within `margin_db` of what it would be with no
/// feedback at all. Returns `max_db` if it never howls within the sweep.
pub fn max_stable_gain(fb: FeedbackCfg, t: &Trial, max_db: i32, margin_db: f32) -> i32 {
    let none = Trial { path: &vec![0.0; t.path.len()], drift: None, ..*t };
    let mut best = 0;
    for g in 0..=max_db {
        let g = g as f32;
        let open = run(&linear_config(g, FeedbackCfg::OFF), &none).tail_db;
        let closed = run(&linear_config(g, fb), t).tail_db;
        if closed - open > margin_db {
            return best;
        }
        best = g as i32;
    }
    max_db
}

/// The scenario with every resonance moved 7 % up, one more sample of delay and 3 dB more coupling: a plausible
/// shift when the arm is pressed harder or the glasses slip.
pub fn drifted(s: &Scenario, peak_db: f32) -> Vec<f32> {
    let modes: &'static [(f32, f32, f32)] = Box::leak(s.modes.iter().map(|&(f, q, w)| (f * 1.07, q, w)).collect::<Vec<_>>().into_boxed_slice());
    path_fir(&Scenario { delay: s.delay + 1, modes, ..*s }, peak_db + 3.0)
}

const FEEDBACK_USAGE: &str = "usage: hearing-desktop feedback [--scenario damped|ringy] [--coupling-db DB] [--input noise|voiced] [--drift]\n\
       [--taps N] [--delay N] [--mu X] [--cal-ms X] [--mu-cal X] [--leak X] [--max-db N] [--margin-db X]\n\
Finds the highest chain gain before the loop howls, without and with the canceller.";

/// The canceller settings the simulator uses unless told otherwise.
pub const DEFAULT_FB: FeedbackCfg =
    FeedbackCfg { taps: 64, delay: 16, mu: 0.002, calibrate_ms: 3000.0, mu_cal: 0.05, probe_dbfs: -40.0, leak: 0.001, seed: 99 };

/// `hearing-desktop feedback ...`
pub fn report(args: &[String]) -> Result<(), String> {
    let (mut scenario, mut coupling, mut input, mut drift) = (SCENARIOS[0], -30.0f32, Input::Noise, false);
    let (mut fb, mut max_db, mut margin) = (DEFAULT_FB, 60, 3.0f32);
    let mut it = args.iter();
    while let Some(flag) = it.next() {
        if flag == "--drift" {
            drift = true;
            continue;
        }
        let mut v = || it.next().ok_or(format!("{flag} needs a value\n{FEEDBACK_USAGE}"));
        let num = |s: &String| s.parse::<f32>().map_err(|e| format!("{flag}: {e}"));
        match flag.as_str() {
            "--scenario" => {
                let name = v()?;
                scenario = *SCENARIOS.iter().find(|s| s.name == name).ok_or(format!("unknown scenario {name:?}"))?;
            }
            "--coupling-db" => coupling = num(v()?)?,
            "--input" => {
                input = match v()?.as_str() {
                    "noise" => Input::Noise,
                    "voiced" => Input::Voiced,
                    other => return Err(format!("unknown input {other:?}")),
                }
            }
            "--taps" => fb.taps = num(v()?)? as usize,
            "--delay" => fb.delay = num(v()?)? as usize,
            "--mu" => fb.mu = num(v()?)?,
            "--cal-ms" => fb.calibrate_ms = num(v()?)?,
            "--mu-cal" => fb.mu_cal = num(v()?)?,
            "--leak" => fb.leak = num(v()?)?,
            "--max-db" => max_db = num(v()?)? as i32,
            "--margin-db" => margin = num(v()?)?,
            _ => return Err(FEEDBACK_USAGE.into()),
        }
    }
    let path = path_fir(&scenario, coupling);
    let drift_path = drift.then(|| drifted(&scenario, coupling));
    let trial = Trial { path: &path, drift: drift_path.as_deref(), input, in_dbfs: INPUT_DBFS };
    println!(
        "path '{}': delay {} samples ({:.1} ms), peak coupling {coupling:.0} dB, so about {:.0} dB of gain is the theoretical limit{}",
        scenario.name,
        scenario.delay,
        1000.0 * scenario.delay as f32 / SAMPLE_RATE,
        -coupling,
        if drift { "; the path drifts half way (+3 dB, resonances +7 %, +1 sample)" } else { "" }
    );
    println!("input: {input:?} at {INPUT_DBFS:.0} dBFS RMS, {SIM_SECONDS:.0} s per run, howl = output {margin:.0} dB above the no-feedback output");
    let g0 = max_stable_gain(FeedbackCfg::OFF, &trial, max_db, margin);
    let g1 = max_stable_gain(fb, &trial, max_db, margin);
    let mis = run(&linear_config(g1 as f32, fb), &trial).misalignment_db;
    // Fidelity at a gain both loops handle, with a 6 dB safety margin below the uncancelled limit.
    let g_op = (g0 - 6).max(0) as f32;
    let f_off = fidelity_db(g_op, FeedbackCfg::OFF, &trial);
    let f_on = fidelity_db(g_op, fb, &trial);
    println!("max stable gain without canceller: {g0} dB");
    println!(
        "max stable gain with canceller ({} taps, delay {}, calibrate {} ms, mu {}, leak {}): {g1} dB  ({:+} dB), misalignment there {mis:.1} dB",
        fb.taps, fb.delay, fb.calibrate_ms, fb.mu, fb.leak, g1 - g0
    );
    println!("fidelity of the output against the no-feedback ideal at {g_op:.0} dB gain: {f_off:.1} dB without, {f_on:.1} dB with the canceller");
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn path_peak_is_what_was_asked_for() {
        let h = path_fir(&SCENARIOS[1], -30.0);
        let peak = (0..400)
            .map(|k| {
                let w = 2.0 * PI * (100.0 + 6900.0 * k as f32 / 399.0) / SAMPLE_RATE;
                let (re, im) = h.iter().enumerate().fold((0.0, 0.0), |(re, im), (n, v)| {
                    (re + v * (w * n as f32).cos(), im - v * (w * n as f32).sin())
                });
                (re * re + im * im).sqrt()
            })
            .fold(0.0f32, f32::max);
        assert!((20.0 * peak.log10() + 30.0).abs() < 0.5, "{}", 20.0 * peak.log10());
        assert!(h[..SCENARIOS[1].delay].iter().all(|v| v.abs() < 1e-6), "energy before the delay");
    }

    #[test]
    fn sources_have_the_requested_level() {
        for kind in [Input::Noise, Input::Voiced] {
            let mut s = Source::new(kind, -30.0);
            let v: Vec<f32> = (0..160_000).map(|_| s.next()).collect();
            let db = rms_db(&v);
            assert!((db + 30.0).abs() < 1.0, "{kind:?}: {db}");
        }
    }

    fn trial_for<'a>(path: &'a [f32], input: Input) -> Trial<'a> {
        Trial { path, drift: None, input, in_dbfs: INPUT_DBFS }
    }

    #[test]
    fn canceller_makes_a_howling_gain_stable_and_keeps_the_sound() {
        let path = path_fir(&SCENARIOS[0], -30.0);
        let t = trial_for(&path, Input::Voiced);
        // 38 dB of gain on a path whose peak coupling is -30 dB: the loop gain is above 1 without help.
        let howl = run(&linear_config(38.0, FeedbackCfg::OFF), &t).tail_db - run(&linear_config(38.0, FeedbackCfg::OFF), &Trial { path: &vec![0.0; path.len()], ..t }).tail_db;
        assert!(howl > 10.0, "should howl without the canceller: {howl}");
        let held = run(&linear_config(38.0, DEFAULT_FB), &t).tail_db - run(&linear_config(38.0, FeedbackCfg::OFF), &Trial { path: &vec![0.0; path.len()], ..t }).tail_db;
        assert!(held < 3.0, "canceller should hold it: {held}");
        // And at a gain that is stable either way, the canceller must not damage the voiced sound.
        let off = fidelity_db(24.0, FeedbackCfg::OFF, &t);
        let on = fidelity_db(24.0, DEFAULT_FB, &t);
        assert!(on > off - 3.0, "fidelity {on} dB with vs {off} dB without");
    }

    #[test]
    fn a_fast_always_adapting_filter_cancels_the_wanted_sound() {
        // The reason for calibrating instead: this documents the failure of plain NLMS in a closed loop.
        let path = path_fir(&SCENARIOS[0], -30.0);
        let t = trial_for(&path, Input::Voiced);
        let fast = FeedbackCfg { calibrate_ms: 0.0, mu: 0.02, leak: 0.0, ..DEFAULT_FB };
        let off = fidelity_db(24.0, FeedbackCfg::OFF, &t);
        let on = fidelity_db(24.0, fast, &t);
        assert!(on < off - 4.0, "expected clear damage: {on} dB vs {off} dB");
    }
}

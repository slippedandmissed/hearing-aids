use crate::bands::Multiband;
use crate::biquad::{Biquad, Q_BUTTERWORTH};
use crate::config::{Config, EQ_BANDS};
use crate::dynamics::CONTROL_STEP;
use crate::feedback::Canceller;
use crate::gate::Expander;
use crate::{Limiter, SAMPLE_RATE};

/// The processing chain for one ear:
/// high-pass → feedback canceller → expander → band split with per-band compression → exciter EQ → fade-in → limiter.
///
/// The feedback canceller uses the final output as its reference.
#[derive(Debug, Clone, Copy)]
pub struct Ear {
    highpass: [Biquad; 2],
    feedback: Canceller,
    gate: Expander,
    bands: Multiband,
    eq: [Biquad; EQ_BANDS],
    limiter: Limiter,
    /// Fade-in position in samples and its length.
    fade_pos: u32,
    fade_len: u32,
    tick: usize,
}

impl Ear {
    pub fn new(cfg: &Config) -> Self {
        // 2 x Butterworth section = 4th order, so DC and rumble are well down.
        let hp = Biquad::highpass(cfg.highpass_hz, Q_BUTTERWORTH);
        Self {
            highpass: [hp; 2],
            feedback: Canceller::new(&cfg.feedback),
            gate: Expander::new(cfg),
            bands: Multiband::new(cfg),
            eq: core::array::from_fn(|i| Biquad::peaking(cfg.eq[i].freq_hz, cfg.eq[i].gain_db, cfg.eq[i].q)),
            limiter: Limiter::new(cfg.limit_dbfs),
            fade_pos: 0,
            fade_len: (cfg.fade_in_ms * 1e-3 * SAMPLE_RATE) as u32,
            tick: 0,
        }
    }

    /// Samples that reached the limiter's knee since start-up.
    pub fn limiter_engaged(&self) -> u32 {
        self.limiter.engaged()
    }

    #[inline]
    fn process_sample(&mut self, x: f32) -> f32 {
        // A NaN or infinity must never enter a filter: it would stay in the state forever.
        let x = if x.is_finite() { x } else { 0.0 };
        if self.feedback.calibrating() {
            // Boot calibration: the exciter plays quiet noise made here and the canceller measures the path.
            let mic = self.highpass[0].process(x);
            let mic = self.highpass[1].process(mic);
            self.feedback.cancel(mic);
            let out = self.limiter.process(self.feedback.probe());
            self.feedback.push_reference(out);
            return out;
        }
        if self.tick == 0 {
            self.gate.update_gain();
            self.bands.update_gains();
        }
        self.tick = (self.tick + 1) % CONTROL_STEP;

        let mut y = self.highpass[0].process(x);
        y = self.highpass[1].process(y);
        y = self.feedback.cancel(y);
        y = self.gate.process(y);
        y = self.bands.process(y);
        for e in &mut self.eq {
            y = e.process(y);
        }
        if self.fade_pos < self.fade_len {
            y *= self.fade_pos as f32 / self.fade_len as f32;
            self.fade_pos += 1;
        }
        let out = self.limiter.process(y);
        self.feedback.push_reference(out);
        out
    }

    /// True while the boot calibration is playing its noise (the input is ignored).
    pub fn calibrating(&self) -> bool {
        self.feedback.calibrating()
    }

    /// The feedback canceller's current estimate of the exciter-to-microphone path (empty if it is off), and the
    /// delay in samples it starts at.
    pub fn feedback_path(&self) -> (&[f32], usize) {
        (self.feedback.weights(), self.feedback.delay())
    }

    /// Process one block. `input` and `output` must have the same length.
    pub fn process(&mut self, input: &[f32], output: &mut [f32]) {
        debug_assert_eq!(input.len(), output.len());
        for (y, &x) in output.iter_mut().zip(input) {
            *y = self.process_sample(x);
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::config::{Band, BANDS};
    use crate::db_to_lin;
    use core::f32::consts::PI;

    fn tone(hz: f32, amp: f32, n: usize) -> Vec<f32> {
        (0..n).map(|i| amp * libm::sinf(2.0 * PI * hz * i as f32 / SAMPLE_RATE)).collect()
    }

    fn run(cfg: &Config, input: &[f32]) -> Vec<f32> {
        let mut out = vec![0.0; input.len()];
        let mut ear = Ear::new(cfg);
        // Odd block sizes on purpose: the result must not depend on how the frontend slices the stream.
        for (i, o) in input.chunks(13).zip(out.chunks_mut(13)) {
            ear.process(i, o);
        }
        out
    }

    fn peak(v: &[f32]) -> f32 {
        v.iter().fold(0.0, |m, x| m.max(x.abs()))
    }

    #[test]
    fn passthrough_is_minus_6_db_in_the_speech_band() {
        let n = SAMPLE_RATE as usize * 2;
        for hz in [300.0, 1000.0, 3000.0] {
            let out = run(&Config::PASSTHROUGH, &tone(hz, 0.1, n));
            let g = 20.0 * libm::log10f(peak(&out[n / 2..]) / 0.1);
            assert!((g + 6.02).abs() < 0.4, "{hz} Hz: {g}");
        }
    }

    #[test]
    fn fades_in_from_silence() {
        let n = SAMPLE_RATE as usize;
        let out = run(&Config::PASSTHROUGH, &tone(1000.0, 0.1, n));
        assert!(peak(&out[..50]) < 0.2 * peak(&out[n / 2..]));
    }

    #[test]
    fn block_size_does_not_matter() {
        let input = tone(700.0, 0.05, 4000);
        let a = run(&Config::CONDUCTIVE_GUESS, &input);
        let mut ear = Ear::new(&Config::CONDUCTIVE_GUESS);
        let mut b = vec![0.0; input.len()];
        ear.process(&input, &mut b);
        assert_eq!(a, b);
    }

    #[test]
    fn output_never_exceeds_ceiling_even_at_huge_gain() {
        let mut cfg = Config::PASSTHROUGH;
        cfg.bands = [Band { gain_db: 60.0, threshold_dbfs: 0.0, ratio: 1.0 }; BANDS];
        cfg.limit_dbfs = -18.0;
        cfg.fade_in_ms = 0.0;
        let out = run(&cfg, &tone(1000.0, 1.0, 20_000));
        assert!(peak(&out) <= db_to_lin(-18.0) + 1e-6);
        assert!(peak(&out) > 0.9 * db_to_lin(-18.0), "should be driving the ceiling");
    }

    #[test]
    fn nan_and_infinity_do_not_poison_the_filters() {
        let mut input = tone(1000.0, 0.05, 6000);
        input[100] = f32::NAN;
        input[200] = f32::INFINITY;
        input[300] = f32::NEG_INFINITY;
        let out = run(&Config::CONDUCTIVE_GUESS, &input);
        assert!(out.iter().all(|y| y.is_finite()));
        assert!(peak(&out[3000..]) > 0.01, "chain went dead after a bad sample");
    }

    #[test]
    fn dc_offset_is_removed() {
        let input = vec![0.2; SAMPLE_RATE as usize * 2];
        let mut cfg = Config::PASSTHROUGH;
        cfg.limit_dbfs = 0.0;
        let out = run(&cfg, &input);
        assert!(out.last().unwrap().abs() < 1e-3);
    }

    #[test]
    fn conductive_guess_compresses_speech_levels_and_respects_the_ceiling() {
        let n = SAMPLE_RATE as usize * 2;
        let cfg = Config::CONDUCTIVE_GUESS;
        let quiet = peak(&run(&cfg, &tone(1000.0, db_to_lin(-60.0), n))[n / 2..]);
        let loud = peak(&run(&cfg, &tone(1000.0, db_to_lin(-30.0), n))[n / 2..]);
        // 30 dB more input must give clearly less than 30 dB more output (and the limiter bounds the loud one).
        let rise = 20.0 * libm::log10f(loud / quiet);
        assert!(rise < 22.0, "{rise}");
        assert!(loud <= db_to_lin(cfg.limit_dbfs) + 1e-6);
    }

    #[test]
    fn calibration_plays_noise_then_hands_over_to_the_chain() {
        use crate::config::FeedbackCfg;
        let mut cfg = Config::PASSTHROUGH;
        cfg.feedback = FeedbackCfg { taps: 32, delay: 8, mu: 0.0, calibrate_ms: 100.0, mu_cal: 0.1, probe_dbfs: -30.0, leak: 0.0, seed: 5 };
        cfg.limit_dbfs = 0.0;
        let mut ear = Ear::new(&cfg);
        let silent = vec![0.0f32; 4000];
        let mut out = vec![0.0f32; 4000];
        ear.process(&silent, &mut out);
        let cal_len = (0.1 * SAMPLE_RATE) as usize;
        let rms = |v: &[f32]| libm::sqrtf(v.iter().map(|x| x * x).sum::<f32>() / v.len() as f32);
        let level_db = 20.0 * libm::log10f(rms(&out[..cal_len]));
        assert!((level_db + 30.0).abs() < 2.0, "probe level {level_db}");
        assert!(!ear.calibrating());
        assert!(rms(&out[cal_len + 200..]) < 1e-4, "chain should be silent for silent input");
    }
}

//! Adaptive feedback canceller (NLMS).
//!
//! The exciter's vibration reaches the microphone through the head and the earring. That path is an unknown FIR
//! filter between the output the chain sent and what the microphone hears a little later. The canceller keeps an
//! estimate of it, predicts the feedback from the recent output and subtracts the prediction from the microphone
//! signal before the rest of the chain amplifies it.
//!
//! The path includes a pure delay (I2S output buffering, the PDM decimation filter, the sound travelling), so the
//! estimate covers `taps` coefficients starting `delay` samples back. Both are measured on the bench, not assumed.
//!
//! Known limit: the output is correlated with the wanted input (it IS the input, amplified), so NLMS is biased
//! toward cancelling wanted tonal sounds such as vowels. A small step size keeps that slow; the simulator in
//! `hearing-desktop` measures how much it matters.
use crate::config::FeedbackCfg;
use crate::{SAMPLE_RATE, db_to_lin};

pub const MAX_TAPS: usize = 64;
pub const MAX_DELAY: usize = 64;
/// History length; a power of two at least `MAX_TAPS + MAX_DELAY`.
const HIST: usize = 128;
/// Regularisation per tap: reference power below -80 dBFS RMS barely adapts the filter.
const EPS_PER_TAP: f32 = 1e-8;
/// The leak toward the calibrated filter is applied every this many samples (with the strength scaled up).
const LEAK_EVERY: u32 = 16;

#[derive(Debug, Clone, Copy)]
pub struct Canceller {
    w: [f32; MAX_TAPS],
    /// The filter measured at calibration; the running filter is pulled toward it.
    w_cal: [f32; MAX_TAPS],
    /// Output history stored twice (`buf[i]` and `buf[i + HIST]`) so any window is one contiguous slice.
    /// `buf[pos + k]` is the output `k + 1` samples ago.
    buf: [f32; 2 * HIST],
    pos: usize,
    taps: usize,
    delay: usize,
    mu: f32,
    mu_cal: f32,
    leak: f32,
    probe_amp: f32,
    rng: u32,
    cal_left: u32,
    tick: u32,
}

impl Canceller {
    pub fn new(cfg: &FeedbackCfg) -> Self {
        let delay = cfg.delay.min(MAX_DELAY);
        let taps = cfg.taps.min(MAX_TAPS).min(HIST - delay);
        let cal_left = if taps > 0 { (cfg.calibrate_ms.max(0.0) * 1e-3 * SAMPLE_RATE) as u32 } else { 0 };
        Self {
            w: [0.0; MAX_TAPS],
            w_cal: [0.0; MAX_TAPS],
            buf: [0.0; 2 * HIST],
            pos: 0,
            taps,
            delay,
            mu: cfg.mu.clamp(0.0, 1.0),
            mu_cal: cfg.mu_cal.clamp(0.0, 1.0),
            leak: cfg.leak.clamp(0.0, 1.0),
            probe_amp: db_to_lin(cfg.probe_dbfs),
            rng: cfg.seed.max(1),
            cal_left,
            tick: 0,
        }
    }

    /// True while the boot calibration is running: the caller must output `probe()` instead of the chain.
    pub fn calibrating(&self) -> bool {
        self.cal_left > 0
    }

    /// One sample of calibration noise (roughly Gaussian, `probe_dbfs` RMS).
    pub fn probe(&mut self) -> f32 {
        let mut sum = 0.0;
        for _ in 0..4 {
            self.rng ^= self.rng << 13;
            self.rng ^= self.rng >> 17;
            self.rng ^= self.rng << 5;
            sum += self.rng as f32 * (2.0 / u32::MAX as f32) - 1.0;
        }
        self.probe_amp * sum * (libm::sqrtf(3.0) / 2.0)
    }

    /// The current estimate of the path, `taps` coefficients starting `delay()` samples back.
    pub fn weights(&self) -> &[f32] {
        &self.w[..self.taps]
    }

    pub fn delay(&self) -> usize {
        self.delay
    }

    /// Subtract the predicted feedback from one microphone sample and adapt. Call before `push_reference`.
    #[inline]
    pub fn cancel(&mut self, mic: f32) -> f32 {
        if self.taps == 0 {
            return mic;
        }
        let u = &self.buf[self.pos + self.delay..self.pos + self.delay + self.taps];
        let w = &mut self.w[..self.taps];
        let (mut est, mut power) = (0.0f32, 0.0f32);
        for (wk, uk) in w.iter().zip(u) {
            est += wk * uk;
            power += uk * uk;
        }
        let e = mic - est;
        let mu = if self.cal_left > 0 { self.mu_cal } else { self.mu };
        if mu > 0.0 {
            let g = mu * e / (power + EPS_PER_TAP * self.taps as f32);
            if g.is_finite() {
                for (wk, uk) in w.iter_mut().zip(u) {
                    *wk += g * uk;
                }
            } else {
                w.fill(0.0);
            }
        }
        if self.cal_left == 0 && self.leak > 0.0 {
            self.tick += 1;
            if self.tick >= LEAK_EVERY {
                self.tick = 0;
                let k = (self.leak * LEAK_EVERY as f32).min(1.0);
                for (wk, ck) in w.iter_mut().zip(&self.w_cal) {
                    *wk -= k * (*wk - ck);
                }
            }
        }
        e
    }

    /// Record the sample just sent to the exciter. During calibration this also counts the calibration down and,
    /// at its end, remembers the measured filter.
    #[inline]
    pub fn push_reference(&mut self, out: f32) {
        self.pos = (self.pos + HIST - 1) & (HIST - 1);
        self.buf[self.pos] = out;
        self.buf[self.pos + HIST] = out;
        if self.cal_left > 0 {
            self.cal_left -= 1;
            if self.cal_left == 0 {
                self.w_cal = self.w;
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    /// Deterministic white noise in -1..1.
    struct Noise(u32);
    impl Noise {
        fn next(&mut self) -> f32 {
            self.0 ^= self.0 << 13;
            self.0 ^= self.0 >> 17;
            self.0 ^= self.0 << 5;
            (self.0 as f32 / u32::MAX as f32) * 2.0 - 1.0
        }
    }

    #[test]
    fn identifies_a_known_path_in_open_loop() {
        // Path: 20 samples of delay, then a decaying 3-tap response. Canceller delay 16, 16 taps.
        let mut h = [0.0f32; 40];
        h[20] = 0.3;
        h[21] = -0.15;
        h[22] = 0.08;
        let cfg = FeedbackCfg { taps: 16, delay: 16, mu: 0.1, ..FeedbackCfg::OFF };
        let mut c = Canceller::new(&cfg);
        let mut n = Noise(1);
        let mut out_hist = [0.0f32; 40]; // out_hist[k] = output k+1 samples ago
        let mut last_err = 0.0;
        for i in 0..20_000 {
            let mic: f32 = out_hist.iter().zip(&h).map(|(o, h)| o * h).sum();
            let e = c.cancel(mic);
            if i > 19_000 {
                last_err = last_err * 0.99 + e * e * 0.01;
            }
            let out = 0.1 * n.next();
            c.push_reference(out);
            out_hist.rotate_right(1);
            out_hist[0] = out;
        }
        // The path lies within the window (indices 20..22 of 16..32), so cancellation should be deep.
        let residual_db = 10.0 * libm::log10f(last_err.max(1e-20) / (0.1f32 * 0.1 / 3.0 * 0.3 * 0.3));
        assert!(residual_db < -30.0, "residual {residual_db} dB");
        let w = c.weights();
        assert!((w[4] - 0.3).abs() < 0.01 && (w[5] + 0.15).abs() < 0.01, "{:?}", &w[..8]);
    }

    #[test]
    fn off_is_a_pure_passthrough() {
        let mut c = Canceller::new(&FeedbackCfg::OFF);
        c.push_reference(1.0);
        assert_eq!(c.cancel(0.25), 0.25);
    }

    #[test]
    fn silence_does_not_move_the_weights() {
        let mut c = Canceller::new(&FeedbackCfg { taps: 32, delay: 8, mu: 0.1, ..FeedbackCfg::OFF });
        let mut n = Noise(7);
        for _ in 0..10_000 {
            c.cancel(1e-5 * n.next()); // microphone noise only, reference silent
            c.push_reference(0.0);
        }
        assert!(c.weights().iter().all(|w| w.abs() < 1e-6));
    }

    #[test]
    fn oversized_settings_are_clamped() {
        let c = Canceller::new(&FeedbackCfg { taps: 10_000, delay: 10_000, mu: 5.0, ..FeedbackCfg::OFF });
        assert!(c.delay() <= MAX_DELAY && c.weights().len() <= MAX_TAPS);
    }
}

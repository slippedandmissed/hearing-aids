use crate::config::{Config, Gate};
use crate::dynamics::{Envelope, SmoothGain};

/// Downward expander on the whole signal.
#[derive(Debug, Clone, Copy)]
pub struct Expander {
    env: Envelope,
    gain: SmoothGain,
    p: Gate,
}

impl Expander {
    pub fn new(cfg: &Config) -> Self {
        // Fast to open (so speech onsets are not clipped), slow to close.
        Self { env: Envelope::new(2.0, 80.0), gain: SmoothGain::new(1.0), p: cfg.gate }
    }

    pub fn update_gain(&mut self) {
        let level = self.env.level_db();
        let under = (self.p.threshold_dbfs - level).max(0.0);
        let atten = (under * (self.p.ratio - 1.0).max(0.0)).min(self.p.max_atten_db.max(0.0));
        self.gain.set_target_db(-atten);
    }

    #[inline]
    pub fn process(&mut self, x: f32) -> f32 {
        self.env.process(x);
        x * self.gain.next()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::SAMPLE_RATE;
    use crate::dynamics::CONTROL_STEP;
    use core::f32::consts::PI;

    fn run(amp: f32) -> f32 {
        let mut cfg = Config::PASSTHROUGH;
        cfg.gate = Gate { threshold_dbfs: -60.0, ratio: 2.0, max_atten_db: 12.0 };
        let mut g = Expander::new(&cfg);
        let n = SAMPLE_RATE as usize;
        let mut peak = 0.0f32;
        for i in 0..2 * n {
            if i % CONTROL_STEP == 0 {
                g.update_gain();
            }
            let y = g.process(amp * libm::sinf(2.0 * PI * 1000.0 * i as f32 / SAMPLE_RATE));
            if i >= n {
                peak = peak.max(y.abs());
            }
        }
        peak / amp
    }

    #[test]
    fn loud_signal_passes_untouched() {
        assert!((run(0.1) - 1.0).abs() < 0.02);
    }

    #[test]
    fn very_quiet_signal_is_turned_down_by_at_most_the_limit() {
        let g = 20.0 * libm::log10f(run(4.5e-4)); // -67 dBFS peak = -70 RMS, 10 dB under the threshold
        assert!((g + 10.0).abs() < 1.5, "{g}");
        let g = 20.0 * libm::log10f(run(1e-6)); // far under: pinned at the limit
        assert!((g + 12.0).abs() < 0.8, "{g}");
    }
}

//! Linkwitz-Riley band split with a compressor per band.
//!
//! The signal is split from the bottom: band 0 is the low-pass at crossover 0, the rest goes on to the next
//! crossover, and so on. Each band is then passed through all-pass sections at the crossovers above it, so the
//! phase of every path matches and the bands sum back to a flat response when all gains are equal.
use crate::config::{BANDS, Band, Config};
use crate::dynamics::{Envelope, SmoothGain, db_to_gain};
use crate::biquad::{Biquad, Q_BUTTERWORTH};

const XO: usize = BANDS - 1;

#[derive(Debug, Clone, Copy)]
pub struct Multiband {
    lp: [[Biquad; 2]; XO],
    hp: [[Biquad; 2]; XO],
    /// `ap[k][j]`: all-pass at crossover `j` for band `k`, used only when `j > k`.
    ap: [[Biquad; XO]; XO],
    env: [Envelope; BANDS],
    gain: [SmoothGain; BANDS],
    params: [Band; BANDS],
}

impl Multiband {
    pub fn new(cfg: &Config) -> Self {
        let q = Q_BUTTERWORTH;
        let f = cfg.crossover_hz;
        Self {
            lp: core::array::from_fn(|j| [Biquad::lowpass(f[j], q); 2]),
            hp: core::array::from_fn(|j| [Biquad::highpass(f[j], q); 2]),
            ap: core::array::from_fn(|_| core::array::from_fn(|j| Biquad::allpass(f[j], q))),
            env: [Envelope::new(cfg.attack_ms, cfg.release_ms); BANDS],
            gain: core::array::from_fn(|k| SmoothGain::new(db_to_gain(cfg.bands[k].gain_db))),
            params: cfg.bands,
        }
    }

    /// Gain in dB for a band at a given level: full gain below the threshold, then 1/ratio slope above it.
    fn target_db(p: &Band, level_db: f32) -> f32 {
        let over = (level_db - p.threshold_dbfs).max(0.0);
        p.gain_db - over * (1.0 - 1.0 / p.ratio.max(1.0))
    }

    /// Re-evaluate the compression curves. Call every `CONTROL_STEP` samples.
    pub fn update_gains(&mut self) {
        for k in 0..BANDS {
            let db = Self::target_db(&self.params[k], self.env[k].level_db());
            self.gain[k].set_target_db(db);
        }
    }

    #[inline]
    pub fn process(&mut self, x: f32) -> f32 {
        let mut rest = x;
        let mut out = 0.0;
        for k in 0..BANDS {
            let mut band = if k < XO {
                let (mut lo, mut hi) = (rest, rest);
                for s in 0..2 {
                    lo = self.lp[k][s].process(lo);
                    hi = self.hp[k][s].process(hi);
                }
                rest = hi;
                lo
            } else {
                rest
            };
            self.env[k].process(band);
            for j in (k + 1)..XO {
                band = self.ap[k][j].process(band);
            }
            out += band * self.gain[k].next();
        }
        out
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::SAMPLE_RATE;
    use crate::dynamics::CONTROL_STEP;
    use core::f32::consts::PI;

    fn flat_cfg(gain_db: f32) -> Config {
        let mut c = Config::PASSTHROUGH;
        c.bands = [Band { gain_db, threshold_dbfs: 0.0, ratio: 1.0 }; BANDS];
        c
    }

    /// Output peak for a sine of amplitude `amp` after settling, with control updates as the Ear does.
    fn peak_out(mb: &mut Multiband, hz: f32, amp: f32) -> f32 {
        let n = SAMPLE_RATE as usize;
        let mut peak = 0.0f32;
        for i in 0..2 * n {
            if i % CONTROL_STEP == 0 {
                mb.update_gains();
            }
            let y = mb.process(amp * libm::sinf(2.0 * PI * hz * i as f32 / SAMPLE_RATE));
            if i >= n {
                peak = peak.max(y.abs());
            }
        }
        peak
    }

    #[test]
    fn equal_gains_sum_to_a_flat_response() {
        for hz in [150.0, 400.0, 500.0, 900.0, 1500.0, 2200.0, 3000.0, 5000.0, 7000.0] {
            let mut mb = Multiband::new(&flat_cfg(0.0));
            let g = 20.0 * libm::log10f(peak_out(&mut mb, hz, 0.1) / 0.1);
            assert!(g.abs() < 0.3, "{hz} Hz: {g} dB");
        }
    }

    #[test]
    fn linear_band_applies_its_gain() {
        let mut mb = Multiband::new(&flat_cfg(20.0));
        let g = 20.0 * libm::log10f(peak_out(&mut mb, 1000.0, 0.01) / 0.01);
        assert!((g - 20.0).abs() < 0.5, "{g}");
    }

    #[test]
    fn gain_curve_is_exact() {
        let p = Band { gain_db: 30.0, threshold_dbfs: -50.0, ratio: 2.0 };
        assert_eq!(Multiband::target_db(&p, -80.0), 30.0);
        assert_eq!(Multiband::target_db(&p, -50.0), 30.0);
        assert_eq!(Multiband::target_db(&p, -30.0), 20.0);
        let linear = Band { ratio: 1.0, ..p };
        assert_eq!(Multiband::target_db(&linear, -10.0), 30.0);
        let nonsense = Band { ratio: 0.0, ..p }; // a ratio under 1 must not expand
        assert_eq!(Multiband::target_db(&nonsense, -10.0), 30.0);
    }

    #[test]
    fn compression_follows_the_ratio_above_the_threshold() {
        // Only band 1 (500-1500 Hz) compresses. Threshold -50 dBFS RMS, ratio 2. A sine of -30 dBFS peak is -33 dBFS
        // RMS, 17 dB over, so the gain must drop by 17 * (1 - 1/2) = 8.5 dB relative to the same band with
        // compression off. (Compare against that, not against the nominal 30 dB: a 30 dB band next to 0 dB
        // neighbours has its own shape from the crossover skirts.)
        let gain_db = |ratio: f32, tone_db: f32| {
            let mut c = flat_cfg(0.0);
            c.bands[1] = Band { gain_db: 30.0, threshold_dbfs: -50.0, ratio };
            let amp = db_to_gain(tone_db);
            20.0 * libm::log10f(peak_out(&mut Multiband::new(&c), 1000.0, amp) / amp)
        };
        let linear = gain_db(1.0, -30.0);
        let compressed = gain_db(2.0, -30.0);
        // Within 2 dB: the neighbouring bands leak into this tone and their share of the sum does not change when this
        // band's gain does.
        assert!((linear - compressed - 8.5).abs() < 2.0, "{linear} -> {compressed}");
        // Below the threshold compression does nothing.
        let quiet = gain_db(2.0, -70.0);
        assert!((quiet - linear).abs() < 0.5, "{quiet} vs {linear}");
    }

    #[test]
    fn bands_are_independent() {
        // Only the top band amplifies: a 6 kHz tone gains, a 200 Hz tone does not.
        let mut c = flat_cfg(0.0);
        c.bands[BANDS - 1].gain_db = 20.0;
        let g_hi = 20.0 * libm::log10f(peak_out(&mut Multiband::new(&c), 6000.0, 0.01) / 0.01);
        let g_lo = 20.0 * libm::log10f(peak_out(&mut Multiband::new(&c), 200.0, 0.01) / 0.01);
        assert!(g_hi > 18.0, "{g_hi}");
        assert!(g_lo.abs() < 1.0, "{g_lo}");
    }
}

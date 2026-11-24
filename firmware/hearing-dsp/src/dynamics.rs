//! Level detection and gain smoothing shared by the gate and the band compressors.
use crate::SAMPLE_RATE;

/// How many samples between gain-curve evaluations (the logs and exponentials are the expensive part;
/// 8 samples is 0.5 ms). The gain is smoothed per sample in between.
pub const CONTROL_STEP: usize = 8;

/// 20·log10(2): dB per octave of amplitude.
const DB_PER_OCTAVE: f32 = 6.0206;

/// Pre-smoothing of the power signal before the attack/release stage, ms. Adds to the effective attack time.
const PRE_SMOOTH_MS: f32 = 3.0;

/// One-pole smoothing coefficient for a time constant in ms.
pub fn coef(ms: f32) -> f32 {
    1.0 - libm::expf(-1.0 / (ms.max(0.01) * 1e-3 * SAMPLE_RATE))
}

#[inline]
pub fn lin_to_db(x: f32) -> f32 {
    DB_PER_OCTAVE * libm::log2f(x.max(1e-9))
}

#[inline]
pub fn db_to_gain(db: f32) -> f32 {
    libm::exp2f(db * (1.0 / DB_PER_OCTAVE))
}

/// Level follower on the signal power (so the level is an RMS level: a full-scale sine reads -3 dBFS), with separate
/// attack and release.
#[derive(Debug, Clone, Copy)]
pub struct Envelope {
    smooth: f32,
    value: f32,
    attack: f32,
    release: f32,
    pre: f32,
}

impl Envelope {
    pub fn new(attack_ms: f32, release_ms: f32) -> Self {
        Self { smooth: 0.0, value: 0.0, attack: coef(attack_ms), release: coef(release_ms), pre: coef(PRE_SMOOTH_MS) }
    }

    #[inline]
    pub fn process(&mut self, x: f32) -> f32 {
        // Smooth the squared signal first, so the ripple of a low tone does not bias the asymmetric stage upward.
        self.smooth += self.pre * (x * x - self.smooth);
        let p = self.smooth;
        let c = if p > self.value { self.attack } else { self.release };
        self.value += c * (p - self.value);
        self.value
    }

    /// RMS level in dBFS.
    pub fn level_db(&self) -> f32 {
        0.5 * lin_to_db(self.value)
    }
}

/// A linear gain that glides to its target, so changes made every `CONTROL_STEP` samples do not click.
#[derive(Debug, Clone, Copy)]
pub struct SmoothGain {
    current: f32,
    target: f32,
    step: f32,
}

impl SmoothGain {
    pub fn new(initial: f32) -> Self {
        Self { current: initial, target: initial, step: coef(0.5) }
    }

    pub fn set_target_db(&mut self, db: f32) {
        self.target = db_to_gain(db);
    }

    #[inline]
    pub fn next(&mut self) -> f32 {
        self.current += self.step * (self.target - self.current);
        self.current
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn db_conversions_round_trip() {
        for db in [-60.0, -20.0, 0.0, 12.0] {
            assert!((lin_to_db(db_to_gain(db)) - db).abs() < 0.01);
        }
    }

    #[test]
    fn envelope_attacks_faster_than_it_releases() {
        let mut e = Envelope::new(2.0, 100.0);
        for _ in 0..200 {
            e.process(1.0);
        }
        let up = e.level_db();
        assert!(up > -3.0, "{up}"); // full-scale DC is 0 dBFS RMS
        for _ in 0..200 {
            e.process(0.0);
        }
        assert!(e.level_db() > up - 6.0, "released too fast");
    }

    #[test]
    fn smooth_gain_converges_without_overshoot() {
        let mut g = SmoothGain::new(1.0);
        g.set_target_db(-20.0);
        let mut prev = 1.0;
        for _ in 0..2000 {
            let v = g.next();
            assert!(v <= prev && v >= 0.1 - 1e-6);
            prev = v;
        }
        assert!((prev - 0.1).abs() < 1e-3);
    }
}

#[cfg(test)]
mod level_tests {
    use super::*;

    #[test]
    fn a_sine_reads_its_rms_level_within_1_db() {
        for hz in [200.0f32, 500.0, 1000.0, 4000.0] {
            let mut e = Envelope::new(5.0, 60.0);
            for i in 0..32_000 {
                e.process(0.1 * libm::sinf(2.0 * core::f32::consts::PI * hz * i as f32 / SAMPLE_RATE));
            }
            // 0.1 peak = -20 dBFS peak = -23.01 dBFS RMS
            assert!((e.level_db() + 23.01).abs() < 1.0, "{hz} Hz: {}", e.level_db());
        }
    }
}

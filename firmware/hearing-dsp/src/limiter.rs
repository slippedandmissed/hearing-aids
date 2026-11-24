use crate::db_to_lin;

/// Where the soft knee starts, as a fraction of the ceiling.
const KNEE: f32 = 0.7;

/// Last stage of the chain. Linear up to 70 % of the ceiling, then a smooth `tanh` knee that approaches the ceiling,
/// then a hard clamp. NaN is muted. This is the safety stage: whatever happens upstream, the output never exceeds
/// the ceiling. It is an instantaneous waveshaper (no look-ahead), so peaks it catches are distorted, not ducked.
#[derive(Debug, Clone, Copy)]
pub struct Limiter {
    ceiling: f32,
    knee: f32,
    engaged: u32,
}

impl Limiter {
    pub fn new(ceiling_dbfs: f32) -> Self {
        let ceiling = db_to_lin(ceiling_dbfs);
        Self { ceiling, knee: ceiling * KNEE, engaged: 0 }
    }

    pub fn ceiling(&self) -> f32 {
        self.ceiling
    }

    /// Number of samples that reached the knee since start-up (saturating). A health indicator: if this climbs
    /// quickly in normal use, the gain or compression is set too high.
    pub fn engaged(&self) -> u32 {
        self.engaged
    }

    #[inline]
    pub fn process(&mut self, x: f32) -> f32 {
        if x.is_nan() {
            return 0.0;
        }
        let a = x.abs();
        if a <= self.knee {
            return x;
        }
        self.engaged = self.engaged.saturating_add(1);
        let room = self.ceiling - self.knee;
        let y = (self.knee + room * libm::tanhf((a - self.knee) / room)).min(self.ceiling);
        if x < 0.0 { -y } else { y }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn never_exceeds_ceiling() {
        let mut l = Limiter::new(-18.0);
        let c = l.ceiling();
        for x in [0.0, 0.1, -0.1, 1.0, -1.0, 1e9, -1e9, f32::INFINITY, f32::NEG_INFINITY] {
            assert!(l.process(x).abs() <= c, "{x}");
        }
    }

    #[test]
    fn nan_is_muted() {
        assert_eq!(Limiter::new(-18.0).process(f32::NAN), 0.0);
    }

    #[test]
    fn below_the_knee_is_untouched() {
        let mut l = Limiter::new(-6.0); // ceiling 0.501, knee 0.351
        assert_eq!(l.process(0.25), 0.25);
        assert_eq!(l.engaged(), 0);
    }

    #[test]
    fn knee_is_continuous_monotonic_and_odd() {
        let mut l = Limiter::new(0.0);
        let mut prev = 0.0;
        for i in 0..=2000 {
            let x = i as f32 * 0.001;
            let y = l.process(x);
            assert!(y >= prev - 1e-6, "not monotonic at {x}");
            assert!((y - prev).abs() < 0.0015, "jump at {x}");
            assert_eq!(l.process(-x), -y);
            prev = y;
        }
        assert!(l.engaged() > 0);
    }
}

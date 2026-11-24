//! Second-order IIR sections (RBJ cookbook), direct form II transposed.
use crate::SAMPLE_RATE;
use core::f32::consts::{PI, SQRT_2};

/// Butterworth Q, also the Q of the sections inside a Linkwitz-Riley 4th-order crossover.
pub const Q_BUTTERWORTH: f32 = 1.0 / SQRT_2;

#[derive(Debug, Clone, Copy)]
pub struct Biquad {
    b0: f32,
    b1: f32,
    b2: f32,
    a1: f32,
    a2: f32,
    z1: f32,
    z2: f32,
}

impl Biquad {
    const fn from_coeffs(b0: f32, b1: f32, b2: f32, a1: f32, a2: f32) -> Self {
        Self { b0, b1, b2, a1, a2, z1: 0.0, z2: 0.0 }
    }

    /// Passes the signal unchanged.
    pub const fn identity() -> Self {
        Self::from_coeffs(1.0, 0.0, 0.0, 0.0, 0.0)
    }

    // Common prelude: (cos w0, alpha, a0). Frequencies are clamped well inside (0, Nyquist) so a bad
    // config cannot produce an unstable or NaN filter.
    fn prelude(freq_hz: f32, q: f32) -> (f32, f32, f32) {
        let f = freq_hz.clamp(10.0, SAMPLE_RATE * 0.45);
        let w0 = 2.0 * PI * f / SAMPLE_RATE;
        let alpha = libm::sinf(w0) / (2.0 * q.max(0.1));
        (libm::cosf(w0), alpha, 1.0 + alpha)
    }

    pub fn lowpass(freq_hz: f32, q: f32) -> Self {
        let (c, alpha, a0) = Self::prelude(freq_hz, q);
        let b1 = (1.0 - c) / a0;
        Self::from_coeffs(b1 * 0.5, b1, b1 * 0.5, -2.0 * c / a0, (1.0 - alpha) / a0)
    }

    pub fn highpass(freq_hz: f32, q: f32) -> Self {
        let (c, alpha, a0) = Self::prelude(freq_hz, q);
        let b1 = -(1.0 + c) / a0;
        Self::from_coeffs(-b1 * 0.5, b1, -b1 * 0.5, -2.0 * c / a0, (1.0 - alpha) / a0)
    }

    /// Constant 0 dB peak-gain band-pass.
    pub fn bandpass(freq_hz: f32, q: f32) -> Self {
        let (c, alpha, a0) = Self::prelude(freq_hz, q);
        Self::from_coeffs(alpha / a0, 0.0, -alpha / a0, -2.0 * c / a0, (1.0 - alpha) / a0)
    }

    pub fn allpass(freq_hz: f32, q: f32) -> Self {
        let (c, alpha, a0) = Self::prelude(freq_hz, q);
        let a1 = -2.0 * c / a0;
        let a2 = (1.0 - alpha) / a0;
        Self::from_coeffs(a2, a1, 1.0, a1, a2)
    }

    /// Peaking EQ. A gain of exactly 0 dB is an identity, so unused EQ bands cost almost nothing to configure.
    pub fn peaking(freq_hz: f32, gain_db: f32, q: f32) -> Self {
        if gain_db == 0.0 {
            return Self::identity();
        }
        let (c, alpha, _) = Self::prelude(freq_hz, q);
        let a = libm::powf(10.0, gain_db / 40.0);
        let a0 = 1.0 + alpha / a;
        Self::from_coeffs(
            (1.0 + alpha * a) / a0,
            -2.0 * c / a0,
            (1.0 - alpha * a) / a0,
            -2.0 * c / a0,
            (1.0 - alpha / a) / a0,
        )
    }

    #[inline]
    pub fn process(&mut self, x: f32) -> f32 {
        let y = self.b0 * x + self.z1;
        self.z1 = self.b1 * x - self.a1 * y + self.z2;
        self.z2 = self.b2 * x - self.a2 * y;
        y
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    /// Steady-state gain of a filter at one frequency (peak of the output over the last second).
    pub fn gain_at(mut f: impl FnMut(f32) -> f32, hz: f32) -> f32 {
        let n = SAMPLE_RATE as usize;
        let mut peak = 0.0f32;
        for i in 0..2 * n {
            let x = libm::sinf(2.0 * PI * hz * i as f32 / SAMPLE_RATE);
            let y = f(x);
            if i >= n {
                peak = peak.max(y.abs());
            }
        }
        peak
    }

    #[test]
    fn lowpass_passes_low_and_stops_high() {
        let mut f = Biquad::lowpass(1000.0, Q_BUTTERWORTH);
        assert!((gain_at(|x| f.process(x), 100.0) - 1.0).abs() < 0.02);
        let mut f = Biquad::lowpass(1000.0, Q_BUTTERWORTH);
        assert!(gain_at(|x| f.process(x), 6000.0) < 0.05);
    }

    #[test]
    fn highpass_kills_dc_and_passes_high() {
        let mut f = Biquad::highpass(100.0, Q_BUTTERWORTH);
        let mut y = 0.0;
        for _ in 0..16_000 {
            y = f.process(0.5);
        }
        assert!(y.abs() < 1e-3, "dc leaks: {y}");
        let mut f = Biquad::highpass(100.0, Q_BUTTERWORTH);
        assert!((gain_at(|x| f.process(x), 2000.0) - 1.0).abs() < 0.02);
    }

    #[test]
    fn allpass_has_unit_magnitude() {
        for hz in [200.0, 1000.0, 3000.0] {
            let mut f = Biquad::allpass(1000.0, Q_BUTTERWORTH);
            assert!((gain_at(|x| f.process(x), hz) - 1.0).abs() < 0.02, "{hz}");
        }
    }

    #[test]
    fn peaking_hits_its_gain_at_the_centre() {
        let mut f = Biquad::peaking(1000.0, 6.0, 1.0);
        let g = 20.0 * libm::log10f(gain_at(|x| f.process(x), 1000.0));
        assert!((g - 6.0).abs() < 0.2, "{g}");
        let mut id = Biquad::peaking(1000.0, 0.0, 1.0);
        assert_eq!(id.process(0.3), 0.3);
    }

    #[test]
    fn impulse_response_decays_even_for_extreme_settings() {
        for f in [Biquad::lowpass(1.0, 50.0), Biquad::highpass(1e9, 0.0), Biquad::peaking(8000.0, 40.0, 20.0)] {
            let mut f = f;
            let mut last = 0.0;
            f.process(1.0);
            for _ in 0..50_000 {
                last = f.process(0.0);
            }
            assert!(last.is_finite() && last.abs() < 1e-3, "{last}");
        }
    }
}

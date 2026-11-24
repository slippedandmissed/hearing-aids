//! Hearing-aid DSP. `no_std`, no allocation, `f32` (the nRF52840 has a single-precision FPU).
//!
//! One [`Ear`] per ear; the two ears are independent aids. Frontends convert samples with
//! [`from_i16`] / [`to_i16`] and feed blocks of any length.
#![cfg_attr(not(test), no_std)]

mod bands;
mod biquad;
mod config;
mod dynamics;
mod ear;
mod feedback;
mod gate;
mod limiter;
mod melody;

pub use biquad::Biquad;
pub use config::{BANDS, Band, Config, EQ_BANDS, EqBand, FeedbackCfg, Gate, SAMPLE_RATE};
pub use feedback::{MAX_DELAY, MAX_TAPS};
pub use ear::Ear;
pub use limiter::Limiter;
pub use melody::{Melody, Note, STARTUP, Tone};

/// Convert a signed 16-bit sample to the library's nominal range of -1.0 ..= 1.0.
#[inline]
pub fn from_i16(x: i16) -> f32 {
    x as f32 * (1.0 / 32768.0)
}

/// Convert back to `i16`, rounding and saturating.
#[inline]
pub fn to_i16(x: f32) -> i16 {
    // `as` saturates and maps NaN to 0, which is the behaviour we want at the very last step.
    libm::roundf(x * 32768.0) as i16
}

/// Decibels to a linear amplitude ratio.
#[inline]
pub fn db_to_lin(db: f32) -> f32 {
    libm::powf(10.0, db * (1.0 / 20.0))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn i16_roundtrip_is_exact() {
        for x in [i16::MIN, -12345, -1, 0, 1, 4000, i16::MAX] {
            assert_eq!(to_i16(from_i16(x)), x);
        }
    }

    #[test]
    fn to_i16_saturates_and_survives_nan() {
        assert_eq!(to_i16(10.0), i16::MAX);
        assert_eq!(to_i16(-10.0), i16::MIN);
        assert_eq!(to_i16(f32::NAN), 0);
    }

    #[test]
    fn db_conversion() {
        assert!((db_to_lin(0.0) - 1.0).abs() < 1e-6);
        assert!((db_to_lin(-6.0206) - 0.5).abs() < 1e-4);
        assert!((db_to_lin(20.0) - 10.0).abs() < 1e-4);
    }
}

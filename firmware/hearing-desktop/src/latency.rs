//! Group delay of the chain, measured from the phase slope of sine tones through the real code.
use hearing_dsp::{Config, Ear, SAMPLE_RATE};
use std::f64::consts::PI;

const FREQS: [f32; 11] = [150.0, 250.0, 400.0, 500.0, 750.0, 1000.0, 1500.0, 2000.0, 3000.0, 4000.0, 6000.0];
/// Half the frequency spacing used for the phase slope, Hz.
const DELTA: f32 = 12.0;
/// Test amplitude (-50 dBFS): small enough for the limiter to stay out of it.
const AMP: f32 = 0.003;

/// Phase (radians) of the output relative to the input sine at `hz`, once settled.
fn phase(cfg: &Config, hz: f32) -> f64 {
    let mut cfg = *cfg;
    cfg.fade_in_ms = 0.0;
    cfg.feedback = hearing_dsp::FeedbackCfg::OFF;
    let mut ear = Ear::new(&cfg);
    let n = 3 * SAMPLE_RATE as usize;
    let (mut i_acc, mut q_acc) = (0.0f64, 0.0f64);
    let w = 2.0 * PI * hz as f64 / SAMPLE_RATE as f64;
    let mut y = [0.0f32];
    for k in 0..n {
        let x = AMP * (w * k as f64).sin() as f32;
        ear.process(&[x], &mut y);
        if k >= n / 3 {
            i_acc += y[0] as f64 * (w * k as f64).sin();
            q_acc += y[0] as f64 * (w * k as f64).cos();
        }
    }
    q_acc.atan2(i_acc)
}

/// Group delay in ms at `hz`.
pub fn group_delay_ms(cfg: &Config, hz: f32) -> f32 {
    let mut dphi = phase(cfg, hz + DELTA) - phase(cfg, hz - DELTA);
    // The step is small enough that a wrap is the only way to be off by a whole turn.
    while dphi > PI {
        dphi -= 2.0 * PI;
    }
    while dphi < -PI {
        dphi += 2.0 * PI;
    }
    (-dphi / (2.0 * PI * 2.0 * DELTA as f64) * 1000.0) as f32
}

pub fn print(cfg: &Config) -> Result<(), String> {
    println!("group delay of the DSP chain (ms), from the phase slope of -50 dBFS sine tones");
    print!("{:>8}", "Hz");
    for f in FREQS {
        print!("{f:>7.0}");
    }
    print!("\n{:>8}", "ms");
    for f in FREQS {
        print!("{:>7.2}", group_delay_ms(cfg, f));
    }
    println!("\n");
    println!("Not in that number (read from the firmware structure, UNVERIFIED until measured on the device):");
    println!("  - the PDM peripheral's decimation filter: not known, see the nRF52840 product specification");
    println!("  - capture in 16-frame blocks: a sample waits up to 16 frames (1.0 ms) for its block to complete");
    println!("  - the hand-over to the I2S buffer and the double-buffered I2S output: about 1 to 2 blocks (1 to 2 ms)");
    println!("  - the class-D amplifier, the exciter and the sound's travel through the head");
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn a_pure_one_pole_has_the_known_delay_at_low_frequency() {
        // The 100 Hz high-pass in PASSTHROUGH is the only filter that matters at 150 Hz and its group delay there is
        // large and positive; at 3 kHz everything is nearly flat and small. This pins down the sign convention.
        let cfg = Config::PASSTHROUGH;
        let low = group_delay_ms(&cfg, 150.0);
        let high = group_delay_ms(&cfg, 3000.0);
        assert!(low > 2.0 * high, "{low} ms at 150 Hz vs {high} ms at 3 kHz");
        assert!(high > 0.0 && high < 2.0, "{high}");
    }
}

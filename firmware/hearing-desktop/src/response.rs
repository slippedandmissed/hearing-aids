//! Gain of the whole chain for sine tones, by frequency and input level.
use hearing_dsp::{Config, Ear, SAMPLE_RATE};
use std::f32::consts::PI;

const FREQS: [f32; 12] = [125.0, 250.0, 500.0, 750.0, 1000.0, 1500.0, 2000.0, 3000.0, 4000.0, 5000.0, 6000.0, 7000.0];
/// Input levels, dBFS peak.
const LEVELS: [f32; 5] = [-80.0, -70.0, -60.0, -50.0, -40.0];

/// Gain in dB at one frequency and level (peak out over peak in, once settled).
fn gain_db(cfg: &Config, hz: f32, level_dbfs: f32) -> f32 {
    let amp = 10f32.powf(level_dbfs / 20.0);
    let mut cfg = *cfg;
    cfg.fade_in_ms = 0.0;
    let mut ear = Ear::new(&cfg);
    let n = SAMPLE_RATE as usize;
    let input: Vec<f32> = (0..2 * n).map(|i| amp * (2.0 * PI * hz * i as f32 / SAMPLE_RATE).sin()).collect();
    let mut out = vec![0.0; input.len()];
    for (i, o) in input.chunks(16).zip(out.chunks_mut(16)) {
        ear.process(i, o);
    }
    let peak = out[n..].iter().fold(0.0f32, |m, y| m.max(y.abs()));
    20.0 * (peak / amp).max(1e-9).log10()
}

pub fn print(cfg: &Config) -> Result<(), String> {
    println!("gain (dB) of the chain by input level (dBFS peak, rows) and frequency (Hz, columns);");
    println!("the ceiling is {:.1} dBFS, so rows that reach it are limited, not linear", cfg.limit_dbfs);
    print!("{:>9}", "");
    for f in FREQS {
        print!("{f:>7.0}");
    }
    println!();
    for level in LEVELS {
        print!("{:>6.0} dB", level);
        for f in FREQS {
            print!("{:>7.1}", gain_db(cfg, f, level));
        }
        println!();
    }
    Ok(())
}

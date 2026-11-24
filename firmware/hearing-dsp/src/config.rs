/// Sample rate shared by the PDM microphone decimation and the I2S output, in Hz.
/// 32 MHz / 31 / 64 on the nRF52840. ESTIMATE until measured on hardware.
pub const SAMPLE_RATE: f32 = 32_000_000.0 / 31.0 / 64.0;

/// Number of compression bands (the crossovers are `BANDS - 1`).
pub const BANDS: usize = 4;
/// Number of parametric EQ sections after the bands (for the exciter response).
pub const EQ_BANDS: usize = 3;

/// One compression band.
#[cfg_attr(feature = "serde", derive(serde::Serialize, serde::Deserialize))]
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Band {
    /// Gain for quiet sounds (below the threshold), dB.
    pub gain_db: f32,
    /// Band level (RMS, dBFS; a sine at -30 dBFS peak is -33 dBFS RMS) above which the gain starts to fall.
    pub threshold_dbfs: f32,
    /// Compression ratio above the threshold; 1.0 = linear.
    pub ratio: f32,
}

/// Downward expander on the whole signal, to keep microphone self-noise from being amplified in quiet passages.
#[cfg_attr(feature = "serde", derive(serde::Serialize, serde::Deserialize))]
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Gate {
    /// Level (RMS, dBFS) below which the signal is turned down.
    pub threshold_dbfs: f32,
    /// Expansion ratio below the threshold; 1.0 = off.
    pub ratio: f32,
    /// The most the expander will turn the signal down, dB.
    pub max_atten_db: f32,
}

/// A peaking EQ section; 0 dB = unused.
#[cfg_attr(feature = "serde", derive(serde::Serialize, serde::Deserialize))]
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct EqBand {
    pub freq_hz: f32,
    pub gain_db: f32,
    pub q: f32,
}

/// Feedback canceller settings. `mu` = 0 or `taps` = 0 turns it off.
#[cfg_attr(feature = "serde", derive(serde::Serialize, serde::Deserialize))]
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct FeedbackCfg {
    /// Filter length (at most `MAX_TAPS`).
    pub taps: usize,
    /// Samples of pure delay in the exciter-to-microphone path that the filter skips (at most `MAX_DELAY`).
    pub delay: usize,
    /// NLMS step size while running, 0 .. 1. Very small, because the loop is closed: the output is the amplified
    /// input, so a fast filter learns to cancel the wanted sound (tonal vowels first). 0 freezes the filter after
    /// calibration.
    pub mu: f32,
    /// Boot calibration: for this many ms the chain is replaced by quiet noise the device makes itself, so the
    /// path is measured with nothing else to confuse it. 0 = no calibration.
    pub calibrate_ms: f32,
    /// Step size during calibration.
    pub mu_cal: f32,
    /// Level of the calibration noise, dBFS RMS.
    pub probe_dbfs: f32,
    /// While running, how fast the filter is pulled back toward the calibrated one (fraction per sample).
    pub leak: f32,
    /// Seed of the calibration noise. Use a different one per ear.
    pub seed: u32,
}

impl FeedbackCfg {
    pub const OFF: FeedbackCfg =
        FeedbackCfg { taps: 0, delay: 0, mu: 0.0, calibrate_ms: 0.0, mu_cal: 0.0, probe_dbfs: -40.0, leak: 0.0, seed: 1 };
}

/// Settings for one ear. Plain data so a frontend can build it from a file or a `const`.
#[cfg_attr(feature = "serde", derive(serde::Serialize, serde::Deserialize))]
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Config {
    /// Input high-pass (DC offset, wind, handling noise), Hz.
    pub highpass_hz: f32,
    pub gate: Gate,
    /// Band edges, ascending, Hz (Linkwitz-Riley 4th order).
    pub crossover_hz: [f32; BANDS - 1],
    pub bands: [Band; BANDS],
    /// Level-detector times shared by all bands, ms.
    pub attack_ms: f32,
    pub release_ms: f32,
    pub feedback: FeedbackCfg,
    /// Exciter equalisation, applied after the bands.
    pub eq: [EqBand; EQ_BANDS],
    /// Output ceiling in dBFS (peak). Nothing the chain produces may exceed it.
    pub limit_dbfs: f32,
    /// Fade-in after start-up, ms (0 = none).
    pub fade_in_ms: f32,
}

const NO_EQ: EqBand = EqBand { freq_hz: 1000.0, gain_db: 0.0, q: 1.0 };
const GATE_OFF: Gate = Gate { threshold_dbfs: -90.0, ratio: 1.0, max_atten_db: 0.0 };

impl Config {
    /// The behaviour of the first passthrough firmware: -6.02 dB (gain 4/8), nothing else, ceiling about -18.2 dBFS
    /// (4000/32768). Plus a 100 Hz high-pass so PDM offset cannot reach the exciter.
    pub const PASSTHROUGH: Config = Config {
        highpass_hz: 100.0,
        gate: GATE_OFF,
        crossover_hz: [500.0, 1500.0, 3000.0],
        bands: [Band { gain_db: -6.0206, threshold_dbfs: 0.0, ratio: 1.0 }; BANDS],
        feedback: FeedbackCfg::OFF,
        attack_ms: 5.0,
        release_ms: 60.0,
        eq: [NO_EQ; EQ_BANDS],
        limit_dbfs: -18.2,
        fade_in_ms: 100.0,
    };

    /// A starting point for a conductive loss from wax: roughly flat, about 30 dB for quiet sounds, compressed above
    /// about -50 dBFS. **ESTIMATE**: there is no audiogram, no measurement of the exciter and no measurement of the
    /// feedback margin. Do not wear it until feedback has been measured on the bench.
    pub const CONDUCTIVE_GUESS: Config = Config {
        gate: Gate { threshold_dbfs: -75.0, ratio: 2.0, max_atten_db: 10.0 },
        bands: [Band { gain_db: 30.0, threshold_dbfs: -50.0, ratio: 2.5 }; BANDS],
        // Boot calibration of the exciter-to-microphone path, then a filter held close to it. A delay of 0 is
        // harmless (the window just starts early; too high loses most of the benefit), so it stays 0 until the real
        // onset of the path is measured on the bench, see the Firmware chapter.
        feedback: FeedbackCfg { taps: 64, delay: 0, mu: 0.002, calibrate_ms: 3000.0, mu_cal: 0.05, probe_dbfs: -40.0, leak: 0.001, seed: 1 },
        ..Self::PASSTHROUGH
    };
}

impl Config {
    /// The same settings for the other ear: only the calibration-noise seed differs, so the two exciters do not
    /// play the same noise.
    pub const fn for_right_ear(mut self) -> Config {
        self.feedback.seed = self.feedback.seed.wrapping_mul(2_654_435_761).wrapping_add(1);
        self
    }
}

impl Default for Config {
    fn default() -> Self {
        Self::PASSTHROUGH
    }
}

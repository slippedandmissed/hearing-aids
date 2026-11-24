//! The start-up jingle: three rising notes, short, short, long. Frontends play it through the exciters at power-on and
//! blink an LED while each note sounds, so the pattern is both heard and seen. It is generated sample by sample, so it
//! needs no table and can be tested on the host.
//!
//! The last note is held for 0.3 s at 1008 Hz, which is what a phone tuner app can lock on to: that pitch checks the
//! real sample rate (the clock plan), as the Firmware chapter's bring-up plan describes.

use crate::SAMPLE_RATE;

/// One note of a melody: `hz == 0.0` is a rest.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Note {
    pub hz: f32,
    pub ms: u32,
}

/// E5, G5 and B5-ish (1008 Hz), with 40 ms gaps. About 0.58 s in all.
pub const STARTUP: [Note; 5] = [
    Note { hz: 659.3, ms: 100 },
    Note { hz: 0.0, ms: 40 },
    Note { hz: 784.0, ms: 100 },
    Note { hz: 0.0, ms: 40 },
    Note { hz: 1008.0, ms: 300 },
];

/// Peak level of the notes (1500 of 32768, about -27 dBFS): audible, nowhere near the limiter.
pub const LEVEL: f32 = 1500.0 / 32768.0;

/// Each note fades in and out over this long, so the exciter does not click.
const RAMP_MS: f32 = 5.0;

/// A melody played one sample at a time.
pub struct Melody<'a> {
    notes: &'a [Note],
    index: usize,
    pos: u32,
    phase: f32,
}

/// What [`Melody::next_sample`] returns.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Tone {
    /// The sample, -1.0 ..= 1.0.
    pub value: f32,
    /// True while a note (not a rest) is sounding: drive the LED from this.
    pub on: bool,
}

impl<'a> Melody<'a> {
    pub const fn new(notes: &'a [Note]) -> Self {
        Melody { notes, index: 0, pos: 0, phase: 0.0 }
    }

    /// The next sample, or `None` when the melody has finished.
    pub fn next_sample(&mut self) -> Option<Tone> {
        let note = *self.notes.get(self.index)?;
        let len = (note.ms as f32 * 1e-3 * SAMPLE_RATE) as u32;
        let tone = if note.hz > 0.0 {
            let ramp = RAMP_MS * 1e-3 * SAMPLE_RATE;
            let from_end = (len - self.pos) as f32;
            let env = (self.pos as f32 / ramp).min(from_end / ramp).min(1.0);
            self.phase += note.hz / SAMPLE_RATE;
            if self.phase >= 1.0 {
                self.phase -= 1.0;
            }
            Tone { value: LEVEL * env * libm::sinf(core::f32::consts::TAU * self.phase), on: true }
        } else {
            Tone { value: 0.0, on: false }
        };
        self.pos += 1;
        if self.pos >= len {
            self.index += 1;
            self.pos = 0;
            self.phase = 0.0;
        }
        Some(tone)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn play() -> std::vec::Vec<Tone> {
        let mut m = Melody::new(&STARTUP);
        std::iter::from_fn(|| m.next_sample()).collect()
    }

    #[test]
    fn lasts_about_half_a_second() {
        let secs = play().len() as f32 / SAMPLE_RATE;
        assert!((0.55..0.62).contains(&secs), "{secs}");
    }

    #[test]
    fn is_quiet_and_starts_and_ends_at_zero() {
        let s = play();
        assert!(s.iter().all(|t| t.value.abs() <= LEVEL * 1.001));
        assert!(s.iter().any(|t| t.value.abs() > LEVEL * 0.95));
        assert!(s[0].value.abs() < 0.001 && s[s.len() - 1].value.abs() < 0.001);
    }

    #[test]
    fn led_flags_make_short_short_long() {
        let s = play();
        let mut runs = std::vec::Vec::new();
        let mut run = 0;
        for t in &s {
            if t.on {
                run += 1;
            } else if run > 0 {
                runs.push(run);
                run = 0;
            }
        }
        if run > 0 {
            runs.push(run);
        }
        let ms: std::vec::Vec<f32> = runs.iter().map(|&n| n as f32 / SAMPLE_RATE * 1e3).collect();
        assert_eq!(ms.len(), 3, "{ms:?}");
        assert!((ms[0] - 100.0).abs() < 2.0 && (ms[1] - 100.0).abs() < 2.0 && (ms[2] - 300.0).abs() < 2.0, "{ms:?}");
    }

    #[test]
    fn last_note_is_at_the_tuner_pitch() {
        // Count rising zero crossings in the last 250 ms, which is inside the held note.
        let s = play();
        let n = (0.25 * SAMPLE_RATE) as usize;
        let tail = &s[s.len() - n - 100..s.len() - 100];
        let crossings = tail.windows(2).filter(|w| w[0].value < 0.0 && w[1].value >= 0.0).count();
        let hz = crossings as f32 / (n as f32 / SAMPLE_RATE);
        assert!((hz - 1008.0).abs() < 8.0, "{hz}");
    }

    #[test]
    fn an_empty_melody_ends_at_once() {
        assert!(Melody::new(&[]).next_sample().is_none());
    }
}

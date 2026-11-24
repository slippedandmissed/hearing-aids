//! Offline windowed-sinc resampler. Quality matters more than speed here, and the input is a test file.

const HALF_WIDTH: isize = 24; // sinc lobes each side, at the lower of the two rates

fn sinc(x: f64) -> f64 {
    if x.abs() < 1e-9 { 1.0 } else { (std::f64::consts::PI * x).sin() / (std::f64::consts::PI * x) }
}

/// One output sample at input position `t` (in input samples), from a buffer whose index 0 is input position 0.
fn at(input: &[f32], t: f64, cutoff: f64, reach: isize) -> f32 {
    let centre = t.floor() as isize;
    let mut acc = 0.0f64;
    for k in (centre - reach + 1)..=(centre + reach) {
        if k < 0 || k as usize >= input.len() {
            continue;
        }
        let d = k as f64 - t;
        let w = 0.5 + 0.5 * (std::f64::consts::PI * d / reach as f64).cos(); // Hann
        acc += input[k as usize] as f64 * cutoff * sinc(d * cutoff) * w;
    }
    acc as f32
}

fn geometry(from: f32, to: f32) -> (f64, f64, isize) {
    let ratio = from as f64 / to as f64; // input samples per output sample
    let cutoff = (1.0 / ratio).min(1.0); // low-pass at the lower Nyquist
    (ratio, cutoff, (HALF_WIDTH as f64 / cutoff).ceil() as isize)
}

pub fn to_rate(input: &[f32], from: f32, to: f32) -> Vec<f32> {
    if (from - to).abs() < 0.5 {
        return input.to_vec();
    }
    let (ratio, cutoff, reach) = geometry(from, to);
    let n_out = (input.len() as f64 / ratio).floor() as usize;
    (0..n_out).map(|n| at(input, n as f64 * ratio, cutoff, reach)).collect()
}

/// The same resampler for a live stream: feed it blocks of any size, collect what it can produce.
/// Its delay is `reach` input samples (see `delay_ms`).
pub struct Stream {
    ratio: f64,
    cutoff: f64,
    reach: isize,
    from: f32,
    /// Input history; index 0 is input position `base`.
    buf: Vec<f32>,
    /// Position of the next output, in the same coordinates as `buf` indices.
    pos: f64,
}

impl Stream {
    pub fn new(from: f32, to: f32) -> Self {
        let (ratio, cutoff, reach) = geometry(from, to);
        // Zero history in front, as the offline version sees before the start of a file.
        Self { ratio, cutoff, reach, from, buf: vec![0.0; reach as usize], pos: reach as f64 }
    }

    /// Delay the resampler adds, ms.
    pub fn delay_ms(&self) -> f32 {
        1000.0 * self.reach as f32 / self.from
    }

    pub fn push(&mut self, input: &[f32], out: &mut Vec<f32>) {
        self.buf.extend_from_slice(input);
        while (self.pos.floor() as isize + self.reach) < self.buf.len() as isize {
            out.push(at(&self.buf, self.pos, self.cutoff, self.reach));
            self.pos += self.ratio;
        }
        let drop = (self.pos.floor() as isize - self.reach).max(0) as usize;
        self.buf.drain(..drop);
        self.pos -= drop as f64;
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn tone(rate: f32, hz: f32, n: usize) -> Vec<f32> {
        (0..n).map(|i| 0.5 * (2.0 * std::f32::consts::PI * hz * i as f32 / rate).sin()).collect()
    }

    #[test]
    fn tone_keeps_its_amplitude_and_length() {
        let out = to_rate(&tone(48_000.0, 1000.0, 48_000), 48_000.0, 16_129.0);
        assert!((out.len() as i64 - 16_129).abs() <= 1);
        let peak = out[500..out.len() - 500].iter().fold(0.0f32, |m, x| m.max(x.abs()));
        assert!((peak - 0.5).abs() < 0.01, "peak {peak}");
    }

    #[test]
    fn content_above_the_new_nyquist_is_removed() {
        let out = to_rate(&tone(48_000.0, 12_000.0, 48_000), 48_000.0, 16_129.0);
        let peak = out[500..out.len() - 500].iter().fold(0.0f32, |m, x| m.max(x.abs()));
        assert!(peak < 0.01, "aliased peak {peak}");
    }

    #[test]
    fn streaming_matches_offline_for_any_block_sizes() {
        for (from, to) in [(48_000.0, 16_129.0), (16_129.0, 44_100.0), (44_100.0, 48_000.0)] {
            let input = tone(from, 700.0, 20_000);
            let offline = to_rate(&input, from, to);
            let mut s = Stream::new(from, to);
            let mut out = Vec::new();
            let mut i = 0;
            for size in [1usize, 7, 480, 33, 1024].iter().cycle() {
                if i >= input.len() {
                    break;
                }
                let end = (i + size).min(input.len());
                s.push(&input[i..end], &mut out);
                i = end;
            }
            let n = out.len().min(offline.len()) - 10;
            assert!(n > offline.len() / 2);
            let worst = (0..n).map(|k| (out[k] - offline[k]).abs()).fold(0.0, f32::max);
            assert!(worst < 1e-5, "{from}->{to}: worst difference {worst}");
        }
    }
}

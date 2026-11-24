\clearpage

# Firmware

> The signal processing exists and is tested on a PC; nothing has run on the device. This records what exists, what is assumed, how to bring it up on the bench and what is next, and grows as the firmware does.

## Status

| item | state |
|---|---|
| Layout | a cargo workspace in `firmware/`: `hearing-dsp` (`no_std`, no alloc, `f32`; the signal processing, tested on the host), `hearing-xiao` (embassy-nrf [@embassy]; PDM in, DSP, I2S out), `hearing-desktop` (runs the same DSP over WAV files) |
| Device frontend | compiles for `thumbv7em-none-eabihf`; **not run on hardware** |
| What it does | stereo PDM in → one `Ear` per channel (the chain below, set to the `PASSTHROUGH` preset: −6 dB, flat) → stereo I2S out, 16-frame blocks, boot beep |
| Host tools | `hearing-desktop`: `process` (WAV through the chain), `response` (gain by frequency and level), `latency` (group delay), `feedback` (closed-loop simulation), `live` (microphone to headphones; not exercised yet, see the log), `profile` (print a profile as TOML); `--profile FILE.toml` works everywhere a preset does |
| Settings file | `firmware/profiles/device.toml` is read by `hearing-desktop --profile` and baked into the firmware by `hearing-xiao/build.rs`; a misspelt setting stops the build |
| Footprint | about 30 KB flash, 6.7 KB RAM (`.uf2` 60 KB); CPU load **not measured** |
| Flashing | `.uf2` for the XIAO's bootloader [@uf2; @adafruit_bl], application origin `0x27000` (**UNVERIFIED** for this bootloader; no SWD probe needed) |
| DSP | chain below, tested on the host (35 library and 6 desktop tests); feedback canceller written and simulated on **assumed** paths only |
| Settings | changed by reflashing for the first prototype; no Bluetooth or phone app yet ([@trouble] is the candidate host stack if that changes) |

## Signal chain (`hearing-dsp`, one per ear)

| stage | what it does | notes |
|---|---|---|
| input guard | NaN and infinity become 0 | one bad sample would otherwise stay in a filter state for ever |
| high-pass | 4th order, 100 Hz | removes PDM offset, wind and handling rumble |
| feedback canceller | subtracts a prediction of what the exciter will make the microphone hear | NLMS filter, up to 64 taps after a delay; calibrated at boot (next section); off in `PASSTHROUGH` |
| expander | turns the signal down below a level, up to a limit | stops microphone self-noise being amplified in quiet; off in `PASSTHROUGH` |
| band split | 4 bands, Linkwitz-Riley 4th order at 500, 1500, 3000 Hz | all-pass sections keep the phase of every band equal, so equal gains sum to a flat response (tested to within 0.3 dB) |
| compressor | per band: full gain below a threshold, then a 1/ratio slope | level is the RMS of the band (a sine at −30 dBFS peak is −33 dBFS RMS); attack 5 ms, release 60 ms; gain recomputed every 8 samples (0.5 ms) and smoothed |
| exciter EQ | 3 peaking sections | unused (0 dB) until the exciter is measured |
| fade-in | 100 ms at start-up | |
| limiter | linear to 70 % of the ceiling, then a smooth `tanh` knee, then a hard clamp | the safety stage: no input can exceed the ceiling (tested with infinities and 60 dB of gain). It has no look-ahead, so peaks it catches are distorted, not ducked |

Two presets exist. `PASSTHROUGH` is −6 dB flat and is what the device runs. `CONDUCTIVE_GUESS` is about 30 dB for quiet sounds, compressed above −50 dBFS RMS with ratio 2.5, with the expander on; it is an **ESTIMATE** for a roughly flat conductive loss (there is no audiogram) and must not be worn before the feedback margin has been measured. With the placeholder ceiling of −18.2 dBFS the limiter decides loud sounds: at 30 dB of gain anything above about −48 dBFS peak at the input reaches it. `hearing-desktop response --preset conductive` prints the gain by frequency and input level; `hearing-desktop process IN.wav OUT.wav` runs a file through the same code and reports how often the limiter knee was reached.

Not yet in the chain: a howl detector with a notch as a backstop, and any noise reduction. The CPU cost on the XIAO is an estimate (about 25 biquads per ear, a few logarithms per 8 samples, and the canceller's two passes over 64 taps) and has not been measured; whether it fits in the 3968 cycles available per stereo frame is a bench question.

## Feedback

The exciter shakes the head and the earring, and some of that reaches the microphone a moment later. Amplify enough and the loop howls. How much gain is possible before that depends on the path from exciter to microphone, which nobody has measured: it exists only on the bench to come. Everything below is a simulation against **assumed** paths, so the numbers say how much a canceller *can* help, not how much it will.

`hearing-desktop feedback` closes a synthetic path around the real chain. The path is a pure delay (1.5 ms: output buffering, PDM filter, travel) followed by two or three resonances, scaled so its peak magnitude is a chosen coupling (−30 dB by default). Two shapes: *damped* (Q 2–3) and *ringy* (Q 8–10, a long tail). The input is quiet room noise or a speech-like voiced signal at −70 dBFS RMS. "Max stable gain" is the highest whole dB at which the output stays within 3 dB of what the same chain would give with no feedback at all (a conservative margin, short of actual instability). "Fidelity" is the output against that no-feedback ideal at a gain 6 dB under the uncancelled limit.

**A plain adaptive filter is the wrong tool.** An always-adapting NLMS filter adds 13–19 dB of stable gain, and wrecks the sound: voiced fidelity falls from 12 dB to 3 dB. The reason is that the loop's output *is* the input, amplified, so a filter that learns "what the output will do to the microphone" learns to cancel vowels too. A test keeps this documented (`a_fast_always_adapting_filter_cancels_the_wanted_sound`).

**What the firmware does instead.** For 3 s after boot the chain is replaced by quiet noise (−40 dBFS RMS) that the device makes itself; with no speech around, a fast NLMS filter measures the path cleanly. After that the filter runs with a very small step (0.002) and is pulled back toward the calibrated filter (0.1 % per sample), so it can follow a little but cannot learn the speech. Wear the earrings in place when switching on. The two ears use different noise.

| path | input | no canceller | with canceller | when the path drifts |
|---|---|---|---|---|
| damped | noise | 30 dB | +12 dB | +6 dB |
| damped | voiced | 30 dB | +16 dB | +7 dB |
| ringy | noise | 33 dB | +8 dB | +4 dB |
| ringy | voiced | 33 dB | +13 dB | +5 dB |

(Max stable gain; "drift" moves the resonances 7 % up, adds 3 dB of coupling and one sample of delay half way through. Voiced fidelity with the canceller stays within 1.5 dB of the same chain without one, and is better where the feedback had been colouring the sound.) Two properties matter more than the table. First, the gain depends on the delay setting being at or below the real onset of the path: set too low it is harmless (the window starts early), set too high (32 samples against an onset of 25) the benefit drops from +16 to +3 dB. Second, the trade between following a changing path and damaging speech is a smooth curve in the simulator; the settings above sit at the safe end. The way past it is an adaptation signal that is not correlated with speech (a little probe noise while running, or adapting only in quiet), which is not written.

On the bench, the calibration noise can be recorded to measure the real path, which settles the delay, the coupling and whether 64 taps (4 ms) reach the tail.

## Bench bring-up

The order for the day the boards arrive. It needs a multimeter, your ears, a phone with a tuner app and the XIAO's USB cable; it does not need an oscilloscope. Each stage says what to expect and what a miss means. The firmware has **never run on hardware**: expect the first stages to find things.

| # | do | expect | if not |
|---|---|---|---|
| 0 | Continuity and voltages of Steps 3 and 10 of the assembly guide, before any firmware | VBAT 3.7–4.2 V at pad 3; 3.3 V across C4 on each dangle; no VBAT-to-GND beep | do not flash; fix the wiring first |
| 1 | Flash `firmware/hearing-xiao.uf2` (double-tap reset, copy to the drive). Open `INFO_UF2.txt` on the drive first and note the bootloader and SoftDevice lines | the board restarts and the red charge/power LED behaves as before | the application start address `0x27000` is **unverified**; if the board falls back to the bootloader or never starts, compare it with the SoftDevice size in `INFO_UF2.txt` and change `memory.x` |
| 2 | Switch on with each exciter held in your fingers, not on your head | a short 1 kHz beep (0.3 s) from both exciters | silence from both: the amplifier may reject 16.129 kHz (risk 1); silence from one: the Troubleshooting table |
| 3 | Play the beep against a tuner app | about 1008 Hz (the beep is a 16-sample sine at 16.129 kHz); a different pitch means a different real sample rate, and a ratio of the two readings tells you by how much | this is the no-scope test of the clock plan: a clean beep at the right pitch means the PDM and I2S clocks are what the code says |
| 4 | Talk near each bear's microphone hole, exciter still in your fingers | a quiet copy of your voice (the default profile is −6 dB flat) | no sound: mic clock or data wiring (risk 2), or the dangle's L/R strap; cover one bear's hole to confirm each ear hears its own microphone |
| 5 | Put the exciters on your head as in Step 15, at the default (−6 dB) profile | a clean, quiet copy of your voice, no squeal | squeal at −6 dB means the loop gain is already near 1: stop and measure it as in stage 6 |
| 6 | **Measure the feedback margin** with a reflash ladder: edit `firmware/profiles/device.toml`, set all four `gain_db` to 0, 6, 12, 18, 24 dB in turn, flash, talk. Note the highest gain with no squeal, with the canceller off. Then repeat the same ladder with the canceller on (the `[feedback]` table below), so the two numbers are comparable | one number for each: **max stable gain without and with the canceller**, directly comparable with the simulator's table | squeal at the lowest rung: the coupling is much stronger than assumed; the answer is mechanical (mic seal, arm), not firmware |
| 7 | Listen for crackles with the canceller on | clean | crackling or dropouts mean the DSP does not fit in the time available (the CPU cost is **unmeasured**); say so, and see the telemetry step |

To use a gain other than −6 dB, replace the bands in `firmware/profiles/device.toml` (arrays are replaced whole), for example for 12 dB:

```toml
preset = "passthrough"
bands = [
  { gain_db = 12.0, threshold_dbfs = 0.0, ratio = 1.0 },
  { gain_db = 12.0, threshold_dbfs = 0.0, ratio = 1.0 },
  { gain_db = 12.0, threshold_dbfs = 0.0, ratio = 1.0 },
  { gain_db = 12.0, threshold_dbfs = 0.0, ratio = 1.0 },
]
```

For the canceller-on rungs add this to the same file (the delay stays 0 until the path has been measured):

```toml
[feedback]
taps = 64
delay = 0
mu = 0.002
calibrate_ms = 3000.0
mu_cal = 0.05
probe_dbfs = -40.0
leak = 0.001
```

The canceller listens for 3 s after switching on while the exciter plays quiet noise (a faint hiss): wear the earrings in place first.

Record the results in the manual's tables, flip ESTIMATE to MEASURED where they were measured, and note anything surprising in the log below. The ceiling (`limit_dbfs`) and the hardware power cap stay as they are throughout; do not raise them to get more volume.

What this plan cannot do without more firmware: show the real exciter-to-microphone path (a delay and an impulse response), which needs the calibration noise and the microphone samples sent to a PC over USB serial; and show CPU load. Both are the next firmware step, and stage 6 is much easier with them.

## Pin and clock map (as coded)

| signal | XIAO pin | nRF52840 | direction |
|---|---|---|---|
| PDM_CLK | D4 | P0.04 | out |
| PDM_DATA | D5 | P0.05 | in |
| I2S_BCLK | D8 | P1.13 | out |
| I2S_LRCLK | D9 | P1.14 | out |
| I2S_DIN | D10 | P1.15 | out |
| I2S MCK (unused externally, parked) | D0 | P0.02 | out |
| Charge-current select | | P0.13 | input = 50 mA, drive low = 100 mA |

PDM clock = 32 MHz / 31 = 1.032 MHz, ratio 64 → 16.129 kHz; the I2S master clock is derived from the same 32 MHz, so no sample-rate converter is needed ([@nrf52840_ps]). Memory: flash origin `0x27000`, length `0xCD000`; RAM origin `0x20000008`.

## Latency

`hearing-desktop latency` measures the group delay of the DSP chain from the phase slope of sine tones: about 0.8 ms at 1 kHz, 0.3 ms at 3 kHz and 0.1 ms at 6 kHz, rising to 2.3 ms at 250 Hz and 3.8 ms at 150 Hz (almost all of it the 4th-order 100 Hz high-pass). That is the DSP only. The device adds capture in 16-frame blocks (up to 1 ms), the hand-over and double-buffered I2S output (about 1 to 2 ms) and the PDM decimation filter (not known), which have been read from the code and **not measured**, so the total is roughly 2 to 4 ms above 1 kHz if nothing else surprises. Whether that comb-filters unpleasantly against the direct sound through a partly blocked ear is a listening question for the bench. A shorter high-pass (2nd order) or 8-frame blocks are the cheap levers if it matters.

## Next, in order

1. First run of `hearing-desktop live` on the Mac with headphones, to judge a profile by ear.
2. Telemetry on the device: the microphone samples and the calibration noise sent to a PC over USB serial (to measure the real feedback path), CPU load from the cycle counter, LED blink codes. Written blind, since there is no hardware to test it on.
3. The bench bring-up above, when the boards arrive.
4. After the first measurements: probe-noise or quiet-gated adaptation if the canceller needs to track, a howl detector with a notch as a backstop, and shorter latency if the bench says it matters.
5. Charge-current control and battery-voltage read-out (careful: do not read the battery voltage with P0.14 high while charging).

## Firmware log

- **2026-11-23 (tools).** `hearing-profile` crate: one TOML file (preset plus overrides, typos rejected) is read by the desktop tool and baked into the firmware by `build.rs`. `latency` command: DSP group delay 0.1 to 0.8 ms above 1 kHz. `live` mode written (streaming resampler tested against the offline one) but **not run**: the session's sandbox could not open the audio device (CoreAudio error `!obj` at the first device query), so it needs a first run on the Mac with headphones. Bench bring-up plan written for a setup with no oscilloscope. The `CONDUCTIVE_GUESS` canceller delay went from 16 to 0 until the real path is measured.
- **2026-11-23 (feedback).** Canceller and closed-loop simulator written. First version (plain NLMS) raised the stable gain a lot and destroyed voiced sound (fidelity 12 → 3 dB); replaced by boot calibration plus a leashed filter, which keeps the sound and still adds 4–16 dB in simulation. Simulated on assumed paths only. The howl metric alone had hidden the damage: a stability number needs a fidelity number beside it.
- **2026-11-23 (later).** DSP chain written and tested on the host: biquads, band split, compressor, expander, EQ, soft limiter. A first compressor detector (rectified peak) read 4 dB low on a sine and was replaced by an RMS detector. Tests that compared a compressed band with its nominal gain were wrong, because a 30 dB band beside 0 dB neighbours has its own shape from the crossover skirts; they now compare with the same band uncompressed.
- **2026-11-23.** Workspace scaffolded: gain and hard limiter in `hearing-dsp`, XIAO frontend ported to it, desktop WAV tool with a windowed-sinc resampler to 16.129 kHz. Host tests pass (10); the device build produces a `.uf2`. Nothing run on hardware.

\clearpage

# Firmware (placeholder)

> Short on purpose: the firmware is not written yet. This records what exists, what is assumed and what is next, and grows as the firmware does.

## Status

| item | state |
|---|---|
| `firmware/passthrough` (Rust, embassy-nrf [@embassy]) | compiles for `thumbv7em-none-eabihf`; **not run on hardware** |
| What it does | stereo PDM in → `process()` → stereo I2S out, 16-sample blocks, hard limiter, low fixed gain, boot beep |
| Footprint | about 13.7 KB flash, 1.2 KB RAM (release build) |
| Flashing | `.uf2` for the XIAO's bootloader [@uf2; @adafruit_bl], application origin `0x27000` (**UNVERIFIED** for this bootloader; no SWD probe needed) |
| DSP | none yet (a `process()` stub with gain and limit) |
| Bluetooth tuning | not started ([@trouble] is the candidate host stack) |
| Phone app | not started (React Native planned) |

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

## Next, in order

1. Bench bring-up on a XIAO + one dangle PCB: tone out, microphone level read-out over USB serial, LED blink codes for self-diagnosis.
2. A `no_std` DSP library, tested on the laptop with WAV files: band equaliser, compressor, hard limiter, feedback cancellation (adaptive filter), noise gate.
3. USB-serial control for tuning (gain per band, limiter threshold).
4. Bluetooth Low Energy tuning service and a React Native app.
5. Charge-current control and battery-voltage read-out (careful: do not read the battery voltage with P0.14 high while charging).

## Firmware log

*(empty: add dated entries here as the firmware develops)*

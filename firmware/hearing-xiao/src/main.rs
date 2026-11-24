//! STEREO mic -> hearing-dsp -> stereo I2S amp for ONE plain XIAO nRF52840 in the necklace box. Two PDM mics share CLK/DATA
//! (left/right by SELECT strap); two I2S amps share BCLK/LRCLK/DIN (left/right slot). Mics and amps are on the earring dangles. Plays a short start-up melody through the exciters and blinks the green LED with it, so the amp/exciter path is audible and the program visibly runs.
//! Sample rate: PDM 1.032 MHz / 64 and I2S MCK (32 MHz / 31) / 64 are the SAME 16.129 kHz, both divided from the 32 MHz clock -> no drift.
#![no_std]
#![no_main]

use embassy_executor::Spawner;
use hearing_dsp::{Config, Ear, Melody, STARTUP, from_i16, to_i16};
use embassy_nrf::gpio::{Level, Output, OutputDrive};
use embassy_nrf::i2s::{self, Config as I2sConfig, MasterClock, MckFreq, MultiBuffering, OutputStream, I2S};
use embassy_nrf::pdm::{self, Config as PdmConfig, Frequency, OperationMode, Pdm, Ratio, SamplerState};
use embassy_nrf::{bind_interrupts, peripherals};
use embassy_sync::blocking_mutex::raw::CriticalSectionRawMutex;
use embassy_sync::channel::Channel;
use panic_halt as _;

/// Stereo frames per block (16 frames ~= 1 ms at 16.129 kHz); N = interleaved samples (L,R,L,R...).
const FRAMES: usize = 16;
const N: usize = 2 * FRAMES;
static BLOCKS: Channel<CriticalSectionRawMutex, [i16; N], 4> = Channel::new();

/// Settings for both ears, from `firmware/profiles/device.toml` at build time (see `build.rs`).
#[allow(unused_imports)]
use hearing_dsp::{Band, EqBand, FeedbackCfg, Gate};
const CONFIG: Config = include!(concat!(env!("OUT_DIR"), "/profile.rs"));

bind_interrupts!(struct Irqs {
    PDM => pdm::InterruptHandler<peripherals::PDM>;
    I2S => i2s::InterruptHandler<peripherals::I2S>;
});

#[embassy_executor::task]
async fn mic_task(mut pdm: Pdm<'static>) {
    pdm.start().await;
    let mut bufs = [[0i16; N]; 2];
    pdm.run_task_sampler(&mut bufs, |buf| {
        let _ = BLOCKS.try_send(*buf); // drop the block if the amp side is behind (keeps latency bounded)
        SamplerState::Sampled
    })
    .await
    .unwrap();
}

#[embassy_executor::task]
async fn amp_task(mut out: OutputStream<'static, i16, 2, N>, mut led: Output<'static>) {
    out.start().await.unwrap();
    // Start-up melody (short, short, long; the last note is 1008 Hz for a tuner app), with the LED on while a note
    // sounds. Level -27 dBFS: audible proof that I2S -> amp -> exciter works, with no test equipment. The LED is
    // active low.
    let mut melody = Melody::new(&STARTUP);
    loop {
        let buf = out.buffer();
        let (mut on, mut done) = (false, false);
        for f in 0..FRAMES {
            let v = match melody.next_sample() {
                Some(t) => {
                    on = t.on;
                    to_i16(t.value)
                }
                None => {
                    on = false;
                    done = true;
                    0
                }
            };
            buf[2 * f] = v;
            buf[2 * f + 1] = v;
        }
        if on { led.set_low() } else { led.set_high() }
        let _ = out.send().await;
        if done {
            break;
        }
    }
    let mut ears = [Ear::new(&CONFIG), Ear::new(&CONFIG.for_right_ear())];
    loop {
        let blk = BLOCKS.receive().await;
        // Interleaved: even = left ear, odd = right ear (swap via the PDM edge setting or the SELECT straps).
        let mut x = [[0.0f32; FRAMES]; 2];
        let mut y = [[0.0f32; FRAMES]; 2];
        for f in 0..FRAMES {
            x[0][f] = from_i16(blk[2 * f]);
            x[1][f] = from_i16(blk[2 * f + 1]);
        }
        ears[0].process(&x[0], &mut y[0]);
        ears[1].process(&x[1], &mut y[1]);
        let buf = out.buffer();
        for f in 0..FRAMES {
            buf[2 * f] = to_i16(y[0][f]);
            buf[2 * f + 1] = to_i16(y[1][f]);
        }
        let _ = out.send().await;
    }
}

#[embassy_executor::main]
async fn main(spawner: Spawner) {
    let p = embassy_nrf::init(Default::default());

    // Mic (on the dangle PCB): PDM CLK = D4 (P0.04), DIN = D5 (P0.05). Any GPIO works; the peripheral pins are configurable.
    let mut pcfg = PdmConfig::default();
    pcfg.frequency = Frequency::Default; // 1.032 MHz
    pcfg.ratio = Ratio::Ratio64; // -> 16.129 kHz
    pcfg.operation_mode = OperationMode::Stereo;
    let pdm = Pdm::new(p.PDM, Irqs, p.P0_04, p.P0_05, pcfg);

    // I2S to the amp on the dangle: SCK=D8 (P1.13), LRCK=D9 (P1.14), SDOUT=D10 (P1.15). The MCK pin is unused by the amp: parked on D0 (P0.02), leave it unconnected.
    let mclk = MasterClock::new(MckFreq::_32MDiv31, i2s::Ratio::_64x);
    let icfg = I2sConfig::default(); // 16-bit, I2S format, stereo: left slot -> left amp, right slot -> right amp
    let buffers = MultiBuffering::<i16, 2, N>::new();
    let out = I2S::new_master(p.I2S, Irqs, p.P0_02, p.P1_13, p.P1_14, mclk, icfg).output(p.P1_15, buffers);

    spawner.spawn(mic_task(pdm).unwrap());
    // XIAO nRF52840 user LED (green, P0.30, lit when the pin is low; UNVERIFIED against this board).
    let led = Output::new(p.P0_30, Level::High, OutputDrive::Standard);
    spawner.spawn(amp_task(out, led).unwrap());
}

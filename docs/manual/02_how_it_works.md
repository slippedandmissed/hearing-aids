\clearpage

# How each part works

For a reader who has soldered a few kits but has not designed audio hardware. Every part gets a short explanation and a **Why this one**: what else was possible and why it lost. Skip it if you already know the territory.

![One ear: where each stage lives and what the signal looks like there.](assets/signal-path.svg)

## Bone conduction and the exciter

Your ear has two routes for sound. In **air conduction** sound travels down the ear canal and moves the eardrum. In **bone conduction** the skull itself vibrates and the fluid in the inner ear moves with it. Wax in the canal blocks the first route; the second is unaffected.

An **exciter** is a loudspeaker motor without the cone: a coil pushes a small mass back and forth, and the housing vibrates whatever it is pressed against. The Dayton DAEX-9-4SM ([@daex9]) is a flat 13 × 26.5 × 5.75 mm slab of 2.3 g, with a 4 Ω coil (3.6 Ω DC) and a mechanical resonance around 1.2 kHz. It is made for pressing on panels, so **pressure** and **position** matter more than they would for a speaker. Too loose and nothing couples into the bone; too tight and it hurts. The printed spring arm sets the pressure (about 2 – 5 N, [Mechanics](#spring-arm)); the best spot, behind the ear on the mastoid, is found by trying.

**Why this one.** The first idea was a clip on the **tragus** (the flap in front of the ear canal), and then a cuff on the **helix** (the rim) with an arm back to the mastoid. A tragus clip will not stay on, and the cuff was dropped when the aid had to be tunable in software. The mastoid is a large, firm surface behind the ear, and the exciter is small and light enough to hang on a glasses stem.

## The microphone: digital, so the long wire does not matter

A **MEMS microphone** is a silicon chip with a tiny membrane. The Knowles SPH0641LM4H-1 ([@sph0641]) has the converter built in and speaks **PDM**, pulse-density modulation: give it a clock of about a megahertz and it answers with single bits whose *density of ones* follows the sound pressure. The XIAO's hardware averages those bits back into ordinary 16-bit samples (*decimation*).

![PDM: two microphones share one clock wire and one data wire. The microphone strapped to GND answers after the rising edge, the one strapped to 3V3 after the falling edge.](figures/system/timing_pdm.png)

That sharing is why one XIAO can hear **both** ears: the left microphone's SELECT pin is tied to ground and the right one's to 3.3 V, so they take turns on the same data wire. The sound hole is the dimple in the bear's belly button, sealed to the board by a ring of silicone so sound can only come in that way.

**Why this one.** The microphone sits in the earring, 60 cm of wire from the processor. An analogue microphone would send a tiny voltage down that wire and pick up every bit of noise on the way. A digital one sends clean ones and zeros, which a long wire barely hurts (this is our reasoning; the noise on the real cable is still to be measured). It also needs no analogue front end: the nRF52840 has PDM hardware built in. The earring also had to be small, and this part is 3.5 × 2.7 mm.

## The amplifier: I2S in, class-D out

The processed sound is numbers, which have to become a voltage again. The **MAX98357A** ([@max98357a]) is a *class-D* amplifier with a digital input. It reads **I2S**, a three-wire audio bus (a bit clock, a left/right frame clock and one data wire), and drives the exciter with a square wave at about 300 kHz whose pulse width follows the audio. The exciter's coil and mass cannot follow 300 kHz, so they follow the average, which is the sound. Class-D is efficient: the amplifier barely warms up, which matters in an earring.

![I2S: both amplifiers listen to the same three wires. Each picks the left or right half of the frame; a pull-up resistor on its SD_MODE pin chooses which (2 kΩ = left, 220 kΩ = right).](figures/system/timing_i2s.png)

![The output stage of the amplifier: a bridge of four switches, the two 22 Ω resistors and the exciter, and what the pulses look like.](assets/circuit-class-d.svg)

Two details. The output is *bridge-tied*, the two outputs swinging in opposition, so the exciter sees up to twice the voltage of a single-ended output. And a 100 kΩ resistor on GAIN_SLOT sets 3 dB, the lowest gain the part offers, because we need very little power.

**Why this one.** The nRF52840 has no digital-to-analogue converter, so the choice was an external DAC plus an analogue amplifier, or one chip that does both. The MAX98357A is that one chip, and its SD_MODE pin lets two of them share one bus, each taking its own channel. It was verified on the supplier listing (LCSC C910544).

## The brain: one XIAO nRF52840 for both ears

The Seeed XIAO nRF52840 ([@xiao_wiki]) is a thumb-sized board around Nordic's nRF52840 ([@nrf52840_ps]): a 64 MHz Cortex-M4F with hardware PDM and I2S blocks, Bluetooth, a USB-C port and a LiPo charger. It listens, runs the DSP and feeds the amplifiers, with the sample timing handled in hardware.

![Both the microphone clock and the amplifier's frame clock are divided down from the same 32 MHz crystal, so they cannot drift against each other.](figures/system/clocks.png)

The one open risk is that 16.129 kHz is 0.8 % above the 16 kHz the amplifier datasheet lists. Class-D amplifiers normally tolerate a few percent, but this is **UNVERIFIED**; [Decisions and open risks](#decisions-and-open-risks) lists what would settle it.

**Why one for both ears.** Early designs put a small computer in every earring. That would have doubled the cost and put a battery in each earlobe. The nRF52840's PDM and I2S blocks are stereo, so one board handles both sides, at the price of 8 wires up each side of the neck. Both earring boards use the same 8-pad connector in the same order, so the long shared bus can be replaced by a second XIAO later without a PCB change if it turns out to be noisy.

**Why the processor is in the chest.** The earring should be light and the cable thin, and a heavy battery on an earlobe is the wrong place for it. Hence the earring holds only the microphone, the amplifier and a regulator, and the necklace box holds everything else.

## Inside the two boards

The parts above live on two kinds of PCB. These diagrams draw them the way a textbook would: every resistor and capacitor with its value, and each chip as a box with a symbol of what happens inside. A name on a pin is a flag, and pins with the same name are joined. They are drawn by hand and `make check` compares every part, value and wire with the routed boards, so they cannot drift from the design.

### The earring board

![The earring board, left variant. Below: the two parts that change on the right-hand board.](assets/circuit-dangle.svg)

- **Regulator U3 with C4 and C5** makes a steady 3.3 V for the microphone alone, from the battery's 3.0 – 4.2 V.
- **Microphone U2** is a moving membrane (a variable capacitor) followed by a ΣΔ converter that turns it into the bit stream. Its SELECT pin is tied to ground on the left board and to 3.3 V on the right, which is how both microphones share one data wire.
- **Amplifier U1** receives I2S, converts it, and drives a class-D bridge. **R_GAIN** to the battery sets the lowest gain, 3 dB. **R_SD** to 3.3 V chooses which half of the I2S frame it plays: 2 kΩ for left, 220 kΩ for right.
- **C1, C2 and C3** smooth the battery voltage: 10 µF covers slow changes, 1 µF and 100 nF the fast ones.
- **R_OUT1 and R_OUT2** are the two 22 Ω resistors in series with the exciter, the hardware power cap described below.

### The bee board

![The carrier board in the bee: the power path, the XIAO, and the signals that fan out to both ears.](assets/circuit-carrier.svg)

- **The power path** runs left to right: the battery plug, the reverse-protection transistor Q1, the switch, the fuse, and then the supply rail (VBAT) with its capacitors and the power light.
- **The XIAO** takes its power from the battery wires on its back pads. It has its own charger, which is why charging only works with the switch on.
- **Ten 33 Ω resistors**: each of the five signals leaves the XIAO and splits, through one resistor to each ear. They slow the clock edges a little, so the long cable does not ring or radiate.
- **Ear pads** are the same eight, in the same order, as the earring board's connector, so each cable is a straight one-to-one harness.

## Power: one cell

![Power tree. The battery feeds the box electronics, the two amplifiers and, through a small regulator in each earring, the microphones.](figures/system/power_tree.png)

A **LiPo cell** swings from 4.2 V (full) to about 3.0 V (empty). The microphone wants 1.62 – 3.6 V, so each earring has its own 3.3 V **LDO regulator** (XC6206, [@xc6206]) for the microphone alone. The rest, from the battery to the switch:

- **A P-channel MOSFET** at the battery input conducts when the cell is the right way round and blocks when it is reversed. LiPo plugs have no standard polarity, and a reversed cell would otherwise destroy the board.

![Q1 with the battery connected both ways round.](assets/circuit-reverse-protection.svg)

- **A slide switch** turns everything off. The SK12D07VG4 is rated for 500 mA; another candidate, the MSK12C02, was rejected because it is only rated for 50 mA.
- **A resettable PTC fuse** limits fault currents.
- **The XIAO's own charger** fills the cell from USB-C whenever the switch is on.

## The hardware power cap

Software has bugs. A firmware error could send a full-scale square wave to the exciter. So each earring puts **two 22 Ω resistors in series** with the exciter, one in each leg. The exciter is only 4 Ω, so the resistors take most of the voltage and limit the current whatever the firmware does:

![Left: exciter power against frequency for different series resistances (ngspice sweep; the exciter's mechanical model is assumed). Middle: the worst case in time, a full-scale 1 kHz square wave through 44 Ω. Right: how the maximum power falls with series resistance; 44 Ω is the fitted value.](figures/sims/exciter_power.png)

With 44 Ω the worst-case drive is about 30 mW at the exciter's resonance and about 88 mA peak in the square-wave case, comfortably inside what the 1206 resistors can dissipate. The price is wasted efficiency and a slightly lower maximum loudness.

**Why a hardware limit.** A limit in firmware is only as good as the firmware, and this device sits against your head. The resistors do not depend on any software being right.

## Feedback

The microphone and the exciter are on the same person, a few centimetres apart, and bone conducts sound well. If the processed sound reaches the microphone loudly enough it is amplified again and the system **howls**. Three things fight this: the microphone is mechanically separated from the exciter (earlobe versus mastoid, a spring arm between them); it sees the outside world through a sealed hole; and the firmware ([Firmware](#firmware-placeholder)) is planned to have a feedback canceller and a gain limit. Whether that is enough is the largest *behavioural* unknown of the project.

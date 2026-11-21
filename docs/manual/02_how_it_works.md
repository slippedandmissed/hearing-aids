\clearpage

# How each part works

This chapter explains the parts for a reader who has soldered a few kits but has not designed audio hardware. Skip it if you already know it.

## Bone conduction and the exciter

Your ear has two routes for sound: **air conduction** (sound waves travel down the ear canal and move the eardrum) and **bone conduction** (the skull itself vibrates, and the fluid in the inner ear moves with it). Wax in the canal blocks the first route; the second is unaffected. A **bone-conduction exciter** is a voice-coil motor without a cone: an electrical signal pushes a small mass back and forth, and the housing vibrates whatever it is pressed against.

The exciter used here (Dayton DAEX-9-4SM, [@daex9]) is a flat 13 × 26.5 × 5.75 mm slab weighing 2.3 g, with a 4 Ω coil (3.6 Ω DC resistance) and a mechanical resonance around 1.2 kHz. It is designed for pressing against panels, so contact **pressure** and **position** matter far more than they do for a speaker: too loose and nothing couples into the bone, too tight and it is uncomfortable. The printed spring arm sets the pressure (about 2 – 5 N, [Mechanics](#spring-arm)); the best spot, behind the ear on the mastoid, is found by trying.

## The microphone: a digital (PDM) MEMS microphone

A **MEMS microphone** is a silicon chip with a tiny membrane. The Knowles SPH0641LM4H-1 ([@sph0641]) has the converter built in and speaks **PDM** (pulse-density modulation): you give it a clock of about a megahertz and it answers with a stream of single bits whose *density of ones* tracks the sound pressure. A louder positive swing means more ones. A low-pass filter in the processor turns the bit stream back into ordinary 16-bit samples (this is called *decimation*).

![PDM: two microphones share one clock wire and one data wire. The microphone strapped to GND answers after the rising edge, the one strapped to 3V3 after the falling edge.](figures/system/timing_pdm.png)

This is why one XIAO can listen to *both* ears: the left microphone has its SELECT pin tied to ground and the right one to 3.3 V, so they take turns on the same data wire. The microphone's sound hole is the dimple in the bear's belly button, sealed to the board with a thin foam or silicone ring so that sound can only enter through it.

## The amplifier: I2S in, class-D out

The signal is processed as numbers, so it has to be turned back into a voltage. The **MAX98357A** ([@max98357a]) is a *class-D* amplifier with a digital input: it reads **I2S** (a three-wire audio bus: a bit clock, a left/right frame clock and one data wire) and drives the exciter with a pulse-width-modulated square wave at about 300 kHz. The exciter's coil and mechanical inertia smooth that into the audio waveform. Class-D is efficient (the amplifier barely warms up), which matters in an earring.

![I2S: both amplifiers listen to the same three wires. Each picks the left or right half of the frame; a pull-up resistor on its SD_MODE pin chooses which (2 kΩ = left, 220 kΩ = right).](figures/system/timing_i2s.png)

Two small details deserve mention. The amplifier output is *bridge-tied*: the two outputs swing in opposition, so the exciter sees up to twice the voltage of a single-ended output. And 3 dB of gain (a 100 kΩ resistor on GAIN_SLOT) is the lowest setting the part offers: we need very little power.

## The brain: XIAO nRF52840 and where 16.129 kHz comes from

The Seeed XIAO nRF52840 ([@xiao_wiki]) is a thumb-sized board around Nordic's nRF52840 ([@nrf52840_ps]): a 64 MHz Cortex-M4F with hardware PDM and I2S blocks, Bluetooth, a USB-C port and a LiPo charger. It listens to the microphones, runs the DSP, and feeds the amplifiers, all with the sample timing handled in hardware.

![Both the microphone clock and the amplifier's frame clock are divided down from the same 32 MHz crystal, so they cannot drift against each other.](figures/system/clocks.png)

The one open risk is that 16.129 kHz is 0.8 % above the 16 kHz the amplifier datasheet lists. Class-D amplifiers normally tolerate a few percent, but this is **UNVERIFIED**; chapter 9 lists the fallback.

## Power: one cell, three jobs

![Power tree. The battery feeds the box electronics, the two amplifiers and, through a small regulator in each earring, the microphones.](figures/system/power_tree.png)

A **LiPo cell** swings from 4.2 V (full) to about 3.0 V (empty), too variable for a microphone that wants 1.62 – 3.6 V, so each earring has a **3.3 V LDO regulator** (XC6206, [@xc6206]) just for the mic. A **P-channel MOSFET** at the battery input conducts when the cell is the right way round and blocks when it is reversed; a **resettable PTC fuse** limits fault currents; a slide switch turns everything off. The XIAO's own charger fills the cell from USB-C whenever the switch is on.

## The hardware power cap

Software can have bugs. A firmware error could in principle send a full-scale square wave to the exciter. So each earring PCB puts **two 22 Ω resistors in series** with the exciter (one in each leg). Because the exciter is only 4 Ω, the resistors take most of the voltage and bound the current whatever the firmware does:

![Left: exciter power against frequency for different series resistances (ngspice sweep; the exciter's mechanical model is assumed). Middle: the worst case in time, a full-scale 1 kHz square wave through 44 Ω. Right: how the maximum power falls with series resistance; 44 Ω is the fitted value.](figures/sims/exciter_power.png)

With 44 Ω the worst-case drive is about 30 mW at the exciter's resonance and about 88 mA peak in the square-wave case, comfortably inside what the 1206 resistors can dissipate. The price is wasted efficiency and a slightly lower maximum loudness: that is the trade this project chose for safety.

## Feedback

The microphone and the exciter are on the same person, a few centimetres apart, and bone conducts sound well. If the processed sound reaches the microphone loudly enough, it is amplified again and the system **howls**. The design fights this in three ways: the mic is mechanically separated from the exciter (earlobe versus mastoid, a spring arm in between), the microphone sees the outside world through a sealed hole, and the firmware (chapter 8) is planned to include a feedback canceller and a gain limit. Whether this is enough is the largest *behavioural* unknown of the project.

## Why one microcontroller serves both ears

Early designs put a small computer in every earring. That would have doubled the cost and put a battery in each earlobe. Instead, the stereo-capable PDM and I2S hardware of the nRF52840 handles both sides, at the cost of running 8 wires up each side of the neck. The wires are chosen so the two sides are *identical* (the same 8-pad connector, the same pad order): if the long shared bus turns out to be noisy, a second XIAO can replace it with no PCB change.

\clearpage

# Overview

## The idea

Chronic wax blockages in both ears make ordinary hearing *conductive*: sound cannot get through the ear canal, but the inner ear behind it is healthy. Skull vibrations bypass the blockage, which is why a bone-conduction device can help on bad days. Instead of a behind-the-ear aid with an ear-mould (which would sit in the blocked canal), this project keeps the canal **open** and delivers sound by pressing a small vibrating *exciter* against the mastoid bone behind each ear.

The design goals, in the order they were decided:

1. **Open ear, bone conduction**, one unit per ear, usable while wearing glasses.
2. **Low latency** (a few milliseconds) so your own voice and the aided copy do not echo.
3. **Digital signal processing** so tuning is done in software, not by swapping resistors: equaliser, compressor, hard limiter, feedback suppression, later a phone app.
4. **Designed on screen**: CAD, PCBs and documentation are all generated from code; assembly needs only through-hole soldering and one fiddly pair of wires.
5. **Appearance**: pink and blue gummy-bear earrings (the microphones) and a bee-shaped necklace pendant (the microcontroller and battery).

## What is in it

![What lives where: the glasses stems and earlobes carry the sensors and transducers, the neck carries two thin cables, the chest carries the computer and battery.](figures/system/architecture.png)

Per ear there are four things: **clips** that snap onto the glasses stem, a printed **spring arm** that curves behind the ear and presses the **exciter** against the mastoid, a **gummy-bear earring** containing a small PCB (microphone, amplifier, regulator) and a short exciter cable. Between the ears and the chest runs an **8-wire cable per ear**, tied to a necklace chain. In the **bee** sits one XIAO nRF52840 microcontroller that listens to both microphones and drives both amplifiers, a 500 mAh battery, a switch, an LED and a USB-C port.

![Signal chain for one ear. The microphone and amplifier are in the earring; the processing is in the necklace box.](figures/system/signal_chain.png)

## Key numbers

| quantity | value | status |
|---|---|---|
| Sample rate (microphone, processing, amplifier) | 16.129 kHz, one 32 MHz clock for all | DERIVED |
| Audio bandwidth | about 0.1 – 7 kHz | ESTIMATE |
| Latency, microphone to exciter | about 3 – 4 ms (16-sample blocks) | ESTIMATE, not measured |
| Maximum exciter power (hardware cap) | about 30 mW sine, about 88 mA peak in a firmware-bug square wave | ESTIMATE (assumed exciter model) |
| Supply | one LiPo cell, 3.0 – 4.2 V | DATASHEET |
| Run time on 500 mAh | about 30 h typical (about 15 mA) | ESTIMATE |
| Charging | USB-C, 50 or 100 mA (firmware selects), about 5 – 10 h | DATASHEET / ESTIMATE |
| Mass on the head, per side | about 6 g on the glasses + about 6 g on the lobe | ESTIMATE |
| Necklace box | 105 × 116 × 17 mm including wings, about 50 g | DERIVED / ESTIMATE |
| Cost, everything | about £215 – 330 (see chapter 5) | ESTIMATE |

## What is *not* done

The firmware is a compile-only skeleton (chapter 8). The PCBs have not been ordered or powered. The 16.129 kHz sample rate is outside the amplifier's listed rates by 0.8 % and has not been tried. The stems of the author's glasses were measured only with a ruler, so the clips are printed in a range of sizes (chapter 4). The risks are listed honestly in chapter 9.

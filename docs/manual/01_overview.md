\clearpage

```{=latex}
\part{The project}
```

# Overview

## The idea

Chronic wax blockages in both ears make hearing *conductive*: sound cannot get through the ear canal, but the inner ear behind it is healthy. Vibrations in the skull bypass the blockage, so a bone-conduction device can help on bad days. A behind-the-ear aid with an ear-mould would sit in the blocked canal. This one keeps the canal **open** and presses a small vibrating *exciter* against the mastoid bone behind each ear.

The goals, in the order they were decided:

1. **Open ear, bone conduction**, one unit per ear, usable with glasses.
2. **Low latency**, a few milliseconds, so your own voice and its aided copy do not echo.
3. **Tuning in software**: equaliser, compressor, limiter, feedback suppression, later a phone app. No swapping resistors.
4. **Designed on screen** from code (CAD, PCBs, drawings), buildable with a soldering iron and no SMD work.
5. **Fun to wear**: pink and blue gummy-bear earrings (the microphones) and a bumblebee pendant (the computer and battery).

## The whole thing

Per ear: **clips** on the glasses stem, a printed **spring arm** that reaches behind the ear and presses the **exciter** on the mastoid, and a **gummy-bear earring** holding a small PCB (microphone, amplifier, regulator). An 8-wire cable per ear runs down the neck to the **bee**, which holds one XIAO nRF52840 that listens to both microphones and drives both amplifiers, a 500 mAh battery, a switch, an LED and a USB-C port. [How each part works](#how-each-part-works) explains each of them.

![Where everything sits, and the path one ear's sound takes.](assets/system-overview.svg){height=43%}

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
| Cost, everything | £300.05 paid (every order placed); about £305 – 317 projected in total, the difference being UK import charges still to come (see [Parts and cost](#parts-and-cost)) | MEASURED (paid) / ESTIMATE (rest) |

## Where it stands

Designed, ordered and not yet built. The firmware is a compile-only skeleton ([Firmware](#firmware-placeholder)), nothing has arrived or been powered, and the clip's grip on real glasses is unproven. [Decisions and open risks](#decisions-and-open-risks) lists what could still go wrong.

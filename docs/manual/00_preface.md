**What this is.** A pair of DIY *open-ear* hearing aids that deliver sound by bone conduction. A microphone hangs from each earlobe inside a gummy-bear earring, a microcontroller in a bee-shaped necklace box processes the sound, and a vibrating transducer held against the bone behind each ear by a spring arm clipped to the glasses plays it back. Nothing goes in the ear canal.

\clearpage

# About this document {-}

This is a **working document**: a combined *datasheet* (what each part is and what it can do), *user manual* (how to build, wear and look after it) and *project log* (what was decided and why). Everything in it is generated from the repository: change a parameter in the CAD, a netlist in the PCB scripts or a number in the parts list, run `make docs`, and every drawing, table, render and cost figure is rebuilt.

**Reading guide.**

- Chapter 1 gives the idea in two pages. Chapter 2 explains how each piece works at a hobbyist level.
- Chapters 3 and 4 are the datasheet half: the electronics (two custom PCBs, wiring, simulations) and the mechanics (glasses clips, spring arm, bears, bee box, blueprints and renders of the print files).
- Chapter 5 lists every part and what it should cost. Chapter 6 is the IKEA-style assembly guide for when the parts arrive.
- Chapter 7 covers use, safety and troubleshooting; chapter 8 is a placeholder for the firmware; chapter 9 is the project log with open risks. The appendix explains the repository and how to regenerate this PDF.

**Status words used throughout.** The project is designed entirely on screen; **no part has been built or powered yet**. So every number carries one of these tags:

| tag | meaning |
|---|---|
| **DATASHEET** | read from a manufacturer datasheet or product page |
| **MEASURED** | measured on the author's own glasses or head (ruler, ±0.5 mm) |
| **DERIVED** | calculated from other numbers in this document |
| **ESTIMATE** | a reasoned guess with stated assumptions; replace by measurement |
| **UNVERIFIED** | depends on something nobody has tested on hardware yet |

> **Safety and scope.** This is a hobby and learning project, *not a medical device*. It has not been tested on hardware or on people, and it does not replace an audiogram, a clinician, or treatment for the wax blockages that motivated it. The hardware limits the transducer power in two independent ways (a hard limiter in firmware and a series resistor network on each PCB), but you remain responsible for keeping the volume at a comfortable level. Stop at once if anything hurts, buzzes uncomfortably, or you feel dizzy.

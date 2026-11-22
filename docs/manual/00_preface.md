**What this is.** A pair of DIY *open-ear* hearing aids that deliver sound by bone conduction. A microphone hangs from each earlobe inside a gummy-bear earring, a microcontroller in a bee-shaped necklace box processes the sound, and a vibrating transducer held against the bone behind each ear by a spring arm clipped to the glasses plays it back. Nothing goes in the ear canal.

\clearpage

# About this document {-}

This is a **working document**, and it may be unfinished: the project is designed on screen and the parts are being ordered and assembled. It has three parts.

- **The project** (chapters 1 – 4) is the part to read. The idea, how each piece works and why it was chosen, why the plastic is shaped as it is, and the decisions and open risks.
- **Build and use** (chapters 5 – 7) is the assembly guide for when the parts arrive, followed by use, care and safety, and the firmware status.
- **Reference** (chapters 8 – 11 and the appendix) is for looking things up: the electronics and mechanical datasheets, the cost ledger, and the project log.

The diagrams in the first two parts are mostly drawn by hand (plain-text SVG files in `docs/assets/`) and are edited when the design changes. The pictures in the reference part, the tables and the cost figures are generated from the repository: change a parameter, a netlist or a number in the parts list, run `make docs`, and they are rebuilt.

**Status words used throughout.** The project is designed entirely on screen; **no part has been built or powered yet**. So every number carries one of these tags:

| tag | meaning |
|---|---|
| **DATASHEET** | read from a manufacturer datasheet or product page |
| **MEASURED** | measured on the author's own glasses or head (ruler ±0.5 mm; calipers for the glasses stem) |
| **DERIVED** | calculated from other numbers in this document |
| **ESTIMATE** | a reasoned guess with stated assumptions; replace by measurement |
| **UNVERIFIED** | depends on something nobody has tested on hardware yet |

> **Safety and scope.** This is a hobby and learning project, *not a medical device*. It has not been tested on hardware or on people, and it does not replace an audiogram, a clinician, or treatment for the wax blockages that motivated it. The hardware limits the transducer power in two independent ways (a hard limiter in firmware and a series resistor network on each PCB), but you remain responsible for keeping the volume at a comfortable level. Stop at once if anything hurts, buzzes uncomfortably, or you feel dizzy.

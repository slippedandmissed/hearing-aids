\clearpage

# Decisions and open risks

The choices that shape the project, and what would prove each one wrong. The reasoning behind them is in [How each part works](#how-each-part-works) and [The mechanics, and why](#the-mechanics-and-why).

## Decisions at a glance

| decision | the alternative | why |
|---|---|---|
| Bone conduction on the mastoid | a clip on the tragus, a cuff on the helix | the clip would not stay on; the mastoid is a large, firm surface |
| Digital signal processing | an analogue AGC chain | tuning without a soldering iron; an app later |
| One XIAO for both ears | one per ear | half the cost and one battery; the risk is the long shared bus |
| Microphone and amplifier in the earring, processor in the chest | everything in the ear | weight on the ear and thin cables |
| PDM digital microphone | an analogue microphone | clean bits over 60 cm of wire; hardware PDM on the XIAO |
| I2S class-D amplifier | a DAC plus an analogue amplifier | the nRF52840 has no DAC; one chip; two share a bus |
| Hardware power cap, 2 × 22 Ω | a firmware limit only | protects against firmware bugs |
| A spring-jaw clip that grips | an exact-fit clip | a 3× lever, a tapered and twisted stem, and measurement error |
| XIAO soldered into the carrier, battery in a wing | a socket, a stacked battery | 15.8 mm thick versus 22 – 29 mm |
| Paint on grey, dyed black for flexing parts | colour printing | MJF is grey or black only; paint cracks where parts flex |
| 30 AWG ribbon | 28 AWG | 28 AWG wires (1.2 mm) are too fat for the cable slot |
| Makefile | a justfile | file-based dependencies; nothing extra to install |
| Commit the router result as a lock | regenerate every time | the router's input is not reproducible, so a rebuild could route worse |

## Open risks and what would settle each

| # | risk | settled by |
|---:|---|---|
| 1 | The amplifier rejects 16.129 kHz | first power-up: the boot beep is audible and at the right pitch (tuner app); a frequency counter or scope on LRCLK if one is available |
| 2 | The microphone clock margin of 0.8 % | a bench test across temperature |
| 3 | Noise on the shared 8-wire, 60 cm bus | a real cable test |
| 4 | Feedback between the exciter and the microphone | a listening test, then the feedback canceller |
| 5 | Bone-conduction coupling at the mastoid | wearing it |
| 6 | Clip grip on the real stem (thickness is measured, 3.54 mm; the height at 127 mm is interpolated) | the first fitting |
| 7 | The assumed heights of the JST socket, headers and battery | the real parts |
| 8 | JLCPCB's review of the assembled order (the microphone is flagged *difficult*) | their email after the order |
| 9 | Weight on the lobe (about 6 g) | wearing it |
| 10 | Room in the cable slot for two ribbons and the exciter wires | the dry-fit in Steps 8 and 9 |
| 11 | Gesso sticking to MJF nylon | a test on a spare print |

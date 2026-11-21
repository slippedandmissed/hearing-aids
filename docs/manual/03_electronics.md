\clearpage

# Electronics datasheet

Three boards are *designed* in this project; none has been ordered. All three are drawn in KiCad's Python API from scripts, routed with Freerouting [@freerouting], checked with KiCad's design-rule checker [@kicad], and exported as Gerber/BOM/CPL files for JLCPCB assembly [@jlcpcb_cap]. Part numbers are LCSC (JLCPCB's catalogue) numbers; stock and "extended part" fees must be re-checked on the order page.

## Dangle PCB (one per ear, two variants)

A 13 × 28 mm, two-layer board that lives inside the gummy bear. All parts are on the top side so JLCPCB can assemble it in one pass; the bottom side is a ground plane with a large **L** or **R**, the pad key and the signature.

| item | value |
|---|---|
| Size / layers / thickness | 13 × 28 mm, corner radius 1 mm / 2 / 1.6 mm FR-4 |
| Supply | VBAT straight from the cell (3.0 – 4.2 V), mic on a local 3.3 V LDO |
| Interfaces | 8 through-hole pads for the neck cable; 2 through-hole pads for the exciter |
| Variants | **LEFT**: SD_MODE pulled up through 2 kΩ, mic SELECT to GND. **RIGHT**: SD_MODE through 220 kΩ, mic SELECT to 3V3 |
| Quiescent current | about 3 mA (amplifier 2.4 mA, microphone about 0.6 mA) [@max98357a; @sph0641], ESTIMATE |
| Output cap | 2 × 22 Ω in series with the exciter (about 30 mW worst case) |
| Assembly | JLCPCB, economic PCBA, single side |

![Dangle PCB schematic, LEFT variant (the RIGHT variant differs only in the two straps marked in pink).](figures/circuits/dangle_L_schematic.png)

![Dangle PCB schematic, RIGHT variant.](figures/circuits/dangle_R_schematic.png)

### Connector pinout

| pad | signal | direction (from the box) | notes |
|---:|---|---|---|
| 1 | I2S_LRCLK | out | frame clock, 16.129 kHz |
| 2 | I2S_DIN | out | audio data, left and right slots |
| 3 | VBAT | power | straight from the battery, 3.0 – 4.2 V |
| 4 | PDM_DATA | in | microphone bit stream (both ears share the wire) |
| 5 | I2S_BCLK | out | bit clock, about 516 kHz |
| 6 | GND | power | |
| 7 | PDM_CLK | out | microphone clock, 1.032 MHz |
| 8 | GND | power | second ground, run next to the clock lines |
| EXC+ / EXC− | exciter | out | bridge-tied amplifier output through 22 Ω each |

### Bill of materials (JLCPCB assembles all of these)

LEFT variant:

<!-- include: tables/jlc_dangle_L.md -->

RIGHT variant (same, except the SD_MODE resistor and the mic strap):

<!-- include: tables/jlc_dangle_R.md -->

### Layout

![Dangle PCB, top (component) side and bottom side, left variant. KiCad 3D render.](figures/renders/pcb_dangle_L_top.png){width=28%} ![](figures/renders/pcb_dangle_L_bottom.png){width=28%}

![Right variant, top and bottom.](figures/renders/pcb_dangle_R_top.png){width=28%} ![](figures/renders/pcb_dangle_R_bottom.png){width=28%}

![Mechanical drawing with pad positions and the microphone port.](figures/blueprints/dangle_pcb.png)

**Design notes.** The microphone is *bottom-port*: its sound hole (0.5 mm NPTH) goes through the board toward the bare bottom face, which is held against a sealing ring on the bear's front wall. The amplifier's exposed pad and the microphone's ground ring are tied to the bottom ground plane with vias. The two 22 Ω resistors are 1206 so they can dissipate the worst case without drama.

## Carrier PCB (necklace box)

A 56 × 40 mm, two-layer board (corner radius 9 mm to fit the bee's thorax). The XIAO's pin rows are soldered **directly into the board** (no sockets: they would add 8.5 mm of height), sitting 2.5 mm above it on the pins' plastic spacers.

| item | value |
|---|---|
| Size / layers | 56 × 40 mm, r 9 mm / 2 (bottom = ground plane) |
| Power path | JST-PH battery plug → AO3401A reverse-polarity P-FET → SK12D07VG4 slide switch → 500 mA PTC → VBAT; 22 µF + 100 nF; red LED with 2.2 kΩ |
| Signals | five XIAO pins (PDM_CLK D4, PDM_DATA D5, I2S_BCLK D8, I2S_LRCLK D9, I2S_DIN D10) each through a 33 Ω series resistor to *each* ear block (10 resistors) |
| Ear blocks | two groups of 8 pads (staggered 2 × 4, 2.7 mm pitch), same order as the dangle |
| Mounting | two M2 holes, 50.8 mm apart |
| Battery to XIAO | two 30 AWG wires from the carrier holes B+ / B− to the XIAO's back pads |
| Assembly | JLCPCB places the 33 Ω resistors, caps, LED, PTC and P-FET; **you** solder the JST socket, the switch, the XIAO pins, the ear pads and the two battery wires |

![Carrier PCB schematic. Net names join the circuit: each signal appears on the XIAO and on both ear blocks through its own 33 Ω resistor.](figures/circuits/carrier_schematic.png)

### Bill of materials (JLCPCB assembles these)

<!-- include: tables/jlc_carrier.md -->

You also need: the JST-PH S2B-PH-K socket (C173752), the SK12D07VG4 switch (C393937), and 2 × 8 wire-to-board connections.

![Carrier PCB, top and bottom. KiCad 3D render.](figures/renders/pcb_carrier_top.png){width=60%}

![Mechanical drawing of the carrier PCB (component side) with the XIAO footprint and mounting holes.](figures/blueprints/carrier_pcb.png)

**Charging.** The XIAO has its own USB-C charger. The cell connects to the XIAO's BAT+ and BAT− pads on the *back* of the module (about 1 × 2 mm, 1.9 mm apart; positions from Seeed's board file [@seeed_opl]). The charge current is selected by the XIAO's P0.13 pin (about 50 mA left floating, about 100 mA driven low; [@xiao_wiki]). **Charging only works with the slide switch ON**, because the switch sits between the cell and the XIAO.

### Design rule checks

<!-- include: tables/drc.md -->

All three boards route with **no unconnected nets**. The remaining KiCad messages are cosmetic (silkscreen over copper, the switch's own outline overhanging the board edge) or benign (courtyard overlaps of through-hole wire pads against 1206 resistors, the microphone footprint's own acoustic-port ring).

## Wiring of the parts you assemble yourself

The next figure shows the same system as *you* will see it: the PCBs are black boxes, and only the wires you solder are drawn. Ribbons A and B each carry four wires; wire *n* of ribbon A goes to pad *n*, wire *n* of ribbon B goes to pad *n + 4*, at both ends.

![Wiring of the user-assembled parts. Wire 3 (red) is battery plus; wires 6 and 8 are ground.](figures/system/wiring.png)

**Why 8 wires and not fewer.** Two wires would do for power, but audio data needs a clock and a data line each for the microphones (2), a bit clock, a frame clock and a data line for the amplifiers (3), plus battery plus and *two* grounds so the fast clocks have a return path right next to them. That makes 8. A ground wire is placed between the noisy lines in the connector order; the 33 Ω series resistors at the box end slow the edges so the cable does not radiate or ring.

## Operating conditions

| parameter | value | source / status |
|---|---|---|
| Cell voltage | 3.0 – 4.2 V | LiPo, protected cell, DATASHEET class |
| Amplifier supply range | about 2.5 – 5.5 V | [@max98357a] |
| Microphone supply range | 1.62 – 3.6 V | [@sph0641] |
| Microphone clock (standard mode) | 1.024 – 2.475 MHz | [@sph0641]; ours is 1.032 MHz |
| Amplifier frame rates listed | 8, 16, 32, 44.1, 48, 88.2, 96 kHz | [@max98357a]; ours is 16.129 kHz, UNVERIFIED |
| Typical current from the cell | about 15 mA | ESTIMATE (figure below) |
| Run time, 500 mAh | about 30 h typical, 20 – 55 h range | ESTIMATE |
| Exciter electrical limit | about 30 mW worst case sine; about 88 mA peak in a square-wave fault | ESTIMATE |
| Charging | 50 / 100 mA constant-current from the XIAO | DATASHEET [@xiao_wiki] |
| Ambient temperature | indoor use; not characterised | UNVERIFIED |
| Water | none: sweat and rain are not designed for | |

## Estimates from simulation

![Battery: where the current goes (left) and run time against capacity for three loads (right). All currents are ESTIMATES from datasheet typical values.](figures/sims/battery.png)

![Latency budget against DSP block size. The firmware's 16-sample blocks give about 3.6 ms; beyond about 5 ms the aided sound starts to be heard as an echo.](figures/sims/latency.png)

![The two clock margins that are tight: the microphone clock sits 0.8 % above its minimum, and the amplifier's frame rate is 0.8 % above one of its listed rates.](figures/sims/margins.png)

## Known electrical risks

1. **Amplifier frame rate (16.129 kHz).** Not a listed rate. If the amplifier stays silent or clicks, the fallback is a different PDM/I2S clock plan (all nRF52840 rates are roughly 0.8 % off a listed rate) or a sample-rate converter in firmware.
2. **Microphone clock margin.** 1.032 MHz is only 0.8 % above the lower limit of standard mode; temperature or clock tolerance could push it below. The datasheet's low-power mode is the fallback.
3. **Eight digital wires over about 60 cm** as a shared bus per side. Series resistors, grounds between signals and equal cable lengths mitigate it; only a real test settles it. The fallback is two XIAOs, with no PCB change.
4. **Microphone stock.** The SPH0641LM4H-1 showed about 85 pieces on the JLCPCB listing; check before ordering and consider a spare.
5. **JLCPCB placement orientation (CPL).** Part rotations have not been checked against JLCPCB's preview; do that before paying.
6. **LiPo plug polarity** differs between vendors; check it against the board silkscreen every time.

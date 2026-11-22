# PLAN.md: running state of the project

Last updated 2026-11-21 (end of the documentation and figure-readability pass). The manual (`make docs`) is the detailed record; this file is the short, current status for whoever (human or assistant) picks the work up next. See `CLAUDE.md` for how to work in the repo.

## Goal

Two independent open-ear bone-conduction hearing aids for temporary help on bad-wax days, plus fun and learning. Worn as: glasses-stem clips with a spring arm pressing an exciter on the mastoid, a **gummy-bear earring** (pink left, blue right) holding the microphone and amplifier PCB, and a **bumblebee necklace box** with one XIAO nRF52840 and a LiPo. Not a medical device. Budget ceiling about £200 (flexible; the estimate is now above it).

## State at a glance

| area | state | where |
|---|---|---|
| CAD: stem clips, spring arm, bears (L/R), bee box | **done on screen**, 58 print STLs, all valid | `cad/`, `make print-files` |
| Blueprint drawings, print renders, previews | done | `make docs` |
| Dangle PCB L/R, carrier PCB | **designed, routed, DRC: 0 unconnected nets**; checked in JLCDFM and the assembly preview; **ORDERED 2026-11-22 (£94.84, 5 of each, all 5 assembled); not yet arrived or powered** | `pcb/`, `make pcb` |
| Routing | accepted results committed as locks | `pcb/routes/` (`make reroute` to redo) |
| Firmware | compile-only stereo PDM→I2S passthrough | `firmware/passthrough/`, `make firmware` |
| Manual (datasheet + user manual + log) | generated, 70 pages: illustrated front matter, datasheets, 18 assembly pages, BOM and cost, log. Figures reviewed by eye for colliding text (schematics, block diagrams, charts, blueprints, assembly steps); not every small label has been re-checked | `docs/`, `make docs` |
| Prints / other parts ordered | **PCBs ordered; prints, exciters, XIAO etc. not ordered; no print quote yet** | chapter 5 of the manual, `docs/data/orders.toml` |

Everything is **unverified on hardware**.

## Documentation and figures (how they are built)

- `make docs` regenerates every figure (stamp per group in `docs/build/figures`), the tables from `docs/data/orders.toml` (the cost ledger), the bibliography from `sources.toml` and the PDF. Assembly instructions are one image per step (`docs/figures/assembly.py`); step 0 spans three pages (`step00`, `step00b`, `step00c`).
- Figures are drawn at about page width with large text, because the PDF scales them down: block labels auto-shrink to fit their box (`common.box`), schematic IC blocks wrap their titles and warn on pin/text collisions (`schem.py`), 3D renders subdivide large triangles (`common.draw_tris`) so the depth sort does not glitch.
- Tables use alternating row shading; bibliography URLs wrap; schematics and blueprints sit on landscape pages as vector PDFs.

## Architecture (decisions that hold)

- Bone conduction at the mastoid; exciter pressed by a printed PA12 spring arm (2.4 / 2.8 / 3.2 mm variants) fused to a C-clip on the glasses stem (clip A at station 100 mm, clip B+arm at 127 mm). Clips printed in a fit matrix (stem thickness A–D = 3.34/3.54/3.74/3.94 mm × height 1–3 = −0.4/0/+0.4 mm). The stem is MEASURED with calipers (2026-11-21): 3.54 mm thick, 6.40 mm at the hinge, 4.7 mm at the end of the straight section, 9.36 mm at the paddle; the matrix stays because MJF tolerance (±0.3 mm, holes shrink) equals the 0.25 mm clip clearance. Stations: straight section 105.33 mm (measured); tallest point 134.72 mm from the hinge in a straight line, modelled at 135 mm along the stem.
- Digital signal path: SPH0641LM4H-1 PDM mic (in the dangle) → XIAO nRF52840 (PDM→16.129 kHz PCM, DSP, I2S) → MAX98357A class-D amp (in the dangle) → 2 × 22 Ω hardware power cap → DAEX-9-4SM. **One** XIAO serves both ears (stereo PDM/I2S); 8 wires per ear in two 4-wire silicone ribbons (VBAT, 2 GND, PDM clk/data, I2S ×3), same pad order on both PCBs.
- Dangle PCB 13 × 28 mm, all SMD on top, bottom = ground plane + big L/R + signature; L/R variants differ in R_SD (2 k / 220 k) and the mic SELECT strap.
- Carrier PCB 56 × 40 mm (r 9 mm corners): JST-PH → AO3401A reverse-polarity P-FET → SK12D07VG4 switch → 500 mA PTC → VBAT; LED; ten 33 Ω series resistors; two 8-pad ear blocks; XIAO soldered straight into the board (battery wired to its back pads); XIAO's own charger via its USB-C (works only with the switch ON).
- Bee box: thorax 62 × 46 × 15.8 mm (board), abdomen 44 wide × 10.1 mm (battery pocket), head ball with the chain hole, cosmetic flat wings, raised stripe bumps; overall 105 × 116 × 16.9 mm. Bears 32 × 46 × 7.6 mm with screw posts, mic ring, PCB stops, strain pegs; all cables leave through one top slot.
- Paint rather than multi-colour printing; clips and arm stay unpainted grey MJF PA12.
- Tooling: build123d, KiCad 10 (+ Freerouting 1.9.0), Rust/embassy-nrf, pandoc, Makefile (no `just`).

## Numbers worth remembering (all ESTIMATES unless noted)

- Sample rate 16.129 kHz (32 MHz / 31 / 64), latency about 3–4 ms, worst-case exciter power about 30 mW (assumed exciter model), about 15 mA typical → about 30 h on 500 mAh, mass about 6 g per stem and 6 g per lobe.
- Cost: **£94.84 paid** (JLCPCB, 3 orders, 2026-11-22); projected total about £239–322 (prints £40–80 at an *assumed* £0.3–0.6/cm³ for 137 cm³, lean set about 73 cm³; exciters £25–35; XIAO ×2 £28–34; rest £50–70).

## Open risks (what would settle each)

1. Amplifier rejects 16.129 kHz (first power-up, scope on LRCLK). Fallback: another clock plan or firmware resampling.
2. Mic clock only 0.8 % above its 1.024 MHz minimum.
3. 8 digital wires × 60 cm as a shared bus (fallback: two XIAOs, no PCB change).
4. Feedback between exciter and mic; bone-conduction coupling quality; weight on the lobe.
5. Assumed part heights (JST 7.8, XIAO header plastic 2.5, battery 5.5 mm), stem dimensions.
6. JLCPCB specifics not yet checked: CPL rotations, 0.5 mm NPTH, mic stock (about 85), extended-part fees, Helvetica signature in the silkscreen preview.
7. Print price (not quoted) is above the old £25–50 estimate.

## TODO (next steps, roughly in order)

- [ ] Get print quotes (JLC3DP and a UK MJF bureau) for the full and lean sets; decide.
- [x] Gerbers reviewed in JLCDFM, CPL rotations checked in the assembly preview, **three PCB orders placed 2026-11-22** (£94.84 incl. shipping and import VAT; JLCONE desktop-app discount −£13.64). Watch for JLCPCB's email about the microphone (extended, flagged difficult) and their post-order DFM/placement analysis.
- [ ] Order exciters, XIAO ×2, LiPo (check plug polarity), ribbon cable, small parts, consumables (estimates in `docs/data/orders.toml`; record each real order there as a ledger entry).
- [x] Glasses stem measured with calipers (thickness, three heights); `GlassesParams` and the clip matrix updated.
- [x] Stations measured (straight section 105.33 mm; tallest point 134.72 mm chord).
- [ ] Measure the stem height at 50 mm and at the tip (currently interpolated; tip assumed 4.0 mm).
- [x] Parameter audit against JLC3DP limits (2026-11-21): bear posts 3.4 mm, PCB stops 1.0 mm, engraving 0.8 mm deep, exciter pocket clearance 0.45 mm. Mesh-level audit done 2026-11-22 (`make print-audit`; findings in manual chapter 4). Screw counterbore fixed (0.4 mm deep, 0.8 mm floor, 3.6 mm wide). **Screws chosen: M1.6 × 4 mm (12) and M2 × 4 mm (4), A2 stainless pan head cross recess; the old M2 × 8 would have poked 2.8 mm out of the back of the bee box.** Fixed 2026-11-22: clip engraving 0.6 mm deep (1.0 mm floor), bear cable notch skin 0.8 mm (was 0.5). Kept: 0.75 mm under the engraved L/R. **Ribbon: 30 AWG silicone, 4 wires, 1 m, 5 pieces (wires 0.8 mm; ~0.8 × 3.2 mm per ribbon, inferred); confirm the stacked pair fits the cable slot at the first test fit.**
- [x] JLCDFM (JLCPCB's free checker) run on all three final gerbers 2026-11-21; results table in the manual (chapter 3). Changes made because of it: vias 0.7/0.3 mm; ground vias 0.2 mm from SMD pads; 0.2 mm between via pads; same-net ground stubs 0.15 mm apart; exciter resistors laid flat 2.4 mm from the wire pads (were 0.32 mm); C3 and C5 moved; silkscreen outlines of SMD parts removed; pad digits moved off the pads; bottom text clear of the mic hole; carrier Q1 moved, carrier text 0.17 mm. New routing locks committed.
- [x] Hand edits on top of the router's result are persisted (`pcb/route_edits.py`, `pcb/routes/*.edits.json`, applied after the lock import; see manual chapter 3), so a small fix no longer means a new router run. Used for the carrier and both dangles (2026-11-22).
- [x] Final JLCDFM round 2026-11-22: no red anywhere except carrier THT-to-SMD (8) and dangle R silkscreen-to-hole (14; three ground vias under bottom text, no legal nudge). Carrier: silkscreen text thickened to 0.17 mm and digits 0.8 mm, connector outlines 0.17 mm, one via moved by an edit; PTH-without-pad = the two NPTH mounting holes, slots = XIAO socket oval holes.
- [x] LED D1 polarity checked in the JLCPCB assembly viewer (anode top, matches our footprint).
- [ ] Known residuals, all judged acceptable (reasons in the manual): silkscreen over three vias on dangle R's bottom text (cosmetic gaps in letters); one 0.11 mm pad-spacing warning on both dangles (mic land pattern, not traced); THT-to-SMD on the carrier (battery-wire holes beside the XIAO pads, 8 danger); a same-net via-to-track gap of 0.05-0.06 mm made by the autorouter; 2-3 "via without pad" warnings not understood; KiCad hole clearance relaxed to 0.18 mm (mic land pattern).
- [x] CPL checked in JLCPCB's assembly preview for dangle L (2026-11-21): parts land on their pads, pin-1 markers agree. The CPL used `H - y`, which sat 28 mm off the gerbers; it now uses `-y` (gerber frame) for the dangles and the carrier.
- [x] Assembly previews of dangle R and the carrier viewed 2026-11-22. Dangle R matches L. Carrier: all parts on pads; Q1 (SOT-23) was half a turn out, fixed with a +180° CPL correction in `bom_carrier.py` and re-checked. LED D1 cathode side not readable in the preview (low stakes). Mic C497724 is Extended and flagged 'difficult': you decided to include it and accept the review/fee (about £6.39 per 5 boards in the draft quote).
- [ ] Verify assumed heights against the real JST, headers, battery; adjust `cad/bee_box.py`.
- [ ] Firmware: bench bring-up (tone, mic level over USB serial, LED codes), DSP library tested on WAV files, feedback canceller, USB-serial then BLE tuning, React Native app.
- [ ] After hardware arrives: update the manual's status tags (ESTIMATE → MEASURED) and the assembly chapter with what really happened.
- [ ] Documentation polish: re-check small labels in the figures not yet inspected after the last pass (the mastoid measurement guide, the print-render contact sheets); the BAT+ rail flag on the carrier schematic sits on its wire.
- [ ] Optional polish: straight-on photo of the glasses to refine the preview front; a smaller/lighter bear (the PCB sets a minimum of about 40 mm).

## History (short)

- 2026-11-20: concept (tragus clip → helix cuff → glasses clip + earring + necklace box), parts research, firmware feasibility, dangle and carrier PCBs, housing, soldered-XIAO and battery-wing decisions.
- 2026-11-21: documentation pass: neutral-tone illustrated front matter, redrawn schematics and block diagrams, stacked charts, three-page step 0, shaded tables, wrapped bibliography.
- 2026-11-21: gummy bears and bee, assembly preview, glasses front from photos, carrier r9 corners and signatures, 58 print files, then the repository restructure (Makefile, sources manifest, routing locks, `-dct 0`) and this manual.

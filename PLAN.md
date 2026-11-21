# PLAN.md: running state of the project

Last updated 2026-11-21 (end of the documentation and figure-readability pass). The manual (`make docs`) is the detailed record; this file is the short, current status for whoever (human or assistant) picks the work up next. See `CLAUDE.md` for how to work in the repo.

## Goal

Two independent open-ear bone-conduction hearing aids for temporary help on bad-wax days, plus fun and learning. Worn as: glasses-stem clips with a spring arm pressing an exciter on the mastoid, a **gummy-bear earring** (pink left, blue right) holding the microphone and amplifier PCB, and a **bumblebee necklace box** with one XIAO nRF52840 and a LiPo. Not a medical device. Budget ceiling about £200 (flexible; the estimate is now above it).

## State at a glance

| area | state | where |
|---|---|---|
| CAD: stem clips, spring arm, bears (L/R), bee box | **done on screen**, 58 print STLs, all valid | `cad/`, `make print-files` |
| Blueprint drawings, print renders, previews | done | `make docs` |
| Dangle PCB L/R, carrier PCB | **designed, routed, DRC: 0 unconnected nets**; gerber/BOM/CPL generated; **not ordered, not powered** | `pcb/`, `make pcb` |
| Routing | accepted results committed as locks | `pcb/routes/` (`make reroute` to redo) |
| Firmware | compile-only stereo PDM→I2S passthrough | `firmware/passthrough/`, `make firmware` |
| Manual (datasheet + user manual + log) | generated, 70 pages: illustrated front matter, datasheets, 18 assembly pages, BOM and cost, log. Figures reviewed by eye for colliding text (schematics, block diagrams, charts, blueprints, assembly steps); not every small label has been re-checked | `docs/`, `make docs` |
| Prints / parts ordered | **nothing ordered; no quotes yet** | chapter 5 of the manual |

Everything is **unverified on hardware**.

## Documentation and figures (how they are built)

- `make docs` regenerates every figure (stamp per group in `docs/build/figures`), the tables from `docs/data/parts.toml`, the bibliography from `sources.toml` and the PDF. Assembly instructions are one image per step (`docs/figures/assembly.py`); step 0 spans three pages (`step00`, `step00b`, `step00c`).
- Figures are drawn at about page width with large text, because the PDF scales them down: block labels auto-shrink to fit their box (`common.box`), schematic IC blocks wrap their titles and warn on pin/text collisions (`schem.py`), 3D renders subdivide large triangles (`common.draw_tris`) so the depth sort does not glitch.
- Tables use alternating row shading; bibliography URLs wrap; schematics and blueprints sit on landscape pages as vector PDFs.

## Architecture (decisions that hold)

- Bone conduction at the mastoid; exciter pressed by a printed PA12 spring arm (2.4 / 2.8 / 3.2 mm variants) fused to a C-clip on the glasses stem (clip A at station 100 mm, clip B+arm at 127 mm). Clips printed in a fit matrix (stem thickness A–D = 3.2/3.6/4.0/4.4 mm × height 1–3 = −0.6/0/+0.6 mm) because the stem was measured with a ruler only (thickness assumed 3.5 mm).
- Digital signal path: SPH0641LM4H-1 PDM mic (in the dangle) → XIAO nRF52840 (PDM→16.129 kHz PCM, DSP, I2S) → MAX98357A class-D amp (in the dangle) → 2 × 22 Ω hardware power cap → DAEX-9-4SM. **One** XIAO serves both ears (stereo PDM/I2S); 8 wires per ear in two 4-wire silicone ribbons (VBAT, 2 GND, PDM clk/data, I2S ×3), same pad order on both PCBs.
- Dangle PCB 13 × 28 mm, all SMD on top, bottom = ground plane + big L/R + signature; L/R variants differ in R_SD (2 k / 220 k) and the mic SELECT strap.
- Carrier PCB 56 × 40 mm (r 9 mm corners): JST-PH → AO3401A reverse-polarity P-FET → SK12D07VG4 switch → 500 mA PTC → VBAT; LED; ten 33 Ω series resistors; two 8-pad ear blocks; XIAO soldered straight into the board (battery wired to its back pads); XIAO's own charger via its USB-C (works only with the switch ON).
- Bee box: thorax 62 × 46 × 15.8 mm (board), abdomen 44 wide × 10.1 mm (battery pocket), head ball with the chain hole, cosmetic flat wings, raised stripe bumps; overall 105 × 116 × 16.9 mm. Bears 32 × 46 × 7.6 mm with screw posts, mic ring, PCB stops, strain pegs; all cables leave through one top slot.
- Paint rather than multi-colour printing; clips and arm stay unpainted grey MJF PA12.
- Tooling: build123d, KiCad 10 (+ Freerouting 1.9.0), Rust/embassy-nrf, pandoc, Makefile (no `just`).

## Numbers worth remembering (all ESTIMATES unless noted)

- Sample rate 16.129 kHz (32 MHz / 31 / 64), latency about 3–4 ms, worst-case exciter power about 30 mW (assumed exciter model), about 15 mA typical → about 30 h on 500 mAh, mass about 6 g per stem and 6 g per lobe.
- Cost about £215–330 (JLCPCB £72–103 incl. VAT; prints £40–80 at an *assumed* £0.3–0.6/cm³ for 137 cm³, lean set about 73 cm³; exciters £25–35; XIAO ×2 £28–34; rest £50–70).

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
- [ ] Review the gerbers in JLCPCB's viewer / a gerber viewer; check CPL rotations; confirm mic and amp stock; then order the three PCB orders.
- [ ] Order exciters, XIAO ×2, LiPo (check plug polarity), ribbon cable, small parts, consumables (see `docs/data/parts.toml`).
- [ ] Measure the glasses stem with calipers when available; update `GlassesParams` and prune the clip matrix.
- [ ] Verify assumed heights against the real JST, headers, battery; adjust `cad/bee_box.py`.
- [ ] Firmware: bench bring-up (tone, mic level over USB serial, LED codes), DSP library tested on WAV files, feedback canceller, USB-serial then BLE tuning, React Native app.
- [ ] After hardware arrives: update the manual's status tags (ESTIMATE → MEASURED) and the assembly chapter with what really happened.
- [ ] Documentation polish: re-check small labels in the figures not yet inspected after the last pass (the mastoid measurement guide, the print-render contact sheets); the BAT+ rail flag on the carrier schematic sits on its wire.
- [ ] Optional polish: straight-on photo of the glasses to refine the preview front; a smaller/lighter bear (the PCB sets a minimum of about 40 mm).

## History (short)

- 2026-11-20: concept (tragus clip → helix cuff → glasses clip + earring + necklace box), parts research, firmware feasibility, dangle and carrier PCBs, housing, soldered-XIAO and battery-wing decisions.
- 2026-11-21: documentation pass: neutral-tone illustrated front matter, redrawn schematics and block diagrams, stacked charts, three-page step 0, shaded tables, wrapped bibliography.
- 2026-11-21: gummy bears and bee, assembly preview, glasses front from photos, carrier r9 corners and signatures, 58 print files, then the repository restructure (Makefile, sources manifest, routing locks, `-dct 0`) and this manual.

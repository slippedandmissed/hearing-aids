\clearpage

# Mechanical datasheet

Every shape is a Python script (build123d [@build123d]); dimensions live in a few parameter files, and the drawings and renders in this chapter are generated from the same solids that are sent for printing. The body shown in the previews is a generic CC0 mesh [@makehuman] used only to check scale and fit.

## The assembled picture

![The whole system on the generic body, from the front, back, three-quarters and both ears. Brown: glasses; grey: clips and spring arm; orange: exciter; pink / blue: the bears; silver: chain and ear wires; yellow and black: the bee.](figures/renders/preview_assembly.png)

## Glasses stem, clips and spring arm

### The stem

The glasses are a 57□17-145 frame (lens 57 mm, bridge 17 mm, temple 145 mm). The stem profile, **MEASURED** with calipers on 2026-11-21, is 6.40 mm tall at the hinge, 4.7 mm where the straight section ends and 9.36 mm at the widest part of the rear paddle before it tapers quickly; the thickness is a consistent 3.54 mm along the whole stem. The straight section is 105.33 mm long, and the tallest point is 134.72 mm from the hinge in a straight line; the model puts it at 135 mm along the stem, because the stem bends and the path is slightly longer. A second set of measurements perpendicular to the lens plane gave 113.56 mm and 130.75 mm; those include the hinge's offset from the lens plane, so the model uses the along-the-stem values. Photographs showed that the frame is a cat-eye acetate front with thin translucent-brown temples; the preview's front is a rough interpretation (no lenses).

### Clips

Two **C-clips** snap onto the stem from underneath: **clip A** at 100 mm from the hinge, **clip B** at 127 mm. A clip has a 1.6 mm wall, 0.25 mm clearance and a 14 mm length; its slot on the underside is narrower than the stem so it clicks on. Because the printer's tolerance (±0.3 mm for MJF nylon, and holes print smaller than modelled) is as large as the 0.25 mm clearance, the clips are still printed in a *range of sizes* (stem thickness 3.34 / 3.54 / 3.74 / 3.94 mm, where 3.54 mm is the measured value, × height −0.4 / 0 / +0.4 mm) and you use the smallest that slides on with a click. Following JLC3DP's published limits ([JLC3DP design guideline](https://jlc3dp.com/help/article/212-3D-Printing-Design-Guideline): 1.0 mm recommended wall, 0.5–0.8 mm minimum engraved detail, ±0.3 mm tolerance), the ID text on the clips is engraved 0.8 mm deep in 3.6–4 mm bold text, the bear's screw posts are 3.4 mm across (1.05 mm wall round the 1.3 mm pilot), the PCB stops are 1.0 mm thick and the exciter pocket has 0.45 mm clearance each side (**ASSUMED**; test-fit it first).

### Spring arm {#spring-arm}

Clip B carries a **leaf-spring arm** that curves behind the ear and ends in a plate holding the exciter against the mastoid. It is fused to the clip (one printed part), thin in the direction it flexes and tall in the other, like a miniature glasses temple. The pad force follows the cantilever formula $F = \frac{3EI}{L^3}\,\delta$, where $E$ is the nylon's modulus (about 1.7 GPa for PA12, ESTIMATE), $I = h t^3/12$ with arm height $h = 7$ mm and thickness $t$, $L \approx 55$ mm the free length and $\delta$ the preload (how far the relaxed pad sits proud of the skin, 5 mm).

![Pad force against arm thickness for three preloads, and the bending strain in the arm. The printed variants are 2.4, 2.8 and 3.2 mm; 2.8 mm at 5 mm preload gives about 2 N.](figures/sims/spring_arm.png)

![Stem clips and spring arm, with the stem profile and the three views of the arm part.](figures/blueprints/clips_arm.png)

## Gummy-bear dangle

The bear is a hollow shell with a flat back plate. Seen from the front it is 32.2 × 46.3 mm and 7.6 mm thick. Inside:

- the 13 × 28 mm dangle PCB lies *component side toward the back plate*, its bare bottom face against the front wall, the **microphone port under the belly button**;
- a **ring** around the port presses against the board (add a foam ring or a dab of silicone to seal it);
- **four screw posts** (M1.6 × 4 mm pan-head screws that cut their own thread, pilot Ø1.3 mm, 5.8 mm deep) hold the back plate; each head sits in a Ø3.6 mm counterbore 0.4 mm deep (head about 3.2 mm wide and 1.3 mm tall, not measured; it stands about 0.9 mm proud of the back face), with a Ø2.0 mm clearance hole for the 1.6 mm shank; and two **pillars** on the back plate clamp the board's bare edge strips;
- small **stops** keep the board from sliding sideways; two **pegs** in the head let each cable make a turn before it leaves, as strain relief;
- **all cables leave through one slot at the top of the head**; the hook loop sits above it. The slot is on the *back-of-head* side, so it is on opposite sides of the left and right bears.

![Bear shell (left ear): front, side, and a section through the microphone port with the layers dimensioned.](figures/blueprints/bear_shell.png)

![Back plate: the engraved letter, screw holes (Ø1.8, with a shallow head recess), and the two PCB pillars.](figures/blueprints/bear_backplate.png)

![The bears as printed: shell and back plate in pink (left) and blue (right).](figures/renders/print_bears.png)

## Bee necklace box

The **thorax** (62 × 46 mm, 15.8 mm thick) holds the 56 × 40 carrier PCB on two M2 screw posts and four supports; the **abdomen** (44 mm wide, 10.1 mm thick) is a pocket for the 30 × 35 × 5.5 mm battery; the **head** is a solid ball with the chain hole through it. The cover presses onto the base with a lip. Openings: USB-C on the right edge, the switch lever through the top edge (next to the head), two ear-cable slots in the top edge, an LED window. The flat single-layer **wings** are printed as part of the base and are purely cosmetic.

![Bee box: front, base with the cover off (PCB and battery outlines dashed), side and a section through the thorax.](figures/blueprints/bee_box.png)

![The bee as printed, with the intended paint zones coloured: yellow bumps and black stripe valleys, silver wings.](figures/renders/print_bee.png)

**Assumed heights** that must be checked with the real parts before printing: JST-PH socket 7.8 mm, XIAO pin-header plastic 2.5 mm, USB plug opening 11.6 × 6.8 mm, battery 30 × 35 × 5.5 mm.

![Glasses front close-up on the head model (preview only).](figures/renders/glasses_check.png)

## Mass

![Estimated mass: about 6 g per glasses stem, 6 g per lobe, and about 50 g for the necklace box (mostly nylon and the battery).](figures/sims/mass.png)

## The print files

Everything is printed in plain grey **MJF nylon (PA12)** [@jlc3dp]. Clips and arm stay unpainted; shells and the bee are sanded, primed and painted. Colour regions are 0.4 mm paint wells and raised bumps, not multi-colour printing.

![The finished print files, one of each kind (rendered from the STLs that will be sent for printing).](figures/renders/print_overview.png)

![Clip A in every size of the fit matrix.](figures/renders/print_clips_matrix.png)

![Clip B with spring arm and exciter plate, and the three arm thicknesses.](figures/renders/print_arms.png)

Every part carries an engraved ID so the many near-identical clips can be told apart (the right-ear parts are mirrored, but their text still reads correctly):

![Engraved IDs on clip A (left and right) and clip B + arm (right).](figures/renders/print_engraving.png)

<!-- include: tables/print_summary.md -->

: Print volume by group (all files, with the spare bears) {#tbl:print}

The full file list with volumes, bounding boxes and validity checks is in the appendix. Cost is discussed in chapter 5; **no price has been quoted yet**.

### Mesh audit against JLC3DP's limits

`make print-audit` (`cad/print_audit.py`) measures the real triangles of every STL, not the design parameters. From 12 000 random points on each surface a ray goes into the solid to the opposite wall (the local wall thickness) and out across the air to the next surface (the local gap). It reports the 1st-percentile wall and the share of the surface thinner than 1.0 mm (JLC3DP's recommended wall) and 0.8 mm, and the share of gaps narrower than 0.4 mm (the nylon clearance). Sampling is random, so a very small feature can be missed, and the minimum is not meaningful (every sharp edge is a wedge of near-zero thickness); the percentages are. Run on 2026-11-22, on the files as designed after the JLC3DP parameter audit:

| part | finding | cause |
|---|---|---|
| bear back plates (L, R) | about 4 % of the surface has a 0.5 mm wall, about 8 % is under 1.0 mm, 7 – 8 % under 0.8 mm | three thin places, all traced in `cad/gummy_dangle.py`. The screw-head counterbores were 0.7 mm deep in the 1.2 mm plate (a 0.5 mm floor) and are now 0.4 mm deep (a measured 0.8 mm floor, 1.2 mm of material beyond the counterbore edge). Still open: the wire notch leaves 0.5 mm and the large L or R engraved 0.45 mm into the back leaves 0.75 mm |
| clips A and B | 3 – 5 % (clip A) and about 2 % (clip B) of the surface is 0.8 mm | the engraved IDs are 0.8 mm deep in a 1.6 mm wall, so 0.8 mm is left under the letters; clip B also has a few thin spots near the arm tip (not traced) |
| bear shells | 5 % of the surface under 1.0 mm, 0.6 % under 0.8 mm, one patch of 1.0 mm over the PCB at the top | probably a thin ceiling region near the mic seal (not traced) |
| bee cover and base | 1 – 9 % under 1.0 mm, 1 % under 0.8 mm; two tiny patches 0.3 – 0.5 mm thick | probably lip and flange edges on the cover and an eye well on the base (not traced) |
| narrow gaps (under 0.4 mm) | 0.1 – 0.4 % on the clips and the bear shells | the 0.25 mm clip-to-stem clearance and the 0.4 mm paint wells, by design |

None of these is a wrong model; they are the places where legibility, fit and strength trade against JLC3DP's recommended 1.0 mm wall. JLC3DP's own model check, run when the STLs are uploaded for a quote, has not been consulted yet.

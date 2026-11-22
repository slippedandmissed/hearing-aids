\clearpage

# Mechanical datasheet

Every shape is a Python script (build123d [@build123d]); dimensions live in a few parameter files, and the drawings and renders in this chapter are generated from the same solids that are sent for printing. The body shown in the previews is a generic CC0 mesh [@makehuman] used only to check scale and fit.

## The assembled picture

![The whole system on the generic body, from the front, back, three-quarters and both ears. Brown: glasses; black: clips and spring arm; orange: exciter; pink / blue: the bears; silver: chain and ear wires; yellow and black: the bee.](figures/renders/preview_assembly.png)

## Glasses stem, clips and spring arm

### The stem

The glasses are a 57□17-145 frame (lens 57 mm, bridge 17 mm, temple 145 mm). The stem profile, **MEASURED** with calipers on 2026-11-21, is 6.40 mm tall at the hinge, 4.7 mm where the straight section ends and 9.36 mm at the widest part of the rear paddle before it tapers quickly; the thickness is a consistent 3.54 mm along the whole stem. The straight section is 105.33 mm long, and the tallest point is 134.72 mm from the hinge in a straight line; the model puts it at 135 mm along the stem, because the stem bends and the path is slightly longer. A second set of measurements perpendicular to the lens plane gave 113.56 mm and 130.75 mm; those include the hinge's offset from the lens plane, so the model uses the along-the-stem values. Photographs showed that the frame is a cat-eye acetate front with thin translucent-brown temples; the preview's front is a rough interpretation (no lenses).

### The clip {#clip}

The reasoning is in [The mechanics, and why](#the-mechanics-and-why); these are the numbers. One **spring-jaw clip** at 127 mm from the hinge carries the spring arm, and the arm and clip are one printed part. Each jaw is split into three fingers by two 1 mm slits, the top plate sits 0.3 mm above the stem's top edge at its tallest point over the clip, and the arm hangs from a rigid shelf on the top plate. The stem height at 127 mm is interpolated, not measured.

| dimension | value | status |
|---|---|---|
| jaw thickness / top plate / clip length | 1.4 / 1.6 / 14 mm (1.2 mm jaws were flagged by JLC3DP's thin-wall heatmap) | DESIGN |
| free gap under the top plate / at the narrowest point | 4.9 mm / 2.65 mm (grip **N**, nominal) or 2.35 mm (grip **T**, tight) | DESIGN |
| fingers per jaw | 3 (two 1 mm slits) | DESIGN |
| distance from the arm to the jaws | at least 1.28 mm (measured on the model) | DERIVED |

![Grip force per jaw and jaw strain against the thickness of the glasses arm, for the two grips. The model is a cantilever jaw with E = 1.7 GPa and a 2 % strain limit (both ASSUMED); at the measured 3.54 mm, grip N gives about 8 N per jaw and 1.0 % strain, grip T about 11 N and 1.4 %.](figures/sims/clip_grip.png)

Grip **N** is expected to work on flat glasses arms about 3.2 – 4.2 mm thick and grip **T** about 2.9 – 3.9 mm (the lower limit is where the jaw preload falls to about 0.17 mm per jaw, the upper where the jaw strain reaches 2 %). Both are printed for each ear. N is the one to try first; T is for when N is loose or twists when the arm is loaded: the arm's pull tries to roll the clip, and a jaw that has less preload than that roll needs would lift off. (The needed preload is an order-of-magnitude estimate and has not been tested.) Nylon relaxes under constant load, so the grip may loosen over weeks; a strip of self-adhesive felt or silicone on the jaw faces is the fallback. The stem path is ASSUMED from photographs, so its real bend and twist may differ from the model: the first test fit settles it. This design is meant for flat plastic or acetate arms at least 2.5 mm thick and 4 mm tall; thin metal arms would need another grip.

Following JLC3DP's published limits ([JLC3DP design guideline](https://jlc3dp.com/help/article/212-3D-Printing-Design-Guideline): 1.0 mm recommended wall, 0.5 – 0.8 mm minimum engraved detail, ±0.3 mm tolerance), the ID text on the clips is engraved 0.6 mm deep in 4 mm bold text and the arm-thickness digits on the exciter plate in 6.5 mm bold text (5 mm gave strokes about 0.5 mm wide that JLC3DP's heatmap flagged red), the bear's screw posts are 3.4 mm across (1.05 mm wall round the 1.3 mm pilot), the PCB stops are 1.0 mm thick and the exciter pocket has 0.45 mm clearance each side (**ASSUMED**; test-fit it first).

### Spring arm {#spring-arm}

The clip carries a **leaf-spring arm** that curves behind the ear and ends in a plate holding the exciter against the mastoid. It is fused to the clip (one printed part), thin in the direction it flexes and tall in the other, like a miniature glasses temple. The pad force follows the cantilever formula $F = \frac{3EI}{L^3}\,\delta$, where $E$ is the nylon's modulus (about 1.7 GPa for PA12, ESTIMATE), $I = h t^3/12$ with arm height $h = 7$ mm and thickness $t$, $L \approx 55$ mm the free length and $\delta$ the preload (how far the relaxed pad sits proud of the skin, 5 mm).

![Pad force against arm thickness for three preloads, and the bending strain in the arm. The printed variants are 2.4, 2.8 and 3.2 mm; 2.8 mm at 5 mm preload gives about 2 N.](figures/sims/spring_arm.png)

![Stem clips and spring arm, with the stem profile and the three views of the arm part.](figures/blueprints/clips_arm.png)

## Gummy-bear dangle

The bear is a hollow shell with a flat back plate. Seen from the front it is 32.2 × 46.3 mm and 7.6 mm thick. Inside:

- the 13 × 28 mm dangle PCB lies *component side toward the back plate*, its bare bottom face against the front wall, the **microphone port under the belly button**;
- a **ring** around the port presses against the board (seal it with a thin bead of silicone cured beforehand, or a foam ring);
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

**Assumed heights**, to be checked against the real parts: JST-PH socket 7.8 mm, XIAO pin-header plastic 2.5 mm, USB plug opening 11.6 × 6.8 mm, battery 30 × 35 × 5.5 mm.

![Glasses front close-up on the head model (preview only).](figures/renders/glasses_check.png)

## Mass

![Estimated mass: about 6 g per glasses stem, 6 g per lobe, and about 50 g for the necklace box (mostly nylon and the battery).](figures/sims/mass.png)

## The print files

Everything is printed in **MJF nylon (PA12)** [@jlc3dp], in two colours because the dye bath colours a whole part and cannot be applied to part of one. The clips, the spring arms and the **bee base** are **dyed black**: the clips and arms stay unpainted, and the base needs no black paint (head, stinger and antennae) and only its wings painted silver. The **bear shells, back plates and the bee cover** are **natural grey**, then sanded, primed and painted (yellow over black dye would take several coats of primer, while black into a few valleys over grey is easy). Colour regions are 0.4 mm paint wells and raised bumps, not multi-colour printing.

![The finished print files, one of each kind (rendered from the STLs that will be sent for printing).](figures/renders/print_overview.png)

![The spring-jaw end of clip + arm, cropped from the print file.](figures/renders/print_clip.png)

![The clip with spring arm and exciter plate, and the three arm thicknesses.](figures/renders/print_arms.png)

Every part carries an engraved ID so the many near-identical clips can be told apart (the right-ear parts are mirrored, but their text still reads correctly; N and T are the two grips):

![Engraved IDs on the clip + arm: left grip N, right grip N, right grip T.](figures/renders/print_engraving.png)

<!-- include: tables/print_summary.md -->

: Print volume by group (all files, with the spare bears) {#tbl:print}

The full file list with volumes, bounding boxes and validity checks is in the appendix. Cost is in [Parts and cost](#parts-and-cost).

### Mesh audit against JLC3DP's limits

`make print-audit` (`cad/print_audit.py`) measures the real triangles of every STL, not the design parameters. From 12 000 random points on each surface a ray goes into the solid to the opposite wall (the local wall thickness) and out across the air to the next surface (the local gap). It reports the 1st-percentile wall and the share of the surface thinner than 1.0 mm (JLC3DP's recommended wall) and 0.8 mm, and the share of gaps narrower than 0.4 mm (the nylon clearance). Sampling is random, so a very small feature can be missed, and the minimum is not meaningful (every sharp edge is a wedge of near-zero thickness); the percentages are. Run on 2026-11-22, on the files as designed after the JLC3DP parameter audit:

| part | finding after the 2026-11-22 changes | what is left |
|---|---|---|
| bear back plates (L, R) | up to 11 % of the surface under 1.0 mm and 9 % under 0.8 mm: the floors are 0.75 – 0.8 mm, so the measurement counts them as thin | screw counterbores 0.4 mm deep (0.8 mm floor, was 0.5 mm); cable notch leaves a 0.8 mm skin (was 0.5 mm); the large L or R engraved 0.45 mm leaves 0.75 mm, kept because it is cosmetic |
| clip + arm (8 files) | 1.7 – 2.5 % under 1.0 mm and 0.1 – 0.4 % under 0.8 mm (first-percentile wall 1.0 mm); JLC3DP's heatmap flagged the first 1.2 mm jaws yellow and red, which is why they are 1.4 mm now, with a 0.4 mm lead-in so the jaw tips are 1.0 mm; after that only the finger tips show yellow | the jaws are 1.4 mm; the engraved IDs are 0.6 mm deep in the 1.6 mm top plate, so 1.0 mm is left under the letters; the remaining readings are letter edges, the jaw tips and a few thin spots near the arm tip (not traced) |
| bear shells | 5 % under 1.0 mm, 0.7 % under 0.8 mm; one patch of 1.0 mm over the PCB at the top | probably a thin ceiling region near the mic seal (not traced) |
| bee cover and base | 1 – 9 % under 1.0 mm, 1 % under 0.8 mm; two tiny patches 0.3 – 0.5 mm thick | probably lip and flange edges on the cover and an eye well on the base (not traced) |
| narrow gaps (under 0.4 mm) | 0.2 – 0.4 % on the clips and the bear shells | the jaw lead-in edges, the engraved digits and the 0.4 mm paint wells, by design (the finger slits are 1 mm) |

None of these is a wrong model; they are the places where legibility, fit and strength trade against JLC3DP's recommended 1.0 mm wall. The cable notch assumes the cable: 30 AWG silicone ribbon with 0.8 mm wires is about 0.8 mm thick, so two stacked ribbons (1.6 mm) pass the 2.4 mm slot with 3.0 mm of room under it; that thickness is inferred from the wire size and should be confirmed with the real cable. JLC3DP's own model check, run when the STLs are uploaded for a quote, has not been consulted yet.

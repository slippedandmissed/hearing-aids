\clearpage

```{=latex}
\part{Build and use}
```

# Assembly instructions

Follow the pictures; the text under each picture has the detail. Allow a weekend. **Nothing in this guide has been done on real hardware yet**; treat it as the plan, and update it (and the CAD) the first time reality disagrees.

**Order of work.** Prepare and paint the prints first so the paint can dry while you solder. Build the carrier and the bee, then the two bears, then test everything on the bench. Only then fit the clips and arm and put it on.

**Soldering skill needed.** Through-hole soldering and soldering a wire to a pad. No surface-mount chips: JLCPCB places and solders those.

## Step 0: Check what you have {-}

![Everything you should have in front of you before you start.](assets/parts-checklist.svg)

The printed parts, so you can tell them apart:

![](figures/assembly/step00b.png)

![](figures/assembly/step00c.png)

Every clip is engraved with its fit code (side, grip, arm thickness). The grips and arms are explained in Step 12.

## Step 1: Look before you solder {-}

Do this for all three boards, under a magnifier or a phone macro photo, against the renders in the [Electronics datasheet](#electronics-datasheet).

1. **No solder bridges** between neighbouring pads, and every surface-mount part present.
2. **The silkscreen reads "morgan".**
3. **Continuity, battery unplugged:** VBAT and GND must not beep. On a dangle board, test pad 3 against pads 6 and 8. On the carrier, test the battery socket's + against its −. The picture under Step 10 shows exactly where (marker a).
4. Anything wrong: stop and re-order that board rather than repair it. You have five of each.

## Step 2: Prime and paint the printed parts {-}

![What gets which colour, and where the tape goes.](assets/paint-plan.svg)

Paint first so it can dry while you solder.

1. **Sand** the bears and the bee cover lightly with 400-grit and wipe them clean.
2. **Tape** over the sound port and the loop hole of each bear and over the screw holes of the back plates (numbers 2 and 3 in the picture).
3. **Gesso** as the primer, thin coats, each dry before the next. **Untested on MJF nylon:** try it on a spare print first. A spray primer is the fallback.
4. **Base colours:** left bear bubblegum pink (about `#FF6FB5`), right bear fizzy blue (about `#3DB9FF`), bee cover yellow.
5. **Details:** the bears' eye and nose wells in black; the bee's grooves in black and its wings in silver. The bee base is printed black, so its head, stinger and antennae need no paint.
6. **Pull the tape** and check the sound hole is clear: a toothpick will tell you.
7. A matt acrylic varnish is optional and was not bought. Without it the paint can rub off where an earring touches skin.

**Do not paint the clips or the spring arms:** paint cracks where they flex.

## The carrier board at a glance {-}

![The five things you solder on the carrier, in order. Colours match the step headings below.](assets/carrier-solder-map.svg)

JLCPCB has already fitted everything grey. You solder: the battery wires, the XIAO, the battery socket, the switch and the ribbons. Two orderings matter:

- **Battery wires first.** Their pads are on the XIAO's back and are hidden once it sits on the carrier.
- **Ribbon B before ribbon A.** The B wires pass down between the A pads.

**Tape.** Painter's tape does three jobs here (suggested): it holds the XIAO seated while you tack its corner pins; it holds the carrier to the bench while you solder ribbons, so the cables cannot drag it around; and a flag on wire 1 of every ribbon, at both ends, so you can never swap the ends.

**Heat-shrink.** Slide it on **before** you solder, then park it well away from the iron: it cannot be threaded over a finished joint. Shrink it afterwards with a lighter held a few centimetres away, or with the side of a hot iron barrel. The black 2:1 kit has all the sizes.

## Step 3: Solder the two battery wires to the back of the XIAO {-}

![](figures/assembly/step03.png)

1. Tin each of the two small pads on the *back* of the XIAO (BAT+ and BAT−, about 1 × 2 mm, 1.9 mm apart) with a little solder.
2. Cut two wires about 25 mm long (red for BAT+, black for BAT−) and strip and tin 2 mm of each. **Slide a 10 mm piece of 1.5 mm heat-shrink onto each wire now.**
3. Hold the wire on the pad, touch it with the iron for about 2 s, release. Never hold the iron on a pad for more than about 3 s.
4. Tug gently: the joint must hold. Slide each sleeve down over the joint and shrink it, so a bare pad can never touch its neighbour.

Do this **before** the XIAO goes on the carrier: afterwards the pads are underneath. Use the second XIAO to practise first.

## Step 4: Solder the XIAO onto the carrier {-}

1. Feed the two wires through the carrier holes B+ and B− beside the XIAO's footprint and keep them slack.
2. Push the XIAO's pins into the 2 × 7 holes until the plastic of the pin header touches the board; the USB-C connector must point to the **right edge**, as in the carrier picture. A strip of painter's tape across the XIAO holds it seated. Tack one pin at each corner, check that it sits flat, then solder all 14 pins.
3. Solder the wire ends in B+ and B− from the underside and trim flush.
4. **Trim all pin tails to 1 mm or less**, so the board lies flat on the posts in the box.

## Step 5: Solder the battery socket and the slide switch {-}

- The JST-PH socket goes on the left edge, plug entry facing outward. The slide switch goes on the top edge with its lever sticking out.
- **LiPo plugs have no standard polarity.** Before plugging in, compare the red wire with the `+` silkscreen next to the socket. If they are swapped, swap the two wires inside the plug (lift the latch with a pin) rather than the socket. The reverse-protection transistor should save the electronics, but do not rely on it.

## Step 6: Prepare four ribbon cables {-}

Cut four ribbons of about 60 cm (measure from the box to the ear and add 10 cm), strip 2 mm and tin every wire. Use the same wire position on both ends of every ribbon:

| ribbon | wire | pad | signal |
|---|---:|---:|---|
| A | 1 | 1 | I2S_LRCLK |
| A | 2 | 2 | I2S_DIN |
| A | 3 | 3 | VBAT |
| A | 4 | 4 | PDM_DATA |
| B | 1 | 5 | I2S_BCLK |
| B | 2 | 6 | GND |
| B | 3 | 7 | PDM_CLK |
| B | 4 | 8 | GND |

Mark the first wire of every ribbon with a dab of paint or tape at both ends.

## Step 7: Solder the ribbons to the two ear blocks {-}

Slide a 15 mm piece of 3 mm heat-shrink over each ribbon pair first (it cannot be added once the wires are soldered), and tape the carrier to the bench.

1. **Ribbon B first** (pads 5 – 8, the back row): push each wire down through the gap between two A pads, from the top. Solder from the top, then trim the tail flush underneath.
2. **Then ribbon A** (pads 1 – 4, the front row), the same way.
3. Left-ear cables go to the left block, right-ear cables to the right block.
4. Tug-test every wire. With the multimeter, **VBAT (pad 3) to GND (pads 6 and 8) must not beep.**

## Step 8: Solder the cable and the exciter wires to each dangle PCB {-}

![The dangle PCB seen from the component side, with the order of work.](assets/dangle-solder-map.svg)

Do the left board with the left-ear cables and the right board with the right-ear cables. The big letter on the bare face tells you which is which.

1. **Heat-shrink first.** Slide a 15 mm piece of 3 mm sleeve onto each ribbon pair and park it well back.
2. **Ribbon A first**, into pads 1 – 4, the far row. Its wires pass between the pads of row B, with about 0.2 mm to spare each side, so row B must still be empty.
3. **Then ribbon B**, into pads 5 – 8, the near row.
4. **Exciter wires**, about 5 cm, to EXC+ (right pad) and EXC− (left pad) as you see the board in the picture.
5. Insert every wire from the **component side**, solder it there and trim it flush: the bare face must stay flat, because it sits 0.4 mm from the bear's front wall (a small pocket takes any solder blob).
6. Shrink the sleeve about 20 mm below the board, so A and B leave as one cable.

This is the opposite order to the carrier (Step 7). There the B row is the far one.

**Dry-fit first.** Before soldering anything, push one spare ribbon wire through between two B pads. It should slide with a little room (about 0.2 mm each side). If it jams, strip less insulation back or use thinner wire for that ribbon.

## Step 9: Assemble each gummy bear {-}

![One bear, exploded, and how the cables run.](assets/bear-assembly.svg)

Start the silicone a day ahead, and do the rest after the bench test of Step 10 if you can, because the bear is awkward to reopen. The shell lies front-down on the bench, so its open side faces you.

1. **Silicone first, a day early.** Run a thin bead on the printed ring around the microphone port inside the shell (not on the board), keep it out of the 0.5 mm sound hole, and leave it about 24 hours in the open air. Cheap bathroom silicone is probably the vinegar type, whose fumes corrode copper while it cures; curing it on the shell keeps them off the board, and the cured ring can be removed if you have to rework.
2. **Lay the PCB in**, bare face down on the ring and components up toward you, with the microphone hole over the sound hole.
3. **Cables out through the slot** at the top, once round each of the two pegs, with the exciter wires alongside them in the gap above the components.
4. **Back plate on.** Its two pillars rest on the bare edge strips of the board. Seat it flat.
5. **Four M1.6 × 4 mm screws, just snug**: nylon strips easily. The heads stand proud of the back; the tips end inside the posts.
6. After the bench test, a dab of silicone round the cable slot is the strain relief.

**Dry-fit first.** Before the bear is closed, lay both ribbons and the two exciter wires through the slot together. They should pass with a little room (the slot is 4.4 mm wide, and the notch under it takes two stacked ribbons plus two thin wires with about 0.4 mm to spare, if the exciter wires are 0.8 mm). If they do not, use thinner wire for the exciter leads: no reprint is needed.

## Step 10: Test on the bench {-}

![Where to probe, what to expect, and the tone test.](assets/bench-tests.svg)

1. Flash the firmware ([Firmware](#firmware-placeholder); double-tap reset to enter the bootloader, copy the `.uf2`).
2. Switch on: the red LED should light.
3. Measure VBAT (about 3.7 – 4.2 V) at carrier ear pad 3 (marker b), and the 3.3 V rail across C4 on a dangle board with its ribbon connected (marker c).
4. In a quiet room, hold the exciter in your fingers (not on your skull) and raise the volume slowly: expect a clean tone and no squeal.

**Until the firmware exists, only the continuity and voltage tests are possible.** Do not skip this step.

## Step 11: Assemble the bee box {-}

![The bee base with the cover off, and the six moves.](assets/bee-assembly.svg)

1. **Battery** into the abdomen pocket, lead toward the thorax.
2. **Carrier board** onto its two posts with two M2 × 4 mm screws. Not longer: an 8 mm screw would come out of the back.
3. **Battery plug** into the JST socket from the left edge. Before it goes in, compare the red wire with the `+` on the board. LiPo plugs have no standard polarity: if they differ, swap the wires inside the plug (lift the latch with a pin), not the socket. The reverse-protection FET should save the board, but do not rely on it.
4. **Ribbons** out through the top slots with a loop of slack inside, and the heat-shrink sleeve just outside the slot.
5. **Cover** on: press the lip into the base until it clicks. Check no wire is pinched.
6. **Chain** through the head. Step 14 does the cables.

## Step 12: Fit the clip {-}

![Where the clip sits, how it grips the stem, and the exciter on its arm.](assets/clip-fit.svg)

The clip and its arm are one piece. Start with the **N** grip.

1. Mark the stem **127 mm from the hinge**, on the bend.
2. Press the clip on from below, mouth up toward the stem. It needs firm pressure, then stays put with a slight click: the jaws spring apart to take the stem.
3. Push the arm gently sideways. The clip must not twist or slide.
4. **Loose, or it twists?** Swap to the **T** grip. Still loose: a strip of self-adhesive felt on the inside of the jaws.
5. **Will not go on?** Do not force it, the stem is plastic. Measure the stem again: it should be at least 3.2 mm thick.

## Step 13: Fit the spring arm and the exciter {-}

1. The arm curves behind the ear to the mastoid, the bone behind it.
2. Put the exciter in the plate (13 × 26.5 × 5.75 mm) with a drop of glue at each corner.
3. Thread its two wires through the tie hole, then on to the bear (Step 8).
4. Check the pad: it should press gently (about 2 – 5 N) and not squeeze the ear. If it pushes hard, swap to the 2.4 mm arm; if it floats off the skin, use the 3.2 mm arm.

## Step 14: Dress the cables and hang the bears {-}

![Laid out flat first, then fitted. Details A, B and C below it.](assets/necklace-assembly.svg)

1. **Chain through the bee.** Open the chain's clasp and thread the chain through the hole in the bee's head (6.2 mm; the links are 2 mm). The bee sits in the middle.
2. **Lay it out flat**, as in the top strip: bee in the middle, one ribbon pair on each side, the bears at the ends. Hold each pair against the chain with a turn of painter's tape every 10 cm. The tape is temporary.
3. **Twist ties**, starting at the bee: one every 8 – 10 cm along the first 20 cm, round the chain and both ribbons together, two full turns, snug but not tight. Fold the tails flat, because they will lie against your neck. Remove the tape as each tie goes on.
4. **Beyond the last tie** the ribbons leave the chain and run up to the ear. Leave a 3 – 4 cm loop of slack at the ear, so turning your head never pulls on the PCB.
5. **Jump rings.** Join each bear's loop (a 2.2 mm hole, too small for the ear wire) to its ear hook with a 4 mm jump ring. Twist the ring open sideways, never pull it apart, thread loop and hook, and close it flush: 0.7 mm wire opens under load.
6. **Try it on** before trimming any tails. Check both ribbons reach, the slack loops sit behind the ears, and the bee hangs at the chest.

The ribbons enter the bee through the top slots with a loop of slack inside the box, and the heat-shrink sleeve sits just outside the slot (detail B).


## Step 15: First power-up with the exciter against your head {-}

1. Everything on: clips fitted, bears hung, bee on, switch off.
2. **Volume low.** Switch on and put the glasses on.
3. Raise the volume slowly while you talk. A clean, quiet copy of your voice is the aim.
4. **Squeal or buzz?** Turn it down and move the exciter away from the microphone. A bone-conduction exciter sits only a few centimetres from the mic, so some squeal at high gain is likely: the [Firmware](#firmware-placeholder) chapter plans a feedback canceller for it, which does not exist yet.
5. The hardware cap keeps the exciter well under 100 mW whatever the firmware does, but **stop if anything hurts**.

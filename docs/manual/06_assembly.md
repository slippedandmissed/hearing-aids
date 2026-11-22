\clearpage

# Assembly instructions

Follow the pictures; the text under each picture has the detail. Allow a weekend. **Nothing in this guide has been done on real hardware yet**; treat it as the plan, and update it (and the CAD) the first time reality disagrees.

**Order of work.** Prepare and paint the prints first so the paint can dry while you solder. Build the carrier and the bee, then the two bears, then test everything on the bench. Only then fit the clips and arm and put it on.

**Soldering skill needed.** Through-hole soldering and soldering a wire to a pad. No surface-mount chips: JLCPCB places and solders those.

## Step 0: Check what you have {-}

![](figures/assembly/step00.png)

![](figures/assembly/step00b.png)

![](figures/assembly/step00c.png)

- 3 PCBs (2 dangle variants and the carrier), 2 XIAO nRF52840, a LiPo with JST plug, 4 ribbon cables, 3 exciters, screws, hooks and a chain.
- The printed set (see chapter 4); every clip is marked with its fit code.
- Tools: soldering iron with a fine tip, solder, flux pen, side cutters, wire strippers, tweezers, a multimeter, a small Phillips screwdriver, 400-grit sandpaper, primer, paints, clear lacquer, tape, hot glue or epoxy.

## Step 1: Look before you solder {-}

![](figures/assembly/step01.png)

- Compare each board with its render in chapter 3 under a magnifier or a phone macro photo: no solder bridges between neighbouring pads, every surface-mount part present, the silkscreen reads "morgan".
- With the multimeter on continuity (beep): **VBAT and GND must not beep**. On the dangle boards, test pad 3 against pads 6 and 8. On the carrier, test a battery-socket pad against ground.
- Stop and re-order a board if you find anything wrong.

## Step 2: Prime and paint the printed parts {-}

![](figures/assembly/step02.png)

1. Sand lightly with 400-grit and wipe clean.
2. Plastic primer, thin coats.
3. Base colours: left bear bubblegum pink (about `#FF6FB5`), right bear fizzy blue (about `#3DB9FF`), bee yellow.
4. Details: black into the bee's stripe valleys, silver on the wings, bear eyes and nose.
5. Clear lacquer. **Do not paint the clips or the spring arm** (paint cracks where they flex).

Keep paint out of the microphone hole, the screw holes and the clip cavities.

## Step 3: Solder the two battery wires to the back of the XIAO {-}

![](figures/assembly/step03.png)

1. Tin each of the two small pads on the *back* of the XIAO (BAT+ and BAT−, about 1 × 2 mm, 1.9 mm apart) with a little solder.
2. Strip and tin 2 mm of each wire (30 AWG, about 25 mm long: red for BAT+, black for BAT−).
3. Hold the wire on the pad, touch it with the iron for about 2 s, release. Never hold the iron on a pad for more than about 3 s.
4. Tug gently: the joint must hold.

Do this **before** the XIAO goes on the carrier: afterwards the pads are underneath. Use the second XIAO to practise first.

## Step 4: Solder the XIAO onto the carrier {-}

![](figures/assembly/step04.png)

1. Feed the two wires through the carrier holes B+ and B− beside the XIAO's footprint and keep them slack.
2. Push the XIAO's pins into the 2 × 7 holes; the USB-C connector must point to the **right edge**. Tack one pin at each corner, check that it sits flat, then solder all 14 pins.
3. Solder the wire ends in B+ and B− from the underside and trim flush.
4. **Trim all pin tails to 1 mm or less**, so the board lies flat on the posts in the box.

## Step 5: Solder the battery socket and the slide switch {-}

![](figures/assembly/step05.png)

- The JST-PH socket goes on the left edge, plug entry facing outward. The slide switch goes on the top edge with its lever sticking out.
- **LiPo plugs have no standard polarity.** Before plugging in, compare the red wire with the `+` silkscreen next to the socket. If they are swapped, swap the two wires inside the plug (lift the latch with a pin) rather than the socket. The reverse-protection transistor should save the electronics, but do not rely on it.

## Step 6: Prepare four ribbon cables {-}

![](figures/assembly/step06.png)

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

![](figures/assembly/step07.png)

Solder from the top side of the carrier: ribbon A to pads 1 – 4 (front row), ribbon B to pads 5 – 8 (back row), for the left block with the left-ear cables and for the right block with the right-ear cables. Tug-test every wire; then with the multimeter check that **VBAT (pad 3) and GND (pads 6, 8) do not beep**.

## Step 8: Solder the cable and the exciter wires to each dangle PCB {-}

![](figures/assembly/step08.png)

- Insert each wire from the **component side**, solder from the same side and trim it flush: the bare bottom face must stay flat (it sits 0.4 mm from the bear's front wall, with a small pocket for any solder blob).
- Ribbon A to pads 1 – 4 (top row), ribbon B to pads 5 – 8; the exciter wires (about 5 cm) to EXC+ (right pad) and EXC− (left pad) seen from the component side.
- Left cables go to the **L** board, right cables to the **R** board; the big letter is on the bottom face.

## Step 9: Assemble each gummy bear {-}

![](figures/assembly/step09.png)

1. Lay the foam or silicone ring on the ring around the microphone port in the shell.
2. Lay the PCB in: **components down**, bare face against the ring, microphone hole over the belly-button hole.
3. Fit the back plate with its two pillars on the board's bare edge strips. Pass both cables through the slot at the top and take them once around each peg.
4. Four M1.6 × 4 mm screws, just snug (nylon strips easily). The heads stand proud of the back; the tips end inside the posts.
5. After testing, a dab of silicone around the cable slot for strain relief.

## Step 10: Test on the bench {-}

![](figures/assembly/step10.png)

1. Flash the firmware (chapter 8; double-tap reset to enter the bootloader, copy the `.uf2`).
2. Switch on: the red LED should light.
3. Measure VBAT (about 3.7 – 4.2 V) at pad 3 and the 3.3 V rail near the microphone.
4. In a quiet room, hold the exciter in your fingers (not on your skull) and raise the volume slowly: expect a clean tone and no squeal.

**Until the firmware exists, only the continuity and voltage tests are possible.** Do not skip this step.

## Step 11: Assemble the bee box {-}

![](figures/assembly/step11.png)

1. Battery into the abdomen pocket, plug toward the thorax; its lead goes through the opening to the JST socket.
2. Carrier board on its two screw posts (and the four supports) with two M2 × 4 mm screws (not longer: an 8 mm screw would come out of the back).
3. Battery plug into the JST socket (check polarity).
4. Ear cables out through the top slots with a loop inside.
5. Cover on: press the lip into the base until it clicks. Make sure no wire is pinched.
6. The chain goes through the hole in the bee's head.

## Step 12: Fit the clips {-}

![](figures/assembly/step12.png)

Try the A-type clips at station 100 mm from the hinge (clip B at 127 mm) starting with fit **B2**. Press from below (slot side up). Choose the smallest cavity that slides on with a firm click; if it is loose, pad it with tape or go one size down; if it will not go on, go one size up. Never force it: the stem is plastic.

## Step 13: Fit the spring arm and the exciter {-}

![](figures/assembly/step13.png)

Clip A on at 100 mm, clip B with the arm at 127 mm. The arm curves behind the ear to the mastoid. Put the exciter in the plate (13 × 26.5 × 5.75 mm) with a drop of glue at the corners, thread its wires through the tie hole, then to the dangle. Check that the pad presses gently (about 2 – 5 N) and does not squeeze the ear. If it pushes hard, swap to the 2.4 mm arm; if it floats off the skin, use the 3.2 mm arm.

## Step 14: Hang the bears, route the cables {-}

![](figures/assembly/step14.png)

Bear hook loops onto the earring hooks; the neck cables go down behind the ear and along the neck; Velcro or cable ties every 8 – 10 cm along the chain; **leave a loop of slack at the ear** so head movement never pulls on the PCB.

## Step 15: First power-up with the exciter against your head {-}

![](figures/assembly/step15.png)

Volume low; raise slowly; if it squeals or buzzes, turn it down and move the exciter away from the microphone. The hardware cap limits the exciter to well under 100 mW whatever the firmware does, but stop if anything hurts.

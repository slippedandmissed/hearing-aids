\clearpage

# The mechanics, and why

Every shape is Python (build123d [@build123d]), so a dimension changes in one place. This chapter explains why the shapes are what they are. The numbers and drawings are in the [Mechanical datasheet](#mechanical-datasheet).

## The clip and the arm

![Five problems, and the feature each one forces.](assets/clip-reasoning.svg)

The pad hangs about 45 mm from a clip that is 14 mm long, so any slack in the clip is tripled at the pad. With 0.25 mm of clearance each side the clip can rock about 2°, which moves the pad about 1.6 mm, out of a preload of 5 mm; the printer's ±0.3 mm tolerance can make that 3.6 mm. These are estimates from the stem model, nothing tested on glasses.

An exact fit would also fight the stem. Within ±7 mm of the clip it grows from 7.0 to 9.2 mm tall, its faces twist by about 5° across the clip, and 27 mm further forward it bends by 41°. So the clip does not fit the stem; it **grips** it. Two thin jaws hang from a top plate, angled towards each other like a V. The stem is pushed in from below, wedges where the gap equals its thickness, and springs the jaws apart. Any stem inside the jaws' travel is held with a spring force, and only the thickness matters, which is the one dimension that was measured well (3.54 mm). Two 1 mm slits split each jaw into three fingers, which follow the twist one at a time.

The arm is a leaf spring: thin in the direction it flexes, tall in the other, like a miniature glasses temple. It hangs from a **rigid shelf** on the top plate and not from a jaw, because a jaw with an arm fused to it cannot spring and the other jaw would have to take all the travel.

Two things cannot be known before the first fitting: how firmly the pad should press, and exactly how this stem behaves. So two grips are printed (**N** nominal, **T** tight, for when N is loose) and three arm thicknesses (2.4, 2.8 and 3.2 mm: softer or stiffer pad force), and you swap until it feels right. The force follows the cantilever formula, about 2 N for the 2.8 mm arm at 5 mm of preload.

## The bear

The bear is built around its PCB. The microphone, amplifier, regulator, two 1206 resistors for the power cap, a few capacitors and 8 cable pads fit on a **13 × 28 mm** board. Around it the shell adds walls, and the whole bear is 32 × 46 × 7.6 mm. It hangs on an ear hook from a 2.2 mm loop at the top, so everything points down: the cables leave through one slot beside the loop and run down the neck. The slot is on the back-of-head side, which is why the left and right bears are mirror images and not copies.

The microphone has to hear the world, so it is a bottom-port part: its sound hole goes *through* the board, against a ring on the inside of the front wall, and out through a hole that is disguised as the bear's belly button. The ring does the sealing and the back plate does the squeezing: two pillars on the back plate press on the bare edge strips of the board, so that the seal is the clamp. Four small screws hold the back plate (the posts are 3.4 mm across, leaving a 1.05 mm wall round the pilot, above the printer's recommended 1.0 mm), two pegs give the cables a turn as strain relief, and small stops keep the board from sliding.

The board sits **components toward the back plate**, with 2.8 mm between them and the plate for the components, the wire ends and the wire runs. That gap, plus the board, the ring and the walls, is the 7.6 mm. Each bear weighs about 6 g, which is the one thing here that only wearing it will settle.

The eyes, nose and belly-button dimple are shallow wells for paint, because the printer makes grey or black and nothing else.

## The bee

![Why the box is a flat board plus a wing. The last bar is arithmetic, not a model.](assets/bee-thickness.svg)

The carrier board holds the XIAO, the battery socket, the switch, two blocks of 8 ear pads and ten series resistors, which makes it 56 × 40 mm. It has 9 mm rounded corners so that it fits inside a rounded body. That body is the **thorax**.

The tallest things on the board are the battery socket and the XIAO on its pin-header plastic, so they set the thorax thickness. A socketed XIAO would have made the box 24 – 29 mm thick; soldering the XIAO's pins straight into the carrier gives 15.8 mm. The battery is 30 × 35 × 5.5 mm. Stacked on the board it would add more than 6 mm and turn a flat badge into a block, so it lies in a pocket beside the board instead. That pocket is the **abdomen**, 44 mm wide and 10.1 mm thick. A solid ball with the chain hole through it makes the **head**, and the flat cosmetic wings, antennae and stinger finish the shape. The bee is what the electronics wanted to be.

The chain hole is 6.2 mm so that the chain's clasp end passes through it. The USB-C connector is on the right edge, so the battery charges without opening the box, the switch lever sticks out of the top edge, and two slots in the top edge let the ear cables out. With the battery the box is about 51 g, which sits on the chest, not on the ears.

## The plastic, the colours and the printer

The clip jaws and the arm are springs, so the material has to be tough and slightly flexible, and survive being flexed many times. **PA12 nylon**, printed by multi jet fusion (MJF), is: its stiffness is about 1.7 GPa, and a strain of 2 % is taken as the limit for the design (both estimates). MJF also needs no support structure, so the fingers, hooks and slits print as drawn.

The printing service can only supply nylon in natural grey or dyed black, and a dye colours a whole part. So the colours are:

- **Dyed black, never painted:** the clips and arms, because paint cracks where they flex, and the bee base, because its head, stinger and antennae look right black.
- **Natural grey, then painted:** the bears and the bee cover, painted in the colours you pick.

The service's published limits shaped the details too: walls of at least 1.0 mm, engraved text no finer than 0.5 – 0.8 mm (the clip codes are 0.6 mm deep), and a tolerance of ±0.3 mm, which is why nothing relies on a press fit that tight. A file holding several loose parts is treated as an assembly and refused, so every part is its own file: 14 in all.

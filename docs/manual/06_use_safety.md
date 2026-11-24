\clearpage

# Use, care and safety

## Putting it on

1. Switch the bee **ON** (red LED) and hang it round your neck, with the chain's slack clear of snags.
2. Put on the glasses with the clips and arms fitted. Each exciter rests on the mastoid, the bony bump behind the ear.
3. Hang the bears on the earrings, keeping a slack loop of cable at each ear.
4. Start quiet and raise the volume until speech is clear, never until it is loud.

## Adjusting

- **Pressure:** swap the arm. 2.4 mm is softer, 2.8 mm standard, 3.2 mm stiffer. Do not heat or bend nylon beyond a gentle nudge at fitting.
- **Position:** a few millimetres changes the loudness a lot. Mark the spot that works.
- **Howl:** the exciter is too close to the microphone or the gain is too high. Turn it down and move the earring away from the arm.

## Charging

Plug USB-C into the bee with the **slide switch ON**; the switch sits between the cell and the charger. 500 mAh at 50 – 100 mA takes about 5 – 10 hours. Charge on a hard surface, in sight, never while worn or under a pillow, and unplug when full.

## Safety

- **Hearing.** Bone conduction can reach the inner ear at levels you cannot judge by feel. Do not turn it up to cope with a blockage that needs treatment; see a clinician about the wax.
- **Electrical limits.** The series resistors limit the exciter to about 30 mW in the worst case; the firmware adds its own hard limiter.
- **Battery.** A LiPo can burn if shorted, crushed or reversed. Use a protected cell; check the plug polarity; never leave the box in a hot car; stop using a puffy cell.
- **Skin contact.** The exciter and the arm sit on your skin for hours: if the skin reddens or hurts, remove them and shorten the wearing time.
- **Water.** Nothing is waterproof. Remove for showers and rain.
- **Small parts.** The screws and the bears' parts are choking hazards for children and pets.

## Troubleshooting

| symptom | likely cause | what to try |
|---|---|---|
| no LED when switched on | battery flat or unplugged, plug reversed, switch dirty | check the plug polarity, charge, measure VBAT at pad 3 |
| charging does nothing | slide switch is OFF, bad USB cable, XIAO battery wires loose | switch ON, another cable, re-solder the BAT wires |
| silence from one ear | cable wire broken or on the wrong pad, amp strap wrong | continuity test pad by pad, check L/R board against L/R cable |
| both ears silent, LED on | firmware not running, amplifier rate rejected (16.129 kHz) | reflash; the start-up jingle and green blink are missing: reflash; play its last note against a phone tuner app (about 1008 Hz); see risk 1 in [Decisions and open risks](#decisions-and-open-risks) |
| a howl or whistle | feedback | lower the volume, reposition, check the mic seal |
| crackles with head movement | broken ribbon wire or poor joint | flex test while measuring continuity |
| sound only when pressing the exciter | too little pad pressure | thicker arm, re-seat the clip, re-bend the plate gently |
| the bear rattles | board not clamped | tighten the screws a little, check the stops and pillars |

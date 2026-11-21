"""Dangle PCB: areas of the BOTTOM silkscreen where no via may sit (ink over a via hole is blanked or smudged by the fab; JLCDFM 'silkscreen to hole').
Boxes are (x0, y0, x1, y1) in board mm, generous around the text/glyphs placed in finish.py: KEEP IN SYNC with that file."""
BOTTOM_SILK_NO_VIA = [
    (2.9, 2.6, 4.1, 4.4),      # '+'   (exciter pad N side)
    (8.9, 2.6, 10.1, 4.4),     # '-'
    (7.2, 5.0, 8.3, 12.9),     # big L (printed mirrored on the bottom: the upright bar is on the right, x ~ 7.7)
    (3.9, 11.8, 8.3, 12.9),    # big L: foot, extends to the left
    # (the pad key lines, 13.0-17.3 mm, have no zone: they are small, the key is repeated in the manual, and a via under a character only clips that stroke)
    (2.3, 18.7, 10.9, 20.6),   # 'morgan'
    (1.6, 21.0, 11.5, 22.7),   # 'LEFT / RIGHT EAR'
]

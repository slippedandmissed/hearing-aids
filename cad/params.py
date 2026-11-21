"""All dimensions in mm. Every value says where it came from.
SOURCE tags: DATASHEET (verified on a listing), ASSUMED (typical/guess, replace when measured), MEASURE (needs Morgan's ear), DESIGN (our choice).
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Params:
    # --- exciter: Dayton DAEX-9-4SM (DATASHEET: 13 x 26.5 x 5.75 mm, 2.3 g)
    exc_w: float = 13.0
    exc_l: float = 26.5
    exc_t: float = 5.75
    exc_clear: float = 0.3          # DESIGN: pocket clearance each side
    exc_window_inset: float = 1.2   # DESIGN: lip that stops exciter falling through the skin-side window
    exc_angle: float = 90.0         # DESIGN: 0 = long axis vertical, 90 = horizontal. Horizontal chosen for the mastoid: a vertical plate would hang below the lobe
    jaw_t: float = 1.6              # DESIGN: wall thickness of the exciter holder plate (nylon min wall ~1 mm)

P = Params()

# ---- ear hook / spring arm. All PLACEHOLDERS until Morgan measures (see docs). Coordinates: canal opening = origin, +Y nose, +Z up, +X out of the ear.
@dataclass(frozen=True)
class HookParams:
    arm_t: float = 2.4          # DESIGN: lateral thickness of the leaf-spring arm (flexes sideways). Variants 1.6/2.4/3.2
    arm_h: float = 7.0          # DESIGN: arm height (stiff in the vertical plane, like glasses temples)
    preload: float = 5.0        # DESIGN: how far the relaxed pad sits medial of the skin (arm flexes this much when worn)
    mastoid_y: float = -33.0    # DERIVED from B=22 mm: ~7 mm behind the groove (which is ~26 mm behind the canal) (ASSUMED direction)
    mastoid_z: float = -19.0    # DERIVED from B=22 mm along skin ~ 20 mm straight, mm below canal level
    ear_protrusion: float = 20.5   # MEASURED 2026-11-20 (card/coin stack, 20-21 mm, mid-height gap behind helix)
    path_A: float = 56.0        # MEASURED 2026-11-20: groove top -> mastoid, along skin (supersedes earlier 39 mm)
    path_B: float = 22.0        # MEASURED 2026-11-20: groove at canal level -> mastoid, along skin
    E_pa12: float = 1700.0      # N/mm^2, ASSUMED for printed nylon PA12 (check JLC3DP material sheet)

H = HookParams()

# ---- Morgan's glasses (frame stamp "57[]17 145": lens width 57, bridge 17, temple length 145 mm)
@dataclass(frozen=True)
class GlassesParams:
    lens_w: float = 57.0         # STAMP
    bridge: float = 17.0         # STAMP
    temple_len: float = 145.0    # STAMP (hinge to tip, along the stem)
    temple_t: float = 3.54       # MEASURED (calipers, 2026-11-21): consistent along the whole stem
    temple_h_hinge: float = 6.40  # MEASURED (calipers, 2026-11-21) stem height at the hinge
    temple_h_straight_end: float = 4.7  # MEASURED (calipers): height where the straight section ends
    straight_end_station: float = 105.33 # MEASURED (calipers, along the stem): mm from hinge where the straight section ends
    temple_h_paddle: float = 9.36 # MEASURED (calipers): max height of the rear paddle, before it tapers quickly
    paddle_station: float = 135.0 # DERIVED: straight-line hinge-to-tallest-point 134.72 mm (MEASURED); the path is slightly longer because the stem bends
    temple_h_tip: float = 4.0    # ASSUMED: height at the very tip after tapering
    clip_len: float = 14.0       # DESIGN: length of each C-clip along the stem
    clip_wall: float = 1.6       # DESIGN
    clip_clear: float = 0.25     # DESIGN: gap between stem and clip cavity
    clip_stations: tuple = (100.0, 127.0)   # DESIGN: mm from the hinge along the stem

G = GlassesParams()

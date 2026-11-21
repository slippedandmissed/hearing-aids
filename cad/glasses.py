"""Morgan's glasses stem (parametric stand-in) + C-clips that hold the exciter arm. World coords: canal opening = origin.
Stem path is ASSUMED from the worn-glasses photos (stem passes just over the top of the helix, tip ends behind the UPPER ear)."""
import numpy as np
from build123d import *
from params import P, H, G, GlassesParams
from earhook import catmull, ear_hook

# (y forward, z up, lateral height above skin) -- hinge first. Front part splays out so the hinge sits ~70 mm from the midline (57-17 frame is ~140 wide). y of the hinge is solved so path length == temple_len.
STEM_CTRL = [(95, 42, 31), (60, 41, 18), (20, 40.5, 10), (-8, 40, 12.5), (-26, 34, 9), (-37, 24, 5.5), (-40, 17, 4.5)]

def stem_path(skin_x, g: GlassesParams = G):
    ctrl = [list(c) for c in STEM_CTRL]
    for _ in range(4):                                    # shift the hinge so the stem is exactly temple_len long
        c = np.array(catmull(ctrl, 30))
        P3 = np.array([[skin_x(y, z) + l, y, z] for y, z, l in c])
        seg = np.linalg.norm(np.diff(P3, axis=0), axis=1); L = seg.sum()
        ctrl[0][0] += (g.temple_len - L) * 0.9
    s = np.concatenate([[0], np.cumsum(seg)])
    return P3, s

def hfun(s, g: GlassesParams = G):
    """Stem height (mm) at station s along the stem (piecewise linear through the measured values)."""
    return float(np.interp(s, [0, g.straight_end_station, g.paddle_station, g.temple_len], [g.temple_h_hinge, g.temple_h_straight_end, g.temple_h_paddle, g.temple_h_tip]))

def _section(pt, tan, w, h):
    lat = Vector(1, 0, 0); xdir = (lat - tan * lat.dot(tan)).normalized()
    return Plane(origin=pt, x_dir=xdir, z_dir=tan) * Rectangle(w, h), Plane(origin=pt, x_dir=xdir, z_dir=tan)

def glasses_stem(skin_x, g: GlassesParams = G):
    P3, s = stem_path(skin_x, g)
    idx = list(range(0, len(P3) - 1, 4)) + [len(P3) - 1]
    secs = []
    for i in idx:
        j0, j1 = max(i - 1, 0), min(i + 1, len(P3) - 1)
        tan = Vector(*(P3[j1] - P3[j0])).normalized()
        h = hfun(s[i], g)
        secs.append(_section(Vector(*P3[i]), tan, g.temple_t, h)[0])
    return loft(secs), P3, s

def clip_at(P3, s, station, g: GlassesParams = G):
    """C-clip (snap-on, slot on the underside) around the stem at `station` mm from the hinge."""
    i = int(np.argmin(abs(s - station)))
    j0, j1 = max(i - 1, 0), min(i + 1, len(P3) - 1)
    tan = Vector(*(P3[j1] - P3[j0])).normalized()
    h = hfun(s[i], g)
    ci, co = g.clip_clear, g.clip_wall + g.clip_clear
    sec, pl = _section(Vector(*P3[i]), tan, g.temple_t + 2 * co, h + 2 * co)
    outer = extrude(sec, amount=g.clip_len / 2, both=True)
    inner = extrude((pl * Rectangle(g.temple_t + 2 * ci, h + 2 * ci)), amount=g.clip_len, both=True)
    slot = extrude((pl * Pos(0, -(h / 2 + co / 2), 0) * Rectangle(g.temple_t - 0.6, co + 1.0)), amount=g.clip_len, both=True)
    return (outer - inner) - slot, np.array(P3[i])

def exciter_arm(skin_x, P3, s, anchor_pt, p=P, h=H, g: GlassesParams = G, preload=None, arm_t=None, lat_off=None, drop=0.0):
    """Leaf-spring arm from the rear housing (pod), down behind the ear to the mastoid plate.
    lat_off = lateral offset of the arm start from the stem centre; drop = how far below the stem point it starts."""
    a_y, a_z = anchor_pt[1], anchor_pt[2] - drop
    off = (g.temple_t / 2 + g.clip_wall + g.clip_clear + h.arm_t / 2) if lat_off is None else lat_off
    lat0 = anchor_pt[0] - skin_x(a_y, a_z) + off
    prefix = [(a_y, a_z, lat0), (a_y - 3, a_z - 8, lat0 - 2), (-36, 10, 8), (-35, 1, 7), (-34, -5, 6.5)]
    return ear_hook(skin_x, p, h, preload=preload, arm_t=arm_t, prefix=prefix)

if __name__ == "__main__":
    flat = lambda y, z: 0.0
    stem, P3, s = glasses_stem(flat)
    print("stem length", s[-1], "tip", P3[-1], "valid", stem.is_valid, "vol", stem.volume)
    for st in G.clip_stations:
        c, pt = clip_at(P3, s, st); print("clip", st, "valid", c.is_valid, "vol", round(c.volume), "at", pt.round(1))

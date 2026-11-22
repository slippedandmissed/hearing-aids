"""Morgan's glasses stem (parametric stand-in) + C-clips that hold the exciter arm. World coords: canal opening = origin.
Stem path is ASSUMED from the worn-glasses photos (stem passes just over the top of the helix, tip ends behind the UPPER ear)."""
import numpy as np
from dataclasses import dataclass, replace
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

_vec = lambda v: np.array([v.X, v.Y, v.Z])

# ---------------------------------------------------------------------------------------------------------------- compliant (spring-jaw) clip
@dataclass(frozen=True)
class FlexParams:
    """V-jaw spring clip. The two jaws hang from a top plate and are angled towards each other (a V): the stem is pushed in from below and wedges where the free gap
    equals its thickness; being pushed further, up to the top plate, it springs the jaws apart and is gripped by the spring force (no exact fit needed).
    ESTIMATE-level numbers: PA12 E = 1700 MPa, strain limit 2 % (the same values as the spring arm), nothing tested."""
    t_jaw: float = 1.4          # DESIGN: jaw thickness. 1.2 mm was flagged by JLC3DP's thin-wall heatmap (every face just under its 1.2 mm limit, some red slivers); 1.4 mm clears it
    t_top: float = 1.6          # DESIGN: top plate thickness (the ID text is engraved 0.6 mm deep in it)
    gap_top: float = 4.9        # DESIGN: free gap between the jaws just under the top plate (accepts stems up to about this thick)
    gap_tip: float = 2.65       # DESIGN: free gap at the narrowest point near the jaw tips (about 0.3 mm interference per jaw on the measured 3.54 mm stem); the variant 'T' (tight) uses a smaller one
    lead: float = 0.4           # DESIGN: lead-in chamfer at each jaw tip (widens the mouth so the stem can be pushed in); 0.4 leaves a 1.0 mm flat at the tip (0.6 left 0.8 mm and JLC3DP's heatmap showed yellow triangles)
    lead_h: float = 1.2
    top_clear: float = 0.3      # DESIGN: gap between the stem's top edge and the top plate
    below: float = 1.0          # DESIGN: how far the jaws reach below the stem's bottom edge at the nominal height
    length: float = 14.0        # DESIGN: clip length along the stem
    n_slits: int = 2            # DESIGN: slits that split each jaw into n_slits + 1 independent fingers, so they follow the twist of the stem faces (about 5 deg over the clip length at 127 mm)
    slit_w: float = 1.0         # DESIGN: slit width (JLC3DP: keep features at least 0.4 mm apart)
    shelf_w: float = 3.8        # DESIGN: the arm hangs from a rigid shelf on the +u side of the top plate, NOT from a jaw (an arm fused to a jaw makes that jaw rigid, so the other jaw would take all the spring travel): shelf width beyond the jaw's outer face at the top plate; the arm overlaps its outer 0.8 mm
    arm_up: float = 1.0         # DESIGN: arm root centre height above the top plate underside (the 7 mm tall arm root spans +-3.3 mm around it)
    E: float = 1700.0           # N/mm2 ASSUMED
    eps_max: float = 0.02       # ASSUMED strain limit for PA12 under long-term load

FLEX = FlexParams(); FLEX_TIGHT = replace(FLEX, gap_tip=2.35)       # variants: N (nominal) and T (tight: for a grip that stays firm if the print comes out loose)

def _frame(P3, s, station, g=G):
    i = int(np.argmin(abs(s - station))); j0, j1 = max(i - 1, 0), min(i + 1, len(P3) - 1)
    tan = Vector(*(P3[j1] - P3[j0])).normalized()
    sec, pl = _section(Vector(*P3[i]), tan, g.temple_t, hfun(s[i], g))
    return i, pl

def flex_profile(P3, s, station, fp: FlexParams = FLEX, g=G):
    """vertical extents of the stem over the clip length in the clip frame -> (v_top_max, v_bottom_min, centre height); measured on the stem model"""
    i, pl = _frame(P3, s, station, g); half = fp.length / 2; vt, vb = -1e9, 1e9
    for k in np.where(abs(s - s[i]) <= half)[0]:
        d = np.array(P3[k]) - np.array(P3[i]); v = d @ _vec(pl.y_dir); h = hfun(s[k], g)
        vt, vb = max(vt, v + h / 2), min(vb, v - h / 2)
    return vt, vb, hfun(s[i], g)

def flex_outline(P3, s, station, fp: FlexParams = FLEX, g=G):
    """(vt_in, vt_out, v_bottom, gap(v)) in the clip frame; v measured from the stem centre at the clip centre, up = the top plate"""
    vtop, vbot, h = flex_profile(P3, s, station, fp, g)
    vt_in = vtop + fp.top_clear; vt_out = vt_in + fp.t_top; vb = vbot - fp.below
    v_narrow = vb + fp.lead_h                      # the narrowest point of the V
    gap = lambda v: fp.gap_tip + (fp.gap_top - fp.gap_tip) * (v - v_narrow) / (vt_in - v_narrow)       # free gap at height v (linear between the narrowest point and the top plate)
    return vt_in, vt_out, vb, gap

def flex_grip(P3, s, station, T_stem, h_stem, fp: FlexParams = FLEX, g=G):
    """for a stem of thickness T_stem and height h_stem pushed up to the top plate: interference per jaw (mm), force per jaw (N) and root strain (%)
    The stem's bottom corners touch the jaws at depth a below the top plate; a jaw is a cantilever of width = clip length minus the slits, thickness t_jaw: k = 3 E I / a^3, strain = 3 t d / (2 a^2)."""
    vt_in, vt_out, vb, gap = flex_outline(P3, s, station, fp, g)
    a = h_stem + fp.top_clear; v_contact = vt_in - a
    d = max(0.0, (T_stem - gap(v_contact)) / 2); I = (fp.length - fp.n_slits * fp.slit_w) * fp.t_jaw ** 3 / 12; k = 3 * fp.E * I / a ** 3
    return d, k * d, 100 * 3 * fp.t_jaw * d / (2 * a ** 2), a

def clip_flex(P3, s, station, fp: FlexParams = FLEX, g=G):
    """-> (clip solid, g, i, engraving spec, arm): arm = dict(lat_outer, shift) tells arm_geom where the arm starts (on the shelf, clear of the jaws)"""
    i, pl = _frame(P3, s, station, g); vt_in, vt_out, vb, gap = flex_outline(P3, s, station, fp, g)
    tj = fp.t_jaw; v_n = vb + fp.lead_h
    def half(v): return gap(v) / 2
    R = [(0, vt_out), (half(vt_in) + tj, vt_out), (half(vb) + tj, vb), (fp.gap_tip / 2 + fp.lead, vb), (fp.gap_tip / 2, v_n), (half(vt_in), vt_in), (0, vt_in)]
    v_n_gap = half(v_n)                                  # below the narrowest point the inner face is cut by the lead-in chamfer; the outer face keeps the jaw thickness t_jaw along the slope
    R[2] = (v_n_gap + tj - (v_n - vb) * (half(vt_in) - v_n_gap) / (vt_in - v_n), vb)
    L = [(-x, y) for x, y in reversed(R[1:-1])]
    pts = R + L
    face = pl * Polygon(*pts, align=None)
    body = extrude(face, amount=fp.length / 2, both=True)
    u_top = half(vt_in) + tj                                           # outer half-width of the top plate / jaw roots
    # finger slits: through both jaws, from below up to the underside of the top plate (the plate stays whole)
    pitch = fp.length / (fp.n_slits + 1)
    for k in range(fp.n_slits):
        w_k = -fp.length / 2 + pitch * (k + 1)
        body = body - pl * Pos(0, (vt_in + vb - 2.0) / 2, w_k) * Box(2 * u_top + 4, vt_in - (vb - 2.0), fp.slit_w)
    # rigid shelf for the arm on the +u side, above the jaws: spans from just inside the plate end to the arm's overlap zone
    v_arm = vt_in + fp.arm_up; v_top_shelf = v_arm + 3.5; u_in = u_top - 0.3; u_out = u_top + fp.shelf_w
    shelf = pl * Pos((u_in + u_out) / 2, (vt_in + v_top_shelf) / 2, 0) * Box(u_out - u_in, v_top_shelf - vt_in, fp.length)
    body = body + shelf
    top_origin = np.array(P3[i]) + _vec(pl.y_dir) * vt_out
    arm = dict(lat_outer=u_out, shift=_vec(pl.y_dir) * v_arm)           # the arm starts at the shelf (arm_geom adds half the arm thickness and overlaps 0.8 mm into it)
    return body, g, i, dict(origin=top_origin, normal=_vec(pl.y_dir), xdir=_vec(pl.z_dir), size=4.0), arm

def flex_span(P3, s, station, T_stem, fp: FlexParams = FLEX, g=G):
    """interference per jaw (mm) at the two ends and the middle of the clip length for a stem of thickness T_stem: the stem tapers and bends along the clip, so its bottom edge sits at different depths"""
    i, pl = _frame(P3, s, station, g); vt_in, vt_out, vb, gap = flex_outline(P3, s, station, fp, g); out = []
    for dk in (-fp.length / 2, 0.0, fp.length / 2):
        k = int(np.argmin(abs(s - (s[i] + dk)))); d = np.array(P3[k]) - np.array(P3[i]); vbot = d @ _vec(pl.y_dir) - hfun(s[k], g) / 2
        out.append(max(0.0, (T_stem - gap(vbot)) / 2))
    return out

if __name__ == "__main__":
    flat = lambda y, z: 0.0
    stem, P3, s = glasses_stem(flat)
    print("stem length", s[-1], "tip", P3[-1], "valid", stem.is_valid, "vol", stem.volume)
    for st in G.clip_stations:
        c, pt = clip_at(P3, s, st); print("clip", st, "valid", c.is_valid, "vol", round(c.volume), "at", pt.round(1))

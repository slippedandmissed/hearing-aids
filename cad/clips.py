"""Glasses-stem clip and spring-arm geometry shared by print_files.py and the blueprint drawings (head coordinates, canal opening = origin)."""
import numpy as np
from dataclasses import replace, dataclass
from build123d import *
import assembly as A
from params import G, H, P
from glasses import glasses_stem, hfun, _section, exciter_arm

stem, P3, s = glasses_stem(A.X0)

def g_for(T, dh, g0=G):
    return replace(g0, temple_t=T, temple_h_hinge=g0.temple_h_hinge + dh, temple_h_straight_end=g0.temple_h_straight_end + dh,
                   temple_h_paddle=g0.temple_h_paddle + dh, temple_h_tip=g0.temple_h_tip + dh)

vec = lambda v: np.array([v.X, v.Y, v.Z])

def clip_geom(station, T, dh):
    g = g_for(T, dh)
    i = int(np.argmin(abs(s - station))); j0, j1 = max(i - 1, 0), min(i + 1, len(P3) - 1)
    tan = Vector(*(P3[j1] - P3[j0])).normalized(); h = hfun(s[i], g)
    ci, co = g.clip_clear, g.clip_wall + g.clip_clear
    sec, pl = _section(Vector(*P3[i]), tan, g.temple_t + 2 * co, h + 2 * co)
    outer = extrude(sec, amount=g.clip_len / 2, both=True)
    inner = extrude(pl * Rectangle(g.temple_t + 2 * ci, h + 2 * ci), amount=g.clip_len, both=True)
    slot = extrude(pl * Pos(0, -(h / 2 + co / 2), 0) * Rectangle(g.temple_t - 0.6, co + 1.0), amount=g.clip_len, both=True)
    top_origin = np.array(P3[i]) + vec(pl.y_dir) * (h / 2 + co)       # centre of the outer top face (opposite the slot)
    return (outer - inner) - slot, g, i, dict(origin=top_origin, normal=vec(pl.y_dir), xdir=vec(pl.z_dir), size=3.6 if station < 110 else 4.0)

def arm_geom(g, i, arm_t, arm=None):
    """arm: what clip_flex returns (dict lat_outer, shift: the arm starts on the clip's shelf); None = the old straight clip wall"""
    lat_outer = g.temple_t / 2 + g.clip_wall + g.clip_clear if arm is None else arm["lat_outer"]
    anchor = np.array(P3[i]) + (0 if arm is None else arm["shift"])
    off = lat_outer + arm_t / 2 - 0.8              # 0.8 mm overlap into the clip: fuses into one solid
    return exciter_arm(A.X0, P3, s, anchor, p=P, h=H, g=g, arm_t=arm_t, lat_off=off)             # default preload = relaxed (printed) shape




# ---------------------------------------------------------------------------------------------------------------- compliant (spring-jaw) clip: geometry lives in glasses.py
import glasses as _gl
from glasses import FlexParams, FLEX, FLEX_TIGHT
def clip_flex(station, fp=FLEX, g=G): return _gl.clip_flex(P3, s, station, fp, g)
def flex_grip(station, T_stem, h_stem, fp=FLEX, g=G): return _gl.flex_grip(P3, s, station, T_stem, h_stem, fp, g)
def flex_span(station, T_stem, fp=FLEX, g=G): return _gl.flex_span(P3, s, station, T_stem, fp, g)
def flex_outline(station, fp=FLEX, g=G): return _gl.flex_outline(P3, s, station, fp, g)
def _frame(station, g=G): return _gl._frame(P3, s, station, g)

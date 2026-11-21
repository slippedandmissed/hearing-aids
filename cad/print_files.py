"""Generate every printable STL (plus manifest) into cad/print/.  uv run python print_files.py   (QUICK=1 builds one variant of each, for testing)

Printed in plain grey MJF nylon (PA12). Per ear (LEFT built, RIGHT = exact mirror):
  clip A      : C-clip at station 100 mm along the stem            -> fit matrix  T (stem thickness) x H (stem height offset)
  clip B + arm: C-clip at station 127 mm FUSED to the spring arm + exciter plate -> same fit matrix at arm 2.8 mm, plus arm 2.4 / 3.2 mm at the middle fit
  Both: ID text engraved 0.4 mm deep.  clips: top face "L"/"R" + T letter + H digit; arm plate: side + arm thickness.
Fit codes:  T letter A..D = stem thickness 3.2 / 3.6 / 4.0 / 4.4 mm;  H digit 1..3 = stem height offset -0.6 / 0 / +0.6 mm (vs. the measured/interpolated profile).
Also: gummy bear shells + back plates (L/R) and the bee box base + cover."""
import os, csv, sys
import numpy as np
from dataclasses import replace
from build123d import *
import assembly as A
from params import G, H, P
import gummy_dangle as gd
import bee_box as bee
from bee_box import HP

OUT = "print"; os.makedirs(OUT, exist_ok=True)
QUICK = bool(os.environ.get("QUICK"))
T_LIST = {"A": 3.2, "B": 3.6, "C": 4.0, "D": 4.4}
H_LIST = {"1": -0.6, "2": 0.0, "3": 0.6}
ARM_MAIN, ARM_EXTRA = 2.8, (2.4, 3.2)
DENS = 1.0                    # g/cm3 effective for MJF PA12 parts
ENGRAVE = 0.4
from clips import stem, P3, s, g_for, vec, clip_geom, arm_geom
MANIFEST = []

def mirrored(shape, specs):
    m = mirror(shape, about=Plane.YZ)
    out = []
    for sp in specs:
        R = np.array([-1.0, 1.0, 1.0])
        out.append(dict(sp, origin=sp["origin"] * R, normal=sp["normal"] * R, xdir=-(sp["xdir"] * R)))        # reading direction flips so text is NOT mirrored on the mirrored part
    return m, out

def engrave(shape, spec, txt):
    pl = Plane(origin=tuple(spec["origin"] + spec["normal"] * 0.05), x_dir=tuple(spec["xdir"]), z_dir=tuple(spec["normal"]))
    t = pl * Text(txt, font_size=spec["size"], font="Helvetica", font_style=FontStyle.BOLD)
    return shape - extrude(t, amount=-(ENGRAVE + 0.05))

def finish(shape, name, qty, note):
    bb = shape.bounding_box()
    shape = shape.move(Location((-(bb.min.X + bb.max.X) / 2, -(bb.min.Y + bb.max.Y) / 2, -bb.min.Z)))      # centre on the origin, lowest point on z=0
    nsol = len(shape.solids()); vol = shape.volume / 1000.0; bb = shape.bounding_box()
    export_stl(shape, f"{OUT}/{name}.stl")
    MANIFEST.append((name + ".stl", qty, round(vol, 2), round(vol * DENS, 1), f"{bb.size.X:.1f} x {bb.size.Y:.1f} x {bb.size.Z:.1f}", "ok" if (shape.is_valid and nsol == 1) else f"CHECK valid={shape.is_valid} solids={nsol}", note))
    print(f"{name:34s} {vol:6.2f} cm3  {bb.size.X:5.1f} x {bb.size.Y:5.1f} x {bb.size.Z:5.1f}  {'ok' if (shape.is_valid and nsol == 1) else 'CHECK'}", flush=True)

def ear_pairs(shape, specs):
    return (("L", shape, specs), ("R",) + mirrored(shape, specs))

# ---------------- clips A and B+arm
fits = [(tl, hd) for tl in T_LIST for hd in H_LIST]
if QUICK: fits = [("B", "2")]
for tl, hd in fits:
    T, dh = T_LIST[tl], H_LIST[hd]
    ca, g, ia, sa = clip_geom(100.0, T, dh)
    for side, shp, specs in ear_pairs(ca, [sa]):
        finish(engrave(shp, specs[0], f"{side}A{tl}{hd}"), f"clipA_{side}_{tl}{hd}", 1, f"stem thickness {T}, height {dh:+.1f} vs nominal; station 100")
    cb, g, ib, sb = clip_geom(127.0, T, dh)
    arm = arm_geom(g, ib, ARM_MAIN)
    part = cb + arm
    plate_x = A.X0(H.mastoid_y, H.mastoid_z) + P.exc_t - H.preload + P.jaw_t
    sp_plate = dict(origin=np.array([plate_x, H.mastoid_y, H.mastoid_z + 4.0]), normal=np.array([1.0, 0, 0]), xdir=np.array([0, 1.0, 0]), size=5.0)
    for side, shp, specs in ear_pairs(part, [sb, sp_plate]):
        shp = engrave(shp, specs[0], f"{side}B{tl}{hd}"); shp = engrave(shp, specs[1], f"{side}{ARM_MAIN}")
        finish(shp, f"clipB_arm{ARM_MAIN}_{side}_{tl}{hd}", 1, f"stem thickness {T}, height {dh:+.1f}; spring arm {ARM_MAIN} mm; station 127")
    del arm, part

# extra spring-arm stiffness variants at the middle fit (B2)
if not QUICK:
    T, dh = T_LIST["B"], H_LIST["2"]
    cb, g, ib, sb = clip_geom(127.0, T, dh)
    for at in ARM_EXTRA:
        part = cb + arm_geom(g, ib, at)
        plate_x = A.X0(H.mastoid_y, H.mastoid_z) + P.exc_t - H.preload + P.jaw_t
        sp_plate = dict(origin=np.array([plate_x, H.mastoid_y, H.mastoid_z + 4.0]), normal=np.array([1.0, 0, 0]), xdir=np.array([0, 1.0, 0]), size=5.0)
        for side, shp, specs in ear_pairs(part, [sb, sp_plate]):
            shp = engrave(shp, specs[0], f"{side}BB2"); shp = engrave(shp, specs[1], f"{side}{at}")
            finish(shp, f"clipB_arm{at}_{side}_B2", 1, f"stem thickness {T}, nominal height; spring arm {at} mm; station 127")

# ---------------- gummy bears and bee box
for side in ("L", "R"):
    sh, lid, _ = gd.build(gd.GP(), side)
    finish(sh, f"bear_shell_{side}", 2, "painted; 1 spare")
    finish(lid, f"bear_backplate_{side}", 2, "engraved letter on the back; 1 spare")
bb_, bc_, _ = bee.build(HP())
finish(bb_, "bee_base", 1, "chain hole through the head; cosmetic flat wings fused to the base")
finish(bc_, "bee_cover", 1, "painted: yellow bumps, black valleys")

with open(f"{OUT}/manifest.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["file", "qty", "volume_cm3", "mass_g_est", "bbox_mm", "check", "note"]); w.writerows(MANIFEST)
tot = sum(r[1] * r[2] for r in MANIFEST)
print(f"files {len(MANIFEST)}; total print volume incl. quantities {tot:.1f} cm3 (~{tot * DENS:.0f} g)")

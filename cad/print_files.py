"""Generate every printable STL (plus manifest) into cad/print/.  uv run python print_files.py   (QUICK=1 builds one variant of each, for testing)

Printed in MJF nylon (PA12): clips and arms and the bee base dyed black, the rest natural grey. Per ear (LEFT built, RIGHT = exact mirror):
  clip + arm: a spring-jaw clip (V-shaped jaws, see clips.clip_flex) at station 127 mm on the glasses stem, FUSED to the spring arm + exciter plate.
                Grip variants N (nominal) and T (tight, a firmer grip if the print comes out loose) at arm 2.8 mm, plus arm 2.4 / 3.2 mm at variant N.
  There is no clip A any more: a separate clip 27 mm along the stem was not connected to anything and could not stabilise the clip (analysis in manual chapter 4); the surviving clip used to be called clip B.
  The ID text is engraved 0.6 mm deep: clip top "L"/"R" + variant letter; arm plate: side + arm thickness.
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
ARM_MAIN, ARM_EXTRA = 2.8, (2.4, 3.2)
DENS = 1.0                    # g/cm3 effective for MJF PA12 parts
ENGRAVE = 0.6      # JLC3DP lists 0.5-0.8 mm as the minimum engraved detail depth/width; 0.6 mm leaves a 1.0 mm floor in the 1.6 mm clip wall (was 0.8 mm deep, 0.8 mm floor)
from clips import stem, P3, s, vec, arm_geom, clip_flex, FLEX, FLEX_TIGHT
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

def centred(shape):
    bb = shape.bounding_box()
    return shape.moved(Location((-(bb.min.X + bb.max.X) / 2, -(bb.min.Y + bb.max.Y) / 2, -bb.min.Z)))      # centre on the origin, lowest point on z=0 (moved() returns a copy; move() would change the shape in place)

def strip_stray(path):
    """the STL export leaves a few single zero-area triangles (0.04 mm) from sliver faces of the B-rep; drop every component of fewer than 10 faces"""
    import trimesh
    m = trimesh.load(path, force="mesh"); m.merge_vertices(); parts = m.split(only_watertight=False)      # vertices must be merged first or every triangle is its own component
    keep = [p for p in parts if len(p.faces) >= 10]
    if len(keep) != len(parts): trimesh.util.concatenate(keep).export(path)

def finish(shape, name, qty, note):
    """export one STL and add it to the manifest (a part must be one valid solid)"""
    shape = centred(shape)
    nsol = len(shape.solids()); vol = shape.volume / 1000.0; bb = shape.bounding_box(); good = shape.is_valid and nsol == 1
    export_stl(shape, f"{OUT}/{name}.stl"); strip_stray(f"{OUT}/{name}.stl")
    MANIFEST.append((name + ".stl", qty, round(vol, 2), round(vol * DENS, 1), f"{bb.size.X:.1f} x {bb.size.Y:.1f} x {bb.size.Z:.1f}", "ok" if good else f"CHECK valid={shape.is_valid} solids={nsol}", note))
    print(f"{name:34s} {vol:6.2f} cm3  {bb.size.X:5.1f} x {bb.size.Y:5.1f} x {bb.size.Z:5.1f}  {'ok' if good else 'CHECK'}", flush=True)
    return shape

def ear_pairs(shape, specs):
    return (("L", shape, specs), ("R",) + mirrored(shape, specs))

# ---------------- clip + arm
plate_x = A.X0(H.mastoid_y, H.mastoid_z) + P.exc_t - H.preload + P.jaw_t
sp_plate = dict(origin=np.array([plate_x, H.mastoid_y, H.mastoid_z + 4.0]), normal=np.array([1.0, 0, 0]), xdir=np.array([0, 1.0, 0]), size=6.5)      # 6.5 mm bold: strokes about 0.75 mm (5 mm gave 0.5 mm strokes that JLC3DP's heatmap flagged red)
VARIANTS = {"N": FLEX} if QUICK else {"N": FLEX, "T": FLEX_TIGHT}
for vn, fp in VARIANTS.items():
    cb, g, ib, sb, lat = clip_flex(127.0, fp)
    for at in ((ARM_MAIN,) + (ARM_EXTRA if (vn == "N" and not QUICK) else ())):
        part = cb + arm_geom(g, ib, at, lat)
        for side, shp, specs in ear_pairs(part, [sb, sp_plate]):
            shp = engrave(shp, specs[0], f"{side}{vn}"); shp = engrave(shp, specs[1], f"{side}{at}")
            finish(shp, f"clip_arm{at}_{side}_{vn}", 1, f"spring-jaw clip, grip {'nominal' if vn == 'N' else 'tight'} (tip gap {fp.gap_tip} mm); spring arm {at} mm; station 127")

# ---------------- gummy bears and bee box
for side in ("L", "R"):
    sh, lid, _ = gd.build(gd.GP(), side)
    finish(sh, f"bear_shell_{side}", 2, "natural grey, painted; 1 spare")
    finish(lid, f"bear_backplate_{side}", 2, "engraved letter on the back; 1 spare")
bb_, bc_, _ = bee.build(HP())
finish(bb_, "bee_base", 2, "dyed black (head, stinger, antennae need no paint; wings painted silver); chain hole through the head; 1 spare")
finish(bc_, "bee_cover", 2, "natural grey, painted: yellow bumps, black valleys; 1 spare")

with open(f"{OUT}/manifest.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["file", "qty", "volume_cm3", "mass_g_est", "bbox_mm", "check", "note"]); w.writerows(MANIFEST)
tot = sum(r[1] * r[2] for r in MANIFEST)
print(f"files {len(MANIFEST)}; total print volume incl. quantities {tot:.1f} cm3 (~{tot * DENS:.0f} g)")

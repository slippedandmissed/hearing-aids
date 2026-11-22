"""Previews of the gummy-bear dangle (out/preview_gummy.png) and the bee necklace box (out/preview_bee.png). uv run python previews.py"""
import os, textwrap
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from build123d import Box, Pos, Cylinder
import gummy_dangle as gd, bee_box as bb
from bee_box import HP

def tris(shape, tol=0.06):
    v, t = shape.tessellate(tol, 0.25); v = np.array([[p.X, p.Y, p.Z] for p in v]); return v[np.array(t)]
def draw(ax, items, el, az, span, ctr):
    e, a = np.radians(el), np.radians(az); L = np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)]); T, C = [], []
    for s, c in items:
        try: t = tris(s)
        except ValueError: continue
        n = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0]); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
        shade = (0.35 + 0.65 * np.abs(n @ L))[:, None]; col = c(t.mean(1)) if callable(c) else np.tile(np.array(c, float), (len(t), 1)); T.append(t); C.append(shade * col)
    ax.add_collection3d(Poly3DCollection(np.vstack(T), facecolors=np.vstack(C), edgecolor="none"))
    ax.set_xlim(ctr[0] - span, ctr[0] + span); ax.set_ylim(ctr[1] - span, ctr[1] + span); ax.set_zlim(ctr[2] - span, ctr[2] + span)
    ax.set_box_aspect((1, 1, 1)); ax.view_init(el, az); ax.set_axis_off()
def sheet(panels, path, note):
    fig = plt.figure(figsize=(18, 11))
    for k, (t, items, el, az, span, ctr) in enumerate(panels):
        ax = fig.add_subplot(2, 3, k + 1, projection="3d"); draw(ax, items, el, az, span, ctr); ax.set_title(textwrap.fill(t, 42), fontsize=12)
    fig.text(0.5, 0.01, textwrap.fill(note, 150), ha="center", va="bottom", fontsize=10); fig.tight_layout(rect=(0, 0.04, 1, 1)); os.makedirs(os.path.dirname(path), exist_ok=True); fig.savefig(path, dpi=80); plt.close(fig)

# ---- bear
g = gd.GP(); shell, lid, i = gd.build(g, "L"); shellR, lidR, _ = gd.build(g, "R"); PINK, BLUE, GREY, GRN = (1.0, 0.45, 0.72), (0.30, 0.72, 1.0), (0.7, 0.7, 0.72), (0.15, 0.55, 0.30)
pcb = Pos(0, g.pcb_y, g.lid_t + g.parts_gap + g.pcb_t / 2) * Box(g.pcb_w, g.pcb_l, g.pcb_t)
half = lambda s: s & Pos(0, -100 + g.pcb_y - 3.7, 0) * Box(300, 200, 300)
sheet([("front, pink (left ear)", [(shell, PINK)], 90, -90, 26, (0, 2, 4)), ("front, blue (right ear)", [(shell, BLUE)], 90, -90, 26, (0, 2, 4)),
       ("3/4 view", [(shell, PINK)], 40, -60, 26, (0, 2, 3)),
       ("inside the shell from the back: screw posts (4), mic ring, PCB stops, strain pegs, cable slot at the top", [(shell, PINK)], -90, -90, 26, (0, 2, 0)),
       ("back plates, as seen from behind: pink L (left ear), blue R (right ear); engraved letters, cable slot at the top", [(shell, PINK), (lid, PINK), (Pos(40, 0, 0) * shellR, BLUE), (Pos(40, 0, 0) * lidR, BLUE)], -90, -90, 34, (20, 2, 0)),
       ("cut across the mic (y=-3.7): PCB between the ring and the lid pillars", [(half(shell), PINK), (half(pcb), GRN), (half(lid), PINK)], 0, 90, 22, (0, 0, 4))],
      "out/preview_gummy.png", "Gummy bear v2: ALL cables leave through the slot at the top of the head (beside the hook loop). Screws: M1.6 x 4 x4 into the posts. Colours illustrative.")

# ---- bee
p = HP(); b = bb.BP(); base, cover, j = bb.build(p, b)
YEL, BLK, SIL, DK = np.array((1.0, 0.82, 0.15)), np.array((0.12, 0.12, 0.14)), np.array((0.85, 0.88, 0.92)), np.array((0.35, 0.35, 0.38))
def cov_col(c):
    out = np.tile(YEL, (len(c), 1)); ab = (c[:, 1] < -22) & (c[:, 2] > j["wing_top"] - 0.3)
    hot = np.zeros(len(c), bool)
    for yc in b.ridge_y: hot |= abs(c[:, 1] - yc) < 2.6
    out[ab & ~hot] = BLK; return out
def base_col(c):
    out = np.tile(DK, (len(c), 1)); out[abs(c[:, 0]) > 31.5] = SIL
    out[(c[:, 1] > 22.5) & (abs(c[:, 0]) < 13)] = BLK; out[(c[:, 1] < j["wy0"] + 1.0)] = BLK; return out
def dummies():
    z_bb, z_bt = j["z_bb"], j["z_bt"]
    return [(Pos(0, 0, (z_bb + z_bt) / 2) * Box(56, 40, 1.6), GRN), (Pos(0, (j["bat_yt"] + j["bat_yb"]) / 2, 2.1 + p.bat_t / 2 - 0.1) * Box(30, 35, p.bat_t), (0.95, 0.6, 0.2)),
            (Pos(2, -1.0, z_bt + 2.5 + 0.6 + 0.9) * Box(21, 17.8, 2.4), (0.25, 0.45, 0.85))]
cx = (0, 8, 8)
sheet([("front (as worn)", [(base, base_col), (cover, cov_col)], 90, -90, 62, cx), ("side", [(base, base_col), (cover, cov_col)], 0, 0, 62, cx),
       ("3/4 view", [(base, base_col), (cover, cov_col)], 38, -55, 62, cx), ("cover off: board + battery (wings = single flat layer on the back)", [(base, base_col)] + dummies(), 70, -90, 62, cx),
       ("from the back (flat)", [(base, base_col), (cover, cov_col)], -90, -90, 62, cx), ("low 3/4 from the side", [(base, base_col), (cover, cov_col)], 12, -25, 62, cx)],
      "out/preview_bee.png", "Cartoon bee v1. Yellow bumps = abdomen segments + thorax dome; black valleys between them = stripes; silver = flat 1-layer wings; black = head/stinger. Colours show intended paint zones.")
print("ok")

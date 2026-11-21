"""Schematic (not to scale) showing the ear/mastoid measurements. uv run python docs/figures/measure_mastoid.py -> docs/build/figures/measure/mastoid.png"""
from common import save, out_path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse

def smooth(pts, closed=True, n=24):
    pts = np.array(pts, float)
    if closed: pts = np.vstack([pts[-1], pts, pts[0], pts[1]])
    else: pts = np.vstack([2 * pts[0] - pts[1], pts, 2 * pts[-1] - pts[-2]])
    out = []
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1:i + 3]
        for t in np.linspace(0, 1, n, endpoint=False):
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t**2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t**3))
    if not closed: out.append(pts[-2])
    return np.array(out)

fig, ax = plt.subplots(figsize=(14, 9))
skin, skin_d = "#f1d3c2", "#e3b7a2"
# head side profile (left side of head, nose to the right)
head = smooth([(-48, -140), (-80, -60), (-98, 10), (-92, 70), (-60, 112), (0, 125), (55, 105), (80, 70), (88, 35), (108, 5), (92, -8), (96, -30), (88, -55), (60, -98), (20, -118), (-5, -125), (-8, -150)])
ax.fill(head[:, 0], head[:, 1], color=skin, ec="#b58b78", lw=1.5, zorder=1)
ax.annotate("front of face / nose", xy=(42, 52), xytext=(5, 52), fontsize=11, color="#a07a68", arrowprops=dict(arrowstyle="->", color="#a07a68", lw=2), va="center")

# ear (helix rim outline), lobe at the bottom
ear = smooth([(8, 28), (2, 38), (-8, 40), (-17, 33), (-22, 20), (-23, 6), (-20, -6), (-14, -18), (-8, -30), (0, -33), (6, -26), (8, -16), (7, -4), (11, 4), (8, 12), (10, 20)])
ax.fill(ear[:, 0], ear[:, 1], color=skin_d, ec="#8e6552", lw=2, zorder=3)
anti = smooth([(2, 28), (-6, 30), (-13, 22), (-15, 8), (-11, -4)], closed=False)
ax.plot(anti[:, 0], anti[:, 1], color="#8e6552", lw=1.5, zorder=4)
ax.add_patch(Ellipse((-1, 2), 9, 14, fc="#c99a86", ec="#8e6552", lw=1.2, zorder=4))
ax.add_patch(Ellipse((8, 2), 5, 8, fc=skin_d, ec="#8e6552", lw=1.2, zorder=5))          # tragus
ax.add_patch(Ellipse((-1.5, 1.5), 3.5, 5, fc="#3a2a24", zorder=6))                        # canal opening

# mastoid bump (behind & below the ear)
ax.add_patch(Ellipse((-30, -18), 17, 24, fc="#d9a58a", ec="#9b5d3f", lw=2, ls="--", zorder=2))
ax.plot(-30, -18, marker="*", ms=22, color="#7a2f9a", zorder=8)

# hidden groove behind the ear (dashed): where the paper strip runs
groove_top = (-10, 36)
path_A = smooth([groove_top, (-21, 28), (-27, 12), (-29, 0), (-30, -10), (-30, -18)], closed=False)
ax.plot(path_A[:, 0], path_A[:, 1], color="#d62728", lw=4.5, zorder=9)
G = (-27, 1.5)
path_B = smooth([G, (-29, -6), (-30, -18)], closed=False)
ax.plot(path_B[:, 0], path_B[:, 1], color="#1f77b4", lw=4.5, zorder=9)
ax.plot([-1.5, G[0]], [1.5, G[1]], color="#1f77b4", lw=1.3, ls=":", zorder=7)

def label(xy, text, xytext, color, **kw):
    ax.annotate(text, xy=xy, xytext=xytext, fontsize=12, color=color, weight="bold",
                arrowprops=dict(arrowstyle="-|>", color=color, lw=1.5), bbox=dict(boxstyle="round,pad=0.4", fc="white", ec=color, lw=1.5), zorder=10, **kw)

label(groove_top, "A starts HERE: the top of the groove behind the ear,\nwhere the top of the ear meets the scalp\n(NOT the top rim of the ear, NOT the canal)", (-98, 42), "#d62728")
label((-30, -18), "mastoid bump = END POINT for A and B\n(hard bone behind & just below the earlobe;\npress there and you'll feel a firm knob)", (-98, -38), "#7a2f9a")
label(G, "B starts HERE: the groove behind the ear,\nlevel with the ear canal opening\n(dotted line = straight back from the canal)", (-98, 9), "#1f77b4")
label((-1.5, 1.5), "ear canal\nopening", (12, -42), "#333333")
ax.text(0, 46, "top rim of the ear (helix)\nnot a start point", fontsize=10, color="#555", ha="center")

ax.text(-27, -60, "Measure ALONG THE SKIN (follow the groove) with a strip of paper: mark the strip with a pen at both ends,\nthen lay it flat against a ruler.   A = red path length (expect roughly 40-50 mm).   B = blue path length (expect roughly 15-30 mm).",
        ha="center", fontsize=11, bbox=dict(boxstyle="round,pad=0.5", fc="#fffbe6", ec="#c9b458"))
ax.set_title("Left ear seen from the left side (schematic, not to scale)\nRed/blue lines run in the groove BEHIND the ear, hidden from this view", fontsize=13)
ax.set_xlim(-100, 45); ax.set_ylim(-62, 62); ax.set_aspect("equal"); ax.axis("off")
fig.tight_layout(); save(fig, "measure", "mastoid", dpi=110)

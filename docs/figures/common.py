"""Shared helpers for every figure script: palette, output paths, a small software STL renderer, block-diagram primitives."""
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FIG = os.path.join(ROOT, "docs", "build", "figures")
TAB = os.path.join(ROOT, "docs", "build", "tables")
sys.path.insert(0, os.path.join(ROOT, "cad"))

C = dict(ink="#1f2933", mute="#6b7785", line="#9aa5b1", paper="#ffffff", accent="#e5489b", blue="#2f8bd6", pink="#ff73b8", yellow="#f5c518", green="#2e9d6b",
         red="#d64545", orange="#f08a24", violet="#7a5fd0", teal="#17a2a2", blueprint="#0b3d91", bp_line="#e8f0ff", bp_dim="#ffd166")
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": C["line"], "axes.labelcolor": C["ink"], "text.color": C["ink"],
                     "xtick.color": C["mute"], "ytick.color": C["mute"], "axes.titleweight": "bold", "figure.dpi": 100, "savefig.dpi": 200})

def out_path(group, name):
    d = os.path.join(FIG, group); os.makedirs(d, exist_ok=True); return os.path.join(d, name)

# Figures are drawn at "design" sizes (up to 20 inches wide) and then scaled to the 6-inch text block of the PDF, which shrinks the text.
# Shrinking the canvas before saving keeps the layout (all positions are data coordinates) but makes the text relatively larger.
VECTOR_GROUPS = {"circuits", "system", "sims", "costs"}
SHRINK = {"system": 1.0, "circuits": 0.72, "sims": 0.65, "costs": 0.7, "blueprints": 0.6, "renders": 0.75, "measure": 0.8}

def save(fig, group, name, **kw):
    s = kw.pop("shrink", SHRINK.get(group, 1.0))
    if s != 1.0: w, h = fig.get_size_inches(); fig.set_size_inches(w * s, h * s)
    p = out_path(group, name if "." in name else name + ".png")
    bb, pad, fc = kw.pop("bbox_inches", "tight"), kw.pop("pad_inches", 0.08), kw.pop("facecolor", fig.get_facecolor())
    fig.savefig(p, bbox_inches=bb, pad_inches=pad, facecolor=fc, **kw)
    if group in VECTOR_GROUPS:                                          # also a vector PDF: the manual embeds it so small text stays sharp when zoomed
        pv = os.path.splitext(p)[0] + ".pdf"; fig.savefig(pv, bbox_inches=bb, pad_inches=pad, facecolor=fc)
    plt.close(fig); print("wrote", os.path.relpath(p, ROOT)); return p

# ------------------------------------------------------------------ software STL / mesh renderer
def load_mesh(path):
    import trimesh
    m = trimesh.load(path); return m.vertices[m.faces]                    # (n, 3, 3) triangles

def subdivide(tris, max_edge):
    """split triangles until every edge is shorter than max_edge: matplotlib sorts by triangle centre, which glitches for long thin or large triangles"""
    import trimesh
    v = tris.reshape(-1, 3); f = np.arange(len(v)).reshape(-1, 3)
    nv, nf = trimesh.remesh.subdivide_to_size(v, f, max_edge=max_edge, max_iter=8)
    return nv[nf]

def draw_tris(ax, items, el=30, az=-60, light=None, edge=False, max_edge=4.0, zoom=1.0):
    """items: [(tris (n,3,3), rgb or fn(tris)->(n,3))]. Flat shaded, depth sorted by matplotlib (large triangles are subdivided first)."""
    e, a = np.radians(el), np.radians(az)
    if max_edge: items = [(subdivide(t_, max_edge), c_) for t_, c_ in items]
    L = np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)]) if light is None else np.asarray(light, float)
    T, Cc = [], []
    for tris, col in items:
        n = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0]); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
        base = col(tris) if callable(col) else np.tile(np.array(matplotlib.colors.to_rgb(col)), (len(tris), 1))
        T.append(tris); Cc.append(np.clip((0.38 + 0.62 * np.abs(n @ L))[:, None] * base, 0, 1))
    T = np.vstack(T); Cc = np.vstack(Cc)
    ax.add_collection3d(Poly3DCollection(T, facecolors=Cc, edgecolor=("#00000022" if edge else "none"), linewidths=0.2))
    P = T.reshape(-1, 3); lo, hi = P.min(0), P.max(0); ctr = (lo + hi) / 2; r = (hi - lo).max() / 2 * 1.02 / zoom
    ax.set_xlim(ctr[0] - r, ctr[0] + r); ax.set_ylim(ctr[1] - r, ctr[1] + r); ax.set_zlim(ctr[2] - r, ctr[2] + r)
    ax.set_box_aspect((1, 1, 1)); ax.view_init(el, az); ax.set_axis_off()
    return lo, hi

def shape_tris(shape, tol=0.08):
    v, t = shape.tessellate(tol, 0.3); v = np.array([[p.X, p.Y, p.Z] for p in v]); return v[np.array(t)]

# ------------------------------------------------------------------ block diagram primitives (axes in data units, y up)
def canvas(w, h, title=None):
    fig, ax = plt.subplots(figsize=(w, h)); ax.set_xlim(0, w); ax.set_ylim(0, h); ax.set_aspect("equal"); ax.axis("off")
    if title: ax.text(0.1, h - 0.15, title, fontsize=11, fontweight="bold", va="top")
    return fig, ax

def box(ax, x, y, w, h, text, fc="#eef2f7", ec=None, fs=8.5, bold=False, tc=None, lw=1.2, r=0.08, ls="-"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=fc, ec=ec or C["line"], lw=lw, ls=ls, zorder=2))
    t = ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, fontweight="bold" if bold else "normal", color=tc or C["ink"], zorder=3, linespacing=1.25)
    try:                                                         # shrink the font until the label fits inside the box (with a margin)
        rend = ax.figure.canvas.get_renderer()
        for _ in range(30):
            bb = t.get_window_extent(rend).transformed(ax.transData.inverted())
            if bb.width <= 0.88 * w and bb.height <= 0.9 * h: break
            t.set_fontsize(t.get_fontsize() - 0.4)
    except Exception: pass

def arrow(ax, p, q, text=None, color=None, lw=1.4, fs=7.5, off=(0, 0.12), both=False, ls="-", rad=0.0, tcolor=None):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="<|-|>" if both else "-|>", mutation_scale=9, color=color or C["mute"], lw=lw, ls=ls, zorder=1, connectionstyle=f"arc3,rad={rad}"))
    if text: ax.text((p[0] + q[0]) / 2 + off[0], (p[1] + q[1]) / 2 + off[1], text, ha="center", va="bottom", fontsize=fs, color=tcolor or C["mute"])

def group(ax, x, y, w, h, label, ec=None, fc="none", fs=8):
    ax.add_patch(Rectangle((x, y), w, h, fc=fc, ec=ec or C["line"], lw=1.0, ls=(0, (4, 3)), zorder=0))
    ax.text(x + 0.08, y + h - 0.06, label, fontsize=fs, color=ec or C["mute"], va="top", fontweight="bold")


def smooth(pts, closed=True, n=24):
    """Catmull-Rom smoothing of a 2D polyline (closed or open)"""
    pts = np.array(pts, float)
    pts = np.vstack([pts[-1], pts, pts[0], pts[1]]) if closed else np.vstack([2 * pts[0] - pts[1], pts, 2 * pts[-1] - pts[-2]])
    out = []
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1:i + 3]
        for t in np.linspace(0, 1, n, endpoint=False): out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t ** 2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    if not closed: out.append(pts[-2])
    return np.array(out)

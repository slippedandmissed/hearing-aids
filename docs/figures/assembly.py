"""The three generated figures that the assembly guide still uses: the printed parts and the clip grips and arms (Step 0) and the XIAO back pads (Step 3), drawn from the real CAD files.
Every other assembly figure is a hand-drawn SVG in docs/assets/, and the manual draws the step numbers and titles itself (docs/manual/header.tex), so these carry none.
uv run python docs/figures/assembly.py   (writes docs/build/figures/assembly/step00b.png, step00c.png, step03.png)"""
import os
from common import *
from matplotlib.patches import Circle, Polygon, Rectangle, FancyBboxPatch

PRINT = os.path.join(ROOT, "cad", "print")
INK, FILL, ACC = "#111111", "#f1f1ef", "#e5483b"
PINK, BLUE, YEL = "#ff8ec8", "#52b6ff", "#ffd23f"

def canvas(w, h):
    """a blank figure of w x h drawing units (0.72 inch per unit), axes filling it"""
    fig = plt.figure(figsize=(w * 0.72, h * 0.72), facecolor="white"); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, w); ax.set_ylim(0, h); ax.axis("off")
    return fig, ax

def mesh(n): return load_mesh(os.path.join(PRINT, n + ".stl"))

def badge(ax, x, y, txt, r=0.28):
    ax.add_patch(Circle((x, y), r, fc="white", ec=INK, lw=1.8, zorder=6)); ax.text(x, y, txt, ha="center", va="center", fontsize=11, fontweight="bold", zorder=7)

def warn(ax, x, y, txt, w=3.6, color=ACC):
    ax.add_patch(Polygon([(x, y + 0.55), (x - 0.5, y - 0.3), (x + 0.5, y - 0.3)], fc="#ffd23f", ec=INK, lw=2, zorder=6)); ax.text(x, y - 0.02, "!", ha="center", va="center", fontsize=16, fontweight="bold", zorder=7)
    import textwrap
    wmax = min(w, ax.get_xlim()[1] - (x + 0.7) - 0.3)
    ax.text(x + 0.7, y + 0.1, textwrap.fill(txt, max(12, int(wmax / 0.128))), ha="left", va="center", fontsize=9, color=INK, linespacing=1.25)

def big_arrow(ax, p, q, color=INK, lw=3, text=None, fs=9, off=(0, 0.22)):
    ax.annotate("", xy=q, xytext=p, arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, mutation_scale=18), zorder=5)
    if text: ax.text((p[0] + q[0]) / 2 + off[0], (p[1] + q[1]) / 2 + off[1], text, ha="center", va="bottom", fontsize=fs, color=color, fontweight="bold")

def line_rect(ax, x, y, w, h, fc=FILL, ec=INK, lw=2, r=0.0, z=2):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=fc, ec=ec, lw=lw, zorder=z))

def wire(ax, pts, color, lw=3.2, z=4):
    xs, ys = zip(*pts); ax.plot(xs, ys, color="black", lw=lw + 1.6, solid_capstyle="round", zorder=z - 0.1); ax.plot(xs, ys, color=color, lw=lw, solid_capstyle="round", zorder=z)

def tris_3d(fig, rect, items, el=30, az=-55, boxes=(), zoom=1.0):
    """a transparent 3D axes occupying `rect` (fig coords) holding shaded triangles"""
    a3 = fig.add_axes(rect, projection="3d"); a3.patch.set_alpha(0); draw_tris(a3, items, el=el, az=az, zoom=zoom); return a3

def _tri_cell(fig, H, cx, cy, w, h, name, col, el, az, zoom=1.0):
    T = mesh(name); tris_3d(fig, [(cx - w / 2) / 12, (cy - h / 2) / H, w / 12, h / H], [(T, col)], el=el, az=az, zoom=zoom)
    lo, hi = T.reshape(-1, 3).min(0), T.reshape(-1, 3).max(0); return hi - lo

def step00b():
    import textwrap
    H = 7.3
    fig, ax = canvas(12, H)
    cells = [("Clip + spring arm, left", "clip_arm2.8_L_N", "#59616e", 20, -30, "×4"), ("Clip + spring arm, right", "clip_arm2.8_R_N", "#59616e", 20, -30, "×4"),
             ("Bear shell, left", "bear_shell_L", PINK, 55, -55, "×2"), ("Back plate, left", "bear_backplate_L", PINK, 55, -55, "×2"),
             ("Bear shell, right", "bear_shell_R", BLUE, 55, -55, "×2"), ("Back plate, right", "bear_backplate_R", BLUE, 55, -55, "×2"),
             ("Bee base", "bee_base", "#59616e", 40, -55, "×2"), ("Bee cover", "bee_cover", YEL, 40, -55, "×2")]
    for k, (t, n, col, el, az, q) in enumerate(cells):
        cx = 1.6 + (k % 4) * 3.0; cy = 5.5 - (k // 4) * 3.05
        d = _tri_cell(fig, H, cx, cy, 2.6, 2.1, n, col, el, az, zoom=(1.5 if "clip_" in n else 1.25))
        ax.text(cx, cy - 1.15, t, ha="center", va="top", fontsize=9.5, fontweight="bold"); ax.text(cx, cy - 1.5, f"{d[0]:.0f} × {d[1]:.0f} × {d[2]:.0f} mm", ha="center", va="top", fontsize=9)
        badge(ax, cx - 1.3, cy + 1.0, q.split()[0], 0.28)
        if len(q.split()) > 1: ax.text(cx - 0.92, cy + 1.0, " ".join(q.split()[1:]).strip("()"), ha="left", va="center", fontsize=8, color="#444444")
    ax.text(0.5, 0.45, textwrap.fill("JLC3DP or a UK MJF bureau, PA12 nylon: clips, arms and bee base dyed black, the rest natural grey. Bears and bee cover are painted afterwards (step 2). One spare of each bear and bee part. The clips come in four variants per ear: grips N and T, and arms 2.4, 2.8 and 3.2 mm.", 100), fontsize=9, color="#444444", va="center", linespacing=1.3)
    return fig

def step00c():
    H = 7.3
    fig, ax = canvas(12, H)
    ax.text(0.5, 7.05, "Clip grips: two variants per ear", fontsize=9.5, fontweight="bold", va="center")
    for k, (t, sub, nm) in enumerate((("N: nominal", "try this first", "clip_arm2.8_L_N"), ("T: tight", "if N is loose on the glasses arm", "clip_arm2.8_L_T"))):
        cx = 2.2 + k * 3.6; _tri_cell(fig, H, cx, 5.4, 1.7, 1.7, nm, "#59616e", 20, -30, zoom=1.4)
        ax.text(cx, 4.35, t, fontsize=10, fontweight="bold", va="center", ha="center"); ax.text(cx, 4.0, sub, fontsize=8.5, va="center", ha="center", color="#444444")
    ax.text(8.2, 5.4, "The jaws spring apart when\nthe clip is pushed onto the\nglasses arm. Designed for a flat\narm about 3.2 - 4.2 mm thick\n(calculated, not tested).\nTry them in step 12.", fontsize=8.5, va="center", ha="left", color="#444444")
    ax.text(0.5, 2.15, "Spring arm thickness (the 2.8 mm arm is printed with both grips)", fontsize=9.5, fontweight="bold", va="center")
    for k, (t, sub) in enumerate((("2.4 mm", "softer: less force on the bone"), ("2.8 mm", "default"), ("3.2 mm", "stiffer: more force"))):
        cx = 2.2 + k * 3.2; _tri_cell(fig, H, cx, 1.4, 1.5, 1.5, f"clip_arm{t[:3]}_L_N", "#59616e", 5, -90, zoom=1.3)
        ax.text(cx, 0.6, t, fontsize=10, fontweight="bold", va="center", ha="center"); ax.text(cx, 0.25, sub, fontsize=8.5, va="center", ha="center", color="#444444")
    return fig

# ============================================================================== 3. XIAO battery wires
def step03():
    fig, ax = canvas(12, 6.4)
    # XIAO back view, 21 x 17.8 mm drawn at scale 0.27 inch/mm (~) : width 21 mm -> 5.8 units
    s = 0.28; cx, cy = 3.7, 3.6; w, h = 21 * s, 17.8 * s
    line_rect(ax, cx - w / 2, cy - h / 2, w, h, fc="#2c6bd1", lw=3, r=0.1); ax.text(cx, cy + 1.0, "XIAO nRF52840 — BACK", ha="center", color="white", fontsize=10, fontweight="bold")
    ax.add_patch(Rectangle((cx + w / 2 - 0.5, cy - 0.6), 0.5, 1.2, fc="#c0c0c0", ec=INK, lw=1.5)); ax.text(cx + w / 2 + 0.1, cy, "USB-C end", fontsize=8, rotation=90, va="center")
    px = [(cx + 0.317 * s, cy - 4.445 * s), (cx + 2.222 * s, cy - 4.445 * s)]
    for (x, y), nm, col in zip(px, ("BAT+", "BAT−"), ("#d93a3a", "#111111")):
        ax.add_patch(Rectangle((x - 0.14, y - 0.28), 0.28, 0.56, fc="#e8c34a", ec=INK, lw=1.5, zorder=3)); ax.text(x + (-0.12 if nm == "BAT+" else 0.12), y + 0.6, nm, ha=("right" if nm == "BAT+" else "left"), fontsize=9, fontweight="bold", color="white")
        wire(ax, [(x, y), (x, y - 1.8 - (0.0 if nm == "BAT+" else 0.4)), (x + (2.4 if nm == "BAT+" else 3.0), y - 1.8 - (0.0 if nm == "BAT+" else 0.4))], col, 3)
    ax.text(0.6, 0.5, "pads ≈ 1 × 2 mm,\n1.9 mm apart", ha="left", fontsize=8.5)
    big_arrow(ax, (7.2, 3.0), (8.0, 3.0)); ax.text(8.2, 3.0, "other ends go to the\ncarrier holes B+ / B−\n(see the next steps)", fontsize=9, va="center")
    warn(ax, 8.0, 1.2, "Do this BEFORE the XIAO goes on the carrier: the pads end up underneath.", 3.6)
    return fig

STEPS = [step00b, step00c, step03]

if __name__ == "__main__":
    for f in STEPS:
        fig = f()
        for t in fig.axes[0].texts: t.set_fontsize(t.get_fontsize() * 1.2)
        save(fig, "assembly", f.__name__, dpi=150)

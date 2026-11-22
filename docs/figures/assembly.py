"""IKEA-style assembly figures: one image per step, drawn from the real CAD files, PCB renders and board coordinates.
uv run python docs/figures/assembly.py   (writes docs/build/figures/assembly/stepNN_*.png)"""
import os
from PIL import Image
import matplotlib.patches
from common import *
from matplotlib.patches import Circle, Polygon, Rectangle, FancyBboxPatch
from build123d import Box, Cylinder, Pos, Rot
import gummy_dangle as gd
import bee_box as bee

PRINT = os.path.join(ROOT, "cad", "print")
INK, FILL, ACC = "#111111", "#f1f1ef", "#e5483b"
PINK, BLUE, YEL = "#ff8ec8", "#52b6ff", "#ffd23f"

def mesh(n): return load_mesh(os.path.join(PRINT, n + ".stl"))
def pcb_img(name): return Image.open(os.path.join(FIG, "renders", name))

# ------------------------------------------------------------------ IKEA-style page furniture
def page(n, title, w=12, h=7.6, header=True):
    fig = plt.figure(figsize=(w * 0.72, h * 0.72), facecolor="white"); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, w); ax.set_ylim(0, h); ax.axis("off")
    if not header: return fig, ax          # the manual draws the step number and title itself (header.tex \steptitle); a figure carries none
    ax.add_patch(Circle((0.75, h - 0.75), 0.5, fc="white", ec=INK, lw=3)); ax.text(0.75, h - 0.78, str(n), ha="center", va="center", fontsize=26, fontweight="bold")
    ax.text(1.55, h - 0.75, title, ha="left", va="center", fontsize=15 * 0.9, fontweight="bold")
    ax.plot([0.25, w - 0.25], [h - 1.4, h - 1.4], color=INK, lw=1)
    return fig, ax

def badge(ax, x, y, txt, r=0.28):
    ax.add_patch(Circle((x, y), r, fc="white", ec=INK, lw=1.8, zorder=6)); ax.text(x, y, txt, ha="center", va="center", fontsize=11, fontweight="bold", zorder=7)

def warn(ax, x, y, txt, w=3.6, color=ACC):
    ax.add_patch(Polygon([(x, y + 0.55), (x - 0.5, y - 0.3), (x + 0.5, y - 0.3)], fc="#ffd23f", ec=INK, lw=2, zorder=6)); ax.text(x, y - 0.02, "!", ha="center", va="center", fontsize=16, fontweight="bold", zorder=7)
    import textwrap
    wmax = min(w, ax.get_xlim()[1] - (x + 0.7) - 0.3)
    ax.text(x + 0.7, y + 0.1, textwrap.fill(txt, max(12, int(wmax / 0.128))), ha="left", va="center", fontsize=9, color=INK, linespacing=1.25)

def tick(ax, x, y, txt, color="#1a8f4d"):
    ax.add_patch(Circle((x, y), 0.26, fc=color, ec=INK, lw=1.5, zorder=6)); ax.text(x, y - 0.02, "✓", ha="center", va="center", fontsize=13, color="white", fontweight="bold", zorder=7)
    ax.text(x + 0.45, y, txt, ha="left", va="center", fontsize=9)

def big_arrow(ax, p, q, color=INK, lw=3, text=None, fs=9, off=(0, 0.22)):
    ax.annotate("", xy=q, xytext=p, arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, mutation_scale=18), zorder=5)
    if text: ax.text((p[0] + q[0]) / 2 + off[0], (p[1] + q[1]) / 2 + off[1], text, ha="center", va="bottom", fontsize=fs, color=color, fontweight="bold")

def line_rect(ax, x, y, w, h, fc=FILL, ec=INK, lw=2, r=0.0, z=2):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=fc, ec=ec, lw=lw, zorder=z))

def wire(ax, pts, color, lw=3.2, z=4):
    xs, ys = zip(*pts); ax.plot(xs, ys, color="black", lw=lw + 1.6, solid_capstyle="round", zorder=z - 0.1); ax.plot(xs, ys, color=color, lw=lw, solid_capstyle="round", zorder=z)

def image_at(ax, img, x, y, w, h=None, z=1):
    h = h or w * img.height / img.width; ax.imshow(img, extent=(x, x + w, y, y + h), zorder=z, aspect="auto"); return h

def tris_3d(fig, rect, items, el=30, az=-55, boxes=(), zoom=1.0):
    """a transparent 3D axes occupying `rect` (fig coords) holding shaded triangles"""
    a3 = fig.add_axes(rect, projection="3d"); a3.patch.set_alpha(0); draw_tris(a3, items, el=el, az=az, zoom=zoom); return a3

def box_tris(shape): return shape_tris(shape, 0.05)

# ============================================================================== 0. what is in the box
def step00():
    H = 9.4
    fig, ax = page("0", "Check what you have (1/3): electronics and hardware", 12, H)
    ax.text(0.5, 7.55, "From JLCPCB (assembled except the through-hole parts)", fontsize=9.5, fontweight="bold", va="center")
    items = [("Dangle PCB\nLEFT", "pcb_dangle_L_top.png"), ("Dangle PCB\nRIGHT", "pcb_dangle_R_top.png"), ("Carrier PCB", "pcb_carrier_top.png")]
    x = 0.5
    for t, f in items:
        im = pcb_img(f); hgt = 2.0; wd = hgt * im.width / im.height; image_at(ax, im, x, 5.2, wd, hgt); badge(ax, x + 0.05, 7.15, "×1", 0.25)
        ax.text(x + wd / 2, 5.05, t, ha="center", va="top", fontsize=8.0); x += max(wd, 1.1) + 0.45
    ax.text(8.6, 6.4, "The 58 printed parts are\nshown on the next two pages.", fontsize=9.5, va="center", color="#444444")
    ax.text(0.5, 4.3, "Off the shelf (not designed here)", fontsize=9.5, fontweight="bold", va="center")
    stuff = [("XIAO nRF52840\nwith pin headers", 2), ("500 mAh LiPo\n(JST-PH plug)", 1), ("Exciter\nDAEX-9-4SM", 3), ("Ribbon cable\n30 AWG, 1 m", 4), ("M1.6 × 4\nscrews", 8), ("M2 × 4\nscrews", 2), ("Ear-hook\nwires", 2), ("Necklace\nchain", 1), ("Foam ring /\nsilicone dab", 2)]
    cols = 5; cells = []
    for k, (t, q) in enumerate(stuff):
        cx = 1.3 + (k % cols) * 2.35; cy = 3.2 - (k // cols) * 1.9; cells.append((cx, cy))
        line_rect(ax, cx - 0.85, cy - 0.5, 1.7, 1.0, fc="#f1f1ef", lw=1.4, r=0.1); badge(ax, cx - 0.85, cy + 0.5, f"×{q}", 0.25)
        ax.text(cx, cy - 0.62, t, ha="center", va="top", fontsize=8.0)
    def small3d(k, items, el=40, az=-50):
        cx, cy = cells[k]; tris_3d(fig, [(cx - 1.2) / 12, (cy - 0.9) / H, 2.4 / 12, 1.8 / H], items, el=el, az=az)
    small3d(0, [(box_tris(Box(21, 17.8, 1.2)), "#1f3d7a"), (box_tris(Pos(-8.5, 0, 2.2) * Box(8, 8.5, 3.2)), "#c9ced6"), (box_tris(Pos(3, 0, 1.2) * Box(7, 7, 1)), "#222222"), (box_tris(Pos(2, 8.4, 0.9) * Box(17, 1.8, 2.4)), "#d9b44a"), (box_tris(Pos(2, -8.4, 0.9) * Box(17, 1.8, 2.4)), "#d9b44a")])
    small3d(1, [(box_tris(Box(35, 30, 5.5)), "#8a96ad"), (box_tris(Pos(-20.5, -3, 0) * Box(6, 1.2, 1.2)), "#d33b33"), (box_tris(Pos(-20.5, 3, 0) * Box(6, 1.2, 1.2)), "#111111"), (box_tris(Pos(-25.5, 0, 0) * Box(4, 9, 4)), "#f4f1e8")])
    small3d(2, [(box_tris(Box(26.5, 13, 5.75)), "#2d2d30"), (box_tris(Pos(0, 0, 3.0) * Box(23.5, 10.5, 0.9)), "#b8bcc4")])
    cx, cy = cells[3]                                           # ribbon: coloured parallel wires
    for i, col in enumerate(("#d33b33", "#f0a030", "#e6d233", "#3a9d4a", "#3a6fd1", "#8a4fc0")): ax.plot([cx - 0.7, cx + 0.7], [cy + 0.3 - i * 0.12, cy + 0.3 - i * 0.12 - 0.05], color=col, lw=3.2, solid_capstyle="round", zorder=5)
    for k in (4, 5):                                           # screws
        cx, cy = cells[k]
        for dx in (-0.4, 0.0, 0.4):
            ax.plot([cx + dx - 0.12, cx + dx + 0.12], [cy - 0.1, cy + 0.15], color="#6f7681", lw=4.5, solid_capstyle="butt", zorder=5); ax.add_patch(Circle((cx + dx + 0.12, cy + 0.16), 0.1 if k == 4 else 0.13, fc="#9aa1ab", ec=INK, lw=1.2, zorder=6))
    cx, cy = cells[6]; t = np.linspace(0, 1, 40); ax.plot(cx - 0.6 + 1.2 * t, cy - 0.3 + 0.9 * np.sin(np.pi * t) ** 0.8, color="#b0b5bd", lw=4, zorder=5, solid_capstyle="round")   # ear hook wire
    cx, cy = cells[7]                                           # chain
    for i in range(6): ax.add_patch(matplotlib.patches.Ellipse((cx - 0.65 + i * 0.26, cy + (0.12 if i % 2 else -0.12) * 0.5), 0.34, 0.2 if i % 2 else 0.3, angle=0 if i % 2 else 90, fc="none", ec="#a7acb4", lw=2.4, zorder=5))
    cx, cy = cells[8]; ax.add_patch(Circle((cx - 0.35, cy), 0.28, fc="none", ec="#e9d7a8", lw=7, zorder=5)); ax.add_patch(Circle((cx + 0.5, cy), 0.2, fc="#e8edf3", ec="#9aa1ab", lw=1.5, zorder=5))
    return fig


def _tri_cell(fig, H, cx, cy, w, h, name, col, el, az, zoom=1.0):
    T = mesh(name); tris_3d(fig, [(cx - w / 2) / 12, (cy - h / 2) / H, w / 12, h / H], [(T, col)], el=el, az=az, zoom=zoom)
    lo, hi = T.reshape(-1, 3).min(0), T.reshape(-1, 3).max(0); return hi - lo

def step00b():
    import textwrap
    H = 7.3
    fig, ax = page(None, None, 12, H, header=False)
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
    fig, ax = page(None, None, 12, H, header=False)
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

# ============================================================================== 1. inspect the boards
def step01():
    fig, ax = page(1, "Look before you solder")
    im = pcb_img("pcb_carrier_top.png"); wd = 6.2; hgt = image_at(ax, im, 0.5, 1.3, wd)
    big_arrow(ax, (7.6, 4.4), (6.0, 3.8)); ax.text(7.7, 4.1, "no solder bridges between pads", fontsize=9, fontweight="bold")
    ax.text(7.7, 3.3, "A magnifier or a phone macro photo\nhelps. Compare with the render.", fontsize=9)
    tick(ax, 7.8, 5.7, "SMD parts present"); tick(ax, 7.8, 5.1, "silkscreen reads ‘morgan’")
    warn(ax, 8.0, 2.0, "Nothing here has been tested on real hardware yet.", 3.6)
    return fig

# ============================================================================== 2. paint
def step02():
    fig, ax = page(2, "Prime and paint the printed parts (let each coat dry)")
    for k, (txt, col) in enumerate((("1  Sand lightly\n(400 grit)", "#d9d9d9"), ("2  Plastic primer", "#bdbdbd"), ("3  Base colour:\nbears pink / blue,\nbee yellow", PINK), ("4  Details: bee stripes\nblack, wings silver,\nbear eyes + nose", "#222222"), ("5  Clear lacquer\n(not on flexing clips)", "#f7f7f7"))):
        x = 0.7 + k * 2.3; ax.add_patch(Circle((x + 0.9, 5.2), 0.7, fc=col, ec=INK, lw=2.5)); ax.text(x + 0.9, 3.9, txt, ha="center", va="top", fontsize=8.5, fontweight="bold")
        if k < 4: big_arrow(ax, (x + 1.7, 5.2), (x + 2.1, 5.2), lw=2)
    sh, lid = mesh("bear_shell_L"), mesh("bee_cover")
    a3 = tris_3d(fig, [0.04, 0.08, 0.22, 0.42], [(sh, PINK)], el=75, az=-90); a3b = tris_3d(fig, [0.30, 0.08, 0.28, 0.42], [(lid, lambda t: np.where((t.mean(1)[:, 1] < -22)[:, None], np.array([[0.12, 0.12, 0.14]]), np.array([[1.0, 0.82, 0.25]])))], el=75, az=-90)
    warn(ax, 8.0, 1.9, "Keep paint out of the mic port, the screw holes and the clip cavities. The spring arm and clips stay unpainted.", 3.8)
    return fig

# ============================================================================== 3. XIAO battery wires
def step03():
    fig, ax = page(None, None, 12, 6.4, header=False)
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

# ============================================================================== 4. XIAO onto carrier (side view + top view)
def step04():
    fig, ax = page(4, "Solder the XIAO straight onto the carrier")
    x0, y0, w = 0.5, 3.0, 4.6
    ax.add_patch(Rectangle((x0, y0), w, 0.22, fc="#2b7a52", ec=INK, lw=2)); ax.text(x0 + w + 0.15, y0 + 0.1, "carrier 1.6 mm", fontsize=8.5, va="center")
    ax.add_patch(Rectangle((x0 + 0.6, y0 + 0.22), w - 1.2, 0.3, fc="#222222", ec=INK, lw=2)); ax.text(x0 + w + 0.15, y0 + 0.6, "pin-header plastic 2.5 mm", fontsize=8.5, va="center")
    ax.add_patch(Rectangle((x0 + 0.6, y0 + 0.52), w - 1.2, 0.14, fc="#2c6bd1", ec=INK, lw=2)); ax.text(x0 + w + 0.15, y0 + 1.0, "XIAO 1.2 mm", fontsize=8.5, va="center")
    ax.add_patch(Rectangle((x0 + w - 1.9, y0 + 0.66), 0.9, 0.34, fc="#c0c0c0", ec=INK, lw=2)); ax.text(x0 + w - 1.45, y0 + 1.15, "USB-C", ha="center", fontsize=8)
    for k in range(7): ax.plot([x0 + 0.9 + k * 0.5] * 2, [y0 - 0.25, y0 + 0.22], color="#c9a227", lw=3)
    ax.text(x0 + 1.4, y0 - 0.55, "trim the pin tails to ≤ 1 mm after soldering", fontsize=9, fontweight="bold", color=ACC)
    big_arrow(ax, (x0 + 1.3, y0 + 2.4), (x0 + 1.3, y0 + 0.85)); ax.text(x0 + 1.5, y0 + 2.2, "press down until the\nplastic touches the board", fontsize=8.5)
    im = pcb_img("pcb_carrier_top.png"); image_at(ax, im, 8.4, 1.6, 3.4)
    ax.annotate("", xy=(11.5, 2.85), xytext=(11.95, 2.85), arrowprops=dict(arrowstyle="-|>", lw=3, color=ACC)); ax.text(9.7, 4.6, "USB-C points to the RIGHT edge", ha="center", fontsize=9, fontweight="bold", color=ACC)
    return fig

# ============================================================================== 5. JST + switch
def step05():
    fig, ax = page(5, "Solder the battery socket and the slide switch")
    im = pcb_img("pcb_carrier_top.png"); hgt = image_at(ax, im, 0.6, 1.3, 6.4)
    sx = lambda x: 0.6 + (x / 56.0) * 6.4 * 0.96 + 0.1; sy = lambda y: 1.3 + hgt - 0.1 - (y / 40.0) * hgt * 0.93
    big_arrow(ax, (sx(2), sy(31) + 0.0), (sx(11) - 0.9, sy(31)), ACC, 4); ax.text(0.5, 0.6, "JST-PH socket: the plug enters from the LEFT edge", fontsize=9, fontweight="bold", color=ACC)
    big_arrow(ax, (sx(19.5), sy(3.8) - 1.2), (sx(19.5), sy(3.8) - 0.3), INK, 4); ax.text(7.4, 5.7, "slide switch lever sticks\nout of the top edge", fontsize=9, fontweight="bold", va="center")
    warn(ax, 7.6, 3.5, "LiPo plugs have NO standard polarity. Check which wire is red against the + and − silkscreen BEFORE plugging in. If they are swapped, swap the two wires inside the plug with a pin or tweezers.", 3.2)
    return fig

# ============================================================================== 6. neck cables
def step06():
    fig, ax = page(6, "Prepare four ribbon cables (two per ear)")
    cols = ["#d93a3a", "#f08a24", "#f5c518", "#1a8f4d"]
    for r, (name, y) in enumerate((("ribbon A", 4.8), ("ribbon B", 3.3))):
        line_rect(ax, 2.0, y - 0.55, 6.0, 1.1, fc="#e9ecef", lw=1.5, r=0.1)
        for k in range(4):
            yy = y + 0.38 - k * 0.25; wire(ax, [(1.0, yy), (8.9, yy)], cols[k], 2.6)
        ax.text(0.5, y, name, ha="right", va="center", fontsize=10, fontweight="bold"); ax.text(9.2, y + 0.35, "wire 1\n…\nwire 4", fontsize=7.5, va="center")
    ax.text(0.5, 5.85, "60 cm each (box to ear + 10 cm spare), 4 wires per ribbon", fontsize=9, fontweight="bold", va="center")
    big_arrow(ax, (3.0, 2.55), (3.0, 2.0)); ax.text(3.2, 2.3, "strip 2 mm, twist, tin", fontsize=9)
    tbl = [("ribbon A wire 1", "pad 1  I2S_LRCLK"), ("ribbon A wire 2", "pad 2  I2S_DIN"), ("ribbon A wire 3", "pad 3  VBAT"), ("ribbon A wire 4", "pad 4  PDM_DATA"), ("ribbon B wire 1", "pad 5  I2S_BCLK"), ("ribbon B wire 2", "pad 6  GND"), ("ribbon B wire 3", "pad 7  PDM_CLK"), ("ribbon B wire 4", "pad 8  GND")]
    for k, (a, b) in enumerate(tbl): ax.text(0.7, 1.75 - k * 0.24, f"{a}  →  {b}", fontsize=8.5, family="monospace")
    warn(ax, 7.2, 1.3, "Mark the first wire of every ribbon with a dab of paint or tape at BOTH ends.", 4.0)
    return fig

# ============================================================================== 7. cables to the carrier
def step07():
    fig, ax = page(7, "Solder the ribbons to the two ear blocks on the carrier")
    im = pcb_img("pcb_carrier_top.png"); hgt = image_at(ax, im, 2.2, 0.6, 7.6)
    sx = lambda x: 2.2 + (x / 56.0) * 7.6 * 0.96 + 0.2; sy = lambda y: 0.6 + hgt - 0.15 - (y / 40.0) * hgt * 0.92
    wire(ax, [(sx(5.5), sy(3.8)), (sx(5.5), sy(-1.0)), (sx(2.5), sy(-2.2))], "#ff73b8", 4); wire(ax, [(sx(46.5), sy(3.8)), (sx(46.5), sy(-1.0)), (sx(49.5), sy(-2.2))], "#2f8bd6", 4)
    ax.text(0.4, 5.6, "LEFT ear block\n(pads 1–8)", fontsize=9, fontweight="bold", color="#e5489b"); ax.text(11.6, 5.6, "RIGHT ear block\n(pads 1–8)", fontsize=9, fontweight="bold", color="#2f8bd6", ha="right")
    return fig

# ============================================================================== 8. dangle PCB wires
def step08():
    fig, ax = page(8, "Solder the cable and the exciter wires to each dangle PCB")
    for k, (side, f) in enumerate((("LEFT", "pcb_dangle_L_top.png"), ("RIGHT", "pcb_dangle_R_top.png"))):
        im = pcb_img(f); hgt = 4.5; wd = hgt * im.width / im.height; x = 0.8 + k * 3.0; image_at(ax, im, x, 1.0, wd, hgt); ax.text(x + wd / 2, 5.85, f"{side} dangle", ha="center", fontsize=10, fontweight="bold")
    x = 0.8; wd = 4.5 * pcb_img("pcb_dangle_L_top.png").width / pcb_img("pcb_dangle_L_top.png").height
    ax.text(7.4, 5.0, "Cable in from the top: ribbon A to\npads 1–4, ribbon B to pads 5–8", fontsize=9, fontweight="bold", color=ACC, va="top")
    big_arrow(ax, (x + wd * 0.5, 0.45), (x + wd * 0.5, 1.0)); ax.text(x + wd * 0.5, 0.15, "exciter wires (EXC+ / EXC−)", ha="left", fontsize=8.5, fontweight="bold")
    warn(ax, 7.6, 2.8, "Keep the solder blobs on the bottom face tiny: they sit in a 0.6 mm pocket in the bear's front wall.", 3.0)
    return fig

# ============================================================================== 9. bear exploded
def step09():
    fig, ax = page(9, "Assemble each gummy bear (exploded view)")
    g = gd.GP(); shell = mesh("bear_shell_L"); lid = mesh("bear_backplate_L")
    zl, zp = 0.0, 6.0
    pcb = box_tris(Pos(0, 0.5, 0) * Box(13, 28, 1.6)); sc = box_tris(Cylinder(1.3, 1.6)); ring = box_tris(Cylinder(1.9, 0.5))
    # exploded stack along z: shell(top), gasket, PCB, back plate, screws (below)
    def mv(T, dx, dy, dz): T = T.copy(); T[:, :, 0] += dx; T[:, :, 1] += dy; T[:, :, 2] += dz; return T
    # the shell STL is centred on the origin with z-min = 0; line everything up in that frame (x/y approx)
    sb = shell.reshape(-1, 3).min(0); shell_c = shell.mean((0, 1))
    items = [(mv(lid, 0, 0, -26), "#ffc2e0"), (mv(pcb, shell_c[0], shell_c[1] - 0.5 + 0.5, 4.0 - 14), "#2b7a52"), (mv(ring, shell_c[0] + 2.6, shell_c[1] - 3.7 - 0.0, 5.7 - 6), "#222222"), (shell, PINK)]
    for (px, py) in gd.POSTS: items.append((mv(sc, shell_c[0] + px, shell_c[1] + py, -37), "#999999"))
    a3 = tris_3d(fig, [0.05, 0.05, 0.55, 0.78], items, el=18, az=-60)
    for (px, py) in gd.POSTS:
        a3.plot([shell_c[0] + px] * 2, [shell_c[1] + py] * 2, [-37, 1.0], color="#555555", lw=0.8, ls=(0, (3, 3)))
    badge(ax, 7.0, 3.3, "×4"); ax.text(7.45, 3.3, "M1.6 × 4 screws", fontsize=8.5, va="center"); warn(ax, 7.3, 1.9, "Dab of silicone around the cable slot for strain relief, after testing.", 4.2)
    return fig

# ============================================================================== 10. bench test
def step10():
    fig, ax = page(10, "Test on the bench BEFORE anything touches your head")
    line_rect(ax, 0.8, 3.4, 2.5, 1.5, fc="#e8edf3", r=0.1); ax.text(2.05, 4.15, "laptop\n(USB)", ha="center", fontsize=9, fontweight="bold")
    line_rect(ax, 5.0, 3.0, 2.8, 2.3, fc=YEL, r=0.2); ax.text(6.4, 4.15, "bee box\n(XIAO + battery)", ha="center", fontsize=9, fontweight="bold")
    wire(ax, [(3.3, 4.2), (5.0, 4.2)], "#444444", 4); ax.text(4.15, 4.35, "USB-C", ha="center", fontsize=8.5)
    line_rect(ax, 9.0, 3.0, 2.0, 1.2, fc=PINK, r=0.2); ax.text(10.0, 3.6, "dangle", ha="center", fontsize=9, fontweight="bold"); wire(ax, [(7.8, 3.6), (9.0, 3.6)], "#444444", 4)
    line_rect(ax, 8.6, 1.1, 2.8, 1.0, fc="#d0d0d0", r=0.2); ax.text(10.0, 1.6, "speaker or exciter\non a table", ha="center", va="center", fontsize=8.5); wire(ax, [(10.0, 3.0), (10.0, 2.1)], "#777777", 3)
    warn(ax, 1.0, 1.6, "Firmware is not written yet (see chapter 9). Until it is, only continuity and voltage tests are possible.", 6.2)
    return fig

# ============================================================================== 11. bee exploded
def step11():
    fig, ax = page(11, "Assemble the bee box")
    p = bee.HP(); b = bee.BP(); base, cover, info = bee.build(p, b)
    B = mesh("bee_base"); Cv = mesh("bee_cover")
    def mv(T, dx, dy, dz): T = T.copy(); T[:, :, 0] += dx; T[:, :, 1] += dy; T[:, :, 2] += dz; return T
    bb = B.reshape(-1, 3).min(0); bc = B.reshape(-1, 3).max(0); ctr = (bb + bc) / 2
    # STLs are centred on the origin in x/y and z-min = 0: x/y of the board/battery relative to the housing frame equal the housing frame minus the bbox centre offset
    off = np.array([-(bb[0] + bc[0]) / 2, -(bb[1] + bc[1]) / 2, 0]) * 0
    dz_expl = (30, 15, 0)
    brd = box_tris(Pos(0, 0, 0) * Box(56, 40, 1.6)); xiao = box_tris(Pos(2, -1, 0) * Box(21, 17.8, 4.0)); batt = box_tris(Pos(0, (info["bat_yt"] + info["bat_yb"]) / 2, 0) * Box(30, 35, 5.5))
    shift = np.array([-(bb[0] + bc[0]) / 2, -(bb[1] + bc[1]) / 2, 0])
    # bounding-box centre of the printed base is not the housing origin: re-add it
    ox, oy = (bb[0] + bc[0]) / 2, (bb[1] + bc[1]) / 2
    items = [(Cv, lambda t: np.where((t.mean(1)[:, 1] < -22 - 0)[:, None], np.array([[0.12, 0.12, 0.14]]), np.array([[1.0, 0.82, 0.25]]))), (mv(brd, 0, 0, 0), "#2b7a52")]
    items = [(mv(Cv, 0, 0, 38), lambda t: np.where((t.mean(1)[:, 1] < -22)[:, None], np.array([[0.12, 0.12, 0.14]]), np.array([[1.0, 0.82, 0.25]]))),
             (mv(xiao, 0, 0, 0), "#2c6bd1"), (B, "#c3c9d3")]
    zb, zt = info["z_bb"], info["z_bt"]
    items = [(mv(Cv, 0, 0, 62), lambda t: np.where((t.mean(1)[:, 1] < -22)[:, None], np.array([[0.12, 0.12, 0.14]]), np.array([[1.0, 0.82, 0.25]]))),
             (mv(xiao, 0, 0, zt + 3.6 + 38), "#2c6bd1"), (mv(brd, 0, 0, zb + 22), "#2b7a52"), (mv(batt, 0, 0, 2.0 + 2.75 + 8), "#f08a24"), (B, "#c3c9d3")]
    a3 = tris_3d(fig, [0.0, 0.02, 0.6, 0.82], items, el=28, az=-55)
    steps = ["1  Battery into the abdomen pocket, plug socket toward the thorax", "2  Carrier board on its 2 screw posts + 4 supports: 2 × M2 × 4", "3  Battery plug into the JST socket (check polarity!)", "4  Ear cables through the top slots, ribbons tied off inside", "5  Cover on: press the lip into the base until it clicks"]
    import textwrap
    yy = 5.7
    for st in steps:
        txt = textwrap.fill(st[3:], 38); ax.text(7.4, yy, st[0], fontsize=12, fontweight="bold", va="top"); ax.text(7.9, yy, txt, fontsize=8.5, va="top", linespacing=1.25); yy -= 0.215 * (txt.count("\n") + 1) + 0.3
    warn(ax, 7.9, 1.3, "Chain goes through the hole in the bee's head. Don't force the cover: check no wire is pinched.", 4.0)
    return fig

# ============================================================================== 12. clip sizing
def step12():
    fig, ax = page(12, "Fit the clip: it springs onto the glasses arm")
    for k, (t, col) in enumerate((("won't go on:\ndo not force it", ACC), ("right: firm pressure,\nthen it stays put", "#1a8f4d"), ("loose or twists:\nuse grip T, or add felt", "#e08a00"))):
        x = 1.6 + k * 3.6
        line_rect(ax, x - 0.55, 3.6, 1.1, 1.5, fc="#e9ecef", lw=2.5, r=0.1); line_rect(ax, x - 0.3, 3.9, 0.6, 0.9, fc="#9bb7e0", lw=1.8, r=0.05)
        ax.text(x, 3.3, t, ha="center", va="top", fontsize=9, color=col, fontweight="bold")
    ax.text(6.0, 5.75, "Press the clip onto the glasses arm at 127 mm from the hinge,\nfrom below (jaws facing up the arm)", ha="center", va="center", fontsize=9.5, fontweight="bold")
    big_arrow(ax, (2.0, 2.0), (4.4, 2.0), text="start with grip N", fs=9, off=(0, 0.25)); ax.text(5.0, 1.9, "then T if N is loose", fontsize=9)
    warn(ax, 1.0, 0.9, "Never force it: the stem is plastic.", 5.0)
    return fig

# ============================================================================== 13. arm + exciter
def step13():
    fig, ax = page(13, "Fit the spring arm, then the exciter")
    e = Image.open(os.path.join(FIG, "overview", "worn_ear_plain.png")); h = 5.2; image_at(ax, e, 0.4, 0.3, h * e.width / e.height, h)
    big_arrow(ax, (5.9, 4.6), (2.7, 2.7)); ax.text(6.0, 4.8, "exciter pad rests on the\nbone behind the ear", fontsize=9, fontweight="bold")
    warn(ax, 7.6, 2.4, "If the pad pushes hard: swap to the 2.4 mm arm. If it floats off the skin: use the 3.2 mm arm.", 4.0)
    return fig

# ============================================================================== 14. dangles + neck cables
def step14():
    fig, ax = page(14, "Hang the bears, run the cables, clip to the chain")
    e = Image.open(os.path.join(FIG, "overview", "worn_front_plain.png")); h = 5.3; wd = h * e.width / e.height; image_at(ax, e, 0.8, 0.3, wd, h)
    ax.text(5.3, 5.0, "bears hang from the earlobes", fontsize=9, fontweight="bold"); ax.text(5.3, 4.5, "cables follow the chain\nto the bee on the chest", fontsize=9, fontweight="bold", va="top")
    warn(ax, 5.8, 2.2, "Keep a loop of slack at the ear so head movements never pull on the PCB.", 5.6)
    return fig

# ============================================================================== 15. first power-up
def step15():
    fig, ax = page(15, "First power-up with the exciter against your head")
    for k, (t, col) in enumerate((("volume LOW", "#1a8f4d"), ("raise slowly", "#e08a00"), ("squeal / buzz?\n→ turn down,\nmove the exciter\naway from the mic", ACC))):
        x = 1.8 + k * 3.8; ax.add_patch(Circle((x, 4.8), 0.8, fc="white", ec=col, lw=4)); ax.text(x, 4.8, ["1", "2", "3"][k], ha="center", va="center", fontsize=28, color=col, fontweight="bold"); ax.text(x, 3.5, t, ha="center", va="top", fontsize=9.5, fontweight="bold", color=col)
    return fig

STEPS = [step00, step00b, step00c, step01, step02, step03, step04, step05, step06, step07, step08, step09, step10, step11, step12, step13, step14, step15]

if __name__ == "__main__":
    k = 0
    for f in STEPS:
        fig = f()
        if f in (step00b, step00c): name = f.__name__
        else: name = f"step{k:02d}"; k += 1
        for t in fig.axes[0].texts[(0 if f in (step00b, step00c, step03) else 2):]: t.set_fontsize(t.get_fontsize() * 1.2)          # the first two texts are the page number and the title (the headerless figures have none)
        save(fig, "assembly", name, dpi=150)

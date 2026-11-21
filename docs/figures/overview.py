"""Illustrated overview for the front of the manual: cover, why bone conduction, annotated worn views, parts at a glance, exploded views.
uv run python docs/figures/overview.py   (writes docs/build/figures/overview/*.png)"""
import os
from PIL import Image
from common import *
import assembly as A
import gummy_dangle as gd
import bee_box as bee
from matplotlib.patches import Circle, FancyBboxPatch, Polygon, Rectangle, Ellipse
from mpl_toolkits.mplot3d import proj3d
from build123d import Box, Pos, Cylinder, fillet, Axis

PINK, BLUE, YEL, INK = "#ff7ab8", "#4db3ff", "#ffd23f", "#1f2933"
PINKD, BLUED, YELD = "#d6277f", "#1c7fd1", "#a37f00"
SK = "#f2cdb8"

_scene = None
def scene():
    global _scene
    if _scene is None: _scene = A.build_scene()
    return _scene

# ------------------------------------------------------------------ annotation helpers
def overlay(fig):
    fig.canvas.draw(); W, H = fig.canvas.get_width_height()
    ov = fig.add_axes([0, 0, 1, 1], facecolor="none"); ov.set_xlim(0, W); ov.set_ylim(0, H); ov.axis("off"); return ov, W, H

def px(ax, p):
    x2, y2, _ = proj3d.proj_transform(p[0], p[1], p[2], ax.get_proj()); return ax.transData.transform((x2, y2))

def tag(ov, target, text_xy, text, color=INK, fs=10.5, ha="left"):
    ov.annotate(text, xy=target, xytext=text_xy, ha=ha, va="center", fontsize=fs, color=color, fontweight="bold", zorder=10,
                arrowprops=dict(arrowstyle="-|>", color=color, lw=1.6, shrinkA=2, shrinkB=1, mutation_scale=11),
                bbox=dict(boxstyle="round,pad=0.35", fc="white", ec=color, lw=1.3))

def mx(p): return np.array([2 * A.XM - p[0], p[1], p[2]])                  # mirror about the body midline

# ============================================================================== 1. worn, annotated
def worn_front(labels=True):
    fig = plt.figure(figsize=(6.4, 9.6), dpi=110, facecolor="white"); ax = fig.add_axes([0, 0, 1, 1], projection="3d")
    A.draw_scene(ax, scene(), 8, 90, (96, 96, 206), (A.XM, 0, -104), 0.55, ortho=True); ov, W, H = overlay(fig); an = A.ANCHORS
    if not labels: return fig
    tag(ov, px(ax, an["bear"]), (W * 0.02, H * 0.60), "earring: microphone\nand amplifier", PINKD)
    tag(ov, px(ax, mx(an["bear"])), (W * 0.98, H * 0.60), "right ear: same layout\n(blue earring)", BLUED, ha="right")
    tag(ov, px(ax, an["glasses_front"] + np.array([30, 0, 18])), (W * 0.98, H * 0.90), "glasses with clips\nand spring arms", "#6b4f2a", ha="right")
    tag(ov, px(ax, an["chain_top"] + np.array([8, 0, 22])), (W * 0.98, H * 0.44), "cables along the\nnecklace chain", "#6b7785", ha="right")
    tag(ov, px(ax, an["bee"] + np.array([0, 0, 22])), (W * 0.02, H * 0.20), "pendant: microcontroller\nand battery", YELD)
    return fig

def worn_ear(labels=True):
    fig = plt.figure(figsize=(7.2, 7.2), dpi=110, facecolor="white"); ax = fig.add_axes([0, 0, 1, 1], projection="3d"); xl = A.X0(0, 0) + 10
    A.draw_scene(ax, scene(), 0, 0, 62, (xl, -12, 8), 0.55, ortho=True); ov, W, H = overlay(fig); an = A.ANCHORS
    if not labels: return fig
    tag(ov, px(ax, an["clipA"]), (W * 0.52, H * 0.94), "clips on the glasses arm", "#444444")
    tag(ov, px(ax, an["arm"]), (W * 0.03, H * 0.76), "spring arm around the ear", "#444444")
    tag(ov, px(ax, an["exciter"]), (W * 0.03, H * 0.30), "exciter on the mastoid bone\nbehind the ear", "#c46a00")
    tag(ov, px(ax, an["mic"]), (W * 0.55, H * 0.12), "microphone opening", PINKD)
    return fig

# ============================================================================== 2. why bone conduction
def why_bone():
    fig, ax = plt.subplots(figsize=(9.5, 5.8)); ax.set_aspect("equal"); ax.axis("off"); ax.set_xlim(-150, 150); ax.set_ylim(-108, 100)
    ax.add_patch(Ellipse((0, 0), 124, 190, fc=SK, ec="#a77b62", lw=2.5, zorder=1))                                  # head, seen from the front (cross-section)
    ax.add_patch(Ellipse((0, 4), 100, 160, fc="#efe6d2", ec="#b9a77c", lw=2, zorder=2)); ax.text(0, -52, "skull bone", ha="center", color="#8a7a50", fontsize=12, style="italic", zorder=3)
    ax.add_patch(Ellipse((0, 28), 66, 44, fc="#e8b6c6", ec="#a96a80", lw=1.5, zorder=2, alpha=0.7)); ax.text(0, 28, "brain", ha="center", va="center", color="#8c4b63", fontsize=12, style="italic", zorder=3)
    for sx in (-1, 1):
        ax.add_patch(Ellipse((sx * 66, -4), 22, 44, fc=SK, ec="#a77b62", lw=2.5, zorder=4))                          # outer ear
        x0 = -58 if sx < 0 else 34
        ax.add_patch(Rectangle((x0, -9), 24, 4, fc="#e9a9a0", ec="#a77b62", lw=1, zorder=3))                          # ear canal
        ax.plot([sx * 34, sx * 34], [-14, -1], color="#6b7785", lw=3, zorder=5)                                      # eardrum
        th = np.linspace(0, 3.6 * np.pi, 80); r = 2 + 2.4 * th / np.pi
        ax.plot(sx * (22 + r * np.cos(th) * 0.9), -12 + r * np.sin(th) * 0.9, color="#c9a227", lw=2.4, zorder=5)    # cochlea = the inner ear
        ax.plot([sx * 22, sx * 8, 0], [-12, -2, 10], color="#e5c200", lw=2, zorder=5)                                # nerve to the brain
    ax.add_patch(Ellipse((-52, -7), 9, 8, fc="#7a4b21", ec="#4a2c12", lw=1.5, zorder=6))                             # wax
    ax.annotate("", xy=(-58, -7), xytext=(-112, -7), arrowprops=dict(arrowstyle="-|>", color=C["red"], lw=3.5), zorder=7)
    ax.text(-148, 14, "sound travelling\nthrough the air", ha="left", va="bottom", color=C["red"], fontsize=12.5, fontweight="bold")
    ax.plot([-55, -49], [-2, -12], color=C["red"], lw=5, zorder=8); ax.plot([-55, -49], [-12, -2], color=C["red"], lw=5, zorder=8)
    ax.text(-102, -44, "wax blocks the\near canal", ha="center", color="#7a4b21", fontsize=12.5, fontweight="bold")
    ax.add_patch(Rectangle((72, -46), 10, 22, fc="#f08a24", ec=INK, lw=2, zorder=6))                                  # the exciter, behind the ear
    for k in range(3): ax.add_patch(plt.matplotlib.patches.Arc((83, -35), 12 + 9 * k, 12 + 9 * k, theta1=-55, theta2=55, color="#f08a24", lw=2.2, zorder=6))
    ax.text(108, -66, "exciter\nbehind the ear", ha="center", color="#b0620f", fontsize=12.5, fontweight="bold")
    path = smooth([(70, -36), (54, -30), (42, -22), (30, -15)], closed=False)
    ax.plot(path[:, 0], path[:, 1], color=C["green"], lw=5, zorder=7, solid_capstyle="round"); ax.annotate("", xy=(25, -12), xytext=(32, -16), arrowprops=dict(arrowstyle="-|>", color=C["green"], lw=5), zorder=8)
    ax.text(104, 26, "vibration travels\nthrough the skull", ha="center", color=C["green"], fontsize=12.5, fontweight="bold")
    ax.text(0, -102, "The inner ear (spiral) is unaffected. Vibration of the skull reaches it without passing through the blocked canal.", ha="center", fontsize=10.5, color=C["mute"])
    return fig

# ============================================================================== 3. four steps
def four_steps():
    fig = plt.figure(figsize=(12, 3.6), facecolor="white"); titles = ["1  MICROPHONE", "2  PROCESSING", "3  EXCITER", "4  INNER EAR"]
    subs = ["The microphone in the\nearring picks up sound.", "The microcontroller in the\npendant filters, amplifies and\nlimits the signal.", "The exciter behind the ear\nconverts the signal into\nvibration.", "The vibration travels through\nthe skull to the inner ear."]
    for k in range(4):
        ax = fig.add_axes([0.01 + k * 0.25, 0.28, 0.22, 0.58], projection="3d")
        if k == 0:
            sh, lid, _ = gd.build(gd.GP(), "L"); draw_tris(ax, [(shape_tris(sh), PINK)], el=75, az=-90)
        elif k == 1:
            b_, c_, i_ = bee.build(bee.HP(), bee.BP()); T = [(shape_tris(b_), "#c3c9d3"), (shape_tris(c_), lambda t: np.where((t.mean(1)[:, 1] < -22)[:, None] & (t.mean(1)[:, 2] > 9.0)[:, None], np.array([[0.12, 0.12, 0.14]]), np.array([[1.0, 0.82, 0.25]])))]
            draw_tris(ax, T, el=70, az=-90)
        elif k == 2:
            draw_tris(ax, [(shape_tris(Box(13, 26.5, 5.75)), "#f08a24")], el=25, az=-50)
        else:
            ax.axis("off")
        ax.set_axis_off()
        fig.text(0.12 + k * 0.25, 0.93, titles[k], ha="center", fontsize=15, fontweight="bold", color=[PINKD, YELD, "#b0620f", C["green"]][k]); fig.text(0.12 + k * 0.25, 0.20, subs[k], ha="center", va="top", fontsize=10)
        if k < 3: fig.text(0.235 + k * 0.25, 0.55, "➜", ha="center", va="center", fontsize=24, color=C["mute"])
    ax = fig.axes[3]; ax.remove(); a2 = fig.add_axes([0.76, 0.28, 0.22, 0.58]); a2.axis("off"); a2.set_aspect("equal"); a2.set_xlim(-1, 1); a2.set_ylim(-1, 1)
    sp = smooth([(0, 0.9), (0.55, 0.7), (0.75, 0.1), (0.5, -0.6), (0, -0.85), (-0.5, -0.6), (-0.75, 0.1), (-0.55, 0.7)]); a2.fill(sp[:, 0], sp[:, 1], color=SK, ec="#a77b62", lw=2)
    th = np.linspace(0, 3.4 * np.pi, 80); r = 0.04 + 0.05 * th / np.pi; a2.plot(0.15 + r * np.cos(th) * 1.4, -0.05 + r * np.sin(th) * 1.4, color="#c9a227", lw=3); a2.text(0, 0.45, "♪ ♫", ha="center", fontsize=22, color=C["green"])
    return fig

# ============================================================================== 4. parts at a glance
def parts():
    import trimesh
    import textwrap
    fig = plt.figure(figsize=(12, 9.2), facecolor="white")
    cells = [("Glasses clips + spring arm", "Clip onto the glasses arm. The spring arm holds the exciter against the bone behind the ear. 3D-printed nylon, about 3 g."),
             ("Exciter", "Bone-conduction vibrator: Dayton DAEX-9-4SM, 13 × 26.5 × 5.75 mm, 2.3 g, 4 Ω."),
             ("Gummy-bear earrings", "Left (pink) and right (blue). Each contains a microphone and an amplifier. 32 × 46 mm, about 6 g."),
             ("Earring circuit board", "13 × 28 mm: digital microphone, amplifier and 3.3 V regulator. Assembled by JLCPCB."),
             ("Bee necklace box", "Contains the microcontroller module (Seeed XIAO nRF52840) and a 500 mAh battery. 105 × 116 mm including wings."),
             ("Necklace circuit board", "56 × 40 mm: connects the microcontroller, battery, switch and charger to the two 8-wire cables.")]
    for k, (t, d) in enumerate(cells):
        r, c = divmod(k, 3); x0 = 0.01 + c * 0.33; y0 = 0.545 - r * 0.49
        ax = fig.add_axes([x0, y0 + 0.13, 0.31, 0.30], projection="3d") if k not in (3, 5) else fig.add_axes([x0, y0 + 0.13, 0.31, 0.30])
        if k == 0:
            T = load_mesh(os.path.join(ROOT, "cad", "print", "clipB_arm2.8_L_B2.stl")); draw_tris(ax, [(T, "#b9c0cb")], el=15, az=-35)
        elif k == 1: draw_tris(ax, [(shape_tris(Box(13, 26.5, 5.75)), "#f08a24")], el=28, az=-45)
        elif k == 2:
            s1, _, _ = gd.build(gd.GP(), "L"); s2, _, _ = gd.build(gd.GP(), "R"); T1, T2 = shape_tris(s1), shape_tris(s2).copy(); T2[:, :, 0] += 36; draw_tris(ax, [(T1, PINK), (T2, BLUE)], el=70, az=-90)
        elif k == 4:
            b_, c_, i_ = bee.build(bee.HP(), bee.BP()); draw_tris(ax, [(shape_tris(b_), "#c3c9d3"), (shape_tris(c_), lambda t: np.where(((t.mean(1)[:, 1] < -22) & (t.mean(1)[:, 2] > 9.0))[:, None], np.array([[0.12, 0.12, 0.14]]), np.array([[1.0, 0.82, 0.25]])))], el=68, az=-90)
        else:
            ax.axis("off"); im = Image.open(os.path.join(FIG, "renders", "pcb_dangle_L_top.png" if k == 3 else "pcb_carrier_top.png")); ax.imshow(im); 
        fig.text(x0 + 0.155, y0 + 0.46, f"{k + 1}  {t}", ha="center", fontsize=15, fontweight="bold"); fig.text(x0 + 0.155, y0 + 0.12, textwrap.fill(d, 34), ha="center", va="top", fontsize=13)
    return fig

# ============================================================================== 5. exploded views
def _grp(fig, ax, items, el, az, ctr, span):
    draw_tris(ax, items, el=el, az=az); return ax

def explode_bear(labels=True):
    g = gd.GP(); shell, lid, info = gd.build(g, "L")
    off = dict(shell=34.0, ring=20.0, pcb=10.0, lid=0.0, screw=-14.0)
    def mv(T, dz): T = T.copy(); T[:, :, 2] += dz; return T
    pcb = shape_tris(Pos(0, g.pcb_y, g.lid_t + g.parts_gap + g.pcb_t / 2) * Box(g.pcb_w, g.pcb_l, g.pcb_t), 0.05)
    comp = [(Pos(0, 4.7, 3.55) * Box(3, 3, 0.9), "#33373d"), (Pos(2.6, -4.5, 3.55) * Box(2.7, 3.5, 1.0), "#7a808a"), (Pos(-3.7, -4.1, 3.55) * Box(1.6, 2.9, 1.0), "#33373d"), (Pos(0, -11.5, 3.6) * Box(7.5, 1.6, 0.8), "#9a8f7a")]
    ring = shape_tris(Pos(g.mic_dx, g.pcb_y + g.mic_dy, g.lid_t + g.parts_gap + g.pcb_t + 0.2) * (Cylinder(1.9, 0.4) - Cylinder(0.7, 0.4)), 0.05)
    screws = [(mv(shape_tris(Pos(px_, py_, 0.6) * Cylinder(1.1, 5.0), 0.05), off["screw"]), "#8f98a3") for px_, py_ in gd.POSTS]
    items = [(mv(shape_tris(shell), off["shell"]), PINK), (mv(ring, off["ring"]), "#222222"), (mv(pcb, off["pcb"]), "#2b7a52")] + [(mv(shape_tris(b), off["pcb"]), c) for b, c in comp] + [(mv(shape_tris(lid), off["lid"]), "#ffb3d6")] + screws
    fig = plt.figure(figsize=(6.6, 6.4), dpi=110, facecolor="white"); ax = fig.add_axes([0, 0, 1, 1], projection="3d")
    draw_tris(ax, items, el=24, az=-62); ax.set_proj_type("ortho")
    P = np.vstack([t for t, _ in items]).reshape(-1, 3); lo, hi = P.min(0), P.max(0); ctr = (lo + hi) / 2; ax.set_xlim(ctr[0] - 23, ctr[0] + 23); ax.set_ylim(ctr[1] - 27, ctr[1] + 27); ax.set_zlim(ctr[2] - 34, ctr[2] + 34); ax.set_box_aspect((46, 54, 68))
    for (px_, py_) in [(g.mic_dx, g.pcb_y + g.mic_dy)] + list(gd.POSTS):                         # dotted alignment lines between the layers
        ax.plot([px_, px_], [py_, py_], [off["screw"], off["shell"]], color="#9aa5b1", lw=0.9, ls=(0, (3, 3)), zorder=0)
    ov, W, H = overlay(fig)
    if not labels: return fig
    tag(ov, px(ax, (0, 12, 7.6 + off["shell"] - 2)), (W * 0.70, H * 0.93), "shell (microphone\nopening at the front)", PINKD)
    tag(ov, px(ax, (g.mic_dx, g.pcb_y + g.mic_dy, 5.9 + off["ring"])), (W * 0.62, H * 0.66), "sealing ring around the\nmicrophone opening", "#444444")
    tag(ov, px(ax, (4, 8, 4.8 + off["pcb"])), (W * 0.64, H * 0.50), "circuit board: microphone,\namplifier, regulator", C["green"])
    tag(ov, px(ax, (0, -4, 0.6 + off["lid"])), (W * 0.62, H * 0.30), "back plate\n(engraved L or R)", "#c24a8c")
    tag(ov, px(ax, (gd.POSTS[3][0], gd.POSTS[3][1], 0.6 + off["screw"])), (W * 0.60, H * 0.10), "four screws", "#555555")
    return fig

def explode_bee(labels=True):
    p = bee.HP(); b = bee.BP(); base, cover, info = bee.build(p, b)
    off = dict(cover=84.0, xiao=56.0, board=30.0, batt=14.0)
    def mv(T, dz): T = T.copy(); T[:, :, 2] += dz; return T
    rb = lambda w, h, t, r: fillet(Box(w, h, t).edges().filter_by(Axis.Z), r)
    board = shape_tris(Pos(0, 0, (info["z_bb"] + info["z_bt"]) / 2) * rb(56, 40, 1.6, 9.0), 0.05)
    xiao = shape_tris(Pos(2, -1, info["z_bt"] + 2.5 + 0.6) * Box(21, 17.8, 1.2), 0.05); usb = shape_tris(Pos(2 + 10.5 - 3.6, -1, info["z_bt"] + 2.5 + 1.2 + 1.65) * Box(7.2, 8.9, 3.3), 0.05)
    sw = shape_tris(Pos(-8.5, 17.5, info["z_bt"] + 2.0) * Box(8.9, 4.0, 3.6), 0.05); jst = shape_tris(Pos(-17, -11, info["z_bt"] + 3.9) * Box(6, 6, 7.8), 0.05)
    batt = shape_tris(Pos(0, (info["bat_yt"] + info["bat_yb"]) / 2, 2.1 + p.bat_t / 2) * Box(p.bat_x, p.bat_y, p.bat_t), 0.05)
    def cover_col(t):
        c = t.mean(1); out = np.tile(np.array([1.0, 0.82, 0.25]), (len(t), 1)); ab = (c[:, 1] < -22) & (c[:, 2] > info["wing_top"] - 0.3); hot = np.zeros(len(c), bool)
        for yc in b.ridge_y: hot |= abs(c[:, 1] - yc) < 2.6
        out[ab & ~hot] = (0.12, 0.12, 0.14); return out
    def base_col(t):
        c = t.mean(1); out = np.tile(np.array([0.78, 0.8, 0.85]), (len(t), 1)); out[np.abs(c[:, 0]) > 31.5] = (0.93, 0.95, 0.99); out[(c[:, 1] > 22.5) & (np.abs(c[:, 0]) < 13)] = (0.14, 0.14, 0.16); out[c[:, 1] < info["wy0"] + 1.0] = (0.14, 0.14, 0.16); return out
    items = [(mv(shape_tris(cover), off["cover"]), cover_col), (mv(xiao, off["xiao"]), "#2c6bd1"), (mv(usb, off["xiao"]), "#c0c0c0"), (mv(board, off["board"]), "#2b7a52"), (mv(sw, off["board"]), "#6b4f2a"), (mv(jst, off["board"]), "#e9e9e9"),
             (mv(batt, off["batt"]), "#f08a24"), (shape_tris(base), base_col)]
    fig = plt.figure(figsize=(6.6, 7.2), dpi=110, facecolor="white"); ax = fig.add_axes([0, 0, 1, 1], projection="3d")
    draw_tris(ax, items, el=26, az=-52); ax.set_proj_type("ortho")
    P = np.vstack([t for t, _ in items]).reshape(-1, 3); lo, hi = P.min(0), P.max(0); ctr = (lo + hi) / 2; ax.set_xlim(ctr[0] - 56, ctr[0] + 56); ax.set_ylim(ctr[1] - 62, ctr[1] + 62); ax.set_zlim(ctr[2] - 60, ctr[2] + 60); ax.set_box_aspect((112, 124, 120))
    for (px_, py_) in ((-20, 12), (20, 12), (0, -36), (24, -12)):
        ax.plot([px_, px_], [py_, py_], [0, off["cover"] + 3], color="#9aa5b1", lw=0.9, ls=(0, (3, 3)), zorder=0)
    ov, W, H = overlay(fig)
    if not labels: return fig
    tag(ov, px(ax, (20, 0, info["out_top"] + off["cover"])), (W * 0.58, H * 0.95), "cover (painted)", YELD)
    tag(ov, px(ax, (2, -1, info["z_bt"] + 4 + off["xiao"])), (W * 0.64, H * 0.74), "microcontroller module\n(XIAO nRF52840)", "#1c4fa8")
    tag(ov, px(ax, (-20, 12, info["z_bt"] + off["board"])), (W * 0.00, H * 0.68), "carrier circuit board", C["green"], ha="left")
    tag(ov, px(ax, (0, (info["bat_yt"] + info["bat_yb"]) / 2, 5.5 + off["batt"])), (W * 0.56, H * 0.35), "battery (in the abdomen)", "#b0620f")
    tag(ov, px(ax, (0, 31, 5)), (W * 0.02, H * 0.90), "base; the chain passes\nthrough the head", "#555555")
    return fig

# ============================================================================== 6. cover
def cover():
    W, Hh = 8.27, 11.69; fig = plt.figure(figsize=(W, Hh), facecolor="white"); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, Hh); ax.axis("off")
    ax.add_patch(Rectangle((0, 9.55), W, Hh - 9.55, fc="#fff3fa", ec="none")); [ax.add_patch(Rectangle((k * W / 3, 9.5), W / 3, 0.06, fc=c, ec="none")) for k, c in enumerate((PINK, YEL, BLUE))]
    ax.text(0.5, 10.95, "Open-ear hearing aids", fontsize=34, fontweight="bold", va="center", color=INK)
    ax.text(0.52, 10.3, "Bone-conduction hearing aids for conductive hearing loss:\nglasses clips, earrings and a necklace pendant", fontsize=13, va="center", color=C["mute"], linespacing=1.4)
    ax.text(0.52, 9.78, "datasheet  ·  user manual  ·  project log", fontsize=11, va="center", color=INK, style="italic")
    def put(path, x, y, w, h, cap=None):
        im = Image.open(path).convert("RGB")
        from PIL import ImageChops
        bb = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).getbbox()                   # trim the white margins so the picture fills its box
        if bb: im = im.crop((max(bb[0] - 6, 0), max(bb[1] - 6, 0), min(bb[2] + 6, im.width), min(bb[3] + 6, im.height)))
        s_ = min(w / im.width, h / im.height); iw, ih = im.width * s_, im.height * s_
        ax.imshow(im, extent=(x + (w - iw) / 2, x + (w + iw) / 2, y + (h - ih) / 2, y + (h + ih) / 2), aspect="auto", zorder=2)
        if cap: ax.text(x + w / 2, y - 0.08, cap, ha="center", va="top", fontsize=8.5, color=C["mute"])
    o = lambda n: os.path.join(FIG, "overview", n)
    put(o("worn_front_plain.png"), 0.35, 3.75, 3.8, 5.6)
    put(o("worn_ear_plain.png"), 4.35, 6.35, 3.5, 3.0)
    put(o("explode_bee_plain.png"), 4.35, 3.45, 3.5, 2.85)
    ys, hs = 0.95, 2.25
    put(os.path.join(FIG, "renders", "pcb_dangle_L_top.png"), 0.4, ys, 1.2, hs, "earring board, left"); put(os.path.join(FIG, "renders", "pcb_dangle_R_top.png"), 1.75, ys, 1.2, hs, "earring board, right")
    put(os.path.join(FIG, "renders", "pcb_carrier_top.png"), 3.1, ys + 0.3, 2.4, 1.6, "necklace board"); put(o("explode_bear_plain.png"), 5.7, ys, 2.2, 2.25)
    ax.text(0.4, 0.38, "Generated from code: CAD, circuit boards, drawings and simulations.", fontsize=8.5, color=C["mute"]); ax.text(W - 0.4, 0.38, "morgan", fontsize=12, color=INK, ha="right", fontweight="bold")
    return fig

if __name__ == "__main__":
    for name, f, kw in (("worn_front", worn_front, dict(dpi=170)), ("worn_ear", worn_ear, dict(dpi=170)), ("why_bone", why_bone, dict(dpi=200)), ("four_steps", four_steps, dict(dpi=180)), ("parts", parts, dict(dpi=170)),
                        ("explode_bear", explode_bear, dict(dpi=170)), ("explode_bee", explode_bee, dict(dpi=170))):
        save(f(), "overview", name, shrink=1.0, **kw)
    for name, f in (("worn_front_plain", worn_front), ("worn_ear_plain", worn_ear), ("explode_bear_plain", explode_bear), ("explode_bee_plain", explode_bee)):
        save(f(labels=False), "overview", name, shrink=1.0, dpi=170)
    save(cover(), "overview", "cover", shrink=1.0, dpi=200, bbox_inches=None, pad_inches=0)

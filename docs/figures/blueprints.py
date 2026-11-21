"""Technical drawings (light drafting paper, shaded parts, coloured cut faces) of every printed part and both PCBs, with dimensions taken from the CAD parameters.
Projections come from the real build123d solids (hidden-line removal); dimensions are computed, not typed.
Run from docs/figures:  uv run python blueprints.py"""
import os, sys
import numpy as np
from common import *
from build123d import Box, Pos, Plane, Vector
import gummy_dangle as gd
import bee_box as bee
from params import G, H, P

BG, LN, DM, HID = "#fbfaf6", "#1f2933", "#0b5cad", "#8a97a8"
CUT = "#f4a259"

# ------------------------------------------------------------------ projection helpers
def basis(origin, up):
    d = -np.asarray(origin, float); d /= np.linalg.norm(d); up = np.asarray(up, float)
    right = np.cross(d, up); right /= np.linalg.norm(right); u = np.cross(right, d); return right, u
def p2(p, origin, up):
    r, u = basis(origin, up); p = np.asarray(p, float); return np.array([p @ r, p @ u])

def sample(e):
    n = int(min(120, max(2, e.length / 0.4))); return np.array([(q.X, q.Y) for q in (e @ t for t in np.linspace(0, 1, n))])

def shaded(ax, fills, origin, up, cut=None):
    """painter's-algorithm shaded fill of tessellated solids, orthographic along the view direction. fills = [(shape, colour)], cut = (axis, value, colour)"""
    r, u = basis(origin, up); d = -np.asarray(origin, float); d /= np.linalg.norm(d)
    light = -d * 0.8 + u * 0.45 - r * 0.35; light /= np.linalg.norm(light)
    polys, cols, depth = [], [], []
    for shape, col in fills:
        tr = shape_tris(shape, 0.12); n = np.cross(tr[:, 1] - tr[:, 0], tr[:, 2] - tr[:, 0]); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
        keep = (n @ d) < 0.05; tr, n = tr[keep], n[keep]
        base = np.tile(np.array(matplotlib.colors.to_rgb(col)), (len(tr), 1)); sh = (0.55 + 0.45 * np.clip(n @ light, 0, 1))[:, None]; c = np.clip(base * sh, 0, 1)
        if cut is not None:
            ax_i, val, ccol = cut; on = np.all(np.abs(tr[:, :, ax_i] - val) < 0.02, axis=1); c[on] = np.array(matplotlib.colors.to_rgb(ccol))
        polys.append(np.stack([tr @ r, tr @ u], -1)); cols.append(c); depth.append(tr.mean(1) @ d)
    polys = np.vstack(polys); cols = np.vstack(cols); depth = np.concatenate(depth); order = np.argsort(-depth)
    from matplotlib.collections import PolyCollection
    ax.add_collection(PolyCollection(polys[order], facecolors=cols[order], edgecolors=cols[order], linewidths=0.25, zorder=0.5))

def draw_view(ax, shape, origin, up, hidden=True, lw=0.9, color="#c9ced6", fills=None, cut=None):
    vis, hid = shape.project_to_viewport(origin, viewport_up=up, look_at=(0, 0, 0))
    shaded(ax, fills or [(shape, color)], origin, up, cut)
    allp = []
    if hidden:
        for e in hid: pts = sample(e); ax.plot(pts[:, 0], pts[:, 1], color=HID, lw=0.45, ls=(0, (4, 2)), alpha=0.8, zorder=1)
    for e in vis: pts = sample(e); ax.plot(pts[:, 0], pts[:, 1], color=LN, lw=lw, solid_capstyle="round", zorder=2); allp.append(pts)
    P_ = np.vstack(allp); return P_.min(0), P_.max(0)

def dim(ax, p, q, off=4.0, text=None, fs=7.5, gap=0.8, ext=1.2, tol=None):
    p = np.asarray(p, float); q = np.asarray(q, float); v = q - p; L = np.hypot(*v); u = v / L; n = np.array([-u[1], u[0]])
    if off < 0: n = -n; off = -off
    a, b = p + n * off, q + n * off
    for s_, e_ in ((p, a), (q, b)): ax.plot([s_[0] + n[0] * gap, e_[0] + n[0] * ext], [s_[1] + n[1] * gap, e_[1] + n[1] * ext], color=DM, lw=0.6, zorder=3)
    ax.annotate("", xy=b, xytext=a, arrowprops=dict(arrowstyle="<|-|>", color=DM, lw=0.9, shrinkA=0, shrinkB=0, mutation_scale=7), zorder=4)
    ang = np.degrees(np.arctan2(u[1], u[0])); ang = ang - 180 if ang > 90 else ang + 180 if ang < -90 else ang
    mid = (a + b) / 2 + n * 0.25
    ax.text(mid[0], mid[1], text or f"{L:.1f}", color=DM, fontsize=fs, rotation=ang, ha="center", va="bottom", rotation_mode="anchor", zorder=5,
            bbox=dict(fc=BG, ec="none", pad=0.8, alpha=0.9))

def callout(ax, xy, txy, text, fs=7.2, ha="left"):
    ax.annotate(text, xy=xy, xytext=txy, color=DM, fontsize=fs, ha=ha, va="center", arrowprops=dict(arrowstyle="-|>", color=DM, lw=0.7, mutation_scale=6), zorder=5, bbox=dict(fc=BG, ec="none", pad=1))

def circle_dim(ax, c, d, txt, off=(6, 6), fs=7.2):
    t = np.linspace(0, 2 * np.pi, 60); ax.plot(c[0] + d / 2 * np.cos(t), c[1] + d / 2 * np.sin(t), color=DM, lw=0.5, zorder=3)
    callout(ax, (c[0] + d / 2 * 0.7, c[1] + d / 2 * 0.7), (c[0] + off[0], c[1] + off[1]), txt, fs)

def sheet(nrows, ncols, size, title, part, material="PA12 (MJF nylon), plain grey", notes=(), wr=None):
    fig = plt.figure(figsize=size, facecolor=BG); axs = []
    gs = fig.add_gridspec(nrows, ncols, left=0.03, right=0.97, top=0.87, bottom=0.14, wspace=0.12, hspace=0.18, width_ratios=wr)
    for i in range(nrows):
        for j in range(ncols):
            ax = fig.add_subplot(gs[i, j], facecolor=BG); ax.set_aspect("equal"); ax.axis("off"); axs.append(ax)
    fig.patch.set_facecolor(BG)
    fig.text(0.03, 0.955, title, color=LN, fontsize=15, fontweight="bold", va="center", family="DejaVu Sans")
    fig.add_artist(plt.Rectangle((0.015, 0.012), 0.97, 0.09, transform=fig.transFigure, fc="#eef1f5", ec=LN, lw=1.0))
    cols = [("PART", part), ("MATERIAL", material), ("UNITS", "millimetres"), ("SCALE", "see bar"), ("DRAWN BY", "build123d + matplotlib"), ("SIGNED", "morgan")]
    x = 0.025; W_in = size[0]
    for a_, b_ in cols:                                         # lay the title-block cells out by character count so they never overlap
        fig.text(x, 0.085, a_, color=HID, fontsize=7, va="center"); fig.text(x, 0.045, b_, color=LN, fontsize=8.5, va="center", fontweight="bold")
        x += (max(len(a_) * 0.9 * 7, len(b_) * 1.05 * 8.5) / 72.0) / W_in + 0.02
    if notes: fig.text(0.03, 0.905, "   ·   ".join(notes), color=HID, fontsize=8, ha="left", va="center")
    return fig, axs


def layer_stack(ax, xr, layers, fs=7.5):
    """name every z-layer (with its thickness) in an evenly spaced column to the right of a section, with leader lines"""
    n = len(layers); z_lo = layers[0][0]; z_hi = layers[-1][1]; span = (z_hi - z_lo)
    for k, (z0, z1, tx) in enumerate(layers):
        ty = z_lo + span * (k + 0.5) / n * 1.9 - span * 0.45
        txt = tx if any(ch.isdigit() for ch in tx) else f"{tx}  {z1 - z0:.1f}"
        ax.plot([xr + 0.5, xr + 9.5], [(z0 + z1) / 2, ty], color=DM, lw=0.5); ax.text(xr + 10, ty, txt, color=LN, fontsize=fs, va="center")

def label(ax, text, xy=None):
    ax.text(0.5, 1.0, text, transform=ax.transAxes, color=LN, fontsize=9, ha="center", va="bottom", fontweight="bold")

def scalebar(ax, x, y, length=10):
    y = min(ax.get_ylim()) + 1.0; x = min(ax.get_xlim()) + 1.5           # always in the bottom-left corner of the view, clear of the dimensions
    ax.plot([x, x + length], [y, y], color=LN, lw=2); ax.text(x + length / 2, y + 1.0, f"{length} mm", color=LN, fontsize=7.5, ha="center", va="bottom")

def pad_limits(ax, lo, hi, m=17):
    ax.set_xlim(lo[0] - m, hi[0] + m); ax.set_ylim(lo[1] - m, hi[1] + m)

# ============================================================================== 1. gummy bear
def bear():
    g = gd.GP(); shell, lid, info = gd.build(g, "L")
    fig, axs = sheet(1, 3, (17, 8), "GUMMY-BEAR DANGLE — shell (left ear)", "bear_shell_L.stl", notes=("front wall 1.2 mm, side wall 1.2 mm", "4 × M1.6 self-tapping posts (pilot Ø1.3)", "mic port Ø1.4 in the belly button"), wr=(1.0, 1.15, 1.35))
    ax = axs[0]; o, up = (0, 0, 300), (0, 1, 0)
    lo, hi = draw_view(ax, shell, o, up, color="#ff9fcd"); pad_limits(ax, lo, hi, 13); label(ax, "FRONT")
    dim(ax, (lo[0], lo[1]), (hi[0], lo[1]), -7); dim(ax, (hi[0], lo[1]), (hi[0], hi[1]), -7)
    mx, my = g.mic_dx, g.pcb_y + g.mic_dy
    circle_dim(ax, (mx, my), 1.4, "mic port Ø1.4\n2.6 right, 3.7 below centre", (9, -9))
    pcb = np.array([[-g.pcb_w / 2, g.pcb_y - g.pcb_l / 2], [g.pcb_w / 2, g.pcb_y - g.pcb_l / 2], [g.pcb_w / 2, g.pcb_y + g.pcb_l / 2], [-g.pcb_w / 2, g.pcb_y + g.pcb_l / 2], [-g.pcb_w / 2, g.pcb_y - g.pcb_l / 2]])
    ax.plot(pcb[:, 0], pcb[:, 1], color=C["green"], lw=0.9, ls="--", zorder=2); callout(ax, (g.pcb_w / 2, g.pcb_y + 9), (14, g.pcb_y + 13), "PCB 13 × 28\n(dashed)")
    circle_dim(ax, (0, 23.0), g.loop_hole, f"hook loop hole Ø{g.loop_hole}", (-12, 6)); dim(ax, (-14, 0), (-14, 23.0), -3, "23.0")
    ax.plot([-14.5, 0], [0, 0], color=DM, lw=0.4, ls=":"); scalebar(ax, lo[0], lo[1] - 12)
    ax = axs[1]; o, up = (300, 0, 0), (0, 0, 1)
    lo, hi = draw_view(ax, shell, o, up, color="#ff9fcd"); pad_limits(ax, lo, hi, 13); label(ax, "SIDE")
    dim(ax, (lo[0], hi[1]), (lo[0], lo[1]), 7, f"{g.height:.1f}  thick"); dim(ax, (lo[0], lo[1]), (hi[0], lo[1]), -6, f"{hi[0] - lo[0]:.1f}")
    callout(ax, (lo[0] + 1, g.height - 0.6), (hi[0] - 18, hi[1] + 6), "front wall 1.2 over\nPCB ceiling gap 0.4")
    ax = axs[2]; half = shell & Pos(0, 100 + my, 0) * Box(300, 200, 300)        # keep y >= mic height, look from -Y at the cut face
    lo, hi = draw_view(ax, half, (0, -300, 0), (0, 0, 1), color="#ff9fcd", cut=(1, my, CUT)); pad_limits(ax, lo, hi, 13); label(ax, f"SECTION A–A  (cut through the mic port, y = {my:.1f})")
    # internal layer stack along z (x of the view = world x, y of the view = z)
    zs = [(0, g.lid_t, "back plate 1.2"), (g.lid_t, g.lid_t + g.parts_gap, "parts gap 2.8"), (g.lid_t + g.parts_gap, g.lid_t + g.parts_gap + g.pcb_t, "PCB 1.6"), (g.lid_t + g.parts_gap + g.pcb_t, g.lid_t + g.parts_gap + g.pcb_t + g.ceil_gap, "gap 0.4"), (g.lid_t + g.parts_gap + g.pcb_t + g.ceil_gap, g.height, "front wall")]
    layer_stack(ax, hi[0] + 2, zs)
    scalebar(ax, lo[0], lo[1] - 10)
    return fig

# ============================================================================== 2. back plate
def backplate():
    g = gd.GP(); shell, lid, info = gd.build(g, "L")
    fig, axs = sheet(1, 2, (13, 8), "GUMMY-BEAR DANGLE — back plate (left ear)", "bear_backplate_L.stl", notes=("engraved L 0.45 mm deep", "screw holes Ø1.8, head recess Ø3.2", "2 edge pillars clamp the PCB"))
    ax = axs[0]; lo, hi = draw_view(ax, lid, (0, 0, -300), (0, 1, 0), color="#ffc2e0"); pad_limits(ax, lo, hi, 12); label(ax, "BACK  (looking at the plate from behind)")
    dim(ax, (lo[0], lo[1]), (hi[0], lo[1]), -6); dim(ax, (hi[0], lo[1]), (hi[0], hi[1]), -6)
    for (px, py) in gd.POSTS: circle_dim(ax, (-px, py), 1.8, "Ø1.8", (-5 if px < 0 else 5, 5 if py > 0 else -5))
    scalebar(ax, lo[0], lo[1] - 11)
    ax = axs[1]; lo, hi = draw_view(ax, lid, (300, 0, 0), (0, 0, 1), color="#ffc2e0"); pad_limits(ax, lo, hi, 12); label(ax, "SIDE")
    dim(ax, (lo[0], lo[1]), (lo[0], hi[1]), 6, f"{hi[1] - lo[1]:.1f}"); dim(ax, (lo[0], lo[1]), (hi[0], lo[1]), -6, f"{hi[0] - lo[0]:.1f}")
    callout(ax, (0, g.lid_t + 1.4), (hi[0] - 6, hi[1] + 5), "PCB pillar 2.8 high\n(on the board's bare edge strips)")
    return fig

# ============================================================================== 3. bee box
def beebox():
    p = bee.HP(); b = bee.BP(); base, cover, info = bee.build(p, b)
    full = base + cover
    fig, axs = sheet(2, 2, (15, 12), "BEE NECKLACE BOX — base + cover", "bee_base.stl + bee_cover.stl", notes=("thorax holds the 56 × 40 carrier PCB (r9 corners)", "abdomen holds the 30 × 35 × 5.5 LiPo", "chain passes through the head hole"))
    ax = axs[0]; lo, hi = draw_view(ax, full, (0, 0, 400), (0, 1, 0), fills=[(base, "#c3c9d3"), (cover, "#ffd23f")]); pad_limits(ax, lo, hi, 16); label(ax, "FRONT (cover side)")
    dim(ax, (lo[0], lo[1]), (hi[0], lo[1]), -8, f"{hi[0] - lo[0]:.0f}  (incl. wings)"); dim(ax, (hi[0], lo[1]), (hi[0], hi[1]), -8, f"{hi[1] - lo[1]:.0f}")
    hx = p.out_w / 2; hy = p.out_h / 2
    dim(ax, (-hx, -hy), (hx, -hy), 5.2, f"{p.out_w:.0f}", fs=7); dim(ax, (-hx, -hy), (-hx, hy), 5.2, f"{p.out_h:.0f}", fs=7)
    circle_dim(ax, (0, b.chain_hole_y), b.chain_hole, f"chain hole Ø{b.chain_hole}\n(axis along X)", (-34, 8))
    callout(ax, (b.abd_w / 2, info["wy0"] + 12), (hi[0] - 18, info["wy0"] + 8), f"abdomen {b.abd_w:.0f} wide")
    scalebar(ax, lo[0], lo[1] - 16, 20)
    ax = axs[1]; lo, hi = draw_view(ax, base, (0, 0, 400), (0, 1, 0), color="#c3c9d3"); pad_limits(ax, lo, hi, 16); label(ax, "BASE with cover removed (hidden detail dashed)")
    bx, by = 28, 20
    ax.plot([-bx, bx, bx, -bx, -bx], [-by, -by, by, by, -by], color=C["green"], lw=0.9, ls="--"); callout(ax, (bx, by), (bx + 8, by + 12), "carrier PCB 56 × 40\n(green, dashed)")
    ax.plot([-15, 15, 15, -15, -15], [info["bat_yb"], info["bat_yb"], info["bat_yt"], info["bat_yt"], info["bat_yb"]], color=C["orange"], lw=0.9, ls="--"); callout(ax, (15, info["bat_yb"] + 5), (28, info["bat_yb"] - 4), "LiPo 30 × 35 (orange)")
    for sx in (-1, 1): circle_dim(ax, (sx * p.mount_hole_x, 0), 1.8, "M2 pilot", (sx * 8, -8), fs=6.5)
    ax = axs[2]; lo, hi = draw_view(ax, full, (400, 0, 0), (0, 1, 0), fills=[(base, "#c3c9d3"), (cover, "#ffd23f")]); pad_limits(ax, lo, hi, 14); label(ax, "SIDE  (view from the right)")
    zlo, zhi = lo[0], hi[0]
    dim(ax, (zlo, lo[1]), (zhi, lo[1]), -6, f"{zhi - zlo:.1f}  thick"); callout(ax, (zlo + 0.3, info["wy0"] + 3), (zlo + 16, info["wy0"] + 12), f"abdomen {info['wing_top']:.1f}")
    callout(ax, (zhi - 0.3, 0), (zhi + 8, 8), f"thorax {info['out_top']:.1f}")
    ax = axs[3]; half = full & Pos(0, 0, 0) * Box(400, 400, 400).moved(Pos(0, 0, 0)) if False else None
    cut = full & (Pos(0, 100 - 3, 0) * Box(400, 200, 400))            # keep y >= -3 ... section through the thorax centre line
    sec = full & (Pos(0, 100 + 3.0, 0) * Box(400, 200, 400)); lo, hi = draw_view(ax, sec, (0, -400, 0), (0, 0, 1), fills=[(base & (Pos(0, 103.0, 0) * Box(400, 200, 400)), "#c3c9d3"), (cover & (Pos(0, 103.0, 0) * Box(400, 200, 400)), "#ffd23f")], cut=(1, 3.0, CUT)); pad_limits(ax, lo, hi, 14); label(ax, "SECTION B–B (through the thorax, y = 3)")
    zs = [(0, 1.6, "floor"), (1.6, info["z_bb"], "stand-off"), (info["z_bb"], info["z_bt"], "PCB"), (info["z_bt"], info["out_top"] - 1.6, "components"), (info["out_top"] - 1.6, info["out_top"], "cover")]
    layer_stack(ax, hi[0] + 2, zs)
    scalebar(ax, lo[0], lo[1] - 8, 20)
    return fig

# ============================================================================== 4. clips and spring arm
def clip_section(ax, T, h, wall=1.6, clr=0.25, length=14, label_txt="", x0=0, y0=0):
    """cross-section of a C-clip around a stem of thickness T and height h (slot on the underside)"""
    ci, co = clr, wall + clr; W = T + 2 * co; Hh = h + 2 * co
    ax.add_patch(plt.Rectangle((x0 - W / 2, y0 - Hh / 2), W, Hh, fc="#c9d1dc", ec=LN, lw=1.2, zorder=0.6))
    ax.add_patch(plt.Rectangle((x0 - (T + 2 * ci) / 2, y0 - (h + 2 * ci) / 2), T + 2 * ci, h + 2 * ci, fc=BG, ec=LN, lw=1.2, zorder=0.7))
    sw = T - 0.6; ax.add_patch(plt.Rectangle((x0 - sw / 2, y0 - Hh / 2 - 0.05), sw, co + 0.1, fc=BG, ec=LN, lw=1.0, zorder=3))
    ax.add_patch(plt.Rectangle((x0 - T / 2, y0 - h / 2), T, h, fc="#b9d2f5", ec=HID, lw=0.8, zorder=1))
    dim(ax, (x0 - W / 2, y0 + Hh / 2), (x0 + W / 2, y0 + Hh / 2), 3.2, f"{W:.1f}"); dim(ax, (x0 + W / 2, y0 - Hh / 2), (x0 + W / 2, y0 + Hh / 2), 3.2, f"{Hh:.1f}")
    dim(ax, (x0 - T / 2, y0 - Hh / 2), (x0 + T / 2, y0 - Hh / 2), -3.6, f"cavity {T + 2 * ci:.2f}  (stem {T})", fs=6.5)
    dim(ax, (x0 - W / 2, y0 - h / 2 - ci), (x0 - W / 2, y0 + h / 2 + ci), -3.4, f"cavity {h + 2 * ci:.2f}", fs=6.5); callout(ax, (x0 + sw / 2, y0 - Hh / 2), (x0 + 6, y0 - Hh / 2 - 4.5), f"slot {sw:.1f}")
    ax.text(x0, y0 + Hh / 2 + 7.5, label_txt, color=LN, fontsize=8, ha="center", fontweight="bold")

def clips():
    from clips import clip_geom, arm_geom, g_for, P3, s
    fig, axs = sheet(2, 3, (16, 11), "STEM CLIPS AND SPRING ARM (left ear shown)", "clipA_*, clipB_arm*", notes=("right ear is the mirror image", "fit matrix: stem thickness A–D 3.34 / 3.54 / 3.74 / 3.94, height 1–3 = −0.4 / 0 / +0.4", "wall 1.6, clearance 0.25, length 14", "arm 2.8 mm (2.4 / 3.2 variants), height 7.0"))
    ax = axs[0]; clip_section(ax, 3.6, 4.6, label_txt="CLIP A  section (station 100 mm, fit B2)"); ax.set_xlim(-14, 14); ax.set_ylim(-14, 14)
    ax = axs[1]; clip_section(ax, 3.6, 8.9, label_txt="CLIP B  section (station 127 mm, fit B2)"); ax.set_xlim(-14, 14); ax.set_ylim(-16, 14)
    ax = axs[2]
    st = np.linspace(0, 145, 300); hp = np.array([ __import__("glasses").hfun(x, G) for x in st ])
    ax.fill_between(st, -hp / 2, hp / 2, color="#b9d2f5", ec=LN); ax.set_xlim(-8, 155); ax.set_ylim(-19, 14)
    for stn, nm in ((100, "A"), (127, "B")): ax.add_patch(plt.Rectangle((stn - 7, -5.5 if nm == "A" else -7), 14, 11 if nm == "A" else 14, fc="none", ec=C["pink"], lw=1.6)); ax.text(stn, -10.2, f"clip {nm}", color=C["pink"], fontsize=8, ha="center", va="top")
    dim(ax, (0, -8), (145, -8), -6.5, "temple length 145 (hinge → tip)"); ax.text(0, 8.5, f"hinge h={G.temple_h_hinge}", color=LN, fontsize=8); ax.text(95, 12.3, f"h={G.temple_h_straight_end} at 105", color=LN, fontsize=8, ha="center"); ax.text(152, 8.3, f"paddle h={G.temple_h_paddle}", color=LN, fontsize=8, ha="right")
    label(ax, "STEM PROFILE (height along the temple, calipers)")
    # arm + plate in three views
    cb, g, ib, sb = clip_geom(127.0, 3.6, 0.0); part = cb + arm_geom(g, ib, 2.8)
    c = part.bounding_box().center(); part = part.moved(Pos(-c.X, -c.Y, -c.Z)) if hasattr(part, "moved") else part.move(__import__("build123d").Location((-c.X, -c.Y, -c.Z)))
    for ax, (o, up, nm) in zip(axs[3:], (((300, 0, 0), (0, 0, 1), "ARM + PLATE  from the outside (+X)"), ((0, 0, 300), (0, 1, 0), "from above (+Z)"), ((0, -300, 0), (0, 0, 1), "from behind (−Y)"))):
        lo, hi = draw_view(ax, part, o, up, color="#bcc6d6"); pad_limits(ax, lo, hi, 11); label(ax, nm)
        dim(ax, (lo[0], lo[1]), (hi[0], lo[1]), -6); dim(ax, (hi[0], lo[1]), (hi[0], hi[1]), -6); scalebar(ax, lo[0], lo[1] - 9, 10)
    return fig

# ============================================================================== 5. PCBs
FR4, PADC, SILK = "#2b7a52", "#e8c34a", "#f5fff8"

def outline(W, Hh, r):
    a = np.linspace(0, np.pi / 2, 14)
    o = np.vstack([np.c_[W - r + r * np.sin(a), r - r * np.cos(a)], np.c_[W - r + r * np.cos(a), Hh - r + r * np.sin(a)], np.c_[r - r * np.sin(a), Hh - r + r * np.cos(a)], np.c_[r - r * np.cos(a), r - r * np.sin(a)]])
    return np.vstack([o, o[0]])

def pad(ax, x, y, d=1.5, txt=None, ty=None, tcol=SILK, fs=6.3):
    ax.add_patch(plt.Circle((x, y), d / 2, fc=PADC, ec="#b8932a", lw=0.8, zorder=3)); ax.add_patch(plt.Circle((x, y), 0.35, fc=FR4, ec="none", zorder=4))
    if txt: ax.text(x, y + (ty if ty is not None else 1.4), txt, color=tcol, fontsize=fs, ha="center", va="center", zorder=5)

def part(ax, x, y, w, h, name, fc="#33373d"):
    ax.add_patch(plt.Rectangle((x - w / 2, y - h / 2), w, h, fc=fc, ec="#0e1114", lw=0.9, zorder=3)); ax.text(x, y, name, color="white", fontsize=6.6, ha="center", va="center", zorder=5)

def dangle_pcb():
    W, Hh = 13.0, 28.0
    fig, axs = sheet(1, 2, (13, 10), "DANGLE PCB — mechanical drawing", "dangle_L / dangle_R gerbers", material="FR-4 1.6 mm (JLCPCB)", notes=("13 × 28 mm, corner r 1.0", "all SMD parts on the top side", "bottom = ground plane + big L/R letter + signature"))
    out = outline(W, Hh, 1.0)
    ax = axs[0]; ax.invert_yaxis(); ax.fill(out[:, 0], out[:, 1], color=FR4, zorder=0); ax.plot(out[:, 0], out[:, 1], color=LN, lw=1.4, zorder=2)
    part(ax, 6.5, 9.8, 3.0, 3.0, "U1\namp"); part(ax, 3.9, 19.0, 2.7, 3.5, "U2\nmic", "#7a808a"); part(ax, 10.2, 18.6, 1.6, 2.9, "U3", "#33373d")
    for x, y, w, h, n in ((3.5, 5.4, 3.2, 1.6, "R"), (9.5, 5.4, 3.2, 1.6, "R"), (10.6, 10.6, 2.0, 1.25, "C1"), (10.3, 8.4, 1.6, 0.8, "C2"), (5.6, 13.6, 0.8, 1.6, ""), (8.2, 13.6, 0.8, 1.6, ""), (8.0, 20.8, 1.6, 0.8, ""), (11.9, 16.3, 0.8, 1.6, ""), (1.7, 11.0, 0.8, 1.6, "")):
        part(ax, x, y, w, h, n, "#9a8f7a")
    for nm, x, y in (("1", 1.9, 23.8), ("2", 4.6, 23.8), ("3", 7.3, 23.8), ("4", 10.0, 23.8), ("5", 3.25, 25.9), ("6", 5.95, 25.9), ("7", 8.65, 25.9), ("8", 11.3, 25.9)): pad(ax, x, y, 1.5, nm, ty=(-1.3 if y < 25 else 1.3))
    pad(ax, 9.5, 1.4, 1.5, "EXC+", ty=-2.4, tcol=LN, fs=6.8); pad(ax, 3.5, 1.4, 1.5, "EXC−", ty=-2.4, tcol=LN, fs=6.8)
    ax.add_patch(plt.Circle((3.9, 19.0), 0.25, fc=BG, ec=LN, lw=1, zorder=6)); callout(ax, (3.9, 19.0), (-2.0, 13.0), "mic port NPTH Ø0.5\n(3.9 from left,\n19.0 from top)", ha="right")
    callout(ax, (6.5, 9.8), (21.0, 7.0), "U1 MAX98357A\nTQFN-16 3 × 3", ha="left"); callout(ax, (10.2, 18.6), (21.0, 20.0), "U3 XC6206 LDO\nSOT-23", ha="left")
    dim(ax, (0, 0), (W, 0), -3.2, "13.0"); dim(ax, (W, 0), (W, Hh), -3.2, "28.0"); dim(ax, (1.9, Hh), (10.0, Hh), 3.0, "cable pad pitch 2.7 (rows staggered 1.35)", fs=6.5); dim(ax, (3.5, 0), (9.5, 0), -6.4, "exciter pads 6.0 apart", fs=6.5)
    ax.set_xlim(-16, W + 22); ax.set_ylim(Hh + 7, -10); label(ax, "TOP (component side)")
    ax = axs[1]; ax.invert_yaxis(); ax.fill(out[:, 0], out[:, 1], color=FR4, zorder=0); ax.plot(out[:, 0], out[:, 1], color=LN, lw=1.4, zorder=2)
    ax.add_patch(plt.Rectangle((0.3, 0.3), W - 0.6, Hh - 0.6, fc="#e8c34a", alpha=0.25, zorder=1)); ax.text(W / 2, 7.0, "L", color=SILK, fontsize=52, ha="center", va="center", fontweight="bold", zorder=3)
    ax.text(W / 2, 21.0, "morgan", color=SILK, fontsize=9, ha="center", zorder=3); ax.text(W / 2, 23.6, "LEFT EAR", color=SILK, fontsize=7, ha="center", zorder=3); ax.text(W / 2, 15.6, "1 LRCLK  2 DIN\n3 VBAT  4 DATA\n5 BCLK  6 GND\n7 CLK  8 GND", color=SILK, fontsize=5.5, ha="center", va="center", zorder=3)
    ax.set_xlim(-16, W + 22); ax.set_ylim(Hh + 7, -10); label(ax, "BOTTOM (faces the bear's front wall;\nground plane, shown mirrored as printed)")
    callout(ax, (W, 12), (W + 1.5, 12), "gold = copper\nground pour", ha="left")
    return fig

def carrier_pcb():
    W, Hh, r = 56.0, 40.0, 9.0
    fig, axs = sheet(1, 1, (15, 10.8), "CARRIER PCB — mechanical drawing (component side)", "carrier gerbers", material="FR-4 1.6 mm (JLCPCB)", notes=("56 × 40 mm, corner r 9.0", "2 × M2 mounting holes Ø2.2", "XIAO pins soldered into 2 × 7 holes (15.24 mm apart)"))
    ax = axs[0]; ax.invert_yaxis(); out = outline(W, Hh, r); ax.fill(out[:, 0], out[:, 1], color=FR4, zorder=0); ax.plot(out[:, 0], out[:, 1], color=LN, lw=1.6, zorder=2)
    X0, Y0 = 30.0, 21.0
    ax.add_patch(plt.Rectangle((X0 - 10.5, Y0 - 8.9), 21, 17.8, fc="#2f6fd0", alpha=0.55, ec="#143d82", lw=1.0, zorder=2)); ax.text(X0, Y0 + 0.5, "XIAO nRF52840\n21 × 17.8 (sits 2.5 mm above)", color="white", fontsize=8, ha="center", va="center", zorder=5)
    for (x, y, d, nm) in ((2.6, 20.0, 2.2, "MH1"), (53.4, 20.0, 2.2, "MH2")):
        ax.add_patch(plt.Circle((x, y), 2.2, fc=PADC, ec="#b8932a", zorder=3)); ax.add_patch(plt.Circle((x, y), d / 2, fc=BG, ec=LN, lw=1, zorder=4)); ax.text(x, y + 3.4, nm, color=SILK, fontsize=7, ha="center", zorder=5)
    for k in range(7): pad(ax, X0 + 7.62, Y0 - 7.62 + 0 + (k - 3) * 0 * 0, 0.01) if False else None
    for k in range(7):
        pad(ax, X0 + (k - 3) * 2.54, Y0 - 7.62, 1.7); pad(ax, X0 + (k - 3) * 2.54, Y0 + 7.62, 1.7)
    for x, y, nm in ((16.6, 19.0, "B+"), (16.6, 21.0, "B−")): pad(ax, x, y, 1.5); ax.text(x - 1.4, y, nm, color=SILK, fontsize=7, ha="right", va="center", zorder=5)
    for side, x0 in (("L", 3.9), ("R", 42.65)):
        for n in range(8):
            row_a = n < 4; i = n % 4; x = x0 + 2.7 * i + (0 if row_a else 1.35); y = 3.8 if row_a else 6.3
            pad(ax, x, y, 1.5, str(n + 1), ty=(-1.5 if row_a else 1.5))
    part(ax, 11.0, 31.0, 5.0, 8.0, "JST-PH\nbattery", "#e9e9e9"); ax.texts[-1].set_color("#1f2933")
    part(ax, 19.5, 3.8, 9.0, 4.4, "SW1", "#6b4f2a"); part(ax, 15.5, 35.0, 3.0, 2.6, "Q1", "#33373d"); part(ax, 34.0, 35.0, 5.2, 2.4, "F1 PTC", "#c9c27a"); ax.texts[-1].set_color("#1f2933")
    part(ax, 41.0, 35.0, 2.2, 1.4, "", "#9a8f7a"); part(ax, 50.0, 36.0, 1.0, 1.7, "", "#d64545"); part(ax, 16.0, 14.5, 1.8, 9.5, "", "#33373d"); part(ax, 44.0, 14.5, 1.8, 9.5, "", "#33373d")
    dim(ax, (0, 0), (W, 0), -5.0, "56.0"); dim(ax, (W, 0), (W, Hh), -5.5, "40.0"); dim(ax, (2.6, Hh), (53.4, Hh), 4.5, "M2 mounting holes 50.8 apart (centres 20 from the top edge)", fs=7)
    callout(ax, (W - r + 1.0, 1.5), (W + 1.0, -3.5), "corner r 9.0")
    ax.set_xlim(-8, W + 10); ax.set_ylim(Hh + 8, -9); label(ax, "TOP (component side). The XIAO's USB-C points to the right edge")
    return fig

if __name__ == "__main__":
    for name, f in (("bear_shell", bear), ("bear_backplate", backplate), ("bee_box", beebox), ("clips_arm", clips), ("dangle_pcb", dangle_pcb), ("carrier_pcb", carrier_pcb)):
        try: save(f(), "blueprints", name, dpi=150, facecolor=BG)
        except Exception as e: print("FAILED", name, repr(e)); raise

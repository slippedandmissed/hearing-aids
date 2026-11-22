"""Renders of the finished print files (cad/print/*.stl), the KiCad 3D renders of the PCBs and the CAD previews, collected into docs/build/figures/renders.
uv run python docs/figures/renders.py"""
import os, shutil
from PIL import Image, ImageChops
from common import *

PRINT = os.path.join(ROOT, "cad", "print")
NYLON, PINK, BLUE, YEL = "#59616e", "#ff8ec8", "#52b6ff", "#ffd23f"      # NYLON = dyed-black MJF PA12 (clips, arms, bee base); the bears and the bee cover are natural grey under their paint

def mesh(name):
    p = os.path.join(PRINT, name + ".stl")
    return load_mesh(p)

def one(ax, items, el=28, az=-55, edge=False):
    draw_tris(ax, items, el=el, az=az, edge=edge)

def grid(rows, cols, size, **kw):
    fig = plt.figure(figsize=size, facecolor="white"); axs = [fig.add_subplot(rows, cols, i + 1, projection="3d") for i in range(rows * cols)]
    fig.subplots_adjust(left=0.01, right=0.99, top=0.93, bottom=0.01, wspace=0.0, hspace=0.12); return fig, axs

# ============================================================================== clips
def clips_matrix():
    """the spring-jaw clip end of clip + arm (grip N), cropped to the clip, in four views"""
    T = mesh("clip_arm2.8_L_N"); c = T.mean(1); keep = c[:, 2] > T[:, :, 2].max() - 15.0           # triangles within 15 mm of the clip end (the top of the printed part)
    clip = T[keep]
    fig, axs = grid(1, 4, (13, 3.8))
    for ax, (el, az, ttl) in zip(axs, ((-60, -90, "from below: the V-shaped mouth"), (25, -40, "3/4 view"), (5, -90, "side"), (65, -90, "from above: engraved ID"))):
        one(ax, [(clip, NYLON)], el=el, az=az); ax.set_title(ttl, fontsize=9)
    fig.subplots_adjust(top=0.84); fig.suptitle("Spring-jaw clip end of clip + arm, left ear, grip N (grip T looks the same; its jaws are 0.3 mm closer together)", fontsize=9.5, y=0.97)
    return fig

def arms():
    fig = plt.figure(figsize=(13, 6.2), facecolor="white")
    ax = fig.add_subplot(1, 3, 1, projection="3d"); one(ax, [(mesh("clip_arm2.8_L_N"), NYLON)], el=18, az=-35); ax.set_title("clip + spring arm + exciter plate (3/4 view)", fontsize=9)
    ax = fig.add_subplot(1, 3, 2, projection="3d"); one(ax, [(mesh("clip_arm2.8_L_N"), NYLON)], el=5, az=-90); ax.set_title("seen from the side", fontsize=9)
    ax = fig.add_subplot(1, 3, 3, projection="3d")
    tr = []
    for k, name in enumerate(("clip_arm2.4_L_N", "clip_arm2.8_L_N", "clip_arm3.2_L_N")):
        T = mesh(name).copy(); T[:, :, 1] += k * 40; tr.append((T, (NYLON, "#677080", "#7a8494")[k]))
    one(ax, tr, el=12, az=-90); ax.set_title("arm thickness variants 2.4 / 2.8 / 3.2 mm", fontsize=9)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.92, bottom=0.01, wspace=0.0)
    return fig

def engraving():
    fig = plt.figure(figsize=(12, 4.2), facecolor="white")
    for k, (nm, ttl) in enumerate((("clip_arm2.8_L_N", "clip + arm (left, grip N)"), ("clip_arm2.8_R_N", "clip + arm (right, grip N): mirrored part, ID still reads correctly"), ("clip_arm2.8_R_T", "clip + arm (right, grip T)"))):
        ax = fig.add_subplot(1, 3, k + 1, projection="3d"); one(ax, [(mesh(nm), NYLON)], el=55, az=(-60 if k == 0 else -120 if k == 1 else -110), edge=False); ax.set_title(ttl, fontsize=8.5)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.9, bottom=0.0, wspace=0.0)
    return fig

# ============================================================================== bears and bee
def bears():
    fig = plt.figure(figsize=(14, 6.4), facecolor="white")
    specs = [("bear_shell_L", PINK, 80, -90, "left shell, front"), ("bear_shell_R", BLUE, 80, -90, "right shell, front"), ("bear_shell_L", PINK, -75, -90, "left shell, inside (posts, ring, pegs)"), ("bear_backplate_L", PINK, -80, -90, "left back plate (engraved L)"), ("bear_backplate_R", BLUE, -80, -90, "right back plate (engraved R)"),
             ("bear_shell_L", PINK, 35, -55, "3/4 view")]
    for k, (n, c, el, az, t) in enumerate(specs):
        ax = fig.add_subplot(2, 3, k + 1, projection="3d"); T = mesh(n)
        if "plate" in n: one(ax, [(T, c)], el=el, az=az)
        else: one(ax, [(T, c)], el=el, az=az)
        ax.set_title(t, fontsize=9)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.93, bottom=0.01, wspace=0.0, hspace=0.1)
    return fig

def bee():
    fig = plt.figure(figsize=(14, 5.6), facecolor="white")
    base, cover = mesh("bee_base"), mesh("bee_cover")
    def cover_col(t):
        c = t.mean(1); out = np.tile(np.array(matplotlib.colors.to_rgb(YEL)), (len(t), 1)); ab = (c[:, 1] < -22) & (c[:, 2] > 9.0)
        # black stripe valleys: abdomen top surface between the raised yellow bumps
        out[ab & (np.abs(((c[:, 1] + 29.0) / 9.5 + 0.5) % 1.0 - 0.5) > 0.3)] = (0.12, 0.12, 0.14); return out
    def base_col(t):
        c = t.mean(1); out = np.tile(np.array(matplotlib.colors.to_rgb("#3a404a")), (len(t), 1)); out[np.abs(c[:, 0]) > 31.5] = (0.88, 0.92, 0.98); return out      # base dyed black: head, stinger and antennae need no paint; only the wings are painted silver
    for k, (it, el, az, t) in enumerate((([(base, base_col), (cover, cover_col)], 75, -90, "assembled, front"), ([(base, base_col)], 75, -90, "base (cover off)"), ([(cover, cover_col)], -75, -90, "cover, seen from inside"), ([(base, base_col), (cover, cover_col)], 25, -60, "3/4 view"))):
        ax = fig.add_subplot(1, 4, k + 1, projection="3d"); one(ax, it, el=el, az=az); ax.set_title(t, fontsize=9)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.9, bottom=0.01, wspace=0.0)
    return fig

def overview():
    names = [("clip_arm2.8_L_N", NYLON, "clip + arm, left"), ("clip_arm2.8_R_N", NYLON, "clip + arm, right"), ("bear_shell_L", PINK, "bear shell L"), ("bear_backplate_L", PINK, "back plate L"), ("bear_shell_R", BLUE, "bear shell R"), ("bear_backplate_R", BLUE, "back plate R"), ("bee_base", NYLON, "bee base"), ("bee_cover", YEL, "bee cover")]
    fig = plt.figure(figsize=(14, 7), facecolor="white")
    for k, (n, c, t) in enumerate(names):
        ax = fig.add_subplot(2, 4, k + 1, projection="3d"); T = mesh(n); lo, hi = T.reshape(-1, 3).min(0), T.reshape(-1, 3).max(0)
        one(ax, [(T, c)], el=40 if "bear" not in n else 55, az=-55); ax.set_title(f"{t}\n{(hi - lo)[0]:.0f} × {(hi - lo)[1]:.0f} × {(hi - lo)[2]:.0f} mm", fontsize=8.5)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.9, bottom=0.01, wspace=0.0, hspace=0.18)
    return fig

# ============================================================================== PCB renders + CAD previews
def trim(src, dst, pad=12):
    im = Image.open(src).convert("RGBA"); bg = Image.new("RGBA", im.size, (255, 255, 255, 255)); comp = Image.alpha_composite(bg, im).convert("RGB")
    diff = ImageChops.difference(comp, Image.new("RGB", comp.size, (255, 255, 255))); bbox = diff.getbbox()
    if bbox: comp = comp.crop((max(bbox[0] - pad, 0), max(bbox[1] - pad, 0), min(bbox[2] + pad, comp.width), min(bbox[3] + pad, comp.height)))
    os.makedirs(os.path.dirname(dst), exist_ok=True); comp.save(dst); print("wrote", os.path.relpath(dst, ROOT))

def collect():
    for b in ("dangle_L", "dangle_R", "carrier"):
        for side in ("top", "bottom"):
            src = os.path.join(ROOT, "pcb", "renders", f"{b}_{side}.png")
            if os.path.exists(src): trim(src, out_path("renders", f"pcb_{b}_{side}.png"))
    for n in ("preview_assembly", "preview_bee", "preview_gummy", "glasses_check"):
        src = os.path.join(ROOT, "cad", "out", n + ".png")
        if os.path.exists(src): trim(src, out_path("renders", n + ".png"), 6)

if __name__ == "__main__":
    for name, f in (("print_clip", clips_matrix), ("print_arms", arms), ("print_engraving", engraving), ("print_bears", bears), ("print_bee", bee), ("print_overview", overview)):
        save(f(), "renders", name, dpi=160)
    collect()

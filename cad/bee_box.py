"""Cartoon bumblebee necklace box v1.
thorax = main body (carrier PCB, flat 1-layer cosmetic wings splayed up-and-out on the back plane), abdomen = battery wing with raised yellow bumps and black stripe valleys,
stinger nub, ball head (solid, belongs to the base) with the chain hole through it, antennae, eye wells. Internals as necklace_housing v0.2.
Frame: X right, Y up, Z from the back (0) to the front (cover side). Carrier PCB needs >= ~9 mm corner radius."""
from dataclasses import dataclass
import math
from build123d import *

@dataclass(frozen=True)
class HP:
    """Parameters of the electronics space inside the necklace box (carrier PCB + battery + XIAO). Heights marked ASSUMED must be checked against the real parts."""
    wall: float = 1.6
    out_w: float = 62.0; out_h: float = 46.0; out_r: float = 5.0
    board_t: float = 1.6
    standoff: float = 2.0            # board bottom above the base plate (trim all pin tails to <= 1 mm)
    bat_x: float = 30.0; bat_y: float = 35.0; bat_t: float = 5.5       # ASSUMED 503035-size 500 mAh LiPo, lying with its 35 mm side vertical
    bat_clear: float = 1.0
    wing_w: float = 40.0             # outer width of the battery wing
    male_plastic: float = 2.5        # ASSUMED plastic spacer of the XIAO's pin headers (rests on the board)
    xiao_t: float = 1.2; usb_h: float = 3.3
    jst_h: float = 7.8               # ASSUMED JST-PH side-entry height above the board
    plug_h: float = 6.8; plug_w: float = 11.6                            # USB-C plug opening (ASSUMED)
    mount_hole_x: float = 25.4       # board mounting holes at (+-25.4, 0)
    post_pilot: float = 2.6          # SCREW: M2 x 4 mm pan head, cross recess, A2 stainless (head ~4.0 wide x 1.6 tall, ISO 7045 maxima, NOT measured). Pilot from the post top down to z = 1.0: the screw (board top at z = 5.2) ends at z = 1.2, inside the base wall, leaving 1.0 mm under the tip. (M2 x 8 would poke 2.8 mm out of the back.)
    lug_hole: float = 6.2            # chain bail hole (match your chain's clasp end)
    switch_x: float = -8.5           # slide switch, top wall (board x=19.5)

@dataclass(frozen=True)
class BP:
    thorax_r: float = 14.0
    head_r: float = 11.0; head_cy: float = 33.0; head_rz: float = 6.5
    chain_hole: float = 6.2; chain_hole_y: float = 36.5
    abd_w: float = 44.0; abd_r: float = 9.0
    ridge_y: tuple = (-29.0, -38.5, -48.0); ridge_R: float = 3.75; ridge_h: float = 1.2     # yellow bumps; the valleys between them are the black stripes
    dome: tuple = (24.0, 17.0, 3.5)
    wing_len: float = 33.0; wing_w: float = 16.0; wing_t: float = 1.2; wing_ang: float = 42.0; wing_root: tuple = (27.0, 12.0)

def rr(x0, x1, y0, y1, r): return Pos((x0 + x1) / 2, (y0 + y1) / 2) * RectangleRounded(x1 - x0, y1 - y0, r)

def build(p: HP = HP(), b: BP = BP()):
    w = p.wall; W, H = p.out_w, p.out_h; hx, hy = W / 2, H / 2
    z_bb = w + p.standoff; z_bt = z_bb + p.board_t
    xiao_bot = z_bt + p.male_plastic; xiao_top = xiao_bot + p.xiao_t + p.usb_h
    usb_c = xiao_top - p.usb_h / 2; plug_top = usb_c + p.plug_h / 2
    in_top = max(z_bt + p.jst_h + 0.3, xiao_top + 0.6, plug_top + 0.3); out_top = in_top + w
    wing_in_h = w + p.bat_t + p.bat_clear + 0.4; wing_top = wing_in_h + w
    bat_yt = -hy + 1.1; bat_yb = bat_yt - p.bat_y
    wy1 = -hy + 6.0; wy0 = bat_yb - 0.4 - w; wx = b.abd_w / 2
    th = rr(-hx, hx, -hy, hy, b.thorax_r); ab = rr(-wx, wx, wy0, wy1, b.abd_r)
    outer = extrude(th, amount=out_top) + extrude(ab, amount=wing_top)
    cav = Pos(0, 0, w) * (extrude(offset(th, amount=-w), amount=in_top - w) + extrude(offset(ab, amount=-w), amount=wing_in_h - w))
    shell = outer - cav
    # ---- head (solid, base), stinger (solid, base), antennae
    head = Pos(0, b.head_cy, b.head_rz) * scale(Sphere(1.0), by=(b.head_r, b.head_r, b.head_rz))
    stinger = Pos(0, wy0 + 1.4, wing_top / 2) * Rot(90, 0, 0) * (Pos(0, 0, 4.5) * Cone(4.5, 1.0, 9.0))      # 9 mm cone pointing down (-y), base inside the abdomen wall
    stinger = stinger + Pos(0, wy0 + 1.6, wing_top / 2) * Rot(90, 0, 0) * Cylinder(4.5, 1.6)
    ant = None
    for sx in (-1, 1):
        a = Pos(sx * 5.0, 40.5, b.head_rz) * Rot(0, 0, -sx * 25) * (Pos(0, 4.0, 0) * (Rot(90, 0, 0) * Cylinder(1.2, 8.0)) + Pos(0, 8.0, 0) * Sphere(2.1))
        ant = a if ant is None else ant + a
    head = head + ant
    head = head - Pos(0, b.chain_hole_y, b.head_rz) * (Rot(0, 90, 0) * Cylinder(b.chain_hole / 2, 40.0))
    for sx in (-1, 1): head = head - Pos(sx * 4.2, b.head_cy + 1.5, 2 * b.head_rz - 1.1) * Cylinder(1.6, 2.0)     # eye wells
    zs = z_bt - 0.4; ztop = out_top + 3.0
    lowslab = Pos(0, 0, zs / 2) * Box(W + 20, 400, zs); upslab = Pos(0, 0, zs + (ztop - zs) / 2) * Box(W + 20, 400, ztop - zs)
    base = (shell & lowslab) + head + stinger
    cover = ((shell & upslab) - head) - stinger
    # ---- wings: flat 1-layer plates on the back plane (fused with the base floor), raised veins on the front for paint
    for sx in (-1, 1):
        ang = sx * b.wing_ang; ux, uy = math.cos(math.radians(b.wing_ang)) * sx, math.sin(math.radians(b.wing_ang))
        cx, cy = sx * b.wing_root[0] + ux * b.wing_len / 2, b.wing_root[1] + uy * b.wing_len / 2
        plate = extrude(Ellipse(b.wing_len / 2, b.wing_w / 2), amount=b.wing_t)
        for off in (-3.2, 0.0, 3.2): plate = plate + Pos(0, off, b.wing_t - 0.01) * Box(b.wing_len * 0.75, 0.8, 0.45)
        base = base + Pos(cx, cy, 0) * Rot(0, 0, ang) * plate
    # ---- internal posts (as v0.2)
    for sx in (-1, 1):
        post = Pos(sx * p.mount_hole_x, 0, (w + z_bb) / 2) * Cylinder(2.75, z_bb - w) - Pos(sx * p.mount_hole_x, 0, z_bb - 3.0) * Cylinder(0.9, 6.0)
        base = base + post
        base = base - Pos(sx * p.mount_hole_x, 0, z_bb - p.post_pilot / 2 + 0.05) * Cylinder(0.9, p.post_pilot + 0.1)      # pilot continues into the base wall
        for sy in (-1, 1): base = base + Pos(sx * 24.0, sy * 16.0, (w + z_bb) / 2) * Cylinder(2.0, z_bb - w)
        for sy in (bat_yt, bat_yb): base = base + Pos(sx * (p.bat_x / 2 + 0.6), sy - (0.6 if sy == bat_yb else -0.6), (w + 0.4 + p.bat_t + w) / 2) * Cylinder(0.8, p.bat_t + 0.4)
    lip = extrude(offset(th, amount=-w - 0.25), amount=3.0) - extrude(offset(th, amount=-w - 1.25), amount=3.0)
    flange = extrude(offset(th, amount=-w + 0.4), amount=1.0) - extrude(offset(th, amount=-w - 1.25), amount=1.0)   # joins the lip to the cover wall (overlaps it by 0.4 mm)
    cover = cover + Pos(0, 0, zs - 3.0) * lip + Pos(0, 0, zs) * flange
    # ---- openings
    for sx in (-1, 1): cover = cover - Pos(sx * 20.0, hy - w / 2, zs + 2.4) * Box(8.0, w + 2.0, 4.8)
    cover = cover - Pos(-8.5, hy - w / 2, z_bt + 1.8) * Box(7.4, w + 2.0, 3.8)
    cover = cover - Pos(22.0, -16.0, (z_bt + out_top) / 2) * Cylinder(1.0, out_top - z_bt + 2.0)
    cover = cover - Pos(hx - w / 2, -1.0, usb_c) * Box(w + 2.0, p.plug_w, p.plug_h)
    # ---- bumps: thorax dome + abdomen yellow ridges (cover); black stripes are the valleys between
    dx, dy, dz = b.dome
    dome = Pos(0, 0, out_top - 2.5) * scale(Sphere(1.0), by=(dx, dy, dz)) & Pos(0, 0, out_top + 5) * Box(W, H, 10)
    cover = cover + dome
    abd_prism = extrude(offset(ab, amount=-w + 0.6), amount=wing_top + 3)
    for yc in b.ridge_y:
        rid = Pos(0, yc, wing_top - b.ridge_R + b.ridge_h) * (Rot(0, 90, 0) * Cylinder(b.ridge_R, b.abd_w)) & abd_prism & (Pos(0, yc, wing_top + 1.0) * Box(b.abd_w + 4, 20, 2.6))
        cover = cover + rid
    info = dict(cav=cav, out_top=out_top, wing_top=wing_top, wy0=wy0, bat_yt=bat_yt, bat_yb=bat_yb, z_bb=z_bb, z_bt=z_bt, zs=zs, chain_local=(0.0, b.chain_hole_y, b.head_rz))
    return base, cover, info

if __name__ == "__main__":
    import os; os.makedirs("out", exist_ok=True)
    p = HP(); base, cover, i = build(p)
    bbx = (base + cover).bounding_box()
    bat = Pos(0, (i["bat_yt"] + i["bat_yb"]) / 2, 1.6 + 0.4 + p.bat_t / 2) * Box(p.bat_x, p.bat_y, p.bat_t)
    print(f"bee box v1: {bbx.size.X:.0f} wide (incl. wings) x {bbx.size.Y:.0f} tall x {bbx.size.Z:.1f} thick; aspect {bbx.size.Y / bbx.size.X:.2f}:1; battery outside cavity {(bat - i['cav']).volume:.1f} mm3; valid {base.is_valid} {cover.is_valid}")

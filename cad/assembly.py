"""Full assembly preview: woman's head/neck/torso (MakeHuman CC0 base) + glasses stem + clips + electronics pods + spring arms
+ exciters, BOTH ears, cables down the neck, necklace chain and box.  python assembly.py -> out/preview_assembly.png
World: X = out of the LEFT ear, Y = nose, Z = up, origin ~ left ear canal opening (mm)."""
import os, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection
from build123d import Box, Pos, Location, Plane, Vector
from params import P, H, G
from earhook import catmull, exciter_dims
from glasses import glasses_stem, clip_flex, exciter_arm, FLEX
import gummy_dangle as gd
import bee_box as bee

HERE = os.path.dirname(os.path.abspath(__file__))
SKIN, BROWN, TEAL, BLUE, ORANGE, GREY = (0.93, 0.78, 0.70), (0.45, 0.30, 0.22), (0.25, 0.70, 0.65), (0.30, 0.55, 0.85), (0.95, 0.60, 0.20), (0.55, 0.55, 0.60)
PINK = (0.85, 0.50, 0.65)
NYLON = (0.23, 0.25, 0.29)        # MJF PA12 dyed black, for the unpainted clips + lever arm
SILVER = (0.80, 0.82, 0.86)

def shape_tris(shape, tol=0.05):
    v, tr = shape.tessellate(tol, 0.2)
    v = np.array([[p.X, p.Y, p.Z] for p in v]); return v[np.array(tr)]

# ---------------- body
d = np.load(os.path.join(HERE, "..", "assets", "body_upper.npz")); BV, BF = d["V"], d["F"]
XM = -60.0                                                    # body midline (model origin is at the LEFT ear canal, midline is 60 mm toward the right)
keep = np.all(np.abs(BV[BF][:, :, 0] - XM) < 125, axis=1)           # drop the arms
BT = BV[BF[keep]]
L = BV[BV[:, 0] > 0]

def surf_x(y, z, r=6.0):
    m = (abs(L[:, 1] - y) < r) & (abs(L[:, 2] - z) < r)
    return L[m, 0].max() if m.any() else np.nan

def front_y(x, z, r=8.0):
    m = (abs(BV[:, 0] - x) < r) & (abs(BV[:, 2] - z) < r) & (BV[:, 1] > -20)
    return BV[m, 1].max() if m.any() else np.nan

def slice_stats(z):
    m = (abs(BV[:, 2] - z) < 4) & (abs(BV[:, 0]) < 90) & (BV[:, 1] > -120)
    return np.abs(BV[m, 0]).max(), BV[m, 1].max(), BV[m, 1].min()

# skin surface near the ear for the CAD parts: quadratic fit to the cranium, ear region excluded
sel = (BV[:, 0] > 0) & (abs(BV[:, 1] + 10) < 110) & (BV[:, 2] > -35) & (BV[:, 2] < 80) & ~((BV[:, 1] > -48) & (BV[:, 1] < 14) & (BV[:, 2] > -45) & (BV[:, 2] < 48))
y_, z_, x_ = BV[sel, 1], BV[sel, 2], BV[sel, 0]
A = np.stack([np.ones_like(y_), y_, z_, y_ ** 2, z_ ** 2, y_ * z_], 1)
coef = np.linalg.lstsq(A, x_, rcond=None)[0]
def X0(y, z): return float(coef @ np.array([1, y, z, y * y, z * z, y * z]))

# ---------------- one ear's worth of hardware (left); mirrored for the right
def ear_pieces():
    out = []
    stem, P3, sarr = glasses_stem(X0)
    global HINGE; HINGE = np.array(P3[0])
    out.append((shape_tris(stem), BROWN))
    clip, _, i_clip, _, lat = clip_flex(P3, sarr, 127.0, FLEX)                  # one spring-jaw clip per ear, fused to the arm (clip A no longer exists)
    out.append((shape_tris(clip), NYLON))
    arm = exciter_arm(X0, P3, sarr, np.array(P3[i_clip]) + lat["shift"], preload=0.0, lat_off=lat["lat_outer"] + H.arm_t / 2 - 0.8)
    out.append((shape_tris(arm), NYLON))
    dy, dz = exciter_dims()
    ex = Pos(X0(H.mastoid_y, H.mastoid_z) + P.exc_t / 2, H.mastoid_y, H.mastoid_z) * Box(P.exc_t, *((P.exc_w, P.exc_l) if dz > dy else (P.exc_l, P.exc_w)))
    out.append((shape_tris(ex), ORANGE))
    plate_z = dz + 2 * P.jaw_t + 2
    E = np.array([X0(H.mastoid_y, H.mastoid_z) + P.exc_t + P.jaw_t / 2, H.mastoid_y, H.mastoid_z - plate_z / 2 + 2.5])
    # earring dangle (mic + amp PCB) hanging from the lobe piercing
    ear = L[(L[:, 0] > np.array([X0(y, z) for y, z in zip(L[:, 1], L[:, 2])]) + 3) & (abs(L[:, 1] + 12) < 32) & (L[:, 2] > -50) & (L[:, 2] < 50)]
    lobe_z = ear[:, 2].min(); lob = ear[ear[:, 2] < lobe_z + 6]
    pierce = np.array([lob[:, 0].mean() + 1.5, lob[:, 1].mean(), lobe_z + 7.0])
    bshell, blid, binfo = gd.build(gd.GP(), "L")
    lx, ly, lz = binfo["loop"]                                      # hook loop hole centre (local)
    t = np.array([pierce[0] + 2.0 - lz, pierce[1] - lx, pierce[2] - 1.5 - ly])   # place so the loop hole sits just below/outside the piercing
    loopw = np.array([lz, lx, ly]) + t
    th = np.radians(BEAR_YAW); Rz = np.array([[np.cos(th), -np.sin(th), 0], [np.sin(th), np.cos(th), 0], [0, 0, 1]])
    yaw = lambda Pw: (np.asarray(Pw) - loopw) @ Rz.T + loopw        # turn the bear about the vertical axis through its hook loop: front faces slightly forward
    W = lambda sh: yaw(shape_tris(sh)[:, :, [2, 0, 1]] + t)         # local (x,y,z) -> world (z,x,y)
    out.append((W(bshell), BEARP)); out.append((W(blid), BEARP))
    ANCHORS['bear'] = W(bshell).reshape(-1, 3).mean(0); ANCHORS['mic'] = yaw(np.array([[gd.GP().height, gd.GP().mic_dx, gd.GP().pcb_y + gd.GP().mic_dy]]) + t)[0]; ANCHORS['hook'] = loopw
    ANCHORS['clipA'] = np.array(P3[int(np.argmin(abs(sarr - 100)))]); ANCHORS['clip'] = np.array(P3[int(np.argmin(abs(sarr - 127)))])
    hook = [pierce + [-3, 0, 0.5], pierce + [0.5, 0, 3.0], pierce + [3.5, 0, 2.0], loopw + [0, 0, 1.0]]
    out.append((tube(catmull(np.array(hook, float), 8), 0.5, 5), (0.80, 0.82, 0.86)))
    top = np.array([gd.GP().slot_x, 0, 0]); topw = yaw(np.array([1.6, gd.GP().slot_x, 21.0]) + t)     # cable slot exit (top of head, back side)
    sx = lambda y, z: (lambda v: v if not np.isnan(v) else X0(y, z))(surf_x(y, z, 9.0))
    ANCHORS['exciter'] = np.array(E); ANCHORS['arm'] = np.array(P3[int(np.argmin(abs(sarr - 127)))]) + np.array([4.0, -8.0, -22.0])
    exc_cable = catmull(np.array([topw, [sx(-26, -22) + 4, -26, -22], [sx(-31, -27) + 4, -31, -27], E], float), 10)
    out.append((tube(exc_cable, 0.7, 5), (0.10, 0.10, 0.12)))
    bottom = topw                                                    # neck cable starts at the same top slot (all cables leave through the top)
    return out, E, bottom

# ---------------- neck, chain, box
BVb = BV[np.unique(BF[keep])]                                   # body vertices without the arms
nk = BVb[(abs(BVb[:, 2] + 95) < 5) & (abs(BVb[:, 0] - XM) < 60) & (BVb[:, 1] > -110)]
yc = (nk[:, 1].max() + nk[:, 1].min()) / 2
print("neck: half-width", round(abs(nk[:, 0] - XM).max()), "centre y", round(yc), "depth", round(nk[:, 1].max() - nk[:, 1].min()))
def radial(phi, z, w=7, dang=np.radians(8), rmax=None):
    rmax = (92 if abs(np.sin(phi)) > 0.5 else 150) if rmax is None else rmax
    m = abs(BVb[:, 2] - z) < w; V = BVb[m]
    ang = np.arctan2(V[:, 0] - XM, -(V[:, 1] - yc)); r = np.hypot(V[:, 0] - XM, V[:, 1] - yc)
    ok = (abs(((ang - phi + np.pi) % (2 * np.pi)) - np.pi) < dang) & (r < rmax)
    return r[ok].max() if ok.any() else np.nan
z0, hang = -118.0, 125.0
def chain_pt(phi):
    z = z0 - hang * np.exp(-((phi - np.pi) / 0.75) ** 2)
    r = radial(phi, z)
    if np.isnan(r): r = 70.0
    r = r + 3.0 if (np.pi / 2 < phi < 3 * np.pi / 2) is False else r + 4.0
    return np.array([XM + r * np.sin(phi), yc - r * np.cos(phi), z])
phis = np.linspace(0, 2 * np.pi, 200)
chain = np.array([chain_pt(p) for p in phis])
bp = bee.HP(); bbase, bcover, binf = bee.build(bp); _b = bee.BP()
BW = 62.0
top = chain_pt(np.pi)
box_c = np.array([XM, top[1] - _b.head_rz + 3.0, top[2] - _b.chain_hole_y])      # chain passes through the head hole (local y=34, z=5.8)
def box_tris(shape):                       # box local (X,Y,Z) -> world (X, Z, Y) (+ translate)
    T = shape_tris(shape); return T[:, :, [0, 2, 1]] + box_c

def sm(pts, n=14): return catmull(np.array(pts), n)
def tube(P_, r=1.1, n=6):
    P_ = np.asarray(P_, float); N = len(P_)
    t = np.gradient(P_, axis=0); t /= np.linalg.norm(t, axis=1, keepdims=True) + 1e-12
    ref = np.array([0.0, 0.0, 1.0]); rings = []
    for i in range(N):
        u = np.cross(t[i], ref)
        if np.linalg.norm(u) < 1e-6: u = np.cross(t[i], [1.0, 0, 0])
        u /= np.linalg.norm(u); v = np.cross(t[i], u)
        ang = np.linspace(0, 2 * np.pi, n, endpoint=False)
        rings.append(P_[i] + r * (np.outer(np.cos(ang), u) + np.outer(np.sin(ang), v)))
    T = []
    for i in range(N - 1):
        for j in range(n):
            a_, b_, c_, d_ = rings[i][j], rings[i][(j + 1) % n], rings[i + 1][(j + 1) % n], rings[i + 1][j]
            T += [[a_, b_, c_], [a_, c_, d_]]
    return np.array(T)
def cable_for_side(start):
    # ear -> down behind the ear -> neck -> joins the chain at the side -> along the chain -> box top slot (left side; mirrored for the right)
    sx = lambda y, z: (lambda v: v if not np.isnan(v) else X0(y, z))(surf_x(y, z, 9.0))
    pts = [start, [sx(-24, -50) + 5, -26, -50], [sx(-28, -66) + 5, -28, -66], [sx(-30, -85) + 5, -30, -85], [sx(-30, -102) + 5, -30, -102]]
    pts = [np.array(p, float) for p in pts]
    pts.append(chain_pt(np.pi / 2) + np.array([2.5, 0, 0]))
    for phi in np.linspace(np.pi / 2 + 0.15, np.pi - 0.16, 7): pts.append(chain_pt(phi) + np.array([2.5, 2.0, 0]))
    pts.append(BEE_END)
    return sm(pts)


CATEYE = [(0, 30), (2, 38), (10, 42), (24, 44), (40, 45.5), (52, 45), (57, 40), (58, 30), (56, 18), (50, 7), (40, 2.5), (26, 1), (12, 2), (4, 7), (0, 16)]   # soft cat-eye: convex top rising gently outward, flat bottom, round outer corner (x outward from the nose edge, y up)
def _closed_catmull(pts, n=6):
    P_ = np.array(pts, float); N = len(P_); out = []
    for i in range(N):
        p0, p1, p2, p3 = P_[(i - 1) % N], P_[i], P_[(i + 1) % N], P_[(i + 2) % N]
        for t in np.linspace(0, 1, n, endpoint=False):
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t ** 2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    return np.array(out)

def frame_front(y_front_off=7.0, z_hinge=None, tilt=15.0, wrap=8.0, shift=0.0):
    """Cat-eye acetate front after the user's photos (57-17, thick translucent rims, high keyhole bridge, tilted lenses that wrap back slightly). No lenses.
    Built flat as local (x lateral, h height, d depth), warped, then mapped to world (x, d, h)."""
    from build123d import Polygon, extrude, offset, Box, Pos
    rim, depth, half_bridge = 4.2, 5.0, 8.5
    poly = _closed_catmull(CATEYE)
    shape = None
    for sx in (-1, 1):
        pts = [(sx * (half_bridge + x), y) for x, y in poly]
        o = Polygon(*pts, align=None)
        ring = extrude(o, amount=depth) - extrude(offset(o, amount=-rim), amount=depth)
        shape = ring if shape is None else shape + ring
        shape = shape + Pos(sx * (half_bridge + 58 + 1.5), 41.0, -4.0 - shift / 2) * Box(5.0, 8.0, 9.0 + shift)   # end piece reaching back to the hinge (longer when the front is moved forward)
    shape = shape + Pos(0, 31.0, depth / 2) * Box(2 * half_bridge + 5.0, 7.0, depth)                       # keyhole bridge
    T = shape_tris(shape).copy()
    x, h, d = T[..., 0], T[..., 1], T[..., 2]
    h_top = 45.5
    d2 = d + (h - h_top) * np.sin(np.radians(tilt)) - np.clip(abs(x) - half_bridge, 0, None) * np.tan(np.radians(wrap))   # bottom tilts back, outer parts wrap back
    h2 = h_top + (h - h_top) * np.cos(np.radians(tilt)) - d * np.sin(np.radians(tilt))
    T = np.stack([x, d2, h2], -1)                                                                           # (x, h, d) -> (x, d, h)
    zc = (HINGE[2] if z_hinge is None else z_hinge) - 41.0
    return T + np.array([XM, HINGE[1] + y_front_off - 4.5 + shift, zc])

def frame_cols(T):
    """translucent-acetate look: dark brown at the top fading to pale clear at the bottom"""
    z = T[:, :, 2].mean(1); f = np.clip((z - z.min()) / (z.max() - z.min() + 1e-9), 0, 1) ** 0.8
    top, bot = np.array((0.42, 0.26, 0.20)), np.array((0.86, 0.74, 0.70))
    return bot[None, :] * (1 - f)[:, None] + top[None, :] * f[:, None]

ANCHORS = {}
BEARP, BEARB = (1.0, 0.45, 0.72), (0.30, 0.72, 1.0)
BEAR_YAW = 25.0                      # degrees, front of each bear turned toward the nose
def mirror_pts(T): return T * np.array([-1, 1, 1]) + np.array([2 * XM, 0, 0])             # mirror about the body midline (x = XM)
def as_cols(T, c): return np.tile(np.array(c, float), (len(T), 1)) if not callable(c) else c(T)

# chest front surface (max y per 2 mm cell of x,z) to keep the bee clear of the body
_pts = np.vstack([BT.reshape(-1, 3), BT.mean(1)])
_cell = 2.0
_ys = {}
for _x, _y, _z in _pts:
    if _z < -300 or _z > -40: continue
    k = (int(round(_x / _cell)), int(round(_z / _cell))); _ys[k] = max(_ys.get(k, -1e9), _y)
def chest_y(x, z):
    k = (int(round(x / _cell)), int(round(z / _cell))); return _ys.get(k, -1e9)
BEE_PIVOT = box_c + np.array([0.0, _b.head_rz, _b.chain_hole_y])           # centre of the chain hole in the head (world)
def bee_xf(P, alpha):
    """tilt about the ear-to-ear (x) axis through the chain hole; positive alpha swings the BOTTOM of the bee forward (+y)"""
    d = np.asarray(P) - BEE_PIVOT; c, s = np.cos(np.radians(alpha)), np.sin(np.radians(alpha))
    out = d.copy(); out[..., 1] = d[..., 1] * c - d[..., 2] * s; out[..., 2] = d[..., 1] * s + d[..., 2] * c
    return out + BEE_PIVOT
_beeT = [shape_tris(s)[:, :, [0, 2, 1]] + box_c for s in (bbase, bcover)]
def bee_clearance(alpha):
    worst = 1e9
    for T in _beeT:
        Q = bee_xf(T.reshape(-1, 3), alpha)
        for x, y, z in Q[::3]:
            ys = chest_y(x, z)
            if ys > -1e8: worst = min(worst, y - ys)
    return worst

_fy = {}
for _x, _y, _z in _pts:
    if -10 < _z < 70 and _y > 60:
        k = (int(round(_x / _cell)), int(round(_z / _cell))); _fy[k] = max(_fy.get(k, -1e9), _y)
def face_clearance(T):
    worst = 1e9
    for x, y, z in T.reshape(-1, 3)[::2]:
        ys = _fy.get((int(round(x / _cell)), int(round(z / _cell))), None)
        if ys is not None: worst = min(worst, y - ys)
    return worst

def build_scene():
    """Everything in the preview as a list of (triangles (n,3,3), colours (n,3)) in head coordinates; also fills ANCHORS (3D label positions)."""
    global BEE_END, BEE_ALPHA
    BEE_ALPHA = next((al for al in np.arange(0, 75, 2.5) if bee_clearance(al) >= 1.0), 60.0)
    print("bee tilt (bottom forward):", BEE_ALPHA, "deg; clearance", round(bee_clearance(BEE_ALPHA), 1), "mm (untilted:", round(bee_clearance(0.0), 1), "mm)")
    BEE_END = bee_xf(np.array([XM + 20.0, box_c[1] + 4.5, box_c[2] + 23.0]), BEE_ALPHA)
    left, E, bottom = ear_pieces()
    scene = [(BT, as_cols(BT, SKIN))]
    for T, col in left:
        scene.append((T, as_cols(T, col)))
        Tm = mirror_pts(T); scene.append((Tm, as_cols(Tm, BEARB if col == BEARP else col)))        # right ear = mirror image (blue bear)
    # bee: colour by local rule (before moving into the world), then transform
    YEL, BLK, SIL, DK = np.array((1.0, 0.82, 0.15)), np.array((0.12, 0.12, 0.14)), np.array((0.85, 0.88, 0.92)), np.array((0.35, 0.35, 0.38))
    def cov_col(c):
        out = np.tile(YEL, (len(c), 1)); cc = c.mean(1); ab = (cc[:, 1] < -22) & (cc[:, 2] > binf["wing_top"] - 0.3); hot = np.zeros(len(cc), bool)
        for yc in _b.ridge_y: hot |= abs(cc[:, 1] - yc) < 2.6
        out[ab & ~hot] = BLK; return out
    def base_col(c):
        cc = c.mean(1); out = np.tile(DK, (len(cc), 1)); out[abs(cc[:, 0]) > 31.5] = SIL
        out[(cc[:, 1] > 22.5) & (abs(cc[:, 0]) < 13)] = BLK; out[cc[:, 1] < binf["wy0"] + 1.0] = BLK; return out
    for sh, fn in ((bbase, base_col), (bcover, cov_col)):
        Tl = shape_tris(sh); scene.append((bee_xf(Tl[:, :, [0, 2, 1]] + box_c, BEE_ALPHA), fn(Tl)))
    shift = next((s for s in np.arange(0, 40, 0.5) if face_clearance(frame_front(shift=s)) >= 1.5), 40.0)
    Tf = frame_front(shift=shift)
    print('glasses front moved forward', shift, 'mm; clearance to face', round(face_clearance(Tf), 1), 'mm; front-plane distance from hinge', round(shift + 2.5, 1))
    scene.append((Tf, frame_cols(Tf)))
    cL = cable_for_side(bottom); mir = lambda P_: P_ * np.array([-1, 1, 1]) + np.array([2 * XM, 0, 0])
    for P_ in (cL, mir(cL)):
        T = tube(P_, 1.7); scene.append((T, as_cols(T, (0.15, 0.15, 0.18))))
    T = tube(chain[::2], 1.0, 5); scene.append((T, as_cols(T, SILVER)))
    ANCHORS["bee"] = np.vstack([t_[0] for t_, _ in scene[-6:-3]]).reshape(-1, 3).mean(0) if False else bee_xf(box_c + np.array([0, 6.0, -25.0]), BEE_ALPHA)
    ANCHORS["chain_top"] = np.array(top)
    ANCHORS["glasses_front"] = Tf.reshape(-1, 3).mean(0)
    return scene

def draw_scene(ax, scene, el, az, span, ctr, light_scale=0.6, ortho=False):
    """span: half-width of the (cubic) view box in mm, or (sx, sy, sz) for a non-cubic box."""
    sx, sy, sz = (span, span, span) if np.isscalar(span) else span
    e_, a_ = np.radians(el), np.radians(az)
    light = np.array([np.cos(e_) * np.cos(a_), np.cos(e_) * np.sin(a_), np.sin(e_)])
    allt, cols = [], []
    for T, c in scene:
        n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
        allt.append(T); cols.append(((1 - light_scale) + light_scale * np.abs(n @ light))[:, None] * c)
    ax.add_collection3d(Poly3DCollection(np.vstack(allt), facecolors=np.clip(np.vstack(cols), 0, 1), edgecolor="none"))
    ax.set_xlim(ctr[0] - sx, ctr[0] + sx); ax.set_ylim(ctr[1] - sy, ctr[1] + sy); ax.set_zlim(ctr[2] - sz, ctr[2] + sz)
    ax.set_box_aspect((sx, sy, sz)); ax.view_init(el, az); ax.set_axis_off()
    if ortho: ax.set_proj_type("ortho")

def render(path="out/preview_assembly.png"):
    scene = build_scene()
    xl = X0(0, 0) + 10
    views = [("front", 8, 90, 135, (XM, 0, -135)), ("back", 8, -90, 135, (XM, 0, -135)),
             ("3/4 from the left", 12, 35, 135, (XM, 0, -135)), ("3/4 from the right", 12, 145, 135, (XM, 0, -135)),
             ("LEFT ear, from the side", 0, 0, 62, (xl, -12, 8)), ("RIGHT ear, from the side", 0, 180, 62, (2 * XM - xl, -12, 8)),
             ("both ears, from the front", 3, 90, 100, (XM, 0, 0)), ("neck / cables, from behind", 5, -90, 110, (XM, -20, -90))]
    fig = plt.figure(figsize=(24, 12))
    for k, (title, el, az, span, ctr) in enumerate(views):
        ax = fig.add_subplot(2, 4, k + 1, projection="3d"); draw_scene(ax, scene, el, az, span, ctr, 0.6); ax.set_title(title, fontsize=11)
    fig.text(0.5, 0.01, "brown = glasses (stems + rough front), black = clip + lever arm (dyed-black MJF nylon), orange = exciter, pink / blue bears = dangles (mic + amp PCB), silver = chain + ear wires, black = cables, bee = necklace box. Schematic; generic CC0 body.", ha="center", fontsize=9)
    fig.tight_layout(rect=(0, 0.02, 1, 1)); os.makedirs(os.path.dirname(path), exist_ok=True); fig.savefig(path, dpi=75); plt.close(fig)


if __name__ == "__main__":
    print("neck slice x_half, y_front, y_back @ z=-118:", slice_stats(-118)); print("skin X0 at canal", round(X0(0, 0), 1), "at mastoid", round(X0(H.mastoid_y, H.mastoid_z), 1))
    render()

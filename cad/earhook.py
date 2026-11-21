"""Ear hook: arm arches over the top of the helix (like glasses), descends behind the ear, and ends in a plate that presses
the exciter on the mastoid. Built in world coords (canal opening = origin) so it can be previewed on the head model.
The arm is a leaf spring: thin laterally (flexes to give pad pressure), tall vertically (stiff, carries the dangle weight)."""
import numpy as np
from build123d import *
from params import P, H, Params, HookParams

def rbox(w, h, d, r):
    """Box centred at the origin (w=X, h=Y, d=Z) with all edges filleted."""
    return fillet(Box(w, h, d).edges(), radius=min(r, w / 2 - 0.01, h / 2 - 0.01, d / 2 - 0.01))

def catmull(pts, n=30):
    pts = np.array(pts, float); pts = np.vstack([2 * pts[0] - pts[1], pts, 2 * pts[-1] - pts[-2]])
    out = []
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        for t in np.linspace(0, 1, n, endpoint=False):
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t**2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t**3))
    out.append(pts[-2]); return np.array(out)

def exciter_dims(p=P):
    ew, el = p.exc_w + 2 * p.exc_clear, p.exc_l + 2 * p.exc_clear
    return (ew, el) if abs(p.exc_angle % 180) < 45 else (el, ew)   # (dy, dz) in world: vertical exciter => long axis along Z

def ear_hook(skin_x, p: Params = P, h: HookParams = H, preload=None, arm_t=None, prefix=None):
    """skin_x(y,z) -> x of the head surface. Returns solid. preload=0 gives the 'worn' shape (for previews)."""
    pre = h.preload if preload is None else preload
    at = h.arm_t if arm_t is None else arm_t
    t = p.jaw_t
    dy, dz = exciter_dims(p)
    ym, zm = h.mastoid_y, h.mastoid_z
    x_in = skin_x(ym, zm) + p.exc_t - pre                      # inner (lateral) face of the exciter plate
    plate_y, plate_z = dy + 2 * t + 2, dz + 2 * t + 2
    plate = Pos(x_in + t / 2, ym, zm) * rbox(t, plate_y, plate_z, 2.5)
    rim_h = p.exc_t - 1.0                                     # exciter base stands 1 mm proud of the rim, touching skin
    rim = Pos(x_in - rim_h / 2, ym, zm) * (Box(rim_h, dy + 2 * t, dz + 2 * t) - Box(rim_h + 0.2, dy, dz))
    tie = Pos(x_in + t / 2, ym, zm - plate_z / 2 + 2.5) * (Rot(0, 90, 0) * Cylinder(0.7, t + 2))   # cable strain-relief hole (thread / tiny tie)

    z_end = zm + plate_z / 2 - 3.0
    tail = (ym, z_end, p.exc_t - pre + t / 2)
    ctrl = (list(prefix) + [tail]) if prefix is not None else [(16, 38, 3), (6, 41, 9), (-6, 40, 12), (-18, 34, 11), (-28, 22, 8), (-31, 12, 6), tail]
    c = catmull([(y, z, l) for (y, z, l) in ctrl])
    pts = [Vector(skin_x(y, z) + l, y, z) for y, z, l in c]
    secs = []
    step = 4
    idx = list(range(0, len(pts) - 1, step)) + [len(pts) - 1]
    lat = Vector(1, 0, 0)
    for i in idx:
        j0, j1 = max(i - 1, 0), min(i + 1, len(pts) - 1)
        tan = (pts[j1] - pts[j0]).normalized()
        xdir = (lat - tan * lat.dot(tan)).normalized()
        secs.append(Plane(origin=pts[i], x_dir=xdir, z_dir=tan) * Rectangle(at, h.arm_h))
    arm = loft(secs)
    return (arm + plate + rim) - tie

def spring_table(h=H):
    """Cantilever estimate of pad force vs arm thickness. L = arm length from the arch to the pad (ASSUMED ~55 mm)."""
    L = 55.0
    print(f"{'arm_t':>6} {'k (N/mm)':>9} {'force @ preload':>16} {'strain %':>9}")
    for t in (1.6, 2.0, 2.4, 2.8, 3.2):
        I = h.arm_h * t**3 / 12; k = 3 * h.E_pa12 * I / L**3; d = h.preload
        print(f"{t:6.1f} {k:9.3f} {k * d:13.2f} N {100 * 3 * t * d / (2 * L**2):9.2f}")

if __name__ == "__main__":
    import os; os.makedirs("out", exist_ok=True)
    flat = lambda y, z: 0.0
    spring_table()
    for t in (1.6, 2.4, 3.2):
        s = ear_hook(flat, arm_t=t)
        print(t, f"volume {s.volume:.0f} mm3 valid={s.is_valid}")

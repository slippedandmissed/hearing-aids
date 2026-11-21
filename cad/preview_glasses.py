"""Close-up of the glasses front on the head model: out/glasses_check.png (face-on, side, 3/4). uv run python preview_glasses.py"""
import os
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import assembly as A

A.ear_pieces()                                              # sets A.HINGE
Tf = A.frame_front(shift=2.0)
fig = plt.figure(figsize=(18, 6))
for k, (el, az, t) in enumerate(((0, 90, "front (face-on)"), (0, 0, "side"), (30, 60, "3/4"))):
    ax = fig.add_subplot(1, 3, k + 1, projection="3d"); e, a_ = np.radians(el), np.radians(az)
    L = np.array([np.cos(e) * np.cos(a_), np.cos(e) * np.sin(a_), np.sin(e)]); Ts, Cs = [], []
    for T, col in ((A.BT, np.tile(np.array(A.SKIN), (len(A.BT), 1))), (Tf, A.frame_cols(Tf))):
        n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
        Ts.append(T); Cs.append(np.clip((0.4 + 0.6 * abs(n @ L))[:, None] * col, 0, 1))
    ax.add_collection3d(Poly3DCollection(np.vstack(Ts), facecolors=np.vstack(Cs), edgecolor="none"))
    ctr, s = (A.XM, 60, 25), 62
    ax.set_xlim(ctr[0] - s, ctr[0] + s); ax.set_ylim(ctr[1] - s, ctr[1] + s); ax.set_zlim(ctr[2] - s, ctr[2] + s)
    ax.set_box_aspect((1, 1, 1)); ax.view_init(el, az); ax.set_axis_off(); ax.set_title(t)
os.makedirs("out", exist_ok=True); fig.savefig("out/glasses_check.png", dpi=70)

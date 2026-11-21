"""Build a female head/neck/torso mesh from MakeHuman CC0 assets (assets/mh_raw, untrusted download: parsed as plain text only).
python -I assets/build_body.py  -> assets/body_upper.npz  (vertices in mm: X = out of LEFT ear, Y = nose, Z = up; origin ~ left ear canal)"""
import numpy as np, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); RAW = os.path.join(HERE, "mh_raw")

def read_obj(path):
    V, F, grp = [], [], None
    for line in open(path):
        if line.startswith("v "): V.append([float(x) for x in line.split()[1:4]])
        elif line.startswith("g "): grp = line.split()[1]
        elif line.startswith("f ") and grp == "body":
            idx = [int(t.split("/")[0]) - 1 for t in line.split()[1:]]
            for k in range(1, len(idx) - 1): F.append([idx[0], idx[k], idx[k + 1]])
    return np.array(V), np.array(F)

def read_target(path, n):
    d = np.zeros((n, 3))
    for line in open(path):
        if line.startswith("#") or not line.strip(): continue
        p = line.split()
        if len(p) == 4: d[int(p[0])] = [float(x) for x in p[1:]]
    return d

V, F = read_obj(os.path.join(RAW, "base.obj")); n = len(V)
V = V + sum(read_target(os.path.join(RAW, f"{r}-female-young.target"), n) for r in ("caucasian", "african", "asian")) / 3.0
V = V + read_target(os.path.join(RAW, "universal-female-young-averagemuscle-averageweight.target"), n)
V = V * 100.0                                                    # decimetres -> mm
body_ids = np.unique(F)
ytop = V[body_ids, 1].max(); ybot = V[body_ids, 1].min(); H = ytop - ybot
print("body height mm", round(H), "x extent", V[body_ids, 0].min().round(), V[body_ids, 0].max().round())
# head vertices
head = body_ids[V[body_ids, 1] > ytop - 0.13 * H]
nose_z = V[head, 2].max()
# ear: lateral extreme cluster at ear height (~0.065*H below the crown)
band = head[(V[head, 1] < ytop - 0.045 * H) & (V[head, 1] > ytop - 0.095 * H) & (V[head, 0] > 0)]
xmax = V[band, 0].max(); ear = band[V[band, 0] > xmax - 12]
ear_c = V[ear].mean(0)
print("ear centroid (mh coords, mm)", ear_c.round(1), "nose z", round(nose_z))
canal = ear_c + np.array([-14.0, -4.0, 10.0])                    # canal opening: medial of the helix rim, a bit low, a bit forward (ASSUMED offsets)
# crop: keep above mid-chest
ycut = ytop - 0.30 * H
keep = np.all(V[F][:, :, 1] > ycut, axis=1)
Fk = F[keep]
used = np.unique(Fk); remap = -np.ones(n, int); remap[used] = np.arange(len(used))
Vk = V[used] - canal; Fk = remap[Fk]
Vk = np.stack([Vk[:, 0], Vk[:, 2], Vk[:, 1]], 1)                  # (x,y,z)_mh -> X lateral, Y forward, Z up
Fk = Fk[:, [0, 2, 1]]                                             # keep winding sane after the axis swap
np.savez(os.path.join(HERE, "body_upper.npz"), V=Vk, F=Fk)
print("saved", Vk.shape, Fk.shape, "extents", (Vk.max(0) - Vk.min(0)).round())
print("crown z", Vk[:, 2].max().round(), "chin approx z", (Vk[:, 2].max() - 0.13 * H).round(), "nose y", Vk[:, 1].max().round())

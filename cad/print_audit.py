"""Mesh-level audit of every print STL against JLC3DP's MJF PA12 limits -> cad/print/audit.csv (+ a printed summary).
  uv run python cad/print_audit.py [name-filter]

What it measures (on the real triangles, not the CAD parameters):
  wall   : from random points on the surface, a ray goes INTO the solid along the inward normal to the opposite wall. The distance is the local wall thickness.
           Reported: the thinnest 1 % of the surface (p1), the share of the surface thinner than 1.0 mm (JLC3DP's recommended wall) and than 0.8 mm.
  gap    : the same, but OUTWARD: the distance to the next surface across an empty gap (slots, pockets, narrow channels), and the share narrower than 0.4 mm
           (nylon needs about 0.4 mm to keep two features apart; powder gets trapped in narrower gaps).
Limits (JLC3DP, researched 2026-11-21): wall >= 1.0 mm recommended, detail >= 0.5 - 0.8 mm, clearance 0.2 - 0.4 mm (one page says 0.6). These are not hard failures: the output
says where to look. Sampling is random (fixed seed), so the numbers are statistical: a very small feature can be missed."""
import os, sys, csv
import numpy as np, trimesh

HERE = os.path.dirname(os.path.abspath(__file__)); PRINT = os.path.join(HERE, "print")
WALL_REC, WALL_MIN, GAP_MIN, N = 1.0, 0.8, 0.4, 12000

def probe(mesh, rng):
    pts, fi = trimesh.sample.sample_surface(mesh, N, seed=int(rng.integers(1 << 31)))
    nrm = mesh.face_normals[fi]; out = {}
    for name, sgn in (("wall", -1.0), ("gap", 1.0)):
        d = sgn * nrm; org = pts + d * 1e-4                                                 # start a hair off the surface, on the side we look into
        loc, ray, tri = mesh.ray.intersects_location(org, d, multiple_hits=False)
        dist = np.full(len(pts), np.inf)
        if len(ray):
            hit_n = mesh.face_normals[tri]; opp = -sgn * (hit_n * d[ray]).sum(1) > 0.3      # the far wall must be roughly parallel: inward rays leave through a face looking the same way, outward rays meet one looking back (not a neighbouring face)
            dd = np.linalg.norm(loc - org[ray], axis=1); ok = ray[opp]; dist[ok] = dd[opp]
        out[name] = dist
    return pts, out

def audit(path, rng):
    m = trimesh.load(path, force="mesh"); pts, d = probe(m, rng); w, g = d["wall"], d["gap"]
    fw = w[np.isfinite(w)]; fg = g[np.isfinite(g)]
    p1 = float(np.percentile(fw, 1)) if len(fw) else float("nan")
    r = dict(file=os.path.basename(path), wall_p1=round(p1, 2), wall_min=round(float(fw.min()), 2) if len(fw) else "",
             pct_wall_lt_1_0=round(100 * float((fw < WALL_REC).sum()) / len(pts), 1), pct_wall_lt_0_8=round(100 * float((fw < WALL_MIN).sum()) / len(pts), 1),
             gap_min=round(float(fg.min()), 2) if len(fg) else "", pct_gap_lt_0_4=round(100 * float((fg < GAP_MIN).sum()) / len(pts), 1))
    thin = pts[np.isfinite(w) & (w < WALL_MIN)]
    r["thin_at"] = "" if not len(thin) else "x %.0f..%.0f, y %.0f..%.0f, z %.0f..%.0f" % tuple(np.ravel([(thin[:, k].min(), thin[:, k].max()) for k in range(3)]))
    return r

if __name__ == "__main__":
    flt = sys.argv[1] if len(sys.argv) > 1 else ""; rng = np.random.default_rng(1); rows = []
    for f in sorted(os.listdir(PRINT)):
        if f.endswith(".stl") and flt in f: rows.append(audit(os.path.join(PRINT, f), rng)); print(rows[-1]["file"], {k: v for k, v in rows[-1].items() if k not in ("file", "thin_at")}, rows[-1]["thin_at"], flush=True)
    with open(os.path.join(PRINT, "audit.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print("wrote cad/print/audit.csv")

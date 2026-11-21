"""JLC BOM + CPL from the final board. KiCad python: python3 bom.py L|R"""
import sys, os, csv
import pcbnew
from pcbnew import ToMM as tomm
V = sys.argv[1]; HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out"); H = 28.0
board = pcbnew.LoadBoard(os.path.join(OUT, f"dangle_{V}_final.kicad_pcb"))
import json
parts = json.load(open(os.path.join(OUT, f"dangle_{V}_parts.json")))
rows = {}; cpl = []
for fp in board.GetFootprints():
    ref = fp.GetReference()
    if ref not in parts or not parts[ref][0]: continue
    lc, val = parts[ref]; fpn = str(fp.GetFPID().GetLibItemName())
    rows.setdefault((val, fpn, lc), []).append(ref)
    pos = fp.GetPosition(); cpl.append((ref, tomm(pos.x), H - tomm(pos.y), "Top", fp.GetOrientationDegrees() % 360))
with open(os.path.join(OUT, f"dangle_{V}_BOM.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
    for (val, fpn, lc), refs in sorted(rows.items(), key=lambda kv: kv[1][0]): w.writerow([val, ",".join(sorted(refs)), fpn, lc])
with open(os.path.join(OUT, f"dangle_{V}_CPL.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
    for ref, x, y, layer, rot in sorted(cpl): w.writerow([ref, f"{x:.3f}mm", f"{y:.3f}mm", layer, f"{rot:.0f}"])
print("BOM rows", len(rows), "CPL rows", len(cpl))

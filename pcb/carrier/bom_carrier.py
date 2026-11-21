import os, csv, json, pcbnew
from pcbnew import ToMM as tomm
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out"); H = 40.0
board = pcbnew.LoadBoard(os.path.join(OUT, "carrier_C_final.kicad_pcb")); parts = json.load(open(os.path.join(OUT, "carrier_C_parts.json")))
JLC_ASSEMBLE = {"RL_", "RR_", "R_LED", "D1", "C_BULK", "C_BYP", "Q1", "F1"}            # SMD parts JLC places; the rest are hand-soldered
rows, cpl, hand = {}, [], []
for fp in board.GetFootprints():
    ref = fp.GetReference()
    if ref not in parts: continue
    lc, val = parts[ref]
    if any(ref.startswith(p) for p in JLC_ASSEMBLE):
        rows.setdefault((val, str(fp.GetFPID().GetLibItemName()), lc), []).append(ref)
        pos = fp.GetPosition(); cpl.append((ref, tomm(pos.x), H - tomm(pos.y), "Top", fp.GetOrientationDegrees() % 360))
    else: hand.append((ref, val, lc))
with open(os.path.join(OUT, "carrier_BOM.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
    for (val, fpn, lc), refs in sorted(rows.items(), key=lambda kv: kv[1][0]): w.writerow([val, ",".join(sorted(refs)), fpn, lc])
with open(os.path.join(OUT, "carrier_CPL.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
    for ref, x, y, layer, rot in sorted(cpl): w.writerow([ref, f"{x:.3f}mm", f"{y:.3f}mm", layer, f"{rot:.0f}"])
print("JLC BOM rows", len(rows), "CPL rows", len(cpl), "hand-soldered:", hand)

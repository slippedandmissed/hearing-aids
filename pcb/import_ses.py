"""Dangle PCB: import Freerouting's .ses into the placed board, tie the amp ground pins to its exposed pad, bridge the mic ground ring, save dangle_<V>_ses.kicad_pcb. KiCad python: import_ses.py L|R"""
import sys, os, json
import pcbnew
from pcbnew import FromMM as mm
V = sys.argv[1]; HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out"); W, H = 13.0, 28.0
board = pcbnew.LoadBoard(os.path.join(OUT, f"dangle_{V}_placed.kicad_pcb"))
ok = pcbnew.ImportSpecctraSES(board, os.path.join(OUT, f"dangle_{V}.ses")); print("SES import", ok)
# --- clean-up after the import
seen = set()
for t in list(board.GetTracks()):                       # drop duplicate vias the importer creates
    if t.GetClass() == "PCB_VIA":
        k = (t.GetPosition().x, t.GetPosition().y, t.GetNetCode())
        if k in seen: board.Remove(t)
        seen.add(k)
code = {n.GetNetname(): n.GetNetCode() for n in board.GetNetInfo().NetsByNetcode().values()}
def trk(pts):
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        t = pcbnew.PCB_TRACK(board); t.SetStart(pcbnew.VECTOR2I(mm(x1), mm(y1))); t.SetEnd(pcbnew.VECTOR2I(mm(x2), mm(y2))); t.SetWidth(mm(0.2)); t.SetLayer(pcbnew.F_Cu); t.SetNetCode(code["GND"]); board.Add(t)
u1 = board.FindFootprintByReference("U1"); pp = {p.GetNumber(): p.GetPosition() for p in u1.Pads()}
ep = pp["17"]
for n in ("3", "11", "15"):                             # amp ground pins -> exposed pad (short straight ties)
    x, y = pcbnew.ToMM(pp[n].GetPosition().x if hasattr(pp[n], "GetPosition") else pp[n].x), pcbnew.ToMM(pp[n].y)
    cx, cy = pcbnew.ToMM(ep.x), pcbnew.ToMM(ep.y)
    tx, ty = (x, cy + (0.4 if y > cy else -0.4)) if n != "15" else (cx - 0.5, y)
    trk([(x, y), (tx, ty)])
u2 = board.FindFootprintByReference("U2"); hc = None
for p in u2.Pads():
    if p.GetNumber() == "": hc = p.GetPosition()
hx, hy = pcbnew.ToMM(hc.x), pcbnew.ToMM(hc.y)           # mic port hole: link the four ground-ring segments by L-shaped tracks outside the hole clearance
trk([(hx - 0.46, hy + 0.43), (hx - 0.8, hy + 0.43), (hx - 0.8, hy - 0.45), (hx - 0.45, hy - 0.45)])            # left pair
trk([(hx + 0.45, hy + 0.44), (hx + 0.8, hy + 0.44), (hx + 0.8, hy - 0.44), (hx + 0.46, hy - 0.44)])            # right pair
trk([(hx - 0.45, hy - 0.45), (hx - 0.45, hy - 0.8), (hx + 0.46, hy - 0.8), (hx + 0.46, hy - 0.44)])            # top link joins the pairs
pcbnew.SaveBoard(os.path.join(OUT, f"dangle_{V}_ses.kicad_pcb"), board)
print("tracks", len(list(board.GetTracks())))

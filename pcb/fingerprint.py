"""Print a SHA-256 fingerprint of a placed board: footprints (reference, position, rotation, footprint name, pad -> net) and the board outline.
Used by pipeline.py to decide whether a committed routing lock (pcb/routes/*.ses) still matches the placement. KiCad python:
  python3 fingerprint.py <board.kicad_pcb>"""
import sys, json, hashlib
import pcbnew
from pcbnew import ToMM

def fingerprint(path):
    b = pcbnew.LoadBoard(path); items = []
    for fp in b.GetFootprints():
        p = fp.GetPosition()
        items.append(["fp", fp.GetReference(), round(ToMM(p.x), 3), round(ToMM(p.y), 3), round(fp.GetOrientationDegrees() % 360, 2), str(fp.GetFPID().GetLibItemName()),
                      sorted((pad.GetNumber(), pad.GetNetname()) for pad in fp.Pads())])
    for d in b.GetDrawings():
        if d.GetLayer() == pcbnew.Edge_Cuts:
            s, e = d.GetStart(), d.GetEnd(); items.append(["edge", d.GetShape(), round(ToMM(s.x), 3), round(ToMM(s.y), 3), round(ToMM(e.x), 3), round(ToMM(e.y), 3)])
    items.sort(key=lambda x: json.dumps(x, sort_keys=True, default=str))
    return hashlib.sha256(json.dumps(items, sort_keys=True, default=str).encode()).hexdigest()

if __name__ == "__main__": print(fingerprint(sys.argv[1]))

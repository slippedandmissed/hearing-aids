"""Generic SES import: python3 import_ses_generic.py <outdir> <prefix_variant>  e.g. carrier/out carrier_C"""
import sys, os, pcbnew
OUT, NAME = sys.argv[1], sys.argv[2]
board = pcbnew.LoadBoard(os.path.join(OUT, f"{NAME}_placed.kicad_pcb"))
print("SES import", pcbnew.ImportSpecctraSES(board, os.path.join(OUT, f"{NAME}.ses")))
seen = set()
for t in list(board.GetTracks()):
    if t.GetClass() == "PCB_VIA":
        k = (round(t.GetPosition().x / 20000), round(t.GetPosition().y / 20000))
        if k in seen: board.Remove(t)
        seen.add(k)
pcbnew.SaveBoard(os.path.join(OUT, f"{NAME}_ses.kicad_pcb"), board); print("tracks", len(list(board.GetTracks())))

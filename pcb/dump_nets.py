"""Dump every footprint's pad -> net map of a routed board to JSON, for the circuit-diagram check (docs/check_circuits.py).
KiCad's python:  $KICAD_PY pcb/dump_nets.py <board.kicad_pcb> <out.json>"""
import sys, json
import pcbnew
board = pcbnew.LoadBoard(sys.argv[1])
if board is None: sys.exit("cannot load " + sys.argv[1])
out = {fp.GetReference(): {p.GetNumber(): p.GetNetname() for p in fp.Pads() if p.GetNumber()} for fp in board.GetFootprints()}
json.dump(out, open(sys.argv[2], "w"), indent=1, sort_keys=True)
print("wrote", sys.argv[2], len(out), "footprints")

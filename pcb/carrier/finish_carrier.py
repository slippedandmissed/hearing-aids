"""Dedupe vias, add silkscreen, save *_final. KiCad python."""
import os, pcbnew
from pcbnew import FromMM as mm, VECTOR2I
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
board = pcbnew.LoadBoard(os.path.join(OUT, "carrier_C_routed.kicad_pcb"))
seen = set()
for t in list(board.GetTracks()):
    if t.GetClass() == "PCB_VIA":
        k = (round(t.GetPosition().x / 20000), round(t.GetPosition().y / 20000))
        if k in seen: board.Remove(t)
        seen.add(k)
def text(s, x, y, h=1.0, layer=pcbnew.F_SilkS, mirror=False, thick=0.15, just=None):
    t = pcbnew.PCB_TEXT(board); t.SetText(s); t.SetLayer(layer); t.SetPosition(VECTOR2I(mm(x), mm(y)))
    t.SetTextSize(VECTOR2I(mm(h), mm(h))); t.SetTextThickness(mm(thick)); t.SetMirrored(mirror); board.Add(t)
text("+", 14.2, 31.0, 1.6, thick=0.3); text("-", 14.2, 29.0, 1.6, thick=0.3)          # battery polarity beside the JST pads (CHECK YOUR BATTERY PLUG)
text("BATT", 15.5, 26.8, 1.0)
text("SWITCH ON TO CHARGE", 36.0, 31.6, 1.0, layer=pcbnew.B_SilkS, mirror=True)
text("B+", 13.6, 19.0, 1.0); text("B-", 13.6, 21.0, 1.0)    # holes for the wires from the XIAO's back pads
text("USB-C END ->", 45.0, 25.0, 1.0)
text("LEFT EAR", 8.6, 10.0, 1.0); text("RIGHT EAR", 49.2, 10.0, 1.0)
for side, x0 in (("L", 3.9), ("R", 42.65)):
    for n in range(8):                                                                   # pad numbers 1..8 (same numbers as the dangle board)
        row_a = n < 4; i = n % 4
        x = x0 + 2.7 * i + (0.0 if row_a else 1.35); y = 3.8 if row_a else 6.3
        text(str(n + 1), x, y - 1.5 if row_a else y + 1.5, 1.0)
for k, line in enumerate(("1 LRCLK 2 DIN 3 VBAT 4 DATA", "5 BCLK 6 GND 7 CLK 8 GND")):          # pad key (bottom silkscreen)
    text(line, 28, 8.0 + 1.2 * k, 1.0, layer=pcbnew.B_SilkS, mirror=True)
text("NECKLACE BOX CARRIER", 28, 12.0, 1.2, layer=pcbnew.B_SilkS, mirror=True)
def sig(x, y, h, layer, mirror=False):
    """signature: lowercase 'morgan' in a normal sans-serif TrueType font (Helvetica) instead of KiCad's stroke font"""
    t = pcbnew.PCB_TEXT(board); t.SetText("morgan"); t.SetLayer(layer); t.SetPosition(VECTOR2I(mm(x), mm(y)))
    t.SetTextSize(VECTOR2I(mm(h), mm(h))); t.SetTextThickness(mm(0.2)); t.SetMirrored(mirror); t.SetUnresolvedFontName("Helvetica"); board.Add(t)
sig(8.0, 24.6, 2.2, pcbnew.F_SilkS)                                           # top silk, free spot between the mounting hole and the JST battery socket
pcbnew.SaveBoard(os.path.join(OUT, "carrier_C_final.kicad_pcb"), board); print("saved")

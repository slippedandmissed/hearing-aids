"""Add silkscreen (L/R labels), then export Gerbers, drill, JLC BOM + CPL and renders. Run with KiCad's python: python3 finish.py L|R"""
import sys, os, csv, subprocess
import pcbnew
from pcbnew import FromMM as mm, ToMM as tomm, VECTOR2I
V = sys.argv[1]; HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out")
src = os.path.join(OUT, f"dangle_{V}_routed.kicad_pcb"); dst = os.path.join(OUT, f"dangle_{V}_final.kicad_pcb")
board = pcbew = pcbnew.LoadBoard(src)
W, H = 13.0, 28.0
seen = set(); vias_xy = []
for t in list(board.GetTracks()):                      # remove any exactly co-located duplicate vias
    if t.GetClass() == "PCB_VIA":
        k = (round(t.GetPosition().x / 20000), round(t.GetPosition().y / 20000))   # 20 um tolerance
        if k in seen: board.Remove(t)
        else: vias_xy.append((tomm(t.GetPosition().x), tomm(t.GetPosition().y)))
        seen.add(k)
WORD = "LEFT" if V == "L" else "RIGHT"
def text(s, x, y, h, layer, mirror=False, thick=0.17):
    t = pcbnew.PCB_TEXT(board); t.SetText(s); t.SetLayer(layer); t.SetPosition(VECTOR2I(mm(x), mm(y)))
    t.SetTextSize(VECTOR2I(mm(h), mm(h))); t.SetTextThickness(mm(thick)); t.SetMirrored(mirror); board.Add(t)
text(V, 6.5, 2.9, 1.8, pcbnew.F_SilkS, thick=0.17)                    # top (component side): big letter between the two exciter pads, clear of the resistors below
text(V, 6.5, 9.0, 7.0, pcbnew.B_SilkS, mirror=True, thick=0.5)        # bottom (faces the housing wall): very big letter
text(WORD + " EAR", 6.5, 21.8, 1.5, pcbnew.B_SilkS, mirror=True, thick=0.2)
# pad numbers (top silk) + key (bottom silk). Numbering matches the carrier board: 1 LRCLK 2 DIN 3 VBAT 4 PDM_DATA / 5 BCLK 6 GND 7 PDM_CLK 8 GND
for n, x in enumerate((1.9, 4.6, 7.3, 10.0), 1): text(str(n), x, 22.2, 0.9, pcbnew.F_SilkS)
for n, x in enumerate((3.25, 5.95, 8.65, 11.3), 5): text(str(n), x, 27.4, 0.8, pcbnew.F_SilkS)
def key_cost(y0):                                              # number of (via, key line) pairs closer than the fab's silkscreen-to-hole limit (0.18 mm + stroke + via radius)
    return sum(1 for (vx, vy) in vias_xy for k in range(4) if 1.0 <= vx <= 12.0 and abs(vy - (y0 + 1.15 * k)) < 0.45 + 0.35 + 0.2)
y0 = min((13.0 + 0.05 * i for i in range(0, 15)), key=lambda v: (key_cost(v), abs(v - 13.4)))   # the key (bottom silk) goes where the routing left it clear of vias; y0 13.0..13.7 (the last line must stay clear of the mic hole at y 18.19)
print("pad key at y0 =", round(y0, 2), "via/line conflicts:", key_cost(y0))
for k, line in enumerate(("1 LRCLK  2 DIN", "3 VBAT  4 DATA", "5 BCLK  6 GND", "7 CLK  8 GND")):
    text(line, 6.5, y0 + 1.15 * k, 0.9, pcbnew.B_SilkS, mirror=True, thick=0.17)
text("-", 3.5, 3.5, 1.2, pcbnew.B_SilkS, mirror=True, thick=0.25); text("+", 9.5, 3.5, 1.2, pcbnew.B_SilkS, mirror=True, thick=0.25)   # exciter pads (seen from the board's bottom)
def sig(x, y, h, layer, mirror=False):
    """signature: lowercase 'morgan' in a normal sans-serif TrueType font (Helvetica) instead of KiCad's stroke font"""
    t = pcbnew.PCB_TEXT(board); t.SetText("morgan"); t.SetLayer(layer); t.SetPosition(VECTOR2I(mm(x), mm(y)))
    t.SetTextSize(VECTOR2I(mm(h), mm(h))); t.SetTextThickness(mm(0.2)); t.SetMirrored(mirror); t.SetUnresolvedFontName("Helvetica"); board.Add(t)
sig(6.5, 19.6, 1.6, pcbnew.B_SilkS, True)                                  # bottom silk, between the pad key and 'LEFT/RIGHT EAR'
pcbnew.SaveBoard(dst, board)

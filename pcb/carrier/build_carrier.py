"""Necklace-box carrier PCB (XIAO socket + power + ear pads). KiCad python. usage: python3 build_carrier.py place
Board 56 x 40 mm, 2 layers, bottom = GND plane. SMD parts on top (JLC-assembled); THT parts hand-soldered."""
import sys, os, json, math
import pcbnew
from pcbnew import FromMM as mm, VECTOR2I
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out"); os.makedirs(OUT, exist_ok=True)
KFP = os.environ.get("KICAD_FOOTPRINTS", "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints" if sys.platform == "darwin" else "/usr/share/kicad/footprints")
W, H = 56.0, 40.0
board = pcbnew.BOARD(); nets = {}
def net(n):
    if n not in nets:
        x = pcbnew.NETINFO_ITEM(board, n); board.Add(x); nets[n] = x
    return nets[n]
LCSC = {}
def place(ref, lib, name, x, y, rot, padnets, value="", lcsc=None):
    path = lib if lib.startswith("/") else os.path.join(KFP, lib + ".pretty")
    fp = pcbnew.FootprintLoad(path, name); fp.SetReference(ref); fp.SetValue(value or name)
    fp.SetPosition(VECTOR2I(mm(x), mm(y))); fp.SetOrientationDegrees(rot)
    for p in fp.Pads():
        k = p.GetNumber()
        if padnets.get(k): p.SetNet(net(padnets[k]))
    fp.Reference().SetVisible(False); fp.Value().SetVisible(False); board.Add(fp)
    if lcsc: LCSC[ref] = (lcsc, value)
    return fp
# outline (rounded rect r=9)
r = 9.0                                   # big corner radius so the board fits the rounded bee thorax (cad/bee_box.py needs >= ~8.1)
def seg(x1, y1, x2, y2):
    s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetStart(VECTOR2I(mm(x1), mm(y1))); s.SetEnd(VECTOR2I(mm(x2), mm(y2))); s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(mm(0.1)); board.Add(s)
def arc(cx, cy, a0):
    s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_ARC); a = math.radians(a0)
    s.SetCenter(VECTOR2I(mm(cx), mm(cy))); s.SetStart(VECTOR2I(mm(cx + r * math.cos(a)), mm(cy + r * math.sin(a)))); s.SetArcAngleAndEnd(pcbnew.EDA_ANGLE(90, pcbnew.DEGREES_T)); s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(mm(0.1)); board.Add(s)
seg(r, 0, W - r, 0); seg(W, r, W, H - r); seg(W - r, H, r, H); seg(0, H - r, 0, r)
arc(W - r, r, -90); arc(W - r, H - r, 0); arc(r, H - r, 90); arc(r, r, 180)

X0, Y0 = 30.0, 21.0                                   # XIAO centre; USB-C end toward +x
SOCK = ("Connector_PinHeader_2.54mm", "PinHeader_1x07_P2.54mm_Vertical")     # XIAO male pins are soldered straight into these holes
none = {}
place("J_XT", *SOCK, X0 + 7.62, Y0 - 7.62, 270, {"5": "PDM_CLK", "6": "PDM_DATA"}, "XIAO pin row top (D0..D6)")
place("J_XB", *SOCK, X0 - 7.62, Y0 + 7.62, 90, {"2": "I2S_BCLK", "3": "I2S_LRCLK", "4": "I2S_DIN", "6": "GND"}, "XIAO pin row bottom (D7,D8,D9,D10,3V3,GND,5V)")
TPH = ("TestPoint", "TestPoint_THTPad_D1.5mm_Drill0.7mm")
place("W_BATP", *TPH, 16.6, 19.0, 0, {"1": "VBAT"}, "XIAO BAT+ wire")
place("W_BATN", *TPH, 16.6, 21.0, 0, {"1": "GND"}, "XIAO BAT- wire")
R06 = ("Resistor_SMD", "R_0603_1608Metric"); C06 = ("Capacitor_SMD", "C_0603_1608Metric"); C08 = ("Capacitor_SMD", "C_0805_2012Metric")
SIG = ["PDM_CLK", "PDM_DATA", "I2S_BCLK", "I2S_LRCLK", "I2S_DIN"]
ycol = [9.0, 10.8, 12.6, 14.4, 16.2]
for s_, y in zip(SIG, ycol):
    place(f"RL_{s_}", *R06, 16.0, y, 0, {"2": s_, "1": f"L_{s_}"}, "33R", "C23140")
    place(f"RR_{s_}", *R06, 44.0, y, 0, {"1": s_, "2": f"R_{s_}"}, "33R", "C23140")
for side, x0 in (("L", 3.9), ("R", 42.65)):                # ear blocks, same pad order as the dangle board
    order = [("A", 0, "I2S_LRCLK"), ("A", 1, "I2S_DIN"), ("A", 2, "VBAT"), ("A", 3, "PDM_DATA"), ("B", 0, "I2S_BCLK"), ("B", 1, "GND"), ("B", 2, "PDM_CLK"), ("B", 3, "GND")]
    for n, (row, i, nm) in enumerate(order, 1):
        x = x0 + 2.7 * i + (1.35 if row == "B" else 0.0); y = 3.8 if row == "A" else 6.3
        place(f"{side}{n}", *TPH, x, y, 0, {"1": nm if nm in ("VBAT", "GND") else f"{side}_{nm}"}, f"{side} ear pad {n}")
# power
place("J_BAT", "Connector_JST", "JST_PH_S2B-PH-K_1x02_P2.00mm_Horizontal", 11.0, 31.0, 270, {"1": "BATP", "2": "GND"}, "JST-PH battery", "C173752")   # plug enters from the LEFT edge
for ref, (hx, hy) in (("MH1", (2.6, 20.0)), ("MH2", (53.4, 20.0))): place(ref, "MountingHole", "MountingHole_2.2mm_M2", hx, hy, 0, {}, "M2 mounting hole")
place("Q1", "Package_TO_SOT_SMD", "SOT-23", float(os.environ.get("Q1X", 15.5)), 35.0, 0, {"1": "GND", "2": "PROT", "3": "BATP"}, "AO3401A", "C15127")
place("SW1", os.path.join(HERE, "lib", "sw.pretty"), "SW-TH_SK12D07VG4", 19.5, 3.8, 180, {"1": "SWOUT", "2": "PROT"}, "SK12D07VG4", "C393937")
place("F1", "Fuse", "Fuse_1206_3216Metric", 34.0, 35.0, 0, {"1": "SWOUT", "2": "VBAT"}, "500mA PTC", "C163512")
place("C_BULK", *C08, 41.0, 35.0, 0, {"1": "VBAT", "2": "GND"}, "22uF", "C45783")
place("C_BYP", *C06, 45.5, 35.0, 0, {"1": "VBAT", "2": "GND"}, "100nF", "C14663")
place("R_LED", *R06, 50.0, 32.0, 90, {"1": "VBAT", "2": "LEDA"}, "2.2k", "C4190")
place("D1", "LED_SMD", "LED_0603_1608Metric", 50.0, 36.0, 90, {"2": "LEDA", "1": "GND"}, "red LED", "C2286")
ds = board.GetDesignSettings(); ds.m_CopperEdgeClearance = mm(0.3); ds.m_HoleClearance = mm(0.2); ds.m_HoleToHoleMin = mm(0.25); ds.m_MinClearance = mm(0.2)
nc = ds.m_NetSettings.GetDefaultNetclass(); nc.SetTrackWidth(mm(0.25)); nc.SetClearance(mm(0.2)); nc.SetViaDiameter(mm(0.7)); nc.SetViaDrill(mm(0.3))
path = os.path.join(OUT, "carrier_C_placed.kicad_pcb"); pcbnew.SaveBoard(path, board)
sys.path.insert(0, os.path.join(HERE, "..")); import silk_strip     # drop the silkscreen outlines of everything but the three big connectors (JLCDFM: outlines sit 0.02-0.09 mm from pads, limit 0.18; the SMD parts are machine-placed; test-pad circles crowd the pad digits; the switch outline crosses the board edge)
print("silkscreen outlines removed:", silk_strip.strip_silk(path, skip_refs=("J_BAT", "J_XT", "J_XB")))
print("connector outline strokes widened to 0.17:", silk_strip.thicken_silk(path, ("J_BAT", "J_XT", "J_XB")))
json.dump(LCSC, open(os.path.join(OUT, "carrier_C_parts.json"), "w"))
tmp = pcbnew.LoadBoard(path)
for fp in tmp.GetFootprints():
    for p in fp.Pads():
        if p.GetNetname() == "GND": p.SetNetCode(0)
for t in list(tmp.GetTracks()): tmp.Remove(t)
pcbnew.ExportSpecctraDSN(tmp, os.path.join(OUT, "carrier_C.dsn")); print("placed + DSN", path)
for fp in board.GetFootprints():
    if fp.GetReference() in ("J_XT", "J_XB", "J_BAT", "SW1", "Q1"):
        print(fp.GetReference(), [(p.GetNumber(), round(pcbnew.ToMM(p.GetPosition().x), 2), round(pcbnew.ToMM(p.GetPosition().y), 2), p.GetNetname()) for p in fp.Pads()])

# ---- every pad / part must lie inside the rounded outline (inset 0.6 mm)
def inside(x, y, inset=0.6):
    cx = min(max(x, r), W - r); cy = min(max(y, r), H - r)
    return math.hypot(x - cx, y - cy) <= r - inset
bad = []
for fp in board.GetFootprints():
    bb = fp.GetBoundingBox(False, False)
    for (px, py) in ((bb.GetLeft(), bb.GetTop()), (bb.GetRight(), bb.GetTop()), (bb.GetLeft(), bb.GetBottom()), (bb.GetRight(), bb.GetBottom())):
        if not inside(pcbnew.ToMM(px), pcbnew.ToMM(py), 0.2): bad.append((fp.GetReference(), round(pcbnew.ToMM(px), 1), round(pcbnew.ToMM(py), 1)))
print("parts with a bounding-box corner outside the rounded outline:", sorted(set(b[0] for b in bad)))

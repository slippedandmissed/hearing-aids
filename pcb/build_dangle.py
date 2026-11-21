"""Generate the dangle PCB (mic + I2S amp + LDO) with KiCad's python. Run with KiCad's bundled python:
  KiCad python: build_dangle.py L|R place   -> out/dangle_<V>_placed.kicad_pcb + .dsn   (then pipeline.py runs Freerouting and the later steps)
Board: 11 x 24 mm, 2 layers. ALL parts on the TOP side (single-sided JLC assembly); bottom face = GND plane + bare, against the housing's front wall.
The mic is bottom-port: port hole (NPTH) goes through the board, aligned with the housing's sound hole (gasket on the bottom face)."""
import sys, os, math
import pcbnew
from pcbnew import FromMM as mm, VECTOR2I

VARIANT = sys.argv[1]; STAGE = sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out"); os.makedirs(OUT, exist_ok=True)
KFP = os.environ.get("KICAD_FOOTPRINTS", "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints")
W, H = 13.0, 28.0

def fp_load(lib, name):
    path = lib if lib.startswith("/") else os.path.join(KFP, lib + ".pretty")
    return pcbnew.FootprintLoad(path, name)

board = pcbnew.BOARD()
nets = {}
def net(name):
    if name not in nets:
        n = pcbnew.NETINFO_ITEM(board, name); board.Add(n); nets[name] = n
    return nets[name]

def place(ref, lib, name, x, y, rot, padnets, value=""):
    fp = fp_load(lib, name); fp.SetReference(ref); fp.SetValue(value or name)
    fp.SetPosition(VECTOR2I(mm(x), mm(y))); fp.SetOrientationDegrees(rot)
    for p in fp.Pads():
        k = p.GetNumber()
        if k in padnets and padnets[k]: p.SetNet(net(padnets[k]))
    fp.Reference().SetVisible(False); fp.Value().SetVisible(False)
    board.Add(fp); return fp

# ---------- outline (rounded rectangle, 1 mm radius)
def edge(shape_fn):
    s = shape_fn(); s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(mm(0.1)); board.Add(s)
r = 1.0
def seg(x1, y1, x2, y2):
    def f():
        s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetStart(VECTOR2I(mm(x1), mm(y1))); s.SetEnd(VECTOR2I(mm(x2), mm(y2))); return s
    edge(f)
def arc(cx, cy, a0):
    def f():
        s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_ARC)
        a = math.radians(a0); b = math.radians(a0 + 90)
        s.SetCenter(VECTOR2I(mm(cx), mm(cy))); s.SetStart(VECTOR2I(mm(cx + r * math.cos(a)), mm(cy + r * math.sin(a)))); s.SetArcAngleAndEnd(pcbnew.EDA_ANGLE(90, pcbnew.DEGREES_T)); return s
    edge(f)
seg(r, 0, W - r, 0); seg(W, r, W, H - r); seg(W - r, H, r, H); seg(0, H - r, 0, r)
arc(W - r, r, -90); arc(W - r, H - r, 0); arc(r, H - r, 90); arc(r, r, 180)

LEFT = VARIANT == "L"
LCSC = {}                                            # ref -> (LCSC part number, value) for the JLC BOM
def P(ref, lib, name, x, y, rot, padnets, value, lcsc):
    LCSC[ref] = (lcsc, value); return place(ref, lib, name, x, y, rot, padnets, value)
PL = os.path.join(HERE, "lib", "parts.pretty")
R06 = ("Resistor_SMD", "R_0603_1608Metric"); C06 = ("Capacitor_SMD", "C_0603_1608Metric"); C08 = ("Capacitor_SMD", "C_0805_2012Metric"); R12 = ("Resistor_SMD", "R_1206_3216Metric")
TPH = ("TestPoint", "TestPoint_THTPad_D1.5mm_Drill0.7mm")
MIC = (3.9, 19.0)                                    # mic centre, rotated 180: pads face the cable end, port ring faces up
P("U1", PL, "TQFN-16_L3.0-W3.0-P0.50-BL-EP1.5", 6.5, 9.8, 0,
  {"1": "I2S_DIN", "2": "GAIN", "3": "GND", "4": "SDM", "7": "VBAT", "8": "VBAT", "9": "OUTP", "10": "OUTN", "11": "GND", "14": "I2S_LRCLK", "15": "GND", "16": "I2S_BCLK", "17": "GND"}, "MAX98357AETE+T", "C910544")
P("U2", PL, "MIC-SMD_5P_L3.5-W2.7-P0.82_SPH0641LU4H-1", MIC[0], MIC[1], 180, {"1": "PDM_DATA", "2": "GND" if LEFT else "V3V3", "3": "GND", "4": "PDM_CLK", "5": "V3V3"}, "SPH0641LM4H-1", "C497724")   # SELECT strapped directly: GND = left, 3V3 = right
P("U3", PL, "SOT-23-3_L2.9-W1.6-P1.90-LS2.8-BR", 10.2, 18.6, 0, {"1": "GND", "2": "V3V3", "3": "VBAT"}, "XC6206P332MR-G", "C5446")
P("R_OUT1", *R12, 9.5, 5.4, 0, {"1": "OUTP", "2": "EXCP"}, "22R 1206", "C17958")
P("R_OUT2", *R12, 3.5, 5.4, 0, {"1": "OUTN", "2": "EXCN"}, "22R 1206", "C17958")
P("C2", *C06, 10.3, 8.4, 0, {"1": "VBAT", "2": "GND"}, "100nF", "C14663")
P("C1", *C08, 10.6, 10.6, 0, {"1": "VBAT", "2": "GND"}, "10uF", "C15850")
P("R_GAIN", *R06, 5.6, 13.6, 90, {"1": "VBAT", "2": "GAIN"}, "100k", "C25803")
P("R_SD", *R06, 8.2, 13.6, 90, {"1": "V3V3", "2": "SDM"}, "2k" if LEFT else "220k", "C22975" if LEFT else "C22961")
P("C3", *C06, float(os.environ.get("C3X", 8.0)), float(os.environ.get("C3Y", 20.8)), 0, {"1": "VBAT", "2": "GND"}, "1uF", "C15849")
P("C4", *C06, 11.9, 16.3, 90, {"1": "V3V3", "2": "GND"}, "1uF", "C15849")
P("C5", *C06, float(os.environ.get("C5X", 1.7)), float(os.environ.get("C5Y", 11.0)), 90, {"1": "V3V3", "2": "GND"}, "100nF", "C14663")
for ref, (x, y), nm in (("J_EXC_N", (3.5, 1.4), "EXCN"), ("J_EXC_P", (9.5, 1.4), "EXCP")):
    place(ref, *TPH, x, y, 0, {"1": nm}, ref)
cable = [("J1", 1.9, 23.8, "I2S_LRCLK"), ("J2", 4.6, 23.8, "I2S_DIN"), ("J3", 7.3, 23.8, "VBAT"), ("J4", 10.0, 23.8, "PDM_DATA"),
         ("J5", 3.25, 25.9, "I2S_BCLK"), ("J6", 5.95, 25.9, "GND"), ("J7", 8.65, 25.9, "PDM_CLK"), ("J8", 11.3, 25.9, "GND")]
for ref, x, y, nm in cable: place(ref, *TPH, x, y, 0, {"1": nm}, ref)
# the mic footprint carries its own 0.5 mm acoustic-port hole pad: make it a proper non-plated hole
for p in board.FindFootprintByReference("U2").Pads():
    if p.GetNumber() == "":
        p.SetAttribute(pcbnew.PAD_ATTRIB_NPTH); ls = pcbnew.LSET(); ls.AddLayer(pcbnew.F_Mask); ls.AddLayer(pcbnew.B_Mask); p.SetLayerSet(ls)

# net classes / design rules
ds = board.GetDesignSettings()
ds.m_CopperEdgeClearance = mm(0.3); ds.m_HoleClearance = mm(0.2); ds.m_HoleToHoleMin = mm(0.25)
ds.m_TrackMinWidth = mm(0.127); ds.m_MinClearance = mm(0.2); ds.m_ViasMinSize = mm(0.5); ds.m_ViasMinDrill = mm(0.3)
nc = ds.m_NetSettings.GetDefaultNetclass(); nc.SetTrackWidth(mm(0.2)); nc.SetClearance(mm(0.2)); nc.SetViaDiameter(mm(0.7)); nc.SetViaDrill(mm(0.3))

if STAGE == "place":
    import json; json.dump(LCSC, open(os.path.join(OUT, f"dangle_{VARIANT}_parts.json"), "w"))
    path = os.path.join(OUT, f"dangle_{VARIANT}_placed.kicad_pcb"); pcbnew.SaveBoard(path, board)
    sys.path.insert(0, HERE); import silk_strip; print("silkscreen outlines removed:", silk_strip.strip_silk(path))   # JLCPCB's checker flags the outlines 0.02-0.09 mm from pads (limit 0.18); parts are machine-placed; test-pad circles crowd the pad digits
    tmp = pcbnew.LoadBoard(path)                       # router copy: GND pads carry no net (obstacles only), ring-bridge tracks removed
    for fp in tmp.GetFootprints():
        for p in fp.Pads():
            if p.GetNetname() == "GND": p.SetNetCode(0)
    for t in list(tmp.GetTracks()): tmp.Remove(t)
    # the mic's ground-ring bridge tracks (import_ses.py) are added after routing: keep the router out of their footprint (0.8 mm around the port hole, + 0.1 mm)
    hx, hy = MIC[0], MIC[0] * 0 + 18.19
    for fp in tmp.GetFootprints():
        for p in fp.Pads():
            if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH and fp.GetReference() == "U2": hx, hy = pcbnew.ToMM(p.GetPosition().x), pcbnew.ToMM(p.GetPosition().y)
    z = pcbnew.ZONE(tmp); z.SetIsRuleArea(True); z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(True); z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False); z.SetDoNotAllowZoneFills(False)
    ls_ = pcbnew.LSET(); ls_.AddLayer(pcbnew.F_Cu); z.SetLayerSet(ls_); z.SetZoneName("mic_ring_keepout")
    o = z.Outline(); o.NewOutline()
    for (kx, ky) in ((hx - 0.9, hy - 0.9), (hx + 0.9, hy - 0.9), (hx + 0.9, hy + 0.54), (hx - 0.9, hy + 0.54)): o.Append(mm(kx), mm(ky))
    tmp.Add(z)
    import silk_zones                                   # no vias under the bottom silkscreen text (tracks are fine)
    for k, (x0, y0, x1, y1) in enumerate(silk_zones.BOTTOM_SILK_NO_VIA):
        zz = pcbnew.ZONE(tmp); zz.SetIsRuleArea(True); zz.SetDoNotAllowTracks(False); zz.SetDoNotAllowVias(True); zz.SetDoNotAllowPads(False); zz.SetDoNotAllowFootprints(False); zz.SetDoNotAllowZoneFills(False)
        lz = pcbnew.LSET(); lz.AddLayer(pcbnew.F_Cu); lz.AddLayer(pcbnew.B_Cu); zz.SetLayerSet(lz); zz.SetZoneName(f"silk_novia_{k}")
        oo = zz.Outline(); oo.NewOutline()
        for (kx, ky) in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)): oo.Append(mm(kx), mm(ky))
        tmp.Add(zz)
    pcbnew.ExportSpecctraDSN(tmp, os.path.join(OUT, f"dangle_{VARIANT}.dsn")); print("placed + DSN", path)

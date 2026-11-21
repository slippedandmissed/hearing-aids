"""Ground via + bottom ground plane step (pure python grid router, no third-party binaries). KiCad python.
Freerouting routes every signal; this step then drops a via from each ground pad to the bottom layer and pours the bottom GND plane.
  python3 ground_plane.py <variant>      env: OUTDIR (default pcb/out), PREFIX (dangle|carrier), INPUT (default <PREFIX>_<variant>_placed.kicad_pcb), BW/BH board size in mm
Reads INPUT, writes <PREFIX>_<variant>_routed.kicad_pcb + .kicad_pro (design rules).  Grid 0.05 mm, tracks 0.2, clearance 0.2, vias 0.6/0.3."""
import sys, os, heapq, math
import pcbnew
from pcbnew import FromMM as mm, ToMM as tomm, VECTOR2I

V = sys.argv[1]; HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.environ.get("OUTDIR", os.path.join(HERE, "out")); PREFIX = os.environ.get("PREFIX", "dangle")
board = pcbnew.LoadBoard(os.path.join(OUT, os.environ.get("INPUT", f"{PREFIX}_{V}_placed.kicad_pcb")))
RES, TW, CL, VD, VDR = 0.05, 0.2, 0.2, 0.7, 0.3     # vias 0.7/0.3: 0.2 mm annular ring (JLCDFM calls 0.15 mm a warning)
VIA_PAD_GAP = 0.2                                     # copper gap between a via and any SMD pad (no via-in-pad: solder wicks down it)
EDGE_CL = 0.3
W, H = float(os.environ.get('BW', 13.0)), float(os.environ.get('BH', 28.0))
NX, NY = int(round(W / RES)) + 1, int(round(H / RES)) + 1
def cell(v): return int(round(v / RES))
zt = [dict(), dict()]        # per layer: cell -> set(net codes) ; obstacles for TRACK centres
zv = [dict(), dict()]        # obstacles for VIA centres
BLOCK = -1
def add_rect(z, layer, net, x0, y0, x1, y1, infl):
    for i in range(max(0, cell(x0 - infl)), min(NX - 1, cell(x1 + infl)) + 1):
        for j in range(max(0, cell(y0 - infl)), min(NY - 1, cell(y1 + infl)) + 1):
            z[layer].setdefault((i, j), set()).add(net)
def add_item(net, layers, x0, y0, x1, y1, hw_self_t=TW / 2, hw_self_v=VD / 2):
    for l in layers:
        add_rect(zt, l, net, x0, y0, x1, y1, CL + hw_self_t)
        add_rect(zv, l, net, x0, y0, x1, y1, CL + hw_self_v)
# --- edge keep-out
for i in range(NX):
    for j in range(NY):
        x, y = i * RES, j * RES
        d = min(x, W - x, y, H - y)
        for l in (0, 1):
            if d < EDGE_CL + TW / 2: zt[l].setdefault((i, j), set()).add(BLOCK)
            if d < EDGE_CL + VD / 2: zv[l].setdefault((i, j), set()).add(BLOCK)
# --- pads
netnames = {n.GetNetCode(): n.GetNetname() for n in board.GetNetInfo().NetsByNetcode().values()} if hasattr(board.GetNetInfo(), "NetsByNetcode") else {}
pads = {}                              # net code -> list of (layers, bbox, pad)
for fp in board.GetFootprints():
    for p in fp.Pads():
        bb = p.GetBoundingBox(); x0, y0, x1, y1 = tomm(bb.GetX()), tomm(bb.GetY()), tomm(bb.GetX() + bb.GetWidth()), tomm(bb.GetY() + bb.GetHeight())
        net = p.GetNetCode() if p.GetNetCode() > 0 else None
        thru = p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH)
        layers = (0, 1) if thru else (0,)
        if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
            r = tomm(p.GetDrillSize().x) / 2; cx, cy = tomm(p.GetPosition().x), tomm(p.GetPosition().y)
            add_item(BLOCK, (0, 1), cx - r - 0.2, cy - r - 0.2, cx + r + 0.2, cy + r + 0.2); continue
        add_item(net if net else BLOCK, layers, x0, y0, x1, y1)
        if net: pads.setdefault(net, []).append((layers, (x0, y0, x1, y1), p))
def blocked(z, l, i, j, net):
    s = z[l].get((i, j))
    return bool(s) and any(c != net for c in s)
def pad_cells(layers, bb, p):
    out = set()
    for l in layers:
        for i in range(cell(bb[0]), cell(bb[2]) + 1):
            for j in range(cell(bb[1]), cell(bb[3]) + 1):
                if not (0 <= i < NX and 0 <= j < NY): continue
                if all(p.HitTest(VECTOR2I(mm(i * RES + dx), mm(j * RES + dy))) for dx, dy in ((0, 0), (0.06, 0), (-0.06, 0), (0, 0.06), (0, -0.06))): out.add((i, j, l))
        if not out: # tiny pads: fall back to the centre cell
            c = p.GetPosition(); out.add((cell(tomm(c.x)), cell(tomm(c.y)), l))
    return out
def route_pair(net, tree, src, goal_layer=None):
    """Dijkstra from src cells to any cell in tree. Returns list of (i,j,l) path from src to tree, or None."""
    pq = []; best = {}; prev = {}
    for s in src: best[s] = 0; heapq.heappush(pq, (0, s))
    while pq:
        cst, cur = heapq.heappop(pq)
        if cst > best.get(cur, 1e18): continue
        if cur in tree or (goal_layer is not None and cur[2] == goal_layer and cur not in src):
            path = [cur]
            while cur in prev: cur = prev[cur]; path.append(cur)
            return path[::-1]
        i, j, l = cur
        for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ni, nj = i + di, j + dj
            if not (0 <= ni < NX and 0 <= nj < NY): continue
            nxt = (ni, nj, l)
            if blocked(zt, l, ni, nj, net) and nxt not in tree and nxt not in src: continue
            c = cst + 1 * (3.0 if l == 1 and goal_layer is None else 1.0) + (0.05 if prev.get(cur) and (prev[cur][0] - i, prev[cur][1] - j) != (-di, -dj) else 0)
            if c < best.get(nxt, 1e18): best[nxt] = c; prev[nxt] = cur; heapq.heappush(pq, (c, nxt))
        nl = 1 - l
        nxt = (i, j, nl)
        if not blocked(zv, 0, i, j, net) and not blocked(zv, 1, i, j, net) and not blocked(zt, nl, i, j, net) and via_ok(i, j):
            c = cst + 25
            if c < best.get(nxt, 1e18): best[nxt] = c; prev[nxt] = cur; heapq.heappush(pq, (c, nxt))
    return None
tracks, vias = [], []
smd_boxes = []
for fp in board.GetFootprints():
    for p in fp.Pads():
        if p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD and not (fp.GetReference() == "U1" and p.GetNumber() == "17"):
            bb = p.GetBoundingBox(); m = VD / 2 + VIA_PAD_GAP; smd_boxes.append((tomm(bb.GetX()) - m, tomm(bb.GetY()) - m, tomm(bb.GetX() + bb.GetWidth()) + m, tomm(bb.GetY() + bb.GetHeight()) + m))
def via_ok(i, j):
    x, y = i * RES, j * RES
    if any(math.hypot(x - vx, y - vy) < 0.8 for _, vx, vy in vias): return False
    return not any(b[0] <= x <= b[2] and b[1] <= y <= b[3] for b in smd_boxes)
def commit(net, path):
    for (i, j, l) in path:
        x, y = i * RES, j * RES
        add_item(net, (l,), x - TW / 2, y - TW / 2, x + TW / 2, y + TW / 2)
    for a, b in zip(path, path[1:]):
        if a[2] != b[2]:
            x, y = a[0] * RES, a[1] * RES; vias.append((net, x, y))
            add_item(net, (0, 1), x - VD / 2, y - VD / 2, x + VD / 2, y + VD / 2)
        else: tracks.append((net, a, b))
code = {n.GetNetname(): n.GetNetCode() for n in board.GetNetInfo().NetsByNetcode().values()}
def add_seg(net, layers, x1, y1, x2, y2, hw=0.1):
    n = max(1, int(math.hypot(x2 - x1, y2 - y1) / 0.05))
    for k in range(n + 1):
        x = x1 + (x2 - x1) * k / n; y = y1 + (y2 - y1) * k / n
        add_item(net, layers, x - hw, y - hw, x + hw, y + hw)
for t in board.GetTracks():                      # copper already on the board (Freerouting result, ring bridges): obstacles
    net = t.GetNetCode()
    if t.GetClass() == "PCB_VIA":
        t.SetWidth(mm(VD)); x, y = tomm(t.GetPosition().x), tomm(t.GetPosition().y); add_item(net, (0, 1), x - VD / 2, y - VD / 2, x + VD / 2, y + VD / 2, 0.1, VD / 2); vias.append((net, x, y))
    else:
        add_seg(net, (0 if t.GetLayer() == pcbnew.F_Cu else 1,), tomm(t.GetStart().x), tomm(t.GetStart().y), tomm(t.GetEnd().x), tomm(t.GetEnd().y), hw=max(0.1, tomm(t.GetWidth()) / 2))
fail = []
for name in ("GND",):
    net = code.get(name)
    if not net or net not in pads: continue
    plist = pads[net]
    if name == "GND":                                   # each GND pad drops a via to the bottom ground plane
        okc = 0; ring_ok = False
        for pd in plist:
            if pd[2].GetParentFootprint().GetReference() == "U1" and pd[2].GetNumber() in ("3", "11", "15"): okc += 1; continue   # tied to the exposed pad
            ring = pd[2].GetParentFootprint().GetReference() == "U2" and pd[2].GetNumber() == "3"
            if ring and ring_ok: okc += 1; continue                       # ring segments are bridged: one connection is enough
            src = pad_cells(*pd)
            if any(c[2] == 1 for c in src): okc += 1; continue          # through-hole pad already reaches the plane
            path = route_pair(net, set(), src, goal_layer=1)
            if path: commit(net, path); okc += 1; ring_ok = ring_ok or ring
            elif not ring: fail.append("GND pad")
        print("GND", okc, "of", len(plist), "pads reach the plane"); continue
# --- write tracks (merge straight runs) and vias
def merge(segs):
    out = []
    for net, a, b in segs:
        out.append([net, a, b])
    # merge consecutive collinear segments on the same net/layer
    merged = []
    for s in out:
        if merged and merged[-1][0] == s[0] and merged[-1][2] == s[1] and merged[-1][1][2] == s[1][2]:
            m = merged[-1]; d1 = (m[2][0] - m[1][0], m[2][1] - m[1][1]); d2 = (s[2][0] - s[1][0], s[2][1] - s[1][1])
            sgn = lambda v: (v > 0) - (v < 0)
            if (sgn(d1[0]), sgn(d1[1])) == (sgn(d2[0]), sgn(d2[1])): m[2] = s[2]; continue
        merged.append(s)
    return merged
for net, a, b in merge(tracks):
    t = pcbnew.PCB_TRACK(board); t.SetStart(VECTOR2I(mm(a[0] * RES), mm(a[1] * RES))); t.SetEnd(VECTOR2I(mm(b[0] * RES), mm(b[1] * RES)))
    t.SetWidth(mm(TW)); t.SetLayer(pcbnew.F_Cu if a[2] == 0 else pcbnew.B_Cu); t.SetNetCode(net); board.Add(t)
for net, x, y in vias:
    v = pcbnew.PCB_VIA(board); v.SetPosition(VECTOR2I(mm(x), mm(y))); v.SetWidth(mm(VD)); v.SetDrill(mm(VDR)); v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v.SetNetCode(net); board.Add(v)
z = pcbnew.ZONE(board); z.SetLayer(pcbnew.B_Cu); z.SetNetCode(code["GND"]); z.SetMinThickness(mm(0.2)); z.SetLocalClearance(mm(CL))
ol = z.Outline(); ol.NewOutline()
for (px, py) in ((0.3, 0.3), (W - 0.3, 0.3), (W - 0.3, H - 0.3), (0.3, H - 0.3)): ol.Append(mm(px), mm(py))
board.Add(z)
pcbnew.ZONE_FILLER(board).Fill(board.Zones())
pcbnew.SaveBoard(os.path.join(OUT, f"{PREFIX}_{V}_routed.kicad_pcb"), board)
import json
rules = {"board": {"design_settings": {"rules": {"min_clearance": 0.2, "min_copper_edge_clearance": 0.2, "min_hole_clearance": 0.2, "min_hole_to_hole": 0.25,
         "min_track_width": 0.15, "min_via_diameter": 0.5, "min_through_hole_diameter": 0.3, "min_via_annular_width": 0.15, "min_resolved_spokes": 2, "min_silk_clearance": 0.0, "min_text_height": 0.8, "min_text_thickness": 0.08}}}, "meta": {"filename": f"{PREFIX}_{V}_routed.kicad_pro", "version": 3}}
json.dump(rules, open(os.path.join(OUT, f"{PREFIX}_{V}_routed.kicad_pro"), "w"), indent=2)
print("failed nets:", fail, "tracks", len(tracks), "vias", len(vias))

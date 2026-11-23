"""Check the hand-drawn circuit diagrams (docs/assets/circuit-*.svg) against the real routed boards, so a diagram cannot drift from the design.

Every drawn part carries metadata:  data-board="dangle_L|dangle_R|carrier_C"  data-ref="R_OUT1"  data-value="22 Ω"  data-pins="1=OUTP,2=EXCP"
(pin = the board's pad number, net = the board's net name; the diagram's visible labels may be friendlier). Checked against pcb/*/out/*_nets.json (made by pcb/dump_nets.py)
and *_parts.json: values numerically, pins exactly (resistors and capacitors may have their two pads swapped), and every part with a connected pad must be drawn.
The parts that differ between the LEFT and RIGHT earring boards must be drawn for dangle_R.   uv run python docs/check_circuits.py"""
import glob, json, os, re, sys
import xml.etree.ElementTree as ET
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREFIX = {"dangle_L": "pcb/out/dangle_L", "dangle_R": "pcb/out/dangle_R", "carrier_C": "pcb/carrier/out/carrier_C"}
UNITS = {"p": 1e-12, "n": 1e-9, "u": 1e-6, "µ": 1e-6, "m": 1e-3, "k": 1e3, "M": 1e6, "": 1.0}
def num(s):
    m = re.match(r"\s*([\d.]+)\s*([pnuµmkM]?)", s); return float(m.group(1)) * UNITS[m.group(2)]
def load(board):
    nets = json.load(open(os.path.join(ROOT, PREFIX[board] + "_nets.json"))); parts = json.load(open(os.path.join(ROOT, PREFIX[board] + "_parts.json")))
    conn = {r: {p: n for p, n in pins.items() if n} for r, pins in nets.items()}
    return {r: c for r, c in conn.items() if c}, {r: v[1] for r, v in parts.items()}     # parts with no connected pad (mounting holes) are not circuit parts
def pinmap(s): return dict(kv.split("=", 1) for kv in s.split(",") if kv.strip())

errors, seen = [], {b: set() for b in PREFIX}
data = {b: load(b) for b in PREFIX}
svgs = sorted(glob.glob(os.path.join(ROOT, "docs", "assets", "circuit-*.svg")))
for path in svgs:
    name = os.path.basename(path)
    for el in ET.parse(path).getroot().iter():
        ref = el.attrib.get("data-ref")
        if ref is None: continue
        board = el.attrib.get("data-board", "")
        if board not in PREFIX: errors.append(f"{name}: {ref}: data-board '{board}' is not one of {sorted(PREFIX)}"); continue
        nets, vals = data[board]; seen[board].add(ref)
        if ref not in nets: errors.append(f"{name}: {ref} is not a connected part of {board}"); continue
        want = nets[ref]; got = pinmap(el.attrib.get("data-pins", ""))
        if ref[0] in "RC" and len(want) == 2:
            if sorted(want.values()) != sorted(got.values()): errors.append(f"{name}: {ref} ({board}) is wired {sorted(got.values())}, the board has {sorted(want.values())}")
        elif got != want: errors.append(f"{name}: {ref} ({board}) pins {got}, the board has {want}")
        v = el.attrib.get("data-value")
        if v is not None and ref in vals:
            if ref[0] in "RC" and ref not in ("RL", "RR") and re.match(r"\s*[\d.]", vals[ref]):
                if abs(num(v) - num(vals[ref])) > 1e-9 * max(1, abs(num(vals[ref]))): errors.append(f"{name}: {ref} ({board}) is drawn as {v}, the board has {vals[ref]}")
            elif v.lower() not in vals[ref].lower() and vals[ref].lower() not in v.lower(): errors.append(f"{name}: {ref} ({board}) is drawn as {v}, the board has {vals[ref]}")
        elif v is not None and ref[0] in "RC": errors.append(f"{name}: {ref} ({board}) has a drawn value but no value on the board")
for board in ("dangle_L", "carrier_C"):                                         # every connected part must be drawn
    for ref in sorted(set(data[board][0]) - seen[board]): errors.append(f"{board}: {ref} is on the board but not drawn in any circuit diagram")
nl, vl = data["dangle_L"]; nr, vr = data["dangle_R"]                              # the right-hand variant: whatever differs must be drawn for it
for ref in sorted(set(nl) | set(nr)):
    if (nl.get(ref) != nr.get(ref) or vl.get(ref) != vr.get(ref)) and ref not in seen["dangle_R"]: errors.append(f"dangle_R: {ref} differs from dangle_L but is not drawn for dangle_R")
if errors: print("\n".join(errors)); sys.exit(f"{len(errors)} circuit diagram mismatch(es)")
print(f"circuit diagrams: {len(svgs)} SVG(s), {sum(len(s) for s in seen.values())} parts checked, all match the boards")

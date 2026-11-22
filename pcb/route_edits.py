"""Persisted hand edits on top of a Freerouting result.

Freerouting's result is committed as a lock (pcb/routes/<board>.ses) and re-used while the placement is unchanged. Small fixes to it (move a via off a
silkscreen line, delete or add a track) must not mean a new router run, because every run is a dice roll. They live in pcb/routes/<board>.edits.json
and are applied by the pipeline to the board imported from the lock, before the ground plane and the finish steps:

  {"placement_sha256": "<the fingerprint the edits were made for>",
   "edits": [ {"op": "move_via",     "from": [x, y], "to": [x, y]},                    # the via only; tracks that ended on it are edited explicitly
              {"op": "delete_via",   "at": [x, y]},
              {"op": "delete_track", "from": [x1, y1], "to": [x2, y2], "layer": "B.Cu"},   # either direction
              {"op": "add_track",    "points": [[x, y], [x, y], ...], "layer": "F.Cu", "net": "GND", "width": 0.25} ]}

Each edit may carry "stage": "ses" (default: the board imported from the lock, before the ground plane) or "ground" (the board after the ground-plane step, whose
vias and stubs are generated, so edits to them must come after it; they are deterministic too). The pipeline calls this once per stage.
Coordinates are KiCad board millimetres (y down, as in the .kicad_pcb file); items are matched within 0.01 mm and an edit that matches nothing is an error.
The edits only apply while the file's fingerprint equals the current placement's; otherwise the pipeline skips them with a warning (the routing they patched is gone).
Done on the file text (pure Python, no pcbnew), like silk_strip.py.
Usage: python3 route_edits.py <board.kicad_pcb> <edits.json> <current placement fingerprint>"""
import json, re, sys, uuid

TOL = 0.01

def _blocks(text, kind):
    for m in re.finditer(r"\n\t\(%s\b" % kind, text):
        d = 0; i = m.start() + 1
        while True:
            c = text[i]
            if c == "(": d += 1
            elif c == ")":
                d -= 1
                if d == 0: break
            elif c == '"':
                i += 1
                while text[i] != '"': i += 2 if text[i] == "\\" else 1
            i += 1
        yield m.start() + 1, i + 1

def _near(a, b): return abs(a[0] - b[0]) <= TOL and abs(a[1] - b[1]) <= TOL

def _xy(blk, key):
    m = re.search(r"\(%s ([\d.\-]+) ([\d.\-]+)\)" % key, blk)
    return (float(m.group(1)), float(m.group(2))) if m else None

def _find(text, kind, pred):
    return [(b, e) for b, e in _blocks(text, kind) if pred(text[b:e])]

def apply(path, edits):
    text = open(path).read()
    for k, ed in enumerate(edits):
        op = ed["op"]
        if op in ("move_via", "delete_via"):
            at = tuple(ed["from"] if op == "move_via" else ed["at"])
            hit = _find(text, "via", lambda b: _near(_xy(b, "at"), at))
            if not hit: sys.exit(f"route edit {k} ({op}): no via at {at}")
            for b, e in reversed(hit):
                if op == "delete_via": text = text[:b].rstrip("\t") + text[e:]
                else: text = text[:b] + re.sub(r"\(at [\d.\-]+ [\d.\-]+\)", "(at %.4f %.4f)" % tuple(ed["to"]), text[b:e], count=1) + text[e:]
            if op == "move_via" and ed.get("drag"):
                for b, e in reversed(_find(text, "segment", lambda blk: _near(_xy(blk, "start"), at) or _near(_xy(blk, "end"), at))):
                    blk = text[b:e]
                    for key in ("start", "end"):
                        if _near(_xy(blk, key), at): blk = re.sub(r"\(%s [\d.\-]+ [\d.\-]+\)" % key, "(%s %.4f %.4f)" % ((key,) + tuple(ed["to"])), blk, count=1)
                    text = text[:b] + blk + text[e:]
        elif op == "delete_track":
            a, z, ly = tuple(ed["from"]), tuple(ed["to"]), ed.get("layer")
            def pred(b):
                s, e_ = _xy(b, "start"), _xy(b, "end")
                return ((_near(s, a) and _near(e_, z)) or (_near(s, z) and _near(e_, a))) and (ly is None or f'(layer "{ly}")' in b)
            hit = _find(text, "segment", pred)
            if not hit: sys.exit(f"route edit {k} (delete_track): no track {a} - {z} on {ly}")
            for b, e in reversed(hit): text = text[:b].rstrip("\t") + text[e:]
        elif op == "add_track":
            pts = ed["points"]; new = ""
            for p, q in zip(pts, pts[1:]):
                new += ('\t(segment\n\t\t(start %.4f %.4f)\n\t\t(end %.4f %.4f)\n\t\t(width %g)\n\t\t(layer "%s")\n\t\t(net "%s")\n\t\t(uuid "%s")\n\t)\n'
                        % (p[0], p[1], q[0], q[1], ed.get("width", 0.25), ed["layer"], ed["net"], uuid.uuid4()))
            i = text.rstrip().rfind(")")                       # before the closing paren of (kicad_pcb ...)
            text = text[:i] + new + text[i:]
        else: sys.exit(f"route edit {k}: unknown op {op}")
    open(path, "w").write(text); return len(edits)

if __name__ == "__main__":
    path, ej, fp = sys.argv[1:4]; stage = sys.argv[4] if len(sys.argv) > 4 else "ses"
    d = json.load(open(ej)); mine = [e for e in d["edits"] if e.get("stage", "ses") == stage]
    if not mine: pass
    elif d.get("placement_sha256") != fp: print(f"   WARNING: {ej} was made for another placement: {stage}-stage edits NOT applied (re-make them for the new routing)")
    else: print(f"   route edits applied ({stage} stage): {apply(path, mine)} ({ej})")

"""Remove silkscreen drawings (fp_line / fp_rect / fp_circle / fp_arc / fp_poly on F.SilkS or B.SilkS) from footprints in a .kicad_pcb file.
Done on the file text because KiCad's python returns bare SWIG objects for some library footprints (cannot be iterated).
  strip_silk(path, only_refs=None, skip_refs=())   only_refs: strip these footprints only (default: all);  skip_refs: leave these alone."""
import re

def _blocks(text, start, kinds):
    """yield (begin, end) of every top-level s-expression starting with '(kind' inside text[start:]"""
    for m in re.finditer(r"\((?:%s)\b" % "|".join(kinds), text):
        depth = 0; i = m.start()
        while True:
            c = text[i]
            if c == "(": depth += 1
            elif c == ")":
                depth -= 1
                if depth == 0: yield m.start(), i + 1; break
            elif c == '"':
                i += 1
                while text[i] != '"': i += 2 if text[i] == "\\" else 1
            i += 1

def strip_silk(path, only_refs=None, skip_refs=()):
    text = open(path).read(); out = []; pos = 0; removed = 0
    for b, e in _blocks(text, 0, ("footprint",)):
        fp = text[b:e]; ref = re.search(r'\(property "Reference" "([^"]*)"', fp)
        ref = ref.group(1) if ref else ""
        if (only_refs is not None and ref not in only_refs) or ref in skip_refs: continue
        new = fp; cuts = []
        for fb, fe in _blocks(fp, 0, ("fp_line", "fp_rect", "fp_circle", "fp_arc", "fp_poly", "fp_curve")):
            if re.search(r'\(layer "[FB]\.Silk(?:S|screen)"\)', fp[fb:fe]): cuts.append((fb, fe))
        if cuts:
            for fb, fe in reversed(cuts): new = new[:fb] + new[fe:]
            out.append((b, e, new)); removed += len(cuts)
    for b, e, new in reversed(out): text = text[:b] + new + text[e:]
    open(path, "w").write(text); return removed

def thicken_silk(path, refs, width=0.17):
    """Widen every silkscreen stroke thinner than `width` mm on the given footprints (JLCDFM warns below 0.153 mm; KiCad's library outlines are 0.12)."""
    text = open(path).read(); edits = []; n = 0
    for b, e in _blocks(text, 0, ("footprint",)):
        fp = text[b:e]; ref = re.search(r'\(property "Reference" "([^"]*)"', fp)
        if not ref or ref.group(1) not in refs: continue
        new = fp
        for fb, fe in reversed(list(_blocks(fp, 0, ("fp_line", "fp_rect", "fp_circle", "fp_arc", "fp_poly", "fp_curve")))):
            blk = fp[fb:fe]
            if not re.search(r'\(layer "[FB]\.Silk(?:S|screen)"\)', blk): continue
            def fix(m):
                global_n[0] += 1 if float(m.group(1)) < width else 0
                return "(width %g)" % max(float(m.group(1)), width)
            nb = re.sub(r"\(width ([\d.]+)\)", fix, blk); new = new[:fb] + nb + new[fe:]
        edits.append((b, e, new))
    for b, e, new in reversed(edits): text = text[:b] + new + text[e:]
    open(path, "w").write(text); return global_n[0]
global_n = [0]

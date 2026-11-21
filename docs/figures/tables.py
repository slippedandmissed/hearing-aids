"""Generate markdown tables for the manual from the data files, the PCB BOMs and the print manifest -> docs/build/tables/*.md.
uv run python docs/figures/tables.py"""
import os, csv, tomllib
from common import *

PARTS = tomllib.load(open(os.path.join(ROOT, "docs", "data", "parts.toml"), "rb"))

def write(name, text):
    os.makedirs(TAB, exist_ok=True); open(os.path.join(TAB, name + ".md"), "w").write(text + "\n"); print("wrote", name + ".md")

def md(rows, header, align=None):
    align = align or ["l"] * len(header)
    wid = [max(len(str(h)), min(40, max((len(str(r[i])) for r in rows), default=4))) for i, h in enumerate(header)]     # dashes set the relative column widths in a pipe table
    sep = [("-" * max(w, 4) + ":") if a == "r" else (":" + "-" * max(w, 4)) for w, a in zip(wid, align)]
    return "\n".join(["| " + " | ".join(header) + " |", "| " + " | ".join(sep) + " |"] + ["| " + " | ".join(str(c) for c in r) + " |" for r in rows])

def csv_rows(path): return list(csv.DictReader(open(path))) if os.path.exists(path) else []

# ------------------------------------------------------------------ cost model (shared with costs.py)
def cost_model():
    rates = PARTS["rates"]; items = []
    for it in PARTS["item"]:
        lo, hi = it["qty"] * it["low"], it["qty"] * it["high"]; v = rates["vat"] if it.get("vat") else 0
        items.append(dict(it, lo=lo * (1 + v), hi=hi * (1 + v)))
    man = csv_rows(os.path.join(ROOT, "cad", "print", "manifest.csv")); vol = sum(float(r["qty"]) * float(r["volume_cm3"]) for r in man) if man else 137.0
    plo, phi = rates["print_gbp_per_cm3"]; lean = rates["lean_print_cm3"]
    items.append(dict(group="3D prints", item=f"MJF nylon prints, full set ({vol:.0f} cm³ incl. spares)", qty=1, lo=vol * plo, hi=vol * phi, source="JLC3DP or a UK MJF bureau (NOT quoted)", note="price per cm³ is an assumption", vat=False))
    return items, vol, lean

def bom_tables():
    items, vol, lean = cost_model(); rows = []
    for it in items:
        rows.append([it["group"], it["item"], it["qty"] if it["group"] != "3D prints" else "set", f"{it['lo']:.0f}–{it['hi']:.0f}" if it["hi"] else "0", it["source"] + (f" — {it['note']}" if it.get("note") else "")])
    lo, hi = sum(i["lo"] for i in items), sum(i["hi"] for i in items)
    rows.append(["**Total**", "", "", f"**{lo:.0f}–{hi:.0f}**", f"JLCPCB lines include 20 % VAT; with the lean print set (≈ {lean} cm³): {lo - vol * PARTS['rates']['print_gbp_per_cm3'][0] + lean * PARTS['rates']['print_gbp_per_cm3'][0]:.0f}–{hi - vol * PARTS['rates']['print_gbp_per_cm3'][1] + lean * PARTS['rates']['print_gbp_per_cm3'][1]:.0f}"])
    write("bom_cost", md(rows, ["Group", "Item", "Qty", "£ (est.)", "Source / note"], ["l", "l", "r", "r", "l"]))
    return lo, hi

def jlc_tables():
    for nm, f in (("dangle_L", "dangle_L_BOM.csv"), ("dangle_R", "dangle_R_BOM.csv"), ("carrier", "carrier_BOM.csv")):
        rows = csv_rows(os.path.join(ROOT, "pcb", "fab", f))
        write(f"jlc_{nm}", md([[r.get("Comment", ""), r.get("Designator", ""), r.get("Footprint", ""), r.get("LCSC Part #", "")] for r in rows], ["Part", "Designators", "Footprint", "LCSC"]) if rows else "*(run `make pcb` to generate this table)*")

def print_tables():
    man = csv_rows(os.path.join(ROOT, "cad", "print", "manifest.csv"))
    if not man: write("print_summary", "*(run `make print-files`)*"); return
    groups = {}
    for r in man:
        n = r["file"]; g = "clip A" if n.startswith("clipA") else "clip B + arm 2.8" if "arm2.8" in n else "clip B + arm 2.4/3.2" if n.startswith("clipB") else n.split("_")[0] + " " + n.split("_")[1].split(".")[0] if n.startswith("bear") else "bee box"
        if n.startswith("bear"): g = "bear " + ("shell" if "shell" in n else "back plate")
        d = groups.setdefault(g, [0, 0.0, 0.0, r["bbox_mm"]]); d[0] += 1; d[1] += float(r["volume_cm3"]) * float(r["qty"]); d[2] += float(r["mass_g_est"]) * float(r["qty"])
    rows = [[g, v[0], f"{v[1]:.1f}", f"{v[2]:.0f}", v[3]] for g, v in groups.items()]
    rows.append(["**all**", sum(v[0] for v in groups.values()), f"**{sum(v[1] for v in groups.values()):.1f}**", f"**{sum(v[2] for v in groups.values()):.0f}**", ""])
    write("print_summary", md(rows, ["Group", "Files", "Volume incl. quantities (cm³)", "Mass (g)", "Example bounding box (mm)"], ["l", "r", "r", "r", "l"]))
    full = md([[r["file"], r["qty"], r["volume_cm3"], r["bbox_mm"], r["check"]] for r in man], ["File", "Qty", "cm³", "Bounding box (mm)", "Check"], ["l", "r", "r", "l", "l"])
    write("print_manifest", full)

def drc_table():
    rows = []
    for nm, p in (("Dangle L", "pcb/out/dangle_L_drc.txt"), ("Dangle R", "pcb/out/dangle_R_drc.txt"), ("Carrier", "pcb/carrier/out/carrier_C_drc.txt")):
        path = os.path.join(ROOT, p)
        if not os.path.exists(path): rows.append([nm, "—", "—"]); continue
        txt = open(path).read(); kinds = {}
        for line in txt.splitlines():
            if line.startswith("[") and "]:" in line: k = line[1:line.index("]")]; kinds[k] = kinds.get(k, 0) + 1
        rows.append([nm, kinds.get("unconnected_items", 0), ", ".join(f"{v} × {k}" for k, v in sorted(kinds.items()) if k != "unconnected_items") or "none"])
    write("drc", md(rows, ["Board", "Unconnected nets", "Other DRC messages (all cosmetic/benign)"]))

if __name__ == "__main__":
    bom_tables(); jlc_tables(); print_tables(); drc_table()
    open(os.path.join(TAB, "tables.stamp"), "w").write("ok")

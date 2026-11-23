"""Generate markdown tables for the manual from the data files, the PCB BOMs and the print manifest -> docs/build/tables/*.md.
uv run python docs/figures/tables.py"""
import os, csv, tomllib
from common import *

ORDERS = tomllib.load(open(os.path.join(ROOT, "docs", "data", "orders.toml"), "rb"))

def write(name, text):
    os.makedirs(TAB, exist_ok=True); open(os.path.join(TAB, name + ".md"), "w").write(text + "\n"); print("wrote", name + ".md")

def md(rows, header, align=None):
    align = align or ["l"] * len(header)
    wid = [max(len(str(h)), min(40, max((len(str(r[i])) for r in rows), default=4))) for i, h in enumerate(header)]     # dashes set the relative column widths in a pipe table
    sep = [("-" * max(w, 4) + ":") if a == "r" else (":" + "-" * max(w, 4)) for w, a in zip(wid, align)]
    return "\n".join(["| " + " | ".join(header) + " |", "| " + " | ".join(sep) + " |"] + ["| " + " | ".join(str(c) for c in r) + " |" for r in rows])

def csv_rows(path): return list(csv.DictReader(open(path))) if os.path.exists(path) else []

# ------------------------------------------------------------------ cost ledger (shared with costs.py): docs/data/orders.toml
CATS = ["Parts", "Manufacturing", "Labour", "Fees", "Consumables", "Tools", "Shipping", "Tax", "Discounts", "Rounding"]      # display order; a new category in the data is appended

def money(lo, hi=None):
    """2 decimals for an exact amount (minus sign for a discount); a rounded range for an estimate"""
    hi = lo if hi is None else hi
    if abs(hi - lo) < 1e-9: return f"{lo:.2f}".replace("-", "\u2212")
    return f"{lo:.0f}\u2013{hi:.0f}"

def ledger():
    """-> (orders, print volume, lean volume). Each order gets .lines (with lo/hi in GBP), .lo, .hi and .paid; paid orders must add up to their invoice total."""
    rates = ORDERS["rates"]
    man = csv_rows(os.path.join(ROOT, "cad", "print", "manifest.csv"))
    def goods(rows):                                    # GBP for a set of files by the JLC3DP rule: max(minimum, per cm3 x volume) per file x quantity, + dyeing for the black parts
        usd = sum(max(rates["print_usd_min"], rates["print_usd_per_cm3"] * float(r["volume_cm3"])) * int(r["qty"]) + (rates["print_usd_dye_small"] * int(r["qty"]) if any(r["file"].startswith(p) for p in rates["print_black"]) else 0) for r in rows)
        return usd * rates["usd_to_gbp"]
    vol = sum(float(r["qty"]) * float(r["volume_cm3"]) for r in man) if man else 84.0
    lean = dict(volume=vol, files=len(man))
    orders = []
    for o in ORDERS["order"]:
        lines = []
        for l in o["line"]:
            item = l["item"]
            if l.get("kind") == "prints":
                lo = hi = goods(man); item = f"{item} ({len(man)} files, {vol:.0f} cm\u00b3, {sum(int(r['qty']) for r in man)} pieces incl. spares)"
            elif l.get("kind") == "vat": lo = 0.2 * sum(x["lo"] for x in lines); hi = 0.2 * sum(x["hi"] for x in lines)
            elif "amount" in l: lo = hi = l["amount"]
            else: q = l.get("qty", 1); lo, hi = q * l["low"], q * l["high"]; item += f" \u00d7 {q}" if q > 1 else ""
            lines.append(dict(l, item=item, lo=lo, hi=hi))
        o2 = dict(o, lines=lines, lo=sum(x["lo"] for x in lines), hi=sum(x["hi"] for x in lines), paid=o["status"] == "paid")
        if o2["paid"] and abs(o2["lo"] - o["paid_total"]) > 0.005: raise SystemExit(f"orders.toml: order {o['id']} lines add up to {o2['lo']:.2f} but the invoice total is {o['paid_total']:.2f}")
        orders.append(o2)
    return orders, vol, lean

def by_category(orders):
    """{category: dict(paid=amount paid, lo=planned low, hi=planned high)} in display order"""
    d = {}
    for o in orders:
        for l in o["lines"]:
            c = d.setdefault(l["category"], dict(paid=0.0, lo=0.0, hi=0.0))
            if o["paid"]: c["paid"] += l["lo"]
            else: c["lo"] += l["lo"]; c["hi"] += l["hi"]
    return {k: d[k] for k in sorted(d, key=lambda k: CATS.index(k) if k in CATS else len(CATS))}

def bom_tables():
    orders, vol, lean = ledger(); rows = []
    for o in orders:
        when = o.get("date") or {"planned": "planned", "owned": "owned"}[o["status"]]
        what = [o["vendor"]] + ([o["ref"]] if o.get("ref") else []) + ([o["note"]] if o.get("note") else [])
        rows.append([f"**{o['title']}**", when, "", f"**{money(o['lo'], o['hi'])}**", " \u2014 ".join(what)])
        for l in o["lines"]: rows.append([f"\u2003{l['item']}", "", l["category"], money(l["lo"], l["hi"]), l.get("note", "")])
    paid = sum(o["lo"] for o in orders if o["paid"]); plo = sum(o["lo"] for o in orders if not o["paid"]); phi = sum(o["hi"] for o in orders if not o["paid"])
    rows.append(["**Paid so far**", "", "", f"**{money(paid)}**", "net of discounts, including tax and shipping"])
    rows.append(["**Still to buy (estimate)**", "", "", f"**{money(plo, phi)}**", "UK import VAT and any courier fee on the exciters (estimate)"])
    rows.append(["**Projected total**", "", "", f"**{money(paid + plo, paid + phi)}**", "paid + estimate"])
    write("bom_cost", md(rows, ["Order / line item", "Date", "Category", "\u00a3", "Vendor, reference, note"], ["l", "l", "l", "r", "l"]))
    cats = by_category(orders); rows = []
    for k, c in cats.items(): rows.append([k, money(c["paid"]) if c["paid"] else "\u2014", money(c["lo"], c["hi"]) if c["hi"] else "\u2014", money(c["paid"] + c["lo"], c["paid"] + c["hi"])])
    rows.append(["**Total**", f"**{money(paid)}**", f"**{money(plo, phi)}**", f"**{money(paid + plo, paid + phi)}**"])
    write("cost_category", md(rows, ["Category", "Paid", "Still to buy (est.)", "Projected"], ["l", "r", "r", "r"]))
    return paid, plo, phi

def jlc_tables():
    for nm, f in (("dangle_L", "dangle_L_BOM.csv"), ("dangle_R", "dangle_R_BOM.csv"), ("carrier", "carrier_BOM.csv")):
        rows = csv_rows(os.path.join(ROOT, "pcb", "fab", f))
        write(f"jlc_{nm}", md([[r.get("Comment", ""), r.get("Designator", "").replace(",", ", "), r.get("Footprint", ""), r.get("LCSC Part #", "")] for r in rows], ["Part", "Designators", "Footprint", "LCSC"]) if rows else "*(run `make pcb` to generate this table)*")

def print_tables():
    man = csv_rows(os.path.join(ROOT, "cad", "print", "manifest.csv"))
    if not man: write("print_summary", "*(run `make print-files`)*"); return
    groups = {}
    for r in man:
        n = r["file"]; g = "clip + arm 2.8" if "arm2.8" in n else "clip + arm 2.4/3.2" if n.startswith("clip_") else n.split("_")[0] + " " + n.split("_")[1].split(".")[0] if n.startswith("bear") else "bee box"
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

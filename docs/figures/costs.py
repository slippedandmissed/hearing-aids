"""Cost charts from the order ledger docs/data/orders.toml (+ the print manifest): by order, by category, and the share of spend. uv run python docs/figures/costs.py
Discounts are negative lines: they appear as negative bars in the by-order and by-category charts and are EXCLUDED from the share chart, which says so."""
from common import *
plt.rcParams.update({"figure.constrained_layout.use": True})
import textwrap
from tables import ledger, by_category, money, CATS

def gbp(lo, hi=None):
    s = money(lo, hi); return ("\u2212\u00a3" + s[1:]) if s.startswith("\u2212") else "\u00a3" + s

CCOL = {"Parts": C["blue"], "Manufacturing": C["green"], "Labour": C["orange"], "Fees": C["yellow"], "Consumables": C["violet"], "Tools": "#8d6e63", "Shipping": C["teal"], "Tax": C["red"], "Discounts": C["pink"], "Rounding": C["mute"]}

def breakdown():
    orders, vol, lean = ledger(); cats = by_category(orders); names = list(cats)
    col = lambda k: CCOL.get(k, C["accent"])
    paid = sum(o["lo"] for o in orders if o["paid"]); plo = sum(o["lo"] for o in orders if not o["paid"]); phi = sum(o["hi"] for o in orders if not o["paid"])
    disc = -sum(l["lo"] for o in orders for l in o["lines"] if l["category"] == "Discounts")
    fig, axs = plt.subplots(4, 1, figsize=(9, 11.5), gridspec_kw=dict(height_ratios=[2.2, 2.2, 0.6, 1.2]))
    # 1. by order: stacked by category; negatives (discounts) run to the left of zero; planned orders are hatched, their uncertainty is the grey tail
    ax = axs[0]; shown = [o for o in orders if o["status"] != "owned"]; xmax = 0; xmin = 0
    for k, o in enumerate(shown):
        pos = neg = 0.0
        for n in names:
            v = sum(l["lo"] for l in o["lines"] if l["category"] == n)
            if v > 0: ax.barh(k, v, left=pos, color=col(n), ec="white", hatch=None if o["paid"] else "//", alpha=1 if o["paid"] else 0.55); pos += v
            elif v < 0: ax.barh(k, v, left=neg, color=col(n), ec="white"); neg += v
        if not o["paid"] and o["hi"] > o["lo"]: ax.barh(k, o["hi"] - o["lo"], left=pos, color="#d5dae0", ec="white", hatch="..")
        end = max(o["hi"], pos); xmax = max(xmax, end); xmin = min(xmin, neg)
        ax.text(end + 1.5, k, (gbp(o["lo"]) + " paid") if o["paid"] else (gbp(o["lo"], o["hi"]) + " est."), va="center", fontsize=10.5)
    ax.set_yticks(range(len(shown))); ax.set_yticklabels([textwrap.fill(o["title"], 24) for o in shown], fontsize=10); ax.invert_yaxis(); ax.axvline(0, color=C["ink"], lw=0.8)
    ax.set_xlim(xmin - 4, xmax * 1.3); ax.grid(axis="x", alpha=0.3); ax.set_xlabel("\u00a3   solid = paid, hatched = estimate, grey = up to the high estimate", fontsize=10.5)
    ax.set_title(f"By order: {gbp(paid)} paid, {gbp(plo, phi)} still to buy", loc="left", fontsize=12)
    # 2. by category: paid (solid), planned low (hatched), planned range (grey tail); discounts negative
    ax = axs[1]; xmax = 0; xmin = 0
    for k, n in enumerate(names):
        c = cats[n]; p = c["paid"]
        if p >= 0: ax.barh(k, p, color=col(n), ec="white")
        else: ax.barh(k, p, color=col(n), ec="white"); xmin = min(xmin, p)
        left = max(p, 0)
        if c["lo"]: ax.barh(k, c["lo"], left=left, color=col(n), alpha=0.55, hatch="//", ec="white"); left += c["lo"]
        if c["hi"] > c["lo"]: ax.barh(k, c["hi"] - c["lo"], left=left, color="#d5dae0", hatch="..", ec="white"); left += c["hi"] - c["lo"]
        xmax = max(xmax, left); lab = (gbp(p) if p else "") + ((" + " if p else "") + gbp(c["lo"], c["hi"]) + " est." if c["hi"] else ""); ax.text(max(left, 0) + 1.5, k, lab, va="center", fontsize=10.5)
    ax.set_yticks(range(len(names))); ax.set_yticklabels(names, fontsize=11); ax.invert_yaxis(); ax.axvline(0, color=C["ink"], lw=0.8); ax.set_xlim(xmin - 4, xmax * 1.4); ax.grid(axis="x", alpha=0.3)
    ax.set_xlabel("\u00a3   paid + estimate still to buy", fontsize=10.5); ax.set_title(f"By category: projected {gbp(paid + plo, paid + phi)}", loc="left", fontsize=12)
    # 3. share of the mid-point of (paid + planned), EXCLUDING discounts
    ax = axs[2]; mid = {n: max(0.0, cats[n]["paid"] + (cats[n]["lo"] + cats[n]["hi"]) / 2) for n in names}; tot = sum(mid.values()); left = 0
    for n in names:
        if mid[n] > 0: ax.barh(0, mid[n], left=left, color=col(n), ec="white", height=0.8); left += mid[n]
    ax.set_xlim(0, tot); ax.set_yticks([]); ax.set_xlabel("\u00a3   paid + mid-point of the estimate, EXCLUDING discounts", fontsize=10.5)
    ax.set_title(f"Share of spend, EXCLUDING the \u00a3{disc:.2f} discount", loc="left", fontsize=12)
    axs[3].axis("off"); keep = [n for n in names if mid[n] / tot > 0.005]
    axs[3].legend([Rectangle((0, 0), 1, 1, color=col(n)) for n in keep], [f"{n}: \u00a3{mid[n]:.0f} ({100 * mid[n] / tot:.0f} %)" for n in keep], loc="upper center", ncol=2, fontsize=10.5, frameon=False)
    save(fig, "costs", "breakdown"); return paid, plo, phi

if __name__ == "__main__":
    print(breakdown())

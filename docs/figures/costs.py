"""Cost breakdown charts from docs/data/parts.toml (+ the print manifest). uv run python docs/figures/costs.py"""
from common import *
plt.rcParams.update({"figure.constrained_layout.use": True})
from tables import cost_model

def breakdown():
    items, vol, lean = cost_model(); groups = {}
    for it in items: g = groups.setdefault(it["group"], [0.0, 0.0]); g[0] += it["lo"]; g[1] += it["hi"]
    names = sorted(groups, key=lambda k: -(groups[k][0] + groups[k][1]))
    cols = [C["blue"], C["pink"], C["yellow"], C["green"], C["orange"], C["violet"], C["teal"], C["red"], C["mute"], C["accent"]]
    fig, axs = plt.subplots(3, 1, figsize=(9, 9.2), gridspec_kw=dict(height_ratios=[2.6, 0.7, 1.3]))
    ax = axs[0]
    for k, n in enumerate(names):
        lo, hi = groups[n]; ax.barh(k, lo, color=cols[k % len(cols)]); ax.barh(k, hi - lo, left=lo, color=cols[k % len(cols)], alpha=0.35, hatch="//", ec="white")
        ax.text(hi + 1.5, k, f"£{lo:.0f}–{hi:.0f}", va="center", fontsize=11)
    ax.set_yticks(range(len(names))); ax.set_yticklabels(names, fontsize=11); ax.invert_yaxis(); ax.set_xlabel("£  (solid = low estimate, hatched = up to the high estimate)", fontsize=11)
    tl, th = sum(v[0] for v in groups.values()), sum(v[1] for v in groups.values())
    ax.set_title(f"Estimated cost: £{tl:.0f}–{th:.0f}  (flexible ceiling ≈ £200)", loc="left", fontsize=12); ax.grid(axis="x", alpha=0.3); ax.set_xlim(0, max(v[1] for v in groups.values()) * 1.3)
    ax = axs[1]; mid = [(groups[n][0] + groups[n][1]) / 2 for n in names]; tot = sum(mid); left = 0
    for k, (n, m) in enumerate(zip(names, mid)):
        ax.barh(0, m, left=left, color=cols[k % len(cols)], ec="white", height=0.8); left += m
    ax.set_xlim(0, tot); ax.set_yticks([]); ax.set_xlabel("£ (mid-point estimate)", fontsize=11); ax.set_title("Share of the mid-point estimate", loc="left", fontsize=12)
    axs[2].axis("off")
    axs[2].legend([Rectangle((0, 0), 1, 1, color=cols[k % len(cols)]) for k in range(len(names))], [f"{n}: £{m:.0f} ({100 * m / tot:.0f} %)" for n, m in zip(names, mid)], loc="upper center", ncol=2, fontsize=10.5, frameon=False)
    save(fig, "costs", "breakdown"); return tl, th

if __name__ == "__main__":
    print(breakdown())

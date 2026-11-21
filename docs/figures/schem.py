"""A tiny schematic drawing library on top of matplotlib (explicit coordinates, 1 unit = 1 grid step), because auto-placement made the
diagrams unreadable. Every function returns the connection points so wires can be drawn between them."""
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon
from common import C

INK = C["ink"]

class Sch:
    def __init__(self, w, h, title=None, fs=8.5):
        self.fig, self.ax = plt.subplots(figsize=(w * 0.62, h * 0.62)); self.ax.set_xlim(0, w); self.ax.set_ylim(0, h)
        self.ax.set_aspect("equal"); self.ax.axis("off"); self.fs = fs
        if title: self.ax.text(0.1, h - 0.1, title, fontsize=fs + 3, fontweight="bold", va="top")

    # ------------------------------------------------------------ wires and labels
    def wire(self, *pts, color=INK, lw=1.3, ls="-"):
        xs, ys = zip(*pts); self.ax.plot(xs, ys, color=color, lw=lw, ls=ls, solid_capstyle="round", zorder=2)

    def dot(self, x, y, r=0.07): self.ax.add_patch(Circle((x, y), r, fc=INK, ec=INK, zorder=4))

    def text(self, x, y, s, ha="left", va="center", color=None, fs=None, bold=False, rot=0, style="normal"):
        self.ax.text(x, y, s, ha=ha, va=va, color=color or INK, fontsize=fs or self.fs, fontweight="bold" if bold else "normal", rotation=rot, style=style, zorder=5, linespacing=1.3)

    def flag(self, x, y, name, side="left", color=None):
        """open circle terminal with a net / connector name"""
        self.ax.add_patch(Circle((x, y), 0.09, fc="white", ec=color or C["blue"], lw=1.2, zorder=4))
        dx = -0.2 if side == "left" else 0.2
        self.text(x + dx, y, name, ha="right" if side == "left" else "left", color=color or C["blue"])

    def rail(self, x, y, name, color=C["red"]):
        """supply rail: wire stub up to a bar with a label"""
        self.wire((x, y), (x, y + 0.35), color=INK); self.wire((x - 0.28, y + 0.35), (x + 0.28, y + 0.35), color=color, lw=2.2)
        self.text(x, y + 0.6, name, ha="center", color=color, bold=True)

    def gnd(self, x, y):
        self.wire((x, y), (x, y - 0.25))
        for i, hw in enumerate((0.32, 0.20, 0.08)): self.wire((x - hw, y - 0.25 - i * 0.1), (x + hw, y - 0.25 - i * 0.1), lw=1.4)

    # ------------------------------------------------------------ components (return end points)
    def res(self, x, y, orient="h", length=1.6, name=None, val=None, color=None, name_side="top"):
        """rectangle resistor centred on (x, y); returns (p1, p2) (left/bottom, right/top)"""
        L = 0.9; w = 0.3
        if orient == "h":
            p1, p2 = (x - length / 2, y), (x + length / 2, y)
            self.wire(p1, (x - L / 2, y)); self.wire((x + L / 2, y), p2)
            self.ax.add_patch(Rectangle((x - L / 2, y - w / 2), L, w, fc="white", ec=color or INK, lw=1.3, zorder=3))
            if name or val: self.text(x, y + 0.42 if name_side == "top" else y - 0.55, "\n".join(s for s in (name, val) if s), ha="center", va="bottom" if name_side == "top" else "top", color=color, fs=self.fs - 1)
        else:
            p1, p2 = (x, y - length / 2), (x, y + length / 2)
            self.wire(p1, (x, y - L / 2)); self.wire((x, y + L / 2), p2)
            self.ax.add_patch(Rectangle((x - w / 2, y - L / 2), w, L, fc="white", ec=color or INK, lw=1.3, zorder=3))
            if name or val: self.text(x + 0.3, y, "\n".join(s for s in (name, val) if s), ha="left", color=color, fs=self.fs - 1)
        return p1, p2

    def cap(self, x, y, orient="v", length=1.4, name=None, val=None, label_side="right", polar=False):
        g = 0.14; hw = 0.32
        if orient == "v":
            p1, p2 = (x, y - length / 2), (x, y + length / 2)
            self.wire(p1, (x, y - g)); self.wire((x, y + g), p2)
            self.wire((x - hw, y - g), (x + hw, y - g), lw=1.8); self.wire((x - hw, y + g), (x + hw, y + g), lw=1.8)
            if name or val: self.text(x + (0.45 if label_side == "right" else -0.45), y, "\n".join(s for s in (name, val) if s), ha="left" if label_side == "right" else "right", fs=self.fs - 1)
        else:
            p1, p2 = (x - length / 2, y), (x + length / 2, y)
            self.wire(p1, (x - g, y)); self.wire((x + g, y), p2)
            self.wire((x - g, y - hw), (x - g, y + hw), lw=1.8); self.wire((x + g, y - hw), (x + g, y + hw), lw=1.8)
            if name or val: self.text(x, y + 0.5, "\n".join(s for s in (name, val) if s), ha="center", va="bottom", fs=self.fs - 1)
        return p1, p2

    def led(self, x, y, name=None, color="#d64545"):
        """vertical LED, anode up, cathode down. returns (cathode, anode)"""
        self.wire((x, y - 0.8), (x, y - 0.3)); self.wire((x, y + 0.3), (x, y + 0.8))
        self.ax.add_patch(Polygon([(x - 0.32, y + 0.3), (x + 0.32, y + 0.3), (x, y - 0.3)], fc=color, ec=INK, lw=1.2, zorder=3))
        self.wire((x - 0.32, y - 0.3), (x + 0.32, y - 0.3), lw=1.8)
        for dy in (0.05, 0.25): self.ax.annotate("", xy=(x + 0.75, y + dy + 0.25), xytext=(x + 0.4, y + dy), arrowprops=dict(arrowstyle="-|>", color=color, lw=1.0), zorder=4)
        if name: self.text(x - 0.5, y, name, ha="right", fs=self.fs - 1)
        return (x, y - 0.8), (x, y + 0.8)

    def switch(self, x, y, name=None, length=2.0):
        """horizontal SPST slide switch; returns (left, right)"""
        a, b = (x - length / 2, y), (x + length / 2, y)
        self.wire(a, (x - 0.5, y)); self.wire((x + 0.5, y), b); self.dot(x - 0.5, y, 0.08); self.dot(x + 0.5, y, 0.08)
        self.wire((x - 0.5, y), (x + 0.42, y + 0.55));
        if name: self.text(x, y + 0.85, name, ha="center", va="bottom", fs=self.fs - 1)
        return a, b

    def fuse(self, x, y, name=None, length=2.0):
        a, b = (x - length / 2, y), (x + length / 2, y)
        self.wire(a, (x - 0.5, y)); self.wire((x + 0.5, y), b)
        self.ax.add_patch(Rectangle((x - 0.5, y - 0.17), 1.0, 0.34, fc="white", ec=INK, lw=1.3, zorder=3)); self.wire((x - 0.5, y), (x + 0.5, y), lw=1.0)
        if name: self.text(x, y + 0.42, name, ha="center", va="bottom", fs=self.fs - 1)
        return a, b

    def pfet(self, x, y, name=None):
        """P-channel MOSFET, source up (battery side), drain right/down handled by the caller. Returns dict(S, D, G)."""
        self.wire((x, y - 0.7), (x, y + 0.7), lw=1.6)                       # channel
        for yy in (y - 0.6, y, y + 0.6): self.wire((x - 0.2, yy), (x, yy), lw=1.0) if False else None
        self.wire((x - 0.28, y - 0.7), (x - 0.28, y + 0.7), lw=1.6)         # gate plate
        self.wire((x - 0.28, y), (x - 0.9, y))                              # gate lead
        self.wire((x, y + 0.6), (x + 0.5, y + 0.6)); self.wire((x, y - 0.6), (x + 0.5, y - 0.6))
        self.wire((x + 0.5, y + 0.6), (x + 0.5, y + 1.2)); self.wire((x + 0.5, y - 0.6), (x + 0.5, y - 1.2))
        self.ax.annotate("", xy=(x + 0.02, y), xytext=(x + 0.4, y), arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.0, mutation_scale=7))   # body arrow (P-channel)
        self.wire((x + 0.4, y), (x + 0.5, y));
        if name: self.text(x + 0.75, y, name, ha="left", fs=self.fs - 1)
        return dict(G=(x - 0.9, y), S=(x + 0.5, y + 1.2), D=(x + 0.5, y - 1.2))

    def battery(self, x, y, name=None):
        """vertical cell, + up. returns (minus, plus)"""
        self.wire((x, y - 0.9), (x, y - 0.25)); self.wire((x, y + 0.25), (x, y + 0.9))
        self.wire((x - 0.45, y - 0.25), (x + 0.45, y - 0.25), lw=2.2); self.wire((x - 0.25, y + 0.25), (x + 0.25, y + 0.25), lw=1.2)
        self.text(x + 0.3, y + 0.75, "+", fs=self.fs + 1, bold=True);
        if name: self.text(x - 0.6, y, name, ha="right", fs=self.fs - 1)
        return (x, y - 0.9), (x, y + 0.9)

    def ic(self, x, y, w, h, title, left=(), right=(), top=(), bottom=(), sub=None, color="#eef2f7", stub=0.7):
        """IC rectangle with lower-left at (x, y). Pins: tuples (name, number, offset) where offset is the position along the edge
        (y for left/right, x for top/bottom, measured from the lower-left corner). The title and subtitle are WRAPPED to the block width and
        stacked from the top; a warning is printed if a side pin would land inside that text. Returns {name: (x, y)} of the OUTER stub ends."""
        import textwrap
        self.ax.add_patch(Rectangle((x, y), w, h, fc=color, ec=INK, lw=1.5, zorder=3))
        upc = 0.0165                                                     # data units per character per point of font size (DejaVu, 0.62 in per unit)
        tl = textwrap.wrap(title, max(8, int((w - 0.5) / (upc * self.fs * 1.08)))) ; sl = textwrap.wrap(sub, max(8, int((w - 0.5) / (0.021 * (self.fs - 1.5)))) ) if sub else []
        cur = y + h - (0.95 if top else 0.45)
        for ln in tl: self.text(x + w / 2, cur, ln, ha="center", va="center", bold=True, fs=self.fs); cur -= 0.55
        for ln in sl: self.text(x + w / 2, cur, ln, ha="center", va="center", color=C["mute"], fs=self.fs - 1.5); cur -= 0.5
        lowest = cur + 0.25                                              # bottom of the title text block
        pins = {}
        for side, lst in (("left", left), ("right", right), ("top", top), ("bottom", bottom)):
            for name, num, off in lst:
                if side in ("left", "right") and y + off + 0.22 > lowest: print(f"   WARNING schematic: pin {name} of '{title}' at offset {off} touches the title text (limit {lowest - y - 0.22:.2f})")
                if side == "left": a, b, tx, ty, ha = (x - stub, y + off), (x, y + off), x + 0.12, y + off, "left"; nx, ny = x - 0.1, y + off + 0.12
                elif side == "right": a, b, tx, ty, ha = (x + w + stub, y + off), (x + w, y + off), x + w - 0.12, y + off, "right"; nx, ny = x + w + 0.1, y + off + 0.12
                elif side == "top": a, b, tx, ty, ha = (x + off, y + h + stub), (x + off, y + h), x + off, y + h - 0.3, "center"; nx, ny = x + off + 0.1, y + h + 0.1
                else: a, b, tx, ty, ha = (x + off, y - stub), (x + off, y), x + off, y + 0.3, "center"; nx, ny = x + off + 0.1, y - 0.1
                self.wire(a, b, lw=1.3); self.text(tx, ty, name, ha=ha, fs=self.fs - 0.5)
                self.text(nx, ny, str(num), ha=("right" if side == "left" else "left"), va="bottom" if side != "bottom" else "top", color=C["mute"], fs=self.fs - 2)
                pins[name] = a
        lw_ = max((len(n) for n, _, _ in left), default=0); rw_ = max((len(n) for n, _, _ in right), default=0)
        if (lw_ + rw_) * upc * (self.fs - 0.5) + 0.5 > w and left and right: print(f"   WARNING schematic: block '{title}' is too narrow for its left and right pin names")
        return pins

    def save(self, group, name):
        from common import save
        return save(self.fig, group, name)

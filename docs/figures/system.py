"""System-level diagrams, redrawn for readability: a 9-inch canvas (about page width), large text, few words, plenty of space.
Details that used to crowd the diagrams live in the tables of the manual.  uv run python docs/figures/system.py"""
from common import *

FS, FSB = 11.5, 12.5          # normal / bold label size (points, on a 9-inch canvas: about 8 pt on the page)

def label(ax, x, y, s, fs=FS, **kw): ax.text(x, y, s, fontsize=fs, ha=kw.pop("ha", "center"), va=kw.pop("va", "center"), **kw)

# ============================================================================== 3. power
def power_tree():
    fig, ax = canvas(9, 5.4)
    box(ax, 0.3, 3.0, 1.9, 1.3, "Battery\n3.0 – 4.2 V", "#e1f5e9", fs=FSB, bold=True); box(ax, 2.6, 3.0, 1.9, 1.3, "Protection:\nswitch + fuse", "#eceff3", fs=FSB, bold=True); box(ax, 4.9, 3.0, 1.7, 1.3, "Power\nrail", "#ffe5e5", fs=FSB, bold=True, ec=C["red"])
    arrow(ax, (2.2, 3.65), (2.6, 3.65), lw=2.5); arrow(ax, (4.5, 3.65), (4.9, 3.65), lw=2.5)
    box(ax, 7.0, 3.0, 1.8, 1.3, "Computer", "#e4eeff", fs=FSB, bold=True); arrow(ax, (6.6, 3.65), (7.0, 3.65), lw=2.5)
    box(ax, 4.15, 0.8, 1.9, 1.3, "Left ear\namplifier", "#dff0ff", fs=FS, bold=True); box(ax, 6.4, 0.8, 1.9, 1.3, "Right ear\namplifier", "#dff0ff", fs=FS, bold=True)
    arrow(ax, (5.4, 3.0), (5.1, 2.1), lw=2); arrow(ax, (6.1, 3.0), (7.3, 2.1), lw=2)
    box(ax, 0.3, 0.8, 3.4, 1.3, "Each earring also has a small\nregulator that makes 3.3 V\nfor its microphone", "#fff2da", fs=10.5); arrow(ax, (4.15, 1.45), (3.7, 1.45), lw=2, color=C["orange"])
    label(ax, 4.5, 4.95, "Charging: a USB-C cable into the bee fills the battery, but only while the slide switch is ON.", 10.5, color=C["mute"], style="italic")
    return fig

# ============================================================================== 4. wiring of one ear (PCBs are black boxes)
WIRES = [("1", "I2S_LRCLK", "#4aa3ff"), ("2", "I2S_DIN", "#4aa3ff"), ("3", "VBAT  (+)", "#d64545"), ("4", "PDM_DATA", "#4aa3ff"), ("5", "I2S_BCLK", "#4aa3ff"), ("6", "GND", "#222222"), ("7", "PDM_CLK", "#4aa3ff"), ("8", "GND", "#222222")]

def wiring():
    fig, ax = canvas(9, 7.4)
    box(ax, 0.2, 5.7, 1.9, 1.15, "Battery\n(JST plug)", "#e1f5e9", fs=FS, bold=True)
    box(ax, 0.2, 1.4, 1.9, 4.0, "NECKLACE\nBOX\n\n(computer +\ncarrier\nboard)", "#222831", tc="white", fs=FSB, bold=True)
    arrow(ax, (1.15, 5.7), (1.15, 5.4), lw=2.5, color=C["red"]); label(ax, 2.3, 6.3, "check the + and − before plugging in", 10.5, ha="left", color=C["red"])
    for i, (n, nm, col) in enumerate(WIRES):
        y = 4.95 - i * 0.42
        ax.plot([2.1, 6.55], [y, y], color="black", lw=5.5, solid_capstyle="round", zorder=2); ax.plot([2.1, 6.55], [y, y], color=col, lw=3.6, solid_capstyle="round", zorder=3)
        label(ax, 2.35, y + 0.1, f"{n}  {nm}", 10, ha="left", va="bottom")
    label(ax, 2.3, 5.75, "two 4-wire ribbons: A = wires 1–4, B = wires 5–8", 10, ha="left", color=C["mute"])
    box(ax, 6.55, 1.75, 2.25, 3.4, "EARRING\nCIRCUIT\nBOARD\n\n(microphone +\namplifier)", "#222831", tc="white", fs=FS, bold=True)
    wire = lambda p, c: (ax.plot(*zip(*p), color="black", lw=5.5, solid_capstyle="round", zorder=2), ax.plot(*zip(*p), color=c, lw=3.6, solid_capstyle="round", zorder=3))
    wire([(7.3, 1.75), (7.3, 1.25)], "#222222"); wire([(8.05, 1.75), (8.05, 1.25)], "#d64545")
    box(ax, 6.55, 0.2, 2.25, 1.0, "Bone vibrator", "#ffe3f0", fs=FS, bold=True)
    label(ax, 4.3, 0.3, "The right ear has an identical cable and board.", 10, color=C["mute"], style="italic")
    return fig

# ============================================================================== 5. clocks
def clocks():
    fig, ax = canvas(9, 4.6)
    box(ax, 0.3, 1.9, 2.1, 1.4, "One 32 MHz\nclock inside\nthe computer", "#e4eeff", fs=FS, bold=True)
    box(ax, 3.2, 3.1, 2.0, 0.95, "÷ 31", "#eceff3", fs=FSB, bold=True); box(ax, 3.2, 1.15, 2.0, 0.95, "÷ 31", "#eceff3", fs=FSB, bold=True)
    arrow(ax, (2.4, 2.9), (3.2, 3.55), lw=2.5); arrow(ax, (2.4, 2.3), (3.2, 1.6), lw=2.5)
    box(ax, 6.0, 3.1, 2.7, 0.95, "mic clock 1.032 MHz\n→ 16 129 samples/s", "#dff0ff", fs=10.5, bold=True); box(ax, 6.0, 1.15, 2.7, 0.95, "amp frame clock\n16 129 per second", "#dff0ff", fs=10.5, bold=True)
    arrow(ax, (5.2, 3.58), (6.0, 3.58), lw=2.5); arrow(ax, (5.2, 1.62), (6.0, 1.62), lw=2.5)
    label(ax, 4.5, 0.55, "Both clocks come from the same source, so the microphone and the amplifier can never drift apart.\nThe amplifier's data sheet lists 16 000, not 16 129: untested (see risks).", 9.8, color=C["mute"])
    return fig

# ============================================================================== 6. timing diagrams (readable versions)
def wave(ax, y, t, v, h=0.7, color=C["ink"], label_=None):
    ax.step(t, y + np.asarray(v) * h, where="post", color=color, lw=2.2)
    if label_: ax.text(-0.3, y + h / 2, label_, ha="right", va="center", fontsize=11.5, color=color, fontweight="bold")

def timing_pdm():
    fig, ax = plt.subplots(figsize=(9, 3.6)); ax.axis("off"); ax.set_xlim(-3.4, 13); ax.set_ylim(-0.5, 4.8)
    n = 12; t = np.arange(n + 1); wave(ax, 3.4, t, [i % 2 == 0 for i in range(n + 1)], label_="clock")
    bits = [1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1]
    for i in range(n):
        col = C["pink"] if i % 2 == 0 else C["blue"]
        ax.add_patch(Rectangle((i + 0.08, 1.5), 0.84, 1.0, fc=col, alpha=0.3, ec=col, lw=1.4)); ax.text(i + 0.5, 2.0, str(bits[i]), ha="center", va="center", fontsize=12, fontweight="bold")
        ax.text(i + 0.5, 1.0, "L" if i % 2 == 0 else "R", ha="center", va="center", fontsize=11.5, color=col, fontweight="bold")
    ax.text(-0.3, 2.0, "data", ha="right", va="center", fontsize=11.5, fontweight="bold")
    ax.text(6.5, 0.1, "L = left microphone, R = right microphone: they take turns on one wire.", ha="center", fontsize=10.5, color=C["mute"])
    ax.set_title("Microphones: two microphones, one clock wire, one data wire", loc="left", fontsize=12.5, fontweight="bold")
    return fig

def timing_i2s():
    fig, ax = plt.subplots(figsize=(9, 3.9)); ax.axis("off"); ax.set_xlim(-3.4, 18); ax.set_ylim(-0.5, 6.2)
    nb = 4; t = np.arange(0, 4 * nb + 1)
    wave(ax, 4.5, t, np.array([(i % 2 == 0) for i in t], int), label_="bit clock"); wave(ax, 2.9, t, np.array([(i // (2 * nb)) % 2 == 1 for i in t], int), label_="left / right")
    for k, (x0, who, col) in enumerate(((0, "LEFT ear's sound", C["pink"]), (2 * nb, "RIGHT ear's sound", C["blue"]))):
        ax.text(x0 + nb, 3.95, who, ha="center", fontsize=10.5, color=col, fontweight="bold")
        for i, b in enumerate([1, 0, 1, 1] if k == 0 else [0, 1, 1, 0]):
            ax.add_patch(Rectangle((x0 + 2 * i + 0.95, 1.15), 1.9, 0.9, fc=col, alpha=0.3, ec=col, lw=1.4)); ax.text(x0 + 2 * i + 1.9, 1.6, str(b), ha="center", va="center", fontsize=12, fontweight="bold")
    ax.text(-0.3, 1.6, "audio data", ha="right", va="center", fontsize=11.5, fontweight="bold")
    ax.text(8.5, 0.1, "One wire carries the left ear's sound, then the right ear's; each amplifier picks its half.", ha="center", fontsize=9.6, color=C["mute"])
    ax.set_title("Amplifiers: stereo sound on one data wire", loc="left", fontsize=12.5, fontweight="bold")
    return fig

if __name__ == "__main__":
    for name, f in (("power_tree", power_tree), ("wiring", wiring), ("clocks", clocks), ("timing_pdm", timing_pdm), ("timing_i2s", timing_i2s)):
        save(f(), "system", name)

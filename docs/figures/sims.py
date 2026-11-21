"""Simulations and estimates (ngspice for the exciter drive network, analytic models for the rest). Every model parameter marked ASSUMED
must be replaced by a measurement before it is trusted.  uv run python docs/figures/sims.py"""
import os, subprocess, tempfile, csv
from common import *

VBAT = 4.2            # full cell, worst case for power
RE, LE = 3.6, 0.15e-3                     # Dayton DAEX-9-4SM: Re 3.6 ohm (datasheet); coil inductance ASSUMED
FS, RM = 1200.0, 6.0                       # mechanical resonance ~1.2 kHz (datasheet, page formatting unclear); resonant impedance peak 6 ohm ASSUMED
LM = 1e-3; CM = 1 / ((2 * np.pi * FS) ** 2 * LM)

def ngspice(netlist, outputs):
    """run ngspice in batch mode; returns the raw numeric table written by wrdata"""
    with tempfile.TemporaryDirectory() as td:
        cir = os.path.join(td, "x.cir"); dat = os.path.join(td, "x.dat")
        open(cir, "w").write(netlist.replace("@DAT@", dat).replace("@OUT@", outputs))
        r = subprocess.run(["ngspice", "-b", cir], capture_output=True, text=True, timeout=120)
        if not os.path.exists(dat): raise RuntimeError(r.stdout[-800:] + r.stderr[-800:])
        return np.loadtxt(dat)

EXC = f"""Re a b {RE}
Le b c {LE}
Rm c 0 {RM}
Lm c 0 {LM}
Cm c 0 {CM}"""

def ac_zin(rs):
    nl = f"""exciter ac
V1 in 0 AC 1
Rs in a {rs}
{EXC}
.ac dec 60 20 20k
.control
run
wrdata @DAT@ i(V1)
.endc
.end"""
    d = ngspice(nl, "")
    f = d[:, 0]; i = -(d[:, 1] + 1j * d[:, 2]); return f, 1 / i                # Zin of the whole network (V = 1 V)

def tran_square(rs, vp, f0=1000.0):
    nl = f"""exciter transient
V1 in 0 PULSE({-vp} {vp} 0 1u 1u {0.5 / f0} {1 / f0})
Rs in a {rs}
{EXC}
.tran 2u 4m
.control
run
wrdata @DAT@ v(a) v(in) i(V1)
.endc
.end"""
    d = ngspice(nl, ""); return d[:, 0], d[:, 1], d[:, 3], -d[:, 5]

# ============================================================================== 1. exciter drive and hardware power cap
plt.rcParams.update({"font.size": 11, "axes.titlesize": 12, "legend.fontsize": 10, "axes.labelsize": 11, "figure.constrained_layout.use": True})

def exciter_power():
    fig, axs = plt.subplots(3, 1, figsize=(9, 11.5))
    ax = axs[0]
    for rs, col in ((0, C["red"]), (22, C["orange"]), (44, C["accent"]), (100, C["blue"])):
        f, z = ac_zin(rs) if rs else ac_zin(1e-3)
        p = 0.5 * VBAT ** 2 * np.real(z - rs) / np.abs(z) ** 2 * 1000      # mW into the exciter, full-scale sine of amplitude VBAT (BTL differential peak)
        ax.semilogx(f, p, color=col, lw=2, label=f"{rs} Ω series" + ("   (= 2 × 22 Ω fitted)" if rs == 44 else ""))
    ax.set_xlabel("frequency (Hz)"); ax.set_ylabel("exciter power, mW"); ax.set_title("Worst-case sine, full scale, 4.2 V cell\n(ngspice AC sweep, exciter model ASSUMED)", fontsize=12, loc="left")
    ax.set_yscale("log"); ax.grid(alpha=0.3, which="both"); ax.legend(fontsize=10, loc="upper center", bbox_to_anchor=(0.5, -0.32), ncol=2, frameon=False); ax.axvspan(300, 4000, color=C["yellow"], alpha=0.12)
    ax.text(1100, ax.get_ylim()[0] * 1.5, "speech band", fontsize=10, color="#b8860b", ha="center")
    ax = axs[1]
    t, va, vin, i = tran_square(44, VBAT)
    ax.plot(t * 1e3, i * 1e3, color=C["accent"], lw=1.6, label="current (mA)")
    ax.plot(t * 1e3, va * 10, color=C["blue"], lw=1.2, alpha=0.8, label="voltage at exciter × 10 (V·10)")
    ax.set_xlabel("time (ms)"); ax.set_title("Firmware-bug case: full-scale 1 kHz square wave\nthrough 44 Ω (ngspice transient)", fontsize=12, loc="left"); ax.grid(alpha=0.3); ax.legend(fontsize=10, loc="upper right")
    ax.set_xlim(0, 4); ax.set_ylim(-110, 160); ax.legend(fontsize=10, loc="upper right", ncol=2)
    ax = axs[2]
    rs = np.linspace(0, 150, 300); f_res = 1200
    z = RE + 1j * 2 * np.pi * f_res * LE + 1 / (1 / RM + 1 / (1j * 2 * np.pi * f_res * LM) + 1j * 2 * np.pi * f_res * CM)
    pexc = 0.5 * VBAT ** 2 * np.real(z) / np.abs(rs + z) ** 2 * 1000
    ax.plot(rs, pexc, color=C["ink"], lw=2); ax.axvline(44, color=C["accent"], ls="--"); ax.text(46, pexc.max() * 0.55, "fitted: 44 Ω\n= 2 × 22 Ω", color=C["accent"], fontsize=10)
    ax.axhline(100, color=C["mute"], lw=0.8, ls=":"); ax.text(148, 106, "100 mW", ha="right", fontsize=10, color=C["mute"])
    ax.set_xlabel("series resistance (Ω)"); ax.set_ylabel("max power at 1.2 kHz, mW"); ax.set_title("Hardware power cap vs series resistance", fontsize=12, loc="left"); ax.grid(alpha=0.3); ax.set_ylim(bottom=0)
    save(fig, "sims", "exciter_power")
    f, z = ac_zin(44); p = 0.5 * VBAT ** 2 * np.real(z - 44) / np.abs(z) ** 2 * 1000
    return dict(peak_mW=p.max(), at=f[p.argmax()], square_mA=np.abs(i).max() * 1e3)

# ============================================================================== 2. battery life
LOADS = {"XIAO nRF52840 (CPU + PDM + I2S)": 6.0, "2 × MAX98357A idle": 4.8, "2 × PDM mic": 1.2, "power LED": 0.9, "2 × exciter drive (speech)": 2.0}   # mA, ASSUMED from datasheet typicals

def battery():
    fig, axs = plt.subplots(3, 1, figsize=(9, 9), gridspec_kw=dict(height_ratios=[1.0, 1.1, 2.6]))
    ax = axs[0]; left = 0; cols = [C["blue"], C["pink"], C["teal"], C["yellow"], C["orange"]]
    for (k, v), c in zip(LOADS.items(), cols):
        ax.barh(0, v, left=left, color=c, ec="white"); (ax.text(left + v / 2, 0, f"{v:.1f}", ha="center", va="center", fontsize=11, color="white" if c in (C["blue"], C["pink"], C["teal"]) else C["ink"]) if v >= 1.5 else None); left += v
    ax.set_yticks([]); ax.set_xlabel("typical current from the cell (mA, ASSUMED)"); ax.set_xlim(0, left * 1.02)
    ax.set_title(f"Where the current goes: ≈ {left:.1f} mA typical", fontsize=12, loc="left")
    axs[1].axis("off"); axs[1].legend([Rectangle((0, 0), 1, 1, color=c) for c in cols], [f"{k}: {v:.1f} mA" for k, v in LOADS.items()], fontsize=10.5, loc="center", ncol=2, frameon=False)
    ax = axs[2]
    caps = np.array([200, 300, 500, 700, 1000]); usable = 0.85
    for scen, mA, col in (("quiet room", left - 0.9 - 1.0, C["green"]), ("typical", left, C["blue"]), ("loud, all the time", left + 6, C["red"])):
        ax.plot(caps, caps * usable / mA, marker="o", color=col, lw=2, label=f"{scen}: {mA:.0f} mA")
    ax.set_xlabel("battery capacity (mAh)"); ax.set_ylabel("run time (hours), 85 % usable"); ax.grid(alpha=0.3); ax.legend(fontsize=10, loc="upper left")
    ax.set_title("Estimated run time", fontsize=12, loc="left"); ax.axvline(500, color=C["mute"], ls=":"); ax.text(510, ax.get_ylim()[1] * 0.93, "planned 500 mAh", fontsize=10, color=C["mute"])
    save(fig, "sims", "battery"); return left

# ============================================================================== 3. spring arm
def spring():
    E, h, L = 1700.0, 7.0, 55.0                    # PA12 MJF (ASSUMED), arm height, free length to the pad (ASSUMED)
    fig, axs = plt.subplots(2, 1, figsize=(9, 8.5))
    t = np.linspace(1.6, 4.2, 200); I = h * t ** 3 / 12; k = 3 * E * I / L ** 3
    ax = axs[0]
    for pre, col in ((3, C["blue"]), (5, C["accent"]), (7, C["orange"])): ax.plot(t, k * pre, lw=2, color=col, label=f"preload {pre} mm")
    ax.axhspan(2, 5, color=C["green"], alpha=0.15); ax.text(1.65, 4.5, "target pad force 2–5 N", color=C["green"], fontsize=10)
    for ta in (2.4, 2.8, 3.2): ax.axvline(ta, color=C["line"], ls=":"); ax.text(ta, ax.get_ylim()[1] * 0.02 + 0.1, f"{ta}", ha="center", fontsize=10, color=C["mute"])
    ax.set_xlabel("arm thickness (mm)"); ax.set_ylabel("force at the exciter pad (N)"); ax.set_title("Cantilever estimate: pad force vs arm thickness", fontsize=12, loc="left"); ax.grid(alpha=0.3); ax.legend(fontsize=10)
    ax = axs[1]
    for pre, col in ((3, C["blue"]), (5, C["accent"]), (7, C["orange"])): ax.plot(t, 100 * 3 * t * pre / (2 * L ** 2), lw=2, color=col, label=f"preload {pre} mm")
    ax.axhline(2.0, color=C["red"], ls="--"); ax.text(4.15, 1.93, "≈ 2 % : comfortable for PA12 long term (ASSUMED)", ha="right", va="top", fontsize=10, color=C["red"]); ax.set_ylim(0, 2.7)
    ax.set_xlabel("arm thickness (mm)"); ax.set_ylabel("peak bending strain (%)"); ax.set_title("Strain in the arm at the preload", fontsize=12, loc="left"); ax.grid(alpha=0.3); ax.legend(fontsize=10, ncol=3, loc="upper center")
    save(fig, "sims", "spring_arm")

# ============================================================================== 4. latency
def latency():
    fig, axs = plt.subplots(2, 1, figsize=(9, 9), gridspec_kw=dict(height_ratios=[2.0, 1.0]))
    fs = 16129.0; blocks = np.array([8, 16, 32, 64, 128])
    ax = axs[0]; dec = 0.5; amp = 0.05
    parts = [("PDM decimation filter", np.full(5, dec), C["blue"]), ("collect one block", blocks / fs * 1e3, C["teal"]), ("DSP (< 0.1 ms at 64 MHz, ASSUMED)", np.full(5, 0.08), C["violet"]),
             ("I2S double buffer (2 blocks)", 2 * blocks / fs * 1e3, C["pink"]), ("class-D amp + cable", np.full(5, amp), C["orange"])]
    bottom = np.zeros(5)
    for name, v, col in parts: ax.bar([str(b) for b in blocks], v, bottom=bottom, color=col, label=name); bottom += v
    for i, b in enumerate(bottom): ax.text(i, b + 0.15, f"{b:.1f} ms", ha="center", fontsize=10)
    ax.set_xlabel("block size (samples)  [firmware uses 16]"); ax.set_ylabel("end-to-end latency (ms)"); ax.legend(fontsize=10, loc="upper left"); ax.set_title("Latency budget vs block size (estimate, not measured)", fontsize=12, loc="left")
    ax.axhline(5, color=C["red"], ls="--"); ax.text(-0.45, 5.4, "≈ 5 ms: echo threshold", ha="left", fontsize=10, color=C["red"])
    ax = axs[1]
    ax.axis("off"); ax.set_title("Why latency matters here", fontsize=12, loc="left", pad=10)
    ax.text(0, 0.95, "You hear your own voice through bone conduction\nand ambient sound through the open ear canal.\nAny aided copy that arrives late is heard as an echo\nor a ‘comb-filter’ colouration.\n\nPDM mic → 16 kHz → DSP → I2S in 16-sample blocks\ncosts ≈ 1 ms per block; the double-buffered I2S\noutput costs two more. Smaller blocks are lower\nlatency but use more CPU on the nRF52840.", va="top", fontsize=11)
    save(fig, "sims", "latency")

# ============================================================================== 5. margins
def margins():
    fig, axs = plt.subplots(2, 1, figsize=(9, 6.4))
    ax = axs[0]
    ax.barh(0, 2.475 - 1.024, left=1.024, color=C["green"], alpha=0.35, height=0.5, ec=C["green"])
    ax.text(1.75, 0, "range the microphone is specified for:\n1.024 – 2.475 MHz", ha="center", va="center", fontsize=11)
    ax.plot([1.032], [0], marker="v", color=C["red"], ms=13, zorder=5)
    ax.annotate("our PDM clock: 1.032 MHz\n(only 0.8 % inside the lower limit)", xy=(1.032, 0.28), xytext=(1.45, 0.78), ha="left", va="center", fontsize=11, color=C["red"], arrowprops=dict(arrowstyle="-", color=C["red"], lw=1.2))
    ax.set_xlim(0.9, 2.6); ax.set_ylim(-0.5, 1.1); ax.set_yticks([]); ax.set_xlabel("clock frequency (MHz)"); ax.set_title("Microphone clock margin", fontsize=12, loc="left")
    ax = axs[1]
    ax.axhline(0, color=C["line"], lw=1)
    for r in (8, 16, 32, 44.1, 48): ax.plot([r], [0], marker="o", ms=11, color=C["green"], alpha=0.8, zorder=3); ax.text(r, -0.32, f"{r:g}", ha="center", va="top", fontsize=11)
    ax.plot([16.129], [0.2], marker="v", color=C["red"], ms=13, zorder=5)
    ax.annotate("our LRCLK: 16.129 kHz\n(0.8 % above the listed 16 kHz,\nnot tested)", xy=(16.129, 0.3), xytext=(21, 0.65), ha="left", va="center", fontsize=11, color=C["red"], arrowprops=dict(arrowstyle="-", color=C["red"], lw=1.2))
    ax.set_xlim(4, 52); ax.set_yticks([]); ax.set_ylim(-0.75, 1.1); ax.set_xlabel("LRCLK sample rate (kHz); green dots = rates listed in the MAX98357A datasheet")
    ax.set_title("Amplifier sample-rate margin", fontsize=12, loc="left")
    save(fig, "sims", "margins")

# ============================================================================== 6. mass
def mass():
    import csv as _csv
    vol = {}
    with open(os.path.join(ROOT, "cad", "print", "manifest.csv")) as f:
        for r in _csv.DictReader(f): vol[r["file"]] = float(r["mass_g_est"])
    items = {
        "Glasses stem (each side)": [("clip A", vol.get("clipA_L_B2.stl", 0.5), C["teal"]), ("clip B + arm", vol.get("clipB_arm2.8_L_B2.stl", 3.1), C["blue"]), ("exciter", 2.3, C["pink"])],
        "Earring (each lobe)": [("bear shell + back plate", vol.get("bear_shell_L.stl", 2.4) + vol.get("bear_backplate_L.stl", 0.9), C["pink"]), ("PCB + parts", 0.9, C["green"]), ("wires, hook, screws", 1.6, C["yellow"])],
        "Necklace box": [("bee base + cover", vol.get("bee_base.stl", 12) + vol.get("bee_cover.stl", 11), C["yellow"]), ("PCB + XIAO", 6.0, C["green"]), ("500 mAh LiPo", 11.0, C["orange"]), ("cables + chain", 10.0, C["mute"])],
    }
    fig, axs = plt.subplots(3, 1, figsize=(9, 7.6), sharex=True); tot = {}
    for ax, (name, parts) in zip(axs, items.items()):
        left = 0
        for lab, g, col in parts:
            ax.barh(0, g, left=left, color=col, ec="white", height=0.7, label=f"{lab}: {g:.1f} g")
            if g >= 2.5: ax.text(left + g / 2, 0, f"{g:.1f}", ha="center", va="center", fontsize=11, color=C["ink"])
            left += g
        ax.text(left + 0.5, 0, f"{left:.1f} g", va="center", fontsize=12, fontweight="bold"); tot[name] = left
        ax.set_ylim(-0.5, 2.0); ax.set_yticks([]); ax.set_xlim(0, 48); ax.grid(axis="x", alpha=0.3); ax.set_title(name, loc="left", fontsize=12)
        ax.legend(loc="upper left", ncol=2, fontsize=10, frameon=False, bbox_to_anchor=(0, 0.98))
    axs[-1].set_xlabel("estimated mass (g); nylon ≈ 1 g/cm³ with volumes from the CAD, electronics ASSUMED")
    save(fig, "sims", "mass"); return tot

if __name__ == "__main__":
    r = {}
    r["exciter"] = exciter_power(); r["battery_mA"] = battery(); spring(); latency(); margins(); r["mass_g"] = mass()
    os.makedirs(TAB, exist_ok=True)
    with open(os.path.join(TAB, "sim_summary.txt"), "w") as f:
        f.write(f"worst_case_exciter_peak_mW {r['exciter']['peak_mW']:.1f} at {r['exciter']['at']:.0f} Hz\nsquare_wave_peak_mA {r['exciter']['square_mA']:.0f}\ntypical_current_mA {r['battery_mA']:.1f}\n")
    print(r)

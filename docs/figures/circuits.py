"""Circuit diagrams of the two custom PCBs (component level, matching pcb/build_dangle.py and pcb/carrier/build_carrier.py).
Higher-level wiring diagrams of the parts you assemble yourself live in system.py.  uv run python docs/figures/circuits.py"""
from common import *
from schem import Sch, INK

BLUE, RED, ORANGE, ACC = C["blue"], C["red"], C["orange"], C["accent"]

# ============================================================================== dangle PCB
def dangle(v):
    left = v == "L"
    s = Sch(36, 15.4, f"Dangle PCB ({'LEFT' if left else 'RIGHT'} variant): PDM microphone + I2S class-D amplifier + 3.3 V LDO", fs=9.5)
    # ---- U1 amplifier (centre)
    u1 = s.ic(9.0, 2.0, 6.6, 9.6, "U1  MAX98357AETE+T", sub="I2S class-D amp, TQFN-16 (C910544)",
              left=[("DIN", "1", 1.0), ("LRCLK", "14", 2.3), ("BCLK", "16", 3.6), ("GAIN_SLOT", "2", 5.4), ("SD_MODE", "4", 7.4)],
              right=[("OUTP", "9", 2.8), ("OUTN", "10", 5.0)], top=[("VDD", "7, 8", 3.0)], bottom=[("GND", "3, 11, 15, EP", 1.6)])
    for n in ("DIN", "LRCLK", "BCLK"):
        x, y = u1[n]; s.wire((x, y), (5.0, y)); s.flag(5.0, y, {"DIN": "I2S_DIN", "LRCLK": "I2S_LRCLK", "BCLK": "I2S_BCLK"}[n], "left")
    x, y = u1["GAIN_SLOT"]; p1, p2 = s.res(6.9, y, length=2.0, name="R_GAIN", val="100 k (3 dB)", color=ACC); s.wire(p2, (x, y)); s.wire(p1, (4.4, y)); s.rail(4.4, y, "VBAT")
    x, y = u1["SD_MODE"]; p1, p2 = s.res(6.9, y, length=2.0, name="R_SD", val=("2 k (LEFT)" if left else "220 k (RIGHT)"), color=ACC); s.wire(p2, (x, y)); s.wire(p1, (4.4, y)); s.rail(4.4, y, "3V3", ORANGE)
    x, y = u1["VDD"]; s.wire((x, y), (x, y + 1.2)); s.dot(x, y + 1.2); s.wire((x, y + 1.2), (16.2, y + 1.2)); s.rail(16.2, y + 1.2, "VBAT")
    for cx, nm, val, side in ((10.4, "C2", "100 nF", "left"), (13.6, "C1", "10 µF", "right")):
        s.dot(cx, y + 1.2); a, b = s.cap(cx, y + 0.5, "v", 1.4, nm, val, label_side=side); s.wire((cx, y + 1.2), b); s.gnd(*a)
    x, y = u1["GND"]; s.gnd(x, y)
    for n, ref, net in (("OUTP", "R_OUT1", "EXC+"), ("OUTN", "R_OUT2", "EXC−")):
        x, y = u1[n]; p1, p2 = s.res(x + 2.4, y, length=2.6, name=ref, val="22 Ω  (1206)", color=ACC); s.wire((x, y), p1); s.wire(p2, (x + 5.0, y)); s.flag(x + 5.0, y, net, "right")
    s.text(20.8, 5.8, "to the exciter\n(about 5 cm of wire)", color=C["mute"], fs=8.5)
    s.text(0.5, 0.5, "Pull-up values pick the amplifier channel: 2 k to 3V3 = LEFT, 220 k to 3V3 = RIGHT.", color=C["mute"], fs=8.3)
    # ---- U3 LDO (bottom centre-right)
    u3 = s.ic(18.2, 1.3, 5.0, 2.6, "U3  XC6206P332MR-G", sub="3.3 V LDO (C5446)", left=[("VIN", "3", 0.8)], right=[("VOUT", "2", 0.8)], bottom=[("GND", "1", 2.1)], stub=0.9)
    x, y = u3["VIN"]; s.wire((x, y), (x - 0.0, y)); s.dot(x, y); s.rail(x, y, "VBAT"); ca, cb = s.cap(x, y - 0.5, "v", 1.2, "C3", "1 µF", "left"); s.wire((x, y), cb); s.gnd(*ca)
    x, y = u3["VOUT"]; s.dot(x, y); s.rail(x, y, "3V3", ORANGE); ca, cb = s.cap(x, y - 0.5, "v", 1.2, "C4", "1 µF", "right"); s.wire((x, y), cb); s.gnd(*ca)
    x, y = u3["GND"]; s.gnd(x, y)
    # ---- U2 PDM microphone (right)
    u2 = s.ic(24.6, 6.6, 6.2, 4.8, "U2  SPH0641LM4H-1", sub="PDM mic, LGA-5 (C497724)", left=[("SELECT", "2", 1.0), ("CLOCK", "4", 2.0)], right=[("DATA", "1", 2.0)], top=[("VDD", "5", 2.8)], bottom=[("GND", "3 (ring)", 2.8)])
    x, y = u2["CLOCK"]; s.wire((x, y), (22.6, y)); s.flag(22.6, y, "PDM_CLK", "left")
    x, y = u2["SELECT"]; s.wire((x, y), (23.2, y))
    if left: s.gnd(23.2, y); s.text(24.4, 9.5, "SELECT → GND: LEFT microphone", ha="right", color=ACC, fs=8.5)
    else: s.rail(23.2, y, "3V3", ORANGE); s.text(24.4, 9.5, "SELECT → 3V3: RIGHT microphone", ha="right", color=ACC, fs=8.5)
    x, y = u2["DATA"]; s.wire((x, y), (x + 1.4, y)); s.flag(x + 1.4, y, "PDM_DATA", "right")
    x, y = u2["VDD"]; s.wire((x, y), (x, y + 1.2)); s.dot(x, y + 1.2); s.rail(x, y + 1.2, "3V3", ORANGE)
    cx = x + 1.9; s.wire((x, y + 1.2), (cx, y + 1.2)); s.dot(cx, y + 1.2); a, b = s.cap(cx, y + 0.5, "v", 1.4, "C5", "100 nF", "right"); s.wire((cx, y + 1.2), b); s.gnd(*a)
    x, y = u2["GND"]; s.gnd(x, y)
    # ---- cable pads (two columns, top middle)
    s.text(17.8, 13.8, "Neck-cable pads J1 … J8", bold=True, fs=9.5)
    pads = ((1, "I2S_LRCLK", BLUE), (2, "I2S_DIN", BLUE), (3, "VBAT", RED), (4, "PDM_DATA", BLUE), (5, "I2S_BCLK", BLUE), (6, "GND", INK), (7, "PDM_CLK", BLUE), (8, "GND", INK))
    for i, (n, nm, col) in enumerate(pads):
        s.text(17.8 + (i // 4) * 3.6, 13.0 - (i % 4) * 0.6, f"{n}  {nm}", color=col, fs=9)
    return s

# ============================================================================== carrier PCB
PADS = [(1, "I2S_LRCLK", BLUE), (2, "I2S_DIN", BLUE), (3, "VBAT", RED), (4, "PDM_DATA", BLUE), (5, "I2S_BCLK", BLUE), (6, "GND", INK), (7, "PDM_CLK", BLUE), (8, "GND", INK)]

def ear_block(s, x, side, title):
    """8-pad ear connector; pins face the XIAO. side 'R' = pins on the right of the box (left-ear block), 'L' = pins on the left."""
    face = "right" if side == "R" else "left"
    pins = [(f"{n}  {nm.replace('I2S_', '').replace('PDM_', '')}", "", 8.4 - (n - 1) * 1.0) for n, nm, _ in PADS]
    kw = {face: pins}
    p = s.ic(x, 2.0, 3.6, 10.6, title, color="#fff4e0", **kw)
    for (n, nm, col), (pn, _, _) in zip(PADS, pins):
        px, py = p[pn]; dirn = 1 if side == "R" else -1
        if nm == "VBAT": s.wire((px, py), (px + dirn * 1.2, py)); s.text(px + dirn * 1.4, py, "VBAT", ha=("left" if dirn > 0 else "right"), color=RED, bold=True, fs=9)
        elif nm == "GND": s.wire((px, py), (px + dirn * 3.4, py)); s.gnd(px + dirn * 3.4, py)
        else:
            rx = px + dirn * 1.2; p1, p2 = s.res(rx, py, length=2.4, color=ACC)
            if n in (1, 7): s.text(rx, py + (0.4 if n == 1 else -0.45), "33 Ω", ha="center", color=ACC, fs=7.2)
            far = px + dirn * 3.2; s.wire((px + dirn * 2.4, py), (far, py)); s.flag(far, py, nm, "right" if side == "R" else "left")

def carrier():
    s = Sch(38, 22.5, "Necklace-box carrier PCB: XIAO nRF52840, power path, 33 Ω series resistors and two 8-pad ear connectors")
    # ---------------- power path along the top
    bm, bp = s.battery(2.0, 17.6); s.gnd(*bm); s.text(1.2, 17.6, "1-cell LiPo\nJST-PH (J_BAT)", ha="right", fs=7.5)
    s.wire(bp, (2.0, 19.6)); s.wire((2.0, 19.6), (4.3, 19.6))
    q = s.ic(5.0, 18.4, 3.8, 3.4, "Q1  AO3401A", sub="P-FET: reverse-polarity protection", left=[("D", "3", 1.2)], right=[("S", "2", 1.2)], bottom=[("G", "1", 2.4)])
    s.gnd(*q["G"]); s.text(4.0, 16.3, "gate → GND: conducts only with the cell the right way round", ha="left", color=C["mute"], fs=7)
    s.wire(q["S"], (11.0, 19.6)); a, b = s.switch(12.5, 19.6, "SW1  SK12D07VG4\n(slide switch: ON = run + charge)", 3.0)
    f1, f2 = s.fuse(16.3, 19.6, "F1  500 mA PTC", 2.6); s.wire(b, f1)
    s.wire(f2, (19.0, 19.6)); s.dot(19.0, 19.6); s.rail(19.0, 19.6, "VBAT")
    ca, cb = s.cap(19.0, 18.1, "v", 1.4, "C_BULK", "22 µF", "left"); s.wire((19.0, 19.6), cb); s.gnd(*ca)
    s.wire((19.0, 19.6), (21.6, 19.6)); s.dot(21.6, 19.6); ca, cb = s.cap(21.6, 18.1, "v", 1.4, "C_BYP", "100 nF", "right"); s.wire((21.6, 19.6), cb); s.gnd(*ca)
    s.wire((21.6, 19.6), (25.2, 19.6)); s.dot(25.2, 19.6); p1, p2 = s.res(25.2, 18.2, "v", 1.6, "R_LED", "2.2 k"); s.wire((25.2, 19.6), p2)
    lc, la = s.led(25.2, 16.2, "D1 red LED"); s.wire(p1, la); s.gnd(*lc)
    s.wire((25.2, 19.6), (28.0, 19.6)); s.text(28.3, 19.6, "VBAT feeds ear pad 3 (both blocks)\nand the XIAO BAT+ wire", color=C["mute"], fs=7.4)
    s.text(0.3, 14.6, "While SW1 is ON the XIAO's own USB-C charger fills the cell\n(50 or 100 mA, set by firmware). The cell reaches the XIAO\nthrough two short wires soldered to its BAT+/BAT− pads.", color=C["mute"], fs=7.4)
    # ---------------- XIAO in the middle
    xi = s.ic(16.5, 3.6, 5.0, 10.0, "XIAO nRF52840", sub="pins soldered into the board", color="#e6f0ff",
              left=[("D4", "P0.04", 7.9), ("D5", "P0.05", 6.8), ("D8", "P1.13", 5.3), ("D9", "P1.14", 4.2), ("D10", "P1.15", 3.1)],
              right=[("5V", "", 7.9), ("3V3", "", 5.8), ("GND", "", 3.1)], bottom=[("BAT+", "", 1.4), ("BAT−", "", 3.6)])
    for key, net in (("D4", "PDM_CLK"), ("D5", "PDM_DATA"), ("D8", "I2S_BCLK"), ("D9", "I2S_LRCLK"), ("D10", "I2S_DIN")):
        x, y = xi[key]; s.wire((x, y), (x - 0.7, y)); s.flag(x - 0.7, y, net, "left")
    for key, txt in (("5V", "5 V (USB), unused"), ("3V3", "3V3, unused")):
        x, y = xi[key]; s.wire((x, y), (x + 0.6, y)); s.text(x + 0.8, y, txt, color=C["mute"], fs=7.4)
    x, y = xi["GND"]; s.wire((x, y), (x + 0.8, y)); s.gnd(x + 0.8, y)
    x, y = xi["BAT+"]; s.wire((x, y), (x, y - 0.4)); s.rail(x, y - 0.4, "VBAT"); s.text(x - 0.7, y - 0.1, "BAT+ wire", ha="right", color=C["mute"], fs=7.2)
    x, y = xi["BAT−"]; s.wire((x, y), (x, y - 0.5)); s.gnd(x, y - 0.5); s.text(x + 0.4, y - 0.1, "BAT− wire", ha="left", color=C["mute"], fs=7.2)
    s.text(19.0, 14.2, "USB-C (laptop / charger)", ha="center", color=C["mute"], fs=7.6)
    # ---------------- ear connector blocks, signals joined to the XIAO by net names
    ear_block(s, 1.4, "R", "J_L  left ear")
    ear_block(s, 33.4, "L", "J_R  right ear")
    s.text(19.0, 1.0, "Net names join the circuit: each signal appears on the XIAO and on BOTH ear blocks through its own 33 Ω resistor (10 in total).\nThe same 8 pads in the same order are on the dangle PCB, so the neck cable is a straight 1:1 harness.", ha="center", color=C["mute"], fs=7.6)
    return s

if __name__ == "__main__":
    for v in ("L", "R"): dangle(v).save("circuits", f"dangle_{v}_schematic")
    carrier().save("circuits", "carrier_schematic")

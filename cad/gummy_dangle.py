"""Gummy-bear earring dangle v2: front shell (dome faces outward) + flat back plate, with internal supports.
Frame: X right (seen from the FRONT), Y up, Z from the back plate (0) toward the front. PCB: component side faces the back plate, bare face (mic hole) faces the front wall.
Board (13 x 28) is mirrored in this view: bear_x = -(board_x - 6.5), bear_y = board_y - 13.5. Mic port = belly button.
ALL cables leave through ONE slot in the top of the head (no bottom hole). All mm; wall/gap values ASSUMED printable in nylon."""
from dataclasses import dataclass
from build123d import *

@dataclass(frozen=True)
class GP:
    wall: float = 1.2
    height: float = 7.6              # overall thickness (z)
    lid_t: float = 1.2
    parts_gap: float = 2.8           # lid top -> PCB component side (parts <= 1.1 mm + wire ends + wire runs)
    pcb_t: float = 1.6
    pcb_w: float = 13.0; pcb_l: float = 28.0
    pcb_clear: float = 0.4
    pcb_y: float = 0.5
    ceil_gap: float = 0.4            # PCB front face -> inner ceiling (solder blobs live in pockets)
    mic_dx: float = 2.6; mic_dy: float = -4.19
    loop_hole: float = 2.2
    post_r: float = 1.7; pilot: float = 1.3     # screw posts; 3.4 mm posts leave a 1.05 mm wall round the pilot (JLC3DP recommends >= 1.0)
    # SCREW: M1.6 x 4 mm pan head, cross recess, A2 stainless, metric thread cutting its own thread in the PA12 post (head ~3.2 wide x 1.3 tall: ISO 7045 maxima, NOT measured)
    pilot_depth: float = 5.8                    # a 4 mm screw seated at z = cb_depth ends at 4.4, so it never bottoms out (a 5 mm screw ends at 5.4, still short of 5.8)
    cb_r: float = 1.8; cb_depth: float = 0.4    # counterbore: 3.6 mm wide (head 3.2 + 0.4), 0.4 mm deep, leaving a 0.8 mm floor in the 1.2 mm plate (was 3.2 x 0.7 = 0.5 mm floor)
    notch_floor: float = 0.8                    # back-plate skin left under the cable notch (was 0.5): 3.0 mm of room under the shell slot. CABLE: 30 AWG silicone ribbon, wires 0.8 mm (+-0.1) side by side, so ~0.8 mm thick x 3.2 mm wide each; two stacked ~1.6 mm (INFERRED from the wire size, the seller gives no ribbon size). Confirm with the real cable at the first test fit
    hole_r: float = 1.0                         # plate clearance hole 2.0 mm for the 1.6 mm shank (MJF shrinks holes; JLC3DP: 0.2-0.4 mm clearance)
    slot_x: float = -5.4; slot_w: float = 4.4   # cable exit slot (top of head, on the back-of-head side)

POSTS = [(-5.8, -16.6), (5.8, -16.6), (-11.4, 3.0), (11.4, 3.0)]      # screw posts: legs + arms (clear of the PCB footprint)

def silhouette(g, grow=0.0):
    e = lambda x, y, rx, ry, rot=0.0: Pos(x, y) * Rot(0, 0, rot) * Ellipse(rx + grow, ry + grow)
    s = e(0, 13.0, 9.5, 8.5) + e(0, -2.0, 11.6, 16.0)
    for sx in (-1, 1):
        s = s + Pos(sx * 6.8, 19.4) * Circle(3.2 + grow)
        s = s + e(sx * 12.0, 3.0, 3.8, 6.2, -sx * 18)
        s = s + e(sx * 5.8, -16.8, 4.8, 4.6)
    try: s = fillet(s.vertices(), radius=1.2 if grow == 0 else 0.6)       # soften the concave joins (gummy look)
    except Exception: pass
    return s

def build(g: GP = GP(), side: str = "L"):
    """side 'L' or 'R': the cable slot and strain pegs sit toward the BACK of the head, which is the -x side of the left bear and the +x side of the right bear (seen from the front)."""
    w = g.wall
    k = 1.0 if side == "L" else -1.0; slot_x = k * g.slot_x
    z_pcb_top = g.lid_t + g.parts_gap + g.pcb_t          # PCB bare (front) face
    z_pcb_bot = g.lid_t + g.parts_gap                    # PCB component side
    z_in_top = z_pcb_top + g.ceil_gap
    assert z_in_top + 1.2 <= g.height + 0.01, (z_in_top, g.height)
    ell = lambda dr: scale(Sphere(1.0), by=(17.5 - dr, 27.0 - dr, 10.0 - dr))
    outer = extrude(silhouette(g), amount=g.height) & ell(0.0)
    outer = outer + Pos(0, 22.4, 1.6) * Box(5.0, 5.0, 3.2)                                   # hook loop block (top centre)
    inner = extrude(offset(silhouette(g), amount=-w), amount=z_in_top) & ell(w)
    shell = outer - inner
    # ---- internal supports (all grow from the front wall, down toward the lid)
    for (px, py) in POSTS:                                                                    # screw posts: M1.6 x 4 mm screws from the back
        post = Pos(px, py, (1.2 + z_in_top + 0.6) / 2) * Cylinder(g.post_r, z_in_top + 0.6 - 1.2)
        shell = shell + post
        shell = shell - Pos(px, py, g.pilot_depth / 2) * Cylinder(g.pilot / 2, g.pilot_depth)      # pilot hole z 0 .. pilot_depth
    mx, my = g.mic_dx, g.pcb_y + g.mic_dy
    boss = Pos(mx, my, (z_pcb_top + z_in_top + 0.4) / 2) * (Cylinder(1.9, z_in_top + 0.4 - z_pcb_top) - Cylinder(0.7, 4.0))   # ring around the port, touches the PCB
    shell = shell + boss
    for sx in (-1, 1):                                                                        # lateral PCB stops (hang from the ceiling beside the PCB, above the wire level)
        for (y0, y1) in ((-11.5, -8.0), (5.0, 8.5)):
            shell = shell + Pos(sx * (g.pcb_w / 2 + g.pcb_clear + 0.6), g.pcb_y + (y0 + y1) / 2, (z_pcb_bot + z_in_top + 0.4) / 2) * Box(1.0, y1 - y0, z_in_top + 0.4 - z_pcb_bot)
    for px in (k * -9.6, k * -1.0):                                                                   # strain-relief pegs: wires snake around them before leaving
        shell = shell + Pos(px, 17.6, (1.5 + z_in_top + 0.4) / 2) * Cylinder(0.7, z_in_top + 0.4 - 1.5)
    # ---- openings and paint wells
    shell = shell - Pos(mx, my, g.height - w / 2) * Cylinder(0.7, w + 2.0)                     # sound port (through the front wall)
    shell = shell - Pos(mx, my, g.height - 0.2) * Cylinder(2.0, 0.6)                           # belly-button dimple
    for sx in (-1, 1): shell = shell - Pos(sx * 3.4, 14.5, g.height - 0.2) * Cylinder(1.3, 0.8)  # eye wells (surface follows the dome, so approximate)
    shell = shell - Pos(0, 11.4, g.height - 0.2) * Cylinder(1.8, 0.8)                          # nose well
    shell = shell - Pos(0, 23.0, 1.6) * Cylinder(g.loop_hole / 2, 8.0)                         # hook loop hole (axis Z)
    shell = shell - Pos(slot_x, 20.0, 2.6) * Box(g.slot_w, 10.0, 2.4)                        # cable exit slot, top of head, z 1.4 .. 3.8
    for (cx, cy, wx, wy) in ((0.0, 11.4, 11.6, 4.2), (3.0, -12.1, 2.2, 2.2), (-3.0, -12.1, 2.2, 2.2)):   # pockets over the soldered wire pads (solder blobs on the front face)
        shell = shell - Pos(cx, cy, z_in_top + 0.2) * Box(wx, wy, 0.8)
    # ---- back plate: plug in the opening, with screw holes and edge pillars that clamp the PCB against the mic ring
    lid = extrude(offset(silhouette(g), amount=-w - 0.15), amount=g.lid_t)
    for (px, py) in POSTS:
        lid = lid - Pos(px, py, 0.6) * Cylinder(g.hole_r, 1.4)
        lid = lid - Pos(px, py, (g.cb_depth - 0.1) / 2) * Cylinder(g.cb_r, g.cb_depth + 0.1)    # shallow counterbore for the screw head (z -0.1 .. cb_depth)
    for sx in (-1, 1): lid = lid + Pos(sx * 5.7, g.pcb_y - 5.5, (g.lid_t + z_pcb_bot) / 2) * Box(1.0, 4.0, z_pcb_bot - g.lid_t)   # lands on the bare strips at the board edges
    lid = lid - Pos(slot_x, 20.0, (g.notch_floor + 1.9) / 2) * Box(g.slot_w + 0.6, 8.0, 1.9 - g.notch_floor)   # notch so the wires can pass the lid (z notch_floor .. 1.9)
    letter = mirror(Text(side, font_size=10.0, font="Helvetica", font_style=FontStyle.BOLD), about=Plane.YZ)           # mirrored so it reads correctly when looking at the back face
    lid = lid - Pos(0, -4.0, 0) * extrude(letter, amount=0.45)                                                       # engraved 0.45 mm into the back face (z=0)
    pcb = Pos(0, g.pcb_y, (g.lid_t + z_pcb_top) / 2) * Box(g.pcb_w + 2 * g.pcb_clear, g.pcb_l + 2 * g.pcb_clear, z_pcb_top - g.lid_t)
    stick_out = (pcb - inner).volume
    return shell, lid, dict(z_pcb_top=z_pcb_top, z_pcb_bot=z_pcb_bot, stick_out=stick_out, inner=inner, loop=(0.0, 23.0, 1.6))

if __name__ == "__main__":
    import os; os.makedirs("out", exist_ok=True)
    shell, lid, i = build(GP(), "L")
    bb = shell.bounding_box()
    print(f"gummy dangle v2: {bb.size.X:.1f} wide x {bb.size.Y:.1f} tall x {bb.size.Z:.1f} thick; shell {shell.volume:.0f} mm3, lid {lid.volume:.0f} mm3 (~{(shell.volume + lid.volume) / 1000:.1f} g nylon); PCB outside cavity: {i['stick_out']:.1f} mm3; valid {shell.is_valid} {lid.is_valid}")

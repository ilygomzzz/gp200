"""Procedural gear builders (bmesh, bevels on every edge). Metres, +y into the room, +z up. bpy only."""
import math

import bmesh
import bpy
from mathutils import Matrix, Vector

import materials as mt
import palette

TH = mt.TH
GROUPS = {}  # group name -> [objects]


def _obj(name, bm, mat, group, loc=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new(name)
    bm.normal_update()
    for f in bm.faces:
        f.smooth = True
    for e in bm.edges:
        e.smooth = not (len(e.link_faces) == 2 and e.calc_face_angle(0) > math.radians(35))
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    o.location, o.rotation_euler = loc, rot
    if mat:
        o.data.materials.append(mat)
    bpy.context.scene.collection.objects.link(o)
    GROUPS.setdefault(group, []).append(o)
    return o


def box(name, size, loc, mat, group, bevel=0.003, seg=3, rot=(0, 0, 0)):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=size, verts=bm.verts)
    if bevel > 0:
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=min(bevel, min(size) / 2.2), segments=seg, profile=0.5, affect="EDGES")
    return _obj(name, bm, mat, group, loc, rot)


def cyl(name, r, h, loc, mat, group, axis="z", bevel=0.001, seg=48, r2=None):
    """cylinder centred on loc; axis z/y/x; bevel on the cap rims"""
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r, radius2=r if r2 is None else r2, depth=h)
    if bevel > 0:
        rim = [e for e in bm.edges if all(abs(abs(v.co.z) - h / 2) < 1e-6 for v in e.verts)]
        bmesh.ops.bevel(bm, geom=rim, offset=min(bevel, r / 2.5, h / 2.5), segments=3, profile=0.5, affect="EDGES")
    rot = {"z": (0, 0, 0), "y": (math.pi / 2, 0, 0), "x": (0, math.pi / 2, 0)}[axis]
    return _obj(name, bm, mat, group, loc, rot)


def star_cyl(name, r, h, n, loc, mat, group, axis="z", bevel=0.0012):
    """knurled cap as geometry: 2n-gon alternating r and 0.94 r, extruded to depth h, rim bevelled"""
    bm = bmesh.new()
    res = bmesh.ops.create_circle(bm, cap_ends=True, segments=2 * n, radius=r)
    for i, v in enumerate(sorted(bm.verts, key=lambda v: math.atan2(v.co.y, v.co.x))):
        if i % 2:
            v.co.x, v.co.y = v.co.x * 0.94, v.co.y * 0.94
    bm.faces.ensure_lookup_table()
    face = bm.faces[0]
    ext = bmesh.ops.extrude_face_region(bm, geom=[face])
    bmesh.ops.translate(bm, vec=(0, 0, h), verts=[v for v in ext["geom"] if isinstance(v, bmesh.types.BMVert)])
    bmesh.ops.translate(bm, vec=(0, 0, -h / 2), verts=list(bm.verts))
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    top = [e for e in bm.edges if all(v.co.z > h / 2 - 1e-6 for v in e.verts)]
    bmesh.ops.bevel(bm, geom=top, offset=min(bevel, h / 3), segments=2, profile=0.5, affect="EDGES")
    rot = {"z": (0, 0, 0), "y": (math.pi / 2, 0, 0), "x": (0, math.pi / 2, 0)}[axis]
    return _obj(name, bm, mat, group, loc, rot)


def screw(name, loc, group, ang=0.0):
    """front-facing cross-slot screw (axis y, head toward -y)"""
    o = [cyl(name, 0.0042, 0.0018, loc, mt.screw(), group, "y", 0.0007, 16)]
    for k in (0, 1):
        o.append(box(name + "_s", (0.0062, 0.0008, 0.0009), (loc[0], loc[1] - 0.0010, loc[2]), mt.rubber(0.5), group, 0.0001, 1, rot=(0, ang + k * math.pi / 2, 0)))
    return o


def sphere(name, r, loc, mat, group):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=r)
    return _obj(name, bm, mat, group, loc)


def hexnut(name, r, h, loc, mat, group, axis="x"):
    return cyl(name, r, h, loc, mat, group, axis, bevel=0.0004, seg=6)


def parent_all(objs, loc, rot=(0, 0, 0)):
    """move a built-at-origin object list into place (rigid)"""
    m = Matrix.Translation(loc) @ Matrix.Rotation(rot[0], 4, "X") @ Matrix.Rotation(rot[2], 4, "Z")
    for o in objs:
        o.matrix_basis = m @ o.matrix_basis


# ---------------- room pieces ----------------
def pedalboard(g="room", tilt=math.radians(8)):
    """deck 1.1 x 0.5 m tilted `tilt` (high at the back), hook-and-loop top, aluminium side rails, rubber feet"""
    W, D = 1.1, 0.5
    hl, al, rb = mt.hook_loop(), mt.brushed(TH["metal"], 0.3), mt.rubber(0.85)
    objs = [box("deck", (W, D, 0.014), (0, D / 2, 0.016), hl, g, 0.002), box("deck_under", (W - 0.02, D - 0.02, 0.012), (0, D / 2, 0.006), mt.steel_black(), g, 0.002)]
    for sx in (-1, 1):
        objs.append(box("rail", (0.02, D + 0.01, 0.034), (sx * (W / 2 + 0.002), D / 2, 0.02), al, g, 0.004))
    objs.append(box("rail_b", (W + 0.03, 0.02, 0.034), (0, D + 0.003, 0.02), al, g, 0.004))
    objs.append(box("rail_f", (W + 0.03, 0.02, 0.03), (0, -0.003, 0.018), al, g, 0.004))
    for sx in (-1, 1):
        for y in (0.04, D - 0.04):
            objs.append(cyl("foot", 0.012, 0.012, (sx * 0.5, y, 0.004), rb, g, bevel=0.002))
    # raise the back: whole board rotated about its front-bottom edge
    for o in objs:
        o.matrix_basis = Matrix.Rotation(tilt, 4, "X") @ o.matrix_basis
    return objs


ZB = 0.40  # rack stand height (m)
RACK_X, RACK_Y = 0.62, 0.78


def rack_case(g="room", loc=(RACK_X, RACK_Y, 0)):
    """4U open-front rack case on a steel-tube stand: tolex sides, black rails with cage-nut holes, ribbed back panel"""
    W, H, D = 0.54, 0.178 + 0.06, 0.36
    zb = ZB  # stand height
    tol, steel, al = mt.tolex(TH["chassis"]["rack_dark"]["body"]), mt.steel_black(0.4), mt.brushed(TH["jack"], 0.35)
    x0, y0 = loc[0], loc[1]
    o = []
    o += [box("rc_l", (0.022, D, H), (x0 - W / 2 + 0.011, y0 + D / 2, zb + H / 2), tol, g, 0.004), box("rc_r", (0.022, D, H), (x0 + W / 2 - 0.011, y0 + D / 2, zb + H / 2), tol, g, 0.004)]
    o += [box("rc_t", (W, D, 0.022), (x0, y0 + D / 2, zb + H - 0.011), tol, g, 0.004), box("rc_b", (W, D, 0.022), (x0, y0 + D / 2, zb + 0.011), tol, g, 0.004)]
    o.append(box("rc_back", (W - 0.04, 0.012, H - 0.04), (x0, y0 + D - 0.006, zb + H / 2), mt.satin(TH["chassis"]["rack_dark"]["face"], 0.7), g, 0.002))
    for sx in (-1, 1):  # rack rails with cage-nut holes (dark squares)
        o.append(box("rail", (0.019, 0.004, H - 0.044), (x0 + sx * 0.2425, y0 + 0.002, zb + H / 2), steel, g, 0.0008))
        for i in range(7):
            o.append(box("hole", (0.007, 0.0016, 0.007), (x0 + sx * 0.2425, y0 - 0.0002, zb + 0.03 + i * 0.0245), mt.rubber(0.9, TH["rubber"]), g, 0.0004))
    o.append(box("rack_blank", (0.482, 0.003, 0.0425), (x0, y0 - 0.001, zb + 0.208 - 0.022 - 3 * 0.044), mt.brushed(TH["chassis"]["rack_dark"]["face"], 0.45), g, 0.0008))  # 4th slot: blank panel
    for sx in (-1, 1):  # carry handles + corner protectors
        o.append(cyl("handle", 0.006, 0.12, (x0 + sx * (W / 2 + 0.02), y0 + D / 2, zb + H / 2), al, g, "y", 0.002, 24))
        for sy in (0.0, D):
            for sz in (0, H):
                o.append(box("cp", (0.034, 0.034, 0.034), (x0 + sx * (W / 2 - 0.012), y0 + sy, zb + sz), al, g, 0.004))
    for sx in (-1, 1):  # stand legs + cross bars
        for sy in (0.03, D - 0.03):
            o.append(cyl("leg", 0.017, zb, (x0 + sx * (W / 2 - 0.03), y0 + sy, zb / 2), steel, g, "z", 0.001, 24))
            o.append(cyl("cap", 0.02, 0.012, (x0 + sx * (W / 2 - 0.03), y0 + sy, 0.005), mt.rubber(), g, "z", 0.002, 24))
    o.append(cyl("bar", 0.008, W - 0.06, (x0, y0 + 0.03, zb * 0.4), steel, g, "x", 0.001, 24))
    o.append(cyl("bar", 0.008, W - 0.06, (x0, y0 + D - 0.03, zb * 0.4), steel, g, "x", 0.001, 24))
    for sx in (-1, 1):
        o.append(cyl("bar", 0.008, D - 0.06, (x0 + sx * (W / 2 - 0.03), y0 + D / 2, zb * 0.4), steel, g, "y", 0.001, 24))
        o.append(cyl("bar", 0.01, D - 0.06, (x0 + sx * (W / 2 - 0.03), y0 + D / 2, zb - 0.012), steel, g, "y", 0.001, 24))
    return o


# ---------------- gear ----------------
def knob_body(name, loc, dia, h, hexcol, group, metal=False, axis="y"):
    """stage knob: knurled cylinder (no pointer: QML draws it)"""
    m = mt.metal_knob(hexcol) if metal else mt.knob(hexcol)
    if metal:
        return star_cyl(name, dia / 2, h, 36, loc, m, group, axis)
    return star_cyl(name, dia / 2, h, 24, loc, m, group, axis)


def head(fam, loc, group="head"):
    """amp head 0.74 x 0.26 x 0.27: tolex box, inset control panel (6 knobs), handle, jewel, vents, feet. front face at y=loc.y"""
    ch = TH["chassis"][fam]
    W, D, H = 0.74, 0.26, 0.27
    x0, y0, z0 = loc
    tol, chrome = mt.tolex(ch["body"]), mt.chrome()
    anod = fam in ("brit_gold", "copper")
    pan = mt.painted(ch["face"], anod)
    al = mt.brushed(TH["metal"], 0.3)
    cz = z0 + 0.02  # on 20 mm feet
    o = [box("h_body", (W, D, H), (x0, y0 + D / 2, cz + H / 2), tol, group, 0.007, 4)]
    for sx in (-1, 1):
        for sy in (0.012, D - 0.012):
            o.append(cyl("foot", 0.016, 0.02, (x0 + sx * (W / 2 - 0.05), y0 + sy + 0.02, z0 + 0.01), mt.rubber(), group, bevel=0.003, seg=24))
    for sx in (-1, 1):
        for sz in (0.014, H - 0.014):
            for sy in (0.004, D - 0.004):
                o.append(box("cp", (0.034, 0.034, 0.034), (x0 + sx * (W / 2 - 0.012), y0 + sy, cz + sz), al, group, 0.004))
    fy = y0 - 0.0006
    o.append(box("h_trim", (0.696, 0.003, 0.158), (x0, fy + 0.0015, cz + 0.145), al, group, 0.0012))
    o.append(box("h_panel", (0.686, 0.003, 0.148), (x0, fy - 0.0012, cz + 0.145), pan, group, 0.001))
    o.append(box("h_nameplate", (0.30, 0.0012, 0.026), (x0 - 0.17, fy - 0.0030, cz + 0.19), mt.satin(TH["rubber"], 0.35), group, 0.0004))
    for i, (sx, sz) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
        o += screw("h_screw", (x0 + sx * 0.329, fy - 0.0032, cz + 0.145 + sz * 0.064), group, 0.6 * i)
    kx = [-0.21 + 0.09 * i for i in range(6)]
    kz = cz + 0.135
    for i, x in enumerate(kx):
        o.append(knob_body(f"knob{i}", (x0 + x, fy - 0.0155, kz), 0.031, 0.022, ch["knob"], group, metal=True))
        o.append(cyl(f"kring{i}", 0.0235, 0.0016, (x0 + x, fy - 0.0028, kz), mt.satin(ch["ink"], 0.6), group, "y", 0.0003, 48))
    for k, z in enumerate((cz + 0.115, cz + 0.155)):  # two input jacks, left
        o.append(cyl(f"jack{k}", 0.0075, 0.014, (x0 - 0.305, fy - 0.007, z), chrome, group, "y", 0.001, 24))
        o.append(cyl(f"jackh{k}", 0.004, 0.015, (x0 - 0.305, fy - 0.0075, z), mt.rubber(0.4, TH["rubber"]), group, "y", 0, 16))
    o.append(box("sw", (0.016, 0.01, 0.022), (x0 + 0.305, fy - 0.004, cz + 0.095), chrome, group, 0.002))
    jewel = cyl("jewel_ring", 0.0125, 0.008, (x0 + 0.305, fy - 0.004, cz + 0.19), chrome, group, "y", 0.001, 32)
    led = sphere("jewel", 0.0095, (x0 + 0.305, fy - 0.0085, cz + 0.19), mt.led(TH["pilot"], 0.0), group)
    led.scale = (1, 0.7, 1)
    o += [jewel, led]
    lea = mt.leather(TH["board_tolex"])
    o.append(box("handle", (0.24, 0.022, 0.02), (x0, y0 + D / 2, cz + H + 0.032), lea, group, 0.008))
    for sx in (-1, 1):
        o.append(box("hbr", (0.026, 0.028, 0.034), (x0 + sx * 0.125, y0 + D / 2, cz + H + 0.012), al, group, 0.004))
    for i in range(14):  # vent slots, top
        o.append(box("vent", (0.006, 0.07, 0.0009), (x0 - 0.2 + i * 0.0308, y0 + D * 0.62, cz + H + 0.0004), mt.rubber(0.9, TH["rubber"]), group, 0.0002, 1))
    return o


CAB = {1: (0.62, 0.50, 0.28), 2: (0.74, 0.50, 0.28), 4: (0.76, 0.50, 0.34)}  # same height: the head sits at one fixed spot for every cab


def cabinet(fam, n, loc, group="cab"):
    """speaker cabinet: tolex box, grille cloth over speaker rings, aluminium piping, corners, feet, side handle"""
    ch = TH["chassis"][fam]
    W, H, D = CAB[n]
    x0, y0, z0 = loc
    tol, al = mt.tolex(ch["body"]), mt.brushed(ch["knob"], 0.3)
    z0 += 0.025
    o = [box("c_body", (W, D, H), (x0, y0 + D / 2, z0 + H / 2), tol, group, 0.007, 4)]
    for sx in (-1, 1):
        for sy in (0.04, D - 0.04):
            o.append(cyl("foot", 0.017, 0.025, (x0 + sx * (W / 2 - 0.06), y0 + sy, z0 - 0.0125), mt.rubber(), group, bevel=0.003, seg=24))
    ins = 0.03
    cw, ch_ = W - 2 * ins, H - 2 * ins
    o.append(box("c_recess", (cw, 0.002, ch_), (x0, y0 + 0.08, z0 + H / 2), mt.satin(palette.mix_hex(TH["wood_hi"], TH["rubber"], 0.3), 0.9), group, 0.001))  # pale baffle: the cones read against it through the cloth
    spk = []
    cols = {1: [(0, 0)], 2: [(-1, 0), (1, 0)], 4: [(-1, -1), (1, -1), (-1, 1), (1, 1)]}[n]
    for i, (cx, cz_) in enumerate(cols):
        sx = x0 + cx * cw / (4 if n > 1 else 2) * (1 if n > 1 else 0)
        sz = z0 + H / 2 + cz_ * ch_ / 4
        r = min(0.155, cw / (2.4 if n > 1 else 2.2), ch_ / (4.6 if n == 4 else 2.2))
        spk.append((0.5 + (sx - x0) / cw, 0.5 + (sz - (z0 + H / 2)) / ch_, r * 0.95))
        o.append(cyl(f"sp_ring{i}", r, 0.03, (sx, y0 + 0.05, sz), mt.rubber(0.7, TH["rubber"]), group, "y", 0.004, 48))
        o.append(cyl(f"sp_cone{i}", r * 0.82, 0.02, (sx, y0 + 0.055, sz), mt.satin(palette.mix_hex(TH["cone"], TH["rubber"], 0.55), 0.85), group, "y", 0.004, 48, r2=r * 0.25))
    o.append(box("c_cloth", (cw, 0.003, ch_), (x0, y0 - 0.0015, z0 + H / 2), mt.cloth(ch["face"], 0.9 if fam == "grille_black" else 0.1, 1.0, 170.0, spk, (cw, ch_)), group, 0.0006, 1))
    for sx in (-1, 1):  # piping: aluminium frame bars
        o.append(box("pipe_v", (0.006, 0.006, ch_ + 0.012), (x0 + sx * (cw / 2 + 0.003), y0 - 0.002, z0 + H / 2), al, group, 0.0015))
    for sz in (-1, 1):
        o.append(box("pipe_h", (cw + 0.012, 0.006, 0.006), (x0, y0 - 0.002, z0 + H / 2 + sz * (ch_ / 2 + 0.003)), al, group, 0.0015))
    for sx in (-1, 1):
        for sz in (0.016, H - 0.016):
            for sy in (0.006, D - 0.006):
                o.append(box("cp", (0.034, 0.034, 0.034), (x0 + sx * (W / 2 - 0.012), y0 + sy, z0 + sz), al, group, 0.004))
    o.append(box("c_handle", (0.016, 0.1, 0.034), (x0 + W / 2 + 0.003, y0 + D / 2, z0 + H * 0.78), mt.rubber(0.5, TH["rubber"]), group, 0.006))
    return o


def stompbox(fam, loc, group, k=1.7, kh=1.3, tilt=math.radians(8), nknobs=3, block="DST", led_hex=None):
    """die-cast pedal (0.073 x 0.129 x 0.052 m times k): powder coat, knob row, blank label recess, LED, chrome footswitch, side jacks.
    Built at the origin (front-centre bottom) then tilted onto the deck."""
    ch = TH["chassis"][fam]
    w, d, h = 0.073 * k, 0.129 * k, 0.052 * kh
    body, chrome = mt.powder(ch["body"]), mt.chrome()
    o = [box("s_body", (w, d, h), (0, d / 2, h / 2), body, group, 0.0045 * k, 4)]
    o.append(box("s_lip", (w * 0.96, d * 0.97, 0.0008), (0, d / 2, h + 0.0003), body, group, 0.0003, 1))
    # blank label recess (QML prints the name here)
    o.append(box("s_label", (w * 0.8, d * 0.22, 0.0008), (0, d * 0.5, h + 0.0004), mt.satin(ch["face"], 0.5), group, 0.0003, 1))
    for i in range(nknobs):
        x = (i - (nknobs - 1) / 2) * w * 0.28 if nknobs > 1 else 0
        o.append(knob_body(f"k{i}", (x, d * 0.8, h + 0.0095 * k), 0.0235 * k, 0.019 * k, ch["knob"], group, axis="z"))
    ledo = sphere("led", 0.0035 * k, (0, d * 0.66, h + 0.0012), mt.led(led_hex or TH["block_colors"][block], 0.0), group)
    ledo.scale = (1, 1, 0.7)
    o.append(ledo)
    o.append(cyl("led_bezel", 0.0055 * k, 0.0014, (0, d * 0.66, h + 0.0005), chrome, group, "z", 0.0004, 24))
    sw_y = d * 0.24
    o.append(cyl("fs_base", 0.0155 * k, 0.004, (0, sw_y, h + 0.002), chrome, group, "z", 0.001, 40))
    o.append(cyl("fs", 0.0125 * k, 0.014 * k, (0, sw_y, h + 0.007 * k + 0.002), mt.brushed(TH["metal"], 0.2), group, "z", 0.003, 40))
    for sx in (-1, 1):
        o.append(hexnut("jn", 0.0058 * k, 0.003, (sx * (w / 2 + 0.0008), d * 0.78, h * 0.5), chrome, group, "x"))
        o.append(cyl("jh", 0.0033 * k, 0.0035, (sx * (w / 2 + 0.0022), d * 0.78, h * 0.5), mt.rubber(0.4, TH["rubber"]), group, "x", 0, 16))
    for o_ in o:
        o_.matrix_basis = Matrix.Translation(loc) @ Matrix.Rotation(tilt, 4, "X") @ o_.matrix_basis
    return o


def rack_unit(block, slot, loc=None, group="rack"):
    """1U rack effect (0.482 x 0.044 face, 0.2 deep) in slot `slot` (0 = top) of the case: brushed face, ears with screws, display window, knobs, buttons"""
    x0, y0 = loc or (RACK_X, RACK_Y)
    zc = ZB + 0.208 - 0.022 - slot * 0.044
    ch = TH["chassis"]["rack_dark"]
    pan, al, chrome = mt.painted(ch["face"]), mt.brushed(TH["metal"], 0.45), mt.chrome()
    fy = y0 - 0.0015
    o = [box("ru_body", (0.45, 0.2, 0.040), (x0, y0 + 0.1, zc), mt.steel_black(0.5), group, 0.002)]
    o.append(box("ru_face", (0.482, 0.003, 0.0425), (x0, fy, zc), pan, group, 0.0008))
    for sx in (-1, 1):
        o.append(box("ru_ear", (0.016, 0.0035, 0.0425), (x0 + sx * 0.233, fy - 0.0003, zc), al, group, 0.0006))
        for dz in (-0.014, 0.014):
            o += screw("ru_screw", (x0 + sx * 0.233, fy - 0.0028, zc + dz), group, 0.9 * slot + dz * 100)
    o.append(box("ru_disp", (0.108, 0.0012, 0.026), (x0 - 0.1, fy - 0.0021, zc + 0.002), mt.glass_dark(), group, 0.0004, 1))
    nk = {"MOD": 3, "DLY": 4, "RVB": 3}[block]
    for i in range(nk):
        o.append(knob_body(f"rk{i}", (x0 + 0.01 + i * 0.045, fy - 0.0095, zc + 0.001), 0.022, 0.014, ch["knob"], group, axis="y"))
    for i in range(3):
        o.append(box("ru_btn", (0.012, 0.004, 0.007), (x0 + 0.165 + i * 0.022, fy - 0.0035, zc - 0.008), chrome, group, 0.0012, 2))
    led = sphere("led", 0.0028, (x0 + 0.19, fy - 0.003, zc + 0.012), mt.led(TH["block_colors"][block], 0.0), group)
    led.scale = (1, 0.7, 1)
    return o + [led]


def eq_box(fam, loc, group, k=1.7, kh=1.3, tilt=math.radians(8), n=7):
    """graphic-EQ pedal: die-cast box, n dark fader slots on the upper face (thumbs are live sprites), footswitch, LED"""
    ch = TH["chassis"][fam]
    w, d, h = 0.073 * k, 0.129 * k, 0.052 * kh
    chrome = mt.chrome()
    o = [box("e_body", (w, d, h), (0, d / 2, h / 2), mt.powder(ch["body"]), group, 0.0045 * k, 4)]
    o.append(box("e_plate", (w * 0.88, d * 0.5, 0.001), (0, d * 0.66, h + 0.0004), mt.satin(ch["face"], 0.5), group, 0.0003, 1))
    for i in range(n):
        o.append(box(f"slot{i}", (0.0035, d * 0.4, 0.0012), ((i - (n - 1) / 2) * w * 0.115, d * 0.66, h + 0.0009), mt.rubber(0.8, TH["rubber"]), group, 0.0004, 1))
    ledo = sphere("led", 0.0035 * k, (0, d * 0.34, h + 0.0012), mt.led(TH["block_colors"]["EQ"], 0.0), group)
    ledo.scale = (1, 1, 0.7)
    o += [ledo, cyl("led_bezel", 0.0055 * k, 0.0014, (0, d * 0.34, h + 0.0005), chrome, group, "z", 0.0004, 24)]
    sw_y = d * 0.16
    o.append(cyl("fs_base", 0.0155 * k, 0.004, (0, sw_y, h + 0.002), chrome, group, "z", 0.001, 40))
    o.append(cyl("fs", 0.0125 * k, 0.014 * k, (0, sw_y, h + 0.007 * k + 0.002), mt.brushed(TH["metal"], 0.3), group, "z", 0.003, 40))
    for o_ in o:
        o_.matrix_basis = Matrix.Translation(loc) @ Matrix.Rotation(tilt, 4, "X") @ o_.matrix_basis
    return o


def treadle(block, loc, group, tilt=math.radians(8), rock=0.0, w=0.15, d=0.3):
    """expression/volume treadle: cast base, rocker footplate with rubber ribs rotated `rock` radians about the hinge, side plates, LED"""
    ch = TH["chassis"]["treadle_black"]
    body, chrome, rb = mt.powder(ch["body"]), mt.chrome(), mt.rubber(0.8)
    hy, hz = d * 0.28, 0.05  # hinge line
    o = [box("t_base", (w, d, 0.045), (0, d / 2, 0.0225), body, group, 0.006, 3)]
    for sx in (-1, 1):
        o.append(box("t_side", (0.012, d * 0.55, 0.05), (sx * (w / 2 - 0.006), hy + 0.02, 0.04), mt.brushed(TH["metal"], 0.4), group, 0.002))
    rock_objs = [box("t_plate", (w * 0.86, d * 0.82, 0.022), (0, d * 0.45, hz + 0.011), body, group, 0.004, 3)]
    for i in range(11):
        rock_objs.append(box("t_rib", (w * 0.74, 0.008, 0.0028), (0, d * 0.12 + i * d * 0.065, hz + 0.0235), rb, group, 0.001, 1))
    rock_objs.append(box("t_heel", (w * 0.86, 0.03, 0.012), (0, d * 0.88, hz + 0.004), rb, group, 0.003))
    pivot = Matrix.Translation((0, hy, hz)) @ Matrix.Rotation(rock, 4, "X") @ Matrix.Translation((0, -hy, -hz))
    for r_ in rock_objs:
        r_.matrix_basis = pivot @ r_.matrix_basis
    ledo = sphere("led", 0.004, (w * 0.3, d * 0.08, 0.048), mt.led(TH["block_colors"][block], 0.0), group)
    ledo.scale = (1, 1, 0.7)
    o += rock_objs + [ledo, cyl("led_bezel", 0.0065, 0.002, (w * 0.3, d * 0.08, 0.046), chrome, group, "z", 0.0004, 24)]
    for o_ in o:
        o_.matrix_basis = Matrix.Translation(loc) @ Matrix.Rotation(tilt, 4, "X") @ o_.matrix_basis
    return o


def plug(kind, side, group="plug"):
    """1/4 inch plug lying along x with the tip at x=0 pointing +x (side L) or -x (R); straight or right-angle boot. Metres."""
    chrome, rb = mt.chrome(), mt.rubber(0.55, TH["rubber"])
    s = 1 if side == "L" else -1
    o = [cyl("tip", 0.0032, 0.014, (-s * 0.007, 0, 0), chrome, group, "x", 0.0008, 24)]
    o.append(cyl("sleeve", 0.0065, 0.026, (-s * 0.027, 0, 0), chrome, group, "x", 0.0012, 32))
    if kind == "s":
        o.append(cyl("boot", 0.0085, 0.03, (-s * 0.055, 0, 0), rb, group, "x", 0.003, 32))
        o.append(cyl("relief", 0.0058, 0.03, (-s * 0.085, 0, 0), rb, group, "x", 0.002, 24, r2=0.0035))
    else:
        o.append(cyl("boot", 0.0085, 0.022, (-s * 0.051, 0, 0), rb, group, "x", 0.003, 32))
        o.append(cyl("elbow", 0.0085, 0.02, (-s * 0.062, 0, -0.011), rb, group, "z", 0.003, 32))
        o.append(cyl("relief", 0.0058, 0.03, (-s * 0.062, 0, -0.035), rb, group, "z", 0.002, 24, r2=0.0035))
    return o


# ---------------- wooden room (2C revision) ----------------
import random

LAMP_XY = (1.9, 0.9)


def wall_planks(y, g="room"):
    """vertical 12 cm planks with 4 mm V-groove gaps over a dark backing"""
    wood = mt.wood(TH["wood_lo"], TH["wood_hi"], "X")
    o = [box("wall_back", (9.0, 0.02, 3.2), (0, y + 0.028, 1.6), mt.satin(TH["floor_lo"], 0.8), g, 0, 1)]
    for i in range(-37, 38):
        o.append(box(f"wall_plank{i}", (0.116, 0.018, 3.0), (i * 0.12, y + 0.009, 1.5), wood, g, 0.003, 2))
    return o


def trim(y, g="room"):
    """chair rail (z 0.9) and skirting, darker varnished stain"""
    w = mt.wood(TH["floor_lo"], TH["wood_lo"], "Y")
    return [box("chair_rail", (9, 0.025, 0.06), (0, y - 0.0125, 0.9), w, g, 0.005),
            box("skirting", (9, 0.02, 0.12), (0, y - 0.01, 0.06), w, g, 0.005),
            box("skirting_top", (9, 0.012, 0.012), (0, y - 0.022, 0.126), w, g, 0.003)]


def floor_planks(g="room"):
    """0.18 m oak planks, random lengths 0.9-1.8 m, 2 mm gaps"""
    rnd = random.Random(200)
    wood = mt.wood(TH["floor_lo"], TH["floor_hi"], "Y", coat=0.5, coat_rough=0.15)
    o = [box("floor_base", (12, 6, 0.02), (0, 0.8, -0.012), mt.satin(TH["floor_lo"], 0.8), g, 0, 1)]
    for r in range(-8, 8):
        x = -4.5 - rnd.random() * 1.0
        while x < 4.5:
            ln = rnd.uniform(0.9, 1.8)
            o.append(box(f"floor_plank{r}_{len(o)}", (ln - 0.002, 0.178, 0.012), (x + ln / 2, r * 0.18 + 0.09, -0.004), wood, g, 0.0015, 2))
            x += ln
    return o


def rug_obj(g="room"):
    """2.6 x 1.5 m rug, 8 mm pile, black bound edge strip below"""
    return [box("rug_edge", (2.63, 1.53, 0.006), (0, 0.35, 0.003), mt.rug_bound(), g, 0.003),
            box("rug", (2.6, 1.5, 0.008), (0, 0.35, 0.008), mt.rug(), g, 0.003)]


def framed_panels(zc, g="room"):
    """two acoustic panels (0.6 m, dark umber fabric) in varnished wood frames"""
    frame = mt.wood(TH["wood_lo"], TH["wood_hi"], "X", coat=0.3)
    cloth = mt.panel_cloth(TH["panel_cloth"])
    o = []
    for x in (-1.15, 1.15):
        for dx, dz, sw, sh in ((0, 0.31, 0.64, 0.04), (0, -0.31, 0.64, 0.04), (-0.31, 0, 0.04, 0.58), (0.31, 0, 0.04, 0.58)):
            o.append(box("pframe", (sw, 0.05, sh), (x + dx, WALL_Y_ - 0.025, zc + dz), frame, g, 0.004, 2))
        o.append(box("acoustic", (0.58, 0.04, 0.58), (x, WALL_Y_ - 0.02, zc), cloth, g, 0.006, 3))
    return o


WALL_Y_ = 1.3


def floor_lamp(shade_hex, g="room"):
    """floor lamp: steel pole + base, open drum shade glowing warm, bulb inside"""
    x, y = LAMP_XY
    steel = mt.steel_black(0.4)
    o = [cyl("lamp_base", 0.14, 0.02, (x, y, 0.012), steel, g, "z", 0.005, 40), cyl("lamp_pole", 0.011, 1.2, (x, y, 0.62), steel, g, "z", 0.001, 16)]
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=False, segments=48, radius1=0.2, radius2=0.15, depth=0.3)
    sh = _obj("lamp_shade", bm, mt.lampshade(shade_hex), g, (x, y, 1.45))
    sh.visible_shadow = False
    o.append(sh)
    o.append(sphere("lamp_bulb", 0.03, (x, y, 1.42), mt.matte_emitter(shade_hex, 400.0), g))
    return o

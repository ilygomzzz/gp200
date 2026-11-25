"""Render pipeline for the pedalboard rig (spec 004 phase 2C). Run inside Blender, no network, no files outside the repo:
  blender -b -P tools/render/rig.py -- JOB [--cpu] [--samples N] [--preview] [--out DIR] [--scratch DIR]
JOB = matsheet | plate | slice | knob | all (all = slice for now). Deterministic: seed 200, fixed samples, sorted manifest."""
import json
import re
import math
import struct
import sys
import time
import zlib
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import materials as mt  # noqa: E402
import models as md  # noqa: E402
import palette  # noqa: E402

ROOT = HERE.parents[1]
TH = mt.TH
SU = 1.5  # px per stage unit
PW, PH = 2400, 780
F, CAM, PITCH, V_BOARD = 16.0, Vector((0, -1.2, 0.65)), 6.0, 505.0  # lens mm, camera m, pitch deg, board-front row in su
WALL_Y, TILT = 1.3, math.radians(8)
IN_UV, OUT_UV = (70, 470), (1500, 232)  # Guitarra input box (floor) / Salida wall plate, stage units
H_MM = 36 * 520 / 1600
EXPOSURE = 0.0
METER_TARGET = 0.07  # scene-linear mean luminance of the rug under the key (design says 0.18; a dark-red rug at 0.18 blows out)
LOG = []
ROOM_PARTS = {}
WORLD_K = 0.03  # faint warm room tone: gives dull metals a reflection to show (world was 0)


# ---------------- colour helpers (computed from theme tokens, never literal hex) ----------------
def _lin2hex(c):
    s = [(12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055) for v in c]
    return "#" + "".join(f"{round(max(0, min(1, x)) * 255):02x}" for x in s)


def lift(h, k):
    return _lin2hex([min(1, v * k) for v in palette.hex_to_linear(h)])


def mixhex(a, b, t):
    return _lin2hex([x * (1 - t) + y * t for x, y in zip(palette.hex_to_linear(a), palette.hex_to_linear(b))])


def kelvin(k):
    """blackbody -> linear rgb (Tanner Helland fit)"""
    t = k / 100.0
    r = 255 if t <= 66 else 329.7 * (t - 60) ** -0.1332
    g = 99.47 * math.log(t) - 161.1 if t <= 66 else 288.12 * (t - 60) ** -0.0755
    b = 255 if t >= 66 else (0 if t <= 19 else 138.52 * math.log(t - 10) - 305.04)
    return [(max(0, min(255, v)) / 255) ** 2.2 for v in (r, g, b)]


# ---------------- projection (stage units) ----------------
def _raw(x, y, z):
    a = math.radians(PITCH)
    dy, dz = y - CAM.y, z - CAM.z
    fw, up = dy * math.cos(a) - dz * math.sin(a), dy * math.sin(a) + dz * math.cos(a)
    return F * x / fw / 36 * 1600, F * up / fw


SH = (260 - V_BOARD) / 520 * H_MM - _raw(0, 0, 0)[1]  # lens shift in mm (content moves up when positive)


def proj(x, y, z):
    u, up = _raw(x, y, z)
    return 800 + u, 260 - (up + SH) / H_MM * 520


def unproject(u, v, plane_y):
    """world point on the plane y=plane_y seen at stage coords (u, v)"""
    a = math.radians(PITCH)
    dirc = (((u - 800) / 1600 * 36) / F, 1.0, ((260 - v) / 520 * H_MM - SH) / F)  # (x, fwd, up) per unit forward
    # camera basis: fwd=(0,cos a,-sin a), up=(0,sin a,cos a)
    d = Vector((dirc[0], math.cos(a) - dirc[2] * -math.sin(a) * -1 * 0 + 0, 0))
    fwd, upv = Vector((0, math.cos(a), -math.sin(a))), Vector((0, math.sin(a), math.cos(a)))
    ray = fwd + upv * dirc[2] + Vector((dirc[0], 0, 0))
    t = (plane_y - CAM.y) / ray.y
    return CAM + ray * t


# ---------------- scene / device ----------------
def reset(exposure=True):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    md.GROUPS.clear()
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    c = sc.cycles
    c.seed, c.use_adaptive_sampling, c.adaptive_threshold = 200, True, 0.01
    c.max_bounces, c.glossy_bounces, c.transmission_bounces, c.diffuse_bounces, c.transparent_max_bounces = 12, 6, 4, 6, 12
    c.sample_clamp_indirect = 10.0
    c.use_denoising, c.denoiser = True, "OPENIMAGEDENOISE"
    try:
        c.denoising_input_passes = "RGB_ALBEDO_NORMAL"
    except Exception:
        pass
    sc.view_settings.view_transform = "AgX"
    looks = [i.identifier for i in sc.view_settings.bl_rna.properties["look"].enum_items]
    pick = [x for x in looks if "Medium High Contrast" in x]
    if pick:
        sc.view_settings.look = pick[0]
    sc.view_settings.exposure = EXPOSURE if exposure else 0.0
    sc.render.image_settings.compression = 15
    w = bpy.data.worlds.new("w")
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs["Strength"].default_value = WORLD_K
    w.node_tree.nodes["Background"].inputs["Color"].default_value = (*kelvin(2900), 1.0)
    sc.world = w
    return sc


def device(cpu):
    sc = bpy.context.scene
    if not cpu:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        for t in ("OPTIX", "CUDA"):
            try:
                prefs.compute_device_type = t
                prefs.get_devices()
            except Exception:
                continue
            devs = [d for d in prefs.devices if d.type == t]
            if devs:
                for d in prefs.devices:
                    d.use = d.type == t
                sc.cycles.device = "GPU"
                return t
    sc.cycles.device = "CPU"
    return "CPU"


def camera(ortho=None, loc=None, rot=None, fit=True):
    cam = bpy.data.cameras.new("cam")
    o = bpy.data.objects.new("cam", cam)
    bpy.context.scene.collection.objects.link(o)
    bpy.context.scene.camera = o
    if ortho:
        cam.type, cam.ortho_scale = "ORTHO", ortho
        o.location, o.rotation_euler = loc, rot
    else:
        cam.lens, cam.sensor_width, cam.sensor_fit = F, 36.0, "HORIZONTAL"
        cam.shift_y = -SH / 36
        o.location = CAM
        o.rotation_euler = (math.radians(90 - PITCH), 0, 0)
    cam.clip_start, cam.clip_end = 0.01, 40
    return o


def area(name, loc, target, size, watts, kelvin_k, sizey=None, spread=None):
    ld = bpy.data.lights.new(name, "AREA")
    ld.shape, ld.size, ld.size_y, ld.energy = "RECTANGLE", size, sizey or size, watts
    ld.color = kelvin(kelvin_k)
    if spread:
        ld.spread = spread
    o = bpy.data.objects.new(name, ld)
    o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.collection.objects.link(o)
    return o


def spot(name, loc, target, deg, blend, watts, kelvin_k):
    ld = bpy.data.lights.new(name, "SPOT")
    ld.energy, ld.spot_size, ld.spot_blend, ld.color, ld.shadow_soft_size = watts, math.radians(deg), blend, kelvin(kelvin_k), 0.15
    o = bpy.data.objects.new(name, ld)
    o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.collection.objects.link(o)
    return o


def room_lights():
    """warm practicals + key (world is black: reflections come from the room itself); kelvin per design table"""
    area("key", (-1.3, -0.6, 2.2), (0.0, 0.7, 0.6), 0.7, 260, 3200, 0.5, math.radians(50))
    area("fill", (0.6, -1.6, 1.4), (0.0, 0.7, 0.4), 2.0, 45, 3000, 1.5)
    spot("rim", (0.4, 1.15, 2.3), (0.0, 0.3, 0.6), 40, 0.7, 120, 3000)


def point(name, loc, watts, k, r=0.03):
    pl = bpy.data.lights.new(name, "POINT")
    pl.energy, pl.color, pl.shadow_soft_size = watts, kelvin(k), r
    po = bpy.data.objects.new(name, pl)
    po.location = loc
    bpy.context.scene.collection.objects.link(po)


def floor_pt(u, v, z=0.0):
    """world point on the plane z=`z` seen at stage coords (u, v)"""
    p0, p1 = unproject(u, v, 0.0), unproject(u, v, 1.0)
    t = (z - p0.z) / (p1.z - p0.z)
    return p0 + (p1 - p0) * t


def build_room():
    g = "room"
    md.floor_planks()
    md.rug_obj()
    md.wall_planks(WALL_Y)
    md.trim(WALL_Y)
    top = unproject(800, 0, WALL_Y).z
    md.framed_panels(top - 0.5)
    # lived-in props: spare cable coiled on the rug, mic stand, floor lamp
    from bpy import data as D
    cv = D.curves.new("cable", "CURVE")
    cv.dimensions, cv.bevel_depth, cv.bevel_resolution = "3D", 0.0045, 4
    sp = cv.splines.new("BEZIER")
    pts = [(-0.95, 0.05, 0.02), (-0.8, 0.3, 0.014), (-0.95, 0.55, 0.014), (-0.7, 0.62, 0.014), (-0.6, 0.35, 0.014), (-0.75, 0.15, 0.014)]
    sp.bezier_points.add(len(pts) - 1)
    for p, q in zip(sp.bezier_points, pts):
        p.co, p.handle_left_type, p.handle_right_type = q, "AUTO", "AUTO"
    co = D.objects.new("cable", cv)
    co.data.materials.append(mt.rubber(0.5, TH["cable"]))
    bpy.context.scene.collection.objects.link(co)
    ms, mx, my = mt.steel_black(0.35), -1.25, 0.8
    md.cyl("mic_pole", 0.011, 1.5, (mx, my, 0.75), ms, g, "z", 0.001, 16)
    md.cyl("mic_boom", 0.008, 0.55, (mx + 0.22, my, 1.52), ms, g, "x", 0.001, 16)
    md.cyl("mic_head", 0.03, 0.09, (mx + 0.5, my, 1.52), mt.rubber(0.4), g, "z", 0.004, 24)
    md.cyl("mic_base", 0.16, 0.025, (mx, my, 0.0125), ms, g, "z", 0.006, 40)
    # caged practical bulb on the planks, top-left
    bp = unproject(150, 95, WALL_Y - 0.1)
    bx, by, bz = bp.x, WALL_Y - 0.1, bp.z
    steel = mt.steel_black(0.5)
    md.box("lamp_plate", (0.1, 0.012, 0.1), (bx, WALL_Y - 0.006, bz), steel, g, 0.004)
    md.cyl("socket", 0.022, 0.07, (bx, by + 0.03, bz), steel, g, "y", 0.004)
    bulb = md.sphere("bulb", 0.04, (bx, by - 0.04, bz), mt.matte_emitter(kelvin_hex(2700), 80.0), g)
    for i in range(8):
        ang = i * math.pi / 4
        md.cyl("cage", 0.0016, 0.13, (bx + 0.056 * math.cos(ang), by - 0.04, bz + 0.056 * math.sin(ang)), steel, g, "y", 0, 8).location.y = by - 0.02
    for j in (-1, 0, 1):
        md.cyl("ring", 0.058, 0.003, (bx, by - 0.04 + j * 0.05, bz), steel, g, "y", 0, 40, r2=0.058)
    point("practical", (bx, by - 0.12, bz), 35, 2700, 0.04)
    md.floor_lamp(kelvin_hex(2900))
    point("lamp", (md.LAMP_XY[0], md.LAMP_XY[1], 1.42), 18, 2900, 0.04)
    # baked Guitarra input (floor stage box) and Salida wall plate
    gp = floor_pt(*IN_UV, 0.0)
    md.box("in_box", (0.16, 0.09, 0.05), (gp.x, gp.y, 0.025), mt.powder(TH["chassis"]["treadle_black"]["body"]), g, 0.006)
    md.cyl("in_jack", 0.009, 0.02, (gp.x + 0.05, gp.y - 0.045, 0.03), mt.chrome(), g, "y", 0.001, 24)
    sp_ = unproject(*OUT_UV, WALL_Y - 0.01)
    md.box("out_plate", (0.1, 0.012, 0.15), (sp_.x, WALL_Y - 0.017, sp_.z), mt.brushed(TH["metal"], 0.3), g, 0.003)
    md.cyl("out_jack", 0.012, 0.014, (sp_.x, WALL_Y - 0.026, sp_.z), mt.chrome(), g, "y", 0.001, 24)
    md.cyl("out_hole", 0.007, 0.016, (sp_.x, WALL_Y - 0.0275, sp_.z), mt.rubber(0.4, TH["rubber"]), g, "y", 0, 16)
    ROOM_PARTS["deck"] = md.pedalboard(g)
    ROOM_PARTS["rack"] = md.rack_case(g)
    return bulb


def kelvin_hex(k):
    return _lin2hex(kelvin(k))


def deck_pt(x, y_local):
    """world point on the tilted deck's top surface at deck-local depth y"""
    return (x, y_local * math.cos(TILT) - 0.023 * math.sin(TILT), y_local * math.sin(TILT) + 0.023 * math.cos(TILT))



# ---------------- layout: every unit has one zone, derived from its world footprint (front face) ----------------
PED_W = {"PRE": 0.124, "DST": 0.124, "NR": 0.10, "EQ": 0.124, "WAH": 0.15, "VOL": 0.15}  # deck widths (m), left to right
PED_YL = {"WAH": 0.08, "VOL": 0.08}  # deck-local depth of the pedal front (default 0.10)
HEAD_Z = 0.025 + 0.50  # cab top: the head sits here for every cab size


def ped_x():
    """deck-local x centre per pedal: 0.045 m gaps, centred on the 1.1 m deck"""
    gap = 0.045
    x = -(sum(PED_W.values()) + gap * (len(PED_W) - 1)) / 2
    out = {}
    for b, w in PED_W.items():
        out[b] = x + w / 2
        x += w + gap
    return out


def box_rect(x0, x1, y0, y1, z0, z1):
    pts = [proj(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]
    us, vs = [p[0] for p in pts], [p[1] for p in pts]
    return [min(us), min(vs), max(us) - min(us), max(vs) - min(vs)]


def layout_zones():
    """stage-unit rect per block: pedals = projected tilted footprint, cab/head = front faces (head clamped under the cab top), rack = face of its slot"""
    z = {}
    for b, cx in ped_x().items():
        w, k = PED_W[b], (1.7 if b not in ("WAH", "VOL") else 1.0)
        d, h = (0.129 * k, 0.052 * 1.3) if b not in ("WAH", "VOL") else (0.30, 0.10)
        if b == "NR":
            d, h = 0.129 * 1.35, 0.052 * 1.3
        y0 = PED_YL.get(b, 0.10)
        c = [deck_pt(cx + sx * w / 2, y0 + sy * d) for sx in (-1, 1) for sy in (0, 1)]
        pts = [proj(p[0], p[1], p[2] + sz) for p in c for sz in (0, h)]
        us = [proj(p[0], p[1], p[2] + sz)[0] for p in c[:2] for sz in (0, h)]  # x extent = front edge (the back is foreshortened and tucked behind it)
        vs = [p[1] for p in pts]
        z[b] = [min(us), min(vs), max(us) - min(us), max(vs) - min(vs)]
    for i, b in enumerate(("MOD", "DLY", "RVB")):
        zc = md.ZB + 0.208 - 0.022 - i * 0.044
        z[b] = box_rect(md.RACK_X - 0.241, md.RACK_X + 0.241, md.RACK_Y - 0.002, md.RACK_Y - 0.002, zc - 0.021, zc + 0.021)
    z["CAB"] = box_rect(-0.67, 0.07, 0.9, 0.9, 0.0, HEAD_Z)
    amp = box_rect(-0.67, 0.07, 0.95, 0.95, HEAD_Z + 0.02, HEAD_Z + 0.02 + 0.27 + 0.06)
    amp[3] = min(amp[3], z["CAB"][1] - amp[1])
    z["AMP"] = amp
    return z


# ---------------- image IO ----------------
def render(path, w, h, samples, border=None, fmt="PNG", alpha=True, denoise=True):
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = w, h, 100
    sc.cycles.samples, sc.cycles.use_denoising = samples, denoise
    sc.render.film_transparent = alpha
    sc.render.use_border = border is not None
    if border:
        x0, y0, x1, y1 = border
        sc.render.border_min_x, sc.render.border_max_x = x0 / w, x1 / w
        sc.render.border_min_y, sc.render.border_max_y = 1 - y1 / h, 1 - y0 / h
    sc.render.use_crop_to_border = False
    st = sc.render.image_settings
    st.file_format, st.color_mode = fmt, "RGBA" if alpha else "RGB"
    if fmt == "JPEG":
        st.quality = 90
    sc.render.filepath = str(path)
    t = time.time()
    bpy.ops.render.render(write_still=True)
    LOG.append((Path(path).name, round(time.time() - t, 1)))


def load(path):
    img = bpy.data.images.load(str(path), check_existing=False)
    img.colorspace_settings.name = "Non-Color"
    img.alpha_mode = "STRAIGHT"
    w, h = img.size
    a = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(a)
    bpy.data.images.remove(img)
    a = a.reshape(h, w, 4)[::-1]
    if a.shape[2] == 4 and str(path).endswith((".jpg", ".jpeg")):
        a[..., 3] = 1
    return a


def write_png(path, arr):
    a = np.clip(np.rint(arr * 255), 0, 255).astype(np.uint8)
    h, w, _ = a.shape
    f = a.copy()
    f[:, 1:] = a[:, 1:] - a[:, :-1]  # PNG filter 1 (Sub), wraps mod 256
    raw = b"".join(b"\x01" + f[y].tobytes() for y in range(h))

    def ch(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)

    Path(path).write_bytes(b"\x89PNG\r\n\x1a\n" + ch(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)) + ch(b"IDAT", zlib.compress(raw, 9)) + ch(b"IEND", b""))


def vigmap(w, h):
    """radial multiplier: 1.0 inside 55% of the half-diagonal, smoothstep to 0.72 at the corners"""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r = np.hypot((xx + 0.5 - w / 2), (yy + 0.5 - h / 2)) / math.hypot(w / 2, h / 2)
    t = np.clip((r - 0.55) / 0.45, 0, 1)
    return (1 - 0.28 * t * t * (3 - 2 * t))[..., None].astype(np.float32)


def save_jpg(path, arr, quality=88):
    h, w = arr.shape[:2]
    img = bpy.data.images.new("_j", w, h, alpha=False, float_buffer=False)
    img.colorspace_settings.name = "Non-Color"
    px = np.ones((h, w, 4), np.float32)
    px[..., :3] = np.clip(arr[..., :3], 0, 1)
    img.pixels.foreach_set(px[::-1].ravel())
    img.file_format = "JPEG"
    img.filepath_raw = str(path)
    bpy.context.scene.render.image_settings.quality = quality
    img.save()
    bpy.data.images.remove(img)


def bbox(a, thr=0.5):
    ys, xs = np.where(a[..., 3] > thr)
    return (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1) if len(xs) else None


def over(base, spr, x, y):
    """composite RGBA `spr` (straight alpha) onto RGB/RGBA `base` at (x, y); returns a copy"""
    out = base.copy()
    h, w = spr.shape[:2]
    reg = out[y:y + h, x:x + w, :3]
    al = spr[..., 3:4]
    out[y:y + h, x:x + w, :3] = spr[..., :3] * al + reg * (1 - al)
    return out


def blur(a, n):
    k = np.ones(n) / n
    for ax in (0, 1):
        for _ in range(3):
            a = np.apply_along_axis(lambda m: np.convolve(m, k, "same"), ax, a)
    return a


# ---------------- manifest ----------------
def manifest_update(out, patch):
    p = Path(out) / "manifest.json"
    m = json.loads(p.read_text()) if p.exists() else {"version": 1}

    def merge(a, b):
        for k, v in b.items():
            if isinstance(v, dict) and isinstance(a.get(k), dict):
                merge(a[k], v)
            else:
                a[k] = v
    merge(m, patch)

    def rnd(v):
        if isinstance(v, float):
            return round(v, 1)
        if isinstance(v, dict):
            return {k: rnd(x) for k, x in v.items()}
        if isinstance(v, list):
            return [rnd(x) for x in v]
        return v
    p.write_text(json.dumps(rnd(m), sort_keys=True, indent=1) + "\n")


def su_rect(box_px):
    x0, y0, x1, y1 = box_px
    return [x0 / SU, y0 / SU, (x1 - x0) / SU, (y1 - y0) / SU]


def quad_rect(pts):
    us, vs = [proj(*p)[0] for p in pts], [proj(*p)[1] for p in pts]
    return [min(us), min(vs), max(us) - min(us), max(vs) - min(vs)]


def ell(c, ax_v, r):
    """projected knob: (x, y, r_su, sy) from centre c and the panel's vertical axis"""
    u0, v0 = proj(*c)
    u1, v1 = proj(c[0] + r, c[1], c[2])
    u2, v2 = proj(c[0] + ax_v[0] * r, c[1] + ax_v[1] * r, c[2] + ax_v[2] * r)
    rr = math.hypot(u1 - u0, v1 - v0)
    return {"x": u0, "y": v0, "r": rr, "sy": abs(v2 - v0) / max(rr, 1e-6)}


# ---------------- jobs ----------------
def matsheet(scratch, samples):
    """scratch sheet: one sphere + tile per material under the room lights, on the plank floor in front of the rug"""
    sc = reset()
    LOG.append(("blender", bpy.app.version_string))
    LOG.append(("device", device(ARGS["cpu"])))
    md.floor_planks()
    md.rug_obj()
    mats = [("tolex", mt.tolex(TH["chassis"]["blackface"]["body"])), ("cloth", mt.cloth(TH["chassis"]["grille_silver"]["face"])),
            ("brushed", mt.brushed(TH["metal"], 0.28)), ("chrome", mt.chrome()), ("powder", mt.powder(TH["chassis"]["fuzz_violet"]["body"])),
            ("painted", mt.painted(TH["chassis"]["blackface"]["face"])), ("anodised", mt.painted(TH["chassis"]["brit_gold"]["face"], True)),
            ("rubber", mt.rubber()), ("knob", mt.knob(TH["chassis"]["fuzz_violet"]["knob"])), ("knob_alu", mt.metal_knob(TH["chassis"]["blackface"]["knob"])),
            ("leather", mt.leather(TH["board_tolex"])), ("screw", mt.screw()), ("steel", mt.steel_black()),
            ("wood", mt.wood(TH["wood_lo"], TH["wood_hi"])), ("panel", mt.panel_cloth(TH["panel_cloth"])), ("hook", mt.hook_loop())]
    for i, (n, m) in enumerate(mats):
        x = (i - (len(mats) - 1) / 2) * 0.16
        md.sphere(n, 0.06, (x, -0.55, 0.06), m, "m")
        md.box(n + "_tile", (0.12, 0.12, 0.01), (x, -0.78, 0.005), m, "m", 0.002)
    room_lights()
    camera(ortho=3.0, loc=(0, -3.0, 2.2), rot=(math.radians(58), 0, 0))
    bpy.data.cameras[0].shift_y = 0.0
    render(scratch / "matsheet.png", 1600, 900, samples, alpha=False)


def meter(scratch, samples):
    """exposure by metering: mean scene-linear luminance of the rug beside the board -> METER_TARGET"""
    sc = bpy.context.scene
    vt, lk = sc.view_settings.view_transform, sc.view_settings.look
    sc.view_settings.view_transform, sc.view_settings.look, sc.view_settings.exposure = "Standard", "None", 0.0
    f = 0.4
    render(scratch / "_m.png", int(PW * f), int(PH * f), samples, alpha=False)
    a = load(scratch / "_m.png")[..., :3]
    a = np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
    (u0, v0), (u1, v1) = proj(0.62, 0.4, 0.008), proj(0.95, 0.0, 0.008)
    sl = a[int(v0 * SU * f):int(v1 * SU * f), int(u0 * SU * f):int(u1 * SU * f)]
    lum = float((0.2126 * sl[..., 0] + 0.7152 * sl[..., 1] + 0.0722 * sl[..., 2]).mean())
    sc.view_settings.view_transform, sc.view_settings.look = vt, lk
    ex = round(math.log2(METER_TARGET / max(lum, 1e-5)), 1)
    LOG.append(("meter_lum_at_ev0", round(lum, 4), "exposure", ex))
    return ex


def lum_of(a):
    a = np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
    return 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]


def plate(out, samples, scale=1.0):
    global EXPOSURE
    sc = reset()
    device(ARGS["cpu"])
    build_room()
    room_lights()
    camera()
    EXPOSURE = meter(out, 24)
    sc.view_settings.exposure = EXPOSURE
    w, h = int(PW * scale), int(PH * scale)
    render(out / "_plate.png", w, h, samples, alpha=False)
    a = load(out / "_plate.png")[..., :3]
    L = lum_of(a)
    cy, cx = h // 2, w // 2
    LOG.append(("lum_centre_corner_pre_vig", round(float(L[cy - 40:cy + 40, cx - 80:cx + 80].mean()), 3), round(float(L[:60, :60].mean()), 3), round(float(L[-60:, -60:].mean()), 3)))
    a = a * vigmap(w, h)
    L = lum_of(a)
    LOG.append(("lum_centre_corner_post_vig", round(float(L[cy - 40:cy + 40, cx - 80:cx + 80].mean()), 3), round(float(L[:60, :60].mean()), 3), round(float(L[-60:, -60:].mean()), 3)))
    save_jpg(out / "plate.jpg", a, 88)
    # compact art cell background: dark-red field corner + black border, flattened to <= 1.6:1 motif contrast
    for o in list(bpy.data.objects):
        if o.name.startswith("cam"):
            bpy.data.objects.remove(o)
    camera(ortho=1.0, loc=(1.0, 0.35, 2.2), rot=(0, 0, 0))
    render(out / "_cell.png", 184, 288, max(32, samples // 4), alpha=False)
    c = load(out / "_cell.png")[..., :3]
    mu = c.mean((0, 1))
    save_jpg(out / "cell_bg.jpg", mu + (c - mu) * 0.4, 85)
    zones = layout_zones()
    lanes = {"board_back": proj(0, 0.56, 0.0)[1], "carpet": proj(0, 0.62, 0.0)[1] + 20, "front": proj(0, -0.12, 0.0)[1]}
    cw = [[proj(0, 0.9, 0)[1], 0.006 * (proj(0.5, 0.9, 0)[0] - proj(0, 0.9, 0)[0]) / 0.5], [proj(0, -0.1, 0)[1], 0.006 * (proj(0.5, -0.1, 0)[0] - proj(0, -0.1, 0)[0]) / 0.5]]
    manifest_update(out, {"version": 1, "px_per_su": SU, "stage": [1600, 520], "plate": "plate.jpg", "cell_bg": "cell_bg.jpg", "units": {},
                          "camera": {"horizon": proj(0, WALL_Y, 0)[1], "f": F, "pitch": PITCH, "exposure": EXPOSURE}, "lanes": lanes, "cable_w": cw, "zones": zones,
                          "jacks": {"in": list(proj(*floor_pt(*IN_UV, 0.0)))[:2], "out": list(proj(*unproject(*OUT_UV, WALL_Y - 0.02)))},
                          "labels": {"Guitarra": [IN_UV[0] - 40, IN_UV[1] + 22, 84, 24], "Salida": [OUT_UV[0] - 30, OUT_UV[1] + 64, 64, 24]}})


KNOBS = [("pointer", f) for f in ("cream", "brushed", "od_green", "dist_orange", "fuzz_violet", "metal_black", "gate_grey")] + \
    [("skirted", f) for f in ("blackface", "graphite", "steel")] + [("chicken", f) for f in ("tweed", "brit_gold", "copper")] + [("rack", "rack_dark")]
K_PX = 5120.0  # px per m in knob layers (256 px = 0.05 m)
KR = 0.0155  # silhouette radius of every knob sprite (QML scales by r / r_px)


def _is_light(hexcol):
    return sum(palette.hex_to_linear(hexcol)) / 3 > 0.2


def knob_cap_objects(ktype, hexcol):
    g = "kn"
    metal = ktype == "skirted" and _is_light(hexcol)
    m = mt.metal_knob(hexcol) if metal else mt.knob(hexcol)
    if ktype == "skirted":
        return [md.star_cyl("skirt", KR, 0.007, 36, (0, 0, 0.0035), m, g, "z", 0.0015), md.cyl("body", KR * 0.8, 0.017, (0, 0, 0.0155), m, g, "z", 0.002, 48),
                md.cyl("dish", KR * 0.66, 0.0012, (0, 0, 0.024), m, g, "z", 0.0004, 48)]
    if ktype == "chicken":
        return [md.cyl("skirt", KR, 0.006, (0, 0, 0.003), m, g, "z", 0.001, 48), md.cyl("body", KR * 0.78, 0.02, (0, 0, 0.016), m, g, "z", 0.002, 48, r2=KR * 0.6)]
    h = 0.014 if ktype == "rack" else 0.02
    return [md.star_cyl("cap", KR, h, 30 if ktype == "rack" else 24, (0, 0, h / 2), m, g, "z", 0.0025), md.cyl("dish", KR * 0.84, 0.0012, (0, 0, h + 0.0004), m, g, "z", 0.0004, 64)]


def ring_rig():
    """rotation-invariant knob light: coaxial soft area light + emissive torus ring at ~55 deg elevation, world 0"""
    area("axis", (0, 0, 0.5), (0, 0, 0), 0.12, 6, 3800)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.063, minor_radius=0.012, location=(0, 0, 0.11))
    t = bpy.context.active_object
    t.data.materials.append(mt.matte_emitter(kelvin_hex(4200), 30.0))
    t.visible_camera = False


def knob_job(out, scratch, samples):
    res = 256
    lum = lambda x: 0.2126 * x[..., 0] + 0.7152 * x[..., 1] + 0.0722 * x[..., 2]
    kt, sheet_rows = {}, []
    for ktype, fam in KNOBS:
        name = f"{ktype}_{fam}"
        hexc = TH["chassis"][fam]["knob"]
        sc = reset(False)
        sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.0
        device(ARGS["cpu"])
        knob_cap_objects(ktype, hexc)
        camera(ortho=res / K_PX, loc=(0, 0, 0.3), rot=(0, 0, 0))
        ring_rig()
        render(scratch / "_k_dome.png", res, res, samples)
        area("k", (-0.07, 0.07, 0.11), (0, 0, 0.01), 0.07, 14, 5000)
        area("k2", (0.09, -0.02, 0.07), (0, 0, 0.01), 0.07, 2.2, 6500)
        render(scratch / "_k_key.png", res, res, samples)
        B, A = load(scratch / "_k_dome.png"), load(scratch / "_k_key.png")
        al = B[..., 3]
        d = lum(A) - lum(B)
        pos = np.clip(d / np.maximum(1 - lum(B), 0.05), 0, 1)
        neg = np.clip(-d / np.maximum(lum(B), 0.05), 0, 1)
        light = np.zeros((res, res, 4), np.float32)
        light[..., :3] = (d > 0)[..., None] * 1.0
        light[..., 3] = np.where(d > 0, pos, neg) * (al > 0.5) * 0.5
        write_png(out / f"k_{name}_light.png", light)
        write_png(out / f"k_{name}_cap.png", B)
        yy, xx = np.mgrid[0:res, 0:res].astype(np.float32)
        cx = cy = res / 2 - 0.5
        px, py = (xx - cx) / K_PX, (cy - yy) / K_PX
        if ktype == "chicken":  # wedge pointer on top of the cap (rotates with the value)
            line = (np.abs(px) < 0.0075 * (1 - (py - 0.0) / 0.0155 * 0.55).clip(0.2, 1)) & (py > 0.0) & (py < KR * 0.97)
        else:
            line = (np.abs(px) < 0.0013 * 1.4) & (py > KR * 0.28) & (py < KR * 0.95)
        mkc = TH["ink_dark"] if _is_light(hexc) else TH["metal"]
        mk = np.zeros((res, res, 4), np.float32)
        mk[..., :3] = palette.hex_to_linear(mkc)
        mk[..., :3] = np.array([int(mkc[i:i + 2], 16) / 255 for i in (1, 3, 5)])
        mk[..., 3] = blur(line.astype(np.float32), 2)
        write_png(out / f"k_{name}_mark.png", mk)
        s = np.zeros((res, res, 4), np.float32)
        s[..., 3] = blur(np.roll(np.roll((al > 0.5).astype(np.float32), 5, 0), 3, 1), 9) * 0.65
        write_png(out / "k_shadow.png", s)
        kt[name] = {"cap": f"k_{name}_cap.png", "mark": f"k_{name}_mark.png", "light": f"k_{name}_light.png", "shadow": "k_shadow.png", "a0": -150, "a1": 150, "px": res, "r_px": KR * K_PX}
        sheet_rows.append((name, B, mk, light, s))
    manifest_update(out, {"knob_types": kt})
    # sheet: rows = knob types, columns = 0 / 50 / 100 %, layers composited as the app does
    sheet = np.ones((len(sheet_rows) * 130, 3 * 130, 3), np.float32) * 0.2
    ov = lambda t, lay: t * (1 - lay[..., 3:4]) + lay[..., :3] * lay[..., 3:4]
    for r, (n, cap, mk, lt, sh) in enumerate(sheet_rows):
        for c, v in enumerate((0, 0.5, 1.0)):
            tile = np.ones((256, 256, 3), np.float32) * 0.2
            tile = ov(ov(ov(tile * (1 - sh[..., 3:4]), cap), lt), rot(mk, 150 - 300 * v))
            sheet[r * 130 + 1:r * 130 + 129, c * 130 + 1:c * 130 + 129] = tile[::2, ::2]
    write_png(scratch / "knob-sheet.png", np.concatenate([sheet, np.ones(sheet.shape[:2] + (1,), np.float32)], 2))



def rot(img, deg):
    """rotate an RGBA array about its centre (nearest, for sheets)"""
    h, w = img.shape[:2]
    a = math.radians(deg)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    cx, cy = (w - 1) / 2, (h - 1) / 2
    x, y = xx - cx, yy - cy
    sx, sy = np.cos(a) * x - np.sin(a) * y + cx, np.sin(a) * x + np.cos(a) * y + cy
    sxi, syi = np.clip(np.rint(sx).astype(int), 0, w - 1), np.clip(np.rint(sy).astype(int), 0, h - 1)
    ok = (sx >= 0) & (sx < w) & (sy >= 0) & (sy < h)
    o = img[syi, sxi] * ok[..., None]
    return o


def set_led(o, strength):
    for n in o.data.materials[0].node_tree.nodes:
        if n.type == "BSDF_PRINCIPLED":
            n.inputs["Emission Strength"].default_value = strength


def only(objs_visible, catchers=()):
    """show `objs_visible`, make `catchers` + room shadow catchers, hide everything else"""
    vis, cat = set(objs_visible), set(catchers)
    for o in bpy.data.objects:
        if o.type not in ("MESH", "CURVE"):
            continue
        o.is_shadow_catcher = o in cat
        o.hide_render = not (o in vis or o in cat)


def sprite(name, out, unit, catchers, plate_img, led=None, samples=128, leds_hex=None):
    """render one stage sprite in place (shadow-catcher room); returns manifest fields"""
    only(unit)
    render(out / "_mask.png", PW, PH, 6, denoise=False)
    body = bbox(load(out / "_mask.png"), 0.5)
    pad = max(70, int((body[2] - body[0]) * 0.3))
    bb = (max(0, body[0] - 24), max(0, body[1] - pad // 2), min(PW, body[2] + pad), min(PH, body[3] + pad))
    only(unit, catchers)
    if led:
        set_led(led[0], 0.0)
    render(out / f"{name}.png", PW, PH, samples, border=bb)
    a = load(out / f"{name}.png")
    a[..., :3] *= vigmap(PW, PH)
    sb = bbox(a, 0.004) or body
    sb = (max(sb[0], bb[0]), max(sb[1], bb[1]), min(sb[2], bb[2]), min(sb[3], bb[3]))
    spr = a[sb[1]:sb[3], sb[0]:sb[2]]
    write_png(out / f"{name}.png", spr)
    res = {"img": f"{name}.png", "img_rect": su_rect(sb), "rect": su_rect(body)}
    patches = []
    if led:
        led_o, strength, tag = led
        set_led(led_o, strength)
        render(out / "_lit.png", PW, PH, samples, border=bb)
        lit = (load(out / "_lit.png") * np.dstack([vigmap(PW, PH)[..., 0]] * 3 + [np.ones((PH, PW), np.float32)]))[sb[1]:sb[3], sb[0]:sb[2]]
        pl = plate_img[sb[1]:sb[3], sb[0]:sb[2], :3]
        base_c = spr[..., :3] * spr[..., 3:4] + pl * (1 - spr[..., 3:4])
        lit_c = lit[..., :3] * lit[..., 3:4] + pl * (1 - lit[..., 3:4])
        pp_ = patch(out, f"{name}_{tag}.png", base_c, lit_c, sb[0], sb[1])
        patches += [pp_] if pp_ else []
        set_led(led_o, 0.0)
    res["leds"] = patches
    return res


def patch(out, fname, base_c, lit_c, ox, oy, thr=0.012):
    d = np.abs(lit_c - base_c).max(2)
    a = np.clip((d - thr) * 7, 0, 1)
    a = blur(a, 5) if a.max() > 0 else a
    box_ = bbox(np.dstack([a, a, a, a]), 0.03)
    if box_ is None:
        print("PATCH-EMPTY", fname)
        return None
    x0, y0, x1, y1 = box_
    al = np.maximum(a[y0:y1, x0:x1], 1e-4)[..., None]
    rgb = np.clip((lit_c[y0:y1, x0:x1] - base_c[y0:y1, x0:x1] * (1 - al)) / al, 0, 1)
    write_png(out / fname, np.concatenate([rgb, al], 2))
    return {"rect": su_rect((ox + x0, oy + y0, ox + x1, oy + y1)), "lit": fname}


HEADS = {"brit_gold": "chicken", "tweed": "chicken", "blackface": "skirted", "copper": "chicken", "steel": "skirted", "graphite": "skirted"}
CABS = {"grille_wheat": (1, 2, 4), "grille_silver": (1, 2, 4), "grille_black": (1, 2, 4)}
STOMPS = {"PRE": ("cream", "brushed"), "DST": ("od_green", "fuzz_violet", "metal_black", "dist_orange"), "NR": ("gate_grey",)}
RACKS = ("MOD", "DLY", "RVB")
FRAMES = 5
_KNOB_NAME = re.compile(r"^(knob|kring|k|rk)\d+(\.\d+)?$")


def lp(p0, lx, ly, lz):
    """deck-local pedal point -> world (tilted like the pedal)"""
    return (p0[0] + lx, p0[1] + ly * math.cos(TILT) - lz * math.sin(TILT), p0[2] + ly * math.sin(TILT) + lz * math.cos(TILT))


def stomp_info(b, p0, k, kh, nk, ktype):
    """live-part geometry of a stompbox built by md.stompbox/eq_box at deck point p0"""
    w, d, h = 0.073 * k, 0.129 * k, 0.052 * kh
    r = {}
    r["_kt"] = ktype
    r["in"] = list(proj(*lp(p0, -w / 2 - 0.0, d * 0.78, h * 0.5)))
    r["out"] = list(proj(*lp(p0, w / 2, d * 0.78, h * 0.5)))
    r["switch"] = quad_rect([lp(p0, -0.03, d * 0.24 - 0.03, h), lp(p0, 0.03, d * 0.24 + 0.03, h + 0.03)])
    wl = w * 0.8
    c0, c1 = lp(p0, -wl / 2, d * 0.5 + d * 0.11, h), lp(p0, wl / 2, d * 0.5 - d * 0.11, h)
    nr = quad_rect([c0, c1])
    hh = nr[2] * 0.2  # un-squashed text height; QML squashes it by nr[3]/hh (foreshortening)
    r["name"] = [nr[0], nr[1] + nr[3] / 2 - hh / 2, nr[2], hh, nr[3] / hh]
    return r


def knob_caps(objs):
    """(cap-top centre, radius, axis) in world space of each baked knob object, left to right"""
    bpy.context.view_layer.update()
    res = []
    for o in sorted([o for o in objs if _KNOB_NAME.match(o.name) and not o.name.startswith("kring")], key=lambda o: o.matrix_world.translation.x):
        mw = o.matrix_world
        n = (mw.to_3x3() @ Vector((0, 0, 1))).normalized()
        if n.dot(CAM - mw.translation) < 0:
            n = -n
        res.append((mw.translation + n * (o.dimensions.z / 2), o.dimensions.x / 2, n))
    return res


def knob_list(objs, ktype):
    """projected cap centre/radius of each baked knob (the pointer overlay sits exactly on it)"""
    res = []
    for c, r, n in knob_caps(objs):
        e = ell(tuple(c), tuple(n.cross(Vector((1, 0, 0))).normalized()), r)
        e["type"] = ktype
        res.append(e)
    return res


HERO_HS = {"AMP": 630, "CAB": 420, "rack": 630}  # px per m; everything else (pedals, treadles) 1260
HERO_PX_SU = 1.4  # hero px per display unit (2x layers)


def thumb(out, fname, a, side=128):
    """premultiplied area-ish downscale of a hero render to a transparent side x side tile (chips, picker, compact cells)"""
    h, w = a.shape[:2]
    k = (side - 8) / max(h, w)
    nh, nw = max(1, round(h * k)), max(1, round(w * k))
    p = a.copy()
    p[..., :3] *= p[..., 3:4]
    p = blur(p, max(1, int(0.6 / k)))
    p = p[np.linspace(0, h - 1, nh).round().astype(int)][:, np.linspace(0, w - 1, nw).round().astype(int)]
    p[..., :3] /= np.maximum(p[..., 3:4], 1e-4)
    t = np.zeros((side, side, 4), np.float32)
    y0, x0 = (side - nh) // 2, (side - nw) // 2
    t[y0:y0 + nh, x0:x0 + nw] = np.clip(p, 0, 1)
    write_png(out / fname, t)


def heroes(U, out, samples):
    """ortho close-up per unit: heads/cabs/rack in front view, pedals/treadles along the deck normal (true-scale top view); baked knobs, LED patch, treadle frames"""
    global SU
    for o in [o for o in bpy.data.objects if o.type in ("LIGHT", "CAMERA")]:
        bpy.data.objects.remove(o)
    X, Z = Vector((1, 0, 0)), Vector((0, 0, 1))
    hero = {}
    for key, objs, _catch, led, ex in U:
        grp = key.split("/")[0]
        front = grp in ("AMP", "CAB", "rack")
        right, up, n, rot = (X, Z, Vector((0, -1, 0)), (math.pi / 2, 0, 0)) if front else (X, Vector((0, math.cos(TILT), math.sin(TILT))), Vector((0, -math.sin(TILT), math.cos(TILT))), (TILT, 0, 0))
        frames = objs if isinstance(objs[0], list) else [objs]
        us, vs = [], []
        for o in sum(frames, []):
            for cn in o.bound_box:
                P = o.matrix_world @ Vector(cn)
                us.append(P.dot(right))
                vs.append(P.dot(up))
        hs, pad = HERO_HS.get(grp, 1260), 0.01
        u0, u1, v0, v1 = min(us) - pad, max(us) + pad, min(vs) - pad, max(vs) + pad
        W, H = int(math.ceil((u1 - u0) * hs)), int(math.ceil((v1 - v0) * hs))
        uc, vc = (u0 + u1) / 2, (v0 + v1) / 2
        Pc = right * uc + up * vc
        cam = camera(ortho=W / hs, loc=tuple(Pc + n * 3), rot=rot)
        cam.data.sensor_fit = "HORIZONTAL"
        ls = [area("hk", Pc + n * 1.8 + right * -1.0 + up * 0.9, Pc, 1.4, 520, 3600), area("hf", Pc + n * 2.0 + right * 1.3 - up * 0.1, Pc, 1.6, 150, 3200),
              area("hr", Pc + n * 0.6 + up * 1.2 + right * 0.2, Pc, 1.0, 220, 4500)]
        name = "h_" + key.replace("/", "_")
        px = lambda P: ((P.dot(right) - u0) * hs / HERO_PX_SU, (v1 - P.dot(up)) * hs / HERO_PX_SU)
        r = {"size": [W / HERO_PX_SU, H / HERO_PX_SU]}
        fr = []
        for i, f in enumerate(frames):
            only(f)
            render(out / f"{name}{'_%d' % i if len(frames) > 1 else ''}.png", W, H, samples)
            a = load(out / f"{name}{'_%d' % i if len(frames) > 1 else ''}.png")
            fr.append(f"{name}{'_%d' % i if len(frames) > 1 else ''}.png")
            if i == len(frames) // 2:
                thumb(out, name.replace("h_", "t_", 1) + ".png", a)
                r["thumb"] = name.replace("h_", "t_", 1) + ".png"
            if led:
                set_led(led[0], led[1])
                render(out / "_hl.png", W, H, samples)
                lit = load(out / "_hl.png")
                set_led(led[0], 0.0)
                SU = HERO_PX_SU
                pp_ = patch(out, f"{name}_led.png", a[..., :3] * a[..., 3:4], lit[..., :3] * lit[..., 3:4], 0, 0)
                SU = 1.5
                r["leds"] = [pp_] if pp_ else []
        r["img"] = fr[len(fr) // 2]
        if len(fr) > 1:
            r["frames"] = fr
        kt = ex.get("_kt") or ex.get("_kt2")
        if kt:
            r["knobs"] = []
            for c, rad, _n in knob_caps(frames[0]):
                x, y = px(c)
                r["knobs"].append({"x": x, "y": y, "r": rad * hs / HERO_PX_SU, "sy": 1, "type": kt})
        for fld, k in (("name", "_hn"), ("display", "_hd")):
            if ex.get(k):
                a_, b_, c_, d_ = ex[k]
                x0_, y0_ = ((a_ - u0) * hs / HERO_PX_SU, (v1 - d_) * hs / HERO_PX_SU)
                r[fld] = [x0_, y0_, (b_ - a_) * hs / HERO_PX_SU, (d_ - c_) * hs / HERO_PX_SU]
        for o in ls:
            bpy.data.objects.remove(o)
        bpy.data.objects.remove(cam)
        hero[key] = r
    return hero


def units_job(out, scratch, samples):
    sc = reset()
    device(ARGS["cpu"])
    build_room()
    room_lights()
    camera()
    plate_img = load(out / "plate.jpg")
    room = list(bpy.data.objects)
    zones, xs = layout_zones(), ped_x()
    fl = [o for o in room if o.name.startswith(("floor", "wall", "rug", "skirting", "chair"))]
    deck = fl + ROOM_PARTS["deck"]
    rack = fl + ROOM_PARTS["rack"]
    res = {}
    U = []  # (key, objs, catchers, led (obj, strength, tag) or None, extra manifest)

    cab2 = {}
    for fam, sizes in CABS.items():
        for n in sizes:
            o = md.cabinet(fam, n, (-0.30, 0.90, 0.0))
            cab2[(fam, n)] = o
            U.append((f"CAB/{fam}/{n}", o, fl, None, {"in": list(proj(0.0, 1.1, HEAD_Z - 0.1))}))
    kz = HEAD_Z + 0.02 + 0.135
    for fam, kty in HEADS.items():
        o = md.head(fam, (-0.30, 0.95, HEAD_Z))
        jew = [x for x in o if x.name.startswith("jewel")][0]
        fy = 0.95 - 0.0006
        nq = quad_rect([(-0.30 - 0.32, fy - 0.004, HEAD_Z + 0.02 + 0.203), (-0.30 - 0.02, fy - 0.004, HEAD_Z + 0.02 + 0.177)])
        hgt = abs(proj(0, fy, HEAD_Z + 0.22)[1] - proj(0, fy, HEAD_Z + 0.19)[1])
        ex = {"_kt": f"{kty}_{fam}", "_hn": (-0.62, -0.32, HEAD_Z + 0.197, HEAD_Z + 0.223),
              "in": list(proj(-0.605, fy - 0.014, HEAD_Z + 0.02 + 0.115)), "out": list(proj(0.07, fy + 0.1, HEAD_Z + 0.06)), "name": nq[:2] + [nq[2], hgt, 1.0]}
        U.append((f"AMP/{fam}", o, cab2[("grille_silver", 2)], (jew, 40.0, "jewel"), ex))
    for b, fams in STOMPS.items():
        for fam in fams:
            k, nk = (1.35, 2) if b == "NR" else (1.7, 3)
            p0 = deck_pt(xs[b], PED_YL.get(b, 0.10))
            o = md.stompbox(fam, p0, "ped", k=k, nknobs=nk, block=b)
            ex = stomp_info(b, p0, k, 1.3, nk, f"pointer_{fam}")
            w_, d_ = 0.073 * k, 0.129 * k
            vb = p0[1] * math.cos(TILT) + p0[2] * math.sin(TILT)
            ex["_hn"] = (p0[0] - w_ * 0.4, p0[0] + w_ * 0.4, vb + d_ * 0.39, vb + d_ * 0.61)
            U.append((f"{b}/{fam}", o, deck, ([x for x in o if x.name.startswith("led")][0], 30.0, "led"), ex))
    p0 = deck_pt(xs["EQ"], 0.10)
    o = md.eq_box("eq_white", p0, "ped")
    ex = stomp_info("EQ", p0, 1.7, 1.3, 0, "")
    ex.pop("_kt", None)
    w, d, h = 0.073 * 1.7, 0.129 * 1.7, 0.052 * 1.3
    ex["faders"] = [quad_rect([lp(p0, (i - 3) * w * 0.115 - 0.004, d * 0.46, h + 0.002), lp(p0, (i - 3) * w * 0.115 + 0.004, d * 0.86, h + 0.002)]) for i in range(7)]
    U.append(("EQ/eq_white", o, deck, ([x for x in o if x.name.startswith("led")][0], 30.0, "led"), ex))
    for b in ("WAH", "VOL"):
        p0 = deck_pt(xs[b], PED_YL[b])
        frames = [md.treadle(b, p0, "ped", rock=-(f / (FRAMES - 1) - 0.5) * 0.4, w=PED_W[b]) for f in range(FRAMES)]
        U.append((f"{b}/treadle_black", frames, deck, None, {}))
    for i, b in enumerate(RACKS):
        o = md.rack_unit(b, i)
        zc = md.ZB + 0.208 - 0.022 - i * 0.044
        fy = md.RACK_Y - 0.0015
        ex = {"_kt": "rack_rack_dark", "_hd": (md.RACK_X - 0.154, md.RACK_X - 0.046, zc - 0.011, zc + 0.015),
              "display": quad_rect([(md.RACK_X - 0.154, fy - 0.0027, zc - 0.011), (md.RACK_X - 0.046, fy - 0.0027, zc + 0.015)]),
              "in": list(proj(md.RACK_X - 0.241, fy, zc)), "out": list(proj(md.RACK_X + 0.241, fy, zc))}
        U.append((f"rack/{b}", o, rack, ([x for x in o if x.name.startswith("led")][0], 30.0, "led"), ex))
    for key, objs, catch, led, ex in U:
        name = key.replace("/", "_")
        zone = zones[key.split("/")[1] if key.startswith("rack") else key.split("/")[0]]
        if isinstance(objs[0], list):  # treadle frames
            fr = []
            for i, f_ in enumerate(objs):
                r = sprite(f"{name}_{i}", out, f_, catch, plate_img, samples=samples)
                fr.append({"img": r["img"], "img_rect": r["img_rect"]})
            res[key] = {"img": fr[FRAMES // 2]["img"], "img_rect": fr[FRAMES // 2]["img_rect"], "frames": fr, "rect": zone, "leds": [],
                        "in": list(proj(*lp(deck_pt(xs[key[:3]], PED_YL[key[:3]]), -PED_W[key[:3]] / 2, 0.1, 0.03))), "out": list(proj(*lp(deck_pt(xs[key[:3]], PED_YL[key[:3]]), PED_W[key[:3]] / 2, 0.1, 0.03)))}
            continue
        r = sprite(name, out, objs, catch, plate_img, led=led, samples=samples)
        r["rect"] = zone
        kt = ex.get("_kt")
        ex = {k: v for k, v in ex.items() if not k.startswith("_")}
        r.update(ex)
        kn = knob_list(objs, kt) if kt else []
        if kn:
            r["knobs"] = kn
        res[key] = r
    manifest_update(out, {"units": res})
    hero = heroes(U, out, max(samples // 2, 32))  # before plugs_job: it rebuilds the scene
    plugs_job(out)
    m = json.loads((out / "manifest.json").read_text())
    for k, h in hero.items():
        m["units"][k]["thumb"] = h.pop("thumb")
        m["units"][k]["hero"] = h
    manifest_update(out, {"units": m["units"]})



def plugs_job(out):
    px_m = 1900.0
    manifest = {}
    for kind in ("s", "a"):
        for side in ("L", "R"):
            sc = reset()
            device(ARGS["cpu"])
            md.plug(kind, side)
            camera(ortho=0.14, loc=(0, -0.5, -0.0), rot=(math.pi / 2, 0, 0))
            area("pk", (-0.15, -0.4, 0.3), (0, 0, 0), 0.4, 14, 4500)
            area("pf", (0.2, -0.4, 0.05), (0, 0, 0), 0.4, 3, 6500)
            sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.8
            w, h = int(0.14 * px_m), int(0.07 * px_m)
            render(out / "_p.png", w, h, 64)
            a = load(out / "_p.png")
            b = bbox(a, 0.02)
            write_png(out / f"plug_{kind}_{side.lower()}.png", a[b[1]:b[3], b[0]:b[2]])
            cx = w / 2 - b[0]
            cy = h / 2 - b[1]
            tip = [cx, cy]
            ex = [(w / 2 - b[0]) - (0.1 if side == "L" else -0.1) * 0 + (-1 if side == "L" else 1) * 0.07 * px_m, cy]
            if kind == "a":
                ex = [w / 2 - b[0] + (-1 if side == "L" else 1) * 0.062 * px_m, cy + 0.035 * px_m]
            name = {"s": "straight", "a": "angle"}[kind] + "_" + side.lower()
            manifest[name] = {"img": f"plug_{kind}_{side.lower()}.png", "tip": tip, "exit": ex, "ring": [ex[0] - 6, cy - 6, 12, 12], "su_per_px": 0.34}
    manifest_update(out, {"plugs": manifest})


def sheet_job(out, scratch):
    """contact sheet of every rendered unit (sprites over the plate, 1/3 scale)"""
    m = json.loads((out / "manifest.json").read_text())
    keys = sorted(m["units"])
    cols, tw, th = 6, 330, 260
    sh = np.ones((((len(keys) + cols - 1) // cols) * th, cols * tw, 3), np.float32) * 0.1
    for i, k in enumerate(keys):
        u = m["units"][k]
        a = load(out / u["img"])
        h, w = (a.shape[0] // 3) * 3, (a.shape[1] // 3) * 3
        a = a[:h, :w].reshape(h // 3, 3, w // 3, 3, 4).mean((1, 3))
        a = a[:th - 4, :tw - 4]
        y, x = (i // cols) * th + 2, (i % cols) * tw + 2
        reg = sh[y:y + a.shape[0], x:x + a.shape[1]]
        reg[:] = a[..., :3] * a[..., 3:4] + 0.2 * (1 - a[..., 3:4])
    write_png(scratch / "M3-families.png", np.dstack([sh, np.ones(sh.shape[:2], np.float32)]))



ARGS = {"cpu": False}


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    jobs = [a for a in argv if not a.startswith("--") and not Path(a).exists() and a in ("matsheet", "plate", "units", "knob", "all", "sheet", "heroes")]
    opt = {"--out": str(ROOT / "app" / "assets" / "render"), "--scratch": None, "--samples": None}
    for i, a in enumerate(argv):
        if a in opt:
            opt[a] = argv[i + 1]
    ARGS["cpu"] = "--cpu" in argv
    pre = "--preview" in argv
    out = Path(opt["--out"])
    out.mkdir(parents=True, exist_ok=True)
    scratch = Path(opt["--scratch"] or out)
    scratch.mkdir(parents=True, exist_ok=True)
    global EXPOSURE
    mp = out / "manifest.json"
    if mp.exists() and "plate" not in jobs:
        EXPOSURE = json.loads(mp.read_text()).get("camera", {}).get("exposure", 0.0)
    t0 = time.time()
    S = lambda d: int(opt["--samples"]) if opt["--samples"] else (24 if pre else d)
    for j in jobs or ["all"]:
        if j == "all":  # clean slate: stale manifest keys / images must not survive
            for f in out.glob("*"):
                if f.suffix in (".png", ".jpg", ".json"):
                    f.unlink()
        if j == "matsheet":
            matsheet(scratch, S(48))
        if j in ("plate", "all"):
            plate(out, S(256), 0.4 if pre else 1.0)
        if j in ("knob", "all"):
            knob_job(out, scratch, S(64))
        if j in ("units", "all"):
            units_job(out, scratch, S(128))
        if j in ("sheet", "all"):
            sheet_job(out, scratch)
    for p in out.glob("_*"):
        p.unlink()
    print("RENDER-LOG", bpy.app.version_string, "total", round(time.time() - t0, 1), "s", json.dumps(LOG))


main()

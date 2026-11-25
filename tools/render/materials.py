"""Procedural material library (shader nodes only, no image files). Base colours come from app/theme.py via palette.py.
bpy only: imported by rig.py inside Blender."""
import bpy
from palette import hex_to_linear, read_theme

TH = read_theme()


def rgb(h):
    return (*hex_to_linear(h), 1.0)


class M:
    """Tiny node-graph helper around one Principled material."""

    def __init__(self, name):
        self.m = bpy.data.materials.new(name)
        self.m.use_nodes = True
        self.nt = self.m.node_tree
        self.nt.nodes.clear()
        out = self.nt.nodes.new("ShaderNodeOutputMaterial")
        self.b = self.nt.nodes.new("ShaderNodeBsdfPrincipled")
        self.nt.links.new(self.b.outputs["BSDF"], out.inputs["Surface"])
        self.out = out
        tc = self.n("ShaderNodeTexCoord")
        self.co, self.gen, self.onrm = tc.outputs["Object"], tc.outputs["Generated"], tc.outputs["Normal"]
        self.geo = self.n("ShaderNodeNewGeometry")

    def n(self, t, **kw):
        node = self.nt.nodes.new(t)
        for k, v in kw.items():
            setattr(node, k, v)
        return node

    def set(self, **kw):
        for k, v in kw.items():
            if k == "Metallic":
                assert v in (0, 1), "Metallic is a switch (0 or 1)"
            self.b.inputs[k.replace("_", " ")].default_value = v
        return self

    def link(self, sock, name):
        self.nt.links.new(sock, self.b.inputs[name])

    def noise(self, scale, detail=2.0, rough=0.5, dist=0.0, vec=None):
        n = self.n("ShaderNodeTexNoise")
        self.nt.links.new(vec or self.co, n.inputs["Vector"])
        n.inputs["Scale"].default_value, n.inputs["Detail"].default_value = scale, detail
        n.inputs["Roughness"].default_value, n.inputs["Distortion"].default_value = rough, dist
        return n.outputs["Fac"]

    def white(self, scale):
        n = self.n("ShaderNodeTexWhiteNoise", noise_dimensions="3D")
        mp = self.n("ShaderNodeVectorMath", operation="SCALE")
        self.nt.links.new(self.co, mp.inputs[0])
        mp.inputs["Scale"].default_value = scale
        self.nt.links.new(mp.outputs[0], n.inputs["Vector"])
        return n.outputs["Value"]

    def voronoi(self, scale, smooth=False, rnd=1.0):
        n = self.n("ShaderNodeTexVoronoi", feature="SMOOTH_F1" if smooth else "F1")
        self.nt.links.new(self.co, n.inputs["Vector"])
        n.inputs["Scale"].default_value = scale
        n.inputs["Randomness"].default_value = rnd
        return n.outputs["Distance"]

    def wave(self, scale, axis="X", dist=0.0):
        n = self.n("ShaderNodeTexWave", wave_type="BANDS", bands_direction=axis, wave_profile="SIN")
        self.nt.links.new(self.co, n.inputs["Vector"])
        n.inputs["Scale"].default_value, n.inputs["Distortion"].default_value = scale, dist
        return n.outputs["Fac"]

    def math(self, op, a, b=None, clamp=False):
        n = self.n("ShaderNodeMath", operation=op, use_clamp=clamp)
        for i, v in enumerate((a, b)):
            if v is None:
                continue
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = v
            else:
                self.nt.links.new(v, n.inputs[i])
        return n.outputs[0]

    def ramp(self, fac, lo, hi):
        """float -> colour/float remap: `lo`..`hi` are colours (rgba) or floats."""
        n = self.n("ShaderNodeValToRGB")
        self.nt.links.new(fac, n.inputs["Fac"])
        n.color_ramp.elements[0].color = lo if isinstance(lo, tuple) else (lo, lo, lo, 1)
        n.color_ramp.elements[1].color = hi if isinstance(hi, tuple) else (hi, hi, hi, 1)
        return n.outputs["Color"]

    def rgb_mul(self, col, fac):
        n = self.n("ShaderNodeMix", data_type="RGBA", blend_type="MULTIPLY")
        n.inputs[0].default_value = 1.0
        for i, v in ((6, col), (7, fac)):
            if isinstance(v, (tuple, list)):
                n.inputs[i].default_value = v
            else:
                self.nt.links.new(v, n.inputs[i])
        return n.outputs[2]

    def bump(self, height, strength=1.0, dist=0.001, normal=None):
        n = self.n("ShaderNodeBump")
        n.inputs["Strength"].default_value, n.inputs["Distance"].default_value = strength, dist
        self.nt.links.new(height, n.inputs["Height"])
        if normal is not None:
            self.nt.links.new(normal, n.inputs["Normal"])
        return n.outputs["Normal"]

    def angle(self):
        """atan2(y, x) of the object coordinate, for radial knurl / spun-metal patterns."""
        s = self.n("ShaderNodeSeparateXYZ")
        self.nt.links.new(self.co, s.inputs[0])
        return self.math("ARCTAN2", s.outputs["Y"], s.outputs["X"])

    def radius(self):
        s = self.n("ShaderNodeSeparateXYZ")
        self.nt.links.new(self.co, s.inputs[0])
        v = self.n("ShaderNodeVectorMath", operation="LENGTH")
        c = self.n("ShaderNodeCombineXYZ")
        self.nt.links.new(s.outputs["X"], c.inputs["X"])
        self.nt.links.new(s.outputs["Y"], c.inputs["Y"])
        self.nt.links.new(c.outputs[0], v.inputs[0])
        return v.outputs["Value"]


    def mixc(self, fac, a, b):
        n = self.n("ShaderNodeMix", data_type="RGBA", blend_type="MIX")
        if isinstance(fac, (int, float)):
            n.inputs[0].default_value = fac
        else:
            self.nt.links.new(fac, n.inputs[0])
        for i, v in ((6, a), (7, b)):
            if isinstance(v, (tuple, list)):
                n.inputs[i].default_value = v
            else:
                self.nt.links.new(v, n.inputs[i])
        return n.outputs[2]

    def xyz(self, vec=None):
        s = self.n("ShaderNodeSeparateXYZ")
        self.nt.links.new(vec or self.co, s.inputs[0])
        return s.outputs["X"], s.outputs["Y"], s.outputs["Z"]

    def comb(self, x, y, z):
        c = self.n("ShaderNodeCombineXYZ")
        for k, v in (("X", x), ("Y", y), ("Z", z)):
            if isinstance(v, (int, float)):
                c.inputs[k].default_value = v
            else:
                self.nt.links.new(v, c.inputs[k])
        return c.outputs[0]

    def bevel_n(self, radius=0.003):
        """rounded-edge normal (Cycles Bevel node)"""
        bv = self.n("ShaderNodeBevel", samples=8)
        bv.inputs["Radius"].default_value = radius
        return bv.outputs["Normal"], bv

    def edge(self, radius=0.003, scale=40.0):
        """wear mask 0..1: 1 - dot(bevel normal, normal) mapped 0.002..0.05, broken up by noise"""
        _, bv = self.bevel_n(radius)
        d = self.n("ShaderNodeVectorMath", operation="DOT_PRODUCT")
        self.nt.links.new(bv.outputs["Normal"], d.inputs[0])
        self.nt.links.new(self.geo.outputs["Normal"], d.inputs[1])
        mr = self.n("ShaderNodeMapRange", clamp=True)
        self.nt.links.new(self.math("SUBTRACT", 1.0, d.outputs["Value"]), mr.inputs["Value"])
        mr.inputs["From Min"].default_value, mr.inputs["From Max"].default_value = 0.002, 0.05
        return self.math("MULTIPLY", mr.outputs["Result"], self.ramp(self.noise(scale, 4), 0.15, 1.0), clamp=True)

    def dust(self, scale=6.0, k=1.0):
        """up-facing surfaces x noise"""
        mr = self.n("ShaderNodeMapRange", clamp=True)
        self.nt.links.new(self.xyz(self.geo.outputs["Normal"])[2], mr.inputs["Value"])
        mr.inputs["From Min"].default_value = 0.5
        return self.math("MULTIPLY", self.math("MULTIPLY", mr.outputs["Result"], self.ramp(self.noise(scale, 3), 0.0, 1.4)), k, clamp=True)

    def wear(self, mask, **bare):
        """mix the main BSDF with a bare-metal BSDF by `mask` (Mix Shader: each sample is one or the other)"""
        b2 = self.n("ShaderNodeBsdfPrincipled")
        for k, v in bare.items():
            b2.inputs[k.replace("_", " ")].default_value = v
        assert b2.inputs["Metallic"].default_value in (0, 1)
        mx = self.n("ShaderNodeMixShader")
        self.nt.links.new(mask, mx.inputs[0])
        self.nt.links.new(self.b.outputs["BSDF"], mx.inputs[1])
        self.nt.links.new(b2.outputs["BSDF"], mx.inputs[2])
        self.nt.links.new(mx.outputs[0], self.out.inputs["Surface"])

    def tangent_x(self):
        """brushing along world x: tangent = normal x X"""
        c = self.n("ShaderNodeVectorMath", operation="CROSS_PRODUCT")
        self.nt.links.new(self.geo.outputs["Normal"], c.inputs[0])
        c.inputs[1].default_value = (1, 0, 0)
        self.nt.links.new(c.outputs[0], self.b.inputs["Tangent"])

    def tangent_radial(self):
        t = self.n("ShaderNodeTangent", direction_type="RADIAL", axis="Z")
        self.nt.links.new(t.outputs[0], self.b.inputs["Tangent"])


def _bumped(m, h, strength, dist, bn=None):
    m.link(m.bump(h, strength, dist, normal=bn), "Normal")


def tolex(base):
    """aged vinyl: coarse pebble, rubbed-grey edges and corners, large scuffs and stains, dust on tops, no sheen/coat"""
    m = M("tolex")
    bn, _ = m.bevel_n(0.004)
    edge, dust = m.edge(0.004, 30), m.dust(6.0, 1.3)
    scuff = m.math("MULTIPLY", m.math("GREATER_THAN", m.noise(14, 4, 0.6), 0.56), m.ramp(m.noise(90, 3), 0.2, 1.0))
    stain = m.ramp(m.noise(3, 3), 0.8, 1.05)
    col = m.rgb_mul(m.rgb_mul(rgb(base), m.ramp(m.noise(5, 3), 0.85, 1.12)), stain)
    rubbed = m.rgb_mul(col, (2.4, 2.3, 2.2, 1))
    worn = m.mixc(m.math("MAXIMUM", edge, m.math("MULTIPLY", scuff, 0.7)), col, rubbed)
    m.link(m.mixc(m.math("MULTIPLY", dust, 0.5), worn, (0.05, 0.045, 0.04, 1)), "Base Color")
    h = m.math("ADD", m.voronoi(300, True), m.math("MULTIPLY", m.noise(1200, 1), 0.25))
    _bumped(m, m.math("SUBTRACT", h, m.math("MULTIPLY", scuff, 0.15)), 0.4, 0.0015, bn)
    rough = m.math("ADD", m.ramp(m.noise(15, 2), 0.55, 0.72), m.math("MULTIPLY", dust, 0.15))
    m.link(m.math("SUBTRACT", rough, m.math("MULTIPLY", m.math("MAXIMUM", edge, scuff), 0.2), clamp=True), "Roughness")
    m.set(Specular_IOR_Level=0.35)
    return m.m


def cloth(base, k=0.18, alpha=0.7, thread=400.0, spk=(), dims=(1.0, 1.0)):
    """dark woven grille cloth (plain weave), ghosting over the speakers so their rings read faintly, dust toward the bottom, stains"""
    m = M("cloth")
    w = m.math("ADD", m.wave(thread, "X", 0.15), m.wave(thread * 0.9, "Y", 0.15))
    dark = m.ramp(m.xyz(m.gen)[2], 0.7, 1.0)
    c = tuple(v * k for v in rgb(base)[:3]) + (1.0,)
    wv = m.ramp(m.math("ADD", w, m.noise(30, 2), clamp=True), 0.8, 1.2)
    col = m.rgb_mul(m.rgb_mul(m.rgb_mul(c, wv), dark), m.ramp(m.noise(4, 3), 0.8, 1.2))
    gx, _gy, gz = m.xyz(m.gen)
    for (u, v, r) in spk:  # speaker cones showing faintly through the cloth: darker disc, softer edge, darker dust cap
        d = m.math("SQRT", m.math("ADD", m.math("POWER", m.math("MULTIPLY", m.math("SUBTRACT", gx, u), dims[0]), 2.0), m.math("POWER", m.math("MULTIPLY", m.math("SUBTRACT", gz, v), dims[1]), 2.0)))
        cone = m.math("MULTIPLY", m.math("SUBTRACT", r, d), 1.0 / (0.25 * r), clamp=True)
        cap = m.math("MULTIPLY", m.math("SUBTRACT", r * 0.22, d), 1.0 / (0.06 * r), clamp=True)
        col = m.rgb_mul(col, m.math("SUBTRACT", 1.0, m.math("ADD", m.math("MULTIPLY", cone, 0.5), m.math("MULTIPLY", cap, 0.2))))
    m.link(col, "Base Color")
    m.link(m.bump(w, 0.6, 0.0008), "Normal")
    m.set(Roughness=0.92, Sheen_Weight=0.2, Sheen_Roughness=0.5, Alpha=alpha, Specular_IOR_Level=0.1)
    return m.m


def brushed(tint_hex, rough=0.4):
    """dull worn aluminium: F0 aluminium x tint, anisotropic along x, tarnish patches, pitting, scratches; edges polished by use"""
    m = M("brushed")
    bn, _ = m.bevel_n(0.002)
    s = m.n("ShaderNodeMapping")
    m.nt.links.new(m.co, s.inputs["Vector"])
    s.inputs["Scale"].default_value = (1.0, 140.0, 140.0)
    n = m.noise(60.0, 4.0, vec=s.outputs[0])
    t = rgb(tint_hex)
    base = tuple(a * b * 0.8 for a, b in zip((0.91, 0.92, 0.92, 1), (min(1, v * 1.15 + 0.1) for v in t[:3]))) + (1,)
    tar = m.ramp(m.noise(7, 4), 0.55, 1.0)
    pits = m.math("GREATER_THAN", m.noise(260, 2), 0.72)
    m.link(m.rgb_mul(m.rgb_mul(base, m.ramp(n, 0.85, 1.05)), tar), "Base Color")
    edge = m.edge(0.002)
    m.link(m.math("SUBTRACT", m.math("ADD", m.ramp(n, rough - 0.07, rough + 0.07), m.math("MULTIPLY", pits, 0.2)), m.math("MULTIPLY", edge, 0.14)), "Roughness")
    _bumped(m, m.math("ADD", n, m.math("MULTIPLY", pits, -0.6)), 0.12, 0.0004, bn)
    m.set(Metallic=1, Anisotropic=0.6)
    m.tangent_x()
    return m.m


def chrome():
    """dulled, pitted chrome: base darker than mirror, patchy haze and scratches"""
    m = M("chrome")
    m.set(Metallic=1, Base_Color=(0.48, 0.48, 0.46, 1))
    haze = m.ramp(m.noise(18, 4), 0.0, 1.0)
    m.link(m.math("ADD", m.ramp(m.noise(900, 3), 0.1, 0.2), m.math("MULTIPLY", haze, 0.22)), "Roughness")
    m.link(m.bump(m.noise(400, 3), 0.1, 0.0003), "Normal")
    return m.m


def powder(base):
    """chipped powder-coat on die-cast: orange peel, bare aluminium on worn edges and chips, scuffs near the footswitch, no coat"""
    m = M("powder")
    bn, _ = m.bevel_n(0.0025)
    edge = m.edge(0.004, 60)
    chips = m.math("MULTIPLY", m.math("GREATER_THAN", m.noise(160, 2), 0.7), m.ramp(m.noise(12, 2), 0.0, 1.0))
    m.link(m.rgb_mul(rgb(base), m.ramp(m.noise(5, 3), 0.85, 1.05)), "Base Color")
    _bumped(m, m.noise(800, 2), 0.14, 0.0006, bn)
    scuff = m.math("MULTIPLY", m.ramp(m.xyz(m.gen)[1], 1.0, 0.0), m.ramp(m.noise(30, 3), 0.0, 0.3))
    m.link(m.math("ADD", m.ramp(m.noise(20, 2), 0.55, 0.7), scuff), "Roughness")
    m.set(Metallic=0)
    m.wear(m.math("MAXIMUM", edge, m.math("MULTIPLY", chips, 0.8)), Metallic=1, Base_Color=(0.55, 0.55, 0.55, 1), Roughness=0.5)
    return m.m


def painted(base, anodised=False):
    """amp faceplate: satin enamel, or anodised aluminium for gold/copper"""
    m = M("painted")
    bn, _ = m.bevel_n(0.0015)
    m.link(m.rgb_mul(rgb(base), m.ramp(m.noise(8, 3), 0.94, 1.04)), "Base Color")
    m.link(m.bump(m.noise(1800, 2), 0.2, 0.0004, normal=bn), "Normal")
    if anodised:
        m.link(m.ramp(m.noise(40, 3), 0.28, 0.36), "Roughness")
        m.set(Metallic=1, Anisotropic=0.4)
        m.tangent_x()
    else:
        m.link(m.ramp(m.noise(30, 3), 0.35, 0.45), "Roughness")
        m.set(Metallic=0)
    return m.m


def rubber(rough=0.75, tint=None):
    m = M("rubber")
    dust = m.dust(5.0, 1.4)
    m.link(m.mixc(m.math("MULTIPLY", dust, 0.3), rgb(tint or TH["rubber"]), (0.03, 0.03, 0.03, 1)), "Base Color")
    m.link(m.math("ADD", m.ramp(m.noise(20, 3), rough - 0.1, rough + 0.1), m.math("MULTIPLY", dust, 0.1), clamp=True), "Roughness")
    m.set(Specular_IOR_Level=0.35)
    m.link(m.bump(m.noise(1500, 2), 0.2, 0.0004), "Normal")
    return m.m


def knob(base):
    """plastic cap: rougher knurl side, smoother top insert, no coat (knurl is geometry)"""
    m = M("knob")
    top = m.math("GREATER_THAN", m.math("ABSOLUTE", m.xyz(m.onrm)[2]), 0.9)
    m.link(m.math("SUBTRACT", 0.4, m.math("MULTIPLY", top, 0.15)), "Roughness")
    m.set(Base_Color=rgb(base), IOR=1.46, Metallic=0)
    m.link(m.bump(m.noise(900, 2), 0.1, 0.0003), "Normal")
    return m.m


def metal_knob(base):
    """spun aluminium cap: radial anisotropy"""
    m = M("knob_metal")
    m.set(Base_Color=tuple(min(1, v * 0.9 + 0.08) for v in rgb(base)[:3]) + (1,), Metallic=1, Anisotropic=0.8)
    m.tangent_radial()
    m.link(m.ramp(m.noise(900, 2), 0.2, 0.26), "Roughness")
    m.link(m.bump(m.noise(1500, 2), 0.1, 0.0003), "Normal")
    return m.m


def leather(base):
    m = M("leather")
    edge = m.edge(0.004)
    m.link(m.rgb_mul(tuple(min(1, v * 1.2) for v in rgb(base)[:3]) + (1,), m.ramp(m.noise(8, 3), 0.9, 1.1)), "Base Color")
    m.link(m.math("SUBTRACT", m.ramp(m.noise(20, 2), 0.4, 0.6), m.math("MULTIPLY", edge, 0.15)), "Roughness")
    m.link(m.bump(m.noise(60, 4), 0.3, 0.001), "Normal")
    return m.m


def screw():
    m = M("screw")
    m.set(Metallic=1, Base_Color=(0.6, 0.6, 0.6, 1), Roughness=0.3)
    return m.m


def led(color_hex, strength=0.0):
    m = M("led")
    m.set(Base_Color=rgb(color_hex), Roughness=0.1, Emission_Color=rgb(color_hex), Emission_Strength=strength, Alpha=1.0)
    return m.m


def glass_dark():
    m = M("display_glass")
    m.set(Base_Color=(0.004, 0.006, 0.007, 1), Roughness=0.05, IOR=1.5, Coat_Weight=1.0, Coat_Roughness=0.03)
    return m.m


def wood(lo, hi, across="X", coat=0.0, coat_rough=0.25):
    """rough-sawn wood: wave bands along the plank, per-plank random offset/value, knots, dust, scuffs; no clear coat (args kept for callers)"""
    m = M("wood")
    oi = m.n("ShaderNodeObjectInfo")
    r = oi.outputs["Random"]
    mp = m.n("ShaderNodeMapping")
    m.nt.links.new(m.co, mp.inputs["Vector"])
    mp.inputs["Scale"].default_value = (1, 1, 0.08) if across == "X" else (0.08, 1, 1)
    m.nt.links.new(m.comb(m.math("MULTIPLY", r, 37.0), m.math("MULTIPLY", r, 11.0), m.math("MULTIPLY", r, 53.0)), mp.inputs["Location"])
    v = mp.outputs[0]
    w = m.n("ShaderNodeTexWave", wave_type="BANDS", bands_direction=across, wave_profile="SIN")
    m.nt.links.new(v, w.inputs["Vector"])
    w.inputs["Scale"].default_value, w.inputs["Distortion"].default_value, w.inputs["Detail"].default_value = 60.0, 7.0, 3.0
    vo = m.n("ShaderNodeTexVoronoi", feature="F1")
    m.nt.links.new(v, vo.inputs["Vector"])
    vo.inputs["Scale"].default_value = 2.2
    knot = m.math("MULTIPLY", m.math("LESS_THAN", vo.outputs["Distance"], 0.1), m.math("GREATER_THAN", m.noise(3, 2, vec=v), 0.5))
    fac = m.math("MULTIPLY", w.outputs["Fac"], m.ramp(m.noise(8, 4, vec=v), 0.5, 1.2))
    col = m.ramp(fac, rgb(lo), rgb(hi))
    vr = m.math("ADD", m.math("MULTIPLY", r, 0.3), 0.85)
    dusty = m.mixc(m.math("MULTIPLY", m.dust(5.0, 0.8), 0.5), m.rgb_mul(col, vr), (0.12, 0.1, 0.085, 1))
    scuf = m.math("MULTIPLY", m.math("GREATER_THAN", m.noise(10, 4), 0.58), 0.08)
    m.link(m.mixc(knot, m.mixc(scuf, dusty, (0.14, 0.1, 0.07, 1)), (0.015, 0.008, 0.004, 1)), "Base Color")
    m.link(m.bump(m.math("ADD", m.noise(220, 4, vec=v), m.math("MULTIPLY", w.outputs["Fac"], 0.6)), 0.5, 0.0012), "Normal")
    m.link(m.ramp(m.noise(14, 2), 0.62, 0.85), "Roughness")
    m.set(IOR=1.45, Specular_IOR_Level=0.3)
    return m.m


def rug():
    """original procedural rug (object-space metres; 2.6 x 1.5): bands + zig-zag frieze + stepped-diamond medallion + stepped crosses on a 4 mm knot grid"""
    m = M("rug")
    S = m.math
    sx, sy, _z = m.xyz()
    jit = S("MULTIPLY", S("SUBTRACT", m.noise(120, 2), 0.5), 0.003)
    K = 3000.0  # ~continuous: edges are anti-aliased by the render samples, not stair-stepped

    def q(v):
        return S("DIVIDE", S("FLOOR", S("MULTIPLY", S("ADD", v, jit), K)), K)

    def band(v, lo, hi):
        return S("MULTIPLY", S("GREATER_THAN", v, lo), S("LESS_THAN", v, hi))
    X, Y = q(sx), q(sy)
    ax, ay = S("ABSOLUTE", X), S("ABSOLUTE", Y)
    ex, ey = S("SUBTRACT", 1.3, ax), S("SUBTRACT", 0.75, ay)
    e = S("MINIMUM", ex, ey)
    side = S("LESS_THAN", ex, ey)
    run = S("ADD", S("MULTIPLY", side, Y), S("MULTIPLY", S("SUBTRACT", 1.0, side), X))
    tri = S("MULTIPLY", S("ABSOLUTE", S("SUBTRACT", S("FRACT", S("DIVIDE", run, 0.12)), 0.5)), 2.0)
    triq = tri
    w = S("DIVIDE", S("SUBTRACT", e, 0.10), 0.12)
    frieze = S("MULTIPLY", band(e, 0.10, 0.22), S("LESS_THAN", w, triq))
    border_black = S("MAXIMUM", S("MAXIMUM", S("LESS_THAN", e, 0.08), frieze), band(e, 0.22, 0.25))
    fld = S("GREATER_THAN", e, 0.25)
    dm = S("ADD", S("MULTIPLY", ax, 0.5), ay)
    ring = S("FLOOR", S("DIVIDE", dm, 0.06))
    med = S("MULTIPLY", S("LESS_THAN", dm, 0.5), fld)
    odd = S("FLOORED_MODULO", ring, 2.0)
    j = S("FLOOR", S("DIVIDE", Y, 0.22))
    xs = S("ADD", X, S("MULTIPLY", S("FLOORED_MODULO", j, 2.0), 0.11))
    i = S("FLOOR", S("DIVIDE", xs, 0.22))
    lx = S("ABSOLUTE", S("SUBTRACT", xs, S("MULTIPLY", S("ADD", i, 0.5), 0.22)))
    ly = S("ABSOLUTE", S("SUBTRACT", Y, S("MULTIPLY", S("ADD", j, 0.5), 0.22)))
    plus = S("MULTIPLY", S("MAXIMUM", S("LESS_THAN", lx, 0.014), S("LESS_THAN", ly, 0.014)), S("LESS_THAN", S("ADD", lx, ly), 0.07))
    hsh = S("FRACT", S("MULTIPLY", S("SINE", S("ADD", S("MULTIPLY", i, 12.9898), S("MULTIPLY", j, 78.233))), 43758.5453))
    cross = S("MULTIPLY", S("MULTIPLY", plus, S("GREATER_THAN", hsh, 0.88)), S("MULTIPLY", fld, S("GREATER_THAN", dm, 0.55)))
    drift = m.ramp(m.noise(1.5, 2, vec=m.comb(0.0, sy, 0.0)), 0.8, 1.15)
    kn = m.ramp(m.n("ShaderNodeTexWhiteNoise", noise_dimensions="3D").outputs["Value"], 0.96, 1.04)
    wn = [n for n in m.nt.nodes if n.bl_idname == "ShaderNodeTexWhiteNoise"][-1]
    m.nt.links.new(m.comb(X, Y, 0.0), wn.inputs["Vector"])
    red = m.rgb_mul(m.rgb_mul(rgb(TH["rug_red"]), drift), kn)
    dk = m.rgb_mul(rgb(TH["rug_red_dk"]), drift)
    blk = rgb(TH["rug_black"])
    col = m.mixc(S("MULTIPLY", med, odd), red, dk)
    col = m.mixc(S("MULTIPLY", med, S("SUBTRACT", 1.0, odd)), col, blk)
    col = m.mixc(cross, col, blk)
    col = m.mixc(border_black, col, blk)
    # worn patch where the player stands
    ell = S("ADD", S("POWER", S("DIVIDE", sx, 0.3), 2.0), S("POWER", S("DIVIDE", S("ADD", sy, 0.48), 0.175), 2.0))
    wear = S("MULTIPLY", S("SUBTRACT", 1.0, ell, clamp=True), m.ramp(m.noise(6, 2), 0.6, 1.4))
    wear = S("MINIMUM", wear, 1.0)
    fade = m.ramp(m.noise(2.5, 4, 0.6), 0.7, 1.1)  # sun-faded / worn patches over the whole rug
    grime = m.mixc(m.math("MULTIPLY", m.ramp(m.noise(9, 4), 0.0, 0.45), 1.0), m.rgb_mul(m.rgb_mul(col, fade), S("SUBTRACT", 1.0, S("MULTIPLY", wear, 0.2))), (0.05, 0.035, 0.03, 1))
    m.link(grime, "Base Color")
    h = S("ADD", S("MULTIPLY", m.voronoi(250, True), 0.6), S("MULTIPLY", m.white(250), 0.3))
    m.link(m.bump(h, 0.9, 0.004), "Normal")
    m.set(Roughness=0.95, Specular_IOR_Level=0.1, Sheen_Roughness=0.5, Sheen_Tint=(0.5, 0.25, 0.2, 1))
    m.link(S("SUBTRACT", 0.12, S("MULTIPLY", wear, 0.1)), "Sheen Weight")
    return m.m


def rug_bound():
    m = M("rug_bound")
    m.set(Base_Color=rgb(TH["rug_black"]), Roughness=0.95, Sheen_Weight=0.4)
    m.link(m.bump(m.math("ADD", m.voronoi(120, True), m.white(120)), 0.6, 0.002), "Normal")
    return m.m


def panel_cloth(base):
    """recipe 10 cloth: acoustic panel"""
    m = M("panel_fabric")
    w = m.math("ADD", m.wave(500, "X", 0.2), m.wave(480, "Y", 0.2))
    m.link(m.rgb_mul(rgb(base), m.ramp(m.math("ADD", w, m.noise(25, 2), clamp=True), 0.8, 1.15)), "Base Color")
    m.link(m.bump(m.math("ADD", w, m.voronoi(400)), 0.8, 0.0012), "Normal")
    m.set(Roughness=0.9, Sheen_Weight=0.4, Sheen_Roughness=0.5)
    return m.m


def satin(base, rough=0.5):
    m = M("satin")
    m.set(Base_Color=rgb(base), Roughness=rough)
    m.link(m.bump(m.noise(600, 3), 0.15, 0.0005), "Normal")
    return m.m


def steel_black(rough=0.45):
    """black powder-coated steel; edges wear to bare steel"""
    m = M("steel_black")
    m.set(Base_Color=(0.025, 0.025, 0.025, 1), Metallic=0)
    m.link(m.ramp(m.noise(20, 2), rough - 0.06, rough + 0.06), "Roughness")
    m.link(m.bump(m.noise(800, 2), 0.12, 0.0004), "Normal")
    m.wear(m.edge(0.002), Metallic=1, Base_Color=(0.6, 0.6, 0.6, 1), Roughness=0.35)
    return m.m


def hook_loop():
    """black hook-and-loop board covering"""
    m = M("hook_loop")
    m.set(Base_Color=(0.012, 0.012, 0.013, 1), Roughness=0.92, Sheen_Weight=0.08, Specular_IOR_Level=0.1, Sheen_Roughness=0.5)
    m.link(m.bump(m.math("ADD", m.voronoi(900, True), m.white(2500)), 0.7, 0.0015), "Normal")
    return m.m


def matte_emitter(col_hex, strength):
    m = M("emit")
    m.set(Base_Color=(0, 0, 0, 1), Emission_Color=rgb(col_hex), Emission_Strength=strength)
    return m.m


def lampshade(col_hex):
    """linen drum shade lit from inside: warm emission over a pale diffuse base"""
    m = M("lampshade")
    m.set(Base_Color=rgb(col_hex), Roughness=0.9, Emission_Color=rgb(col_hex), Emission_Strength=2.2, Sheen_Weight=0.3)
    m.link(m.bump(m.math("ADD", m.wave(500, "X", 0.2), m.wave(480, "Y", 0.2)), 0.4, 0.0008), "Normal")
    return m.m

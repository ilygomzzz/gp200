"""Design tokens (the only place with colour/size literals) + `qml_tokens()` for the QML view (specs 003 glass palette, 004 board)."""
import os

from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QColor

font, icon_font, mono = "Noto Sans", "JetBrainsMono Nerd Font Propo", "JetBrainsMono Nerd Font Mono"
font_small, font_body, font_title, font_display = 12, 14, 18, 24
font_desc = font_small  # alias kept for old call sites (13 folded into 12)
text, dim = "#ffffff", "#b4cbcd"  # ink, inkDim (foam)
ink_soft, ink_off = "#73ffffff", "#40ffffff"
accent, accent_deep, accent_text = "#5a86a8", "#25456a", "#ffffff"
danger, warn = "#e67c73", "#e0b050"
dusk, dusk_dark, tint = "#132238", "#0a111d", "#132238"
glass_alpha = 0.55
plate, plate_border = "#0fffffff", "#554a6e8d"
sel_fill, sel_border = "#24ffffff", "#40ffffff"
field_bg, field_border, popup_bg = "#4d0a111d", "#2effffff", "#f20a111d"
base, alt, button = field_bg, plate, sel_fill
user, tool = "#9cc3dd", "#8a9aa8"  # chat HTML (opaque hex: rich text)
drop = accent
block_colors = {"PRE": "#d4c45c", "WAH": "#c99a66", "DST": "#e0874f", "AMP": "#e8b04e", "NR": "#8fa3b3", "CAB": "#a68c78",
                "EQ": "#7fc8a9", "MOD": "#a98be0", "DLY": "#5fb8d6", "RVB": "#6f93e0", "VOL": "#b4cbcd"}
glyphs = {  # nf-md-*, codepoints read from the installed JetBrainsMono Nerd Font Propo
    "PRE": 0xF013F, "WAH": 0xF0F52, "DST": 0xF140B, "AMP": 0xF0030, "NR": 0xF0581, "CAB": 0xF04C3, "EQ": 0xF0EA2,
    "MOD": 0xF095B, "DLY": 0xF0456, "RVB": 0xF078D, "VOL": 0xF057E,
    "app": 0xF02C4, "search": 0xF0349, "reload": 0xF0450, "power": 0xF0425, "lock": 0xF033E, "ok": 0xF05E0,
    "busy": 0xF0996, "error": 0xF0028, "new_chat": 0xF140F, "send": 0xF048A, "chat": 0xF0B79, "empty": 0xF02C5}
glyphs = {k: chr(v) for k, v in glyphs.items()}
s1, s2, s3, s4, s5, s6 = 4, 8, 12, 16, 24, 32
r_plate, r_card, r_tile, r_pill, r_unit = 20, 8, 12, 999, 12
glass = False  # set by apply()

# --- spec 004 pedalboard tokens ---
chassis_base, cable, jack = "#2a2f36", "#15171a", "#9aa3ab"
metal, metal_dark = "#c3c9ce", "#6b737a"
knob_cap, knob_cap_hi, knob_skirt, knob_knurl = "#1b1d21", "#3c4048", "#2b2e34", "#4a4f57"
bevel_hi, shadow, scrim, pilot, ok = "#26ffffff", "#8c000000", "#66000000", "#e0453a", "#7fc8a9"
ink_dark = "#14171a"  # print on mid-tone chassis
meter_lo, meter_hi = "#5fb8d6", "#e0b050"
font_value = 24
# gear families (spec 004): body / face / ink (print on face) / knob; cabs: body = tolex, face = grille cloth, knob = piping
chassis = {
    "brushed": dict(body="#b9bec4", face="#d3d7db", ink="#14171a", knob="#2b2e34"),
    "cream": dict(body="#d9ccae", face="#e8dfc7", ink="#14171a", knob="#2b2e34"),
    "od_green": dict(body="#4f9a62", face="#68b27a", ink="#0f1a12", knob="#1b1d21"),
    "dist_orange": dict(body="#d9793a", face="#ec9654", ink="#1c1109", knob="#1b1d21"),
    "fuzz_violet": dict(body="#7d5cc2", face="#9a7fd8", ink="#ffffff", knob="#e8e4f0"),
    "metal_black": dict(body="#25272b", face="#33363b", ink="#e9edf0", knob="#9aa3ab"),
    "gate_grey": dict(body="#6f7b86", face="#8794a0", ink="#10151a", knob="#1b1d21"),
    "eq_white": dict(body="#e6e8ea", face="#f4f5f6", ink="#14171a", knob="#2b2e34"),
    "treadle_black": dict(body="#1f2124", face="#2b2e33", ink="#e9edf0", knob="#9aa3ab"),
    "brit_gold": dict(body="#15161a", face="#c9a24a", ink="#1c1405", knob="#e8dcc0"),
    "tweed": dict(body="#b59a62", face="#c9ccd0", ink="#1b1d21", knob="#2b2e34"),
    "blackface": dict(body="#1a1b1f", face="#25272c", ink="#e9edf0", knob="#c3c9ce"),
    "copper": dict(body="#2d2824", face="#b8743f", ink="#1e1006", knob="#14171a"),
    "steel": dict(body="#17191c", face="#8c949b", ink="#101214", knob="#1b1d21"),
    "graphite": dict(body="#202328", face="#3a3f46", ink="#e9edf0", knob="#c3c9ce"),
    "grille_wheat": dict(body="#15161a", face="#c8b57e", ink="#14171a", knob="#e8dcc0"),
    "grille_silver": dict(body="#1a1b1f", face="#a9afb5", ink="#14171a", knob="#c3c9ce"),
    "grille_black": dict(body="#17181b", face="#1d1f23", ink="#e9edf0", knob="#6b737a"),
    "rack_dark": dict(body="#202328", face="#2a2e34", ink="#e9edf0", knob="#c3c9ce", display="#0c1416"),
}
# rig scene (spec 004 part B); stage_w/stage_h/chip_h in stage units / px
stage_wall, stage_wall_hi, stage_mat, stage_horizon = "#0c121a", "#3a3326", "#101214", 0.58  # hi = warm key light
board_tolex, rail = "#1c1d20", "#8c949b"
# render-only palette (2C revision: wooden room, rug, rubber); not exposed to QML
wood_lo, wood_hi, floor_lo, floor_hi = "#2a160b", "#7a4a2a", "#1e0f08", "#5a3420"
rug_red, rug_red_dk, rug_black, panel_cloth, rubber, cone = "#8c1c17", "#4a0e0c", "#141010", "#3a2a20", "#0e0f10", "#16171a"
tex_tolex, tex_powder, tex_brushed, tex_grille, tex_tread, tex_mat, tex_shadow, tex_spot = 0.18, 0.07, 0.2, 0.45, 0.14, 0.14, 0.6, 0.3
stage_w, stage_h, chip_h = 1600, 520, 32
cable_hi, cable_shadow, sel_pool, ghost_op = "#4a4d55", "#000000aa", 0.35, 0.4  # rendered-art cables / selection light pool / ghost units
render_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "render")
tex_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "textures")
face_hi, face_lo, nameplate = "#1fffffff", "#2e000000", "#e614171a"  # enamel overlay + dark print band
led_off, track_on_face, tick = "#73000000", "#4d14171a", "#9914171a"
knob_face, face_max_h, track_code = 72, 344, 1.2  # 344 not 296: picker plate is 60 tall (name+desc) and the switch sits inside the face
cell_w, cell_h, cell_gap, knob_big, knob_mini, w_wide, w_medium = 92, 144, 12, 64, 16, 1440, 1100
fx = os.environ.get("GP200_FX") != "0"  # MultiEffect shadows/glow (off for offscreen shots: layers do not render there)
motion = os.environ.get("GP200_MOTION") != "0"
durations = {"dur_s": 100, "dur_m": 200, "dur_l": 400}  # 0 when motion is off (see qml_tokens)


def q(c, a=None):
    """QColor from a token; a = alpha 0..1 replacing the token's own alpha."""
    c = QColor(c)
    if a is not None:
        c.setAlphaF(a)
    return c


def mix(c1, c2, t):
    a, b = QColor(c1), QColor(c2)
    return QColor(*(round(x * (1 - t) + y * t) for x, y in zip(a.getRgb()[:3], b.getRgb()[:3])))


bg = mix(dusk_dark, tint, glass_alpha)  # opaque fallback; apply() makes it translucent on Hyprland


def apply(platform):
    """Decide glass from the Qt platform name + environment (Hyprland on Wayland, not GP200_GLASS=0)."""
    global glass, bg
    glass = platform == "wayland" and bool(os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")) and os.environ.get("GP200_GLASS") != "0"
    bg = q(tint, glass_alpha) if glass else mix(dusk_dark, tint, glass_alpha)


def _qml(v):
    if isinstance(v, QColor):
        return v.name(QColor.NameFormat.HexArgb)
    if isinstance(v, str) and v.startswith("#"):
        return QColor(v).name(QColor.NameFormat.HexArgb)
    if isinstance(v, dict):
        return {k: _qml(x) for k, x in v.items()}
    return v


def qml_tokens():
    """Plain dict of every token for the QML context property `T` (colours as #AARRGGBB)."""
    names = ("font icon_font mono font_small font_desc font_body font_title font_display text dim ink_soft ink_off accent accent_deep "
             "accent_text danger warn plate plate_border sel_fill sel_border field_bg field_border popup_bg block_colors glyphs s1 s2 s3 s4 "
             "s5 s6 r_plate r_card r_tile r_pill glass bg glass_alpha chassis_base cable jack metal metal_dark knob_cap knob_cap_hi "
             "knob_skirt knob_knurl ink_dark fx bevel_hi shadow scrim pilot ok meter_lo meter_hi font_value cell_w cell_h cell_gap knob_big knob_mini "
             "w_wide w_medium motion face_hi face_lo nameplate led_off track_on_face tick knob_face face_max_h r_unit track_code chassis stage_wall stage_wall_hi stage_mat stage_horizon board_tolex rail "
             "tex_tolex tex_powder tex_brushed tex_grille tex_tread tex_mat tex_shadow tex_spot stage_w stage_h chip_h cable_hi cable_shadow sel_pool ghost_op").split()
    out = {n: _qml(globals()[n]) for n in names}
    out["tex_dir"] = QUrl.fromLocalFile(tex_dir).toString() + "/"
    out["render_dir"] = QUrl.fromLocalFile(render_dir).toString() + "/"
    out.update({k: v if motion else 0 for k, v in durations.items()})
    return out

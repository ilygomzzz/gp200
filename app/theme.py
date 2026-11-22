"""Design tokens (the only place with colour/size literals) + `qml_tokens()` for the QML view (specs 003 glass palette, 004 board)."""
import os

from PyQt6.QtGui import QColor

font, icon_font, mono = "Noto Sans", "JetBrainsMono Nerd Font Propo", "JetBrainsMono Nerd Font Mono"
font_small, font_desc, font_body, font_title, font_display = 12, 13, 14, 18, 24
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
r_plate, r_card, r_tile, r_pill = 20, 8, 12, 999
glass = False  # set by apply()

# --- spec 004 pedalboard tokens ---
chassis_base, cable, jack = "#2a2f36", "#15171a", "#9aa3ab"
metal, metal_dark = "#c3c9ce", "#6b737a"
knob_cap, knob_cap_hi, knob_skirt, knob_knurl = "#1b1d21", "#3c4048", "#2b2e34", "#4a4f57"
bevel_hi, shadow, scrim, pilot, ok = "#26ffffff", "#8c000000", "#66000000", "#e0453a", "#7fc8a9"
ink_dark = "#14171a"  # print on mid-tone chassis
meter_lo, meter_hi = "#5fb8d6", "#e0b050"
font_value = 24
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
             "w_wide w_medium motion").split()
    out = {n: _qml(globals()[n]) for n in names}
    out.update({k: v if motion else 0 for k, v in durations.items()})
    return out

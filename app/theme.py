"""Design tokens (the only place with colour/size literals) + app-wide palette/stylesheet. Spec 003: own fixed glass palette."""
import os

from PyQt6.QtGui import QColor, QFont, QPalette

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


def q(c, a=None):
    """QColor from a token; a = alpha 0..1 replacing the token's own alpha."""
    c = QColor(c)
    if a is not None:
        c.setAlphaF(a)
    return c


def css(c, a=None):
    c = q(c, a)
    return f"rgba({c.red()},{c.green()},{c.blue()},{c.alphaF():.3f})"


def mix(c1, c2, t):
    a, b = QColor(c1), QColor(c2)
    return QColor(*(round(x * (1 - t) + y * t) for x, y in zip(a.getRgb()[:3], b.getRgb()[:3])))


def ifont(px):
    f = QFont(icon_font)
    f.setPixelSize(px)
    return f


def icon_html(name, color=None):
    c = f";color:{color}" if color else ""
    return f'<span style="font-family:\'{icon_font}\'{c}">{glyphs[name]}</span>'


bg = mix(dusk_dark, tint, glass_alpha)  # opaque fallback; apply() makes it translucent on Hyprland


def apply(app):
    global glass, bg
    glass = (app.platformName() == "wayland" and bool(os.environ.get("HYPRLAND_INSTANCE_SIGNATURE"))
             and os.environ.get("GP200_GLASS") != "0")
    bg = q(tint, glass_alpha) if glass else mix(dusk_dark, tint, glass_alpha)
    app.setStyle("Fusion")
    f = QFont(font)
    f.setPixelSize(font_body)
    app.setFont(f)
    pal = QPalette()
    for role, c in [("Window", QColor(0, 0, 0, 0) if glass else bg), ("WindowText", q(text)), ("Base", q(base)), ("AlternateBase", q(alt)),
                    ("Text", q(text)), ("Button", q(button)), ("ButtonText", q(text)), ("Highlight", q(accent)),
                    ("HighlightedText", q(accent_text)), ("PlaceholderText", q(ink_soft)), ("ToolTipBase", q(popup_bg)),
                    ("ToolTipText", q(text))]:
        pal.setColor(getattr(QPalette.ColorRole, role), c)
    for role in ("ButtonText", "WindowText", "Text"):
        pal.setColor(QPalette.ColorGroup.Disabled, getattr(QPalette.ColorRole, role), q(ink_soft))
    app.setPalette(pal)
    pill = lambda h: f"border-radius:{h // 2}px;min-height:{h - 2}px;max-height:{h - 2}px"
    app.setStyleSheet(f"""
QFrame#plate {{ background:{css(plate)}; border:1px solid {css(plate_border)}; border-radius:{r_plate}px; }}
QFrame#bar {{ background:{css(plate)}; border:1px solid {css(plate_border)}; border-left:{s1}px solid {warn}; border-radius:{r_tile}px; }}
QLabel#pill {{ background:{css(plate)}; border:1px solid {css(plate_border)}; color:{dim}; font-size:{font_desc}px; padding:0 {s3}px; {pill(28)}; }}
QLabel#slotpill {{ background:{accent_deep}; color:{accent_text}; font-weight:bold; font-size:{font_body}px; padding:0 {s3}px; {pill(32)}; }}
QPushButton {{ background:transparent; border:1px solid {css(sel_border)}; color:{text}; padding:0 {s4}px; {pill(32)}; }}
QPushButton:hover {{ background:{css(sel_fill)}; }}
QPushButton:disabled {{ color:{css(ink_soft)}; border-color:{css(ink_off)}; background:transparent; }}
QPushButton#primary {{ background:{accent}; border:1px solid {accent}; color:{accent_text}; font-weight:bold; }}
QPushButton#primary:disabled {{ background:transparent; border-color:{css(ink_off)}; color:{css(ink_soft)}; }}
QPushButton#icon {{ border:none; padding:0; min-width:32px; max-width:32px; font-family:'{icon_font}'; font-size:18px; }}
QPushButton#power {{ border-radius:20px; min-width:38px; max-width:38px; min-height:38px; max-height:38px; padding:0; font-family:'{icon_font}'; font-size:20px; }}
QLineEdit {{ background:{css(field_bg)}; border:1px solid {css(field_border)}; padding:0 {s3}px; selection-background-color:{accent}; {pill(32)}; }}
QLineEdit#title {{ background:transparent; border:1px solid transparent; font-size:{font_display}px; font-weight:bold; padding:0 {s2}px; border-radius:{r_tile}px; min-height:44px; max-height:44px; }}
QLineEdit#title:focus, QLineEdit#title:hover {{ background:{css(field_bg)}; border-color:{css(field_border)}; }}
QLineEdit#input {{ {pill(40)}; padding-right:44px; }}
QComboBox {{ background:{css(field_bg)}; border:1px solid {css(field_border)}; padding:0 {s3}px; {pill(32)}; }}
QComboBox:disabled {{ color:{css(ink_soft)}; }}
QTabBar {{ background:transparent; }}
QTabBar::tab {{ background:{css(plate)}; border:1px solid {css(plate_border)}; color:{dim}; padding:0 {s4}px; min-height:30px; }}
QTabBar::tab:selected {{ background:{accent}; border-color:{accent}; color:{accent_text}; font-weight:bold; }}
QTabBar::tab:first {{ border-top-left-radius:16px; border-bottom-left-radius:16px; }}
QTabBar::tab:last {{ border-top-right-radius:16px; border-bottom-right-radius:16px; }}
QTabWidget::pane {{ border:0; background:transparent; top:{s3}px; }}
QScrollArea, QScrollArea > QWidget > QWidget {{ background:transparent; }}
QScrollBar:vertical {{ background:transparent; width:6px; margin:0; }}
QScrollBar:horizontal {{ background:transparent; height:6px; margin:0; }}
QScrollBar::handle {{ background:{css(sel_border)}; border-radius:3px; min-height:24px; min-width:24px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ width:0; height:0; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background:transparent; }}
QSplitter::handle:hover {{ background:{css(sel_fill)}; border-radius:3px; }}
QProgressBar {{ background:transparent; border:0; min-height:2px; max-height:2px; }}
QProgressBar::chunk {{ background:{accent}; }}
QTextBrowser {{ background:transparent; border:0; }}
QMenu, QComboBox QAbstractItemView, QToolTip {{ background:{css(popup_bg)}; color:{text}; border:1px solid {css(sel_border)}; padding:{s1}px; }}
QMenu::item {{ padding:{s1}px {s4}px; border-radius:{s1}px; }}
QMenu::item:selected, QComboBox QAbstractItemView::item:selected {{ background:{accent}; }}
""")

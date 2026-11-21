"""Design tokens (the only place with colour/size literals) + app-wide palette/stylesheet."""
from PyQt6.QtGui import QColor, QPalette

bg, base, alt, button = "#202124", "#17181a", "#26272a", "#2c2d30"
text, dim = "#dddddd", "#777777"
accent, accent_text = "#3d6fb3", "#ffffff"
danger, user, tool = "#ff8888", "#88ccff", "#888888"
led_on, warn = "#6fbf73", "#e0b050"
drop = accent
s1, s2, s3, s4 = 4, 8, 12, 16
radius = 6
font_small, font_body, font_title = 12, 14, 18
mono = "monospace"


def apply(app):
    app.setStyle("Fusion")
    pal = QPalette()
    for role, c in [("Window", bg), ("WindowText", text), ("Base", base), ("AlternateBase", alt), ("Text", text),
                    ("Button", button), ("ButtonText", text), ("Highlight", accent), ("HighlightedText", accent_text),
                    ("PlaceholderText", dim)]:
        pal.setColor(getattr(QPalette.ColorRole, role), QColor(c))
    pal.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(dim))
    pal.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(dim))
    pal.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(dim))
    app.setPalette(pal)
    app.setStyleSheet(f"QPushButton#primary {{ background: {accent}; color: {accent_text}; border-radius: {radius}px; padding: {s1}px {s3}px; }}"
                      f"QPushButton#primary:disabled {{ background: {button}; color: {dim}; }}"
                      f"QFrame#bar {{ background: {alt}; border-left: {s1}px solid {warn}; }}")

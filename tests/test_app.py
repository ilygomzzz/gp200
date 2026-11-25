"""Offline checks for the app's pure helpers. Run: python3 -m unittest discover tests"""
import json
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "app"))
try:
    import chat as a
except ImportError:  # PyQt6 missing
    a = None
try:
    import theme
    from PyQt6.QtGui import QColor
except ImportError:
    theme = None


@unittest.skipIf(a is None, "PyQt6 not installed")
class Chat(unittest.TestCase):
    def test_parse_stream_json(self):
        ev = lambda d: json.dumps(d).encode()
        self.assertEqual(a.parse_event(ev({"type": "system", "subtype": "init", "session_id": "abc"})), [("session", "abc")])
        msg = {"type": "assistant", "message": {"content": [
            {"type": "text", "text": " Hola "},
            {"type": "tool_use", "name": "Bash", "input": {"command": "gp200 write 34B presets/x.json"}}]}}
        self.assertEqual(a.parse_event(ev(msg)), [("text", "Hola"), ("tool", "gp200 write 34B presets/x.json")])
        self.assertEqual(a.parse_event(ev({"type": "result", "is_error": True, "result": "boom"})), [("error", "boom")])
        self.assertEqual(a.parse_event(b"not json"), [])

    def test_touched_slots(self):
        self.assertEqual(a.touched_slots("gp200 write 34B x.json && gp200 select 34b"), ["34B", "34b"])
        self.assertEqual(a.touched_slots("gp200 show 34B"), [])


def _colours(v):
    if isinstance(v, dict):
        for x in v.values():
            yield from _colours(x)
    elif isinstance(v, str) and v.startswith("#"):
        yield v


@unittest.skipIf(theme is None, "PyQt6 not installed")
class Tokens(unittest.TestCase):
    def test_colours_parse_and_motion(self):
        t = theme.qml_tokens()
        cols = list(_colours(t))
        self.assertGreater(len(cols), 30)
        self.assertTrue(all(QColor(c).isValid() and len(c) == 9 for c in cols), cols)
        self.assertTrue(all(t[k] > 0 for k in theme.durations))
        old = theme.motion
        theme.motion = False
        try:
            self.assertTrue(all(theme.qml_tokens()[k] == 0 for k in theme.durations))
        finally:
            theme.motion = old


def _lum(c):
    f = lambda v: v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(c.redF()) + 0.7152 * f(c.greenF()) + 0.0722 * f(c.blueF())


def contrast(fg, bg):
    a, b = sorted((_lum(QColor(fg)), _lum(QColor(bg))), reverse=True)
    return (a + 0.05) / (b + 0.05)


@unittest.skipIf(theme is None, "PyQt6 not installed")
class Polish(unittest.TestCase):
    def test_new_tokens_exported(self):
        t = theme.qml_tokens()
        for k in "face_hi face_lo nameplate led_off track_on_face tick knob_face face_max_h r_unit track_code".split():
            self.assertIn(k, t)
        self.assertEqual(t["font_desc"], t["font_small"])

    def test_block_colours_readable_on_nameplate(self):
        # nameplate (90 % opaque) over the enamel face = chassis tinted 60 % with the block colour
        plate = QColor(theme.nameplate)
        for blk, col in theme.block_colors.items():
            u = theme.mix(theme.chassis_base, col, 0.6)
            flat = QColor.fromRgbF(*(plate.getRgbF()[i] * plate.alphaF() + u.getRgbF()[i] * (1 - plate.alphaF()) for i in range(3)))
            r = contrast(col, flat)
            print(f"contrast {blk} {r:.2f}")
            self.assertGreaterEqual(r, 4.5, blk)


@unittest.skipIf(theme is None, "PyQt6 not installed")
class QmlSmoke(unittest.TestCase):
    def test_main_loads_without_warnings(self):
        import os
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
        import tempfile
        from PyQt6.QtCore import QUrl, pyqtSignal
        from PyQt6.QtGui import QGuiApplication
        from PyQt6.QtQml import QQmlApplicationEngine
        import bridge, gp200_app, model
        sys.path.insert(0, str(Path(__file__).parent))
        from test_bridge import Pedal

        class P(Pedal):
            held = pyqtSignal()
        app = QGuiApplication.instance() or QGuiApplication([])
        p = P()
        hub = a.ChatHub(p, a.ChatStore(tempfile.mktemp()))
        wb = model.Workbench(p)
        board = bridge.Board(wb)
        eng, warnings = QQmlApplicationEngine(), []
        eng.warnings.connect(lambda ws: warnings.extend(w.toString() for w in ws))
        ctx = eng.rootContext()
        for n, o in (("T", theme.qml_tokens()), ("R", __import__("art").load_manifest(theme.render_dir + "/manifest.json")), ("board", board), ("slotChat", bridge.ChatView(hub, wb)),
                     ("globalChat", bridge.ChatView(hub, wb, True)), ("pedal", p)):
            ctx.setContextProperty(n, o)
        eng.load(QUrl.fromLocalFile(str(gp200_app.QML)))
        self.assertTrue(eng.rootObjects())
        board.openSlot(100)
        app.processEvents()
        self.assertEqual(warnings, [])


if __name__ == "__main__":
    unittest.main()

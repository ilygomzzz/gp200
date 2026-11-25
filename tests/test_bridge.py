"""Board / ChatView view-models over a fake pedal and hub. Run: python3 -m unittest discover tests"""
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).parent.parent / "app"))
sys.path.insert(0, str(Path(__file__).parent))
try:
    from PyQt6.QtCore import QCoreApplication, pyqtSignal
    import bridge
    import model as m
    from test_model import FakePedal, preset
except ImportError:
    bridge = None


if bridge:
    class Pedal(FakePedal):
        slot_name, scan_done = pyqtSignal(int, str), pyqtSignal()

        def scan(self, slots):
            self.calls.append(("scan", len(list(slots))))


@unittest.skipIf(bridge is None, "PyQt6 not installed")
class RackArtTests(unittest.TestCase):
    def test_rack_display(self):
        self.assertEqual(bridge.rack_display("DLY", [("Feedback", 20), ("Time", 500), ("Mix", 30)]),
                         (["500 ms", "Mix 30"], ["500 ms", "Mix 30"]))
        self.assertEqual(bridge.rack_display("AMP", [("Gain", 5)]), (["Gain 5"], ["Gain 5"]))
        self.assertEqual(bridge.rack_display("DLY", []), ([], []))

    def test_unit_view_key(self):
        self.assertEqual(bridge.unit_view(preset(), "DLY")["key"], "rack/DLY")
        self.assertTrue(bridge.unit_view(preset(), "CAB")["key"].startswith("CAB/"))
        self.assertTrue(bridge.unit_view(preset(), "AMP")["key"].startswith("AMP/"))

    def test_unit_view_art_fields(self):
        v = bridge.unit_view(preset(), "DLY")
        self.assertEqual((v["kind"], v["family"]), ("rack", "rack_dark"))
        self.assertEqual(len(v["display"]), len(v["displayShort"]))
        self.assertLessEqual(len(v["knobs"]), 8)
        self.assertEqual(len(v["knobs"]), len(v["labels"]))
        self.assertEqual(bridge.unit_view(preset(), "CAB")["kind"], "cabinet")


@unittest.skipIf(bridge is None, "PyQt6 not installed")
class BoardTests(unittest.TestCase):
    def setUp(self):
        QCoreApplication.instance() or QCoreApplication([])
        self.p = Pedal()
        self.wb = m.Workbench(self.p)
        self.b = bridge.Board(self.wb)

    def test_open_edit_move_dirty(self):
        self.assertFalse(self.b.property("open"))
        self.wb.select_block("AMP")
        self.b.openSlot(100)
        self.assertTrue(self.b.property("open"))
        self.assertEqual(sorted(self.b.property("order")), sorted(m.g.BLOCKS))
        self.assertEqual(set(self.b.property("units")), set(m.g.BLOCKS))
        params, hits = self.b.property("params"), {"params": 0, "values": 0, "order": 0}
        self.b.paramsChanged.connect(lambda: hits.__setitem__("params", hits["params"] + 1))
        self.b.valuesChanged.connect(lambda: hits.__setitem__("values", hits["values"] + 1))
        self.b.chainChanged.connect(lambda: hits.__setitem__("order", hits["order"] + 1))
        name = params[0]["name"]
        self.b.setParam(name, params[0]["max"])
        self.assertEqual(self.b.property("values")[name], params[0]["max"])
        self.assertEqual((hits["params"], hits["values"]), (0, 1))  # knob delegates keep their params
        self.assertTrue(self.b.property("dirty"))
        before = self.b.property("order")
        self.b.moveTo(before[0], 3)
        self.assertEqual(self.b.property("order")[2], before[0])
        self.assertGreaterEqual(hits["order"], 2)
        self.b.setEffect(self.b.property("effects")[0])
        self.assertEqual(hits["params"], 1)

    def test_guard_busy_status(self):
        self.b.openSlot(100)
        self.b.toggle("AMP")
        self.b.openSlot(101)
        self.assertEqual(self.b.property("guard"), "34B")
        self.b.confirmSwitch()
        self.assertEqual((self.b.property("guard"), self.b.property("slot")), ("", 101))
        self.p.busy_changed.emit("save")
        self.assertEqual(self.b.property("busy"), "save")
        self.p.busy_changed.emit("claude")
        self.assertEqual(self.b.property("status"), "Claude está usando la pedalera…")
        self.p.busy_changed.emit(None)
        self.assertEqual(self.b.property("busy"), "")
        self.p.slot_name.emit(100, m.EMPTY)
        self.p.slot_name.emit(101, m.EMPTY)
        self.assertEqual([f["slot"] for f in self.b.property("freeSlots")], [100, 101])

    def test_chat_view_send_and_lock(self):
        hub = mock.MagicMock()
        hub.active = None
        hub.session.side_effect = lambda k: mock.MagicMock(html="", restored=False)
        v = bridge.ChatView(hub, self.wb)
        self.assertFalse(v.property("bound"))
        self.b.openSlot(100)
        self.assertEqual(v.property("title").split()[:3], ["Chat", "·", "34B"])
        v.send("hola")
        key, text, sysp = hub.send.call_args.args
        self.assertEqual((key, text), ("34B", "hola"))
        self.assertIn("slot 34B", sysp)
        hub.active = object()
        hub.send.reset_mock()
        self.assertEqual(v.property("locked"), "Claude está respondiendo…")
        v.send("otra")
        hub.send.assert_not_called()
        g = bridge.ChatView(hub, self.wb, True)  # global chat: no preset in the prompt
        hub.active = None
        g.send("hola")
        self.assertEqual(hub.send.call_args.args[0], "global")
        self.assertEqual(hub.send.call_args.args[2], __import__("chat").SYSTEM)


if __name__ == "__main__":
    unittest.main()


class CablePath(unittest.TestCase):
    RECTS = [(574, 60, 249, 111), (573, 179, 250, 173), (556, 373, 70, 88), (637, 373, 70, 88), (936, 152, 174, 45)]

    def test_endpoints_deterministic_and_clear(self):
        import art
        for p0, p1 in (((70, 470), (556, 430)), ((700, 400), (1100, 200)), ((800, 250), (1500, 232))):
            a, b = art.cable_path(p0, p1, self.RECTS, 1), art.cable_path(p0, p1, self.RECTS, 1)
            self.assertEqual(a, b)
            self.assertEqual((a[0], a[-1]), (p0, p1))
            own = [r for r in self.RECTS for p in (p0, p1) if r[0] - 8 <= p[0] <= r[0] + r[2] + 8 and r[1] - 8 <= p[1] <= r[1] + r[3] + 8]
            self.assertFalse(art._hits(a, self.RECTS, own), (p0, p1))

    def test_negative_lane_drops_blocked(self):
        import art
        self.assertEqual(art.cable_path((0, 100), (200, 100), [(90, 50, 20, 100)], -1), [])
        self.assertTrue(art.cable_path((0, 100), (200, 100), [], -1))

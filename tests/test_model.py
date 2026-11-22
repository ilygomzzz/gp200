"""Pure model/chat helpers + Pedal queue + Workbench with a fake pedal. Run: python3 -m unittest discover tests"""
import copy
import json
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).parent.parent / "app"))
sys.path.insert(0, str(Path(__file__).parent))
try:
    from PyQt6.QtCore import QCoreApplication, QObject, pyqtSignal
    import chat
    import model as m
except ImportError:
    m = None
from test_codec import FakeDev

g = m.g if m else None


def preset():
    return g.decode_preset(FakeDev().raw)


@unittest.skipIf(m is None, "PyQt6 not installed")
class Helpers(unittest.TestCase):
    def test_effects_for_amp(self):
        eff = m.effects_for("AMP")
        self.assertTrue(all(i["module"] == "AMP" for _, i in eff))
        names = [m.snap_label(e, i).lower() for e, i in eff]
        self.assertEqual(names, sorted(names))
        self.assertIn("SnapTone 1", [m.snap_label(e, i) for e, i in eff])

    def test_slot_matches(self):
        self.assertTrue(m.slot_matches("34B", "Crunch AZ", ""))
        self.assertTrue(m.slot_matches("34B", "Crunch AZ", "34b"))
        self.assertTrue(m.slot_matches("34B", "Crunch AZ", "  CRUN"))
        self.assertFalse(m.slot_matches("34B", "Crunch AZ", "lead"))
        self.assertTrue(m.slot_matches("34A", m.EMPTY, "vací"))
        self.assertFalse(m.slot_matches("34A", None, "vacío"))

    def test_move_block_clamps(self):
        self.assertEqual(m.move_block(g.BLOCKS, "PRE", -1), g.BLOCKS)
        self.assertEqual(m.move_block(g.BLOCKS, "VOL", 1), g.BLOCKS)
        self.assertEqual(m.move_block(g.BLOCKS, "PRE", 2)[:3], ["WAH", "DST", "PRE"])

    def test_effect_edit(self):
        p = preset()
        eid, info = next((e, i) for e, i in m.effects_for("AMP") if i["name"] != p["blocks"]["AMP"]["effect"])
        new, msgs = m.edit_msgs(p, ("effect", "AMP", info["name"]))
        self.assertEqual(msgs[0], (g.msg_effect(3, eid), 0.4))
        first = (g.msg_param(3, info["params"][0]["idx"], eid, info["params"][0]["default"]), 0.04)
        self.assertEqual((msgs[1], msgs[-1]), (first, first))
        self.assertEqual(new["blocks"]["AMP"]["params"], {x["name"]: x["default"] for x in info["params"]})

    def test_param_edit_fresh_twice_and_clamped(self):
        p = preset()
        name = next(iter(g.EFFECTS[next(e for e, i in g.EFFECTS.items() if i["name"] == p["blocks"]["AMP"]["effect"] and i["module"] == "AMP")]["params"]))["name"]
        new, msgs = m.edit_msgs(p, ("param", "AMP", name, 1e6), fresh={"AMP"})
        self.assertEqual(len(msgs), 2)
        self.assertLessEqual(new["blocks"]["AMP"]["params"][name], 100)
        self.assertEqual(len(m.edit_msgs(p, ("param", "AMP", name, 5))[1]), 1)
        with self.assertRaises(ValueError):
            m.edit_msgs(p, ("effect", "AMP", "nope"))

    def test_free_slots(self):
        names = {98: m.EMPTY, 99: m.EMPTY, 100: "Mine", 101: m.EMPTY, 254: m.EMPTY}
        self.assertEqual(m.free_slots(names), [99, 101])

    def test_clean_drops_raw_params(self):
        p = preset()
        p["blocks"]["AMP"]["params"]["#9"] = 1.0
        self.assertNotIn("#9", m.clean(p)["blocks"]["AMP"]["params"])


@unittest.skipIf(m is None, "PyQt6 not installed")
class Prompts(unittest.TestCase):
    def test_slot_prompt(self):
        s = chat.system_prompt("34A", preset(), True)
        self.assertIn("slot 34A 'Test'", s)
        self.assertIn("unsaved live edits: yes", s)
        js = json.loads(s[s.index("{"):s.rindex("}") + 1])
        self.assertEqual(js["name"], "Test")
        self.assertEqual(chat.system_prompt(), chat.SYSTEM)

    def test_sessions_separate(self):
        hub = chat.ChatHub(mock.MagicMock(), chat.ChatStore("/nonexistent/x.json"))
        hub.session("34A").session_id = "a"
        self.assertIsNone(hub.session("34B").session_id)
        self.assertIsNone(hub.session("global").session_id)

    def test_failed_start_finishes(self):  # else the hub never releases the pedal ("busy" forever)
        app = QCoreApplication.instance() or QCoreApplication([])
        s, got = chat.ChatSession(), []
        s.finished.connect(got.append)
        with tempfile.TemporaryDirectory() as d, mock.patch.dict(os.environ, {"PATH": d, "HOME": d}):
            s.start("hi", "sys")
            for _ in range(100):
                app.processEvents()
                if got:
                    break
                time.sleep(0.01)
        self.assertEqual(got, [[]])
        self.assertIn("No se pudo arrancar claude", s.html)

    def test_store_roundtrip_corrupt_and_failure(self):
        with tempfile.TemporaryDirectory() as d:
            st = chat.ChatStore(Path(d) / "chats.json")
            self.assertEqual(st.load(), {})
            st.save({"34A": {"session": "s", "html": "<p>x</p>"}})
            self.assertEqual(st.load()["34A"]["session"], "s")
            st.path.write_text("{broken")
            self.assertEqual(st.load(), {})
            self.assertTrue((Path(d) / "chats.json.bad").exists())
            with mock.patch("os.replace", side_effect=OSError), self.assertRaises(OSError):
                st.save({"a": {}})
            self.assertEqual(os.listdir(d), ["chats.json.bad"])


class RecDev(FakeDev):
    log = []

    def read(self, slot):
        RecDev.log.append(slot)
        return self.raw

    def close(self):
        pass


@unittest.skipIf(m is None, "PyQt6 not installed")
class PedalQueue(unittest.TestCase):
    def test_high_jumps_ahead_of_scan(self):
        app = QCoreApplication.instance() or QCoreApplication([])
        RecDev.log = []
        p = m.Pedal(RecDev)
        p.hold_for_claude()  # blocks the worker so everything below queues up
        time.sleep(0.1)
        p.scan(range(10))
        p.read(50)
        p.release_claude()
        for _ in range(50):
            app.processEvents()
            time.sleep(0.02)
            if len(RecDev.log) == 11:
                break
        p.stop()
        self.assertEqual(RecDev.log[0], 50)
        self.assertEqual(RecDev.log[1:], list(range(10)))

    def test_hold_leaves_port_closed(self):  # the CLI needs the port while Claude runs
        app = QCoreApplication.instance() or QCoreApplication([])
        opened = []
        p = m.Pedal(lambda: opened.append(1) or RecDev())
        held = []
        p.held.connect(lambda: held.append(1))
        p.hold_for_claude()
        for _ in range(50):
            app.processEvents()
            time.sleep(0.01)
            if held:
                break
        p.release_claude()
        p.stop()
        self.assertEqual(held, [1])
        self.assertEqual(opened, [])


if m:
    class FakePedal(QObject):
        preset_read, saved, progress, failed, busy_changed = pyqtSignal(int, dict), pyqtSignal(int, list, str), pyqtSignal(str), pyqtSignal(str, str), pyqtSignal(object)

        def __init__(self):
            super().__init__()
            self.calls = []

        def read(self, slot, select=False):
            self.calls.append(("read", slot, select))
            self.preset_read.emit(slot, preset())

        def apply(self, msgs, key=None):
            self.calls.append(("apply", len(msgs)))

        def save(self, slot, p):
            self.calls.append(("save", slot))


@unittest.skipIf(m is None, "PyQt6 not installed")
class WorkbenchTests(unittest.TestCase):
    def setUp(self):
        QCoreApplication.instance() or QCoreApplication([])
        self.p = FakePedal()
        self.wb = m.Workbench(self.p)

    def test_open_edit_discard(self):
        self.wb.open(100)
        self.assertEqual(self.p.calls[0], ("read", 100, True))
        self.assertFalse(self.wb.dirty)
        self.wb.toggle("AMP")
        self.assertTrue(self.wb.dirty)
        self.assertEqual(self.p.calls[-1], ("apply", 1))
        self.wb.discard()
        self.assertFalse(self.wb.dirty)
        self.assertEqual(self.p.calls[-1], ("read", 100, True))
        self.assertEqual(self.wb.working, self.wb.stored)

    def test_factory_save_refused_and_save_as_limits(self):
        self.wb.open(11)
        self.wb.toggle("AMP")
        self.wb.save()
        self.assertFalse([c for c in self.p.calls if c[0] == "save"])
        self.wb.save_as(254)
        self.wb.save_as(50)
        self.assertFalse([c for c in self.p.calls if c[0] == "save"])
        self.wb.save_as(100)
        self.assertEqual(self.p.calls[-1], ("save", 100))

    def test_dirty_guard_and_rename(self):
        self.wb.open(100)
        self.wb.toggle("AMP")
        got = []
        self.wb.guard.connect(got.append)
        self.wb.request_open(101)
        self.assertEqual(got, ["34B"])
        self.assertEqual(self.wb.slot, 100)
        self.wb.confirm_switch()
        self.assertEqual(self.wb.slot, 101)
        self.assertFalse(self.wb.rename("é"))
        self.assertFalse(self.wb.rename("x" * 17))
        self.assertTrue(self.wb.rename("Fine"))
        self.assertTrue(self.wb.dirty)

"""Offline checks for the app's pure helpers. Run: python3 -m unittest discover tests"""
import json
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path

try:
    a = SourceFileLoader("gp200_app", str(Path(__file__).parent.parent / "app/gp200_app.py")).load_module()
except ImportError:  # PyQt6 missing
    a = None


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


if __name__ == "__main__":
    unittest.main()

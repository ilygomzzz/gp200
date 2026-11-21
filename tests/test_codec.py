"""Offline codec self-check (no device). Run: python3 -m unittest discover tests"""
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path

g = SourceFileLoader("gp200", str(Path(__file__).parent.parent / "bin/gp200")).load_module()


class Codec(unittest.TestCase):
    def test_nibble_roundtrip(self):
        data = bytes(range(256))
        self.assertEqual(g.unnib(g.nib(data)), data)

    def test_message_sizes_match_protocol(self):
        # sizes from docs/sysex-protocol.md (Preset Forge); all data bytes must be 7-bit
        for msg, size in [(g.msg_read(100), 46), (g.msg_select(100), 30), (g.msg_effect(3, 0x07000010), 54),
                          (g.msg_toggle(3, True), 46), (g.msg_param(3, 0, 0x07000010, 55.0), 62),
                          (g.msg_reorder(list(range(11)), 4, 4), 78), (g.msg_save(100, "Claude Crunch"), 62)]:
            self.assertEqual(len(msg), size)
            self.assertEqual((msg[0], msg[-1]), (0xF0, 0xF7))
            self.assertTrue(all(b < 0x80 for b in msg[1:-1]))

    def test_read_request_is_the_one_verified_on_hardware(self):
        self.assertEqual(g.msg_read(0).hex(" "), "f0 21 25 7e 47 50 2d 32 11 10 " + "00 " * 8 + "04 00 00 00 01 00 00 00 00 00 00 00 01 00 00 00 04 00 00 00 00 00 00 00 00 00 00 f7")

    def test_slot_labels(self):
        self.assertEqual([g.slot_label(s) for s in (0, 3, 4, 100)], ["1A", "1D", "2A", "26A"])
        self.assertEqual(g.parse_slot("26a"), 100)

    def test_decode_reads_chain_order_from_routing_bytes(self):
        raw = bytearray(1176)
        raw[106:108] = b"\x03\x06"
        raw[108:119] = bytes([0, 4, 1, 2, 8, 9, 3, 5, 6, 7, 10])  # captured from slot 26B on hardware
        for pos in range(11):
            raw[120 + pos * 72 + 4] = pos
        p = g.decode_preset(bytes(raw))
        self.assertEqual(p["order"], ["PRE", "NR", "WAH", "DST", "DLY", "RVB", "AMP", "CAB", "EQ", "MOD", "VOL"])
        self.assertEqual(p["fxloop"], [3, 6])
        self.assertTrue(any("order" in x for x in g.diff([], "", p, list(range(11)))))

    def test_build_rejects_bad_input(self):
        old = {"name": "x", "fxloop": [4, 4], "blocks": {b: {"effect": "#0x0", "on": False, "params": {}} for b in g.BLOCKS}}
        for bad in ({"name": "a" * 17}, {"blocks": {"AMP": {"effect": "Nope"}}}, {"blocks": {"AMP": {"effect": "UK 800", "params": {"Gain": 500}}}},
                    {"blocks": {"FOO": {}}}):
            with self.assertRaises(SystemExit):
                g.build(old, bad)


if __name__ == "__main__":
    unittest.main()

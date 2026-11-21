"""Offline codec self-check (no device). Run: python3 -m unittest discover tests"""
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path

g = SourceFileLoader("gp200", str(Path(__file__).parent.parent / "bin/gp200")).load_module()


class FakeDev:
    def __init__(self):
        raw = bytearray(1176)
        raw[28:32] = b"Test"
        raw[108:119] = bytes(range(11))
        for i in range(11):
            raw[120 + i * 72 + 4] = i
            eid = next(e for e, x in g.EFFECTS.items() if x["module"] == g.BLOCKS[i])
            raw[120 + i * 72 + 8:120 + i * 72 + 12] = g.struct.pack("<I", eid)
        self.raw, self.sent = bytes(raw), []

    def read(self, slot):
        return self.raw

    def send(self, msg, gap=0.0):
        self.sent.append(msg)

    def drain(self):
        pass


class Codec(unittest.TestCase):
    def test_write_preset_backs_up_then_selects_first_and_saves_last(self):
        dev, seen = FakeDev(), []
        with tempfile.TemporaryDirectory() as d:
            g.ROOT = Path(d)
            bak, probs, name = g.write_preset(dev, 100, {"name": "X"}, seen.append)
            self.assertEqual(g.json.loads(bak.read_text())["name"], "Test")
        self.assertEqual(dev.sent[0], g.msg_select(100))
        self.assertEqual(dev.sent[-1], g.msg_save(100, "X"))
        self.assertEqual((seen, name), (list(range(1, 12)), "X"))
        self.assertTrue(probs)  # fake readback still says "Test"

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
        self.assertEqual([g.slot_label(s) for s in (0, 2, 3, 98, 99, 254)], ["1A", "1C", "2A", "33C", "34A", "85C"])
        self.assertEqual(g.parse_slot("34b"), 100)

    def test_decode_reads_chain_order_from_routing_bytes(self):
        raw = bytearray(1176)
        raw[106:108] = b"\x03\x06"
        raw[108:119] = bytes([0, 4, 1, 2, 8, 9, 3, 5, 6, 7, 10])  # captured from slot 34C (index 101) on hardware
        for pos in range(11):
            raw[120 + pos * 72 + 4] = pos
        p = g.decode_preset(bytes(raw))
        self.assertEqual(p["order"], ["PRE", "NR", "WAH", "DST", "DLY", "RVB", "AMP", "CAB", "EQ", "MOD", "VOL"])
        self.assertEqual(p["fxloop"], [3, 6])
        self.assertTrue(any("order" in x for x in g.diff([], "", p, list(range(11)))))

    def test_snaptone_upload_framing(self):
        blob = bytearray(g.SNAP_BLOB)
        blob[:8] = b"VTSI" + g.SNAP_BLOB.to_bytes(4, "little")
        crc = g.crc16_modbus(blob[12:])
        blob[8:10] = bytes([crc >> 8, crc & 0xFF])
        self.assertIsNone(g.check_blob(bytes(blob)))
        self.assertEqual(g.crc16_modbus(b"123456789"), 0x4B37)
        fr = g.frames(g.snap_record(1, "1965WRM2", bytes(blob)))
        # same shape as VLTN's verified upload: 45 frames, LEN 0x201C, record 0x1013, last chunk 168 bytes
        self.assertEqual((len(fr), fr[0][9:13], fr[0][13:17]), (45, bytes([0x1C, 0x40, 0, 0]), bytes([1, 3, 1, 0])))
        self.assertEqual([len(f) for f in fr[:1] + fr[-1:]], [380, 350])
        blob[20] ^= 1
        self.assertEqual(g.check_blob(bytes(blob)), "CRC mismatch")

    def test_build_rejects_bad_input(self):
        old = {"name": "x", "fxloop": [4, 4], "blocks": {b: {"effect": "#0x0", "on": False, "params": {}} for b in g.BLOCKS}}
        for bad in ({"name": "a" * 17}, {"blocks": {"AMP": {"effect": "Nope"}}}, {"blocks": {"AMP": {"effect": "UK 800", "params": {"Gain": 500}}}},
                    {"blocks": {"FOO": {}}}):
            with self.assertRaises(SystemExit):
                g.build(old, bad)


if __name__ == "__main__":
    unittest.main()

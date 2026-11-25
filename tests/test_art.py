import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "app"))
from art import art_for, KINDS  # noqa: E402
import theme  # noqa: E402


class Art(unittest.TestCase):
    def test_rules(self):
        self.assertEqual(art_for("DST", "Green OD", "Ibanez® TS-808 Tube Screamer")["family"], "od_green")
        self.assertEqual(art_for("AMP", "UK 800", "Marshall® JCM800")["family"], "brit_gold")
        self.assertEqual(art_for("AMP", "Tweedy", "Fender® Tweed Deluxe")["family"], "tweed")
        self.assertEqual(art_for("AMP", "Dark DLX", "Fender® Deluxe Reverb")["family"], "blackface")
        self.assertEqual(art_for("CAB", "X", "Marshall® 4x12 cabinet"), {"kind": "cabinet", "family": "grille_wheat", "speakers": 4, "cone": 12})
        self.assertEqual(art_for("CAB", "X", "Supro® 1x6\" cabinet")["speakers"], 1)
        self.assertEqual(art_for("CAB", "X", "Supro® 1x6\" cabinet")["cone"], 6)
        self.assertEqual(art_for("PRE", "COMP", "Ross™ Compressor")["family"], "brushed")
        self.assertEqual(art_for("DST", "Muffy", "Big Muff style fuzz")["family"], "fuzz_violet")
        self.assertEqual(art_for("AMP", "Bellman 59N", ""), {"kind": "head", "family": "graphite", "speakers": 2, "cone": 12})
        self.assertEqual(art_for("VOL", "Volume", "")["kind"], "treadle")

    def test_every_effect_maps_to_a_family_with_tokens(self):
        try:
            import theme
        except ImportError:
            self.skipTest("PyQt6 not installed")
        fams = theme.chassis
        for e in json.load(open(ROOT / "data/effects.json")).values():
            a = art_for(e["module"], e["name"], e.get("desc", ""))
            self.assertIn(a["family"], fams, e["name"])
            self.assertEqual(a["kind"], KINDS[e["module"]])
            self.assertTrue({"body", "face", "ink", "knob"} <= set(fams[a["family"]]))
        self.assertIn("display", fams["rack_dark"])


def _lum(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [x / 12.92 if x <= .03928 else ((x + .055) / 1.055) ** 2.4 for x in c]
    return .2126 * c[0] + .7152 * c[1] + .0722 * c[2]


class InkContrast(unittest.TestCase):
    def test_amp_nameplate_ink_on_face(self):
        for f in ("brit_gold", "tweed", "blackface", "copper", "steel", "graphite"):
            c = theme.chassis[f]
            a, b = sorted((_lum(c["ink"]), _lum(c["face"])))
            self.assertGreaterEqual((b + .05) / (a + .05), 4.5, f)


if __name__ == "__main__":
    unittest.main()

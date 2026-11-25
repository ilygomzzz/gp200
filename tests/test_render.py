"""Pure helpers of the render pipeline (tools/render/palette.py, app/art.py manifest). Stdlib only."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "tools" / "render"))
import palette  # noqa: E402

GOOD = {"version": 1, "px_per_su": 1.5, "stage": [1600, 520], "plate": "plate.jpg",
        "units": {"AMP/x": {"img": "a.png", "rect": [0, 0, 1, 1], "hero": {"img": "h.png"}}}}


class Palette(unittest.TestCase):
    def test_theme_families_and_blocks(self):
        t = palette.read_theme()
        for fam in ("brit_gold", "blackface", "dist_orange", "grille_silver", "rack_dark", "treadle_black"):
            self.assertEqual(set(t["chassis"][fam]) >= {"body", "face", "ink", "knob"}, True, fam)
        self.assertEqual(len(t["block_colors"]), 11)
        self.assertEqual(t["chassis_base"], "#2a2f36")  # tuple assignment parsed
        self.assertNotIn("bg", t)  # non-literal skipped

    def test_revision_tokens(self):
        t = palette.read_theme()
        for k in ("wood_lo", "wood_hi", "floor_lo", "floor_hi", "rug_red", "rug_red_dk", "rug_black", "panel_cloth", "rubber", "cone"):
            self.assertRegex(t[k], r"^#[0-9a-f]{6}$", k)

    def test_no_loose_hex_in_render_scripts(self):
        import re
        for f in (ROOT / "tools" / "render").glob("*.py"):
            if f.name != "palette.py":
                self.assertEqual(re.findall(r'"#[0-9a-fA-F]{6}', f.read_text()), [], f.name)

    def test_hex_to_linear(self):
        self.assertAlmostEqual(palette.hex_to_linear("#808080")[0], 0.2158, places=3)
        self.assertEqual(palette.hex_to_linear("#ffffff"), (1.0, 1.0, 1.0))
        self.assertEqual(palette.hex_to_linear("#ff000000"), (0.0, 0.0, 0.0))


class Manifest(unittest.TestCase):
    def mk(self, **kw):
        m = {**GOOD, **kw}
        return m

    def test_valid(self):
        self.assertEqual(palette.validate_manifest(GOOD), [])

    def test_rejects_traversal_and_subdirs(self):
        self.assertTrue(palette.validate_manifest(self.mk(plate="../x.png")))
        self.assertTrue(palette.validate_manifest(self.mk(units={"a": {"img": "a/b.png"}})))

    def test_missing_keys_and_bad_rect(self):
        self.assertTrue(palette.validate_manifest({"version": 1}))
        self.assertTrue(palette.validate_manifest(self.mk(units={"a": {"rect": [0, "x", 1, 1]}})))

    def test_load_manifest(self):
        import json
        import art
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            self.assertEqual(art.load_manifest(d / "manifest.json"), {})  # missing
            (d / "manifest.json").write_text(json.dumps(GOOD))
            self.assertEqual(art.load_manifest(d / "manifest.json"), {})  # files absent
            for f in ("plate.jpg", "a.png", "h.png"):
                (d / f).write_bytes(b"x")
            self.assertEqual(art.load_manifest(d / "manifest.json")["version"], 1)

    def test_unit_key(self):
        import art
        self.assertEqual(art.unit_key("head", "blackface", 2, "AMP"), "AMP/blackface")
        self.assertEqual(art.unit_key("cabinet", "grille_silver", 4, "CAB"), "CAB/grille_silver/4")
        self.assertEqual(art.unit_key("rack", "rack_dark", 2, "DLY"), "rack/DLY")
        self.assertEqual(art.unit_key("stompbox", "dist_orange", 2, "DST"), "DST/dist_orange")


if __name__ == "__main__":
    unittest.main()


class Layout(unittest.TestCase):
    """committed manifest: zones + labels are pairwise disjoint, inside the stage; every key the app can ask for exists"""

    def setUp(self):
        import json
        self.m = json.loads((ROOT / "app" / "assets" / "render" / "manifest.json").read_text())

    def test_no_overlap_inside_stage(self):
        w, h = self.m["stage"]
        rects = {**{"zone " + k: v for k, v in self.m["zones"].items()}, **{"label " + k: v for k, v in self.m["labels"].items()}}
        for k, r in rects.items():
            self.assertTrue(r[0] >= 0 and r[1] >= 0 and r[0] + r[2] <= w and r[1] + r[3] <= h, k)
        ks = list(rects)
        for i, a in enumerate(ks):
            for b in ks[i + 1:]:
                ra, rb = rects[a], rects[b]
                hit = ra[0] < rb[0] + rb[2] and rb[0] < ra[0] + ra[2] and ra[1] < rb[1] + rb[3] and rb[1] < ra[1] + ra[3]
                self.assertFalse(hit, f"{a} x {b}")

    def test_unit_keys(self):
        import art
        for need in ("AMP/blackface", "CAB/grille_silver/2", "rack/DLY", "WAH/treadle_black", "NR/gate_grey", "EQ/eq_white"):
            self.assertIn(need, self.m["units"])
        self.assertEqual(palette.validate_manifest(self.m), [])

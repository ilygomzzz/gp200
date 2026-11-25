import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
try:
    import numpy as np
    import make_textures as mt
    from PyQt6.QtGui import QImage
except ImportError:
    mt = None


def load(p):
    img = QImage(str(p)).convertToFormat(QImage.Format.Format_RGBA8888)
    return np.frombuffer(img.constBits().asarray(img.sizeInBytes()), np.uint8).reshape(img.height(), img.width(), 4).astype(int)


@unittest.skipIf(mt is None, "numpy/PyQt6 missing")
class Textures(unittest.TestCase):
    def test_deterministic_small_and_seamless(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            mt.write(a); mt.write(b)
            total = 0
            for n in mt.TILING + mt.SPRITES:
                fa, fb = Path(a, n + ".png"), Path(b, n + ".png")
                self.assertEqual(hashlib.sha256(fa.read_bytes()).hexdigest(), hashlib.sha256(fb.read_bytes()).hexdigest(), n)
                total += fa.stat().st_size
                im = load(fa)
                if n in ("tread", "grille_weave"):  # regular patterns: period (8 / 4) divides the tile size
                    self.assertEqual(im.shape[0] % (8 if n == "tread" else 4), 0)
                elif n in mt.TILING:  # wrap check: neighbours across the seam differ no more than inside the tile
                    v = (im[..., 3] * np.where(im[..., 0] > 127, 1, -1)).astype(float)
                    inner = max(np.abs(np.diff(v, axis=1)).mean(), np.abs(np.diff(v, axis=0)).mean())
                    seam = max(np.abs(v[:, 0] - v[:, -1]).mean(), np.abs(v[0] - v[-1]).mean())
                    self.assertLessEqual(seam, inner * 2 + 1, n)
                else:
                    self.assertEqual(im[0, :, 3].max() + im[-1, :, 3].max() + im[:, 0, 3].max() + im[:, -1, 3].max(), 0, n)
            self.assertLess(total, 200_000)

    def test_committed_files_match_generator(self):
        with tempfile.TemporaryDirectory() as a:
            mt.write(a)
            for n in mt.TILING + mt.SPRITES:
                self.assertEqual(Path(a, n + ".png").read_bytes(), (ROOT / "app/assets/textures" / (n + ".png")).read_bytes(), n)


if __name__ == "__main__":
    unittest.main()

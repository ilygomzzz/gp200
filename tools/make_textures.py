#!/usr/bin/env python3
"""Generate the colourless material tiles + shadow/spotlight sprites of the rig scene (spec 004, task 2.0).

numpy only, fixed seed, written with QImage (PyQt6). Encoding = signed alpha: RGB white where v > 0.5, black where
v < 0.5, alpha = |v - 0.5| * 2 * 255 (quantised to 16 levels to keep the PNGs small), so one tile lights AND shades
whatever token colour is under it. Tiling files are periodic by construction (FFT blur on the torus).
Usage: tools/make_textures.py [outdir]   (default app/assets/textures)
"""
import sys
from pathlib import Path

import numpy as np

TILING = ("tolex", "powder", "brushed", "grille_weave", "tread", "stage_mat")
SPRITES = ("shadow_contact", "spot")


def blur(a, sx, sy=None):
    """Periodic gaussian blur (frequency domain)."""
    sy = sx if sy is None else sy
    fy, fx = np.meshgrid(np.fft.fftfreq(a.shape[0]), np.fft.fftfreq(a.shape[1]), indexing="ij")
    k = np.exp(-2 * np.pi ** 2 * ((fx * sx) ** 2 + (fy * sy) ** 2))
    return np.real(np.fft.ifft2(np.fft.fft2(a) * k))


def norm(a):
    return (a - a.mean()) / (a.std() + 1e-9)


def make(name):
    rng = np.random.default_rng({"tolex": 1, "powder": 2, "brushed": 3, "grille_weave": 4, "tread": 5, "stage_mat": 6}.get(name, 7))
    if name == "tolex":
        n = rng.standard_normal((128, 128))
        return 0.5 + 0.45 * np.tanh(norm(blur(n, 0.55)) * 0.8)  # fine pebbled grain
    if name == "powder":
        return 0.5 + 0.35 * np.tanh(norm(blur(rng.standard_normal((128, 128)), 0.6)) * 0.5)
    if name == "brushed":
        rows = rng.standard_normal((32, 256))
        k = np.zeros(256); k[:96] = 1 / 96  # horizontal periodic box blur
        rows = np.real(np.fft.ifft(np.fft.fft(rows, axis=1) * np.fft.fft(k), axis=1))
        v = 0.5 + 0.4 * np.tanh(norm(rows) * 0.6)
        return np.clip(v + 0.05 * rng.standard_normal(v.shape), 0, 1)
    if name == "grille_weave":
        y, x = np.mgrid[0:64, 0:64]
        along_x = np.sin(2 * np.pi * x / 4)  # over/under threads: even 2-px bands one way, odd the other
        along_y = np.sin(2 * np.pi * y / 4)
        v = np.where((y // 2) % 2 == 0, along_x, along_y) * 0.35 * (1 + 0.2 * norm(blur(rng.standard_normal((64, 64)), 6)))
        return 0.5 + v
    if name == "tread":
        y = np.arange(32)[:, None] % 8
        return np.broadcast_to(np.select([y < 2, y < 4], [0.85, 0.2], 0.5), (32, 32)).copy()
    if name == "stage_mat":
        y, x = np.mgrid[0:256, 0:256]
        dx, dy = (x % 8) - 3.5, (y % 8) - 3.5
        r = np.hypot(dx, dy)
        bump = np.where(r < 2.5, 0.5 + 0.35 * np.clip((-dx - dy) / 3.5, -1, 1), 0.5)  # light from top-left
        return np.clip(bump + 0.15 * norm(blur(rng.standard_normal((256, 256)), 32)) * 0.5, 0, 1)
    raise KeyError(name)


def sprite(name):
    """Returns (rgba) directly: black shadow / white spot, alpha = profile."""
    if name == "shadow_contact":
        h, w = 64, 256
        y, x = np.mgrid[0:h, 0:w]
        a = 0.9 * np.exp(-(((x - w / 2) / (0.32 * w)) ** 2 + ((y - h / 2) / (0.28 * h)) ** 2) / 2)
        a *= (np.hypot((x - w / 2) / (w / 2 - 1), (y - h / 2) / (h / 2 - 1)) < 1)  # exactly 0 at the border
        rgb = 0
    else:
        h = w = 512
        y, x = np.mgrid[0:h, 0:w]
        r = np.hypot((x - w / 2) / (w / 2 - 1), (y - h / 2) / (h / 2 - 1))
        a = np.clip(1 - r, 0, 1) ** 2
        rgb = 255
    out = np.zeros((h, w, 4), np.uint8)
    out[..., :3] = rgb
    out[..., 3] = np.round(a * 255)
    return out


def rgba(name):
    if name in SPRITES:
        return sprite(name)
    v = make(name)
    out = np.zeros(v.shape + (4,), np.uint8)
    out[..., :3] = np.where(v > 0.5, 255, 0)[..., None]
    out[..., 3] = np.clip(np.round(np.abs(v - 0.5) * 2 * 255 / 16) * 16, 0, 255)
    return out


def write(outdir):
    from PyQt6.QtGui import QImage
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    for name in TILING + SPRITES:
        a = np.ascontiguousarray(rgba(name))
        img = QImage(a.data, a.shape[1], a.shape[0], a.shape[1] * 4, QImage.Format.Format_RGBA8888).copy()
        assert img.save(str(outdir / f"{name}.png")), name


if __name__ == "__main__":
    write(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "app/assets/textures")

"""Palette for the Blender scripts (stdlib only, no bpy, no PyQt): reads app/theme.py with `ast` (Blender's Python has no
PyQt6) and converts hex to linear RGB. Manifest validation is shared with the app (app/art.py)."""
import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "app"))
from art import manifest_errors as validate_manifest  # noqa: E402,F401


def _lit(n):
    if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "dict":
        return {k.arg: _lit(k.value) for k in n.keywords}
    if isinstance(n, ast.Dict):
        return {_lit(k): _lit(v) for k, v in zip(n.keys, n.values)}
    return ast.literal_eval(n)


def read_theme(path=None):
    """Module-level literal assignments of theme.py (incl. tuple targets); non-literal values are skipped."""
    out = {}
    for node in ast.parse((Path(path) if path else ROOT / "app" / "theme.py").read_text()).body:
        if not isinstance(node, ast.Assign):
            continue
        for t in node.targets:
            names = t.elts if isinstance(t, ast.Tuple) else [t]
            vals = node.value.elts if isinstance(t, ast.Tuple) and isinstance(node.value, ast.Tuple) else [node.value]
            for nm, v in zip(names, vals):
                try:
                    out[nm.id] = _lit(v)
                except (ValueError, AttributeError, TypeError):
                    pass
    return out


def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hex_to_linear(h):
    """'#rrggbb' (or '#aarrggbb', alpha dropped) -> (r, g, b) linear floats."""
    h = h.lstrip("#")[-6:]
    return tuple(srgb_to_linear(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4))


def mix_hex(a, b, t):
    """blend two '#rrggbb' in linear space -> '#rrggbb' (for derived material colours)"""
    lin = [x * (1 - t) + y * t for x, y in zip(hex_to_linear(a), hex_to_linear(b))]
    enc = [12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055 for v in lin]
    return "#" + "".join(f"{round(max(0, min(1, x)) * 255):02x}" for x in enc)

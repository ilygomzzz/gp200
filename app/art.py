"""Gear art mapping (spec 004, task 2.1): pure, no Qt. `art_for(block, name, desc)` -> {kind, family, speakers}.
Keyword match on name + desc, case-insensitive, first rule wins; unmatched -> the block's default family.
Families name colour sets in `theme.chassis`; drawings are original (no brand art)."""
import re

KINDS = {"PRE": "stompbox", "WAH": "treadle", "DST": "stompbox", "AMP": "head", "NR": "mini", "CAB": "cabinet", "EQ": "eq",
         "MOD": "rack", "DLY": "rack", "RVB": "rack", "VOL": "treadle"}
DEFAULT = {"PRE": "cream", "WAH": "treadle_black", "DST": "dist_orange", "AMP": "graphite", "NR": "gate_grey", "CAB": "grille_black",
           "EQ": "eq_white", "MOD": "rack_dark", "DLY": "rack_dark", "RVB": "rack_dark", "VOL": "treadle_black"}
_BRIT = r"marshall|jcm|plexi|british|\buk\b"
_FENDERISH = r"fender|twin|deluxe|vibro|blackface|silverface|princeton|champ"
RULES = {
    "PRE": [(r"comp", "brushed")],
    "DST": [(r"screamer|\bts-?\d|\bod\b|overdrive|blues", "od_green"), (r"fuzz|muff", "fuzz_violet"),
            (r"metal|high.?gain", "metal_black"), (r"distortion|\brat\b|\bds-?\d", "dist_orange")],
    "AMP": [(_BRIT, "brit_gold"), (r"tweed", "tweed"), (_FENDERISH, "blackface"), (r"vox|\bac-?\d+|ac30", "copper"),
            (r"mesa|boogie|rectifier|5150|peavey|bogner|engl|diezel|evh", "steel")],
    "CAB": [(_BRIT, "grille_wheat"), (_FENDERISH + r"|tweed", "grille_silver")],
}


def art_for(block, name="", desc=""):
    text = f"{name} {desc}".lower()
    family = DEFAULT.get(block, "graphite")
    for pat, fam in RULES.get(block, []):
        if re.search(pat, text):
            family = fam
            break
    m = re.search(r"(\d)\s*x\s*(\d+)", desc or "")
    sp = int(m.group(1)) if m else 2
    return {"kind": KINDS.get(block, "stompbox"), "family": family, "speakers": sp if sp in (1, 2, 4) else (2 if sp == 3 else 4),
            "cone": int(m.group(2)) if m else 12}


def unit_key(kind, family, speakers, block):
    """Manifest key of a unit sprite: `AMP/blackface`, `CAB/grille_silver/2`, `rack/DLY`."""
    if kind == "rack":
        return f"rack/{block}"
    return f"{block}/{family}/{speakers}" if kind == "cabinet" else f"{block}/{family}"


_IMG = re.compile(r"\.(png|jpe?g)$", re.I)
_NEED = ("version", "px_per_su", "stage", "plate", "units")


def manifest_errors(m, base=None):
    """Problems in a render manifest dict (empty list = valid): required keys, version, every image name bare
    (no separator, no `..`), rects numeric, files present when `base` (a Path) is given."""
    if not isinstance(m, dict):
        return ["manifest is not an object"]
    errs = [f"missing key {k}" for k in _NEED if k not in m]
    if m.get("version") != 1:
        errs.append("unsupported version")

    def walk(v, key=""):
        if isinstance(v, dict):
            for k, x in v.items():
                walk(x, k)
        elif isinstance(v, (list, tuple)):
            if key in ("rect", "img_rect", "name", "display") and not all(isinstance(x, (int, float)) for x in v):
                errs.append(f"{key} not numeric")
            for x in v:
                walk(x, key)
        elif isinstance(v, str) and _IMG.search(v):
            if "/" in v or "\\" in v or ".." in v or not v:
                errs.append(f"bad file name {v!r}")
            elif base is not None and not (base / v).is_file():
                errs.append(f"file not found {v}")
    walk(m)
    return errs


def load_manifest(path):
    """Read `<dir>/manifest.json`; {} (and a stderr reason) when missing or invalid."""
    import json
    import sys
    from pathlib import Path
    path = Path(path)
    try:
        m = json.loads(path.read_text())
    except (OSError, ValueError) as e:
        print(f"render manifest unavailable: {e}", file=sys.stderr)
        return {}
    errs = manifest_errors(m, path.parent)
    if errs:
        print("render manifest rejected: " + "; ".join(errs[:5]), file=sys.stderr)
        return {}
    return m


def _hits(pts, rects, own):
    """True when a polyline point lies inside a (shrunk) rect that is not one of the endpoints' own units"""
    for r in rects:
        if r in own:
            continue
        x0, y0, x1, y1 = r[0] + 2, r[1] + 2, r[0] + r[2] - 2, r[1] + r[3] - 2
        if any(x0 < x < x1 and y0 < y < y1 for x, y in pts):
            return True
    return False


def _spline(ctrl, n=10):
    """Catmull-Rom through `ctrl`, `n` samples per span (natural curve, passes through every control point)"""
    p = [ctrl[0]] + list(ctrl) + [ctrl[-1]]
    out = [ctrl[0]]
    for i in range(1, len(p) - 2):
        a, b, c, d = p[i - 1], p[i], p[i + 1], p[i + 2]
        for k in range(1, n + 1):
            t = k / n
            out.append(tuple(0.5 * (2 * b[j] + (-a[j] + c[j]) * t + (2 * a[j] - 5 * b[j] + 4 * c[j] - d[j]) * t * t + (-a[j] + 3 * b[j] - 3 * c[j] + d[j]) * t ** 3) for j in (0, 1)))
    return out


def cable_path(p0, p1, rects, lane=0, floor=(496, 508)):
    """Stage-unit polyline of a patch cable p0 -> p1 (spec 004 2C.13). A short hop between neighbours is one slack curve; otherwise the cable
    leaves the jack, drops through the nearest free column to a lane on the rug in front of the board, runs along it and rises to the other
    jack. `rects` = [x, y, w, h] of every unit; the rects holding an endpoint are ignored. Pure + deterministic."""
    own = [r for r in rects for p in (p0, p1) if r[0] - 8 <= p[0] <= r[0] + r[2] + 8 and r[1] - 8 <= p[1] <= r[1] + r[3] + 8]
    dx = p1[0] - p0[0]
    sag = min(26.0, 6 + 0.12 * abs(dx))
    direct = [p0, ((p0[0] + p1[0]) / 2, max(p0[1], p1[1]) + sag), p1]
    line = _spline(direct)
    if not _hits(line, rects, own):
        return line
    if lane < 0:  # lane -1 = no rug routing: a blocked cable is dropped
        return []
    ly = min(floor[1], max(p0[1], p1[1], floor[0] - 14) + 14) + 8 * lane

    def column(p):
        for k in range(0, 40):
            for x in ((p[0],) if k == 0 else (p[0] - 4 * k, p[0] + 4 * k)):
                if not _hits([(x, y) for y in range(int(p[1]) + 14, int(ly))], rects, own):
                    return x
        return p[0]
    xa, xb = column(p0), column(p1)
    ctrl = [p0, (xa, p0[1] + 12), (xa, ly - 10), ((xa + xb) / 2, ly + 5), (xb, ly - 10), (xb, p1[1] + 12), p1]
    return _spline(ctrl)

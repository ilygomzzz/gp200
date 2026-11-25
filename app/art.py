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

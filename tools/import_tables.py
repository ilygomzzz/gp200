#!/usr/bin/env python3
"""Regenerate data/effects.json from Preset Forge's TS tables (parsed as text, never executed).

Usage: python3 -I tools/import_tables.py <gp200editor-checkout> > data/effects.json
Source: https://github.com/phash/gp200editor (GPL-3.0), extracted from Valeton's algorithm.xml.
"""
import json, re, sys
from pathlib import Path

core = Path(sys.argv[1]) / "src/core"
names = core.joinpath("effectNames.ts").read_text()
params = core.joinpath("effectParams.ts").read_text()

out = {}
for eid, name, module in re.findall(r"^\s*(\d+):\s*\{\s*name:\s*'((?:[^'\\]|\\.)*)',\s*module:\s*'(\w+)'", names, re.M):
    out[eid] = {"name": name.replace("\\'", "'"), "module": module, "params": []}

# EFFECT_PARAMS: "  <id>: [" followed by one param object per line until "  ],"
body = params.split("EFFECT_PARAMS", 1)[1]
for eid, block in re.findall(r"^\s*(\d+):\s*\[(.*?)^\s*\],", body, re.M | re.S):
    plist = []
    for line in block.splitlines():
        m = re.search(r"type:\s*'(\w+)',\s*name:\s*'((?:[^'\\]|\\.)*)',\s*idx:\s*(\d+),\s*default:\s*(-?[\d.]+)", line)
        if not m:
            continue
        p = {"type": m[1], "name": m[2].replace("\\'", "'"), "idx": int(m[3]), "default": float(m[4])}
        if m[1] == "knob":
            r = re.search(r"min:\s*(-?[\d.]+),\s*max:\s*(-?[\d.]+),\s*step:\s*([\d.]+)", line)
            p.update(min=float(r[1]), max=float(r[2]), step=float(r[3]))
        else:
            p["options"] = [{"name": n, "id": int(i)} for n, i in re.findall(r"name:\s*'((?:[^'\\]|\\.)*)',\s*id:\s*(\d+)", line.split("options", 1)[1])]
        plist.append(p)
    if eid in out:
        out[eid]["params"] = plist

desc = dict(re.findall(r"^\s*'((?:[^'\\]|\\.)*)':\s*'((?:[^'\\]|\\.)*)',", core.joinpath("effectDescriptions.ts").read_text(), re.M))
for v in out.values():
    if v["name"] in desc:
        v["desc"] = desc[v["name"]].replace("\\'", "'")

assert len(out) > 250 and sum(1 for v in out.values() if v["params"]) > 250, "parse failed"
json.dump(out, sys.stdout, indent=0, ensure_ascii=False)

# gp200 — Valeton GP-200JR preset tool (Linux)

Goal: the user says "I want sound X" → Claude asks which slot → designs the preset → writes it to the pedal → verifies. The `gp200` skill (`.claude/skills/gp200/SKILL.md`, symlinked to `~/.claude/skills/gp200`) holds that workflow; this file holds the facts.

User-facing replies in Spanish; code, docs, commits in English.

## Layout
- `bin/gp200` — single-file Python CLI, stdlib only. Talks raw SysEx to `/dev/snd/midiC<N>D0` (card found by `GP200*` in `/proc/asound/cards`; user is in `audio` group, no sudo, no mido). Symlinked as `~/.local/bin/gp200`.
- `data/effects.json` — 305 effects: `{id: {name, module, desc, params:[{type knob|switch|combox, name, idx, default, min/max | options}]}}`. Regenerate with `tools/import_tables.py` (parses Preset Forge TS as text — never execute that repo's code).
- `presets/` — preset JSONs Claude authored (keep them: they are the "source" of what is on the pedal).
- `backups/` — automatic dump of a slot before every `write` (`<timestamp>-<slot>.json`); restorable with `gp200 write <slot> backups/<file>`.
- `tests/test_codec.py` — offline codec check: `python3 -m unittest discover tests`.

## CLI
```
gp200 info                      # identity check
gp200 list 1A-26D               # slot names (~60 ms/slot)
gp200 show 26A [--json]         # human view / full JSON (same format write accepts)
gp200 effects [MODULE] [-q text] [-p]   # catalog; -q searches name + real-gear desc; -p lists params
gp200 write 26A preset.json [-n]        # -n = dry run; otherwise backup → push (~11 s) → readback verify
gp200 select 26A                # switch the pedal to that slot
```

## Preset JSON
```json
{"name": "<=16 ASCII chars",
 "blocks": {
   "AMP": {"effect": "UK 800", "params": {"Gain": 55, "Bass": 45}},
   "DLY": {"effect": "Analog Delay", "on": false}
 },
 "order": ["PRE","WAH","DST","AMP","NR","CAB","EQ","MOD","DLY","RVB","VOL"]}
```
- Blocks (fixed): PRE WAH DST AMP NR CAB EQ MOD DLY RVB VOL. An effect must belong to its block's module (`gp200 effects <BLOCK>`).
- Listed block → ON (unless `"on": false`). Unlisted block → keeps its current effect, turned OFF.
- Params: by catalog name (case-insensitive); unspecified ones = effect default (new effect) or current value (same effect). Switch/combox accept option name or id. Ranges are validated before anything is sent.
- `order` optional (signal chain order); default keeps the slot's current order. `"#n"` keys = raw param index (only for effects missing from the catalog).

## GP-200JR facts (verified 2026-11-21 on hardware)
- Protocol = GP-200's (header `F0 21 25 7E "GP-2"`), docs: https://github.com/phash/gp200editor `docs/sysex-protocol.md`.
- Identity reply byte[22..26] = `1 … 4` (doc says always 1.2; harmless).
- Read reply chunk byte[10] is constant `0x09`, NOT the slot (doc is wrong for JR) — read() just drains before asking.
- Slots 1A–25C factory presets; 25D–64C empty (named "It's GP-200JR"); 64D does not answer reads; 64C name reads oddly ("Jt's") — avoid both.
- Chain order is stored in decoded slot bytes [108:119] (block indices in playback order); [106:108] = FX loop send/return; [104] = slot number. Block records at 120+72·i stay in fixed PRE..VOL order. Reorder (sub=0x20) + fxloop verified writing slot 26B.
- Write = select slot → per block effect-change, 400 ms settle, params (40 ms apart, param 0 resent last), toggle → second param pass → reorder → save-commit. Fewer delays = dropped params (Preset Forge issue #80).
- SnapTone effects (AMP/DST ids 0x0F00000x) are captured profiles: params editable, but we can't create new captures.

## License
Effect tables and protocol knowledge come from Preset Forge (GPL-3.0); this repo is GPL-3.0 too.

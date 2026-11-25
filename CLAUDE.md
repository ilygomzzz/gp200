# gp200 — Valeton GP-200JR preset tool (Linux)

Goal: the user says "I want sound X" → Claude asks which slot → designs the preset → writes it to the pedal → verifies. The `gp200` skill (`.claude/skills/gp200/SKILL.md`, symlinked to `~/.claude/skills/gp200`) holds that workflow; this file holds the facts.

User-facing replies in Spanish; code, docs, commits in English.

## Layout
- `bin/gp200` — single-file Python CLI, stdlib only. Talks raw SysEx to `/dev/snd/midiC<N>D0` (card found by `GP200*` in `/proc/asound/cards`; user is in `audio` group, no sudo, no mido). Symlinked as `~/.local/bin/gp200`.
- `data/effects.json` — 305 effects: `{id: {name, module, desc, params:[{type knob|switch|combox, name, idx, default, min/max | options}]}}`. Regenerate with `tools/import_tables.py` (parses Preset Forge TS as text — never execute that repo's code).
- `presets/` — preset JSONs Claude authored (keep them: they are the "source" of what is on the pedal).
- `backups/` — automatic dump of a slot before every `write` (`<timestamp>-<slot>.json`); restorable with `gp200 write <slot> backups/<file>`.
- `tests/test_codec.py` — offline codec check: `python3 -m unittest discover tests`.
- `app/` — PyQt6 desktop app (spec 002 workbench): `gp200_app.py` (`Shell` wiring + engine + main; Qt Quick, spec 004), `theme.py` (tokens), `model.py` (`Pedal` = only MIDI owner, worker + priority queue; `Workbench` = edit buffer of one slot; pure `edit_msgs`/`move_block`/`effects_for`/`free_slots`/`clean`), `chat.py` (`parse_event`, `system_prompt`, `ChatStore` → `~/.local/share/gp200/chats.json`, `ChatSession`, `ChatHub`), `bridge.py` (QML view-models `Board`, `ChatView` + pure `unit_view`/`chain_view`), `qml/` (whole UI: pedalboard, close-up, knobs, slot grid, chat; one component per file; tokens via context property `T` from `theme.qml_tokens()`); spec 003 glass theme: own fixed palette in `theme.py`, translucent window (Hyprland blur, opaque off Hyprland or `GP200_GLASS=0`), per-block colours/glyphs, knobs, bank-grid slot browser. Launcher `bin/gp200-app` (symlinked in `~/.local/bin`, menu entry `~/.local/share/applications/gp200.desktop`). Loads `bin/gp200` as a module. Tests: `tests/test_app.py` (tokens + QML offscreen smoke), `tests/test_model.py`, `tests/test_bridge.py`.
- `tools/render/` + `app/assets/render/` — spec 004 phase 2C: rig art is rendered with Blender (dev tool only, not a runtime dependency; `blender -b -P tools/render/rig.py -- slice|plate|all`, procedural shader nodes, no downloaded assets); renders + `manifest.json` are committed; `tools/render/palette.py` (stdlib) reads `app/theme.py` by `ast`; QML loads them via `art.load_manifest` → context property `R`.
- `specs/NNN-name/` — **app flow = multi-agent SDD** (skill `gp200-app-sdd`, agents `gp200-designer` → user OK → `gp200-implementer` → `gp200-reviewer`, all in `.claude/`, symlinked into `~/.claude/`). Rules every spec obeys: `constitution.md`. Roadmap: 001 shell (done), 002 preset workbench with per-slot chat + live editing (done), 003 glass UI (done), 004 pedalboard (Qt Quick view: stompboxes, gear art, meter/tuner; phases 1–2 done: rig scene with generated textures in `app/assets/textures` via `tools/make_textures.py`), 005 tabs→preset (GP files from Ultimate Guitar, alphaTab view, scratch slot 85C/85B, patch tempo), 006 guitar trainer (pitch detection, reuses 004's `app/audio.py`); SnapTone screen (pick NAM file → convert → upload) as a later spec.

## CLI
```
gp200 info                      # identity check
gp200 list 1A-33C               # slot names (~60 ms/slot)
gp200 show 34B [--json]         # human view / full JSON (same format write accepts)
gp200 effects [MODULE] [-q text] [-p]   # catalog; -q searches name + real-gear desc; -p lists params
gp200 write 34B preset.json [-n]        # -n = dry run; otherwise backup → push (~11 s) → readback verify
gp200 select 34B                # switch the pedal to that slot
gp200 snaptone [N [vltn|f.vtsi]] [--name X] [--force] [-n]   # list / upload SnapTones (1-5 AMP, 6-10 DST)
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
- **3 presets per bank (A/B/C), 85 banks = indices 0–254** (labels in older notes used 4 per bank — wrong). 1A–33C factory presets (99); 34A–85B empty (named "It's GP-200JR"); 85C (index 254) name reads oddly ("Jt's") — avoid; index 255 does not answer.
- Chain order is stored in decoded slot bytes [108:119] (block indices in playback order); [106:108] = FX loop send/return; [104] = slot number. Block records at 120+72·i stay in fixed PRE..VOL order. Reorder (sub=0x20) + fxloop verified writing slot 34C.
- Delay `Time` is overwritten on save by the patch tempo (default 120 BPM = 500 ms); `gp200` cannot set tempo yet (VLTN: patch setting TEMPO=1, record PATCH_SETTING) → use Time 500 or add tempo support.
- Write = select slot → per block effect-change, 400 ms settle, params (40 ms apart, param 0 resent last), toggle → second param pass → reorder → save-commit. Fewer delays = dropped params (Preset Forge issue #80).
- SnapTones: 10 slots (0-4 AMP, 5-9 DST; effect id 0x0F000000+n, preset JSON `"SnapTone N"`). Upload = record 0x1013 {slot, 0, u32 byte-sum of field, name[16], 0x1288-byte VTSI blob zero-padded to 0x2000} in 45 frames of ≤183 bytes; pedal answers record 0x1014 {slot, status 1=ok}. **JR needs ≥50 ms between frames** (VLTN's 10 ms → dropped frames, no result). Name query = record 0x1012 (flag 0 = holds data). SnapTones can't be read back → `snaptone` refuses non-empty slots without `--force`.
- NAM→VTSI conversion (render Valeton's 70 s `nam_input_wav.wav` through the model + fit) is done by VLTN Tone Studio (github.com/grzmol/VLTN-Tone-Studio, GPL-3, AppImage in `~/Applications`, in the app menu). It can't export blobs, but its `~/.config/VLTN Tone Studio/logs/session.log` logs every frame: `gp200 snaptone N` rebuilds the last upload from it (byte-identical frames verified). Test signal extracted from Valeton Suite 1.0.9's NSIS installer → `~/.local/share/gp200/nam_input_wav.wav`. VLTN misreads JR firmware 1.8.0 as 1.6.0.

## Live edit facts (verified on 35A, 2026-11-21)
- `Device.read(slot)` always returns the **stored** slot, never the edit buffer: live edits (`msg_effect/param/toggle/reorder` after `msg_select`) leave `gp200 show` unchanged until `msg_save`. Edit-buffer contents can't be read back (so audible effect is only checkable by ear).
- The "first param swallowed after an effect change" and "re-select discards the buffer" cannot be observed over MIDI; the app resends the first param (as `push` does) and uses select + reread for Descartar.
- Factory presets can keep another module's effect id in an off block (12A DST = "Super OD", a PRE effect) and out-of-range Delay Time (4.0): `model.clean` swaps/clamps them before `write`; Delay Time is excluded from the readback diff (tempo overwrites it).

## License
Effect tables and protocol knowledge come from Preset Forge (GPL-3.0); this repo is GPL-3.0 too.

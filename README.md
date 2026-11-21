# gp200

Read, create and write presets on a **Valeton GP-200 / GP-200JR** from Linux over USB MIDI — no Windows editor, no drivers, Python stdlib only.

```
gp200 list 1A-33C                 # slot names
gp200 show 34B                    # chain of a slot (--json for the full preset)
gp200 effects AMP -q marshall -p  # 305-effect catalog with real-gear names and params
gp200 write 34B preset.json       # backup → write → verify by readback (-n = dry run)
gp200 select 34B                  # switch the pedal to a slot
gp200 snaptone 3                  # upload a NAM capture converted in VLTN Tone Studio as SnapTone 3
```

Presets are small JSON files (see `CLAUDE.md` for the format), e.g.

```json
{"name": "Crunch",
 "blocks": {"DST": {"effect": "Green OD", "params": {"Gain": 20}},
            "AMP": {"effect": "UK 800", "params": {"Gain": 55, "Middle": 65}},
            "CAB": {"effect": "UK GRN 2"}, "VOL": {"effect": "Volume"}}}
```

`gp200-app` opens a desktop app (PyQt6) with the preset list and a chat with Claude.

It also ships a [Claude Code](https://claude.com/claude-code) skill (`.claude/skills/gp200`): ask "quiero un sonido tipo X", it asks for a slot, designs the chain and writes it.

Tested on a GP-200JR (USB `84ef:0180`). Setup: user in the `audio` group, `ln -s $PWD/bin/gp200 ~/.local/bin/`.

## Credits & license
The SysEx protocol and effect tables come from the reverse-engineering work in [phash/gp200editor (Preset Forge)](https://github.com/phash/gp200editor), GPL-3.0, and SnapTone upload from [grzmol/VLTN-Tone-Studio](https://github.com/grzmol/VLTN-Tone-Studio), GPL-3.0. This project is GPL-3.0 too.

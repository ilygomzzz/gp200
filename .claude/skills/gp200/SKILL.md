---
name: gp200
description: Create, tweak, back up or restore presets on the user's Valeton GP-200JR guitar multi-effects pedal (USB, Linux) with the `gp200` CLI. Use whenever the user asks for a guitar/bass sound or tone ("quiero un sonido tipo…", "hazme un preset de…", "un crunch como AC/DC", "más ganancia en el 34B"), mentions the GP-200/pedalera/presets/slots, or wants to see what is on the pedal — from any folder.
---
Project: `~/projects/gp200` — read its `CLAUDE.md` first for the CLI, preset JSON format and device quirks. CLI: `gp200` (also `~/projects/gp200/bin/gp200`). Reply to the user in Spanish.

## "Quiero sonido X" flow
1. **Ask the slot** (AskUserQuestion), unless they already said it. Offer free slots first: `gp200 list 34A-36C` and suggest ones named "It's GP-200JR" (empty). If they pick a slot that holds a real preset, say what's there (name) and confirm overwrite — a backup is made anyway. Never use 85C (last slot, reads oddly).
2. **Design the chain** like a guitar tech: identify the reference (artist, song, genre, era, gear they used) and map it to real-gear models with `gp200 effects <BLOCK> -q <brand or term>` (descriptions name the real amp/pedal, e.g. `-q marshall`, `-q fender`, `-q "tube screamer"`). Check params with `-p`. Typical chain: [PRE comp/boost] → [DST drive] → AMP → NR gate (for gain) → CAB matching the amp → [EQ] → [MOD] → [DLY] → [RVB] → VOL.
   - Set every param that matters for the sound (gain, EQ, mix, time…), not just the effect. Keep delay/reverb mix modest unless asked (≈10–25). Gate on for high gain. Name ≤16 ASCII chars.
3. **Write** the JSON to `~/projects/gp200/presets/<kebab-name>.json`, run `gp200 write <slot> <file> -n` (dry run) and show the user that summary briefly, then `gp200 write <slot> <file>` (takes ~11 s; it backs up, writes, and verifies by readback). Then `gp200 select <slot>` so they can play it.
4. **Report** in 3–5 lines: slot, name, the chain in one line, and 1–2 knobs worth tweaking. Offer adjustments ("más brillo", "menos delay") — for those, edit the same preset JSON and rewrite the same slot.

## Other requests
- "Qué hay en X" → `gp200 show X`. "Lista" → `gp200 list 1A-33C`.
- Restore / undo → `ls ~/projects/gp200/backups/` and `gp200 write <slot> <backup.json>`.
- Copy a slot → `gp200 show A --json > presets/x.json`, then write it to B.
- NAM capture / TONE3000 tone / "SnapTone" → `gp200 snaptone` lists the 10 slots (1-5 AMP, 6-10 DST). Conversion NAM→SnapTone is done in VLTN Tone Studio (app menu): the user picks the capture there and presses Write (on the JR it times out — expected). Then `gp200 snaptone <N>` (empty slot, ask which) re-uploads the last converted capture from VLTN's log at a pace the JR accepts, and keeps a copy in `~/.local/share/gp200/snaptones/*.vtsi` (re-upload: `gp200 snaptone <N> file.vtsi`). Close VLTN first (it holds the MIDI port). Never `--force` over a non-empty slot without the user's explicit OK: SnapTones can't be read back. Use it in a preset as `{"effect": "SnapTone <N>"}` in AMP (1-5) or DST (6-10).

## If something fails
- "GP-200 not found" → pedal unplugged/off; ask them to connect it.
- "readback differs" → retry the write once; if params still drop, report which ones (timing issue, see CLAUDE.md).
- Unknown effect/param → the error lists valid names; fix the JSON, don't guess IDs.

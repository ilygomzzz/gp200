# 002 — Preset workbench (per-slot chat + live editing)

## Problem
The Presets tab (spec 001) only shows a slot as monospace text. To change anything the user must switch to the global Chat tab and describe the slot in words. User's words: "desde presets poder seleccionar uno y charlar ahí mismo, un poco de ui que me permita mover cosas y etc desde esa vista". Also "seguir patrones de diseño": `app/gp200_app.py` is one ~250-line file with widgets talking to `Device` directly, which breaks `constitution.md` (written after 001).

## Goal
The Presets tab becomes a workbench:
1. Click a slot → the pedal switches to it immediately (the user hears it) and its chain appears as 11 "pedals" in signal order.
2. A chat panel next to it talks about **that** slot (own conversation per slot; slot label + current preset JSON + guitar in the system prompt).
3. Edit in place, live on the pedal's edit buffer: drag to reorder, toggle on/off, change a block's effect (picker filtered by block, with the real-gear description), change params (catalog ranges), rename.
4. Nothing persists until **Guardar** (verified write + automatic backup). **Descartar** reloads the stored version. Factory presets (1A–33C) can be edited live but never overwritten: only **Guardar en…** a free slot.
6. Per-slot chat history (transcript + Claude session id) persists across app restarts in `~/.local/share/gp200/chats.json`, keyed by slot label; "Nueva conversación" clears it.
5. The app is refactored to the constitution: `app/theme.py`, `app/model.py`, `app/chat.py`, `app/widgets/`, one MIDI worker/lock.

The global Chat tab **stays** (renamed "Chat general"): it serves the "make me sound X, which slot?" flow, which has no slot yet. It reuses the same chat panel widget and model with context "global".

## Out of scope (follow-ups)
- Patch tempo / Delay Time (Time is overwritten by the tempo on save; shown read-only with a note). → 003 (tempo support lands with tabs→preset).
- Tabs → preset, alphaTab, scratch slots → 003. Guitar trainer → 004.
- FX loop send/return editing, copying/moving presets between slots, SnapTone upload from the UI.
- Tracking chats when a preset moves to another slot (chats are keyed by slot label). Persisting the global chat (in memory only).
- Undo history beyond "Descartar" (one level: stored version).

## Acceptance criteria
Screenshots: offscreen grab of the window (`QWidget.grab()` in a test script) or `~/Personalization/tools/hx shot "x,y WxH" file.png`; never click on the user's open app window.

1. **Refactor, no regressions.** `python3 -m unittest discover tests` passes. Slot list loads progressively as in 001 (factory names, empty slots greyed "(vacío)"), pedal unplugged → inline error, no crash. No hex colour literals outside `app/theme.py` (`grep -rn "#[0-9a-fA-F]\{3,6\}\b" app --include=*.py` only hits theme.py). No widget imports/calls `g.Device`, `with_device` or `msg_*` (grep).
2. **Screenshot A — workbench, clean slot (e.g. 34A):** left slot list with 34A highlighted; centre header "34A" + name field + disabled "Guardar"/"Descartar"; chain strip of 11 pedals in the slot's stored order, off blocks visibly dimmed with "off" text; AMP selected (accent border) and its editor below (effect picker, description line, on/off switch, one row per catalog param with slider + value); right chat panel titled "Chat · 34A <name>" with empty-state hint.
3. **Screenshot B — dirty:** after moving a block and changing a param: header shows "Sin guardar" in the warn colour, Guardar/Descartar enabled, moved pedal at its new position.
4. **Screenshot C — Claude busy:** while a chat run is active, editor and strip are disabled with the inline note "Claude está usando la pedalera…", chat input disabled, streamed reply lines visible.
5. **Per-slot chat (persistent).** In 34A ask "¿qué tiene este preset?" → Spanish answer about 34A's actual blocks without the user naming the slot. Switch to 34B and back: each slot shows its own transcript; 34B's question does not resume 34A's session. The "Chat general" tab keeps its own separate conversation. Quit and relaunch the app → 34A shows its previous transcript and the next question resumes the same session (`--resume <id>` from `chats.json`); "Nueva conversación" empties the transcript and the next question starts a new session. A corrupt/missing `chats.json` → empty chats, no crash.
6. **Hardware, live edits (test slot 35A, empty):** effect change, param change, toggle and reorder are audible/visible on the pedal within ~0.5 s of the action (effect change ≤ ~1 s); `gp200 show 35A` afterwards still shows the stored (unchanged) preset; Descartar returns the pedal and the view to the stored preset.
7. **Hardware, Guardar on 35A:** writes via the verified path (backup file appears in `backups/`, readback diff empty), inline progress "Guardando 35A… (n/11)", then "Guardado y verificado". Slot list entry updates to the new name.
8. **Exclusive MIDI.** Clicking/editing during the initial slot scan works (edits jump ahead of the scan); sending a chat message while a save runs is disabled with "Espera a que termine de guardar"; after a Claude run that wrote the current slot, the workbench reloads it (and if it was dirty, shows "Claude ha reescrito 35A; tus cambios sin guardar se han sustituido").
9. **Keyboard/context menu parity:** every drag action also works with the keyboard (Ctrl+←/→ on a selected pedal) and the pedal context menu; toggling with Space and the context menu.
10. **Click = select.** Clicking a slot switches the pedal to it (status "Pedalera en 35A"). While dirty, clicking another slot first shows the inline bar "¿Descartar cambios de 35A?" [Descartar y cambiar] [Seguir editando]; no silent loss. While a Claude run is active a click only shows the slot (no select) and the status says "Claude está usando la pedalera: 35A se leerá cuando termine".
12. **Factory slots:** on 12A (factory) live edits work, "Guardar" is disabled with the hint "Preset de fábrica: guárdalo en un slot libre"; "Guardar en…" offers only slots named "It's GP-200JR" (never 85C), the first free from 34A preselected; saving writes there (verified + backup), the factory slot stays untouched (`gp200 show 12A` unchanged) and the workbench opens the target slot.
11. **Must not change:** CLI behaviour of `gp200` (incl. `write` output and backups), the launcher `bin/gp200-app`, the menu entry, the chat tool allow-list.

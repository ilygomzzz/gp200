# gp200 app constitution

Invariants every app spec respects (PyQt6 app in `app/`). Changing anything here = its own spec + user OK.

## Architecture (patterns)
- **Layers**: `bin/gp200` is the protocol/model layer (pure functions + `Device`); the app imports it as a module and never re-implements protocol, effect lookup or preset building. New protocol logic goes into `bin/gp200` with a CLI entry and a test.
- **Model / view split**: pedal state lives in model objects (`app/model.py`: slots, current preset, edit buffer) that emit Qt signals; widgets only render model state and call model methods. No widget talks to `Device` directly.
- **I/O off the UI thread**: every MIDI or subprocess operation runs in a worker (`QThread`/`QProcess`); the UI thread never blocks > 50 ms. Raw MIDI is exclusive: all access goes through the single device lock/queue in the model.
- **One component per file** in `app/widgets/` once a widget passes ~80 lines; reuse existing widgets before adding new ones.
- Pure logic (parsers, mapping, diffing) lives outside widgets and has a unit test in `tests/`.

## Look
- Colors, spacing, radii and fonts come only from `app/theme.py` tokens (no loose hex in widgets).
- Spacing in multiples of 4. Min font 12 px. Monospace only for raw data (params, commands).
- Dark Fusion palette from `theme.py`; empty/disabled things use `theme.dim`, errors `theme.danger`, the accent only for the active/selected thing.
- UI text in plain Spanish; code, comments, docs in English.

## Behaviour
- Anything that writes to the pedal is either **live and undoable** (edit buffer, not saved until "Guardar") or **confirmed** (overwrite a non-empty slot). Every save keeps the automatic backup.
- Long operations show progress/status inline (no modal spinners); errors appear inline in the area that failed, never as a crash or a blocking dialog.
- Drag-and-drop, keyboard and context menus do the same thing (no action only reachable by drag).
- Chat with Claude: one conversation per context (global or per slot); tools limited to the gp200 CLI + repo files; the current context (slot, preset JSON, guitar) is passed in the system prompt, not typed by the user.

## Security
- Subprocesses only with argument lists (no shell strings built from user text). Paths from files/network validated. No secrets in the repo or in logs.

# gp200 app constitution

Invariants every app spec respects (PyQt6 + Qt Quick app in `app/`). Changing anything here = its own spec + user OK.

## Architecture (patterns)
- **Layers**: `bin/gp200` is the protocol/model layer (pure functions + `Device`); the app imports it as a module and never re-implements protocol, effect lookup or preset building. New protocol logic goes into `bin/gp200` with a CLI entry and a test.
- **Model / view split**: pedal state lives in model objects (`app/model.py`: slots, current preset, edit buffer) that emit Qt signals. The view layer is Qt Quick: QML in `app/qml/`, one component per file; Python view-models in `app/bridge.py` adapt `Pedal`/`Workbench`/`ChatHub` to QML (properties, signals, slots) and hold no pedal state of their own. QML never reaches `Device` or `g`.
- **I/O off the UI thread**: every MIDI or subprocess operation runs in a worker (`QThread`/`QProcess`); the UI thread never blocks > 50 ms. Raw MIDI is exclusive: all access goes through the single device lock/queue in the model.
- Reuse existing QML components before adding new ones.
- Pure logic (parsers, mapping, diffing) lives outside widgets and has a unit test in `tests/`.

## Look
- Colors, spacing, radii and fonts come only from `app/theme.py` tokens (no loose hex in QML or Python view code; tokens reach QML only through the `T` object built from `theme.py`).
- Spacing in multiples of 4. Min font 12 px. Monospace only for raw data (params, commands).
- Qt Quick Controls Basic style restyled with the app's own glass palette from `theme.py` (style inspired by desk-ui, no runtime link to it); empty/disabled things use `theme.dim`/`theme.ink_soft`, errors `theme.danger`, the accent only for the active/selected thing.
- Glass: the window may be translucent (alpha only from `theme.glass_alpha`); real blur only from the compositor (Hyprland), one glass layer, inner panels are translucent plates, never a second blur; opaque fallback when not on Hyprland; popups/menus/tooltips opaque.
- Gear art = original vector drawings (QtQuick.Shapes) in chassis colours from `theme.chassis`; no real brand logos/names/trade dress in art (catalog desc text with ® stays as text).
- Category colours (`theme.block_colors`) identify block types; never the only carrier of state (pair with text or shape).
- Glyph icons only from `theme.icon_font` via named `theme.glyphs`; every icon-only button has a Spanish tooltip and accessible name.
- UI text in plain Spanish; code, comments, docs in English.

- **Motion**: animations only answer an action or show live data (meter, tuner, cable glow); <= 400 ms; transform/opacity/colour only; `GP200_MOTION=0` turns them off (instant).

## Behaviour
- Anything that writes to the pedal is either **live and undoable** (edit buffer, not saved until "Guardar") or **confirmed** (overwrite a non-empty slot). Every save keeps the automatic backup.
- Long operations show progress/status inline (no modal spinners); errors appear inline in the area that failed, never as a crash or a blocking dialog.
- Drag-and-drop, keyboard and context menus do the same thing (no action only reachable by drag).
- Chat with Claude: one conversation per context (global or per slot); tools limited to the gp200 CLI + repo files; the current context (slot, preset JSON, guitar) is passed in the system prompt, not typed by the user.

- **Audio** (from phase 3): the app may read the pedal's audio from PipeWire source `gp200_stereo_clean` via `pw-record` in a `QProcess` with a fixed argument list, only while the window is visible; never records to disk; failure = "Sin audio" inline. `numpy` becomes an app dependency (the CLI stays stdlib only).

## Security
- Subprocesses only with argument lists (no shell strings built from user text). Paths from files/network validated. No secrets in the repo or in logs.

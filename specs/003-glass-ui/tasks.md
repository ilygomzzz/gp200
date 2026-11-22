# 003 — Glass UI: tasks

Approved by the user 2026-11-22 (design, constitution, Hyprland rule, renumbering).
Run `python3 -m unittest discover tests` after every task; it must stay green.

- [x] 1. **Constitution** — done by the designer (Look section updated). Implementer: nothing.
- [x] 2. **Tokens** — `app/theme.py`: re-value existing tokens, add the new ones from design.md (fixed `tint`, no
   desk-ui file read, `glass` detection incl. `GP200_GLASS=0`,
   block_colors, glyphs with verified codepoints, radii, spacing s5/s6), app QSS (plate, buttons, fields,
   tab pill, scrollbars, opaque popups/tooltips). Done: app starts offscreen; every glyph renders (check a
   grab); no hex outside `theme.py` (`grep -rn '#[0-9a-fA-F]\{6\}' app/widgets app/gp200_app.py` empty).
- [x] 3. **Window glass** — `app/gp200_app.py`: `setDesktopFileName("gp200")`, `WA_TranslucentBackground` + `bg`
   paint when `theme.glass`, outer padding 16, splitter sizes 312/flex/340, default 1440×880, tab bar pill
   with app glyph + title corner widget, Ctrl+1/Ctrl+2. Done: offscreen grab shows the opaque fallback layout.
- [x] 4. **Pure filter** — `app/model.py`: `slot_matches(label, name, query)`; test in `tests/test_model.py`
   (label "34B", name substring, case-insensitive, empty query matches all, empty slot matches "vacío").
- [x] 5. **Slot grid** — `app/widgets/slot_list.py` rewritten (same API): search + reload row, painted bank grid,
   dirty dot, current outline, keyboard nav, context menu "Abrir", "Ningún slot coincide", status pill.
   Done: A-empty.png matches spec; arrows/Enter/search work offscreen via `QTest`.
- [x] 6. **Knob** — new `app/widgets/knob.py` (`QDial` subclass: paint, vertical drag, Shift fine, context menu
   with inline spinbox and default). Done: `QTest` key/wheel/drag each emit the expected value; disabled
   state shows lock glyph.
- [x] 7. **Block editor** — `app/widgets/block_editor.py`: header (glyph disc, pill picker, power footswitch),
   knob grid with column count from width, switch/combo pill row, DLY note. Same signals.
   Done: B-open.png and F-delay.png match spec.
- [x] 8. **Chain** — `app/widgets/chain_strip.py`: 56×116 tiles with band, glyph, code, name, LED in block colour,
   cable segments, sizes from tokens. Same signals and interactions. Done: B-open.png chain matches spec;
   drag/keyboard/context reorder still produce the same `move`/`move_to` signals.
- [x] 9. **Workbench view + chat** — `app/widgets/workbench_view.py` (plates, header title 24, chips, ghost/primary
   buttons, busy bar on `busy_changed`, status pill, warn-edged inline bars, empty state),
   `app/widgets/chat_panel.py` (plate, icon buttons, input pill, log document stylesheet from tokens).
   Done: C-dirty.png, D-busy.png, E-error.png match spec.
- [x] 10. **Screenshots** — script in the scratchpad (not committed) with a fake pedal, offscreen, saves A–F to
    `specs/003-glass-ui/shots/`.
- [x] 11. **Hyprland rule** (outside repo, approved) — `~/Personalization/dotfiles/.config/hypr/config/windowrules.lua`
    "Opacity Overrides": `class ^gp200$` → `opacity = "1.0 override"`; reload with `~/Personalization/tools/hx reload`;
    add the line to Personalization's `mapa/` note on window rules. Done: `hyprctl clients -j` shows class
    `gp200` for the app window and its opacity is 1.0.
- [ ] 12. **Real glass shot + pedal check** — launch the app on an empty workspace, `grim -g` of its window geometry
    only → G-glass.png. On the real pedal (slot ≥ 34A): knob edit audible, Guardar/Descartar/Guardar en…, dirty
    guard, Claude hold, Ctrl+S, per 002. Done: G-glass.png shows blur; checklist ticked in review.
- [x] 13. **Docs** — `CLAUDE.md`: app line mentions glass theme + `knob.py`; roadmap renumbered (003 glass UI done,
    004 tabs→preset, 005 guitar trainer, SnapTone screen as a later spec); gp200 `mapa/` updated per the global rule.
    Done: both updated in the same commit.

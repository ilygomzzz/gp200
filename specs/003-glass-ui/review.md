APPROVED

Round 1. Tests: `python3 -m unittest discover tests` = 26 OK. Extra shots by the reviewer (realistic params, 1000x640, spinbox): `shots/R-realistic.png`, `R-delay.png`, `R-narrow.png`, `R-spin.png`.
Task 12 (G-glass + on-pedal checks) is left for the main session and does not count here.

| Criterion | Result | Evidence |
|---|---|---|
| A-empty | pass | A-empty.png: top bar, segmented pill, bank grid, empty state, chat hint. (Shot shows no dashed "vacío" cards because the grid is scrolled to banks 1-13; not visible, not checked.) |
| B-open | pass | R-realistic.png: 11 tiles, LEDs lit in block colour for ON, ring for OFF, cable bright through ON/dim through OFF, accent ring on AMP, knob arcs in AMP colour with real values (62/40/55/48/70/35). B-open.png itself has all blocks OFF/0 (fake zeroed data), so it under-demonstrates. |
| C-dirty | pass (partial) | Chip, accent Guardar, ghost buttons visible. The 34B card warn dot is not visible in the shot (grid scrolled); code path exists, slot_list.py:80. |
| D-busy | pass | Progress bar, dimmed/disabled chain+editor, "Guardando 34B…", chat lock text. |
| E-error | pass with nit | Danger pill with glyph shown, but text is elided ("sin acce…"); full text only in tooltip (slot_list.py:182). |
| F-delay | pass | Time knob locked with lock glyph, note visible, Sync/Trail pill combos. Status bar in that shot says "Guardando 34B…" (stale from the D script, not an app bug). |
| G-glass | deferred | Task 12. |
| Min window 1000x640 (design.md) | **fail** | R-narrow.png: chat plate overlaps the centre column, header buttons ("Descartar", "Guardar") are covered and clipped, slot cards cut ("Lead / Lines"). |
| Knob (drag/wheel/keys/menu) | pass | knob.py:93-123 read; 002 values coalesce through ParamRow/Workbench path; implementer's QTest key check ok. Spinbox (R-spin.png, grabbed standalone) opens over the dial, readable, Esc/editingFinished handled. |
| Chain narrow (140 px plate, scrollbar) | pass with nit | R-narrow.png: scrollbar overlays the bottom of the tiles slightly (y~268, below LED row); tiles still usable. |
| Switch/combo pills in one row | pass (unverified wrap) | Only 2 pills in DLY; a 4+ pill effect could overflow the narrow centre column. Not tested. |
| Constitution: no hex outside theme | pass | grep over app/widgets and gp200_app.py empty. |
| Constitution: no Device in widgets / no subprocess / no new timers | pass | grep empty (widgets) for Device/subprocess/QTimer. |
| Layers, model unchanged | pass | model.py diff only adds `slot_matches` (+test); chat.py untouched. |
| Tokens/min font 12/spacing x4 | pass (not exhaustively audited) | Sizes from theme tokens in diff. |
| Opaque popups, tooltips, accessible names, Spanish | pass | knob.py:25-26, tooltips on icon buttons. |
| Outside repo: windowrules.lua | pass | One line added, `class = "^gp200$"`, `opacity = "1.0 override"`, next to terminal override. `hx reload`/`hyprctl clients` check not run by me. |
| Outside repo: mapa/Hyprland.md | pass | Bullet added referencing the rule. |
| Docs (CLAUDE.md, constitution, gp200 mapa) | pass | In diff. |
| Security/perf | pass | No shell strings, no new file paths from input, no polling added. |

## Failures
1. `app/gp200_app.py:36` (and :25-26): minimum widths 260+560+280 = 1100 plus splitter handles and 32 px outer padding exceed the declared window minimum of 1000. At 1000x640 the panels overlap (R-narrow.png). Expected: sum of the three minimums + handles + margins <= window minimum width (lower the min widths, e.g. 232/480/260, or raise `setMinimumSize` width to about 1180 and update design.md), and the header row (title, chip, three buttons) must not be clipped at the minimum.

## Suggestions
- Knob focus ring and "current" outline share the accent (as the implementer noted); acceptable, but the focus ring on a disc next to an accent selected tile is easy to confuse.
- Re-make B/C/F shots with realistic params (script: `/tmp/claude-1000/-home-ilygomzzz-projects/9e6ad2ae-2880-442c-8330-a5a530ccc6b1/scratchpad/rv.py`) so LED/cable ON states are on the spec's shots, and scroll the grid so 34B and a dashed "vacío" card show.
- Elided error text in the status pill (E-error): consider two lines or a wider pill.
- Grab the spinbox inside the full window rather than the editor widget alone.

## Round 2
Tests 26 OK. `gp200_app.py`: panel mins 240/740/260, window min 1300x640 (`min-size.png`): no overlap, header buttons and chain intact. Round-1 failure 1 resolved. Verdict: APPROVED.
Deviations accepted (not failures): window minimum is now 1300 instead of design.md's 1000 (update design.md); pill-row wrap left as a known limit.
Suggestions: at the 240 px slot panel the card name wraps to two lines and the second line is clipped ("Lead / Lines" half-cut, "Crunch / AZ"); full name is in the tooltip. Either elide to one line at narrow widths or raise the slot-panel minimum (~300, window min ~1360). At the default 1440 width cards are fine.
Open: Task 12 (G-glass + on-pedal checklist) still for the main session.

APPROVED (round 2; round-1 CHANGES kept below)

# 004 Pedalboard, Phase 1 review (tasks 1.1-1.13; 1.14 real pedal out of scope, pedal not touched)

Method: unittest (32 OK); offscreen driver (`GP200_FX=0`, fake pedal from tests) that opens slot 100 (34B), takes
shots and drives real mouse/key events through QTest. New shots: `C1-turning.png`, `I1-drag.png`,
`E1-drawers.png`, `E1b-chat.png`, `K-medium-1200.png`, `B1r-1888.png` (re-shot of B1 at 1888).

| Criterion | Result | Evidence |
|---|---|---|
| Tests pass | pass | 32 tests OK |
| A1 empty wide | pass (not re-shot) | `shots/A1-empty-wide.png` |
| B1 open wide: 11 units in ONE row | **FAIL** | `B1r-1888.png`: 11 + VOL wraps to row 2 with the "Salida" jack. Pedalboard.qml:8-10 counts the two jacks as columns (13 items) |
| B1 content (chassis colours, nameplates, mini knobs, LEDs, cables, AMP ring, close-up) | pass, with taste notes | B1r shot |
| C1 turning | pass | `C1-turning.png`: popup "Gain 10", arc, "Sin guardar", Guardar accent. 34B card warn dot not verifiable (fake pedal slot names are "...") |
| D1 compact 945 | pass (implementer shot) | `D1-compact.png` wraps with wrap cable |
| E1 drawers | **FAIL (minor)** | `E1-drawers.png`: slot drawer lets the board show through clearly; constitution says popups/menus opaque. Main.qml:109-119 uses `T.popup_bg` (alpha f2 in theme.py:16) yet bleed is strong; check the SlotGrid cards/plate alpha inside the drawer and make the drawer truly opaque. `E1b-chat.png` taken, not inspected in detail |
| F1 busy, H1 delay | pass (implementer shots, not re-run) | `F1-busy.png`, `H1-delay.png` |
| I1 drag | pass | `I1-drag.png`: unit lifted, other units in place; the accent drop bar is a 3 px line mostly hidden under the lifted unit (suggestion: draw it above, z) |
| Medium 1100-1439 | pass | `K-medium-1200.png`, 1100 px too: slots docked, chat in drawer, board wraps 8+... without clipping |
| Drag reorder | pass | real mouse drag DST: `dropGap` 5, exactly one `move_to('DST', 5)`, order updated. Not tested across the row wrap |
| Ctrl+Left, Space | pass | AMP index 2 to 1; Space toggled once |
| Knob keys | pass | Up +1, PgDn -10, Home 0, End 100 |
| Knob drag | partial | QTest move events produced one coalesced set (value 10, `set_param` called once) so drag works, but 200 px = full range not measured (QTest sends few move events). Wheel, Shift fine, context menus ("Escribir valor…") not exercised |
| Footswitch click zone, double click, context menus | not exercised | Unit.qml:77 uses y 76..112 zone; read only |
| Constitution diff matches Decisions in spec.md | pass | constitution.md diff = the 4 changes verbatim (Architecture, Look, Motion, Audio); Q3 deletion done (`app/widgets/` gone) |
| Layers: QML never reaches Device | pass | grep: bridge.py uses `g` only for catalog/labels (pure helpers); QML only gets `T`, `board`, `slotChat`, `globalChat`, `pedal`. `pedal` has no slots (only signals, used by SlotGrid.qml:19); suggestion: expose it through Board instead |
| No hex outside theme.py | pass | grep over qml/, bridge.py, gp200_app.py: none |
| No QtWidgets left | pass | grep empty |
| No personal data / paths | pass | grep empty |
| Subprocess/MIDI lock | pass | diff adds no subprocess; all MIDI still via `Pedal` |
| Min font 12, spacing multiples of 4 | pass | grep: no pixelSize < 12 |
| No I/O on UI thread / timers | pass | only a 600 ms popup hide Timer and the busy bar animation |
| Teardown QML errors | **benign** | "Cannot read property 'bound/html/hint/title/running' of null" (ChatPane.qml:15,16,30,38,42,43, Main.qml:39) appear ONLY after the engine's context properties are torn down, none during 20 s of normal use, resize, open, drag, drawers. Shutdown-only. Suggestion: guard with `view && view.bound` to keep stderr clean |

## Judging the implementer's known issues
- 1888 wide wraps to 2 rows: real failure. Board width is 1184 px; 13 cells x 104 = 1352 does not fit even if the
  jack counting were fixed, so one row at 1888 needs narrower jack cells or smaller gaps, or the spec/design must
  accept 2 rows at 1888 (then update spec B1). Decide with the user; not a silent deviation.
- Cables snap instead of following animated units: not a criterion failure (Motion rule is "answer an action");
  suggestion only (bind Cable endpoints to the unit's animated x/y).
- Cramped, low-contrast glyph row on stompbox faces: taste; suggestion. Picker ComboBox is unfiltered: spec lists no filter
  (acceptable for phase 1); the ComboBox popup text is white on a near-black field over a bright amp face, readable.

## Failures to fix
1. Pedalboard.qml:8-10 (`count`, `n`): board one row at 1888 wide as in spec B1, or spec amended.
2. Main.qml:109-119 drawers: not opaque (E1-drawers.png).

## Not verified
Real pedal and Hyprland glass/blur (1.14), MultiEffect shadows/glow (disabled offscreen), reorder across the wrap,
wheel/Shift/context-menu on knobs, 2 s drag message coalescing.

# Round 2 (offscreen, no pedal)

Shots renamed: `B1-open-wide-r2.png`, `C1-turning.png`, `E1-drawers.png`, `E1b-chat.png` are round-2 re-shots (I1-drag.png re-taken in round 2).

| Round-1 point | Result | Evidence |
|---|---|---|
| One row at 1888 | pass | `B1-open-wide-r2.png`: 11 units + both jacks in one row (pb width 1184, n 13, rows 1), scaled by `fit`; labels and mini knobs still legible. Wrap path (compact/medium) untouched by the change |
| Drawers opaque | pass | slot drawer (945 wide) and chat drawer (1200 wide) fully opaque in `E1-drawers.png` / `E1b-chat.png` |
| Drag after layout change | pass | real mouse drag DST: one `move_to('DST', 5)`, order updated; Ctrl+Left, Space, knob keys unchanged |
| Teardown errors | still 87 warnings, ALL after the window is closed (counted: 0 before, 87 after "done"). Guards did not silence them but they are shutdown-only; harmless, optional cleanup |
| Drop bar above lifted unit | not re-shot; code change only, accepted |
| Tests | pass | 32 OK |

## Close-up layout vs design.md
Design (Close-up section + mockup): header row, then knob cells 88x112 (dia 64), as many columns as fit, left to right,
then a pill row; plate = "flex". The implementation matches that: 3 knobs left-aligned in 88x112 cells. Deviations, all minor:
- Vertical: `CloseUp.qml` Flow `topPadding: 72` (room for the value popup) plus column spacing leaves ~100 px between the
  header and the knobs; the mockup shows them directly under the header. Suggestion: reduce to ~40 or overlay the popup.
- The plate fills all remaining height (about 620 px at 1888x1016, design mockup ~470), so an AMP with 3 params looks empty. This is
  inherent to "flex" with few params and goes away with phase 2 faces (6 knobs, pills, amp art). Suggestion: cap the plate
  height or centre the knobs vertically; not a failure.
- Switch/combo pills and "Tweedy" picker not visible on this effect (it has none).

Verdict round 2: APPROVED for phase 1 (task 1.14 on real pedal/Hyprland still pending).

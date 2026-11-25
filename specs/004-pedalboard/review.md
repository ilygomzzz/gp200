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

# Phase 2 part A (2.A1-2.A6) — offscreen, no pedal

CHANGES

Tests: 34 OK. No hex literals outside `app/theme.py` (grep over `app/qml` and `app/*.py`); `grep -nE 'radius: (10|14|16|18)\b' app/qml` empty. Warnings from QML: 0 across all my runs.

| Criterion | Result | Evidence |
|---|---|---|
| 2.A1 tokens exported, `font_desc` alias, radii literals gone | pass | `theme.py` diff, `Polish.test_new_tokens_exported`, grep empty |
| 2.A1 nameplate contrast >= 4.5 | pass | `Polish.test_block_colours_readable_on_nameplate` composes the 90 % plate over the 60 % tint face and asserts every block (min CAB 5.23, max VOL 9.37, matches notes.md). Maths is correct. Caveat: asserts block colour as text on plate; `ink_dark` is no longer used on faces |
| 2.A2 stompbox nameplate, LED lens, enamel | pass | `B1-polish.png`: dark code band with block-coloured text legible on all 11 units, filled LED, footswitch larger |
| 2.A3 close-up face capped, knobs centred, LED + switch bottom-centre, popup overlay | pass with a defect | `C1-polish.png`: face 344 px, knobs centred, switch + "Apagado" bottom-centre. Popup is an overlay (`C2-arc-turning.png`), opaque, does not reserve space. Defect below |
| 2.A3 turning a knob shows the bubble | pass | `C2-arc-turning.png` "Gain 6" bubble above the knob, overlapping the picker plate (acceptable, opaque overlay) |
| 2.A3 Space/click on switch toggles | pass | click: LED off -> on; Space with no Tab: toggles back; Tab x4 reaches Footswitch, Space toggles. 0 warnings |
| 2.A4 picker looks like a nameplate; type + Enter sets effect | pass | `C1-polish.png`; Ctrl+A, type "Bellman", Enter -> AMP effect "Bellman 59B", board label updated. Popup list `R2-picker-popup.png`: opaque, 32 px rows, highlighted current, opens from the arrow |
| 2.A5 knob on face: track, white arc, ticks, value chip | pass | `C1-polish.png`, `R2-compact-945-tall.png`; arc visible on the AMP gold face. Not checked on every block colour |
| 2.A6 static skeleton, no icon-only pill | pass | `A1-polish-empty.png`: static bars in slot cards, only the "Leyendo la pedalera..." pill with text |
| Compact 945 | pass at 945x1016 (`R2-compact-945-tall.png`); degraded at 945x800 (see F2) | |

## Failures

F1 (must fix). Dragging a knob scrolls the face. `app/qml/CloseUp.qml:~76-82` puts the knob Flow in a `Flickable` whose `contentHeight` (body = Flow 148 + `ParamPills` + column spacing 12) exceeds the viewport by ~12 px even at 1888, so the Flickable is interactive and steals the vertical drag from `Knob.qml` MouseArea (`app/qml/Knob.qml:~110`, no `preventStealing`). Evidence: `C2-arc-turning.png` — during the drag the whole knob row and the value chips jump up 12 px (knob centre y 465 -> 453) and return on release; a press without movement does not shift anything. Expected: no layout movement while turning. Fix any of: `preventStealing: true` on the Knob MouseArea (also stops Flickable flicking while a knob is held), `interactive: contentHeight > height` plus not reserving the empty `ParamPills` spacing (e.g. `spacing` only when pills are visible), or raise the face so the knob row fits without overflow.

F2 (should fix, minor). At 945x800 with a 6-knob effect (`Bellman 59N`, `R2-compact-945.png`) the knob row is clipped by the face: dials cut in half, labels and values invisible, only scroll-by-wheel reveals them. Face cap 344 minus header/switch leaves ~150 px for a 148 px row plus pills. Expected: the knob row is never clipped; give the Flickable a minimum height or let the switch share the row at narrow heights. At 1016 tall everything fits.

## Deviations in notes.md

| Deviation | Verdict |
|---|---|
| `face_max_h` 344 vs 296 | accept. Picker is 60 tall and the switch lives inside the face, 296 cannot hold them; the token comment records why. polish.md/design.md still say 296: the designer should align them |
| Face top-aligned, no trailing spacer | accept. `C1-polish.png` reads well; the empty plate below the face is the board's remaining space, not a slab |
| StatusPill hidden when text empty | accept (matches 2.A6 intent and the empty-state shot) |
| Footswitch Tab focus + Space (interactive only) | accept; verified, and it satisfies the constitution rule keyboard == mouse. Suggestion: draw a visible focus ring (not checked) |
| Ticks stroke 5 / dash 2, pad 28, >8 knobs use `knob_big` | accept |

## Notes and suggestions
- `B1-polish.png` and `C1-polish.png` are byte-identical (same full-window grab); fine for the criteria, but the label "C1" should say "close-up" in notes.
- The fake catalog gives "Efecto sin catálogo..." for Bellman; test-data artefact, not an app bug.
- Not verified: real pedal, MultiEffect shadows (FX=0), motion (`GP200_MOTION=0` used), ticks on every block colour. My exercise scripts are in the session scratchpad only; extra shots: `C2-arc-turning.png`, `R2-picker-popup.png`, `R2-compact-945.png`, `R2-compact-945-tall.png`.

Verdict part A: CHANGES (F1 required; F2 recommended). Everything else passes.

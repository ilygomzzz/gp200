APPROVED (phase 1 round 2; part A CHANGES then fixed; part B round 2 APPROVED, see sections)

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

# Phase 2 part B (2.0-2.9) — offscreen, fake pedal, GP200_FX=0, no MIDI

CHANGES

Tests: 40 OK. Own harness (QTest on the real window, 1888x1016, slot 34B): real mouse press/move/release on the chain strip, key presses, resizes 1888 -> 1000 -> 945 -> 1200 -> 1888. Extra shots: `RV2-strip-dragmid.png`, `RV2-sel-DLY.png`, `RV2-sel-CAB.png`, `RV2-compact-945.png`.

| Criterion | Result | Evidence |
|---|---|---|
| Tests pass | pass | 40 OK |
| No hex outside theme.py | pass | grep over `app/qml`, `app/*.py` finds only `art.py` family-name strings, no colours |
| make_textures deterministic, colourless, offline | pass | two regenerations identical; output equals committed `app/assets/textures`; numpy + QImage only, no network imports; PNG RGB is white/black + alpha by design |
| Textures budget | pass | 8 PNG, 84 KB total (< 200 KB) |
| Constitution change 5 wording | pass | `git diff constitution.md` text equals spec.md "Constitution change 5" |
| No brand marks in art | pass | M2-families grid: generic shapes, family names are colour/material words; the only brand words are regexes in `art.py` matching catalog desc text (input, not drawn). Plate text "Tweedy" is the catalog effect name |
| Perf | pass (not profiled) | Tex = one tiled Image; 12 `Shape` blocks in total (Knob 4 inside; Stage/Wire/Cable/Treadle 1 each); no Timer/Canvas/JS-per-frame in the new files |
| Accessibility | pass | chain chips: `activeFocusOnTab`, Button role, name "PRE · effect · encendido"; arrows select, Ctrl+arrows move, Space toggles, Enter edits, context menu. Scene units (`SceneUnit.qml`) have a name but no tab stop. Tab order observed after reorder = new chain order (WAH, PRE, AMP, NR, CAB, DST, EQ ...) |
| Chain reorder with real mouse | pass with warning | drag DST over 4 slots: order PRE WAH DST AMP NR CAB EQ ... -> PRE WAH AMP NR CAB DST EQ ...; Ctrl+Right also reorders; click chip selects; scene order unchanged as designed. See F1 |
| Selection sync stage/strip/close-up | pass | board.select drives chip ring, close-up face + hero (DLY, CAB shots); chip click -> close-up. Stage click not driven by my harness (code path shared via board.select) |
| Cables in chain order, behind back line | pass (visual) | B2-rig: cables z 7 over deck/floor, below back-line z 7.5/8 units; no cable crosses cab/rack faces |
| Compact <1100 art cells, resize | pass | 945 and 1000 show art cells in chain order with wrap cable; 1200 shows scene; 1888 -> 945 -> 1888 restores; 0 warnings from resizing |
| Close-up faces (2.9) | pass | `RV2-sel-DLY` rack hero, `RV2-sel-CAB` cabinet hero, J2 amp hero, L2 faders with frequency labels |
| B2 selection: spotlight + 4 px lift | weak | selected unit lifts a few px (DLY, CAB) but the spotlight is barely visible in `RV2-sel-*`; the only clear indicator is the chip ring (see S1) |
| K2 shot content | fail | see F2 |

## Failures

F1 (should fix). Every real chain-strip reorder emits a QML warning: `ChainStrip.qml:94: ReferenceError: cs is not defined` (the `onReleased` line `cs.dropGap = -1` runs after `board.moveTo(...)` rebuilt the Repeater and destroyed the delegate/context). Expected: reset `cs.dropGap` before calling `board.moveTo`, or via a local captured first. Order and send are correct; only the warning (and a stale dropGap if the delegate survives) is at stake. The implementer's board.moveTo-only check could not see it.

F2 (shots must be retaken). `B2-rig.png`, `B2-medium`, `K2-rack.png` are stale or unrealistic: B2/K2 lack the close-up hero that J2 and my fresh grabs show (so they predate 2.9), and K2 shows the rack display "0 ms | 0" while the spec requires "500 ms · Mix 35" (fake pedal values are all 0; spec says realistic, e.g. Gain 55). Because the fixture is zero everywhere, the knob positions, EQ fader positions, treadle angle and display values were never shown with non-trivial data. Retake B2, K2, L2 with realistic values (Delay Time 500, Mix 35, non-zero EQ).

F3 (minor, bug). `Cabinet.qml:28` prints `c.sp + "x12"` always, so a catalog cab "1x6" prints "1x12" (see `RV2-sel-CAB.png`). Expected: the print follows the catalog desc, or no "x12" claim. Also the print touches the cab's bottom-right piping.

## Deviations in notes.md

| Deviation | Verdict |
|---|---|
| tweed/blackface rule split | accept (needed: "Tweed Deluxe" vs blackface Fender models) |
| NR = scaled Stompbox | accept (visible in B2, reads as a small gate pedal) |
| fuzz wedge top omitted | accept; fuzz_violet in M2 is distinct by colour only, fine |
| texture insets approximate rounded corners | accept; no visible bleed in shots |
| M2 grid draws through ArtCell at 2.2x, not the stage | accept for distinctness/seams; it does not prove the stage path, but B2 covers that |
| 2.10 contrast of ink per family not audited; "Tweedy" low contrast on amp plate | not accepted as done: the plate text is hard to read in J2/B2 and collides with the first knob. Please fix or record the ratio (suggestion below) |
| GP200_FX=0 shots; MultiEffect not checked in real window | accept for this round, remains open for the user's real-desktop check |

## Suggestions
- S1: make the stage selection clearer (a brighter spotlight or a thin accent underline on the floor) since the chip ring is the only strong cue.
- S2: amp head name text on the silver plate: use a dark ink and place it away from the knob row.
- S3: scene units at <1400 px: label text under 12 px is hidden as designed, fine.

Not checked: real window MultiEffect, real pedal (2.10), stage mouse click on a unit (tested only through board.select), performance numbers.

Verdict part B: CHANGES (F1 and F2 required, F3 minor).

## Phase 2 part B — round 2

APPROVED for part B (2.0-2.9). 2.10 real-pedal smoke and the real-window MultiEffect check stay with the user.

| Item | Result | Evidence |
|---|---|---|
| Tests | pass | 41 OK |
| F1 dropGap/cs warning | pass | real QTest press/move/release on the strip: order PRE WAH DST AMP ... -> PRE WAH AMP NR CAB DST ..., 0 QML warnings; `ChainStrip.qml:93-94` reads and resets `dropGap` before `moveTo` |
| F2 shots | pass | `J2-amp.png` (hero head, Gain 55/Tone 40/Volume 70, arcs matching), `B2-rig`, `B2-medium`, `K2-rack` now show realistic values; rack displays "Detune 5 · Wet 40", "500 ms · Mix 35", "Decay 70 · Mix 35"; lit LEDs and block-coloured chips visible |
| F3 cab label | pass | stage cab prints "1x6" for the "1x6" Supro desc (`art.py:32` `cone`, `Cabinet.qml:29`) |
| Selection cue | pass | `J2-amp`: selected head has a light rim and sits clearly above the cab; chip ring as before |
| D2-compact (945) | pass | art cells in chain order, wrap cable through the gutter, selected cell (Tweedy) framed, close-up below; no clipping |
| B2-medium (1200) | pass with note | scene scaled, labels hidden, chain strip fits; note below |

Notes (not blocking):
- At 1200 the amp head's top edge touches/clips the stage top (`B2-medium.png`, head at y~148 equals the stage top); at 1888 there is a margin. Suggestion: add a few px of top margin in the stage layout for the head when selected (8 su lift).
- D2-compact: an amp head or rack drawn as a small flat shape inside a tall cell leaves empty cell space; cosmetic.
- Amp nameplate contrast is now asserted >= 4.5 in tests (copper 4.95 per the coordinator; not independently re-computed).

Not checked: real window/MultiEffect, real pedal, mouse click on a stage unit (only through `board.select`), performance numbers.

# Phase 2C (rendered rig), S3 round: reviewer

Verdict: **CHANGES** (uncommitted tree; offscreen only; Blender not run; pedal not touched). Line 1 above still holds the phase 1 verdict; this section is the 2C verdict.

Method: `python3 -m unittest discover tests` = 55 tests OK (includes `test_main_loads_without_warnings` = 0 QML warnings, `test_no_loose_hex_in_render_scripts`, `test_no_overlap_inside_stage`, `test_unit_keys`). Grep for hex, privacy, size, deleted-file refs; viewed `shots/S3-slice.png`, `S3-window.png`, `S3-closeup-AMP.png`, `S3-compact.png`.

| Criterion | Result | Evidence |
|---|---|---|
| Unit tests pass | pass | 55 OK |
| QML smoke 0 warnings | pass | `tests/test_app.py:91-119` asserts `warnings == []` |
| No hex outside theme.py (incl. tools/render) | pass | grep over `app/qml`, `tools/render`, `app/art.py`, `app/bridge.py`, `app/gp200_app.py`: none. Only `tests/test_render.py:21,36-37` (test fixtures). `theme.py` holds 37 hex (allowed) |
| No downloaded assets, text or brand logos baked | pass (by grep) | no `text_add`/font/http/urllib in `tools/render/*.py`; no `.nam`, `.wav`, `.bak` in repo; `backups/` empty and gitignored. Visual check: no logos seen in S3 shots. Full check needs a Blender run (not done) |
| `app/assets/render` ≤ 12 MB | pass | 11,159,517 bytes (11.16 MB decimal); largest file < 600 KB; `plate.jpg` 281,979 bytes (≤ 700 KB) |
| Privacy (no personal paths/emails, no backups, no nam/wav) | pass for committed files | `grep ~` over tools, app, specs, tests, presets, mapa, CLAUDE.md, constitution.md: no hits. **But** untracked `z.png` in repo root (see F1) |
| Deleted vector files: no remaining references | pass | `AmpHead|Cabinet|RackUnit|Treadle|EqBox` only in `spec.md:325` (the rule itself). Vector parts still used: see F2 |
| S3 shots look correct | partial | see F3, F4 |
| 2C.15 audit (determinism, budget table, originality checklist, O3, B3-medium, GP200_FX=0 identical, real-pedal smoke) | **not done** | `tasks.md:183` unticked; no `B3-*`, `H3-*`, `N3-*`, `P3-*`, `C3-*`, `I3-*`, `O3-*`, `M3-*`, `D3-*` shots in `shots/` (only S1/S2/S3 sets, 9 S3 files) |
| Lead-approved cable simplification | accepted | `notes.md` "Deviation decided by the lead". `S3-slice.png` shows the accepted rack/cab drops |

## Failures (blocking)

- **F1 stray file**: `z.png` (1,117,760 bytes, 2304×748, untracked) in the repo root. Not in any spec. Delete it before commit (the file is not mine to delete; reviewer does not edit).
- **F2 vector gear still reachable**: `app/qml/Unit.qml:47` `Stompbox { visible: u.ghost; ... ghost: true }`, reached through `app/qml/Pedalboard.qml:61` `Unit {`, which `app/qml/Main.qml:79` instantiates unconditionally. Spec (full 2C, B3): "zero 2B vector units ... no `Stompbox` reachable". The 2C revision says "no 2B vector unit left anywhere", and 2C.14 is ticked. Expected: ghost/loading states use default-family sprites (spec O3 "loading: default-family sprites at 20 % as ghosts"), or `Pedalboard`/`Unit`/`Stompbox`/`Cable` deleted if dead. `Cable` is only used by `Pedalboard.qml:49`.
- **F3 overlap in the hero (S3-window.png)**: the footswitch of the AMP hero (around x 830–885, y 935–990 in the 1888 px shot) sits across the bottom border of the hero panel and over the "Encendido" tag. Rule of the S2 review: "nothing may overlap". Expected: footswitch fully inside the panel, or the panel grows (`CloseUp.qml` hero/controls row; the `Layout.minimumHeight: 148` change pushed it out earlier).
- **F4 2C.15 not done**: determinism (two `all` runs), budget table, originality checklist and the full-2C shot set are missing. Per the spec the full 2C is not accepted until they exist. A slice-only verdict would be APPROVED for S3 at most. (Not run here: Blender is a slow path and was excluded by the lead.)

## Shot notes (S3, looked at)

- `S3-slice.png`: wooden room, plank wall, red/black rug and the pedalboard read as one room. Pedals and head are clearly rendered now; knob caps and the 34B head are believable. Good.
- `S3-window.png`: chips, chain strip and the hero head render well. The footswitch issue is F3.
- `S3-closeup-AMP.png`: the knobs are rendered caps (`Knob` with `sprite: "pointer_alu"`, `CloseUp.qml:128`), and the head is the rendered model. The rug lane and the cable routing are clean.
- `S3-compact.png`: rendered thumbnails in the cells; rack units (Detune/Pure/Room) are thin strips, hard to read. Chain-order cables run through the cells as lines above the labels; fine for now.

## Suggestions (taste, not blocking)

- Pedal bodies read a little clean at the stage scale; the rustic pass (the S2 round) is only partly visible. Scuffs and wear are hard to see at 1888 px.
- Cable drops from the rack and cab (`S3-slice.png` around x 1270–1340) still look like air lines. Accepted as a lead deviation, but a short shadow under the drop would help.
- Hero text name is elided on narrow heroes (noted in `notes.md`, "Laz..."), consider a second line.

## Security / performance pass (diff)

- Subprocess and shell: not separately grepped in this pass; the render scripts read `app/theme.py` via `ast` (no exec). Re-check before commit.
- Paths: `load_manifest` rejects traversal and subdirectories (`tests/test_render.py:49-53`).
- Blocking: `asynchronous` image loading and timers/polling in the new QML were not checked in this pass (not measured offscreen).
- Nothing new sent to the pedal (`bin/gp200`, `model.py`, `chat.py` untouched in the diff).

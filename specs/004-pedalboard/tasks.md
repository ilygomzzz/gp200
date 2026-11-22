# 004 — Pedalboard: tasks

Waiting for the user's OK (design, mockups, constitution changes, renumbering). Each phase ends shippable:
app runs, `python3 -m unittest discover tests` green, phase shots taken, reviewer pass before the next.
Never write to the pedal outside slot 34B or a free slot ≥ 34A.

## Phase 1 — QML shell + pedalboard + knobs
- [x] 1.1 **Constitution + docs** — `constitution.md` (4 changes from spec.md, after user OK), `CLAUDE.md`
  (app layout: `qml/`, `bridge.py`; roadmap renumbered 004/005/006), project `mapa/` note.
  Done: diff matches spec.md wording.
- [x] 1.2 **Spike: rendering check** — scratch script (not committed): QML window with a `Shape` arc and a
  `MultiEffect` shadow, grabbed with `grabWindow()` on Hyprland and under `QT_QPA_PLATFORM=offscreen`.
  Done: note in `specs/004-pedalboard/notes.md` which shot method works (offscreen or real window only).
- [x] 1.3 **Tokens for QML** — `app/theme.py`: new tokens from design.md, `motion`, `qml_tokens()` dict.
  Test in `tests/test_app.py`: every colour token parses as a QColor, `dur_*` are 0 when `motion` False.
- [x] 1.4 **Pure view helpers** — `unit_view`/`chain_view` (`app/bridge.py` pure functions or
  `app/model.py`); tests in `tests/test_model.py` (mini values = first 3 knob params, unknown effect, order).
- [x] 1.5 **Board view-model** — `app/bridge.py` `Board` (properties/slots in design.md) over `Workbench`.
  Done: `tests/test_bridge.py` with a fake pedal: open → `units`/`order`/`params`; `setParam` changes
  `values` but not `params`; `moveTo` changes `order`; `dirty`/`guard`/`busy` follow the Workbench signals.
- [x] 1.6 **Chat view-model** — `app/bridge.py` `ChatView` (slot + global), lock reasons, rebinding.
  Done: test with a fake `ChatHub` (send → hub.send called with the right key and system prompt).
- [x] 1.7 **Shell** — `app/gp200_app.py`: `QGuiApplication`, `setDesktopFileName("gp200")`, Basic style,
  engine with `T`, `board`, `slotChat`, `globalChat`, `pedal`; scan on start; stop pedal on quit.
  `app/qml/Main.qml` with top bar, tabs, wide/medium/compact states, drawers, glass fill.
  Done: `tests/test_app.py` QML smoke test loads `Main.qml` with no QML warnings (offscreen).
- [x] 1.8 **Slot grid** — `app/qml/SlotGrid.qml` (ListModel + `slot_name` connection, cards, search,
  keyboard, context menu, dirty dot, status pill). Done: A1 shot left column matches 003's A-empty content.
- [x] 1.9 **Knob + popup** — `app/qml/Knob.qml`, `ValuePopup.qml`. Done: QML test (or bridge-driven
  script) for drag/wheel/keys/Home/End/menu values; locked state; C1 shot.
- [x] 1.10 **Units, jacks, cables** — `Unit.qml`, `Stompbox.qml`, `Jack.qml`, `Cable.qml`, `Footswitch.qml`,
  `Pedalboard.qml` (grid positions, wrap, Behaviors, selection/focus, footswitch zone, context menu,
  keyboard, drag + drop bar). Done: B1, D1, I1 shots; reorder via drag/keys/menu each calls `moveTo`/`move` once.
- [x] 1.11 **Close-up + header + inline bars** — `CloseUp.qml`, `ParamPills.qml`, `HeaderBar.qml`,
  `InlineBar.qml`, `StatusPill.qml` (picker, footswitch, knob grid, pills flow, DLY note, guard bar,
  Guardar en… row, busy bar, empty state). Done: B1, F1, H1 shots.
- [x] 1.12 **Chat pane** — `ChatPane.qml` (log over `html`, hint, input, lock, new chat), docked/drawer.
  Done: E1b shot; per-slot and global chats keep history from `chats.json`.
- [x] 1.13 **Remove widgets** — delete `app/widgets/`, widget tests; grep: no `QtWidgets` import in `app/`,
  no hex in `app/qml` or `app/bridge.py`. Done: tests green, A1–I1 shots in `shots/`.
- [ ] 1.14 **Real pedal + Hyprland** — on slot 34B/free slot: phase-1 behaviour list in spec.md
  (toggle by footswitch audible, reorder, knobs, save/readback, discard, guard, Claude hold); live resize
  1888 → 880; `G1-glass.png` (grim). Done: checklist ticked in `review.md`.

## Phase 2 — gear art
- [ ] 2.1 **Art mapping** — `app/art.py` `art_for(block, name, desc)`; tests: TS-808 desc → `od_green`,
  "Marshall® JCM800" → `brit_gold`, "Fender® Tweed Deluxe" → `tweed`, a 4x12 cab → speakers 4, unknown →
  block default, every catalog effect maps to a family with tokens (loop over `data/effects.json`).
- [ ] 2.2 **Tokens** — `theme.chassis` families + knob variants; contrast check of each `ink` on `body`/
  `face` (small script, numbers in `notes.md`).
- [ ] 2.3 **Board units** — `AmpHead.qml`, `Cabinet.qml`, `RackUnit.qml`, `Treadle.qml`, mini stompbox for
  NR, EQ faders on the unit; `Unit.qml` Loader picks by `kind`. Done: B2 shot.
- [ ] 2.4 **Fader** — `Fader.qml` (Knob's input rules, role Slider). Done: test like 1.9.
- [ ] 2.5 **Close-up faces** — `app/qml/faces/` head, cabinet, rack (display with 2 main values), EQ,
  treadle. Done: J2, K2, L2 shots; effect change switches family.
- [ ] 2.6 **Art audit** — M2 families grid shot; check no logo/brand/copied shape. Real-pedal smoke:
  edits on every kind still audible.

## Phase 3 — alive
- [ ] 3.1 **DSP** — `app/audio.py` `level_db`, `pitch_hz`, `note_of`; tests on synthetic sines (E2, A2,
  E4 within ±1 cent at 48 kHz), silence → None/floor.
- [ ] 3.2 **Listener** — `app/audio.py` `Listener` (QProcess args from design.md, chunk parsing, throttled
  signals, start on visible / stop on hide and quit, `available`). Done: test with a fake process feeding a
  sine; manual: `pgrep pw-record` empty after quit.
- [ ] 3.3 **Meter + cable glow + top-bar mini meter** — `Meter.qml`, `Jack.qml`, `Cable.qml`, `TopBar.qml`.
  Done: N3, P3 shots.
- [ ] 3.4 **Tuner** — `Tuner.qml` strip, Ctrl+T. Done: O3 shot; open A within ±3 cents of a reference tuner.
- [ ] 3.5 **Transitions** — entrance stagger, art cross-fade, footswitch/LED, programmatic knob animation,
  `GP200_MOTION=0`. Done: screen recording or 3 frame grabs; all durations ≤ 400 ms; CPU ≤ 10 % idle with audio.

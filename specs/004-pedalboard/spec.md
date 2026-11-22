# 004 — Pedalboard (Qt Quick view: stompboxes, amp, cab, rack, meters, tuner)

Status: **draft, waiting for the user's OK** (design, mockups, constitution changes, roadmap renumbering).

## Problem
003 made the app graphical, but it still reads as a form with coloured tiles: 56×116 chain tiles,
a knob grid on a plate, no motion, no sense of gear. User, verbatim: "y es posible ahora la interfaz,
hacer algo mucho pas profesional y vivo? estilo amplitube, que se vean los pedales y etc, con los knobs y
todo? osea pensando a nivel gigante". Then, after the proposal: "tu dale".

Second, a 003 defect: on Hyprland the window tiles at half screen (DP-2 1920×1080 → ~945×1016; DP-3
2560×1440 → ~1265×1376), but 003's minimum width is 1300 px, so content is clipped.

## Goal
Same app, same model, same behaviour, but the view becomes a live rig, drawn by the GPU:
1. **Qt Quick (QML) view layer** in one `QQmlApplicationEngine` window; Python model untouched
   (`bin/gp200`, `app/model.py` `Pedal`/`Workbench`, `app/chat.py`), exposed through a thin view-model
   (`app/bridge.py`).
2. **Pedalboard**: the 11 blocks in signal order as units on a board, joined by patch cables from an
   input jack ("Guitarra") to an output jack ("Salida"). Each unit is original vector gear art: chassis,
   printed name, mini knobs that show real values, footswitch with LED. Tap the footswitch = on/off;
   drag to reorder (keyboard and context menu do the same).
3. **Close-up**: the selected unit, big, with real knobs (textured, pointer, value arc) that respond to
   drag, wheel and keys and show a big value popup while turning.
4. **Gear by type** (phase 2): AMP = amp head, CAB = speaker cabinet, MOD/DLY/RVB = rack units with a small
   display, EQ = fader bank, WAH/VOL = treadle. Art family chosen from the effect's catalog `desc`
   (e.g. a green overdrive, a gold British head) — original designs, no real brand logos or trade dress.
5. **Alive** (phase 3): live output meter and tuner from the pedal's USB audio, cables that glow with the
   signal, animated preset transitions.
6. **Fits a half-screen tile**: responsive layout from 880 px wide; no Hyprland float rule.

## Phases (each independently shippable; the app works after each)
- **Phase 1 — QML shell + pedalboard + knobs**: everything 002/003 does, in QML. Units are stompboxes
  for every block (category chassis colour), close-up with knobs, slot grid, chat, responsive layout.
  `app/widgets/` is deleted at the end of the phase.
- **Phase 2 — gear art**: amp head, cabinet, rack units, EQ faders, treadles; art family per effect `desc`.
- **Phase 3 — alive**: audio listener (meter + tuner), signal-lit cables, preset/effect transitions.

## Out of scope
- Any change to `bin/gp200`, `app/model.py` logic or `app/chat.py` logic and their signals
  (one pure helper per phase is added to model-side modules, each with a test, see design.md).
- Writing anything new to the pedal (no tempo, no global settings, no tuner on the pedal).
- Audio output, playback, recording to file, effects processing in the app.
- Real-gear photos or bitmaps, real brand names/logos as art, copying AmpliTube's look.
- 3D (Qt Quick 3D), theme switching, light theme, user-placed free board layout (positions come from
  the chain order only).
- Tabs → preset (now 005), guitar trainer (now 006), SnapTone screen (later).

## Roadmap renumbering (needs user OK)
004 pedalboard (this), 005 tabs→preset, 006 guitar trainer (reuses this spec's `app/audio.py` pitch
detection), SnapTone screen later. `CLAUDE.md` roadmap line updated by the implementer.

## Acceptance criteria
Shots go to `specs/004-pedalboard/shots/`. Shots are taken from a real window (Hyprland, fake pedal) with
`QQuickWindow.grabWindow()` from a scratch script, at the stated window size; `G-*` shots are `grim` of
the real app on the real pedal. (Offscreen rendering of Shapes/MultiEffect is not guaranteed; task 1.2
checks it and the reviewer may use offscreen if it works.)

### Phase 1
Screenshots:
- **A1-empty-wide.png** (1888×1016, no slot open): top bar (app glyph, "GP-200JR", pill "Presets | Chat
  general"); slot grid docked left (banks 1..85, A/B/C cards, dashed "vacío" for 34A+); board shows only the
  "Guitarra" and "Salida" jacks joined by one cable and the text "Elige un slot para ver su cadena";
  chat docked right with its hint.
- **B1-open-wide.png** (1888×1016, slot 34B, AMP selected, realistic params): 11 stompboxes in one row in
  signal order, each with chassis in its block colour family, nameplate (effect name), block code, 2–3 mini
  knobs, footswitch and LED (lit = filled LED + glow, off = dark ring); cables between jack and units,
  lit through ON units, grey through OFF; AMP unit has the accent selection ring. Close-up below: AMP
  chassis face, effect picker "UK 800", desc "Marshall® JCM800", big footswitch, 6 knobs with labels.
- **C1-turning.png**: mid-drag on Gain: big value popup "Gain 63" above the knob, value arc updated, chip
  "● Sin guardar", Guardar is the accent solid button, 34B card has the warn dot.
- **D1-compact.png** (945×1016, slot 34B open): no clipping anywhere; slot grid and chat are hidden behind
  top-bar buttons; board wraps to 2 rows (8 + 3) with the wrap cable routed through the row gutter; header
  buttons Descartar / Guardar en… / Guardar fully visible; close-up below with knobs.
- **E1-drawers.png** (945×1016): slot drawer open over the board (left), and a second shot
  **E1b-chat.png** with the chat drawer open (right).
- **F1-busy.png**: Workbench busy "save": accent indeterminate bar on the board, board + close-up at 50 %
  opacity and disabled, status pill "Guardando 34B… (3/11)", chat input locked.
- **H1-delay.png**: DLY selected: Time knob locked (lock glyph on the cap, grey arc), the 003 note visible;
  a combo param is a pill combo.
- **I1-drag.png**: mid-drag of the DST unit: unit lifted (scale 1.05, shadow), accent drop bar in the gap
  where it will land, other units in place.

Behaviour (real pedal, slot 34B or a free slot ≥ 34A):
- Every 002/003 acceptance item still passes: live edits audible, Guardar writes with backup + readback,
  Descartar restores, Guardar en… only free slots, dirty guard on slot switch ("¿Descartar cambios de
  34B?" bar), per-slot chat + global chat, Claude busy hold, Ctrl+S, Ctrl+1/Ctrl+2.
- Footswitch tap (click on the footswitch area of a unit or of the close-up) toggles the block on the
  pedal, audibly; click elsewhere on a unit selects it; double-click a unit / Space toggles.
- Reorder by drag, by Ctrl+←/→ on the focused unit and by context menu ("Mover a la izquierda/derecha")
  each sends one reorder and the order is audible/visible; works across the row wrap in compact layout.
- Knob: vertical drag ≈ 200 px = full range, Shift = fine (×0.2), wheel 1 step, arrows 1 step,
  PgUp/PgDn 10, Home/End min/max; context menu "Escribir valor…", "Valor por defecto". Values coalesce
  through `Workbench.set_param` (no MIDI floods: a 2 s fast drag sends ≤ one message per worker cycle).
- Slot grid: click/Enter opens, arrows navigate, search filters, context menu "Abrir"; in compact the
  drawer closes after a slot is opened.
- Resize live from 1888 to 880 px wide: layout switches wide → medium → compact without overlap or
  clipped header buttons; keyboard focus is kept.
- Window opaque off Hyprland / `GP200_GLASS=0`; glass (wallpaper blurred through) on Hyprland.
- UI thread never blocks > 50 ms (scan of 255 slots keeps the board responsive).

### Phase 2
Screenshots (1888×1016 unless noted):
- **B2-rig.png** (34B realistic): AMP unit is an amp head (tolex frame, faceplate, row of mini knobs,
  pilot light lit when ON), CAB a cabinet (grille, speaker config from desc e.g. "4x12"), MOD/DLY/RVB rack
  units (1U faceplate, small display with main value e.g. "500 ms"), EQ a fader bank, WAH/VOL a treadle,
  other blocks stompboxes. Units sit on a common floor line; cables still connect jack to jack.
- **J2-amp.png**: close-up of AMP = full amp faceplate with knobs in one row, pilot jewel, nameplate.
- **K2-rack.png**: close-up of DLY = rack face, display "500 ms · Mix 35" and knobs.
- **L2-eq.png**: close-up of EQ = vertical faders with frequency labels.
- **M2-families.png** (a scratch grid of the art families, one unit each): every family visibly distinct;
  no real brand logo, name or trade-dress shape anywhere on the art.
Behaviour: same interactions as phase 1 on every unit kind (faders and treadle obey the knob keyboard/
wheel/drag rules); changing the effect of a block changes its art family when the new desc maps elsewhere.

### Phase 3
Screenshots:
- **N3-meter.png** (guitar playing into the pedal): stereo meter next to "Salida" moving; cables of ON
  units glow with level.
- **O3-tuner.png**: tuner open over the board: note name large, needle/strip with cents, "A 110.0 Hz".
- **P3-noaudio.png**: source missing (`pw-record` fails): meter shows "Sin audio" dim, tuner button
  disabled with tooltip, nothing else changes.
Behaviour:
- Opening a slot plays a staggered entrance ≤ 400 ms total; changing an effect cross-fades the art
  (≤ 250 ms); toggling animates the LED/footswitch (≤ 150 ms). `GP200_MOTION=0` makes all of them instant.
- Tuner: a sustained open A string reads "A" within ±3 cents of a reference tuner, updates ≥ 10×/s.
- Meter: level follows playing with ≤ 100 ms visible lag; silence → meter at floor within 1 s.
- `pw-record` runs only while the window is visible; stops on minimise/hide and on quit (no orphan
  process: `pgrep -f "pw-record --target gp200_stereo_clean"` empty after closing).
- CPU with audio on, idle board: ≤ 10 % of one core (measure with `top`).

### Must not change (all phases)
- `bin/gp200`, `Pedal`, `Workbench`, `ChatHub`, `ChatSession` behaviour and signals; `tests/test_model.py`
  and codec tests pass (`python3 -m unittest discover tests`).
- No QML file or bridge talks to `Device`; no hex outside `theme.py`; spacing multiples of 4; min font
  12 px; UI text Spanish; Wayland app_id `gp200` (Hyprland opacity rule keeps working).

## Constitution change (needs user OK; applied by the implementer in task 1.1 after OK)
1. **Architecture**: the view layer is Qt Quick: QML in `app/qml/`, one component per file; Python
   view-models in `app/bridge.py` adapt `Pedal`/`Workbench`/`ChatHub` to QML (properties, signals, slots)
   and hold no pedal state of their own. QML never reaches `Device` or `g`. Replaces the
   "One component per file in `app/widgets/`" rule.
2. **Look**: "no loose hex in widgets" → "no loose hex in QML or Python view code"; tokens reach QML only
   through the `T` object built from `theme.py`. "Fusion" → Qt Quick Controls Basic style, restyled with
   tokens. New: **gear art** = original vector drawings (QtQuick.Shapes) in chassis colours from
   `theme.chassis`; no real brand logos/names/trade dress in art (catalog desc text with ® stays as text).
   Glass rules unchanged (window `color` transparent + `bg` fill, one glass layer, opaque popups).
3. **Motion (new)**: animations only answer an action or show live data (meter, tuner, cable glow);
   ≤ 400 ms; transform/opacity/colour only; `GP200_MOTION=0` turns them off (instant).
4. **Audio (new, phase 3)**: the app may **read** the pedal's audio from PipeWire source
   `gp200_stereo_clean` via `pw-record` in a `QProcess` with a fixed argument list, only while the window is
   visible; never records to disk; failure = "Sin audio" inline. `numpy` becomes an app dependency
   (the CLI stays stdlib only).

## Decisions (user OK 2026-11-22)
- Design, phases and constitution changes approved ("DALE").
- Q1 audio source: unknown yet; label the meter "Salida" and verify by a short recording in phase 3.
- Q2 audio listening: off by default, only after pressing "Escuchar".
- Q3 old widget UI: deleted at the end of phase 1 (git history is the fallback).
- Q4 art priority: the gear used in the user's presets in `presets/` first.

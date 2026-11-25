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
- **Phase 2 — polish + rig scene**: quick touches from `polish.md` (P1–P5), then a stage (amp stack, rack,
  pedalboard on a stage mat, chain strip for order), art family per effect `desc`; art cells below 1100 px.
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

### Phase 2 — polish + rig scene (rewritten 2026-11-25, see `polish.md`)
Part A, quick touches (shots 1888×1016 and 1200 unless noted; fake pedal with realistic values, e.g. Gain 55):
- **B1-polish.png**: stompbox codes printed on a dark nameplate band in the block colour; every block's code
  ≥ 4.5:1 (numbers in `notes.md`); unlit LEDs are filled dark lenses, lit ones in block colour.
- **C1-polish.png**: close-up face ≤ 296 px high (rest of the plate neutral glass), knobs 72 px centred in one row,
  no empty band above them, value bubble still shown while turning; LED + footswitch at the bottom centre with
  "Encendido"/"Apagado"; effect picker is a dark nameplate pill (name 18 px + description), no Basic-style field.
- **C2-arc.png**: one knob on each of the 11 block faces; the value arc and printed ticks are visible on all.
Part B, rig scene (≥ 1100 px wide; its vector gear art is superseded by "Phase 2C — rendered rig" below, its logic stays):
- **B2-rig.png** (34B realistic): the board plate is a stage — dark wall, rubber stage-mat floor, horizon ~58 %
  down, one top-left key light, contact shadows on the floor. Back line: amp head (tolex, panel, pilot jewel lit
  when ON) on a cabinet (grille cloth, speaker config from desc e.g. "4x12"); a rack case with MOD/DLY/RVB as 1U
  units whose displays show the main value in the block colour ("500 ms"). Floor: a pedalboard with rails holding
  PRE/DST/NR/EQ as stompboxes (EQ with mini faders), WAH/VOL as treadles at the right. Cables run in chain order
  between unit jacks ("Guitarra" enters at the floor's left edge, "Salida" leaves the head); OFF blocks have a
  dark LED and a dark cable segment. Under the stage a chain strip of 11 chips (glyph + code) in chain order.
- **B2-medium.png** (1200 wide): same scene scaled; labels below 12 px effective are hidden (tooltip instead).
- **D2-compact.png** (945 wide): no scene; art cells (each block drawn as its kind) in chain order.
- **I2-reorder.png**: dragging a chip in the chain strip moves the block; scene units keep their places, cables
  re-route; Ctrl+←/→ and the context menu do the same.
- **J2-amp.png**, **K2-rack.png** (display "500 ms · Mix 35"), **L2-eq.png** (vertical faders with frequency
  labels): close-up faces drawn by the same unit components as the stage, at larger size.
- **M2-families.png** (scratch grid, every family × kind): every family visibly distinct; no real brand logo,
  name or trade-dress shape anywhere; textures look seamless (no tile seams).
Behaviour: same interactions as phase 1 on every unit kind (clicking a scene unit or a chip selects the block;
faders and treadles obey the knob keyboard/wheel/drag rules); Tab order follows the chain order; changing a
block's effect changes its art family when the new desc maps elsewhere; selection moves the spotlight and lifts
the unit (≤ 200 ms, instant with `GP200_MOTION=0`); all art also renders with `GP200_FX=0` (shadows are sprites,
not MultiEffect). Real pedal: edits on every kind still audible; no change to what is sent.

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

## Constitution change 5 (user OK 2026-11-25; applied by the implementer in task 2.0)
Replace the **gear art** sentence in Look with: "Gear art = original drawings: geometry and colour in
QtQuick.Shapes from `theme` tokens; colourless alpha material tiles and shadow/spotlight sprites generated by
`tools/make_textures.py` (committed in `app/assets/`, no photos, no logos, no third-party art); no real brand
logos/names/trade dress in art (catalog desc text with ® stays as text)."

## Decisions (user OK 2026-11-22)
- Design, phases and constitution changes approved ("DALE").
- Q1 audio source: unknown yet; label the meter "Salida" and verify by a short recording in phase 3.
- Q2 audio listening: off by default, only after pressing "Escuchar".
- Q3 old widget UI: deleted at the end of phase 1 (git history is the fallback).
- Q4 art priority: the gear used in the user's presets in `presets/` first.

## Decisions (user OK 2026-11-25, on `polish.md`)
- Phase 2 = polish quick touches P1–P5 first, then the rig scene (`polish.md` #1).
- Scene layout: units placed **by kind** (amp stack + rack on the back line, stompboxes/treadles on the floor);
  signal order shown by cables in chain order + a **chain strip** under the stage, where reorder lives.
- Floor: **rubber stage mat** (not wood).
- Windows < 1100 px: **art cells**, no scene.
- Constitution change 5 (generated colourless alpha textures + shadow/spotlight sprites) approved.
- Skeleton loading bars are **static** (no pulse), respecting the ≤ 400 ms motion rule.

---

## Phase 2C — rendered rig (draft 2026-11-25, waiting for the user's OK)
Supersedes the **vector gear art** of Part B (QtQuick.Shapes bodies, tiled alpha textures on gear, flat wall/mat, cubic
cables). Kept from 2B: `bridge.py` model (`Board`, `unit_view`, `art_for` kinds/families), chain strip and all
interactions, zone layout by kind, compact (< 1100 px) logic, close-up behaviour (picker, footswitch, knob input rules).

### Problem
User on the 2B scene (commit af44f0f), verbatim: "esta bien, pero se siente muy goofi, lienas con tengentes notorias y
es como para niños chicos, quiero maaas real, y la uliminación, moqueta y todo, no se siente como estar en una sala,
basate muuucho en amplitube". Then chose pre-rendered art made with Blender, AmpliTube's own approach: our own
procedurally modelled gear and room rendered with Cycles, shown as images in QML; knobs and live parts as overlays.

### Goal
The board reads as a photo of a real rehearsal room: carpet, painted wall, warm practical light, real contact shadows,
gear with tolex, grille cloth, brushed metal and chrome. Everything that changes (knob values, LEDs, displays, effect
names, cables, selection) stays live in QML over the renders. Same app, same model, same behaviour.

### Out of scope (2C)
- Any AmpliTube asset, screenshot, model or texture; any downloaded model, HDRI, texture, photo or font for renders;
  real brand logos, names, model numbers, script plates or trade-dress silhouettes (see design.md "Originality").
- Qt Quick 3D or any runtime 3D; Blender as a runtime dependency (it is a dev tool; renders are committed).
- Animated renders (only frame swaps: treadle rocker frames); camera moves; user-placed gear.
- Changes to `bin/gp200`, `model.py`, `chat.py`, what is sent to the pedal.

### Acceptance — vertical slice (gate: user approves S-shots before 2C.9+)
Shots in `specs/004-pedalboard/shots/`, fake pedal with 34B's real values (`gp200 show 34B`: AMP Silver Twin Gain 45,
CAB Dark Twin, DST Lazaro, NR Gate 1, EQ, RVB Tube Spring), offscreen grab as before.
- **R0-plate.png** = `app/assets/render/plate.jpg` itself (2400×780): empty room, no gear except the pedalboard and the
  empty rack case on its stand. Shows: charcoal low-pile carpet with visible fibre grain in the foreground and soft
  falloff to the back; a painted back wall (dark slate, roller texture) with a band of fabric acoustic panels; a caged
  warm bulb (practical) on the wall top-left lighting a warm pool; the floor/wall junction with a dark skirting board and
  ambient occlusion; key light from top-left front, cool fill from the right, a rim light from behind. No pure-black
  areas without detail; no visible tiling repetition; no text, logo or brand.
- **S1-slice.png** (1888×1016, 34B open, AMP selected): plate scaled to the board; rendered amp head (34B family) on a
  rendered cab (34B grille + speaker variant) and a rendered DST stompbox, each with baked contact shadows that touch
  the carpet/cab top; their knobs show 34B's values (pointer angles match Gain 45 etc.); the head's pilot jewel and the
  DST LED are lit (warm glow spills on the panel); effect names printed on the nameplates in perspective. Units not yet
  rendered use the 2B vector component (mixed scene accepted only in the slice). Cables: black rubber, 3-tone shading,
  rendered chrome plugs at the jacks, floor runs lie on the carpet (no loops in the air, no visible tangent swoops).
- **S1-closeup.png** (close-up of AMP, mid-drag on Gain): frontal hero render of the head's control panel at ≥ 2× stage
  detail; the knob being dragged rotates (cap turns, highlight stays fixed), value bubble "Gain 63" shown.
- **S1-knob-sheet.png** (scratch): the slice knob type at 0, 25, 50, 75, 100 % on the stage and on the hero.
User decision required after the S-shots: OK / changes (camera, light, carpet, palette) before the rest is rendered.

### Acceptance — full 2C
- **B3-rig.png** (1888×1016, 34B) and **B3-rig-alt.png** (a slot whose AMP/CAB/DST map to other families, e.g. a
  British head + 4x12): every unit rendered (head, cab, rack case with MOD/DLY/RVB 1U units, PRE, DST, NR, EQ, WAH, VOL);
  rack displays show live values in block colour behind a rendered glass glare; treadle rockers at the frame nearest the
  value; OFF units: LED dark, no glow; ON units: lit LED patch.
- **B3-medium.png** (1200 wide): same scene scaled; text rule from 2B (hidden below 12 px effective, tooltip instead).
- **D3-compact.png** (945 wide): art cells in chain order, each a rendered unit sprite on a rendered carpet cell
  background (no vector art).
- **I3-reorder.png** (+3 frames): chain strip drag moves DLY before DST; cables re-route along the floor lanes, plugs
  stay on jacks, nothing swoops.
- **J3-amp.png, K3-rack.png, L3-eq.png, T3-treadle.png**: close-up heroes = frontal renders of the same models with live
  knobs/faders/rocker frame; EQ fader thumbs are rendered sprites moved by QML.
- **M3-families.png** (scratch contact sheet): every family × kind rendered; visibly distinct; originality checklist in
  design.md ticked in `review.md`.
- **O3-states.png** (4 crops): empty (plate + "Elige un slot para ver su cadena" on the wall), loading (default-family
  sprites at 20 % as ghosts), busy (stage 0.6, input off), selection (light pool + chip; no outline drawn on the gear).
Pipeline:
- `blender -b -P tools/render/rig.py -- all` regenerates `app/assets/render/` from scratch with no network access and
  no file outside the repo read (except Blender itself); re-running produces a byte-identical `manifest.json` and images
  within mean |Δ| ≤ 1/255 per channel on the same device.
- `app/assets/render/` total ≤ 12 MB; `plate.jpg` ≤ 700 KB; no single PNG > 600 KB.
- Without `blender` installed the app and `python3 -m unittest discover tests` still work (renders are committed).
Behaviour: every 2B interaction unchanged (click/toggle/double-click/context menu on units, chain-strip drag/keys/menu,
Tab order, knob drag/wheel/keys on stage-hero-face knobs); hit areas come from manifest rects (clicking transparent
sprite areas does not select); images load `asynchronous` (UI thread never blocks > 50 ms; first open of a slot shows
the plate within 300 ms); `GP200_MOTION=0` instant; `GP200_FX=0` changes nothing in the stage (no MultiEffect used).
Real pedal (free slot ≥ 34A): edits on every kind still audible; nothing new sent.

### Constitution change 6 (needs user OK; applied in task 2C.0)
Replace the **gear art** sentence in Look with:
"Gear art = original renders: geometry and procedural materials authored in our own Blender scripts
(`tools/render/`, shader nodes only: no downloaded models, HDRIs, textures, photos, fonts, logos or third-party art),
rendered with Cycles and committed as PNG/JPEG + `manifest.json` in `app/assets/render/`; material base colours come from
`theme.py` (read by the scripts, never duplicated as hex). QML composes the renders and draws only live parts (knob
pointers, LEDs, display text, names, cables, selection light) from `theme` tokens. Blender is a dev tool, not a runtime
dependency. No real brand logos/names/trade dress in art (catalog desc text with ® stays as text). Colourless alpha
tiles from `tools/make_textures.py` remain allowed for QML-drawn surfaces."

### Decisions (2C, user OK 2026-11-25)
- Plan and constitution change 6 approved ("okay").
- Q1–Q5: proposed defaults (frontal camera ~26° down, carpet floor, QML cables with rendered plugs, black cables with state on plug ring, no depth of field).
- Q6: user approves the slice shots before the rest is rendered.
- Blender 5.3.0 installed; OptiX and CUDA devices available (RTX 3060).

### Decisions (2C revision, 2026-11-25)
User on the slice shots (S1-slice, S1-closeup), verbatim: "ha quedado muyy plastico, busca alguna skill para blender,
haz una habitación calida como de madera, con un alfombra como moqueta con colores rojos y negros con tribales o algo,
y upgradea los iconos de cada dispositivo tanto cuando lo escoges como lo que se ve".
Read as (defaults taken, details in design.md "2C revision"):
- Look: de-plastic every material with PBR values from the installed `blender-materials`/`-lighting`/`-rendering` skills
  (their recipes and values only; we keep headless `blender -b -P tools/render/rig.py`, no MCP).
- Room: warm wooden room (vertical plank panelling, plank floor visible around the rug, tungsten practicals 2700–3200 K,
  darker corners). The charcoal carpet floor and slate plaster wall of 2C are dropped.
- Rug: large carpet-like rug under the pedalboard and gear, red + black original geometric/tribal pattern, pile bump + sheen.
- Gear: every device is a rendered model in the scene **and** in the close-up hero (no 2B vector unit left anywhere,
  including PRE, NR, EQ, WAH/VOL treadles, rack units); hero knobs are rendered caps, not flat dots.
- "Iconos de cada dispositivo": chain-strip chips, the close-up effect picker and compact cells show a rendered
  thumbnail of the device (same models) next to the text label; glyphs stay for buttons.
- Cables: natural curves lying on the rug (no right-angle lanes).
- Order: materials + lighting + wood room + rug plate → re-render the 34B slice (checkpoint) → all units → heroes →
  thumbnails → cables. Originality rules unchanged; budget raised to what the full set really needs (≤ 12 MB kept).

### Acceptance — 2C revision (replaces R0-plate / S1-* above; full-2C list below still applies with these changes)
- **R1-plate.png** (`plate.jpg`, 2400×780): wooden room. Back wall of vertical planks (≈ 12 cm wide, V-grooves that catch
  the key light, per-plank tone/grain variation: no two neighbours identical, no visible repeat), a chair rail and a darker
  skirting; plank floor visible in the front corners and along the wall; the rug covers the centre (pedalboard on it, cab
  and rack-stand feet on its back edge). Caged bulb top-left and a shaded floor lamp right make warm pools on the wood;
  corners fall to dark brown but keep grain detail (no pixel < 6/255 in a 64-px corner patch mean, none clipped white
  except the bulbs). Two framed acoustic panels in dark umber cloth. No text, logo, brand.
- **Rug** (in R1): red field + black border/motifs, stepped-diamond medallion + zig-zag border bands (original formula
  in design.md); visible knot/pile texture and abrash (row tone drift); a worn, flatter patch where the player stands;
  bound edge with real thickness. Motifs 12–25 cm (readable at 1.5 px/su). "Guitarra"/"Salida" labels keep ≥ 4.5:1
  contrast against the plate pixels behind them (measured, listed in notes.md).
- **S2-slice.png** (1888×1016, 34B, AMP selected): same units as S1 re-rendered with the new materials: dark tolex with
  pebble grain and rubbed lighter edges, grille cloth darker than its body trim with visible weave and speaker rings
  ghosting through, brushed-metal panel with anisotropic streak, chrome with crisp highlight, knobs with knurl glints,
  screws on panels/corners; no flat single-tone surface larger than a knob. Units not in the slice still show the 2B
  component (last time this is allowed).
- **S2-closeup.png** (AMP close-up mid-drag on Gain): hero rendered at ≥ 2 px per hero px with rendered knob caps (knurl,
  specular ring, pointer line) on the panel; the face's parameter knobs use the same rendered caps; live value arc and
  "Gain 63" bubble unchanged.
- **S2-knob-sheet.png** (scratch): pointer cap at 0/25/50/75/100 %: highlight ring stays put while the line and knurl
  glints rotate with the cap.
- **Checkpoint**: S2 shots go to the user before 2C.9 starts (one look; if no change is asked the round continues).

Full-2C additions/changes:
- **B3-rig.png / B3-rig-alt.png**: zero 2B vector units (grep: no `AmpHead|Cabinet|RackUnit|Treadle|EqBox|Stompbox`
  instance reachable from `SceneUnit.qml`); every `unit_key` that `art_for` can return has a manifest entry (unit test).
- **H3-heroes.png** (scratch contact sheet): a hero for every kind/family (6 heads, 3 cab families, rack, 2 PRE, 4 DST,
  NR, EQ, treadle), each with rendered knob caps / fader thumbs at their live positions.
- **N3-chips.png** (chain strip crop, 34B, DST off): every chip = state dot + device thumbnail + block label; OFF chip
  thumbnail at reduced opacity and label `ink_soft` (state never by colour alone: dot + label tone + "apagado" in the
  accessible name). **P3-picker.png**: AMP effect picker open, each row with the thumbnail of the family that effect maps to.
- **C3-cables.png** (+ 3 reorder frames): cables lie on the rug as smooth curves (no straight lane segments, no right
  angles, no loops in the air), drop from jacks with a short sag, parallel cables fan out instead of stacking; widths and
  contact shadows follow depth; plugs stay on jacks during a reorder.
- Budget: `app/assets/render/` ≤ 12 MB; `plate.jpg` ≤ 700 KB; any PNG ≤ 600 KB; each hero JPEG ≤ 250 KB; each
  thumbnail ≤ 24 KB. Expected total ≈ 8–9 MB (table in design.md).

### Constitution change 7 (needs user OK; applied in task 2C.R1)
Add to the gear-art sentence in Look: "Rendered device thumbnails (same models) may stand next to a block's text label
in chips, pickers and cells; glyph icons stay for buttons." No other rule changes. Separately (a fix, not a change):
`tools/render/models.py` holds loose hex colours (`#c3c9ce`, `#9aa3ab`, `#101112`, `#0b0b0c`, `#16171a`, `#17181a`…),
which the current rule already forbids; they move to `theme.py` tokens.

### Decisions (2C S2 review, user 2026-11-25)
User: "se ve mejor, pero se nota muy plastico, que sea mas rustico todo, y luego, las posiciones de las cosas, algunas se superponen o estan mal, y quiero rehacer los iconos de los pedales y todo eso".
- Direction OK; next round = rustic/aged look everywhere: rough-sawn wood with knots, dust, scuffs; tolex scuffs and worn corners; dulled/pitted chrome, tarnish on brass/copper; chipped paint on pedal edges; rug pile irregularity and wear; grime in crevices. Lower specular overall; no clear-coat anywhere.
- Layout: nothing may overlap (stage units, rack, cables' plugs, labels Guitarra/Salida); every unit sits in a manifest zone; a test asserts no zone/rect intersections and all rects inside the stage.
- Redo the pedal/device visuals: every unit rendered (2C.9–2C.12), no vector unit left; rendered thumbnails for chips/cells. Constitution change 7 approved by "quiero rehacer los iconos de los pedales" (thumbnails next to the always-visible text label).

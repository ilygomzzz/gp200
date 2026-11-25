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

## Phase 2 — polish + rig scene (rewritten 2026-11-25 from `polish.md`; user decisions in spec.md)
Shots use the fake pedal with realistic values (e.g. Gain 55, Tone 40, Volume 70), offscreen, `GP200_FX=0`.

### Part A — quick touches (they survive inside the scene)
- [x] 2.A1 **Tokens** — `app/theme.py` + `qml_tokens()`: `face_hi face_lo nameplate led_off track_on_face tick
  knob_face face_max_h r_unit track_code` (values in polish.md); `font_desc` aliased to `font_small`; radius
  literals 10/14/16/18 in `app/qml` → `r_unit`/`r_tile`/`r_pill`. Done: token test lists them; contrast of each
  block colour on `nameplate` (all ≥ 4.5) pasted in `notes.md`; `grep -nE 'radius: (10|14|16|18)\b' app/qml` empty.
- [x] 2.A2 **Stompbox** — `Stompbox.qml`, `Led.qml`, `Unit.qml`: nameplate band, enamel overlay, filled LED lens,
  footswitch 24. Done: B1-polish shot.
- [x] 2.A3 **Close-up face** — `CloseUp.qml`, `ValuePopup.qml`, `Knob.qml`: face capped at `face_max_h`, knob row
  centred at `knob_face`, popup as overlay (no `topPadding`), LED + switch + "Encendido"/"Apagado" bottom-centre.
  Done: C1-polish shot; turning a knob shows the bubble; Space/click on the switch toggles.
- [x] 2.A4 **Picker nameplate** — `CloseUp.qml`: styled editable ComboBox (contentItem, popup, indicator) holding
  name + description. Done: C1-polish shows no Basic field; type + Enter still sets the effect (existing test).
- [x] 2.A5 **Knob on face** — `Knob.qml` `onFace`: `track_on_face` track, white arc 4 px, 11 printed ticks, value
  chip. Done: C2-arc shot.
- [x] 2.A6 **Static skeleton + small fixes (trivial)** — `SlotGrid.qml` "…" → static skeleton bar; `StatusPill.qml`
  icon hidden when text empty. Done: A1 re-shot has no icon-only pill.

### Part B — rig scene (≥ 1100 px; art cells below)
- [x] 2.0 **Constitution + textures** — apply "Constitution change 5" (spec.md) to `constitution.md`;
  `tools/make_textures.py` (numpy, fixed seed) → `app/assets/textures/` `tolex powder brushed grille_weave tread
  stage_mat shadow_contact spot` (colourless alpha PNG, tileable, < 200 KB total). Done: test = deterministic
  hash per file + seamless edges (first/last column and row match within 1 level); constitution diff matches.
- [x] 2.1 **Art mapping** — `app/art.py` `art_for(block, name, desc)` → `{kind, family, speakers}`; tests: TS-808 →
  `od_green`, "Marshall® JCM800" → `brit_gold`, "Fender® Tweed Deluxe" → `tweed`, 4x12 cab → speakers 4, unknown →
  block default, every catalog effect maps to a family with tokens.
- [x] 2.2 **Tokens** — `theme.chassis` families + knob variants + stage tokens (`stage_wall stage_wall_hi stage_mat
  stage_horizon board_tolex rail tex_* stage_w stage_h chip_h`); contrast of each `ink` on body/face in `notes.md`.
- [x] 2.3 **Stage** — `Stage.qml` (wall, stage mat, horizon, spotlight, contact shadows, zone layout by kind,
  uniform scale to board width, labels hidden below 12 px effective) replaces the unit row in `Pedalboard.qml`
  for ≥ 1100 px; `bridge.py` units gain `kind`, `family`. Done: B2-rig, B2-medium shots (with placeholder boxes per
  kind until 2.4–2.6 land).
- [x] 2.4 **Amp stack** — `AmpHead.qml` (tolex + texture, panel, knobs, pilot jewel), `Cabinet.qml` (grille
  weave, piping, cone count, "4x12" print). Done: B2-rig shows head on cab; J2-amp shot.
- [x] 2.5 **Rack** — `RackUnit.qml` (brushed 1U, ears, display with 2 values in block colour, 3 knobs) in a rack
  case on a stand. Done: K2-rack shot ("500 ms · Mix 35").
- [x] 2.6 **Floor units** — pedalboard (tolex board + rails) with `Stompbox.qml` (from 2.A2, family colours,
  powder texture), NR mini, EQ with `Fader.qml` (Knob's input rules, role Slider), `Treadle.qml` (WAH/VOL, rocker
  angle = value, toe LED). Done: L2-eq shot; fader test like 1.9.
- [x] 2.7 **Cables + chain strip** — cables in chain order between unit jack points, following animated items,
  OFF segments dark (absorbs polish item 6); `ChainStrip.qml` with Unit's input code (drag, Ctrl+←/→, Space,
  Enter, context menu), Tab order = chain order, selection syncs scene ↔ chip ↔ close-up (spotlight + 4 px lift).
  Done: I2-reorder shot + 3 frame grabs mid-reorder; existing reorder tests pass.
- [x] 2.8 **Compact art cells** — < 1100 px: chain-order cells drawing each block as its kind at cell size.
  Done: D2-compact shot; resize 1888 → 945 → 1888 switches cleanly.
- [x] 2.9 **Close-up faces** — `app/qml/faces/` reuse the 2.4–2.6 components at larger size (no second drawing).
  Done: J2, K2, L2 from the same components; effect change switches family.
- [ ] 2.10 **Art audit** — M2-families grid (family × kind); no logo/brand/copied silhouette; no tile seams;
  `GP200_FX=0` renders everything. Real-pedal smoke on a free slot ≥ 34A: edits on every kind still audible.

### Later polish (not in phase 2 unless trivial while touching the file)
- Selection caret on the close-up pointing at the selected unit (polish item 5).
- Header: "Guardado en 34B" chip when clean, actions only when dirty (item 8).
- Status pill left-aligned at content width (item 9); busy line naming the operation (item 12).
- Empty board with ghost units + shortcuts hint in the close-up area (item 10).
- Slot card hierarchy: code dim, name 14 px one line (item 11).
- Drop `font_desc`, DemiBold instead of bold everywhere (item 7 remainder); dock/drawer size tokens.

## Phase 2C — rendered rig (draft; waits for the user's OK on spec.md "Phase 2C" + constitution change 6)
Supersedes 2.3–2.9 art (not their logic). Renders on the user's PC with `blender` (pacman); the implementer runs
Blender headless only, never edits `.blend` files by hand (there are none: scripts build the scene each run).
Slice first: 2C.0–2C.8 end in a **user review gate**; nothing after 2C.8 starts before the user approves the S-shots.

### Slice (room + amp head + cab + one stompbox + one knob type + cables)
- [ ] 2C.0 **Constitution + docs** — `constitution.md` change 6 (spec.md wording), `CLAUDE.md` layout line
  (`tools/render/`, `app/assets/render/`, Blender = dev tool), project `mapa/` note. Done: diff matches spec wording.
- [ ] 2C.1 **Palette + manifest validation (pure)** — `tools/render/palette.py` (ast read of `app/theme.py`, hex→linear,
  `validate_manifest`). Done: `tests/test_render.py` (stdlib only): palette has every `theme.chassis` family and block
  colour; hex→linear of `#808080` ≈ 0.216; manifest validator rejects `../x.png`, `a/b.png`, missing keys.
- [ ] 2C.2 **Harness + materials** — `tools/render/rig.py` (args after `--`, device pick OPTIX>CUDA>CPU / `--cpu`, seed
  200, AgX, samples, OIDN, crop-to-alpha, manifest merge sorted), `tools/render/materials.py` (all recipes in design.md).
  Done: `blender -b -P tools/render/rig.py -- matsheet` writes a scratch sheet of spheres/tiles (not committed) and prints
  `blender --version` + device + time; shown in the report.
- [ ] 2C.3 **Room plate** — `rig.py plate`: room, pedalboard, empty rack case + stand, lights, camera solved to horizon
  ≈ 302 su; `plate.jpg` 2400×780 + `cell_bg.jpg` + manifest `camera`, `lanes`, `cable_w`. Done: R0-plate shot; ≤ 700 KB;
  render time logged in `notes.md`.
- [ ] 2C.4 **Slice gear** — `tools/render/models.py` head, cabinet, stompbox, plugs; `rig.py slice` renders 34B's
  families (AMP Silver Twin → `art_for` family, CAB Dark Twin family + speakers, DST Lazaro family) as in-place sprites
  with shadow-catcher room, lit patches, frontal heroes, anchors; plugs straight/right-angle L/R. Done: sprites
  composited over the plate in a scratch script line up (no halo, shadows meet the floor); files within budget.
- [ ] 2C.5 **Knob type `pointer`** — `rig.py knob pointer`: cap/mark/light/shadow layers per needed cap colour, signed
  alpha light layer. Done: S1-knob-sheet (5 angles) shows fixed highlight, turning pointer, no edge halo.
- [ ] 2C.6 **Loader** — `app/art.py` `load_manifest`, `unit_key`; `gp200_app.py` context property `R`; `bridge.py`
  unit dicts gain `key`; `theme.py` tokens `render_dir sel_pool cable_hi cable_shadow ghost_op` in `qml_tokens()`.
  Done: tests (valid manifest, missing file → `{}`, path traversal rejected, key for each kind) in `tests/test_bridge.py`.
- [ ] 2C.7 **Composition** — `Stage.qml` (plate image, selection light pool, no lift), new `RenderUnit.qml` (sprite, name
  in perspective, knob marks, lit patches, hit rects), `SceneUnit.qml` (RenderUnit when `R.units[key]`, else 2B
  component), `Knob.qml` `sprite` mode, `faces/Hero.qml` (rendered hero + live knobs). Done: S1-slice and S1-closeup
  shots; QML smoke test loads with an empty and with the slice manifest, 0 warnings.
- [ ] 2C.8 **Cables v2** — `Wire.qml` (depth width, 3-stroke shading, lanes + rounded corners, patch drops, plug sprites,
  boot ring state), `Stage.qml` z order from design.md. Done: S1-slice cables; I3-style 3 frames of a reorder;
  **STOP: report S-shots + render times to the coordinator for the user's review (Decisions Q1–Q6).**

### Rest (after the user's OK on the slice)
- [ ] 2C.9 **All gear** — remaining head families, cab 3×3, rack case units MOD/DLY/RVB + `rack_glare.png`, PRE ×2, DST ×4,
  NR, EQ + `fader_thumb.png`, treadles WAH/VOL × 9 frames; heroes for each. Done: M3-families contact sheet; budget met.
- [ ] 2C.10 **Knob types** — `skirted`, `chicken`, `rack` (+ cap colours per family table). Done: knob sheet per type.
- [ ] 2C.11 **Live parts on every kind** — `RenderUnit.qml`: rack display text under glare, EQ thumbs, treadle frame swap,
  lit patches for every LED/jewel; EQ close-up fader bank uses the rendered thumb (`Fader.qml` sprite mode). Done:
  B3-rig, B3-rig-alt, K3, L3, T3, J3 shots.
- [ ] 2C.12 **Compact cells** — `ArtCell.qml`: `cell_bg.jpg` + RenderUnit at cell scale. Done: D3-compact; resize
  1888 → 945 → 1888 clean.
- [ ] 2C.13 **Remove vector gear** — delete the 2B drawings no longer reached (`AmpHead.qml`, `Cabinet.qml`, `RackUnit.qml`,
  `Treadle.qml`, `EqBox.qml`, Shapes parts of `Stompbox.qml`/`Body.qml` if unused, unused textures in
  `app/assets/textures/` and their generator code/tests); grep proves no references. Done: tests green, B3/D3 retaken
  unchanged.
- [ ] 2C.14 **Audit** — determinism (two `all` runs: manifest identical, images mean |Δ| ≤ 1/255), size budget, originality
  checklist from design.md ticked in `review.md`, O3-states, B3-medium; `GP200_FX=0` identical; real-pedal smoke on a
  free slot ≥ 34A (edits on every kind audible, nothing new sent).

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

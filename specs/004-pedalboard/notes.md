# 004 notes

## 1.2 Rendering spike (offscreen, Qt 6.12, `QT_QPA_PLATFORM=offscreen`)
- `QtQuick.Shapes` (arcs, dashed knurl, cables, radial gradient) render and `grabWindow()` works.
- `layer.effect: MultiEffect` (shadow, LED glow) does NOT render offscreen: the layered item vanishes.
  Shots therefore run with `GP200_FX=0` (token `T.fx`, disables the layers; the app default is on).
  Real-window rendering of MultiEffect was not checked (opening a window on the live desktop was not allowed here).
- Python needs `from PyQt6 import QtQuick` imported before loading QML, or Qt aborts.

## Review fixes
- One row at wide: jacks are 40 px cells, gap 8, whole board scaled uniformly (`Pedalboard.sc`, min 0.87 = ~80 px cells) so 11 units + 2 jacks fit (1184 px board -> 0.97). Below that the board wraps as before.
- Drawers use `Qt.alpha(T.popup_bg, 1)` (opaque); drop bar has z 20 above the lifted unit; QML teardown null reads guarded.

## Phase 2 part A (2.A1-2.A6)
Contrast of block colour on `nameplate` (90 % over the face tint; asserted >= 4.5 in tests/test_app.py):
PRE 9.04, WAH 6.47, DST 6.08, AMP 8.26, NR 6.27, CAB 5.23, EQ 8.23, MOD 5.84, DLY 7.21, RVB 5.45, VOL 9.37.
Deviations:
- `face_max_h` 296 -> 344: picker plate is 60 tall (name + desc) and the switch sits inside the face; 296 clipped the knob chips (checked in shot).
- Face is top-aligned in a ColumnLayout with no trailing spacer (a fillHeight spacer split the free height 50/50 with the face).
- StatusPill hides entirely when text is empty (not just the icon); `font_desc` aliased to `font_small` (12).
- Knob ticks: strokeWidth 5 radial, 2 px dash; knob cell pad 28 when `onFace`; >8 knobs use `knob_big`.
- Footswitch gained Tab focus + Space (interactive only) so Space toggles in the close-up.
- Shots need a ~600 ms settle before grabbing, else the board wraps VOL to a second row (timing artefact of the script).
- Review fixes: Knob MouseArea `preventStealing`; close-up Flickable `interactive` only on overflow, `minimumHeight` 148 (row never clipped, page scrolls instead), no spacing for empty ParamPills. C1-polish is now a close-up crop; C2-arc-turning shows a drag (row stays put); R2-compact-945 retaken at 945x800.

## Phase 2 part B (implementer)
- Done: 2.0-2.9. Shots (shots/): B2-rig, B2-medium, D2-compact, I2-reorder (+ -0/-1/-2 frames), J2-amp, K2-rack, L2-eq, M2-families,
  resize-945 / resize-1888 (resize 1888 -> 945 -> 1888 clean, 0 QML warnings). Tests: 40 OK (rack_display + unit_view art fields added).
- Look fixes after review: deck = dark ribbed `tread` at 0.14 (was tolex camo), mat darker/calmer, tolex retuned to a fine pebbled grain,
  warm key-light wall gradient, stage_h 480 -> 520, back line x1.15, cables z 7 (above deck, behind back-line units and in front
  of floor units so they plug in) so they no longer cross cab/rack faces, rack display "500 ms | 30".
- 2.9: `qml/faces/Hero.qml` shows the head/cab/rack/treadle component enlarged left of the knobs when the close-up is >= 1000 px
  wide; EQ close-up uses a Fader bank (labels are the catalog frequency names). Stompbox kinds have no hero (the face is the pedal).
- 2.10 open: M2 grid + FX=0 done; no real-pedal smoke (coordinator/user). Ink-on-body contrast per family not audited
  (amp head "Tweedy" name on the silver plate is low contrast).
- Deviations: tweed/blackface rule split; NR = scaled Stompbox; fuzz wedge top omitted; texture insets approximate rounded corners;
  M2 grid draws every kind through ArtCell (compact art) at 2.2x, not through the stage.

### Part B review fixes (implementer)
- F1: ChainStrip release now resets `dropGap` before `board.moveTo` (the delegate is destroyed by the move). Verified with a QTest mouse drag
  (AMP chip to the front: order changed, 0 warnings; shot I2-reorder-drag).
- F2: shot fixture (scratchpad script, not the test fake) feeds realistic params (Gain 55, Time 500, Mix 35, EQ bands varied, treadle 60);
  rack display is "500 ms · Mix 35" again (font fits horizontally, min 8 px). B2-rig, B2-medium, J2-amp, K2-rack, L2-eq, D2-compact retaken.
- F3: `art_for` returns `cone`; the cab prints "NxM" from the desc (1x6), placed below the piping between the feet.
- Selection cue: lift 8 su, accent rim light, spotlight opacity 0.3. Amp nameplate: 16 px, no OFF dimming, knobs moved down, ink/face
  contrast >= 4.5 per head family (unit test in test_art.py; copper is the lowest at 4.95).

## Phase 2C slice (implementer)
- Renders (Blender 5.3.0, OPTIX, RTX 3060, seed 200): plate 2400x780 at 256 samples 26 s (165 KB) + cell_bg; slice (3 sprites + hero + lit patches + knob layers + 4 plugs) 74 s at 128 samples; knob job 3 s. `app/assets/render/` is 1.4 MB. Shots in `shots/`: S1-slice, S1-closeup (full window), S1-knob-sheet. R0-plate: view `app/assets/render/plate.jpg` (not copied to shots; plate was only checked via previews and the composite).
- Deviations: art-directed camera (f 18 mm, cam (0,-1.2,0.6), pitch 7 deg, wall y 1.3, board front at v=500, horizon lands at 307 su vs design 302), pedals x1.7 w/d x1.3 h; manifest `zones` (fallback slots for non-rendered units, incl. AMP/CAB); `rect`s absolute stage units; head knobs use `pointer_alu`; knurl via bump; hero is a JPEG with live knobs/LED; `KnobSprite.qml` is a separate component instead of a `Knob.qml` sprite mode (smaller); `palette.validate_manifest` reuses `art.manifest_errors`; plug scale 0.34 su/px approximate; wall/carpet colours are theme tokens lifted in linear space.
- Known weak spots for the review: knob caps are flat grey (dome light 0.5), cab cloth is bland and too bright, non-slice units are still the 2B vector art (visible style clash, expected until 2C.9), the DST name is nearly unreadable (squashed), cables v2 lanes are crowded (long drops from the back-line gear to a lane at y~506; plugs are straight sprites only), lit patches for the hero jewel are a loose threshold, no boot-ring state, `test_app` smoke now loads the slice manifest (empty manifest checked by shot script: 0 warnings).
- Unverified: real-pedal untouched (offscreen only); the I3-style reorder frames of 2C.8 were not taken; R0-plate shot not taken separately.

## 2C revision R1-R5 (implementer, S2 checkpoint)
- Exposure metered on the rug right of the board: mean lum 0.293 at EV0 -> exposure -2.1 (manifest camera.exposure; target 0.07, lowered from the design's number by eye because 0.12/0.09 washed the rug to salmon). Plate lum centre/corner (post vig): 0.102 / 0.001 top-left, 0.008 bottom-right.
- Times (RTX 3060, OPTIX): plate 256 spl 33 s (240 KB); slice jobs 128 spl ~67 s (cab 13 s, amp 7 s, dst 6 s, hero 2x 9 s + lit 9 s); knob job ~3 s; matsheet preview 80 s. app/assets/render 1.4 MB.
- Label contrast vs plate crop: Guitarra 12.4:1, Salida 10.2:1 (T.dim).
- Deviations: METER_TARGET 0.07; rim spot 18 W and key spot angle tuned by eye; rug sheen tint/weight reduced (washed out under key). Hero lights kept at S1 wattages, kelvin changed to 3200/3000. Knob in CloseUp: `Knob.sprite` property overlays a KnobSprite (type pointer_alu) on the drawn cap; the arc/ticks stay vector. Constitution change 7 NOT applied (awaiting user OK).
- Weak spots: amp head and cab read flat/beige-brown (tolex/cloth too uniform under warm light), CloseUp knob caps look near-white on the gold face, rack case dark and empty, rug pattern visibly stepped (pixel-like triangles). Hero only checked via the window shot.
- Shots: S2-slice, S2-closeup (=full window), S2-knob-sheet. Pedal untouched.

## 2C S3 (rustic pass + layout + all units) — partial
- Done: rustic materials (tolex/cloth/brushed/chrome/powder/wood/rug rewritten, no clear coat; rug K=3000 anti-aliased), warm dim world, camera F=16 / cz 0.65 / pitch 6, `layout_zones()` (zones derived from world footprints; AMP clamped under CAB; pedal gap 0.045 m), manifest `jacks` + `labels` read by Stage.qml, RenderUnit frames (treadle, 5 not 9) + rack display text overlay, jobs `plate|knob|units|sheet|all`. 28 unit sprites + 14 knob types (`pointer_*`, `skirted_*`, `chicken_*`, `rack_rack_dark`), assets 5.0 MB, `all` = 3 min 24 s. New tests: Layout (zones/labels disjoint + inside stage, unit keys). 53 tests OK.
- Deviations: treadles 5 frames; zone = front-edge footprint (stacked gear bboxes necessarily overlap); sprites exclude baked knobs/kring (QML KnobSprite draws them); cab heights equalised so the head sits at one spot.
- NOT done: 2C.11 heroes (CloseUp still shows the 2B vector Hero), 2C.12 thumbnails + constitution change 7, 2C.13 cables v3, 2C.14 vector removal.
- Known weak spots (S3-slice): stompbox / head / rack KnobSprites are mispositioned (stomp knobs float above the back edge: `stomp_info` knob coords wrong) and read as white blobs; cab grille is flat, speaker shapes not visible; names on stomp labels misaligned; old Wire routes through units; wall still reads slightly repetitive.
- Shots: S3-slice, S3-window (stage + old CloseUp). S3-closeup-per-kind and S3-compact NOT taken.

## 2C S3 continuation (implementer, second pass)
Done: knobs baked into sprites + QML pointer overlay (markOnly); cab cloth with cone shading; heroes for every kind + thumbs (downscaled from hero, not 3/4 renders; HERO_HS 630/420/1260, HERO_PX_SU 1.4 to keep assets at 11.0 MB); thumbs in chips, picker header and ArtCell (picker rows not thumbnailed); cable_path (pure, tested) wired through Board.cable; vector Loader/AmpHead/Cabinet/RackUnit/Treadle/EqBox removed (Body/Stompbox/Led/Tex remain: ghost units, close-up fader/led, stage dressing).
Open (seen in S3 shots): stompbox name labels still overlap the knob row; hero name text is elided ("Laz..."); cab cones not clearly visible in the stage crop; cables still pass behind cab/rack legs (rect list from QML does not include stand legs); 2C.11, 2C.13, 2C.14 left unticked.
Third pass: stompbox/mini/EQ stage name labels dropped (name lives in chips + close-up hero; hero name now Text.Fit); rack stand footprint added to cable obstacles (Stage.allRects) and rug lane moved to y 496-508; picker rows show per-effect thumbs (Board.effectKeys); close-up hero stays small (row min height 148: raising it pushed the footswitch out of the 338 px panel). Still open: cables from the rack columns and from pedal bottoms cross the treadles/board front (2C.13 unticked), Body/Stompbox/Led/Tex vector parts kept (2C.14 unticked).

## Deviation decided by the lead: simplified cables (2C.13)
Cables are no longer a faithful wiring diagram (chain order is still the strip's). Stage.cablePts: Guitarra to first unit and last unit to Salida run on the rug (dropped if they would cross a unit); floor-to-floor couplers only between neighbouring floor units (gap < 40 su, left to right); every cable touching the amp or rack is drawn short and behind the units, from a floor unit's back edge up. Dropped: floor-to-floor cables between non-adjacent units (e.g. PRE to WAH when other pedals sit between) and right-to-left couplers; any visible Guitarra/Salida cable that would cross a unit. `art.cable_path` lane -1 = drop if blocked (tested). 2C.14 ticked: vector gear files removed; Body/Stompbox/Led/Tex stay as ghost/close-up/stage dressing parts.

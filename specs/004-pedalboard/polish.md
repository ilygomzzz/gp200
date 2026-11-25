# 004 polish — UI/UX audit of phase 1 (commit 8f567b2)

Scope: Qt Quick view (`app/qml/*.qml`, `app/theme.py`, `app/bridge.py`), shots in `shots/` (offscreen, `GP200_FX=0`:
no shadows/glow, so depth is judged without them, which is also what the opaque fallback looks like with FX on a weak GPU).
The live window (class `gp200`, ws 4) was not on the visible workspace, so no live capture was taken; nothing was clicked.

Context assumed: desktop Linux, 945–1888 px wide windows, ~60 cm viewing distance, mouse + keyboard, Spanish UI,
no RTL. Design system = own glass tokens in `theme.py` (Basic style restyled).

## Diagnosis in one paragraph

The structure is right (board on top, close-up below, slots left, chat right) and the stompboxes already read as
gear. What makes it feel "cheap" is not missing features, it is **finish**: (1) large flat fields of a mid-tone
block colour (the close-up is a 1160x620 px slab of `#9c7c44` holding three knobs in the top-left corner),
(2) default-looking controls dropped onto the art (the black editable ComboBox, outline pills, an unlabeled
footswitch floating at the far right), (3) weak hierarchy on the units (12 px dark text on mid-tone faces, a
grey outline LED that disappears, 8 px cables you cannot see), and (4) seven different corner radii and five font
sizes 12/13/14/18/24 that are too close to tell apart. Real gear and pro plugin UIs feel expensive because every
surface is lit (a top highlight, a bottom shade), every print is crisp and high contrast, and controls are composed
around a centre, not flowed from the top-left. The fixes below are mostly that.

Measured contrast (WCAG, `ink_dark #14171a` on the stompbox face = `Qt.tint(chassis_base, block colour @ 0.6)`),
needed 4.5:1 for 12 px text:

| Block | Face | ink_dark on face | block colour on ink_dark band |
|---|---|---|---|
| PRE | #90884d | 5.0 | 10.2 |
| WAH | #896f53 | **3.8** | 7.1 |
| DST | #976445 | **3.6** | 6.6 |
| AMP | #9c7c44 | 4.6 | 9.2 |
| NR  | #677581 | **3.8** | 6.9 |
| CAB | #74675e | **3.3** | 5.7 |
| EQ  | #5d8b7b | 4.7 | 9.2 |
| MOD | #76669c | **3.6** | 6.4 |
| DLY | #4a8196 | **4.2** | 8.0 |
| RVB | #536b9c | **3.4** | 5.9 |
| VOL | #7d8d91 | 5.2 | 10.6 |

7 of 11 faces fail (WCAG Critical). The close-up uses the same face colour for its 13 px description and knob
labels, so the same blocks fail there. Inverting the print (block colour on a dark nameplate) passes for every
block (5.7–10.6) and is the fix used in item 2.

## Proposed new tokens (`theme.py`, exported in `qml_tokens()`)

All are fixed literals, so the "colours only from tokens" rule holds; no derived `Qt.lighter/darker` needed.

| Token | Value | Use |
|---|---|---|
| `face_hi` | `#1fffffff` | top half of the enamel gradient overlay (stompbox body, close-up face) |
| `face_lo` | `#2e000000` | bottom of the enamel gradient overlay |
| `nameplate` | `#e614171a` | dark print band on stompbox and close-up face |
| `led_off` | `#73000000` | unlit LED lens (filled, not outlined) |
| `track_on_face` | `#4d14171a` | knob arc track when the knob sits on a coloured face |
| `tick` | `#9914171a` | printed scale ticks around close-up knobs |
| `knob_face` | 72 | close-up knob diameter (was `knob_big` 64, keep 64 for >8 knobs) |
| `face_max_h` | 296 | max height of the close-up face (header 56 + knobs 160 + pills 48 + 2x16 pad) |
| `r_unit` | 12 | stompbox body + selection ring (replaces literals 10 and 14) |
| `track_code` | 1.2 | `font.letterSpacing` for silkscreen codes (PRE, AMP…) |

Radii after cleanup: `r_card 8` (slot cards, popups' inner), `r_unit 12`/`r_tile 12` (units, tiles, bars),
`r_plate 20` (plates), `r_pill` (anything 32 px high: buttons, fields, ComboBoxes). Literals 10, 14, 16, 18 go.

Type scale after cleanup (ratio ~1.29, four steps, `font_desc` 13 folded into 12 or 14):
`font_small 12` captions/codes, `font_body 14` body/labels, `font_title 18` close-up effect name, `font_display 24`
preset name and value popup. Weights: Regular body, DemiBold (`Font.DemiBold`) for codes and titles instead of
`bold` everywhere.

---

## #1 (user's top priority) — The rig scene

User, verbatim: "que esto tenga como si se viese una pedalera/habitación con, en vez de icono, un dibujo del pedal
o del ampli, muy rollo AmpliTube". Everything in section A is finish; this is the identity. It replaces the
"row of same-size tiles" idea of phase 2 (`design.md` cells 92x144) with a **stage**: a room corner with an amp
stack and a rack on the back line, a pedalboard on the floor in front, real patch cables between them.

### What wrong looks like today
Board = a horizontal strip of 76x104 coloured rectangles with an icon-font glyph; every block, from a wah to a
4x12 cab, has the same shape. It reads as a flow diagram coloured like pedals, not as gear.

### Scene composition (flat-front 2.5D, one key light)
- **View**: flat-front orthographic (no real perspective: hit-testing, drag and focus rings stay rectangular and
  exact). Depth comes from three cues only: two depth rows (back line 1.0, floor row in front and lower), contact
  shadows on the floor, and a floor plane drawn as a trapezoid gradient.
- **Backdrop** (inside the board plate, not the window — glass rule intact): a dark wall (`stage_wall`) with a very
  soft vertical light falloff and a floor (`stage_mat`, rubber stage mat — user decision) meeting at a horizon
  line ~58 % down the stage. One key light top-left: every gradient on every unit highlights top-left / shades
  bottom-right; one soft spotlight ellipse (alpha PNG) behind the amp stack.
- **Zones** (positions by *kind*, not by chain index):
  - Back line left→right: **amp stack** (AMP head on CAB), **rack case** (MOD / DLY / RVB as three 1U units,
    plus NR as a 1U gate if wanted) on a short stand.
  - Floor: a **pedalboard** (tolex-covered board with two aluminium rails) holding PRE, DST, NR (mini), EQ
    (fader pedal) as stompboxes, and WAH + VOL as treadles at the right end, where feet go.
  - Jacks: "Guitarra" cable enters from the floor's left edge; "Salida" leaves the amp head's back.
- **Signal order is still the truth**: since units no longer sit in chain order, the order is shown twice:
  (1) patch cables are drawn in chain order between the units' real jacks (board→rack→amp, wherever the order
  sends them), lit per block colour; (2) a slim **chain strip** under the stage: 11 chips (glyph + code, block
  colour, 32 px high) in chain order — this is where reorder lives (drag a chip, Ctrl+←/→, context menu, as
  today's units). Clicking a unit in the scene or a chip selects the same block. This is AmpliTube's own pattern
  (stage + chain strip) and keeps the constitution's "drag = keyboard = menu" rule.

### Mockup (wide, stage 1184x420 inside the board plate; close-up below unchanged by this item)
```
+-----------------------------------------------------------------------------------------------------+
|  wall (stage_wall, light falloff from top-left)            .  spot  .                               |
|                                                        .'            '.                             |
|        +=====================+                      +-------------------+     +------------------+  |
|        | [o o o o o o]  (*)  |  AMP head 280x96     |  .-.            * |     | MOD  [ 0.8 | 52 ]|  |
|        |  ~nameplate~        |  brushed panel,       |  ( ) chorus  o o |     |  o   o   o    *  |  |  rack 1U x3
|        +=====================+  tolex sides          +-------------------+     | DLY  [ 500 | 30 ]|  |  220x40 each
|        |#####################|                                               |  o   o   o    *  |  |  displays in
|        |##  (  )    (  )   ##|  CAB 280x200          (amp stack shadow)      | RVB  [ 2.4 | 25 ]|  |  block colour
|        |##  (  )    (  )   ##|  grille cloth + cones                         |  o   o   o    *  |  |
|        |#####################|  "4x12" small print                          +------------------+  |
| ======='=====================' ============ horizon ======================== '====[stand]=====' ==== |
|   floor (wood/mat texture, darker toward the viewer)                                                |
|  Guitarra  +------------------------------------------------------------------------------------+   |
|   ==o~~~~~>| [PRE ] [DST ] [NR] [EQ |||] ~~~~~~~~~~~~~~~~~~~~~~~~ [ WAH  /] [ VOL  /]          |   |
|            |  76x104 76x104 64x80 76x104                         treadles 72x112, toe LED      |   |
|            +===================================== rails ==========================================+   |
+-----------------------------------------------------------------------------------------------------+
| chain:  (PRE)(WAH)(DST)(AMP)(NR)(CAB)(EQ)(MOD)(DLY)(RVB)(VOL)   <- 32 px chips, drag/keys reorder   |
+-----------------------------------------------------------------------------------------------------+
cables (~) run in chain order between unit jacks; a block that is OFF has a dark cable segment and dark LED.
```

### How each kind is drawn

| Kind (blocks) | Silhouette / parts | Materials | Live parts (QML) |
|---|---|---|---|
| stompbox (PRE, DST, NR mini, EQ) | die-cast box, rounded 10, chamfered top edge, 2–4 knobs, footswitch, LED, side jacks | powder coat (family colour + noise + enamel gradient), screen-print nameplate (item 2) | mini knobs, LED, switch |
| EQ variant | stompbox with 5 mini faders instead of knobs | same | fader thumbs show the 5 band values |
| treadle (WAH, VOL) | rocker plate on a base, seen front-on with 8° skew, rubber tread | rubber texture (`tread.png`), chrome base | toe LED; rocker angle = Position/Volume value |
| amp head (AMP) | box with rounded tolex corners, brushed/gold control panel, chicken-head or skirted knobs, pilot jewel | tolex texture, brushed metal or gold panel, piping line | knobs (first 6 params), jewel |
| cabinet (CAB) | box, grille cloth frame, piping, speaker count from desc (cones as faint circles behind the cloth) | grille cloth weave (`grille_*.png`, wheat/silver/black), tolex | none (Low/High cut only in close-up) |
| rack 1U (MOD, DLY, RVB) | 19" face, ears with 4 screw holes, a display, 3 knobs | brushed anodised alu, recessed display glass | display shows 2 values in block colour; knobs |

### Rendering technique — evaluated

| Option | Quality ceiling | Cost | Recolour per family from tokens | Verdict |
|---|---|---|---|---|
| A. Pure `QtQuick.Shapes` + gradients (today) | clean flat-vector look; no texture (tolex, cloth, brushed metal need hundreds of paths or none) | low per unit, but every material is an approximation | yes, trivially | good for knobs/LEDs/switches/displays; not enough for "AmpliTube" |
| B. Full pre-rendered PNG art per unit and family | highest (can be painted) | high, needs an artist; 2x/3x sizes; ~20 families x 6 kinds | no (one image per colour) | rejected: cannot recolour, heavy, and we cannot author painted art well |
| C. Authored SVG silhouettes (SVG Tiny 1.2: paths, linear/radial gradients) via `Image { sourceSize }` | good vector quality, crisp at any scale | medium (we write them) | only by shipping variants — Qt SVG ignores CSS vars | partial: fine for fixed parts (rack ears, cab piping, chrome jacks) |
| **D. Hybrid (recommended)**: Shapes for geometry + token colour; **colourless alpha material tiles** (PNG, 128–256 px, tileable, generated by our own script) laid over the token colour with `Image { fillMode: Image.Tile }`; pre-blurred contact-shadow and spotlight PNGs; Shapes for every live part | close to plugin look: real tolex grain, cloth weave, brushed streaks, soft shadows without `MultiEffect` (works with `GP200_FX=0` and offscreen) | medium: one generator `tools/make_textures.py` (numpy noise → PNG; deterministic seed), ~8 tiles < 200 KB total | yes: colour = token `Rectangle`/`ShapePath`, texture = white/black alpha only | **choose D** |

Note: Qt SVG supports SVG Tiny 1.2 only (no `<filter>`, no `<pattern>`, no feTurbulence), which is why textures are
generated PNG tiles, not SVG. Materials to generate: `tolex` (pebbled noise), `grille_weave` (2-axis thread
pattern), `brushed` (horizontal streak noise), `powder` (fine speckle), `tread` (rubber ribs), `floor_wood`
(planks + grain) or `floor_mat`, `shadow_contact` (blurred ellipse), `spot` (radial falloff). Kept in
`app/assets/textures/`, loaded once, `cache: true`, `smooth: true`, `mipmap: true` where scaled.

### New tokens (on top of the table above)
`stage_wall #0c121a`, `stage_mat #17191c`, `stage_horizon 0.58` (fraction), `board_tolex #1c1d20`,
`rail #8c949b`, `light_dir` = top-left (documentation only), texture opacities `tex_tolex 0.35`,
`tex_grille 0.55`, `tex_brushed 0.25`, `tex_powder 0.12`, `tex_floor 0.4`; stage reference size
`stage_w 1600`, `stage_h 480`, `chip_h 32`. Families stay as in `design.md` `chassis` (body/face/ink/knob).

### Scaling (wide / medium / compact)
- The stage is authored at 1600x480 reference units and scaled uniformly to the board width (same `fit` idea as
  today; `scale` on one `Item`, text inside stays ≥ 12 px effective → effect-name labels hide below scale 0.75 and
  move to the chain strip tooltip).
- **wide ≥ 1440**: full scene (scale ~0.74 at 1184 board width; height ~355 + chain strip 40).
- **medium 1100–1440**: same scene, scale 0.55–0.74; back line and floor kept; rack collapses to 3 thin faces
  with displays only.
- **compact < 1100 (945 window)**: no room scene; the chain strip becomes the main board with **art cells**
  (each block drawn as its kind at cell size — phase-2 `design.md` cells, unchanged) so the identity survives;
  stage toggles back on when the window widens.
- Height budget at 1888x1016: top 64 + header 48 + stage 355 + strip 40 + close-up 296 + status 28 + gaps ≈ 880.

### Motion (constitution: answer an action / live data, ≤ 400 ms)
Selection: spotlight ellipse slides to the selected unit (`dur_m`); unit lifts 4 px with its contact shadow
widening. Toggle: LED + cable segment colour fade `dur_s`. Reorder in the chain strip: chips animate; scene units
do not move (their place is by kind), only cables re-route with a 200 ms opacity cross-fade.

### Fold into phase 2 (replaces 2.3, extends 2.2 and 2.5)
- 2.1 art mapping: unchanged (`kind`, `family`).
- 2.2 tokens: + stage/material tokens above.
- **new 2.0 textures**: `tools/make_textures.py` + vendored `app/assets/textures/*.png`; test: deterministic
  output hash, tiles seamless (edge columns match).
- **2.3 replaced by** 2.3a `Stage.qml` (backdrop, zones, scale, keyboard focus order = chain order) + 2.3b unit art
  per kind (`AmpHead.qml`, `Cabinet.qml`, `RackUnit.qml`, `Treadle.qml`, `Stompbox.qml` re-skinned) at stage
  size + 2.3c `ChainStrip.qml` (reorder by drag/keys/menu; current `Unit` input code moves here) + cables between
  unit jack points.
- 2.4 fader: unchanged.
- 2.5 close-up faces: draw from the **same** QML unit components at larger scale (`size` property), so the face
  and the stage unit are the same object — no second drawing.
- 2.6 art audit: + "no brand silhouette" check per kind (no Marshall script/plate shape, no Fender jewel+grille
  combination copied 1:1, no Boss/Ibanez box outline), M2 grid shot of all families × kinds.
- Effort: L–XL (roughly phase 2 x 1.5). Phase-1 quick touches 1–5, 7–12 remain valid inside this scene; item 6
  (cables) is absorbed by 2.3a.

### Open decisions for the user
1. Scene by kind + chain strip for order (recommended) vs keep units in chain order on one floor (simpler, less
   "room").
2. Floor: dark wood planks vs rubber stage mat.
3. Compact window: art cells (recommended) vs a smaller version of the scene.

---

## A. Quick touches (phase-1 polish), ranked

Effort: XS < 30 min, S ~1 h, M ~half day.

### 1. Close-up: compose the face, stop painting a slab — S/M
- **Wrong**: `CloseUp.qml` face fills all remaining height (~620 px at 1888x1016) with one flat mid-tone; knobs
  start ~100 px below the header (`Flow.topPadding: 72` + spacing) and hug the left edge; the footswitch (56) and
  LED (10) float at the top-right, disconnected from anything; the empty rest of the slab is the loudest thing on
  screen.
- **Change**:
  - `face`: `Layout.maximumHeight: T.face_max_h` (wrap the face in a `ColumnLayout` with a trailing
    `Item { Layout.fillHeight: true }`), so extra height stays neutral plate glass. When there are more knob rows
    than fit, the existing `Flickable` scrolls inside the cap. Add the enamel overlay: a child `Rectangle`
    `anchors.fill`, same radius, `gradient: Gradient { GradientStop { position: 0; color: T.face_hi }
    GradientStop { position: 0.5; color: "transparent" } GradientStop { position: 1; color: T.face_lo } }`, plus a
    1 px `bevel_hi` line at y 1 like the stompbox.
  - Knobs: replace `Flow` with a `Row` centred horizontally (`anchors.horizontalCenter`) when they fit in one row,
    `Flow` only on overflow; cell 104x148 with `dia: T.knob_face`; spacing `T.s5`.
  - Remove `topPadding: 72`: make `ValuePopup` an overlay (`parent: Overlay.overlay`, position mapped from the
    knob with `mapToItem`) so it needs no reserved room. Spec 1.x behaviour unchanged.
  - Move `Led` + `Footswitch` to bottom-centre of the face (stompbox anatomy, Jakob's law), LED 10 px 12 px above
    the switch, and a `font_small` label right of it: "Encendido" / "Apagado" (colour is no longer the only cue).
- **Why pro**: centred, bounded composition reads designed; empty space becomes calm glass instead of colour;
  the on/off control sits where every guitarist expects it.
- Mockup: see "Top 3" below.

### 2. Stompbox face: nameplate band, real LED, enamel — S
- **Wrong**: `Stompbox.qml` prints glyph + code in `ink_dark` 12 px on the face (7/11 fail contrast, table above);
  `Led` off state is a 1.5 px `ink_off` outline that vanishes on mid tones; body is a flat tint; footswitch 20 px.
- **Change**:
  - Nameplate: `Rectangle { x: 14; y: 42; width: 64; height: 20; radius: 4; color: T.nameplate }` holding glyph
    (14 px) + code (`font_small`, `Font.DemiBold`, `letterSpacing: T.track_code`) in `sb.col`. Contrast 5.7–10.6.
  - `Led.qml` off: `color: T.led_off`, `border.width: 1; border.color: T.bevel_hi` (a lens, not a hole); on: block
    colour + existing glow.
  - Body: same enamel overlay as item 1 (`face_hi` → `face_lo`), radius `T.r_unit`.
  - Footswitch 20 → 24 px; mini knobs stay 16 (they are a hint, not a control).
- **Why pro**: inverted silkscreen is exactly how printed pedals stay legible on any paint; a filled lens and a
  lit gradient give depth even with `GP200_FX=0`.

### 3. Effect picker reads as a title, not a form field — S
- **Wrong**: `CloseUp.qml` `cb` (editable ComboBox) renders a near-black Basic `TextField` box on the coloured
  face; it is the darkest, most "default widget" object on screen.
- **Change**: style it like `HeaderBar`'s name field: `contentItem: TextField { background: null }` sitting on a
  `nameplate` pill (`radius: T.r_pill`, height 36), text `T.text`, `font_title`, `Font.DemiBold`, chevron glyph in
  the block colour; border `T.accent` only on hover/focus. `popup` background `T.popup_bg`, `r_tile`, max height 360, delegates `font_body`.
  Description moves under the title as `font_body` `T.text` on a second line inside the same nameplate block
  (fixes the 3.3–4.2 contrast of desc text on CAB/MOD/RVB faces).
- **Why pro**: one dark nameplate holding name + model description = the "model plate" of real gear; no stray
  system widget.

### 4. Close-up knobs: visible arc, printed scale — S
- **Wrong**: `Knob.qml` arc uses `arcColor: cu.col` on a face tinted with the same colour → the value arc is
  almost invisible (gold on tan in B1); track `ink_off` (white 25 %) looks washed out on colour.
- **Change**: add `property bool onFace`; when true, track `T.track_on_face`, value arc `T.text` at 3 → 4 px,
  plus 11 printed ticks (one `ShapePath` dashed arc like the knurl, `T.tick`, radius `dia/2 + 12`, 2 px).
  Labels below: name `font_body` `T.ink_dark` only on faces that pass, otherwise put label + value inside a
  small `nameplate` chip (simplest: always chip, width 72, height 36, two lines). Value text keeps `T.mono`.
- **Why pro**: printed scales are the single strongest "hardware" cue; the value is now readable at a glance.
- Note: values show `0` only because the fake pedal sends zeros (bridge falls back correctly); not a UI bug. Shots
  for the spec should use a fake slot with realistic values (task P10).

### 5. Link the selected unit to the close-up — S
- **Wrong**: selection is a 2 px accent ring around the cell; nothing ties the board to the face 40 px below
  (wayfinding).
- **Change**: selected `Unit` lifts `y: -4` (Behavior already there) and its ring becomes `r_unit` 2 px accent;
  the close-up plate gets a 12x8 caret (`Shape` triangle, `T.plate_border` stroke / `T.plate` fill) on its top
  edge at the selected unit's centre x (`pb.mapToItem(cu, unitCentre, 0).x`, animated `dur_m`). Close-up face
  top-left shows the block glyph in `sb.col` inside the nameplate (already there as a 40 px disc; recolour).
- **Why pro**: speech-bubble linkage is how pro editors (rack/pedal editors, DAW inspectors) say "this panel
  edits that thing".

### 6. Cables you can see, that follow — M
- **Wrong**: in one row the gap is 8 px (`gap1`) so cables are 8 px squiggles hidden by the units; when units
  animate (reorder) cables snap to the final position (`Cable` binds to `pb.cx()`, not the unit).
- **Change**: (a) give the `Unit` Repeater an id and bind each cable end to the live item:
  `x0: units.itemAt(blockIndex).x + 84 * …` (Unit already exposes animated `x/y`), so cables move with the
  `Behavior`; (b) put the cable layer `z: -1` and route one-row cables as a loop **below** the units: plug at
  each unit's bottom-centre-ish side (y + 100) with control points at y + 132 (sag 32), so the run is visible in
  the 16 px under the cells; raise `implicitHeight` one-row by 16 px. Wrap mode unchanged.
- **Why pro**: a visible, swinging patch cable is the signature image of a pedalboard; snapping wires look broken.
- Overlap: phase 3.3 cable glow reuses these paths.

### 7. Token hygiene: radii + type scale — S/M (many files, mechanical)
- **Wrong**: radii literals 10, 14, 16, 18 next to tokens 8/12/20; sizes 13 vs 14 vs 12 indistinguishable;
  `font.bold` on codes, buttons, tabs, titles alike; literals 288/360/312/380/88/112/72 bypass tokens
  (constitution: sizes from tokens).
- **Change**: tokens above; replace literals (`Unit` 14 → `r_unit`, `Stompbox` 10 → `r_unit`, `CloseUp` 16 →
  `r_tile`, ComboBoxes 18/16 → `r_pill`), drop `font_desc` (13) in favour of 12/14, `Font.DemiBold` instead of
  bold, add `dock_left 288`, `dock_right 360`, `drawer_left 312`, `drawer_right 380` tokens.
- **Why pro**: consistency is most of what reads as "designed"; users never name it but always feel it.

### 8. Header actions: show them only when they mean something — XS
- **Wrong**: three outline pills (Descartar / Guardar en… / Guardar) are always visible; when clean they are
  disabled but look almost enabled (`sel_border` 25 % outline), so the header always looks like a form waiting
  for input.
- **Change**: when `!board.dirty`, show one quiet chip instead: glyph `ok` + "Guardado en 34B" (`T.dim`,
  `font_small`); when dirty, fade in (`dur_s`) the three buttons and "● Sin guardar". Factory presets: chip reads
  "Preset de fábrica" and `Guardar en…` stays visible (it is the only way out). Keyboard (Ctrl+S) unchanged.
- **Why pro**: progressive disclosure; the header states the truth instead of showing dead controls.

### 9. Status bar: never an icon-only pill — XS
- **Wrong**: `StatusPill` with empty text shows a lone check centred in a full-width pill (A1 shot), which looks
  like a rendering bug; the text is centred under a left-heavy layout.
- **Change**: `visible: text !== ""` for the icon (or bridge supplies "Listo"); in `Main.qml` give it
  `Layout.fillWidth: false; Layout.alignment: Qt.AlignLeft` (it is a pill, let it be pill-sized), height 28.
- **Why pro**: no orphan chrome; status reads where the eye ends (bottom-left of the F pattern).

### 10. Empty and loading states that look intentional — S
- **Wrong**: no slot open → two jacks in the top-left of a short plate, a glyph and a sentence centred, and a
  huge blank below. Slot grid while scanning shows "…" in 255 cards.
- **Change**:
  - Board empty: jacks at the plate's left and right ends (`cx(1)` = right edge) with one long sagging cable
    between them, 11 ghost units (`ghost: true`, dashed `ink_off` outline already exists) along it at 40 %
    opacity, text "Elige un slot para ver su cadena" under it; close-up area shows a centred hint plate:
    "Atajos: ←/→ elegir bloque · Espacio encender · Ctrl+←/→ mover · Enter cambiar efecto" (`font_small`, `T.dim`).
  - Slot cards loading: replace "…" with a static skeleton bar (`Rectangle` 60 % width, 8 px, `T.ink_off`,
    radius 4). No pulse (user decision 2026-11-25: respect the ≤ 400 ms motion rule).
- **Why pro**: an empty board that already looks like a pedalboard invites the action; skeletons say "loading" not
  "broken".

### 11. Slot cards: hierarchy — XS
- **Wrong**: code ("12B") and name are both 12 px; code bold white, name regular white: the name, which is what
  people look for, is the weaker of the two.
- **Change**: code `font_small` DemiBold `T.dim` letterSpacing `track_code`; name `font_body` `T.text`, one line
  + elide (2 lines at 14 px do not fit 28 px). Card height 52 unchanged.

### 12. Busy state says what is busy — XS
- **Wrong**: while saving, board and close-up drop to 50 % opacity and a 2 px bar runs at the top; nothing says
  why near the content.
- **Change**: under the busy bar, a `font_small` `T.dim` line with `board.busy` ("Guardando en 34B…"), left-aligned
  at x 24. Opacity 0.5 → 0.6 (text still legible).

---

## B. Bigger items (fold into phase 2 / 3)

| # | Item | Where it goes | Effort |
|---|---|---|---|
| B1 | Chassis families (tweed, brit gold, od green…) replace the single block tint; the enamel overlay and nameplate from items 1–2 become per-family tokens (`face`, `ink`, `nameplate`, knob variant) | phase 2: 2.1, 2.2 | M (already planned) |
| B2 | Close-up faces per kind (head with panel + logo-free script name, cab grille, rack with 2-value display, EQ faders, treadle) built on item 1's bounded face | phase 2: 2.5 | L (planned) |
| B3 | Board units per kind (AmpHead, Cabinet, RackUnit, Treadle) with items 2/6 rules (nameplate contrast, cable plug points from the unit) | phase 2: 2.3 | L (planned) |
| B4 | Knob variants per family (chicken-head, skirted, bakelite) using item 4's tick + track tokens | phase 2: 2.2/2.5 | M |
| B5 | Cable glow / meter on the cable paths from item 6; signal "travels" left→right only while audio is live | phase 3: 3.3 | M (planned) |
| B6 | Entrance stagger + art cross-fade on effect change; footswitch press depth (scale 0.94 + face_lo darken) | phase 3: 3.5 | M (planned) |
| B7 | Window backdrop: very low-contrast stage gradient (dusk → dusk_dark, top→bottom) on the opaque fallback only; glass stays flat (compositor blur provides depth) | standalone, after phase 2 | S |
| B8 | Chat pane polish: bubbles instead of a single rich-text log, tool calls as collapsible rows, streaming caret (AI latency pattern) | own spec (chat) | M |

Overlaps with phase-2 tasks already in `tasks.md`: items 1 and 3 (face container, nameplate, picker) are the
skeleton that 2.5 fills — do them now so 2.5 only swaps the art inside; item 2 is the "stompbox" kind of 2.3 and its
tokens become one family in 2.2; item 4 is the base for B4 (2.2/2.5 knob variants); item 6 feeds 3.3. Items 5, 7,
8, 9, 10, 11, 12 do not overlap anything planned.

---

## Top 3 quick touches — before / after (the rig scene mockup is in section #1)

### 1. Close-up (1888 wide, AMP selected)

Before (B1-open-wide-r2):
```
+------------------------------------------------------------------------------------------+
| (o) [Tweedy               v]  Fender(R) Tweed Deluxe                            o  (O)    |  <- flat #9c7c44
|                                                                                          |
|                                                                                          |
|  (G)   (T)   (V)                                                                         |  knobs top-left
|  Gain  Tone  Volume                                                                      |
|   0     0     0                                                                          |
|                                                                                          |
|                                    ~380 px of flat colour                                |
|                                                                                          |
+------------------------------------------------------------------------------------------+
```
After:
```
                          v caret under the selected AMP unit (12x8)
+--------------------------^---------------------------------------------------------------+  plate (glass)
|  +------------------------------------------------------------------------------------+  |
|  | [##  AMP  Tweedy                 v ]   <- nameplate pill (#e614171a), name 18 DemiBold |  |  face: max 296 px
|  | [    Fender(R) Tweed Deluxe          ]     desc 14 T.text                            |  |  enamel gradient
|  |                                                                                    |  |
|  |            . ' ' .        . ' ' .        . ' ' .        <- printed ticks, 72 px    |  |
|  |           (  Gain )      ( Tone  )      (Volume )          knobs centred, gap 24  |  |
|  |            [ 55 ]          [ 40 ]         [ 70 ]          value chips, mono       |  |
|  |                                                                                    |  |
|  |                           *  (O)  Encendido       <- LED + 56 px switch, bottom-ctr|  |
|  +------------------------------------------------------------------------------------+  |
|                                                                                          |
|                    (rest of the plate stays neutral glass, no colour)                   |
+------------------------------------------------------------------------------------------+
```

### 2. Stompbox unit (92x144 cell, body 76x104)

```
Before                         After
+----------------+             +----------------+   enamel: face_hi -> face_lo
|   o   o   o    |  mini 16    |   o   o   o    |   mini knobs 16
|                |             | +------------+ |
|   ^ PRE        |  ink_dark   | | ^  P R E   | |   nameplate #e614171a, code in block colour
|     .          |  LED outline| +------------+ |   (5.7 - 10.6 : 1)
|    (O)         |  switch 20  |      (*)       |   LED filled lens (led_off / colour+glow)
+----------------+             |     ( O )      |   switch 24
     COMP                      +----------------+
                                    COMP           effect name 12 T.dim (unchanged)
```

### 3. Effect picker + header state

```
Before:  [34B] Test                                  ( Descartar ) ( Guardar en... ) ( Guardar )   <- always, look enabled
         (o) [####Tweedy######|v]  Fender(R) Tweed Deluxe                       black Basic field on tan

After, clean:  [34B] Test                                                 (ok) Guardado en 34B
After, dirty:  [34B] Test   * Sin guardar                   ( Descartar ) ( Guardar en... ) [ Guardar ]
         face: [ ##  AMP  Tweedy                 v ]   one nameplate holding glyph, code, name, chevron
               [     Fender(R) Tweed Deluxe        ]   accent border only on hover / focus
```

---

## QML quality notes that affect look/feel (from qt-qml-review pass, inline, no agents)

- `CloseUp.qml:71` `topPadding: 72` is layout reserved for a transient popup → visual gap (fixed by item 1's
  overlay popup).
- `Pedalboard.qml:46-53` cables bind to computed slot positions, units to animated `x/y` → desync during the
  200 ms reorder animation (item 6).
- `CloseUp.qml:32` editable ComboBox without a styled `contentItem` → Basic style leaks (item 3).
- `CloseUp.qml:73` and `ParamPills.qml:9` re-run `board.params.filter(...)` as a binding on every `params`
  change; fine at this size, but both Repeaters rebuild all delegates when one value changes if `params` is
  re-emitted with values (check `bridge.py` emits `params` only on effect change, `values` on knob moves —
  currently true, keep it so knobs never flicker mid-drag).
- Literal radii/sizes listed in item 7 contradict the token rule in `constitution.md` (not new rules, just drift).

## Constitution change

**Needed for the rig scene (#1)**: the Look rule says gear art = "original vector drawings (QtQuick.Shapes)".
Option D adds vendored raster assets. Proposed wording: "Gear art = original drawings: geometry and colour in
QtQuick.Shapes from `theme` tokens; colourless alpha material tiles and shadow sprites generated by
`tools/make_textures.py` (committed in `app/assets/`, no photos, no logos, no third-party art)." Needs user OK
before phase 2 starts. The stage backdrop lives inside the board plate (not a second glass layer), so the glass
rules are unaffected.

Quick touches (section A): none required. Gradients use fixed alpha tokens (`face_hi`, `face_lo`), the caret and ticks are original `Shape` art, and all motion stays ≤ 400 ms (skeleton is static).

## Proposed tasks (implementer, in order)

- [ ] P1 **Tokens** — `app/theme.py`: add the tokens in the table, `r_unit`, dock/drawer sizes; drop `font_desc`
  (alias to `font_small` first to keep diffs small). Done: `tests/test_app.py` token test lists them; contrast
  script output for `nameplate` vs every block colour pasted in `notes.md` (all ≥ 4.5).
- [ ] P2 **Stompbox** — `Stompbox.qml`, `Led.qml`, `Unit.qml` (radius): nameplate, enamel, LED lens, switch 24.
  Done: B1 re-shot; zoomed crop of DST/CAB/RVB units shows readable codes.
- [ ] P3 **Close-up face** — `CloseUp.qml`, `ValuePopup.qml`, `Knob.qml` (popup parent): capped face, centred knob
  row, popup as overlay, LED + switch + "Encendido/Apagado" bottom-centre. Done: B1 + K shots; face ≤ 296 px;
  turning a knob still shows the bubble (C1 re-shot); Space/click on switch still toggles.
- [ ] P4 **Picker nameplate** — `CloseUp.qml`: styled ComboBox (contentItem, popup, indicator). Done: no Basic
  widget visible; typing + Enter still filters/sets (existing test).
- [ ] P5 **Knob on face** — `Knob.qml` `onFace`, ticks, value chip. Done: arc visible on every block colour
  (M-style grid shot of 11 faces with one knob each, offscreen).
- [ ] P6 **Selection caret** — `Main.qml`/`CloseUp.qml`/`Unit.qml`. Done: caret tracks the selected unit in one-row
  and wrapped layouts (B1, K shots).
- [ ] P7 **Cables follow + sag** — `Pedalboard.qml`, `Cable.qml`. Done: 3 frame grabs mid-reorder show cables
  attached; I1 drag re-shot.
- [ ] P8 **Header / status / busy** — `HeaderBar.qml`, `StatusPill.qml`, `Main.qml`, `Pedalboard.qml`. Done: shots
  clean vs dirty (B1, H1); A1 has no icon-only pill; F1 shows the busy line.
- [ ] P9 **Empty/loading + slot cards** — `Pedalboard.qml`, `CloseUp.qml` (hint), `SlotGrid.qml`. Done: A1 re-shot,
  scan-in-progress shot shows static skeletons.
- [ ] P10 **Literal sweep + realistic shots** — all QML: radii/sizes → tokens; fake pedal in the shot script
  fills realistic values (e.g. Gain 55, Tone 40, Volume 70) so knobs are not all at 0. Done: `grep -nE
  'radius: (10|14|16|18)\b' app/qml` empty; full shot set re-taken; tests pass.

Rig scene (#1) tasks are the rewritten phase 2 above (2.0 textures, 2.3a Stage, 2.3b unit art, 2.3c chain strip,
2.5 faces from the same components); they start after the user picks the 3 open decisions and OKs the
constitution change. Order suggestion: P1–P5 now (they survive inside the scene), then phase 2; P6–P7 can be
skipped if phase 2 starts soon (2.3a/2.3c replace them).

Real-pedal smoke after P3/P4: toggle + one knob + effect change on a scratch slot still audible (unchanged
model path; view-only changes).

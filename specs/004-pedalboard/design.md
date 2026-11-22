# 004 — Pedalboard: design

Status: draft for the user's OK. Builds on 003 (tokens, glass, block colours, glyphs, copy) — everything
not restated here keeps 003's values and copy.

## Direction
A rig seen from above the floor, under the same frosted dusk-blue glass. The one bold thing is the
**board**: real-looking units in signal order, patch cables sagging between their jacks, LEDs glowing in
each block's colour. Everything around it (top bar, slot grid, chat, status) stays 003-quiet. Gear is
drawn, not photographed: satin chassis, printed nameplates in Noto Sans bold, knurled knobs with a white
pointer. The art borrows *categories* of gear (green overdrive, gold British head, tweed combo, 1U rack),
never a brand's logo, name, shape or colour scheme copied 1:1.

## Decision: full QML window (not QQuickWidget)
`QQmlApplicationEngine` + `ApplicationWindow` (`QGuiApplication`), whole UI in QML.
- One scene graph: animations, cables across the whole board, drawers over content, drag with lift and
  shadow all need one GPU surface. `QQuickWidget` renders to an offscreen FBO then composites into the
  widget backing store (extra copy, no threaded render loop) and mixes badly with
  `WA_TranslucentBackground` glass.
- The responsive fix (half-screen tile) needs dock ↔ drawer switching of the slot grid and chat, which is
  one `states` block in QML but a rebuild of three widget columns in QWidgets.
- What it costs: slot grid and chat are redrawn in QML (they are small: a `GridView` and a `TextArea` over
  `ChatSession.html`). `app/widgets/` is deleted at the end of phase 1; git history is the fallback.
- Checked: `python3 -c "from PyQt6 import QtQuick, QtQml"` OK; Qt 6.12 with `QtQuick.Shapes`,
  `QtQuick.Effects` (MultiEffect), `QtQuick.Controls` (Basic) installed in `/usr/lib/qt6/qml`.

## Decision: responsive layout, no float rule
Tiling is how the user works; a float rule would fight it. The layout has three widths (window width `W`):

| Mode | W | Slot grid | Chat | Board columns (pitch 104) |
|---|---|---|---|---|
| wide | ≥ 1440 | docked left 288 | docked right 360 | 1888 → 11 |
| medium | 1100–1439 | docked left 288 | drawer right 380 | 1265 (DP-3 half) → 8 |
| compact | < 1100 | drawer left 312 | drawer right 380 | 945 (DP-2 half) → 8 |

Window default 1440×900 (when floating), minimum 880×600. Below 880 (3+ tiles) Hyprland may still squeeze
it: content scrolls (board `Flickable`), nothing overlaps.

## Main view — wide (1888×1016, DP-2 maximised tile; all numbers px)
```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│16                                                                                                                │
│ ◉ GP-200JR  ( Presets | Chat general )                                   ▮▮ Salida  [♪ Afinador]   top bar h48   │
│                                                                        (phase 3: mini meter + tuner button)      │
│┌ slots 288 ─────────┐12┌ board column (flex, 1184) ──────────────────────────────────────────────┐12┌ chat 360 ──┐│
││⌕ Buscar slot…    ⟳ ││ │ (34B) Crunch AZ        ● Sin guardar        Descartar  Guardar en…  [Guardar] h48 │  │Chat · 34B ⊕││
││ 1 [1A ][1B ][1C ]  ││ │┌ board plate (h 220) ─────────────────────────────────────────────────────────────┐│  │┌──────────┐││
││ 2 [2A ][2B ][2C ]  ││ ││ ┌──┐  ╭──╮ ╭──╮ ╭──╮ ╭────╮ ╭──╮ ╭────╮ ╭──╮ ╭───╮ ╭───╮ ╭───╮ ╭──╮  ┌──┐ ││  ││ Tú: …    │││
││ …                  ││ ││ │IN│~~│∘∘│~│∘∘│~│∘∘│~│∘∘∘ │~│∘ │~│▒▒▒▒│~│∘∘│~│▭▭▭│~│▭▭▭│~│▭▭▭│~│∘ │~~│OUT││  ││ Claude:… │││
││34 [34A][34B•][34C] ││ ││ │  │  │PRE│ │WAH│ │DST│ │AMP │ │NR│ │CAB │ │EQ│ │MOD│ │DLY│ │RVB│ │VOL│  │▮▮ │ ││  ││          │││
││   vacío Crun… vacío ││ ││ └──┘  │ ● │ │ ○ │ │ ● │ │[●] │ │○ │ │ ●  │ │○ │ │ ○ │ │ ● │ │ ● │ │ ○│  └──┘ ││  ││          │││
││ …                  ││ ││Guitarra╰──╯ ╰──╯ ╰──╯ ╰────╯ ╰──╯ ╰────╯ ╰──╯ ╰───╯ ╰───╯ ╰───╯ ╰──╯ Salida ││  │└──────────┘││
││                    ││ ││      P-Boost V-Wah GreenOD UK800 Gate1 SUPZEP GtrEQ1 Detune Analog Room Volume││  │ hint       ││
││                    ││ │└ cells 92×144, gap 12, padding 16; jacks 40×64 ────────────────────────────────────┘│  │┌ ✎ … ➤──┐││
││                    ││ │┌ close-up plate (flex, min 260) ───────────────────────────────────────────────────┐│  │└────────┘││
││                    ││ ││ ┌ chassis face (AMP family colour, r 16) ───────────────────────────────────────┐ ││  └───────────┘│
││                    ││ ││ │ (▣) [ UK 800              ▾ ]  Marshall® JCM800                       ( ⏻ )   │ ││              │
││                    ││ ││ │                                                                    footswitch│ ││              │
││                    ││ ││ │   ╭───╮    ╭───╮    ╭───╮    ╭───╮    ╭───╮    ╭───╮                Ø56 + LED│ ││              │
││                    ││ ││ │  (  /  )  (  |  )  (  \  )  (  |  )  (  /  )  (  |  )   knobs Ø64, cell 88×112│ ││              │
││                    ││ ││ │   ╰───╯    ╰───╯    ╰───╯    ╰───╯    ╰───╯    ╰───╯                          │ ││              │
││                    ││ ││ │   Gain   Presence  Volume    Bass    Middle   Treble    (labels 13 on chassis)│ ││              │
││                    ││ ││ │    63       50       50       50       50       50     (values mono 12)       │ ││              │
││                    ││ ││ │  [Modo: Normal ▾]  (● Brillo)            switch / combo pills h32             │ ││              │
││ ✓ Listo            ││ ││ └───────────────────────────────────────────────────────────────────────────────┘ ││              │
│└────────────────────┘│ │└──────────────────────────────────────────────────────────────────────────────────┘│              │
│                      │ │ ✓ Pedalera en 34B · cambios en vivo                                 status pill h28 │              │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```
Units in this mockup are phase-1 stompboxes (`∘` mini knobs, `●/○` LED, `~` cable). In phase 2 AMP, CAB,
MOD/DLY/RVB, EQ, WAH/VOL take their own art inside the same 92×144 cell (see Gear).

## Main view — compact (945×1016, DP-2 half tile)
```
┌───────────────────────────────────────────────────────────────────────────────┐
│ [☰]  ◉ GP-200JR  ( Presets | Chat general )                    [♪]  [󰭹•]   h48 │
│      Slots (Ctrl+B)                                         Afinador  Chat (Ctrl+J)
│ (34B) Crunch AZ   ● Sin guardar        Descartar  Guardar en…  [Guardar]  h48 │
│┌ board plate (913 wide, 2 rows: 8 + 3) ─────────────────────────────────────┐ │
││┌──┐ ╭──╮ ╭──╮ ╭──╮ ╭────╮ ╭──╮ ╭────╮ ╭──╮ ╭───╮                            │ │
│││IN│~│PRE│~│WAH│~│DST│~│AMP │~│NR│~│CAB │~│EQ│~│MOD│─╮                        │ │
││└──┘ ╰──╯ ╰──╯ ╰──╯ ╰────╯ ╰──╯ ╰────╯ ╰──╯ ╰───╯  │ wrap cable runs down │ │
││ ╭───────────────────────────────────────────────────╯ the right gutter, back │ │
││ │   ╭───╮ ╭───╮ ╭──╮ ┌───┐                            along the row gutter   │ │
││ ╰──~│DLY│~│RVB│~│VOL│~│OUT│                            (h 16), up into DLY    │ │
││     ╰───╯ ╰───╯ ╰──╯ └───┘                                                    │ │
│└ h = 16 + 144 + 16 + 144 + 16 = 336 ──────────────────────────────────────────┘ │
│┌ close-up plate (flex ≈ 470) ─────────────────────────────────────────────────┐│
││ (▣) [ UK 800 ▾ ]  Marshall® JCM800                                   ( ⏻ )   ││
││   ╭───╮  ╭───╮  ╭───╮  ╭───╮  ╭───╮  ╭───╮      knob cells 88×112, wrap to   ││
││   Gain  Presence Volume Bass  Middle Treble     as many columns as fit (9)    ││
││   [Modo: Normal ▾]  (● Brillo)                                                ││
│└──────────────────────────────────────────────────────────────────────────────┘│
│ ✓ Pedalera en 34B · cambios en vivo                                     h28    │
└───────────────────────────────────────────────────────────────────────────────┘
Drawers (compact): slot grid = left Drawer 312 wide, full height below the top bar, dim scrim 40 %
(`T.scrim`), closes on Esc / scrim click / slot opened. Chat = right Drawer 380, same rules (closing it never
cancels a running Claude turn; the chat button shows a 6 px accent dot while Claude runs).
Medium: slot grid docked 288, only chat is a drawer.
```
Header row in compact: slot pill + title (min 120, elides) + chip; buttons keep their full text; if
`W < 960` the chip text shortens to "● Sin guardar" → "●" with tooltip "Sin guardar" (the only
truncation rule).

## Board geometry
- Cell 92×144 (art area 92×112 aligned to a floor line at y 112; nameplate text below: effect name 12,
  1 line elided, `T.dim`). Gap 12 → pitch 104. Padding 16. Jacks: "IN" 40×64 at the start, "OUT" 40×64
  at the end, labels "Guitarra" / "Salida" 12 `dim` under them; jacks count as cells for wrapping.
- Columns `n = floor((boardW − 32 + 12) / 104)`; position of chain index i (jacks included) =
  `(i % n, i / n)`. Units never get recreated on reorder: a `Repeater` over the 11 fixed blocks, each
  positioned by its index in `board.order` with `Behavior on x/y` (220 ms OutCubic) → reorders and
  wraps animate for free.
- Cable: `Shape` with one `ShapePath` per link (jack k → jack k+1). Jacks on each unit at y 72 (left
  and right edge). Same row: cubic with 12 px sag. Row wrap: right out of the last unit, down the right
  gutter to the row gutter, left along it, up into the first unit of the next row; corners r 12.
  Stroke: 5 px `T.cable` (rubber) + inner 2 px line = block colour of the unit on the link's left at 70 %
  if that unit is ON, else `T.ink_off` (003 rule kept: bypass still passes signal).
- Board plate height = rows × 144 + (rows−1) × 16 + 32; the close-up plate takes the rest (min 260,
  else the page scrolls).

## Units (phase 1: stompbox for every block)
Stompbox art (inside 92×112, origin top-left): body 76×104 at x 8, r 10, fill = chassis colour (see Gear,
phase 1 uses `T.block_colors[block]` mixed 60 % with `T.chassis_base`), 1 px top highlight `T.bevel_hi`,
bottom shadow via MultiEffect (shadowBlur 0.4, `T.shadow`). Top band: up to 3 mini knobs Ø16 (first
three knob params, real values, pointer only). Middle: nameplate = block code 12 bold in chassis ink +
glyph 16. Bottom: footswitch Ø20 (`T.metal` with darker ring) and LED Ø8 above it: ON = filled block
colour + glow (MultiEffect blur, 8 px), OFF = 1.5 px ring `T.ink_off`. Selected unit: 2 px `T.accent`
ring around the cell, r 14. Focus = same ring dashed. Hover = cell fill `T.sel_fill`.

## Close-up (editor)
Plate holds one **face** in the selected unit's chassis colour (r 16, inset 12). Header row h56: glyph disc
Ø40, effect picker (editable ComboBox pill h36, min 240), desc 13 `dim`, footswitch Ø56 + LED Ø10 at the
right. Body: knob grid cells 88×112 (Ø64 knob, label 13 below in chassis ink, value mono 12), columns =
as many as fit, then a flow row of switch pills and combo pills h32 (wraps; fixes the 003 overflow nit).
DLY Time locked + 003 note (warn 13) above the knobs. Unknown effect: 003 copy, no knobs.

## Knob (`Knob.qml`, used everywhere; Ø from the caller)
- Layers (Shapes): value track 270° (from −135° to +135°) 3 px `T.ink_off` at radius r+6, value arc 3 px
  block colour; skirt = circle `T.knob_skirt` with 48 knurl ticks (1 px `T.knob_knurl`); cap = radial
  gradient `T.knob_cap_hi` → `T.knob_cap`; pointer 2 px `T.text` from 30 % to 85 % of the cap radius.
  Phase 2 families may swap cap colours (cream/chrome, see Gear) — knob logic unchanged.
- Input: vertical drag 200 px = full range (Shift ×0.2), wheel 1 step, ←↓ / →↑ 1 step, PgUp/PgDn 10,
  Home/End min/max, context menu "Escribir valor…" (inline SpinBox over the knob, Enter applies, Esc
  cancels) and "Valor por defecto". Step/decimals as 003 (`step` from catalog range).
- Value popup while dragging/wheeling/keys: bubble 96×56 above the knob, opaque `T.popup_bg`, r 12:
  param name 12 `dim` + value mono 24 `text`; fades in 100 ms, out 150 ms, 600 ms after the last change.
- Accessible: role Dial, name = param name, value text; focus ring 2 px accent around the track.
- Locked: arcs `ink_off`, lock glyph replaces the pointer, input ignored, tooltip = the DLY note.

## Gear (phase 2) — original art families
`art_for(block, effect_name, desc)` (pure, `app/art.py`, unit-tested) → `{kind, family}`; colours of each
family live in `theme.chassis[family]` = `{body, face, ink, knob}`. Keyword match on `desc` + `name`,
case-insensitive, first rule wins; unmatched → the block's default family.

| Block | Kind | Families (keywords → family) |
|---|---|---|
| PRE | stompbox | compressor ("comp") → `brushed` (silver, dark ink); boost/other → `cream` |
| WAH | treadle | `treadle_black` (rubber tread, toe LED) |
| DST | stompbox | "screamer\|ts-\|od\|overdrive\|blues" → `od_green`; "fuzz\|muff" → `fuzz_violet` (wedge-top box, not round); "distortion\|rat\|ds-" → `dist_orange`; "metal\|high gain" → `metal_black` |
| AMP | head | "marshall\|jcm\|plexi\|british\|uk" → `brit_gold` (black tolex, gold faceplate, cream knobs); "fender\|tweed" → `tweed` (tweed body, chrome panel); "twin\|deluxe\|vibro\|blackface\|silverface" → `blackface` (black panel, silver trim, skirted knobs); "vox\|ac-\|ac30" → `copper` (copper top panel, chicken-head pointer); "mesa\|boogie\|rectifier\|5150\|peavey\|bogner\|engl\|diezel\|evh" → `steel` (diamond-tread steel plate, black knobs); else `graphite` |
| CAB | cabinet | grille by same keywords as AMP: British → `grille_wheat`, Fender-ish → `grille_silver`, else `grille_black`; speaker count from desc `(\d)x(\d+)` → faint cone circles behind the grille + label "4x12" |
| NR | stompbox (mini, 64 wide) | `gate_grey` |
| EQ | stompbox with faders | `eq_white` (knob params render as vertical faders) |
| MOD / DLY / RVB | rack 1U | `rack_dark` face; display ink = block colour; display shows 2 main values: DLY "Time ms · Mix", RVB "Decay · Mix", MOD "Rate · Depth" (first matching param names, else first two knobs) |
| VOL | treadle | `treadle_black` |

Kinds inside the 92×144 cell (floor line y 112): stompbox 76×104; head 92×60 at y 52 (pilot jewel Ø8
red `T.pilot` when ON, dark when OFF — plus the LED rule, colour never alone); cabinet 92×92 at y 20;
rack 92×40 at y 72 with display 56×16; treadle 60×100 angled (skew 8°); mini stompbox 64×80. Close-up
faces per kind: head = full-width faceplate strip with knobs in one row (wraps) + jewel + nameplate;
cabinet = grille panel with Low/High Cut knobs; rack = 1U face with a 240×48 display + knobs; EQ =
fader bank (fader 24×160, same input rules as Knob, accessible role Slider); treadle = side-view pedal
whose angle follows the first knob param (Position/Volume) + knobs.
No art carries a real logo, brand name, model number or a copied shape (e.g. no round fuzz face, no
diamond grille cloth pattern, no script logos); nameplates show the Valeton catalog effect name.

## Alive (phase 3)
- **Listener** (`app/audio.py`): `QProcess` `["pw-record", "--target", "gp200_stereo_clean", "--format",
  "f32", "--rate", "48000", "--channels", "2", "-"]`; reads stdout chunks, computes per 1024-frame block:
  peak/RMS dBFS per channel (`levels`), and every 4096 frames a pitch estimate (`pitch_hz`, YIN-style on
  the mono mix, 60–1400 Hz) → note name + cents (`note_of`). Signals throttled to 30 Hz (levels) and
  12 Hz (pitch). Starts when the window becomes visible, stops (terminate, then kill after 1 s) on hide/
  minimise/quit. Process error/exit → `available = False` → "Sin audio".
- **Meter**: "OUT" jack becomes a meter jack: 2 bars 6×64, gradient `T.meter_lo` → `T.meter_hi` →
  `T.danger` above −3 dBFS, peak-hold tick 1 s; dB scale ticks −48/−24/−12/−6/0. Mini meter (2 × 4×16)
  in the top bar.
- **Cable glow**: inner line opacity = 0.5 + 0.5 × normalised RMS of the output (same value along all lit
  links; we only measure the output, not per block — no fake per-unit metering).
- **Tuner**: top-bar button "Afinador" toggles a strip (h 96) over the top of the board: note 48 medium,
  octave 18, Hz mono 13, horizontal ±50 cent scale with a needle that moves (Behavior 80 ms); in tune (±3)
  = needle and note in `T.ok`, else `T.text` with arrows ◀ ▶ indicating which way. No signal: "Toca una
  cuerda" `dim`. Esc / button closes. Pure listening: never mutes or switches the pedal.
- **Transitions**: on `loaded` units fade 0→1 and rise 8→0 px, staggered 25 ms in chain order (11 × 25 +
  120 ≤ 400 ms); effect change cross-fades the face/art 200 ms; toggle: footswitch scales 0.94→1 (100 ms)
  and LED glow fades 150 ms; programmatic value changes (load/discard/Claude rewrite) animate knob
  pointers 250 ms, user drags never animate. `GP200_MOTION=0` (`T.motion` false) → every duration 0.

## Tokens (`app/theme.py`; existing ones unchanged)
New (hex only here; values are a starting point, the implementer checks contrast of each `ink` on its
`body`/`face` ≥ 4.5:1 and adjusts):

| Token | Value | Use |
|---|---|---|
| `chassis_base` | `#2a2f36` | mix base for phase-1 stompboxes |
| `cable`, `jack` | `#15171a`, `#9aa3ab` | patch cable rubber, jack sleeves |
| `metal`, `metal_dark` | `#c3c9ce`, `#6b737a` | footswitches, trim |
| `knob_cap`, `knob_cap_hi`, `knob_skirt`, `knob_knurl` | `#1b1d21`, `#3c4048`, `#2b2e34`, `#4a4f57` | default knob |
| `bevel_hi`, `shadow` | `#26ffffff`, `#8c000000` | top highlight, drop shadow |
| `scrim` | `#66000000` | drawer scrim |
| `pilot` | `#e0453a` | amp jewel ON |
| `ok` | `#7fc8a9` | tuner in tune (same hue as EQ, text paired) |
| `meter_lo`, `meter_hi` | `#5fb8d6`, `#e0b050` | meter gradient |
| `font_value` | 24 | knob popup value |
| `cell_w, cell_h, cell_gap` | 92, 144, 12 | board grid |
| `knob_big, knob_mini` | 64, 16 | close-up / unit knobs |
| `w_wide, w_medium` | 1440, 1100 | layout breakpoints |
| `dur_s, dur_m, dur_l` | 100, 200, 400 (0 when `motion` is False) | animation budgets |
| `motion` | bool, `GP200_MOTION != "0"` | reduced motion |
| `chassis` | dict family → `{body, face, ink, knob}`: `od_green` `#3f6b4b/#4c7d58/#f2f5ef/black`, `dist_orange` `#b4592c/#c96a38/#ffffff/black`, `fuzz_violet` `#4f4380/#5e5196/#ffffff/chrome`, `metal_black` `#1f2125/#2a2d32/#e8eaec/black`, `brushed` `#9aa4ac/#b6bec4/#14171a/black`, `cream` `#d8cfb2/#e6dec4/#1b1c1f/black`, `gate_grey` `#4f5861/#5e6873/#ffffff/black`, `eq_white` `#c9d0d5/#dde2e6/#14171a/black`, `treadle_black` `#202226/#2b2e33/#e8eaec/chrome`, `brit_gold` `#1b1c1f/#b8975a/#14130f/cream`, `tweed` `#b49a63/#c8ccd0/#14171a/chrome`, `blackface` `#18191c/#26282c/#e8eaec/black`, `copper` `#2a1f1a/#9a6a45/#fff6ec/cream`, `steel` `#202326/#7c848c/#0e1012/black`, `graphite` `#24272c/#3a3f46/#ffffff/black`, `grille_wheat` `#9c8a6a`, `grille_silver` `#8f969c`, `grille_black` `#2a2c30`, `rack_dark` `#23282e/#2e343b/#ffffff/black` (display bg `#0c1416`) | gear art |

Knob cap variants (`knob` key): `black` = default tokens; `cream` = cap `#e6dfcb`/hi `#f6f1e3`, pointer
`#1b1c1f`; `chrome` = cap `#9ea6ad`/hi `#e2e6e9`, pointer `#1b1c1f`.

### Tokens in QML
`theme.qml_tokens()` returns a plain dict (all token names → values, colours as `#AARRGGBB` strings, which
QML parses natively) and the engine sets it as context property `T` (QVariantMap). QML reads `T.accent`,
`T.chassis.od_green.body`, etc. No hex in `.qml` files (grep check). `T.glass` drives the window fill.

### Glass in QML
`ApplicationWindow { color: "transparent" }` when `T.glass`, a root `Rectangle` filled with `T.bg`; else
`color: T.bg` opaque. Plates = translucent `Rectangle`s (`T.plate`, border `T.plate_border`), never a
second blur (no MultiEffect blur on plates — MultiEffect is used only for unit shadows and LED glow).
`QGuiApplication.setDesktopFileName("gp200")` kept (app_id for the Hyprland opacity rule). Qt Quick
Controls style forced to "Basic" (`QQuickStyle.setStyle("Basic")`) and restyled with tokens; Menus,
ComboBox popups, ToolTips on `T.popup_bg` (opaque).

## States
| State | Look |
|---|---|
| Empty (no slot) | board: IN and OUT jacks joined by one dim cable; centre glyph 48 `ink_off` + "Elige un slot para ver su cadena" 14 `dim`; compact adds a ghost button "Elegir slot" that opens the slot drawer; close-up hidden; header actions hidden |
| Scanning | 003 (cards "…", pill "Leyendo la pedalera…") |
| Loading a slot | units drawn as ghosts (chassis outline 1 px `ink_off`, no labels/knobs/LED), status "Leyendo 34B…"; close-up disabled |
| Clean / Dirty / Factory dirty | 003 (chip, warn dot on card, Guardar solid/ghost, factory hint) |
| Guard (dirty, other slot asked) | 003 inline bar under the header: "¿Descartar cambios de 34B?" + "Descartar y cambiar" / "Seguir editando" |
| Busy "save" / "claude" | 2 px indeterminate accent bar on the board plate top edge; board and close-up opacity 0.5 and disabled; status 003 copy; chats locked (003 copy) |
| Error | 003: danger pill in the failing area (scan → slot pill, workbench → status pill) |
| Drag in progress | dragged unit scale 1.05 + stronger shadow, follows pointer; 3 px accent drop bar (h 112) in the target gap; Esc cancels |
| No audio (phase 3) | OUT jack meter bars hidden, "Sin audio" 12 `dim` under it; tuner button disabled, tooltip "No llega audio de la pedalera" |
| Tuner, no signal | "Toca una cuerda" |

## Interactions
- **Unit**: click = select (close-up shows it); click on the footswitch/LED zone (bottom 36 px of the art) =
  toggle; double-click = toggle; focus (Tab moves through units in chain order) then Space = toggle,
  ←/→ = select neighbour, Ctrl+←/→ = move one place, Enter = focus the close-up's effect picker;
  context menu: "Mover a la izquierda", "Mover a la derecha", "Encender"/"Apagar", "Cambiar efecto…".
  Drag (press + move > 8 px) = reorder; drop index = nearest gap in chain order (wraps across rows) →
  `board.moveTo(block, index)`.
- **Close-up**: effect picker (type to filter, Enter applies), big footswitch = toggle, knobs per Knob.
- **Slot grid**: 003 (click/Enter open, arrows, search, Esc clears, context "Abrir", reload).
- **Top bar**: Ctrl+1/Ctrl+2 tabs; compact/medium: Ctrl+B slot drawer, Ctrl+J chat drawer; phase 3
  Ctrl+T tuner. Ctrl+S save (when dirty and allowed).
- **Chat**: 003 (Enter sends, new-chat button).
- Every icon-only button has a Spanish tooltip and `Accessible.name`.

## Copy (Spanish; 003 copy not listed stays)
- Jacks: "Guitarra", "Salida"
- Top bar tooltips: "Slots (Ctrl+B)", "Chat (Ctrl+J)", "Afinador (Ctrl+T)"
- Empty compact button: "Elegir slot"
- Footswitch tooltip/accessible: "Apagar" / "Encender"; unit accessible name "AMP · UK 800 · encendido"
- Knob popup: "<param> <valor>"; tuner: "Toca una cuerda", "Afinado"; audio: "Sin audio",
  "No llega audio de la pedalera"
- Chip tooltip in narrow header: "Sin guardar"

## Model / view split
- **Unchanged**: `Pedal`, `Workbench`, `ChatHub`, `ChatSession` (constitution); `gp200_app.py` keeps the
  wiring role of 003's `MainWindow` (scan, lock, send, wrote) but as plain functions/a `Shell` QObject,
  no widgets.
- **`app/bridge.py`** (view-models, no pedal state of their own; all properties `notify`-ed):
  - `Board(QObject)` wraps `Workbench` (+ `Pedal` for status): properties `open` (bool), `slotLabel`,
    `name`, `dirty`, `factory`, `busy` (""/"save"/"claude"), `loading`, `status`, `statusError`,
    `order` (list of 11 block codes), `units` (map block → `{effect, on, desc, kind, family, mini:[3 values]}`),
    `selected`, `params` (list of the selected effect's catalog params with `locked`; changes only when
    block/effect changes so knob delegates survive drags), `values` (map param → value, changes on every
    edit), `effects` (names for the selected block), `guard` (label or ""), `freeSlots`;
    slots `openSlot(int)`, `select(str)`, `toggle(str)`, `move(str,int)`, `moveTo(str,int)`,
    `setParam(str,float)`, `setEffect(str)`, `rename(str)`, `save()`, `saveAs(int)`, `discard()`,
    `confirmSwitch()`, `cancelSwitch()`, `defaultOf(str)`. All forward to the existing `Workbench` methods.
  - `ChatView(QObject)` per panel (slot / global): properties `title`, `html`, `locked` (reason or ""),
    `running`; slots `send(str)`, `reset()`; rebinds to `ChatHub.session(key)` on slot change.
  - Slots grid: QML `ListModel` of 255 rows filled once; `Connections` to `Pedal.slot_name(int,str)` →
    `setProperty(row, "name", …)` (per-row update, no 255× array rebuild). `slot_matches` (003) exposed as
    a `Board` slot for the filter.
- **Pure, tested** (new): `unit_view(preset, block)` (mini knob values, on, effect) and `chain_view` in
  `app/bridge.py`'s pure part or `model.py` (phase 1); `art_for` in `app/art.py` (phase 2); `level_db`,
  `pitch_hz`, `note_of` in `app/audio.py` (phase 3, tested on synthetic sines incl. 82.41 Hz E2, 110 Hz,
  329.63 Hz, silence).
- **Workers**: MIDI unchanged (Pedal worker). Audio = `QProcess` (`Listener` in `app/audio.py`, numpy on
  small chunks in the UI thread, each < 2 ms; if profiling shows > 5 ms move it to a `QThread`).
- **QML files** (`app/qml/`, one component each): `Main.qml`, `TopBar.qml`, `SlotGrid.qml`,
  `Pedalboard.qml`, `Unit.qml` (cell: selection, input, Loader for art), `Stompbox.qml`, `Cable.qml`,
  `Jack.qml`, `CloseUp.qml`, `Knob.qml`, `ValuePopup.qml`, `Footswitch.qml`, `ParamPills.qml`,
  `HeaderBar.qml`, `InlineBar.qml`, `ChatPane.qml`, `StatusPill.qml`; phase 2: `AmpHead.qml`,
  `Cabinet.qml`, `RackUnit.qml`, `Fader.qml`, `Treadle.qml`, `faces/` close-up faces per kind;
  phase 3: `Meter.qml`, `Tuner.qml`.

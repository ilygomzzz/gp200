# 003 — Glass UI: design

Status: approved 2026-11-22. Style inspiration only (no runtime link): desk-ui's glass philosophy and its
`glass` "Acero" skin values; Hyprland `~/Personalization/dotfiles/.config/hypr/config/{decorations,colors,windowrules}.lua`.
Current look: `specs/002-preset-workbench/shots/B-dirty.png`.

## Direction
A pedalboard under frosted glass. The window is one sheet of glass in the app's own dusk-blue tint;
everything inside is a lighter plate on it, never a second blur. The one bold element is the **chain**:
coloured stompbox tiles joined by a patch cable, footswitch LEDs glowing in the block's colour. Everything
else stays quiet: foam-grey text, steel-blue accent only on the selected thing, glyphs instead of words
where a glyph is unambiguous (block code text is always kept next to its glyph).

## Main window (default 1440×880, min 1300×640; all numbers px)

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 16                                                                                                 │
│ ◉ GP-200JR   ( Presets | Chat general )                                     top bar h48            │
│ 12                                                                                                 │
│┌ slot plate 312 ──────┐ 12 ┌ centre 732 ──────────────────────────────────────┐ 12 ┌ chat 340 ────┐│
││ ⌕ Buscar slot o nombre⟳│  │ (34B)  Crunch AZ           ● Sin guardar         │    │ 󰭹 Chat · 34B  ⊕││
││ h32                   │   │  h48 title 24             Descartar Guardar en… [Guardar]│ h32         ││
││ 1 ┌A────┐┌B────┐┌C────┐│  │┌ chain plate h140 ───────────────────────────────┐│    │┌ log ────────┐││
││   │1A   ││1B   ││1C   │││  ││▔▔▔▔ ▔▔▔▔ ▔▔▔▔ ▔▔▔▔ ▔▔▔▔ ▔▔▔▔ ▔▔▔▔ ▔▔▔▔ ▔▔▔▔ ▔▔▔▔ ▔▔▔▔ ││    ││ Tú: …       │││
││   │Clean││Lead ││Funk │││  ││ ⇈    ◠    ϟ    ▣    ⊘    ◫    ≋    ∿    ↻    ≈    ◢  ││    ││ Claude: …   │││
││   └─────┘└─────┘└─────┘│  ││PRE──WAH──DST──AMP──NR───CAB──EQ───MOD──DLY──RVB──VOL ││    ││             │││
││ 2 ┌─────┐┌─────┐┌─────┐│  ││P-   V-   Gre  UK   Gate SUP  Gui  Detu Anal Room Volu ││    ││             │││
││   …                   │   ││Boost Wah en OD 800  1    ZEP  EQ1  ne   og               ││    │└─────────────┘││
││34 ┌╌╌╌╌╌┐┌─────┐┌╌╌╌╌╌┐│  ││ ●    ○    ●   [●]   ○    ●    ○    ○    ●    ●    ○  ││    │ hint 13 dim   ││
││   ╎34A  ╎│34B •││╎34C ╎││  │└ tiles 56×116, gap 8, padding 12 ─────────────────┘│    │┌ ✎ input h40 ➤┐││
││   ╎vacío╎│Crun…│╎vacío╎││  │┌ editor plate ───────────────────────────────────┐│    │└──────────────┘││
││   └╌╌╌╌╌┘└─────┘└╌╌╌╌╌┘│  ││ (▣)  [ UK 800             ▾]                 (⏻) ││    └───────────────┘│
││ cards 84×52, gap 4     │  ││ 40   Marshall® JCM800                      40     ││                     │
││ …85                   │   ││                                                   ││                     │
││ ✓ Listo     (pill)    │   ││  ╭─╮    ╭─╮    ╭─╮    ╭─╮    ╭─╮    ╭─╮           ││                     │
│└──────────────────────┘│  ││ ( 80 ) ( 50 ) ( 50 ) ( 50 ) ( 50 ) ( 50 )   knob   ││                     │
│                         │  ││  Gain  Presence Volume Bass Middle Treble 80×96   ││                     │
│                         │  ││  [Modo ▾]  (●━ Brillo)   switch/combo pills h32   ││                     │
│                         │  │└───────────────────────────────────────────────────┘│                     │
│                         │  │ ✓ Pedalera en 34B · cambios en vivo   status pill h28│                     │
│ 16                                                                                                  │
└────────────────────────────────────────────────────────────────────────────────────────────────────┘
```
- Outer padding 16; columns 312 | flex (732 at default size) | 340, gaps 12; columns stay in the existing
  `QSplitter` (handles 12 wide, invisible until hover → `sel_fill`).
- Top bar = the `QTabWidget`'s tab bar styled as a segmented pill (h32, r16); app glyph + "GP-200JR"
  (18, medium) as its top-left corner widget. "Chat general" tab: the general `ChatPanel` full width.
- Slot plate: search field (h32, r16, field colours) + reload icon button (32×32) on one row; bank grid
  in a `QScrollArea`: bank number column 28 (12, `ink_dim`, right-aligned, centred on the row) + 3 cards
  84×52, gap 4, row gap 4. Card: label 12 bold `ink`, name 12 `ink_dim` up to 2 lines elided.
- Chain plate: 11 tiles 56×116, gap 8, padding 12 (720 total; scrolls horizontally below that, as 002).
  Tile: 4 px band in block colour along the top (inside the radius), glyph 24 px centred at y 30,
  block code 12 bold at y 52, effect name 12 two lines at y 66–94, LED Ø10 at y 104.
  Cable: 3 px line through the gaps at y 58 (tile mid-height); each segment takes the colour of the tile
  on its left at 70 % alpha if that tile is ON, else `ink_off` (bypass still passes signal).
  Drop indicator (drag): 2 px `accent` bar, as 002.
- Editor plate: header row h56: glyph disc Ø40 (block colour fill 25 %, glyph in block colour), effect
  picker (editable `QComboBox`, pill h36, min 240, stretch), power footswitch Ø40 at right. Desc line
  13 `ink_dim` under the picker. Body: knob grid, cells 80×96, gap 8, columns = as many as fit
  (8 at default size; catalog max is 13 params → 2 rows). Below the knobs, one flow row of switch pills
  and combo pills (h32). Note line (DLY Time) 13 `warn` above the knobs.
- Knob (80×96): dial Ø56 at top; 270° track arc 4 px `ink_off`, value arc 4 px block colour; value text
  centred in the dial, mono 13 `ink`; name 12 `ink_dim` below, elided to 80. Focus = 2 px `accent` ring
  around the dial. Disabled = arcs `ink_off`, value `ink_soft`, lock glyph replaces the value.
- Status pill (h28, r14, `plate` fill): glyph + text 13. Below the slot grid (scan) and below the editor
  (workbench), as in 002.
- Chat plate: header h32 (title 14 bold elided + icon button "new chat"); log = `QTextBrowser`
  transparent, document stylesheet from tokens; hint 13 `ink_dim`; input pill h40 with send icon button inside.
- Inline bars of 002 (discard guard, "Guardar en") become plates with a 4 px left `warn` edge, same copy and buttons.

## Tokens (`app/theme.py`)
Existing names stay (widgets already use them) with new values; new names added. Hex only here.
The app's own fixed palette; values borrowed from desk-ui's glass skin for family resemblance only.

| Token | Value | Source / use |
|---|---|---|
| `font` | "Noto Sans" | desk-ui glass font |
| `icon_font` | "JetBrainsMono Nerd Font Propo" | desk-ui `iconFont` |
| `mono` | "JetBrainsMono Nerd Font Mono" | raw data only (knob values, params) |
| `font_small, font_body, font_desc, font_title, font_display` | 12, 14, 13, 18, 24 | scale; min 12 |
| `text` (= ink) | `#ffffff` | main text |
| `dim` (= inkDim) | `#b4cbcd` | foam: secondary text, labels |
| `ink_soft` | `#73ffffff` | disabled text, placeholders |
| `ink_off` | `#40ffffff` | tracks, off LED ring, bypass cable |
| `accent` / `accent_deep` / `accent_text` | `#5a86a8` / `#25456a` / `#ffffff` | Acero skin; selection + primary button only |
| `danger` | `#e67c73` | desk-ui danger |
| `warn` | `#e0b050` | dirty, notes (kept) |
| `dusk`, `dusk_dark` | `#132238`, `#0a111d` | desk-ui |
| `tint` | `#132238` | window glass colour, fixed (no desk-ui file is read) |
| `glass_alpha` | 0.55 | window fill alpha over the blur (desk-ui gadgets use 0.4; higher for text) |
| `glass` | bool, set by `apply()` | True only on Wayland with `HYPRLAND_INSTANCE_SIGNATURE` and `GP200_GLASS` ≠ "0" |
| `bg` | glass: `tint` at `glass_alpha`; else opaque mix of `dusk_dark` and `tint` at `glass_alpha` | window |
| `plate`, `plate_border` | `#0fffffff`, `#554a6e8d` (= borderFaint) | inner panels |
| `sel_fill`, `sel_border` | `#24ffffff`, `#40ffffff` | hover / pressed / card outline |
| `field_bg`, `field_border` | `#4d0a111d`, `#2effffff` | inputs, combos, search |
| `popup_bg` | `#f20a111d` | menus, combo popups, tooltips (opaque) |
| `base`, `alt`, `button` | `field_bg`, `plate`, `sel_fill` | Fusion palette roles |
| `user`, `tool` | `#9cc3dd`, `#8a9aa8` | chat HTML (opaque hex: rich text) |
| `led_on` | removed → LED uses the block colour | |
| `block_colors` | PRE `#d4c45c`, WAH `#c99a66`, DST `#e0874f`, AMP `#e8b04e`, NR `#8fa3b3`, CAB `#a68c78`, EQ `#7fc8a9`, MOD `#a98be0`, DLY `#5fb8d6`, RVB `#6f93e0`, VOL `#b4cbcd` | category colours (not accent) |
| `glyphs` | name → codepoint, see below | icons |
| `s1..s6` | 4, 8, 12, 16, 24, 32 | spacing |
| `r_plate`, `r_card`, `r_pill` | 20, 8 (plate 20 − padding 12), 999 → height/2 | concentric radii; chain tiles 12 (20 − padding 8) |

Glyphs (Nerd Fonts `nf-md-*` names; the implementer resolves codepoints from the Nerd Fonts glyph list and
checks each renders with `icon_font`; if one is missing pick the closest `nf-md` glyph and note it):
PRE `chevron_double_up`, WAH `foot_print`, DST `lightning_bolt`, AMP `amplifier`, NR `volume_off`,
CAB `speaker`, EQ `equalizer`, MOD `sine_wave`, DLY `repeat`, RVB `waves`, VOL `volume_high`;
UI: app `guitar_electric`, search `magnify`, reload `refresh`, power `power`, lock `lock`, ok `check_circle`,
busy `progress_clock`, error `alert_circle`, new chat `chat_plus`, send `send`, chat `chat`, empty `guitar_pick`.

### Glass mechanics
- `theme.apply(app)`: Fusion, palette from tokens (Window role transparent when `glass`), one app QSS for
  `QFrame#plate`, `QPushButton` (ghost: transparent + `sel_border`; `#primary`: accent solid; icon buttons
  `#icon`: 32×32 round), `QLineEdit`/`QComboBox` (field pill), `QTabBar` (segmented pill), thin
  `QScrollBar`s (6 px, `sel_border` handle), `QMenu`/`QComboBox QAbstractItemView`/`QToolTip` on `popup_bg`.
- `main()`: `app.setDesktopFileName("gp200")` → Wayland app_id `gp200` (matches `gp200.desktop`, its icon,
  and the Hyprland rule). `MainWindow` sets `WA_TranslucentBackground` when `theme.glass` and paints `bg`.
- Hyprland already blurs every window (`decoration.blur.enabled = BLUR = true`, size 6, passes 4, xray) and
  fades windows to 0.94/0.82. Rule to add (Personalization `config/windowrules.lua`, "Opacity Overrides"):
  `hl.window_rule({ match = { class = "^gp200$" }, opacity = "1.0 override" })` — the app's own alpha decides,
  text stays fully opaque. No blur rule needed.
- Fallback (no Hyprland, X11, offscreen, `GP200_GLASS=0`): opaque `bg`, plates identical; contrast checked on
  the opaque mix.
- Contrast: `text` on `bg`(opaque mix, any tint) ≥ 7:1; `dim` ≥ 4.5:1; block colours are never text on
  plates except glyphs (≥ 3:1 as UI components). The block code is always text in `text`/`dim`, so colour
  never carries state alone (LED on/off also differs in shape: filled vs ring).

## States
| State | Look |
|---|---|
| Empty (no slot open) | centre = `empty` glyph 48 `ink_off` + "Elige un slot para ver su cadena" 14 `dim`; header actions hidden; chat hint as 002 |
| Scanning | cards show label + "…"; scan pill `busy` glyph "Leyendo la pedalera…" |
| Loading a slot | header shows label, tiles show "…" with grey LEDs, editor disabled; status "Leyendo 34B…" (002 copy) |
| Clean | Guardar disabled (ghost, `ink_soft`), no chip |
| Dirty | chip "● Sin guardar" `warn`; card gets a 6 px `warn` dot top-right; Guardar = accent solid; Descartar/Guardar en… enabled |
| Factory slot dirty | Guardar disabled, chip "Preset de fábrica: guárdalo en un slot libre" `warn` |
| Busy "save" | 2 px indeterminate `accent` bar on top edge of the chain plate (`QProgressBar` range 0,0); chain+editor disabled (50 % opacity look); status "Guardando 34B…"; chats locked "Espera a que termine de guardar" |
| Busy "claude" | same bar; status "Claude está usando la pedalera…"; chat input locked "Claude está respondiendo…" |
| Error | status pill `error` glyph + text in `danger`, in the area that failed (scan → slot pill, workbench → editor pill) |
| No search result | grid area: "Ningún slot coincide" 13 `dim` |
| Unknown effect | editor desc "Efecto sin catálogo: solo se puede cambiar por otro", no knobs |

## Interactions
- **Slot grid**: click/Enter = `slot_chosen`; ←/→ within a bank row, ↑/↓ across banks (same column), focus
  ring 2 px `accent`; current slot = `accent` outline + `sel_fill`; typing in search filters rows (a bank row
  stays if any card matches label or name, case-insensitive); Esc in search clears it; context menu "Abrir".
  Reload button = `reload_clicked`.
- **Chain**: unchanged from 002 (click select, double-click/Space toggle, drag or Ctrl+←/→ reorder, ←/→
  step, context menu). Hover tile = `sel_fill`.
- **Knob**: `QDial` subclass (keeps Qt's keyboard: arrows 1 step, PgUp/PgDn 10 steps, Home/End; wheel 1 step;
  accessibility). Mouse: vertical drag, 200 px = full range, Shift = ×0.2 fine; no circular drag. Context menu:
  "Escribir valor…" (inline `QDoubleSpinBox` over the dial, Enter applies, Esc cancels), "Valor por defecto".
  Emits through the same `cb(name, value)` as 002's `ParamRow`; value step/decimals as 002.
- **Power footswitch** (`QPushButton` checkable, round): click/Space = `toggled`; tooltip "Apagar"/"Encender";
  accessible name "Encendido"/"Apagado".
- **Switch params**: checkable pill `QPushButton` (text = param name; checked = block colour 25 % fill + ring).
  **Combo params**: pill `QComboBox`, label = param name as placeholder prefix "Nombre: opción".
- **Chat**: Enter sends, send icon button = Enter, new-chat icon button = 002's "Nueva conversación".
- **Tabs**: Ctrl+1 / Ctrl+2 switch Presets / Chat general (new, one line each).
- Ctrl+S save (002) unchanged.

## Copy (Spanish; 002 strings not listed stay as they are)
- "Elige un slot para ver su cadena" (centre empty state)
- "Buscar slot o nombre" (search placeholder), "Ningún slot coincide"
- "vacío" (empty card), card tooltip "34B · Crunch AZ" / "34A · vacío"
- Tooltips: "Releer la pedalera", "Nueva conversación", "Enviar (Enter)", "Apagar", "Encender"
- Knob menu: "Escribir valor…", "Valor por defecto"
- "● Sin guardar", "Preset de fábrica: guárdalo en un slot libre", "Guardar", "Descartar", "Guardar en…" (kept)

## Model / view split
No model change. `Pedal`, `Workbench`, `ChatHub`, `ChatSession` and their signals are untouched; every widget
keeps its 002 public API so `gp200_app.py` wiring stays as is:
- `SlotList` (rewritten in `widgets/slot_list.py`): same signals `slot_chosen`, `reload_clicked`; same
  methods `set_name`, `set_dirty`, `set_current`, `set_status`, attribute `names`. Internally one painted
  grid widget in a `QScrollArea` (like `ChainStrip`'s `_Inner`). The filter is a pure function
  `slot_matches(label, name, query)` in `app/model.py` next to `free_slots`, with a unit test.
- `ChainStrip`/`PedalTile`: same signals; only `paintEvent` and the cable painting change.
- `BlockEditor`: same signals; `ParamRow` keeps its `set_value`/`cb` contract but builds a `Knob`
  (new `widgets/knob.py`), pill switch or pill combo.
- `ChatPanel`, `WorkbenchView`: same API; layout/objectNames/glyph buttons change; `WorkbenchView` gains the
  busy bar driven by the existing `busy_changed`.
- No new workers; nothing new touches `Device`; no file reads added.

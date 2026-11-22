# 003 — Glass UI (graphical re-skin of the workbench)

Status: **approved by the user 2026-11-22** (design, constitution Look change, Hyprland rule, renumbering).

## Problem
The 002 workbench works but reads as a form: a 255-row text list of slots, tiles that are just
block abbreviations, a param grid of label + slider + spinbox per row, flat grey Fusion panels
(see `specs/002-preset-workbench/shots/B-dirty.png`). It looks unrelated to the user's desktop
(desk-ui: blurred translucent "liquid glass" panels, steel/foam palette, Noto Sans + Nerd Font glyphs).
User, verbatim: "lo que quiero es una UI que no sea full texto, que tenga cosas que tenga esos estilos
de glass del desk-ui".

## Goal
Same app, same behaviour, but graphical and in the desk-ui family:
1. **Glass window**: translucent window blurred by Hyprland (one glass layer), inner areas are
   lighter "plates" (desk-ui rule: never glass on glass). Opaque tinted fallback off Hyprland.
2. **Own fixed glass palette in `theme.py`**, following desk-ui's style philosophy (one glass sheet, plates,
   no glass on glass, every thing its own colour; values inspired by its `glass` "Acero" skin). The app is
   fully independent of desk-ui at runtime: it reads no desk-ui file or state.
3. **Pedalboard chain**: block tiles with a per-block-type colour and glyph, a footswitch LED, and a
   patch cable drawn through the chain (lit through ON blocks, dim through OFF ones).
4. **Knobs** instead of label+slider+spinbox for `knob` params; pill toggles for switches; pill combos.
5. **Slot browser as a bank grid**: one row per bank, three cards A/B/C (the pedal's own layout), search box.
6. **Chat** restyled as a plate with icon buttons; tabs become a segmented pill in a top bar.

## Out of scope
- Any protocol/model change (`bin/gp200`, `model.py`, `chat.py` logic). Workbench/Pedal/ChatHub signals unchanged.
- Animations (static UI; nothing animates in 003).
- Any runtime link to desk-ui (its theme, tint or skins), theme switching, light theme.
- Per-slot AMP colour in the slot grid (needs reading every slot, scan only reads names).
- Chat message bubbles beyond what a document stylesheet on `ChatSession.html` gives.
- Later spec: **SnapTone screen** (pick a NAM file → convert → upload to an empty SnapTone slot).
- Roadmap renumbered (approved): 003 glass UI, 004 tabs→preset, 005 guitar trainer, SnapTone screen later.

## Acceptance criteria
Screenshots go to `specs/003-glass-ui/shots/`. A–E are offscreen (`QT_QPA_PLATFORM=offscreen`, fake
pedal, opaque fallback); G is a real Hyprland capture.

### Screenshots
- **A-empty.png** (1440×880, no slot open): top bar with app glyph, "GP-200JR", segmented pill
  "Presets | Chat general" (Presets active). Left: bank grid, rows "1".."85" each with cards A/B/C;
  factory slots show their name, empty slots (34A+) are dashed and dim with "vacío". Centre: empty state
  = large pedal glyph + "Elige un slot para ver su cadena". Right: chat plate with hint. No QListWidget,
  no grey Fusion frames, no loose text rows.
- **B-open.png** (slot 34B open, AMP selected, clean): header with "34B" pill, preset name as a large
  editable title, Guardar disabled. Chain = 11 tiles in signal order, each with its colour band, glyph,
  block code and effect name, LED lit in block colour when ON, grey ring when OFF; a cable runs left→right,
  bright through ON tiles, dim through OFF. AMP tile has the accent selection ring. Editor: AMP glyph disc,
  effect pill "UK 800", desc "Marshall® JCM800", power footswitch, 6 knobs (Gain…Treble) with arcs in AMP colour.
- **C-dirty.png**: after changing Gain: chip "● Sin guardar" (warn), slot card 34B shows a warn dot,
  Guardar is the accent solid button, Descartar/Guardar en… are ghost buttons.
- **D-busy.png**: Workbench busy = "save": thin accent progress bar on top of the chain plate, chain and
  editor dimmed and disabled, status pill "Guardando 34B…", chat input locked with "Espera a que termine de guardar".
- **E-error.png**: a scan failure shows a danger status pill with a warning glyph under the slot grid
  (text from `Pedal.failed`), nothing else breaks.
- **F-delay.png**: DLY selected: Time knob disabled with lock glyph, note text visible; a switch param shows a pill toggle.
- **G-glass.png** (real, Hyprland, `grim` of the app window geometry only, on an empty workspace over the
  wallpaper): wallpaper visibly blurred through the window background; plates readable; text fully opaque.

### Behaviour (real pedal, slot 34B or a free slot ≥ 34A)
- Everything in 002's acceptance list still passes: live edits audible, Guardar writes with backup and
  readback, Descartar restores, Guardar en… only offers free slots, dirty guard on slot switch, per-slot chat,
  Claude busy hold, Ctrl+S.
- Knob: vertical drag (≈ 200 px = full range), wheel = 1 step, arrows = 1 step, PgUp/PgDn = 10 steps,
  Home/End = min/max; each change sends one `set_param` exactly as the 002 slider did (no extra MIDI
  floods: values coalesce through the existing Workbench path).
- Knob context menu "Escribir valor…" opens an inline spinbox; "Valor por defecto" sets the catalog default.
- Slot grid: click or Enter opens, arrows move between cards (←→ inside a bank, ↑↓ across banks),
  typing in search filters by label or name; context menu "Abrir".
- Chain tiles keep 002's interactions: click select, double-click/Space toggle, drag or Ctrl+←/→ reorder,
  context menu (Mover a la izquierda/derecha, Encender/Apagar, Cambiar efecto…).
- Off Hyprland (or `QT_QPA_PLATFORM=offscreen`) the window is opaque with the same layout and readable contrast.

### Must not change
- `bin/gp200`, `app/model.py`, `app/chat.py` behaviour and all their signals; `tests/` keep passing
  (`python3 -m unittest discover tests`).
- No widget talks to `Device`; no hex outside `theme.py`; spacing multiples of 4; min font 12 px.

## Constitution change (approved, applied to `constitution.md` by the designer)
Section **Look** gains / changes:
- "Dark Fusion palette" → "Fusion + the app's own glass palette in `theme.py`".
- New: the window may be translucent (alpha only from `theme.glass_alpha`); real blur only from the
  compositor (Hyprland window rule), one glass layer, inner plates are translucent fills not blur;
  opaque fallback when not on Hyprland. Popups/menus are opaque.
- New: per-block **category colours** (`theme.block_colors`) are allowed for block identity; the accent
  stays reserved for the active/selected thing.
- New: glyph icons only from `theme.icon_font` (JetBrainsMono Nerd Font Propo) via named `theme.glyphs`;
  every icon-only button has a tooltip and accessible name in Spanish.

## Outside this repo (approved)
- `~/Personalization/dotfiles/.config/hypr/config/windowrules.lua`, next to the terminals opacity
  override: `class ^gp200$` → `opacity = "1.0 override"` (so Hyprland's 0.94/0.82 window opacity does not
  fade our text; blur is already global: `decoration.blur` enabled, xray). It goes there and not in
  desk-ui's `hypr/desk-ui.lua` because that file only owns Quickshell UI rules; app opacity overrides
  live in Personalization. Plus the `mapa/` note per the global rule.

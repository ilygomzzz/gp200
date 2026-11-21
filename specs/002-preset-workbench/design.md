# 002 — Design

## Layout (default window 1280×800, min 1000×640)

```
┌ Presets │ Chat general ──────────────────────────────────────────────────────────────────────────┐
│┌ slots 220 ─┐┌ workbench (flex, min 560) ──────────────────────────┐┌ chat 360 (min 280) ──────┐│
││ 33C Metal…  ││ 35A  [Crunch AZ________]  ● Sin guardar  [Descartar] [Guardar] ││ Chat · 35A Crunch AZ   ││
││▶35A Crunch  ││─────────────────────────────────────────────────────││──────────────────────────││
││ 35B (vacío) ││  ┌──┐┌──┐┌──┐┌━━┓┌──┐┌──┐┌──┐┌──┐┌──┐┌──┐┌──┐  strip ││ Tú: más ganancia         ││
││ 35C (vacío) ││  │PRE││WAH││DST│┃AMP┃│NR ││CAB││EQ ││MOD││DLY││RVB││VOL│  96 h ││ Claude: Subo Gain a 70…  ││
││ …           ││  │Comp││off ││TS9 │┃UK  ┃│…  ││   ││off││off││Ana││Room││   │       ││ ⚙ gp200 write 35A …     ││
││             ││  │ ●  ││ ○  ││ ●  │┃ ●  ┃│ ● ││ ● ││ ○ ││ ○ ││ ● ││ ● ││ ● │       ││                          ││
││             ││  └──┘└──┘└──┘┗━━┛└──┘ … (horizontal scroll if narrow)       ││                          ││
││             ││─────────────────────────────────────────────────────││                          ││
││             ││ AMP  [UK 800              ▾]            [■ Encendido] ││                          ││
││             ││      Marshall® JCM800                                 ││                          ││
││             ││ Gain      ━━━━━━━━━●━━━━━━━━━━━━━━━  [ 55 ]           ││                          ││
││             ││ Bass      ━━━━━━●━━━━━━━━━━━━━━━━━━  [ 45 ]           ││                          ││
││             ││ …  (QScrollArea, one row per catalog param)            ││                          ││
││             ││─────────────────────────────────────────────────────││ [Pregunta o pide un cambio…]││
││[⟳ Releer]   ││ Pedalera en 35A · cambios en vivo             (status)││                          ││
│└─────────────┘└─────────────────────────────────────────────────────┘└──────────────────────────┘│
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```
- Three-pane `QSplitter` (220 / flex / 360). Chat pane collapsible via splitter handle (children not collapsible below min).
- Header row 40 px: slot label (font_title, mono not needed), name `QLineEdit` 16 chars max, ASCII validator (`[ -~]{0,16}`), width 200; dirty marker; Descartar (secondary); Guardar (primary = accent bg).
- Chain strip: 11 tiles, 52×84, gap 4, padding 8 → 612 px; inside `QScrollArea` (horizontal only). Tile = block code (font_small, bold) / effect name (font_small, 2 lines, elided) / LED dot 8 px + "off" text when off.
- Block editor: label column 120, slider flexible, value `QSpinBox`/`QDoubleSpinBox` 64 px mono (step from catalog `step`). `switch` param → `QCheckBox`; `combox` → `QComboBox` with option names.
- Status line 24 px at the bottom of the workbench (also where workbench errors appear).
- Empty state (no slot selected): strip and editor replaced by centred dim text "Elige un slot de la lista para ver su cadena y charlar sobre él." Chat panel shows the same hint, input disabled.

## Theme tokens (`app/theme.py`, new file)
Moved from 001's palette + new ones (marked *new*):
| token | value | use |
|---|---|---|
| `bg` | #202124 | window |
| `base` | #17181a | inputs, lists, tiles |
| `alt` | #26272a | alternate rows, editor bg |
| `button` | #2c2d30 | buttons |
| `text` | #dddddd | text |
| `dim` | #777777 | empty slots, off blocks, hints |
| `accent` | #3d6fb3 | selected tile/slot, primary button |
| `accent_text` | #ffffff | text on accent |
| `danger` | #ff8888 | errors |
| `user` | #88ccff | "Tú:" in chat |
| `tool` | #888888 | ⚙ tool lines |
| `led_on` *new* | #6fbf73 | block LED on |
| `warn` *new* | #e0b050 | "Sin guardar", factory-overwrite note |
| `drop` *new* | = accent | drop indicator line (2 px) |
| `s1..s4` | 4, 8, 12, 16 | spacing |
| `radius` | 6 | tiles, buttons |
| `font_small` / `font_body` / `font_title` | 12 / 14 / 18 px | captions / body / slot label |
| `mono` | "monospace" | param values, tool lines |
Plus `apply(app)` that sets Fusion + palette (moved from `main()`) and a small app-wide stylesheet built from tokens (tile/primary button only).

## States
| state | what shows |
|---|---|
| loading slot | strip tiles dim with "…", editor disabled, status "Leyendo 35A…" (read ≈ 60 ms, usually invisible) |
| clean | Guardar/Descartar disabled, no marker |
| dirty | "● Sin guardar" in `warn`; Guardar/Descartar enabled; slot list row shows a trailing "•" |
| applying live edit | nothing modal; status "Aplicando…" only if the queue is > 300 ms behind |
| saving | whole workbench disabled except status: "Guardando 35A… (n/11)" → "Guardado y verificado" or `danger` "Guardado, pero la relectura difiere: <first problem>" (stays dirty) |
| factory slot (1A–33C) | live edits allowed; Guardar disabled + `warn` hint "Preset de fábrica: guárdalo en un slot libre"; "Guardar en…" enabled when dirty |
| any slot, "Guardar en…" | button opens an inline row: `QComboBox` of free slots (name == "It's GP-200JR", 85C excluded, first free from 34A preselected; if none: "No hay slots libres") + [Guardar aquí] [Cancelar]. Writes `working` to the target via `write_preset`, then the workbench opens the target (pedal selects it). Available on user slots too |
| Claude busy | strip + editor disabled, overlay-free inline note in status "Claude está usando la pedalera…"; Guardar disabled |
| pedal busy (save) and user sends chat | chat input disabled, placeholder "Espera a que termine de guardar" |
| error (device missing / read failed) | `danger` text in the status line of the area that failed (slot list status or workbench status); retry = ⟳ Releer or reselecting the slot |
| dirty + other slot clicked | inline bar under the header (warn left border): "¿Descartar cambios de 35A?" [Descartar y cambiar] [Seguir editando]; the list selection reverts until one is chosen |
| slot clicked while Claude runs | no select, no read (MIDI held): view shows the last read of that slot if cached, else tiles "…"; status "Claude está usando la pedalera: 35A se leerá cuando termine"; read (not select) happens after the run |
| chat restored | transcript from `chats.json` rendered; a dim line "Conversación anterior · se continúa" above the input |
| Delay `Time` param | slider disabled + caption "Lo fija el tempo del preset (120 BPM = 500 ms); aún no se puede cambiar." |
| effect not in catalog (`#0x…`) | tile shows the hex id; editor shows "Efecto sin catálogo: solo se puede cambiar por otro" with picker enabled |

## Interactions
| action | mouse | keyboard | context menu (tile) |
|---|---|---|---|
| select block | click tile | ←/→ moves selection, Tab into editor | — |
| reorder | drag tile, drop line between tiles | Ctrl+←/Ctrl+→ | "Mover a la izquierda" / "Mover a la derecha" |
| toggle | double-click tile, or editor switch | Space | "Encender" / "Apagar" |
| change effect | editor picker | picker focus + type to filter | "Cambiar efecto…" (focuses picker) |
| param | slider / spinbox / wheel | arrows, PgUp/PgDn | — |
| rename | header field, applied on Enter/focus-out | — | — |
| open + select slot | click slot (selects on the pedal and reads it) | ↑/↓ + Enter on list | — |
| new chat | chat header button "Nueva conversación" | — | — |
| save / discard | buttons | Ctrl+S (no Esc: discarding needs the button, review 002) | — |

Effect picker: editable `QComboBox` with `QCompleter` (MatchContains, case-insensitive), items = `effects_for(block)` sorted by name, each item's tooltip and the line under it = catalog `desc` (real gear, e.g. "Marshall® JCM800"). "SnapTone N" appear as named in the CLI (1–5 AMP, 6–10 DST).

When does the pedal switch? On **click** (user decision): `msg_select(slot)` + read, status "Pedalera en 35A". Edits then go straight to the edit buffer ("Pedalera en 35A · cambios en vivo"). Exceptions: dirty guard and Claude-active (see States).

## Copy (Spanish, exact)
Tabs: "Presets", "Chat general". Buttons: "Guardar", "Guardar en…", "Guardar aquí", "Cancelar", "Descartar", "Descartar y cambiar", "Seguir editando", "Nueva conversación", "⟳ Releer". Hints: "Preset de fábrica: guárdalo en un slot libre", "No hay slots libres", "¿Descartar cambios de {slot}?", "Claude está usando la pedalera: {slot} se leerá cuando termine", "Conversación anterior · se continúa". Marker: "● Sin guardar". Chat title: "Chat · {slot} {name}" / "Chat general". Chat placeholder: "Pregunta o pide un cambio sobre {slot}… (Enter)" / global: "Pide un sonido, un cambio… (Enter)". Chat empty state: "Pregúntale a Claude por este preset: qué hace cada bloque, cómo acercarlo a un sonido, qué pastilla usar." Status: "Leyendo la pedalera…", "Listo", "Leyendo {slot}…", "Pedalera en {slot} · cambios en vivo", "Guardando {slot}… ({n}/11)", "Guardado y verificado", "Cambios descartados", "Claude está usando la pedalera…", "Claude ha reescrito {slot}; tus cambios sin guardar se han sustituido". Errors prefixed "⚠ ".

## Model / view split
### `app/model.py`
- **Pure helpers** (unit-tested): `effects_for(block)` → `[(eid, info)]` sorted; `move_block(order, block, delta)` → new order (clamped); `edit_msgs(preset, edit)` → `(new_preset, [(msg_bytes, gap_s)])` for edits `("effect", block, name)`, `("param", block, pname, value)`, `("toggle", block, on)`, `("order", order)`. Effect: `msg_effect` gap 0.4 then every catalog default via `msg_param` 0.04 with the first one resent last (same as `g.push.params`); params dict replaced by catalog defaults. Param: one `msg_param`, sent twice if it is the block's first param write since its effect change (`preset` carries no such state → `Workbench` keeps a `fresh` set and passes it). Validation reuses catalog ranges (clamp to min/max, options by id).
- **`Pedal(QObject)`** — the only owner of MIDI. One worker `QThread` with a priority queue: `HIGH` (edits, read current slot, save, claude hold) before `LOW` (slot-list scan, one job per slot so edits interleave). Each job opens `g.Device()`, runs, closes, under the existing module lock `MIDI`. Param jobs are coalesced by `(block, idx)` (latest value wins). Signals: `slot_name(int, str)`, `preset_read(int, dict)`, `progress(str)`, `failed(str area, str msg)`, `busy_changed(str|None)` (`None`, `"save"`, `"claude"`). Methods: `scan(slots)`, `read(slot)`, `apply(slot, msgs)`, `save(slot, preset)` (calls `g.write_preset`), `select(slot)`, `hold_for_claude()` → enqueues a job that holds the lock until `release_claude()` (UI thread never waits on the lock).
- **`Workbench(QObject)`** — edit buffer for one slot. State: `slot`, `stored` (decoded), `working` (same JSON format `gp200 write` accepts), `dirty`, `selected_block`, `factory` (slot < 99). Signals: `loaded(dict)`, `changed(dict)`, `dirty_changed(bool)`, `block_selected(str)`, `saved(str)`. Methods: `open(slot)` (select + read; read only while Claude holds the pedal), `save()` (refuses factory slots), `save_as(target)` (refuses factory targets and 85C), `free_slots(names)` (pure, tested), `set_effect`, `set_param`, `toggle`, `move`, `rename`, `save()`, `discard()` (= `msg_select(slot)` + reread → working = stored), `reload_after_claude()`. Each edit: update `working` immediately (UI responsive), then `pedal.apply(slot, msgs)` (the pedal is already on the slot since `open`).
### `app/chat.py`
- Pure: `parse_event`, `touched_slots` (moved from 001), `system_prompt(context, preset=None, dirty=False)` → global text (001's SYSTEM) or + "Context: slot {label} '{name}'. Current preset as the user hears it (unsaved live edits: {yes/no}): {compact JSON without '#n' params}. To change it run `gp200 write {label} <file>`; the app re-reads the slot after you finish."
- **`ChatStore`** (pure-ish, tested): `load(path)` / `save(path, data)` for `~/.local/share/gp200/chats.json` = `{"<slot label>": {"session": "<id>", "html": "<transcript>"}}`; atomic write (temp file in the same dir + `os.replace`); unreadable/invalid file → `{}` (and left in place, renamed `chats.json.bad`). Saved after each finished run and on "Nueva conversación" (entry removed). Path validated: only that fixed path.
- **`ChatSession(QObject)`**: one per context key (`"global"` or slot int), holds `session_id`, transcript HTML, `QProcess`. Signals `line(str who, str text, str color_token)`, `running_changed(bool)`, `wrote_slots(list)`. Only one run app-wide: `ChatHub` (dict of sessions + `pedal.hold_for_claude()`/`release_claude()` around each run); args identical to 001 (`--allowedTools` unchanged).
### `app/widgets/`
`slot_list.py` (SlotList), `chain_strip.py` (ChainStrip + PedalTile, drag/drop via `QDrag` with mime `application/x-gp200-block`), `block_editor.py` (BlockEditor + ParamRow), `chat_panel.py` (ChatPanel, binds to a `ChatSession`), `workbench_view.py` (header + dirty bar + strip + editor + status). `app/gp200_app.py` keeps only `MainWindow` + `main()` (~60 lines). Widgets only render model signals and call model methods.

### `bin/gp200` (protocol layer)
Extract `write_preset(dev, slot, new, log=print)` from `cmd_write` → returns `(backup_path, probs)` and raises/returns errors instead of `sys.exit` where the app needs it (catching `SystemExit` as 001 does is acceptable). `cmd_write` calls it; CLI output unchanged. `push` gains an optional `progress(n)` callback replacing the stderr print (CLI passes the print).

## Constitution change
None. (Keeping the global chat is allowed: "one conversation per context (global or per slot)".)

# 002 review notes (implementer)
Hardware, test slot 35A (restored to "It's GP-200JR" from backups/20261121-122512-35A.json; params of the empty slot show noise on readback, name restored).
- Live edits (effect, param, toggle, reorder) via `Workbench` on 35A: `gp200 show 35A` unchanged afterwards; Descartar -> working == stored. Audibility not checked (no ear).
- Factory source 12A: edit live, Guardar refused with hint, `save_as(35A)` wrote with backup + "Guardando 35A… (n/11)"; `gp200 show 12A` unchanged. Found + fixed: factory presets carry a foreign-module effect in off blocks (DST "Super OD") and Delay Time 4.0 (out of range) -> `model.clean`. Delay Time is ignored in the readback diff (tempo overwrites it).
- Guardar on 35A: backup created, "Guardado y verificado".
- NOT done on hardware: after `save_as` from a factory slot with a differing readback the workbench stays on the source (only opens the target on a clean save); real Claude runs / chat persistence across restart (no `claude` invoked; unit-tested store only); full-window run with a real 255-slot scan; click-select UI (offscreen only, shots in shots/).

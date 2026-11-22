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

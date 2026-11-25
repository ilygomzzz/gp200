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

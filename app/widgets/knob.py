from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QFontMetrics, QKeySequence, QPainter, QPen, QShortcut
from PyQt6.QtWidgets import QDial, QDoubleSpinBox, QMenu

import theme

W, H, DIAL = 80, 96, 56
DRAG_PX = 200  # vertical drag for the full range


class Knob(QDial):
    """Integer steps 0..n; `value(i)` = min + i*step. valueChanged(i) is the only output (ParamRow maps it)."""

    def __init__(self, p, color, locked=False):
        super().__init__()
        self.p, self.color, self.locked = p, color, locked
        self.step = p["step"] or 1
        self.mn, self.dec = p["min"], 0 if self.step >= 1 else 2
        self.setRange(0, round((p["max"] - p["min"]) / self.step))
        self.setSingleStep(1)
        self.setPageStep(10)
        self.setNotchesVisible(False)
        self.setFixedSize(W, H)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setToolTip(p["name"].strip())
        self.setAccessibleName(p["name"].strip())
        self.setEnabled(not locked)
        self.press = None
        self.edit = QDoubleSpinBox(self)
        self.edit.setRange(p["min"], p["max"])
        self.edit.setSingleStep(self.step)
        self.edit.setDecimals(self.dec)
        self.edit.setGeometry(4, 18, 72, 24)
        self.edit.hide()
        self.edit.editingFinished.connect(self._apply)
        sc = QShortcut(QKeySequence("Esc"), self.edit, lambda: (self.edit.hide(), self.update()))
        sc.setContext(Qt.ShortcutContext.WidgetShortcut)

    def real(self, i=None):
        return self.mn + (self.value() if i is None else i) * self.step

    def set_real(self, v):
        self.setValue(round((v - self.mn) / self.step))

    def _apply(self):
        if self.edit.isVisible():
            self.edit.hide()
            self.set_real(self.edit.value())
            self.setFocus()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        on = self.isEnabled() and not self.locked
        r = QRectF((W - DIAL) / 2, 4, DIAL, DIAL)
        arc = r.adjusted(4, 4, -4, -4)
        p.setBrush(theme.q(theme.plate))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(r)
        if self.hasFocus():
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.setPen(QPen(theme.q(theme.accent), 2))
            p.drawEllipse(r.adjusted(-1, -1, 1, 1))
        pen = QPen(theme.q(theme.ink_off), 4)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(pen)
        p.drawArc(arc, 225 * 16, -270 * 16)
        span = self.maximum() - self.minimum()
        if on and span and self.value() > self.minimum():
            pen.setColor(theme.q(self.color))
            p.setPen(pen)
            p.drawArc(arc, 225 * 16, round(-270 * 16 * (self.value() - self.minimum()) / span))
        if self.locked:
            p.setFont(theme.ifont(18))
            p.setPen(theme.q(theme.ink_soft))
            p.drawText(r, Qt.AlignmentFlag.AlignCenter, theme.glyphs["lock"])
        elif not self.edit.isVisible():
            f = p.font()
            f.setFamily(theme.mono)
            f.setPixelSize(theme.font_desc)
            p.setFont(f)
            p.setPen(theme.q(theme.text if on else theme.ink_soft))
            p.drawText(r, Qt.AlignmentFlag.AlignCenter, f"{self.real():.{self.dec}f}")
        f = p.font()
        f.setFamily(theme.font)
        f.setPixelSize(theme.font_small)
        p.setFont(f)
        p.setPen(theme.q(theme.dim if on else theme.ink_soft))
        p.drawText(QRectF(0, DIAL + 8, W, 20), Qt.AlignmentFlag.AlignCenter,
                   QFontMetrics(f).elidedText(self.p["name"].strip(), Qt.TextElideMode.ElideRight, W))

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.press = (e.position().y(), self.value())
            self.setFocus()

    def mouseMoveEvent(self, e):
        if self.press and e.buttons() & Qt.MouseButton.LeftButton:
            fine = 0.2 if e.modifiers() & Qt.KeyboardModifier.ShiftModifier else 1
            span = self.maximum() - self.minimum()
            self.setValue(round(self.press[1] + (self.press[0] - e.position().y()) / DRAG_PX * span * fine))

    def mouseReleaseEvent(self, _):
        self.press = None

    def wheelEvent(self, e):
        d = e.angleDelta().y()
        if d:
            self.setValue(self.value() + (1 if d > 0 else -1))
        e.accept()

    def contextMenuEvent(self, e):
        m = QMenu(self)
        m.addAction("Escribir valor…", self._open_edit)
        m.addAction("Valor por defecto", lambda: self.set_real(self.p["default"]))
        m.exec(e.globalPos())

    def _open_edit(self):
        self.edit.setValue(self.real())
        self.edit.show()
        self.edit.setFocus()
        self.edit.selectAll()
        self.update()

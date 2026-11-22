from PyQt6.QtCore import QMimeData, QPointF, QRectF, Qt, pyqtSignal
from PyQt6.QtGui import QDrag, QFont, QPainter, QPainterPath, QPen
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QMenu, QScrollArea, QWidget

import theme
from model import g

MIME = "application/x-gp200-block"


TW, TH = 56, 116


def wrap2(text, fm, w):
    """Up to two lines fitting w px: break at spaces, elide the rest."""
    words, lines = text.split(), [""]
    for wd in words:
        t = (lines[-1] + " " + wd).strip()
        if fm.horizontalAdvance(t) <= w or not lines[-1]:
            lines[-1] = t
        elif len(lines) == 1:
            lines.append(wd)
        else:
            lines[-1] = (lines[-1] + " " + wd)
    return [fm.elidedText(l, Qt.TextElideMode.ElideRight, w) for l in lines[:2]] if lines != [""] else []


class PedalTile(QWidget):
    clicked = pyqtSignal(str)
    toggled = pyqtSignal(str)
    step = pyqtSignal(str, int)  # select neighbour
    moved = pyqtSignal(str, int)
    edit_effect = pyqtSignal(str)

    def __init__(self, block):
        super().__init__()
        self.block, self.effect, self.on, self.selected, self.press, self.hover = block, "", False, False, None, False
        self.color = theme.block_colors[block]
        self.setFixedSize(TW, TH)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def set_state(self, effect, on):
        self.effect, self.on = effect, on
        self.setToolTip(f"{self.block} · {effect}")
        self.update()

    def enterEvent(self, _):
        self.hover = True
        self.update()

    def leaveEvent(self, _):
        self.hover = False
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        if not self.isEnabled():
            p.setOpacity(0.5)
        r = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        path = QPainterPath()
        path.addRoundedRect(r, theme.r_tile, theme.r_tile)
        p.setBrush(theme.q(theme.sel_fill if self.hover else theme.plate))
        p.setPen(QPen(theme.q(theme.accent if self.selected else theme.plate_border), 2 if self.selected else 1))
        p.drawPath(path)
        loading = self.effect == "…"
        col = theme.q(self.color, 1 if self.on and not loading else 0.45)
        p.save()
        p.setClipPath(path)
        p.fillRect(QRectF(0, 0, TW, 5), col)
        p.restore()
        p.setFont(theme.ifont(24))
        p.setPen(col)
        p.drawText(QRectF(0, 14, TW, 32), Qt.AlignmentFlag.AlignCenter, theme.glyphs[self.block])
        f = QFont(theme.font)
        f.setPixelSize(theme.font_small)
        f.setBold(True)
        p.setFont(f)
        p.setPen(theme.q(theme.text if self.on else theme.dim))
        p.drawText(QRectF(0, 46, TW, 16), Qt.AlignmentFlag.AlignCenter, self.block)
        f.setBold(False)
        p.setFont(f)
        p.setPen(theme.q(theme.dim))
        for i, line in enumerate(wrap2("" if loading else self.effect, p.fontMetrics(), TW - 8)):
            p.drawText(QRectF(4, 64 + i * 15, TW - 8, 15), Qt.AlignmentFlag.AlignCenter, line)
        c = QPointF(TW / 2, 104)
        if self.on and not loading:  # LED: filled + glow when ON, ring when OFF (shape differs, not only colour)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(theme.q(self.color, 0.25))
            p.drawEllipse(c, 8, 8)
            p.setBrush(theme.q(self.color))
            p.drawEllipse(c, 5, 5)
        else:
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.setPen(QPen(theme.q(theme.ink_soft), 1.5))
            p.drawEllipse(c, 4.5, 4.5)

    def mousePressEvent(self, e):
        self.press = e.position().toPoint()
        self.setFocus()
        self.clicked.emit(self.block)

    def mouseMoveEvent(self, e):
        if self.press and (e.position().toPoint() - self.press).manhattanLength() > 8:
            self.press = None
            mime = QMimeData()
            mime.setData(MIME, self.block.encode())
            drag = QDrag(self)
            drag.setMimeData(mime)
            drag.setPixmap(self.grab())
            drag.exec(Qt.DropAction.MoveAction)

    def mouseDoubleClickEvent(self, _):
        self.toggled.emit(self.block)

    def keyPressEvent(self, e):
        d = {Qt.Key.Key_Left: -1, Qt.Key.Key_Right: 1}.get(e.key())
        if d and e.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.moved.emit(self.block, d)
        elif d:
            self.step.emit(self.block, d)
        elif e.key() == Qt.Key.Key_Space:
            self.toggled.emit(self.block)
        else:
            super().keyPressEvent(e)

    def contextMenuEvent(self, e):
        m = QMenu(self)
        m.addAction("Mover a la izquierda", lambda: self.moved.emit(self.block, -1))
        m.addAction("Mover a la derecha", lambda: self.moved.emit(self.block, 1))
        m.addAction("Apagar" if self.on else "Encender", lambda: self.toggled.emit(self.block))
        m.addAction("Cambiar efecto…", lambda: self.edit_effect.emit(self.block))
        m.exec(e.globalPos())


class _Inner(QWidget):  # real subclass: PyQt only honours virtual overrides on classes
    def __init__(self, strip):
        super().__init__()
        self.strip = strip
        self.setAcceptDrops(True)

    def dragEnterEvent(self, e):
        if e.mimeData().hasFormat(MIME):
            e.acceptProposedAction()

    def dragMoveEvent(self, e):
        self.strip._drag_move(e)

    def dragLeaveEvent(self, e):
        self.strip._set_drop(None)

    def dropEvent(self, e):
        self.strip._drop(e)

    def paintEvent(self, e):
        self.strip._paint(e)


class ChainStrip(QScrollArea):
    select = pyqtSignal(str)
    toggle = pyqtSignal(str)
    move = pyqtSignal(str, int)
    move_to = pyqtSignal(str, int)
    edit_effect = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setObjectName("plate")
        self.inner, self.order, self.drop_x = _Inner(self), list(g.BLOCKS), None
        self.lay = QHBoxLayout(self.inner)
        self.lay.setSpacing(theme.s2)
        self.lay.setContentsMargins(theme.s3, theme.s3, theme.s3, theme.s3)
        self.tiles = {}
        for b in g.BLOCKS:
            t = self.tiles[b] = PedalTile(b)
            t.clicked.connect(self.select)
            t.toggled.connect(self.toggle)
            t.moved.connect(self.move)
            t.edit_effect.connect(self.edit_effect)
            t.step.connect(self._step)
            self.lay.addWidget(t)
        self.lay.addStretch()
        self.setWidget(self.inner)
        self.setWidgetResizable(True)
        self.setFixedHeight(TH + 2 * theme.s3)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def set_preset(self, p, selected=None, loading=False):
        self.order = p.get("order", list(g.BLOCKS)) if p else list(g.BLOCKS)
        for i, b in enumerate(self.order):
            t = self.tiles[b]
            self.lay.insertWidget(i, t)
            blk = p["blocks"][b] if p else None
            t.set_state(blk["effect"] if blk else "…", bool(blk and blk["on"]))
        self.set_selected(selected)

    def set_selected(self, block):
        for b, t in self.tiles.items():
            t.selected = b == block
            t.update()

    def _step(self, block, d):
        b = self.order[max(0, min(10, self.order.index(block) + d))]
        self.select.emit(b)
        self.tiles[b].setFocus()

    def _slot_at(self, x):
        return next((i for i, b in enumerate(self.order) if x < self.tiles[b].geometry().center().x()), 11)

    def _set_drop(self, x):
        self.drop_x = x
        self.inner.update()

    def _drag_move(self, e):
        i = self._slot_at(e.position().x())
        self._set_drop(self.tiles[self.order[i]].x() - 2 if i < 11 else self.tiles[self.order[10]].geometry().right() + 2)
        e.acceptProposedAction()

    def _drop(self, e):
        self._set_drop(None)
        self.move_to.emit(bytes(e.mimeData().data(MIME)).decode(), self._slot_at(e.position().x()))

    def _paint(self, _):
        p = QPainter(self.inner)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        y = theme.s3 + 58  # cable at tile mid-height; segments sit in the gaps, coloured by the tile on their left
        ts = [self.tiles[b] for b in self.order]
        edges = [(4, ts[0].x(), theme.ink_soft)]
        for i, t in enumerate(ts):
            nxt = ts[i + 1].x() if i < 10 else t.geometry().right() + 1 + theme.s3
            edges.append((t.geometry().right() + 1, nxt, theme.q(t.color, 0.7) if t.on else theme.q(theme.ink_off)))
        for x0, x1, c in edges:
            pen = QPen(theme.q(c), 3)
            pen.setCapStyle(Qt.PenCapStyle.FlatCap)
            p.setPen(pen)
            p.drawLine(int(x0), y, int(x1), y)
        if self.drop_x is not None:
            p.fillRect(int(self.drop_x) - 1, 8, 2, TH + 8, theme.q(theme.drop))

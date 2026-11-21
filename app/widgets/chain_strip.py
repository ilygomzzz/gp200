from PyQt6.QtCore import QMimeData, QPoint, QRectF, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QDrag, QFont, QPainter, QPen
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QMenu, QScrollArea, QWidget

import theme
from model import g

MIME = "application/x-gp200-block"


class PedalTile(QWidget):
    clicked = pyqtSignal(str)
    toggled = pyqtSignal(str)
    step = pyqtSignal(str, int)  # select neighbour
    moved = pyqtSignal(str, int)
    edit_effect = pyqtSignal(str)

    def __init__(self, block):
        super().__init__()
        self.block, self.effect, self.on, self.selected, self.press = block, "", False, False, None
        self.setFixedSize(52, 84)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def set_state(self, effect, on):
        self.effect, self.on = effect, on
        self.setToolTip(f"{self.block} · {effect}")
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        p.setBrush(QColor(theme.base))
        p.setPen(QPen(QColor(theme.accent if self.selected else theme.alt), 2))
        p.drawRoundedRect(r, theme.radius, theme.radius)
        col = QColor(theme.text if self.on else theme.dim)
        p.setPen(col)
        f = QFont()
        f.setPixelSize(theme.font_small)
        f.setBold(True)
        p.setFont(f)
        p.drawText(QRectF(0, 4, 52, 16), Qt.AlignmentFlag.AlignCenter, self.block)
        f.setBold(False)
        p.setFont(f)
        p.drawText(QRectF(4, 22, 44, 34), Qt.AlignmentFlag.AlignHCenter | Qt.TextFlag.TextWordWrap, self.fm_elide())
        p.setBrush(QColor(theme.led_on if self.on else theme.dim))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPoint(14 if not self.on else 26, 70), 4, 4)
        if not self.on:
            p.setPen(col)
            p.drawText(QRectF(20, 62, 30, 16), Qt.AlignmentFlag.AlignVCenter, "off")

    def fm_elide(self):  # two lines of ~7 chars
        return self.effect if len(self.effect) <= 14 else self.effect[:13] + "…"

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
        self.inner, self.order, self.drop_x = _Inner(self), list(g.BLOCKS), None
        self.lay = QHBoxLayout(self.inner)
        self.lay.setSpacing(theme.s1)
        self.lay.setContentsMargins(theme.s2, theme.s2, theme.s2, theme.s2)
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
        self.setFixedHeight(84 + 2 * theme.s2 + 16)
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
        if self.drop_x is not None:
            QPainter(self.inner).fillRect(int(self.drop_x) - 1, 4, 2, 92, QColor(theme.drop))

from PyQt6.QtCore import QPointF, QRectF, Qt, pyqtSignal
from PyQt6.QtGui import QFontMetrics, QKeySequence, QPainter, QPen, QShortcut
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QLineEdit, QMenu, QPushButton, QScrollArea, QVBoxLayout, QWidget

import theme
from model import EMPTY, g, slot_matches

CARD_H, GAP, NUM_W = 52, 4, 28


class _Grid(QWidget):
    """Painted bank grid: one row per bank, cards A/B/C. Owns focus, keyboard, mouse and the filter."""

    def __init__(self, owner):
        super().__init__()
        self.o, self.banks, self.focus_slot, self.tip = owner, list(range(g.NSLOTS // 3)), 0, None
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)
        self._size()

    def _size(self):
        self.setMinimumHeight(max(1, len(self.banks)) * (CARD_H + GAP) + GAP)

    def set_filter(self, query):
        o = self.o
        self.banks = [b for b in range(g.NSLOTS // 3) if any(
            slot_matches(g.slot_label(b * 3 + i), o.names.get(b * 3 + i), query) for i in range(3))]
        self._size()
        self.update()

    def _cw(self):
        return (self.width() - NUM_W - GAP * 3) / 3

    def _rect(self, slot):
        row = self.banks.index(slot // 3)
        w = self._cw()
        return QRectF(NUM_W + GAP + (slot % 3) * (w + GAP), GAP + row * (CARD_H + GAP), w, CARD_H)

    def _at(self, pt):
        row = int((pt.y() - GAP) // (CARD_H + GAP))
        col = int((pt.x() - NUM_W - GAP) // (self._cw() + GAP))
        if 0 <= row < len(self.banks) and 0 <= col < 3 and self._rect(self.banks[row] * 3 + col).contains(pt):
            return self.banks[row] * 3 + col

    def paintEvent(self, e):
        o, p = self.o, QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        f = p.font()
        f.setPixelSize(theme.font_small)
        p.setFont(f)
        fm = QFontMetrics(f)
        for bank in self.banks:
            r0 = self._rect(bank * 3)
            if r0.bottom() < e.rect().top() or r0.top() > e.rect().bottom():
                continue
            p.setPen(theme.q(theme.dim))
            p.drawText(QRectF(0, r0.top(), NUM_W, CARD_H), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, str(bank + 1))
            for s in range(bank * 3, bank * 3 + 3):
                r, name = self._rect(s), o.names.get(s)
                empty = name == EMPTY
                cur, foc = s == o.current, self.hasFocus() and s == self.focus_slot
                p.setBrush(theme.q(theme.sel_fill) if cur else theme.q(theme.plate))
                pen = QPen(theme.q(theme.accent if cur or foc else theme.sel_border if not empty else theme.ink_off), 2 if foc else 1)
                if empty and not cur:
                    pen.setStyle(Qt.PenStyle.DashLine)
                p.setPen(pen)
                p.drawRoundedRect(r.adjusted(1, 1, -1, -1), theme.r_card, theme.r_card)
                p.setPen(theme.q(theme.dim if empty or name is None else theme.text))
                b = p.font()
                b.setBold(True)
                p.setFont(b)
                p.drawText(QRectF(r.left() + 8, r.top() + 4, r.width() - 16, 16), Qt.AlignmentFlag.AlignLeft, g.slot_label(s))
                b.setBold(False)
                p.setFont(b)
                p.setPen(theme.q(theme.dim if empty or name is None else theme.text, 0.8 if not empty else None))
                txt = "…" if name is None else "vacío" if empty else name
                if empty or name is None:
                    p.setPen(theme.q(theme.ink_soft))
                p.drawText(QRectF(r.left() + 8, r.top() + 20, r.width() - 16, 28), Qt.TextFlag.TextWordWrap, fm.elidedText(txt, Qt.TextElideMode.ElideRight, int((r.width() - 16) * 2)))
                if s in o.dirty:
                    p.setBrush(theme.q(theme.warn))
                    p.setPen(Qt.PenStyle.NoPen)
                    p.drawEllipse(QPointF(r.right() - 9, r.top() + 9), 3, 3)
        if not self.banks:
            p.setPen(theme.q(theme.dim))
            p.drawText(self.rect().adjusted(0, theme.s5, 0, 0), Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop, "Ningún slot coincide")

    def mousePressEvent(self, e):
        s = self._at(e.position())
        if s is not None and e.button() == Qt.MouseButton.LeftButton:
            self.focus_slot = s
            self.setFocus()
            self.update()
            self.o.slot_chosen.emit(s)

    def mouseMoveEvent(self, e):
        s = self._at(e.position())
        if s != self.tip:
            self.tip = s
            n = self.o.names.get(s)
            self.setToolTip("" if s is None else f"{g.slot_label(s)} · {'vacío' if n == EMPTY else n or '…'}")

    def contextMenuEvent(self, e):
        s = self._at(e.pos())
        if s is not None:
            m = QMenu(self)
            m.addAction("Abrir", lambda: self.o.slot_chosen.emit(s))
            m.exec(e.globalPos())

    def keyPressEvent(self, e):
        k, s = e.key(), self.focus_slot
        if k in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space):
            return self.o.slot_chosen.emit(s)
        if not self.banks:
            return
        if s // 3 not in self.banks:
            s = self.banks[0] * 3
        row, col = self.banks.index(s // 3), s % 3
        d = {Qt.Key.Key_Left: (0, -1), Qt.Key.Key_Right: (0, 1), Qt.Key.Key_Up: (-1, 0), Qt.Key.Key_Down: (1, 0)}.get(k)
        if not d:
            return super().keyPressEvent(e)
        row, col = max(0, min(len(self.banks) - 1, row + d[0])), max(0, min(2, col + d[1]))
        self.focus_slot = self.banks[row] * 3 + col
        self.o.scroll.ensureVisible(0, int(self._rect(self.focus_slot).center().y()), 0, CARD_H)
        self.update()


class SlotList(QFrame):
    slot_chosen = pyqtSignal(int)  # click or Enter
    reload_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.names, self.dirty, self.current, self.failed = {}, set(), None, False
        self.search = QLineEdit()
        self.search.setPlaceholderText("Buscar slot o nombre")
        self.search.textChanged.connect(lambda t: self.grid.set_filter(t))
        mag = QLabel(theme.glyphs["search"], self.search)
        mag.setFont(theme.ifont(16))
        mag.setStyleSheet(f"color:{theme.dim}; background:transparent")
        mag.move(theme.s3, 6)
        self.search.setTextMargins(theme.s5, 0, 0, 0)
        sc = QShortcut(QKeySequence("Esc"), self.search, self.search.clear)  # Esc in search clears it
        sc.setContext(Qt.ShortcutContext.WidgetShortcut)
        btn = QPushButton(theme.glyphs["reload"])
        btn.setObjectName("icon")
        btn.setToolTip("Releer la pedalera")
        btn.setAccessibleName("Releer la pedalera")
        btn.clicked.connect(self.reload_clicked)
        self.grid, self.scroll = _Grid(self), QScrollArea()
        self.scroll.setWidget(self.grid)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self.status = QLabel()
        self.status.setObjectName("pill")
        self.setObjectName("plate")
        row = QHBoxLayout()
        row.addWidget(self.search)
        row.addWidget(btn)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(theme.s2, theme.s2, theme.s2, theme.s2)
        lay.addLayout(row)
        lay.addWidget(self.scroll, 1)
        lay.addWidget(self.status)
        self.set_status("Leyendo la pedalera…")

    def set_name(self, s, name):
        self.names[s] = name
        self.grid.update()

    def set_dirty(self, s, d):
        (self.dirty.add if d else self.dirty.discard)(s)
        self.grid.update()

    def set_current(self, s):
        self.current = s
        self.grid.focus_slot = s
        self.grid.update()

    def set_status(self, text, error=False):
        self.failed = error
        self.status.setToolTip(text)
        g_ = "error" if error else "busy" if text.endswith("…") else "ok"
        self.status.setText(f"{theme.icon_html(g_, theme.danger if error else None)}  {text}")
        self.status.setStyleSheet(f"color:{theme.danger}" if error else "")

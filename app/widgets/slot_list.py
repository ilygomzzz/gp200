from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QLabel, QListWidget, QListWidgetItem, QPushButton, QVBoxLayout, QWidget

import theme
from model import EMPTY, g


class SlotList(QWidget):
    slot_chosen = pyqtSignal(int)  # click or Enter
    reload_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.list, self.names, self.dirty = QListWidget(), {}, set()
        for s in range(g.NSLOTS):
            self.list.addItem(QListWidgetItem(f"{g.slot_label(s):>4}  …"))
        self.list.itemClicked.connect(lambda it: self.slot_chosen.emit(self.list.row(it)))
        self.list.itemActivated.connect(lambda it: self.slot_chosen.emit(self.list.row(it)))
        self.status = QLabel("Leyendo la pedalera…")
        self.status.setStyleSheet(f"color:{theme.dim}")
        btn = QPushButton("⟳ Releer")
        btn.clicked.connect(self.reload_clicked)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        for w in (self.list, self.status, btn):
            lay.addWidget(w)

    def _refresh(self, s):
        name = self.names.get(s)
        it = self.list.item(s)
        it.setText(f"{g.slot_label(s):>4}  " + ("…" if name is None else "(vacío)" if name == EMPTY else name) + (" •" if s in self.dirty else ""))
        it.setForeground(QColor(theme.dim if name in (None, EMPTY) else theme.text))

    def set_name(self, s, name):
        self.names[s] = name
        self._refresh(s)

    def set_dirty(self, s, d):
        (self.dirty.add if d else self.dirty.discard)(s)
        self._refresh(s)

    def set_current(self, s):
        self.list.setCurrentRow(s)

    def set_status(self, text, error=False):
        self.status.setText(text)
        self.status.setStyleSheet(f"color:{theme.danger if error else theme.dim}")

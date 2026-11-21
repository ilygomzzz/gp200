from PyQt6.QtCore import Qt
from PyQt6.QtGui import QShortcut, QKeySequence
from PyQt6.QtWidgets import (QComboBox, QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QStackedLayout,
                             QVBoxLayout, QWidget)
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtCore import QRegularExpression

import theme
from model import free_slots, g
from widgets.block_editor import BlockEditor
from widgets.chain_strip import ChainStrip

EMPTY_TEXT = "Elige un slot de la lista para ver su cadena y charlar sobre él."


class WorkbenchView(QWidget):
    def __init__(self, wb, slot_names):
        super().__init__()
        self.wb, self.slot_names = wb, slot_names  # slot_names(): {slot: name}
        self.label = QLabel()
        self.label.setStyleSheet(f"font-size:{theme.font_title}px; font-weight:bold")
        self.name = QLineEdit()
        self.name.setFixedWidth(200)
        self.name.setValidator(QRegularExpressionValidator(QRegularExpression("[ -~]{0,16}")))
        self.name.editingFinished.connect(self._rename)
        self.mark = QLabel("● Sin guardar")
        self.mark.setStyleSheet(f"color:{theme.warn}")
        self.discard_b, self.save_b, self.save_as_b = QPushButton("Descartar"), QPushButton("Guardar"), QPushButton("Guardar en…")
        self.save_b.setObjectName("primary")
        self.hint = QLabel("Preset de fábrica: guárdalo en un slot libre")
        self.hint.setStyleSheet(f"color:{theme.warn}")
        head = QHBoxLayout()
        for w in (self.label, self.name, self.mark, self.hint):
            head.addWidget(w)
        head.addStretch()
        for w in (self.discard_b, self.save_as_b, self.save_b):
            head.addWidget(w)
        self.bar = self._bar("", [("Descartar y cambiar", self._confirm), ("Seguir editando", self._cancel)])
        self.bar_text = self.bar.findChild(QLabel)
        self.sa_row = self._bar("Guardar en", [("Guardar aquí", self._save_here), ("Cancelar", lambda: self.sa_row.hide())])
        self.target = QComboBox()
        self.sa_row.layout().insertWidget(1, self.target)
        self.strip, self.editor = ChainStrip(), BlockEditor()
        self.empty = QLabel(EMPTY_TEXT)
        self.empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty.setStyleSheet(f"color:{theme.dim}")
        self.content = QWidget()
        cl = QVBoxLayout(self.content)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.addWidget(self.strip)
        cl.addWidget(self.editor, 1)
        self.stack = QStackedLayout()
        self.stack.addWidget(self.empty)
        self.stack.addWidget(self.content)
        self.status = QLabel("Leyendo la pedalera…")
        self.status.setFixedHeight(24)
        self.note = ""
        lay = QVBoxLayout(self)
        lay.addLayout(head)
        lay.addWidget(self.bar)
        lay.addWidget(self.sa_row)
        lay.addLayout(self.stack, 1)
        lay.addWidget(self.status)
        self.bar.hide(), self.sa_row.hide()
        self._wire()
        self.set_open(False)

    def _bar(self, text, buttons):
        f = QFrame()
        f.setObjectName("bar")
        lay = QHBoxLayout(f)
        lay.addWidget(QLabel(text))
        for t, fn in buttons:
            b = QPushButton(t)
            b.clicked.connect(fn)
            lay.addWidget(b)
        lay.addStretch()
        return f

    def _wire(self):
        wb, st, ed = self.wb, self.strip, self.editor
        st.select.connect(wb.select_block)
        st.toggle.connect(wb.toggle)
        st.move.connect(wb.move)
        st.move_to.connect(wb.move_to)
        st.edit_effect.connect(lambda b: (wb.select_block(b), ed.focus_picker()))
        ed.effect_changed.connect(wb.set_effect)
        ed.param_changed.connect(wb.set_param)
        ed.toggled.connect(wb.toggle)
        self.save_b.clicked.connect(wb.save)
        self.discard_b.clicked.connect(wb.discard)
        self.save_as_b.clicked.connect(self._open_save_as)
        wb.loading.connect(self._loading)
        wb.loaded.connect(self._render)
        wb.changed.connect(self._render)
        wb.block_selected.connect(lambda b: self._render(wb.working) if wb.working else None)
        wb.dirty_changed.connect(lambda _: self._buttons())
        wb.status.connect(self._status)
        wb.guard.connect(lambda lbl: (self.bar_text.setText(f"¿Descartar cambios de {lbl}?"), self.bar.show()))
        wb.busy_changed.connect(lambda _: self._buttons())
        QShortcut(QKeySequence("Ctrl+S"), self, wb.save)

    def set_open(self, on):
        self.stack.setCurrentIndex(1 if on else 0)
        for w in (self.label, self.name, self.mark, self.discard_b, self.save_b, self.save_as_b, self.hint):
            w.setVisible(on)
        self._buttons()

    def _loading(self, slot):
        self.set_open(True)
        self.label.setText(g.slot_label(slot))
        self.name.setText("")
        self.strip.set_preset(None, self.wb.selected_block)
        self.content.setEnabled(False)
        self.bar.hide()

    def _render(self, p):
        self.name.setText(p["name"]) if not self.name.hasFocus() else None
        self.label.setText(self.wb.label)
        self.strip.set_preset(p, self.wb.selected_block)
        self.editor.set_block(self.wb.selected_block, p)
        self._buttons()

    def _buttons(self):
        wb, busy = self.wb, self.wb.busy
        d = wb.dirty
        self.mark.setVisible(d and wb.slot is not None)
        self.discard_b.setEnabled(d and not busy)
        self.save_b.setEnabled(d and not busy and not wb.factory)
        self.save_as_b.setEnabled(d and not busy and wb.working is not None)
        self.hint.setVisible(wb.factory)
        self.content.setEnabled(wb.working is not None and not busy)
        self.name.setEnabled(not busy)

    def _status(self, text, err):
        self.status.setStyleSheet(f"color:{theme.danger if err else theme.text}")
        self.status.setText(text)

    def _rename(self):
        if self.wb.working and self.name.text() != self.wb.working["name"] and not self.wb.rename(self.name.text()):
            self.name.setText(self.wb.working["name"])

    def _confirm(self):
        self.bar.hide()
        self.wb.confirm_switch()

    def _cancel(self):
        self.bar.hide()
        self.wb.cancel_switch()

    def _open_save_as(self):
        free = free_slots(self.slot_names())
        self.target.clear()
        for s in free:
            self.target.addItem(g.slot_label(s), s)
        self.target.setCurrentIndex(0 if free else -1)
        if not free:
            self.target.addItem("No hay slots libres")
        self.sa_row.show()

    def _save_here(self):
        s = self.target.currentData()
        if s is not None:
            self.sa_row.hide()
            self.wb.save_as(s)

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (QCheckBox, QComboBox, QCompleter, QDoubleSpinBox, QGridLayout, QHBoxLayout, QLabel,
                             QScrollArea, QSlider, QVBoxLayout, QWidget)

import theme
from model import effects_for, g, snap_label


class ParamRow:
    """Label + slider + value (knob) or combo (options) or checkbox (switch); emits through `cb(name, value)`."""

    def __init__(self, grid, row, p, cb, locked):
        self.p, self.cb = p, cb
        grid.addWidget(QLabel(p["name"].strip()), row, 0)
        if p["type"] == "knob":
            step = p["step"] or 1
            self.slider, self.w = QSlider(Qt.Orientation.Horizontal), QDoubleSpinBox()
            self.slider.setRange(0, round((p["max"] - p["min"]) / step))
            self.w.setRange(p["min"], p["max"])
            self.w.setSingleStep(step)
            self.w.setDecimals(0 if step >= 1 else 2)
            self.w.setFixedWidth(72)
            self.w.setStyleSheet(f"font-family:{theme.mono}")
            self.slider.valueChanged.connect(lambda i: self.w.setValue(p["min"] + i * step))
            self.w.valueChanged.connect(lambda v: (self._sync(v), cb(p["name"], v)))
            grid.addWidget(self.slider, row, 1)
            grid.addWidget(self.w, row, 2)
            self.step = step
            if locked:
                self.slider.setEnabled(False)
                self.w.setEnabled(False)
        elif p.get("options"):
            self.w = QComboBox()
            for o in p["options"]:
                self.w.addItem(o["name"], o["id"])
            self.w.activated.connect(lambda i: cb(p["name"], self.w.itemData(i)))
            grid.addWidget(self.w, row, 1, 1, 2)
        else:
            self.w = QCheckBox()
            self.w.toggled.connect(lambda v: cb(p["name"], float(v)))
            grid.addWidget(self.w, row, 1, 1, 2)

    def _sync(self, v):
        self.slider.blockSignals(True)
        self.slider.setValue(round((v - self.p["min"]) / self.step))
        self.slider.blockSignals(False)

    def set_value(self, v):
        self.w.blockSignals(True)
        if isinstance(self.w, QDoubleSpinBox):
            self.w.setValue(v)
            self._sync(v)
        elif isinstance(self.w, QComboBox):
            self.w.setCurrentIndex(max(0, self.w.findData(v)))
        else:
            self.w.setChecked(bool(v))
        self.w.blockSignals(False)


class BlockEditor(QWidget):
    effect_changed = pyqtSignal(str, str)
    param_changed = pyqtSignal(str, str, float)
    toggled = pyqtSignal(str, bool)

    def __init__(self):
        super().__init__()
        self.block, self.key, self.rows = None, None, {}
        self.title, self.picker, self.on = QLabel(), QComboBox(), QCheckBox("Encendido")
        self.title.setStyleSheet(f"font-size:{theme.font_title}px; font-weight:bold")
        self.title.setFixedWidth(72)
        self.picker.setEditable(True)
        self.picker.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.picker.completer().setFilterMode(Qt.MatchFlag.MatchContains)
        self.picker.completer().setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.picker.textActivated.connect(lambda t: self.block and self.effect_changed.emit(self.block, t))
        self.on.clicked.connect(lambda v: self.block and self.toggled.emit(self.block, v))
        self.desc = QLabel()
        self.desc.setStyleSheet(f"color:{theme.dim}")
        self.note = QLabel()
        self.note.setStyleSheet(f"color:{theme.warn}")
        self.grid_host = QWidget()
        self.grid = QGridLayout(self.grid_host)
        self.grid.setColumnMinimumWidth(0, 120)
        self.grid.setColumnStretch(1, 1)
        scroll = QScrollArea()
        scroll.setWidget(self.grid_host)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        head = QHBoxLayout()
        for w, st in ((self.title, 0), (self.picker, 1), (self.on, 0)):
            head.addWidget(w, st)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(theme.s2, theme.s2, theme.s2, 0)
        for item in (head, self.desc, self.note, scroll):
            lay.addLayout(item) if hasattr(item, "addWidget") else lay.addWidget(item, 1 if item is scroll else 0)

    def focus_picker(self):
        self.picker.setFocus()
        self.picker.lineEdit().selectAll()

    def set_block(self, block, preset):
        blk = preset["blocks"][block]
        self.block = None  # silence signals while populating
        if self.key != (block, blk["effect"]):
            self.key = (block, blk["effect"])
            self._rebuild(block, blk["effect"])
        self.title.setText(block)
        self.on.setChecked(blk["on"])
        self.on.setText("Encendido" if blk["on"] else "Apagado")
        for name, row in self.rows.items():
            if name in blk["params"]:
                row.set_value(blk["params"][name])
        self.block = block

    def _rebuild(self, block, effect):
        while self.grid.count():
            self.grid.takeAt(0).widget().deleteLater()
        self.rows = {}
        for r in range(self.grid.rowCount()):
            self.grid.setRowStretch(r, 0)
        self.picker.blockSignals(True)
        self.picker.clear()
        for eid, info in effects_for(block):
            self.picker.addItem(snap_label(eid, info))
            self.picker.setItemData(self.picker.count() - 1, info.get("desc", ""), Qt.ItemDataRole.ToolTipRole)
        self.picker.setCurrentText(effect)
        self.picker.blockSignals(False)
        try:
            info = g.find_effect(block, effect)[1]
        except SystemExit:  # "#0x…" or an effect of another module (seen in factory presets)
            info = None
        self.desc.setText(info.get("desc", "") if info else "Efecto sin catálogo: solo se puede cambiar por otro")
        info = info or {"params": []}
        self.note.setText("")
        self.grid.setRowStretch(len(info["params"]), 1)  # keep rows compact
        for i, p in enumerate(info["params"]):
            locked = block == "DLY" and p["name"] == "Time"
            self.rows[p["name"]] = ParamRow(self.grid, i, p, lambda n, v: self.block and self.param_changed.emit(self.block, n, v), locked)
            if locked:
                self.note.setText("Time: lo fija el tempo del preset (120 BPM = 500 ms); aún no se puede cambiar.")

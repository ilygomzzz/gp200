from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QComboBox, QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget

import theme
from model import effects_for, g, snap_label
from widgets.knob import H as KH, W as KW, Knob


class ParamRow:
    """One catalog param: Knob (knob), pill combo (options) or pill toggle (switch); emits through `cb(name, value)`."""

    def __init__(self, p, cb, locked, color):
        self.p = p
        name = p["name"].strip()
        if p["type"] == "knob":
            self.w = Knob(p, color, locked)
            self.w.valueChanged.connect(lambda i: cb(p["name"], self.w.real(i)))
        elif p.get("options"):
            self.w = QComboBox()
            for o in p["options"]:
                self.w.addItem(f"{name}: {o['name']}", o["id"])
            self.w.activated.connect(lambda i: cb(p["name"], self.w.itemData(i)))
        else:
            self.w = QPushButton(name)
            self.w.setCheckable(True)
            self.w.setStyleSheet(f"QPushButton:checked {{ background:{theme.css(color, 0.25)}; border:1px solid {color}; }}")
            self.w.toggled.connect(lambda v: cb(p["name"], float(v)))

    def set_value(self, v):
        self.w.blockSignals(True)
        if isinstance(self.w, Knob):
            self.w.set_real(v)
        elif isinstance(self.w, QComboBox):
            self.w.setCurrentIndex(max(0, self.w.findData(v)))
        else:
            self.w.setChecked(bool(v))
        self.w.blockSignals(False)
        self.w.update()


class BlockEditor(QFrame):
    effect_changed = pyqtSignal(str, str)
    param_changed = pyqtSignal(str, str, float)
    toggled = pyqtSignal(str, bool)

    def __init__(self):
        super().__init__()
        self.setObjectName("plate")
        self.block, self.key, self.rows, self.color = None, None, {}, theme.text
        self.disc, self.picker, self.on = QLabel(), QComboBox(), QPushButton(theme.glyphs["power"])
        self.disc.setFixedSize(40, 40)
        self.disc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.disc.setFont(theme.ifont(22))
        self.picker.setFixedHeight(36)
        self.picker.setMinimumWidth(240)
        self.picker.setEditable(True)
        self.picker.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.picker.completer().setFilterMode(Qt.MatchFlag.MatchContains)
        self.picker.completer().setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.picker.textActivated.connect(lambda t: self.block and self.effect_changed.emit(self.block, t))
        self.on.setObjectName("power")
        self.on.setCheckable(True)
        self.on.clicked.connect(lambda v: self.block and self.toggled.emit(self.block, v))
        self.desc = QLabel()
        self.desc.setStyleSheet(f"color:{theme.dim}; font-size:{theme.font_desc}px")
        self.note = QLabel()
        self.note.setWordWrap(True)
        self.note.setStyleSheet(f"color:{theme.warn}; font-size:{theme.font_desc}px")
        self.knobs, self.pills = QWidget(), QHBoxLayout()
        self.grid = QGridLayout(self.knobs)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(theme.s2)
        self.grid.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        body = QWidget()
        bl = QVBoxLayout(body)
        bl.setContentsMargins(0, 0, 0, 0)
        bl.addWidget(self.note)
        bl.addWidget(self.knobs)
        bl.addLayout(self.pills)
        bl.addStretch()
        self.scroll = QScrollArea()
        self.scroll.setWidget(body)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        head = QHBoxLayout()
        head.setSpacing(theme.s3)
        head.addWidget(self.disc)
        head.addWidget(self.picker, 1)
        head.addWidget(self.on)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(theme.s4, theme.s3, theme.s4, theme.s3)
        lay.addLayout(head)
        lay.addWidget(self.desc)
        lay.addWidget(self.scroll, 1)

    def focus_picker(self):
        self.picker.setFocus()
        self.picker.lineEdit().selectAll()

    def set_block(self, block, preset):
        blk = preset["blocks"][block]
        self.block = None  # silence signals while populating
        if self.key != (block, blk["effect"]):
            self.key = (block, blk["effect"])
            self._rebuild(block, blk["effect"])
        self.on.setChecked(blk["on"])
        self.on.setToolTip("Apagar" if blk["on"] else "Encender")
        self.on.setAccessibleName("Encendido" if blk["on"] else "Apagado")
        for name, row in self.rows.items():
            if name in blk["params"]:
                row.set_value(blk["params"][name])
        self.block = block

    def _layout_knobs(self):
        knobs = [r.w for r in self.rows.values() if isinstance(r.w, Knob)]
        cols = max(1, (self.scroll.viewport().width() + theme.s2) // (KW + theme.s2))
        for i, w in enumerate(knobs):
            self.grid.addWidget(w, i // cols, i % cols)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._layout_knobs()

    def _rebuild(self, block, effect):
        for lay in (self.grid, self.pills):
            while lay.count():
                it = lay.takeAt(0)
                if it.widget():
                    it.widget().deleteLater()
        self.rows = {}
        self.color = theme.block_colors[block]
        self.disc.setText(theme.glyphs[block])
        self.disc.setToolTip(block)
        self.disc.setStyleSheet(f"background:{theme.css(self.color, 0.25)}; color:{self.color}; border-radius:20px")
        self.on.setStyleSheet(f"QPushButton:checked {{ background:{theme.css(self.color, 0.25)}; border:1px solid {self.color}; color:{self.color}; }}")
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
        cb = lambda n, v: self.block and self.param_changed.emit(self.block, n, v)
        for p in info["params"]:
            locked = block == "DLY" and p["name"] == "Time"
            self.rows[p["name"]] = r = ParamRow(p, cb, locked, self.color)
            if not isinstance(r.w, Knob):
                r.w.setFixedHeight(32)
                self.pills.addWidget(r.w)
            if locked:
                self.note.setText("Time: lo fija el tempo del preset (120 BPM = 500 ms); aún no se puede cambiar.")
        self.pills.addStretch()
        self._layout_knobs()

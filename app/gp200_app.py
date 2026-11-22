"""GP-200JR desktop app: preset workbench + chat with Claude (spec 002). Run: bin/gp200-app"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # app/ modules are top-level (theme, model, chat, widgets)

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QPainter, QShortcut
from PyQt6.QtWidgets import QApplication, QHBoxLayout, QLabel, QSplitter, QTabWidget, QVBoxLayout, QWidget  # noqa: E402

import theme  # noqa: E402
from chat import ChatHub, system_prompt  # noqa: E402
from model import Pedal, Workbench, g  # noqa: E402
from widgets.chat_panel import ChatPanel  # noqa: E402
from widgets.slot_list import SlotList  # noqa: E402
from widgets.workbench_view import WorkbenchView  # noqa: E402


class MainWindow(QWidget):
    def __init__(self, pedal=None, hub=None):
        super().__init__()
        self.setWindowTitle("GP-200JR")
        if theme.glass:
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(1440, 880)
        self.setMinimumSize(1300, 640)  # 240+740+260 panels + 2 handles + 32 padding
        self.pedal = pedal or Pedal()
        self.hub = hub or ChatHub(self.pedal)
        self.wb = Workbench(self.pedal)
        self.slots, self.chat, self.general = SlotList(), ChatPanel(), ChatPanel(global_ctx=True)
        self.view = WorkbenchView(self.wb, lambda: self.slots.names)

        split = QSplitter()
        for w, size in ((self.slots, 312), (self.view, 732), (self.chat, 340)):
            split.addWidget(w)
            w.setMinimumWidth({312: 240, 732: 740, 340: 260}[size])
        split.setSizes([312, 732, 340])
        split.setHandleWidth(theme.s3)
        split.setCollapsible(0, False), split.setCollapsible(1, False)
        tabs = QTabWidget()
        tabs.addTab(split, "Presets")
        tabs.addTab(self.general, "Chat general")
        brand = QLabel(f'{theme.icon_html("app")}  GP-200JR')
        brand.setStyleSheet(f"font-size:{theme.font_title}px; font-weight:500; padding-right:{theme.s4}px")
        tabs.setCornerWidget(brand, Qt.Corner.TopLeftCorner)
        for i in (0, 1):
            QShortcut(QKeySequence(f"Ctrl+{i + 1}"), self, lambda i=i: tabs.setCurrentIndex(i))
        lay = QVBoxLayout(self)
        lay.setContentsMargins(theme.s4, theme.s4, theme.s4, theme.s4)
        lay.addWidget(tabs)

        p, wb = self.pedal, self.wb
        p.slot_name.connect(self.slots.set_name)
        p.failed.connect(lambda area, m: area == "scan" and self.slots.set_status(m.removeprefix("⚠ "), True))
        self.slots.slot_chosen.connect(wb.request_open)
        self.slots.reload_clicked.connect(self._scan)
        wb.loading.connect(self._opened)
        wb.guard.connect(lambda _: self.slots.set_current(wb.slot))
        wb.dirty_changed.connect(lambda d: wb.slot is not None and self.slots.set_dirty(wb.slot, d))
        wb.busy_changed.connect(self._busy)
        p.scan_done.connect(lambda: self.slots.failed or self.slots.set_status("Listo"))
        self.chat.submitted.connect(lambda t: self._send(wb.label, t))
        self.general.submitted.connect(lambda t: self._send("global", t))
        self.chat.new_chat.connect(lambda: self.hub.reset(wb.label))
        self.general.new_chat.connect(lambda: self.hub.reset("global"))
        self.general.bind(self.hub.session("global"), "global", None)
        self.hub.running_changed.connect(lambda _: self._lock())
        self.hub.wrote_slots.connect(self._wrote)
        wb.changed.connect(lambda _: self._title())
        wb.loaded.connect(lambda _: self._title())
        self._scan()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)
        p.fillRect(self.rect(), theme.bg)

    def _scan(self):
        self.slots.set_status("Leyendo la pedalera…")
        self.pedal.scan(range(g.NSLOTS))

    def _opened(self, slot):
        self.slots.set_current(slot)
        self.view.set_open(True)
        self.chat.bind(self.hub.session(g.slot_label(slot)), g.slot_label(slot), f"Chat · {g.slot_label(slot)}")
        self._lock()

    def _title(self):
        if self.wb.working:
            self.chat.title.setText(f"Chat · {self.wb.label} {self.wb.working['name']}")

    def _busy(self, what):
        self._lock()

    def _lock(self):
        busy = self.wb.busy
        self.chat.set_locked("Espera a que termine de guardar" if busy == "save" else
                             "Claude está respondiendo…" if self.hub.active else None)
        self.general.set_locked("Espera a que termine de guardar" if busy == "save" else
                                "Claude está respondiendo…" if self.hub.active else None)
        if busy == "claude":
            self.view._status("Claude está usando la pedalera…", False)

    def _send(self, key, text):
        p = self.wb.working if key != "global" else None
        self.hub.send(key, text, system_prompt(key if p else None, p, self.wb.dirty))

    def _wrote(self, slots):
        self.wb.reload_after_claude(slots)
        if slots:
            self.pedal.scan(slots)

    def closeEvent(self, e):
        self.pedal.stop()
        super().closeEvent(e)


def main():
    app = QApplication(sys.argv)
    app.setDesktopFileName("gp200")  # Wayland app_id = gp200 (desktop entry, icon, Hyprland rule)
    theme.apply(app)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

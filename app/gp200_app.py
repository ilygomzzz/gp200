"""GP-200JR desktop app (Qt Quick, spec 004): pedalboard, workbench and chat with Claude. Run: bin/gp200-app"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # app/ modules are top-level (theme, model, chat, bridge)

from PyQt6.QtCore import QUrl  # noqa: E402
from PyQt6.QtGui import QGuiApplication  # noqa: E402
from PyQt6.QtQml import QQmlApplicationEngine  # noqa: E402
from PyQt6.QtQuick import QQuickWindow  # noqa: E402
from PyQt6.QtQuickControls2 import QQuickStyle  # noqa: E402

import art  # noqa: E402
import theme  # noqa: E402
from bridge import Board, ChatView  # noqa: E402
from chat import ChatHub  # noqa: E402
from model import Pedal, Workbench, g  # noqa: E402

QML = Path(__file__).resolve().parent / "qml" / "Main.qml"


class Shell:
    """Owns the model objects and the engine; wiring only (what 003's MainWindow did)."""

    def __init__(self, app, pedal=None, hub=None):
        theme.apply(app.platformName())
        QQuickStyle.setStyle("Basic")
        self.pedal = pedal or Pedal()
        self.hub = hub or ChatHub(self.pedal)
        self.wb = Workbench(self.pedal)
        self.board = Board(self.wb)
        self.slot_chat, self.global_chat = ChatView(self.hub, self.wb), ChatView(self.hub, self.wb, True)
        self.hub.wrote_slots.connect(self._wrote)
        self.engine = QQmlApplicationEngine()
        ctx = self.engine.rootContext()
        for name, obj in (("T", theme.qml_tokens()), ("R", art.load_manifest(theme.render_dir + "/manifest.json")), ("board", self.board), ("slotChat", self.slot_chat),
                          ("globalChat", self.global_chat), ("pedal", self.pedal)):
            ctx.setContextProperty(name, obj)
        self.engine.warnings.connect(lambda ws: [print(w.toString(), file=sys.stderr) for w in ws])
        self.engine.load(QUrl.fromLocalFile(str(QML)))
        app.aboutToQuit.connect(self.pedal.stop)
        self.board.rescan()

    def _wrote(self, slots):
        self.wb.reload_after_claude(slots)
        if slots:
            self.pedal.scan(slots)


def main():
    if theme.os.environ.get("GP200_GLASS") != "0":
        QQuickWindow.setDefaultAlphaBuffer(True)  # needed for the translucent glass window
    app = QGuiApplication(sys.argv)
    app.setDesktopFileName("gp200")  # Wayland app_id = gp200 (desktop entry, icon, Hyprland rule)
    shell = Shell(app)
    if not shell.engine.rootObjects():
        sys.exit(1)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

"""GP-200JR desktop app: preset list + chat with Claude (spec 001). Run: bin/gp200-app"""
import json
import os
import re
import sys
import threading
from importlib.machinery import SourceFileLoader
from pathlib import Path

from PyQt6.QtCore import QProcess, QProcessEnvironment, QThread, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPalette
from PyQt6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem,
                             QPlainTextEdit, QPushButton, QSplitter, QTabWidget, QTextBrowser, QVBoxLayout, QWidget)

ROOT = Path(__file__).resolve().parent.parent
g = SourceFileLoader("gp200", str(ROOT / "bin/gp200")).load_module()
EMPTY = "It's GP-200JR"
GUITAR = "Ibanez AZ24S1F"
MIDI = threading.Lock()  # raw MIDI is exclusive: one reader/writer at a time (app thread or a Claude run)
SYSTEM = (f"You are running inside the GP-200 desktop app's chat, not a terminal. Reply in Spanish, short. "
          f"You cannot use AskUserQuestion: ask questions as plain text and wait for the next message. "
          f"Use the gp200 skill/CLI for the pedal. The user's guitar is an {GUITAR}: recommend pickup "
          f"positions and adapt presets to it.")


def with_device(fn):
    """Open the pedal, run fn(dev), close. Returns (result, error string)."""
    with MIDI:
        try:
            dev = g.Device()
        except SystemExit as e:
            return None, str(e)
        try:
            return fn(dev), None
        except SystemExit as e:
            return None, str(e)
        finally:
            os.close(dev.fd)


def parse_event(line):
    """One stream-json line from `claude -p` -> list of (kind, payload); kinds: session, text, tool, done, error."""
    try:
        ev = json.loads(line)
    except ValueError:
        return []
    t, out = ev.get("type"), []
    if t == "system" and ev.get("subtype") == "init":
        out.append(("session", ev.get("session_id")))
    elif t == "assistant":
        for c in ev.get("message", {}).get("content", []):
            if c.get("type") == "text" and c["text"].strip():
                out.append(("text", c["text"].strip()))
            elif c.get("type") == "tool_use":
                inp = c.get("input", {})
                out.append(("tool", inp.get("command") or inp.get("file_path") or inp.get("skill") or c["name"]))
    elif t == "result":
        out.append(("error" if ev.get("is_error") else "done", ev.get("result", "")))
    return out


def touched_slots(command):
    """Slots a gp200 command writes/selects, e.g. 'gp200 write 34B x.json' -> ['34B']."""
    return re.findall(r"gp200\s+(?:write|select)\s+(\d+[ABCabc])\b", command)


class Loader(QThread):
    slot = pyqtSignal(int, str)
    failed = pyqtSignal(str)

    def __init__(self, slots):
        super().__init__()
        self.slots, self.stop, self.left = slots, False, []

    def run(self):
        def read_all(dev):
            for i, s in enumerate(self.slots):
                if self.stop:  # a Claude run wants the port; the rest is re-read afterwards
                    self.left = self.slots[i:]
                    return
                raw = dev.read(s)
                self.slot.emit(s, raw[28:44].split(b"\0")[0].decode("ascii", "replace"))
        _, err = with_device(read_all)
        if err:
            self.failed.emit(err)


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GP-200JR")
        self.resize(1000, 680)
        self.items, self.session, self.proc, self.pending, self.loader = {}, None, None, set(), None

        # presets tab
        self.slots = QListWidget()
        self.slots.currentRowChanged.connect(self.show_slot)
        self.slots.itemDoubleClicked.connect(self.select_slot)
        for s in range(g.NSLOTS):
            it = QListWidgetItem(f"{g.slot_label(s):>4}  …")
            self.slots.addItem(it)
            self.items[s] = it
        self.chain = QPlainTextEdit(readOnly=True)
        self.chain.setFont(QFont("monospace"))
        self.status = QLabel("Leyendo la pedalera…")
        reload_btn = QPushButton("⟳ Releer")
        reload_btn.clicked.connect(lambda: self.load(range(g.NSLOTS)))
        right = QVBoxLayout()
        right.addWidget(self.chain)
        bar = QHBoxLayout()
        bar.addWidget(self.status, 1)
        bar.addWidget(reload_btn)
        right.addLayout(bar)
        presets = QSplitter()
        presets.addWidget(self.slots)
        rw = QWidget()
        rw.setLayout(right)
        presets.addWidget(rw)
        presets.setSizes([260, 740])

        # chat tab
        self.log = QTextBrowser()
        self.log.setOpenExternalLinks(True)
        self.entry = QLineEdit(placeholderText="Pide un sonido, un cambio… (Enter)")
        self.entry.returnPressed.connect(self.send)
        chat = QWidget()
        cl = QVBoxLayout(chat)
        cl.addWidget(self.log)
        cl.addWidget(self.entry)

        tabs = QTabWidget()
        tabs.addTab(presets, "Presets")
        tabs.addTab(chat, "Chat")
        QVBoxLayout(self).addWidget(tabs)
        self.load(range(g.NSLOTS))

    # ----- presets -----
    def load(self, slots):
        if self.proc:  # a Claude run may hold the MIDI port; refresh when it ends
            self.pending.update(slots)
            return
        self.loader = Loader(list(slots))
        self.loader.slot.connect(self.set_name)
        self.loader.failed.connect(lambda e: self.status.setText(f"⚠ {e}"))
        self.loader.finished.connect(lambda: self.status.text().startswith("⚠") or self.status.setText("Listo"))
        self.loader.start()

    def set_name(self, s, name):
        it = self.items[s]
        it.setText(f"{g.slot_label(s):>4}  {'(vacío)' if name == EMPTY else name}")
        it.setData(Qt.ItemDataRole.UserRole, name)
        it.setForeground(QColor("#777") if name == EMPTY else QColor("#ddd"))

    def show_slot(self, s):
        if s < 0 or self.busy():
            return
        p, err = with_device(lambda dev: g.decode_preset(dev.read(s)))
        self.chain.setPlainText(err or f"{g.slot_label(s)}: {p['name']}\n" + "\n".join(g.show_lines(p)))

    def busy(self):
        return bool(self.proc or (self.loader and self.loader.isRunning()))

    def select_slot(self, item):
        s = self.slots.row(item)
        if self.busy():
            return self.status.setText("Ocupado leyendo la pedalera, prueba en un momento")
        _, err = with_device(lambda dev: dev.send(g.msg_select(s), 0.1))
        self.status.setText(err or f"Pedalera en {g.slot_label(s)}")

    # ----- chat -----
    def say(self, who, text, color="#ddd"):
        esc = text.replace("&", "&amp;").replace("<", "&lt;").replace("\n", "<br>")
        esc = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", re.sub(r"`([^`]+)`", r"<code>\1</code>", esc))
        self.log.append(f'<p style="color:{color}"><b>{who}</b> {esc}</p>')

    def send(self):
        msg = self.entry.text().strip()
        if not msg or self.proc:
            return
        self.entry.clear()
        self.say("Tú:", msg, "#8cf")
        row = self.slots.currentRow()
        sysp = SYSTEM + (f" Slot selected in the app: {g.slot_label(row)}." if row >= 0 else "")
        args = ["-p", msg, "--output-format", "stream-json", "--verbose", "--append-system-prompt", sysp,
                "--allowedTools", "Bash(gp200:*)", f"Bash({ROOT}/bin/gp200:*)", "Read", "Write", "Edit", "Skill"]
        if self.session:
            args += ["--resume", self.session]
        self.proc = QProcess(self)
        env = QProcessEnvironment.systemEnvironment()
        env.insert("PATH", f"{Path.home()}/.local/bin:" + env.value("PATH"))
        self.proc.setProcessEnvironment(env)
        self.proc.setWorkingDirectory(str(ROOT))
        self.proc.readyReadStandardOutput.connect(self.read_claude)
        self.proc.finished.connect(self.claude_done)
        self.buf = b""
        if self.loader and self.loader.isRunning():
            self.loader.stop = True
            self.loader.wait()
            self.pending.update(self.loader.left)
        MIDI.acquire()  # the app stays off the pedal while Claude may use it
        self.entry.setEnabled(False)
        self.proc.start("claude", args)

    def read_claude(self):
        self.buf += bytes(self.proc.readAllStandardOutput())
        *lines, self.buf = self.buf.split(b"\n")
        for line in lines:
            for kind, val in parse_event(line):
                if kind == "session":
                    self.session = val
                elif kind == "text":
                    self.say("Claude:", val)
                elif kind == "tool":
                    self.say("⚙", val, "#888")
                    self.pending.update(g.parse_slot(x) for x in touched_slots(val))
                elif kind == "error":
                    self.say("⚠", val, "#f88")

    def claude_done(self, code, _status):
        err = bytes(self.proc.readAllStandardError()).decode(errors="replace").strip()
        if code and err:
            self.say("⚠", err[-500:], "#f88")
        self.proc = None
        MIDI.release()
        self.entry.setEnabled(True)
        self.entry.setFocus()
        if self.pending:
            todo, self.pending = sorted(self.pending), set()
            self.load(todo)


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    pal = QPalette()
    for role, c in [("Window", "#202124"), ("WindowText", "#ddd"), ("Base", "#17181a"), ("AlternateBase", "#26272a"),
                    ("Text", "#ddd"), ("Button", "#2c2d30"), ("ButtonText", "#ddd"), ("Highlight", "#3d6fb3"),
                    ("HighlightedText", "#fff"), ("PlaceholderText", "#777")]:
        pal.setColor(getattr(QPalette.ColorRole, role), QColor(c))
    app.setPalette(pal)
    w = App()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

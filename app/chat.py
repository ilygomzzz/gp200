"""Chat with Claude: pure helpers (parse_event, touched_slots, system_prompt, ChatStore) + ChatSession/ChatHub."""
import json
import os
import re
import tempfile
from pathlib import Path

from PyQt6.QtCore import QObject, QProcess, QProcessEnvironment, pyqtSignal

import theme
from model import ROOT, clean, g

GUITAR = "Ibanez AZ24S1F"
CHATS = Path.home() / ".local/share/gp200/chats.json"
SYSTEM = (f"You are running inside the GP-200 desktop app's chat, not a terminal. Reply in Spanish, short. "
          f"You cannot use AskUserQuestion: ask questions as plain text and wait for the next message. "
          f"Use the gp200 skill/CLI for the pedal. The user's guitar is an {GUITAR}: recommend pickup "
          f"positions and adapt presets to it.")


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


def system_prompt(label=None, preset=None, dirty=False):
    if not label or preset is None:
        return SYSTEM
    return (f"{SYSTEM} Context: slot {label} '{preset['name']}'. Current preset as the user hears it "
            f"(unsaved live edits: {'yes' if dirty else 'no'}): {json.dumps(clean(preset), separators=(',', ':'))}. "
            f"To change it run `gp200 write {label} <file>`; the app re-reads the slot after you finish.")


class ChatStore:
    """{slot label: {"session": id, "html": transcript}} in one JSON file; atomic writes, corrupt file -> {}."""

    def __init__(self, path=CHATS):
        self.path = Path(path)

    def load(self):
        try:
            data = json.loads(self.path.read_text())
            if isinstance(data, dict) and all(isinstance(v, dict) for v in data.values()):
                return data
        except FileNotFoundError:
            return {}
        except (OSError, ValueError):
            pass
        try:
            os.replace(self.path, self.path.with_name(self.path.name + ".bad"))
        except OSError:
            pass
        return {}

    def save(self, data):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=self.path.parent, prefix=self.path.name + ".")
        try:
            with os.fdopen(fd, "w") as f:
                json.dump(data, f)
            os.replace(tmp, self.path)
        except BaseException:
            Path(tmp).unlink(missing_ok=True)
            raise


def html_line(who, text, token="text"):
    esc = text.replace("&", "&amp;").replace("<", "&lt;").replace("\n", "<br>")
    esc = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", re.sub(r"`([^`]+)`", r"<code>\1</code>", esc))
    return f'<p style="color:{getattr(theme, token)}"><b>{who}</b> {esc}</p>'


class ChatSession(QObject):
    line = pyqtSignal(str)  # html fragment
    cleared = pyqtSignal()
    finished = pyqtSignal(list)  # slot labels Claude touched

    def __init__(self, session_id=None, html=""):
        super().__init__()
        self.session_id, self.html, self.proc, self.buf, self.touched = session_id, html, None, b"", []
        self.restored = bool(session_id or html)

    def say(self, who, text, token="text"):
        self.restored = False
        frag = html_line(who, text, token)
        self.html += frag
        self.line.emit(frag)

    def reset(self):
        self.session_id, self.html, self.restored = None, "", False
        self.cleared.emit()

    def start(self, msg, sysp):
        args = ["-p", msg, "--output-format", "stream-json", "--verbose", "--append-system-prompt", sysp,
                "--allowedTools", "Bash(gp200:*)", f"Bash({ROOT}/bin/gp200:*)", "Read", "Write", "Edit", "Skill"]
        if self.session_id:
            args += ["--resume", self.session_id]
        self.buf, self.touched = b"", []
        self.proc = QProcess(self)
        env = QProcessEnvironment.systemEnvironment()
        env.insert("PATH", f"{Path.home()}/.local/bin:" + env.value("PATH"))
        self.proc.setProcessEnvironment(env)
        self.proc.setWorkingDirectory(str(ROOT))
        self.proc.readyReadStandardOutput.connect(self._read)
        self.proc.finished.connect(self._done)
        self.proc.start("claude", args)

    def _read(self):
        self.buf += bytes(self.proc.readAllStandardOutput())
        *lines, self.buf = self.buf.split(b"\n")
        for ln in lines:
            for kind, val in parse_event(ln):
                if kind == "session":
                    self.session_id = val
                elif kind == "text":
                    self.say("Claude:", val)
                elif kind == "tool":
                    self.say("⚙", val, "tool")
                    self.touched += touched_slots(val)
                elif kind == "error":
                    self.say("⚠", val, "danger")

    def _done(self, code, _status):
        err = bytes(self.proc.readAllStandardError()).decode(errors="replace").strip()
        if code and err:
            self.say("⚠", err[-500:], "danger")
        self.proc = None
        self.finished.emit(self.touched)


class ChatHub(QObject):
    """One ChatSession per context ("global" or slot label); only one Claude run app-wide."""
    running_changed = pyqtSignal(bool)
    wrote_slots = pyqtSignal(list)  # slot ints

    def __init__(self, pedal, store=None):
        super().__init__()
        self.pedal, self.store, self.active, self.go = pedal, store or ChatStore(), None, None
        self.sessions = {"global": ChatSession()}
        for k, v in self.store.load().items():
            self.sessions[k] = ChatSession(v.get("session"), v.get("html", ""))
        pedal.held.connect(self._held)

    def session(self, key):
        if key not in self.sessions:
            self.sessions[key] = ChatSession()
        return self.sessions[key]

    def persist(self):
        data = {k: {"session": s.session_id, "html": s.html} for k, s in self.sessions.items() if k != "global" and (s.html or s.session_id)}
        try:
            self.store.save(data)
        except OSError:
            pass  # chats just won't survive a restart

    def reset(self, key):
        self.session(key).reset()
        self.persist()

    def send(self, key, msg, sysp):
        if self.active:
            return
        s = self.active = self.session(key)
        s.say("Tú:", msg, "user")
        self.go = (s, msg, sysp)
        s.finished.connect(self._finished)
        self.running_changed.emit(True)
        self.pedal.hold_for_claude()

    def _held(self):  # worker thread reached the hold: the CLI may use the port now
        if self.go:
            (s, msg, sysp), self.go = self.go, None
            s.start(msg, sysp)

    def _finished(self, labels):
        s, self.active = self.active, None
        s.finished.disconnect(self._finished)
        self.persist()
        self.wrote_slots.emit([g.parse_slot(x) for x in labels])
        self.pedal.release_claude()
        self.running_changed.emit(False)

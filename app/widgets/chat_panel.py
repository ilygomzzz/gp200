from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextBrowser, QVBoxLayout, QWidget

import theme

EMPTY = "Elige un slot de la lista para ver su cadena y charlar sobre él."
HINT = "Pregúntale a Claude por este preset: qué hace cada bloque, cómo acercarlo a un sonido, qué pastilla usar."


class ChatPanel(QWidget):
    submitted = pyqtSignal(str)  # message text
    new_chat = pyqtSignal()

    def __init__(self, global_ctx=False):
        super().__init__()
        self.global_ctx, self.session, self.label, self.title_text = global_ctx, None, None, "Chat general" if global_ctx else "Chat"
        self.title = QLabel(self.title_text)
        self.title.setStyleSheet(f"font-size:{theme.font_body}px; font-weight:bold")
        self.new_btn = QPushButton("Nueva conversación")
        self.new_btn.clicked.connect(self.new_chat)
        self.log = QTextBrowser()
        self.log.setOpenExternalLinks(True)
        self.hint = QLabel()
        self.hint.setWordWrap(True)
        self.hint.setStyleSheet(f"color:{theme.dim}")
        self.entry = QLineEdit()
        self.entry.returnPressed.connect(self._send)
        head = QHBoxLayout()
        head.addWidget(self.title, 1)
        head.addWidget(self.new_btn)
        lay = QVBoxLayout(self)
        lay.addLayout(head)
        for w in (self.log, self.hint, self.entry):
            lay.addWidget(w)
        self.locked = None  # None | reason text
        self.bind(None, None, None)

    def bind(self, session, label, title):
        """session: ChatSession or None (no slot selected)."""
        if self.session:
            self.session.line.disconnect(self.log.append)
            self.session.cleared.disconnect(self._cleared)
        self.session, self.label = session, label
        self.title.setText(title or self.title_text)
        self.log.setHtml(session.html if session else "")
        if session:
            session.line.connect(self.log.append)
            session.cleared.connect(self._cleared)
        self._refresh()

    def _cleared(self):
        self.log.clear()
        self._refresh()

    def set_locked(self, reason):
        """reason: text shown as placeholder while input is disabled; None = enabled."""
        self.locked = reason
        self._refresh()

    def _refresh(self):
        on = self.session is not None and self.locked is None
        self.entry.setEnabled(on)
        self.new_btn.setEnabled(self.session is not None and not self.locked)
        ctx = "Pide un sonido, un cambio… (Enter)" if self.global_ctx else f"Pregunta o pide un cambio sobre {self.label}… (Enter)"
        self.entry.setPlaceholderText(self.locked or ctx if self.session else "")
        empty = not self.log.toPlainText().strip()
        s = self.session
        self.hint.setText(EMPTY if not s else "" if self.global_ctx else HINT if empty else
                          "Conversación anterior · se continúa" if s.restored else "")

    def _send(self):
        t = self.entry.text().strip()
        if t:
            self.entry.clear()
            self.submitted.emit(t)

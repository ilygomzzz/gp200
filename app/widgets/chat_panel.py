from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextBrowser, QVBoxLayout

import theme

EMPTY = "Elige un slot de la lista para ver su cadena y charlar sobre él."
HINT = "Pregúntale a Claude por este preset: qué hace cada bloque, cómo acercarlo a un sonido, qué pastilla usar."


class ChatPanel(QFrame):
    submitted = pyqtSignal(str)  # message text
    new_chat = pyqtSignal()

    def __init__(self, global_ctx=False):
        super().__init__()
        self.setObjectName("plate")
        self.global_ctx, self.session, self.label, self.title_text = global_ctx, None, None, "Chat general" if global_ctx else "Chat"
        self.title = QLabel(self.title_text)
        self.title.setStyleSheet(f"font-size:{theme.font_body}px; font-weight:bold")
        self.new_btn = QPushButton(theme.glyphs["new_chat"])
        self.new_btn.setObjectName("icon")
        self.new_btn.setToolTip("Nueva conversación")
        self.new_btn.setAccessibleName("Nueva conversación")
        self.new_btn.clicked.connect(self.new_chat)
        self.log = QTextBrowser()
        self.log.setOpenExternalLinks(True)
        self.log.document().setDefaultStyleSheet(f"p {{ margin-bottom:{theme.s2}px; }} code {{ font-family:'{theme.mono}'; }}")
        self.log.setStyleSheet(f"font-size:{theme.font_desc}px")
        self.hint = QLabel()
        self.hint.setWordWrap(True)
        self.hint.setStyleSheet(f"color:{theme.dim}; font-size:{theme.font_desc}px")
        self.entry = QLineEdit()
        self.entry.setObjectName("input")
        self.send_btn = QPushButton(theme.glyphs["send"])
        il = QHBoxLayout(self.entry)
        il.setContentsMargins(0, 0, theme.s1, 0)
        il.addStretch()
        il.addWidget(self.send_btn)
        self.send_btn.setObjectName("icon")
        self.send_btn.setToolTip("Enviar (Enter)")
        self.send_btn.setAccessibleName("Enviar")
        self.send_btn.clicked.connect(self._send)
        self.send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.entry.returnPressed.connect(self._send)
        head = QHBoxLayout()
        head.addWidget(self.title, 1)
        head.addWidget(self.new_btn)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(theme.s3, theme.s3, theme.s3, theme.s3)
        lay.setSpacing(theme.s2)
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
        self.send_btn.setEnabled(on)
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

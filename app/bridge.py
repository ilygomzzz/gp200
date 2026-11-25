"""QML view-models (spec 004): `Board` over Workbench/Pedal, `ChatView` over ChatHub. No pedal state of their own; QML never sees Device."""
import copy

from PyQt6.QtCore import QObject, QVariant, pyqtProperty, pyqtSignal, pyqtSlot

from art import art_for, cable_path, unit_key
from chat import system_prompt
from model import effects_for, free_slots, g, slot_matches, snap_label

DLY_NOTE = "Time: lo fija el tempo del preset (120 BPM = 500 ms); aún no se puede cambiar."


# ---------- pure helpers ----------
def catalog(block, effect):
    """Catalog info of an effect, or None for '#0x…' / another module's effect (seen in factory presets)."""
    try:
        return g.find_effect(block, effect)[1]
    except SystemExit:
        return None


def _fmt(v):
    return str(int(v)) if float(v) == int(v) else f"{v:.1f}"


def rack_display(block, params):
    """The 2 main values a rack unit shows (`params` = [(name, value)] of knob params) -> (full, short):
    ["500 ms", "Mix 35"] and ["500", "35"] (the stage display is small)."""
    want = {"DLY": ("time", "mix"), "RVB": ("decay", "mix"), "MOD": ("rate", "depth")}.get(block, ())
    out = []
    for w in want:
        hit = next(((n, v) for n, v in params if w in n.lower() and (n, v) not in out), None)
        if hit:
            out.append(hit)
    out = (out + [p for p in params if p not in out])[:2]
    return ([f"{_fmt(v)} ms" if "time" in n.lower() else f"{n.strip()} {_fmt(v)}" for n, v in out],
            [f"{_fmt(v)} ms" if "time" in n.lower() else f"{n.strip()} {_fmt(v)}" for n, v in out])


def unit_view(preset, block):
    """What a board unit shows: effect name, on, desc, art (kind/family/speakers), `mini` = normalised (0..1) values of
    its first 3 knob params, `knobs`/`labels` = up to 8, `display` = the rack's 2 values."""
    blk = preset["blocks"][block]
    info = catalog(block, blk["effect"])
    mini, knobs, labels, named = [], [], [], []
    for p in (info or {"params": []})["params"]:
        if p["type"] == "knob" and len(knobs) < 8:
            v = blk["params"].get(p["name"], p["default"])
            span = (p["max"] - p["min"]) or 1
            knobs.append(max(0.0, min(1.0, (v - p["min"]) / span)))
            labels.append(p["name"].strip())
            named.append((p["name"], v))
    mini = knobs[:3]
    desc = (info or {}).get("desc", "")
    art = art_for(block, blk["effect"], desc)
    return {"effect": blk["effect"], "on": bool(blk["on"]), "desc": desc, "mini": mini, "knobs": knobs, "labels": labels,
            "display": rack_display(block, named)[0], "displayShort": rack_display(block, named)[1], **art,
            "key": unit_key(art["kind"], art["family"], art["speakers"], block)}


def chain_view(preset):
    return {"order": list(preset.get("order", g.BLOCKS)), "units": {b: unit_view(preset, b) for b in g.BLOCKS}}


def params_view(block, effect):
    """Catalog params of the selected effect for the knob delegates (no values: those live in `Board.values`)."""
    info = catalog(block, effect)
    out = []
    for p in (info or {"params": []})["params"]:
        out.append({"name": p["name"], "label": p["name"].strip(), "type": p["type"], "default": p["default"],
                    "min": p.get("min", 0), "max": p.get("max", 1), "step": p.get("step") or 1,
                    "options": p.get("options", []), "locked": block == "DLY" and p["name"] == "Time"})
    return out


# ---------- Board ----------
def _prop(typ, name, sig):
    return pyqtProperty(typ, lambda self: getattr(self, "_" + name), notify=sig)


class Board(QObject):
    stateChanged, chainChanged, selectedChanged = pyqtSignal(), pyqtSignal(), pyqtSignal()
    paramsChanged, valuesChanged, effectsChanged = pyqtSignal(), pyqtSignal(), pyqtSignal()

    def __init__(self, wb):
        super().__init__()
        self.wb, self.pedal = wb, wb.pedal
        self.names, self._key = {}, None
        self._open, self._loading, self._guard, self._busy = False, False, "", ""
        self._status, self._statusError, self._scanStatus, self._scanError = "", False, "Leyendo la pedalera…", False
        self._order, self._units, self._params, self._values, self._effects, self._effectKeys = list(g.BLOCKS), {}, [], {}, [], []
        self._selected, self._name, self._slot, self._slotLabel = wb.selected_block, "", -1, ""
        p = self.pedal
        p.slot_name.connect(self.names.__setitem__)
        p.scan_done.connect(lambda: self._scan(self._scanStatus if self._scanError else "Listo", self._scanError))
        p.failed.connect(lambda area, m: area == "scan" and self._scan(m.removeprefix("⚠ "), True))
        wb.loading.connect(self._on_loading)
        wb.loaded.connect(self._refresh)
        wb.changed.connect(self._refresh)
        wb.block_selected.connect(lambda _: self._refresh(wb.working))
        wb.dirty_changed.connect(lambda _: self.stateChanged.emit())
        wb.status.connect(self._on_status)
        wb.guard.connect(self._on_guard)
        wb.busy_changed.connect(self._on_busy)

    # --- properties ---
    open, loading, guard, busy = _prop(bool, "open", stateChanged), _prop(bool, "loading", stateChanged), _prop(str, "guard", stateChanged), _prop(str, "busy", stateChanged)
    status, statusError = _prop(str, "status", stateChanged), _prop(bool, "statusError", stateChanged)
    scanStatus, scanError = _prop(str, "scanStatus", stateChanged), _prop(bool, "scanError", stateChanged)
    slot, slotLabel, name = _prop(int, "slot", stateChanged), _prop(str, "slotLabel", stateChanged), _prop(str, "name", stateChanged)
    order, units = _prop(QVariant, "order", chainChanged), _prop(QVariant, "units", chainChanged)
    selected, params = _prop(str, "selected", selectedChanged), _prop(QVariant, "params", paramsChanged)
    values, effects = _prop(QVariant, "values", valuesChanged), _prop(QVariant, "effects", effectsChanged)
    effectKeys = _prop(QVariant, "effectKeys", effectsChanged)  # unit_key of each picker row, parallel to `effects`

    @pyqtProperty(bool, notify=stateChanged)
    def dirty(self):
        return self.wb.dirty

    @pyqtProperty(bool, notify=stateChanged)
    def factory(self):
        return self.wb.factory

    @pyqtProperty(QVariant, notify=stateChanged)
    def freeSlots(self):
        return [{"slot": s, "label": g.slot_label(s)} for s in free_slots(self.names)]

    @pyqtProperty(QVariant, constant=True)
    def blocks(self):
        return list(g.BLOCKS)

    @pyqtProperty(str, constant=True)
    def dlyNote(self):
        return DLY_NOTE

    # --- model -> view ---
    def _scan(self, text, err):
        self._scanStatus, self._scanError = text, err
        self.stateChanged.emit()

    def _on_loading(self, slot):
        self._open, self._loading, self._guard = True, True, ""
        self._slot, self._slotLabel, self._name, self._units = slot, g.slot_label(slot), "", {}
        self.stateChanged.emit()
        self.chainChanged.emit()

    def _on_status(self, text, err):
        self._status, self._statusError = text.removeprefix("⚠ "), err
        self.stateChanged.emit()

    def _on_guard(self, label):
        self._guard = label
        self.stateChanged.emit()

    def _on_busy(self, what):
        self._busy = what or ""
        if what == "claude":
            self._status, self._statusError = "Claude está usando la pedalera…", False
        self.stateChanged.emit()

    def _refresh(self, preset):
        if preset is None:
            return
        wb, st = self.wb, False
        self._open, self._loading, self._slot, self._slotLabel = True, False, wb.slot, wb.label
        self._name = preset["name"]
        view = chain_view(preset)
        if (view["order"], view["units"]) != (self._order, self._units):
            self._order, self._units = view["order"], view["units"]
            self.chainChanged.emit()
        if wb.selected_block != self._selected:
            self._selected = wb.selected_block
            self.selectedChanged.emit()
        blk = preset["blocks"][self._selected]
        key = (self._selected, blk["effect"])
        if key != self._key:  # delegates survive drags: params/effects only change with block or effect
            self._key = key
            self._params = params_view(*key)
            ef = effects_for(self._selected)
            self._effects = [snap_label(e, i) for e, i in ef]
            self._effectKeys = [unit_key(**{k: a[k] for k in ("kind", "family", "speakers")}, block=self._selected) for a in (art_for(self._selected, i["name"], i.get("desc", "")) for _, i in ef)]
            self.paramsChanged.emit()
            self.effectsChanged.emit()
        if blk["params"] != self._values or not self._values:
            self._values = dict(blk["params"])
            self.valuesChanged.emit()
        self.stateChanged.emit()

    # --- view -> model ---
    @pyqtSlot(float, float, float, float, int, "QVariantList", result="QVariantList")
    def cable(self, x0, y0, x1, y1, lane, rects):
        return [[x, y] for x, y in cable_path((x0, y0), (x1, y1), [tuple(r) for r in rects], lane)]

    @pyqtSlot(int)
    def openSlot(self, slot): self.wb.request_open(slot)

    @pyqtSlot(str)
    def select(self, block): self.wb.select_block(block)

    @pyqtSlot(str)
    def toggle(self, block): self.wb.toggle(block)

    @pyqtSlot(str, int)
    def move(self, block, delta): self.wb.move(block, delta)

    @pyqtSlot(str, int)
    def moveTo(self, block, index): self.wb.move_to(block, index)

    @pyqtSlot(str, float)
    def setParam(self, name, value): self.wb.set_param(self._selected, name, value)

    @pyqtSlot(str)
    def setEffect(self, name): self.wb.set_effect(self._selected, name)

    @pyqtSlot(str, result=bool)
    def rename(self, name):
        ok = self.wb.rename(name)
        self._refresh(self.wb.working)
        return ok

    @pyqtSlot()
    def save(self): self.wb.save()

    @pyqtSlot(int)
    def saveAs(self, slot): self.wb.save_as(slot)

    @pyqtSlot()
    def discard(self): self.wb.discard()

    @pyqtSlot()
    def confirmSwitch(self):
        self._guard = ""
        self.stateChanged.emit()
        self.wb.confirm_switch()

    @pyqtSlot()
    def cancelSwitch(self):
        self._guard = ""
        self.stateChanged.emit()
        self.wb.cancel_switch()

    @pyqtSlot()
    def rescan(self):
        self._scan("Leyendo la pedalera…", False)
        self.pedal.scan(range(g.NSLOTS))

    @pyqtSlot(str, str, str, result=bool)
    def matches(self, label, name, query): return slot_matches(label, name or None, query)

    @pyqtSlot(str, result=float)
    def defaultOf(self, name):
        return next((p["default"] for p in self._params if p["name"] == name), 0.0)


# ---------- chat ----------
def chat_hint(session, global_ctx, empty):
    if session is None:
        return "Elige un slot de la lista para ver su cadena y charlar sobre él."
    if global_ctx:
        return ""
    return ("Pregúntale a Claude por este preset: qué hace cada bloque, cómo acercarlo a un sonido, qué pastilla usar." if empty
            else "Conversación anterior · se continúa" if session.restored else "")


class ChatView(QObject):
    """One chat panel: the slot chat rebinds on every slot open, the global one is fixed."""
    titleChanged, htmlChanged, lockedChanged = pyqtSignal(), pyqtSignal(), pyqtSignal()

    def __init__(self, hub, wb, global_ctx=False):
        super().__init__()
        self.hub, self.wb, self.global_ctx, self.session, self.key = hub, wb, global_ctx, None, None
        hub.running_changed.connect(lambda _: self.lockedChanged.emit())
        wb.busy_changed.connect(lambda _: self.lockedChanged.emit())
        if global_ctx:
            self._bind("global")
        else:
            wb.loading.connect(lambda s: self._bind(g.slot_label(s)))
            wb.loaded.connect(lambda _: self.titleChanged.emit())

    def _bind(self, key):
        if self.session:
            self.session.line.disconnect(self.htmlChanged)
            self.session.cleared.disconnect(self.htmlChanged)
        self.key, self.session = key, self.hub.session(key)
        self.session.line.connect(self.htmlChanged)
        self.session.cleared.connect(self.htmlChanged)
        self.titleChanged.emit()
        self.htmlChanged.emit()
        self.lockedChanged.emit()

    @pyqtProperty(str, notify=titleChanged)
    def title(self):
        if self.global_ctx:
            return "Chat general"
        name = f" {self.wb.working['name']}" if self.wb.working else ""
        return f"Chat · {self.key}{name}" if self.key else "Chat"

    @pyqtProperty(str, notify=htmlChanged)
    def html(self): return self.session.html if self.session else ""

    @pyqtProperty(str, notify=htmlChanged)
    def hint(self): return chat_hint(self.session, self.global_ctx, not (self.session and self.session.html.strip()))

    @pyqtProperty(str, notify=lockedChanged)
    def locked(self):
        return ("Espera a que termine de guardar" if self.wb.busy == "save" else
                "Claude está respondiendo…" if self.hub.active else "")

    @pyqtProperty(bool, notify=titleChanged)
    def bound(self): return self.session is not None

    @pyqtProperty(str, notify=titleChanged)
    def placeholder(self):
        return "Pide un sonido, un cambio… (Enter)" if self.global_ctx else f"Pregunta o pide un cambio sobre {self.key}… (Enter)"

    @pyqtProperty(bool, notify=lockedChanged)
    def running(self): return self.hub.active is not None

    @pyqtSlot(str)
    def send(self, text):
        text = text.strip()
        if text and self.session and not self.locked:
            p = self.wb.working if self.key != "global" else None
            self.hub.send(self.key, text, system_prompt(self.key if p else None, p, self.wb.dirty))

    @pyqtSlot()
    def reset(self):
        if self.session and not self.locked:
            self.hub.reset(self.key)

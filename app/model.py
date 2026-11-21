"""Pedal state: pure edit helpers, `Pedal` (single MIDI owner with a worker thread) and `Workbench` (edit buffer of one slot)."""
import copy
import heapq
import itertools
import os
import re
import threading
from importlib.machinery import SourceFileLoader
from pathlib import Path

from PyQt6.QtCore import QObject, QThread, pyqtSignal

ROOT = Path(__file__).resolve().parent.parent
g = SourceFileLoader("gp200", str(ROOT / "bin/gp200")).load_module()
EMPTY = "It's GP-200JR"
FACTORY = 99  # slots 0..98 (1A-33C)
LAST = g.NSLOTS - 1  # 85C reads oddly: never a save target
MIDI = threading.Lock()  # raw MIDI is exclusive: one operation at a time
HIGH, LOW = 0, 1


# ---------- pure helpers ----------
def snap_label(eid, info):
    return f"SnapTone {eid - 0x0F000000 + 1}" if eid >= 0x0F000000 else info["name"]


def effects_for(block):
    """[(eid, info)] of a block's module sorted by name; SnapTones are numbered as in the CLI."""
    return sorted(((e, i) for e, i in g.EFFECTS.items() if i["module"] == block), key=lambda x: snap_label(*x).lower())


def move_block(order, block, delta):
    o = list(order)
    i = o.index(block)
    o.insert(max(0, min(len(o) - 1, i + delta)), o.pop(i))
    return o


def eid_of(block, name):
    if name.startswith("#"):
        return int(name[1:], 16), {"name": name, "params": []}
    return g.find_effect(block, name)


def clean(preset):
    """Preset without '#n' params of catalogued effects (what `gp200 write` needs and what Claude should see)."""
    out = copy.deepcopy(preset)
    for name, b in out["blocks"].items():
        if b["effect"].startswith("#"):
            continue
        try:
            info = g.find_effect(name, b["effect"])[1]
            for q in info["params"]:  # factory values can sit outside the catalog range (e.g. Delay Time)
                if q["type"] == "knob" and q["name"] in b["params"]:
                    b["params"][q["name"]] = max(q["min"], min(q["max"], b["params"][q["name"]]))
        except SystemExit:  # factory presets keep another module's effect id in some (off) blocks: `write` can't express it
            eid, info = effects_for(name)[0]
            b["effect"], b["params"] = snap_label(eid, info), {p["name"]: p["default"] for p in info["params"]}
        b["params"] = {k: v for k, v in b["params"].items() if not k.startswith("#")}
    return out


def free_slots(names):
    """Slots (>= 34A, never 85C) whose stored name is the factory-empty one, in order. names: {slot: name}."""
    return [s for s in sorted(names) if FACTORY <= s < LAST and names[s] == EMPTY]


def edit_msgs(preset, edit, fresh=()):
    """Apply one edit to a preset: -> (new_preset, [(msg_bytes, gap_s)]). Raises ValueError on invalid edits.
    edits: ("effect", block, name) ("param", block, pname, value) ("toggle", block, on) ("order", order)"""
    new, kind = copy.deepcopy(preset), edit[0]
    try:
        if kind == "order":
            new["order"] = list(edit[1])
            send, ret = new.get("fxloop", (4, 4))
            return new, [(g.msg_reorder([g.BLOCKS.index(b) for b in edit[1]], send, ret), 0.1)]
        block, bi = edit[1], g.BLOCKS.index(edit[1])
        cur = new["blocks"][block]
        if kind == "toggle":
            cur["on"] = bool(edit[2])
            return new, [(g.msg_toggle(bi, cur["on"]), 0.05)]
        if kind == "effect":
            eid, info = eid_of(block, edit[2])
            msgs = [(g.msg_effect(bi, eid), 0.4)]
            defaults = [(p["idx"], p["default"]) for p in info["params"]]
            msgs += [(g.msg_param(bi, i, eid, v), 0.04) for i, v in defaults + defaults[:1]]
            cur["effect"], cur["params"] = snap_label(eid, info) if eid >= 0x0F000000 else info["name"], {p["name"]: p["default"] for p in info["params"]}
            return new, msgs
        eid, info = eid_of(block, cur["effect"])
        p = next((p for p in info["params"] if p["name"] == edit[2]), None)
        if not p:
            raise ValueError(f"{cur['effect']} has no param {edit[2]!r}")
        v = float(edit[3])
        if p["type"] == "knob":
            v = max(p["min"], min(p["max"], v))
        elif v not in {o["id"] for o in p.get("options", [])}:
            raise ValueError(f"{p['name']}: invalid option {v:g}")
        cur["params"][p["name"]] = v
        return new, [(g.msg_param(bi, p["idx"], eid, v), 0.04)] * (2 if block in fresh else 1)
    except SystemExit as e:  # find_effect
        raise ValueError(str(e))


# ---------- Pedal ----------
class Pedal(QObject):
    slot_name = pyqtSignal(int, str)
    preset_read = pyqtSignal(int, dict)
    progress = pyqtSignal(str)
    saved = pyqtSignal(int, list, str)  # slot, readback problems, name
    failed = pyqtSignal(str, str)  # area ("scan"/"workbench"), message
    busy_changed = pyqtSignal(object)  # None | "save" | "claude"
    scan_done = pyqtSignal()
    held = pyqtSignal()  # the worker reached the Claude hold: the port is free for the CLI

    def __init__(self, device_factory=None):
        super().__init__()
        self.factory = device_factory or g.Device
        self.q, self.cv, self.seq, self.keys, self.quit = [], threading.Condition(), itertools.count(), {}, False
        self.release = threading.Event()
        self.thread = QThread(self)
        self.thread.run = self._loop
        self.thread.start()

    def stop(self):
        with self.cv:
            self.quit = True
            self.cv.notify()
        self.release.set()
        self.thread.wait(2000)

    def _put(self, prio, fn, area="workbench", key=None):
        with self.cv:
            if key and key in self.keys:  # coalesce: latest value wins
                self.keys[key][0] = fn
                return
            job = [fn, area, key]
            if key:
                self.keys[key] = job
            heapq.heappush(self.q, (prio, next(self.seq), job))
            self.cv.notify()

    def _loop(self):
        while True:
            with self.cv:
                while not self.q and not self.quit:
                    self.cv.wait()
                if self.quit:
                    return
                _, _, job = heapq.heappop(self.q)
                if job[2]:
                    self.keys.pop(job[2], None)
            fn, area, _ = job
            try:
                if fn == self._hold:  # bound methods: `is` is never true
                    fn(None)
                    continue
                with MIDI:
                    dev = self.factory()
                    try:
                        fn(dev)
                    finally:
                        getattr(dev, "close", lambda: os.close(dev.fd))()
            except (SystemExit, OSError) as e:
                if area == "scan":  # no point retrying 254 more slots
                    with self.cv:
                        self.q = [j for j in self.q if j[2][1] != "scan"]
                        heapq.heapify(self.q)
                self.failed.emit(area, str(e) if isinstance(e, SystemExit) else f"{e.strerror or e}")

    # --- jobs ---
    def scan(self, slots):
        for s in slots:
            self._put(LOW, lambda dev, s=s: self.slot_name.emit(s, g.decode_preset(dev.read(s))["name"]), "scan")
        self._put(LOW, lambda dev: self.scan_done.emit(), "scan")

    def read(self, slot, select=False):
        def job(dev):
            if select:
                dev.send(g.msg_select(slot), 0.3)
            p = g.decode_preset(dev.read(slot))
            self.slot_name.emit(slot, p["name"])
            self.preset_read.emit(slot, p)
        self._put(HIGH, job)

    def apply(self, msgs, key=None):
        def job(dev):
            for m, gap in msgs:
                dev.send(m, gap)
        self._put(HIGH, job, key=key)

    def select(self, slot):
        self._put(HIGH, lambda dev: dev.send(g.msg_select(slot), 0.1))

    def save(self, slot, preset):
        def job(dev):
            self.busy_changed.emit("save")
            try:
                cl = clean(preset)
                _, probs, name = g.write_preset(dev, slot, cl, lambda n: self.progress.emit(f"Guardando {g.slot_label(slot)}… ({n}/11)"))
                # the patch tempo overwrites Delay Time on save (known, out of scope): not a failed save
                info = g.find_effect("DLY", cl["blocks"]["DLY"]["effect"])[1] if not cl["blocks"]["DLY"]["effect"].startswith("#") else {"params": []}
                tidx = next((q["idx"] for q in info["params"] if q["name"] == "Time"), None)
                probs = [x for x in probs if not x.startswith(f"DLY param#{tidx}:")]
                self.slot_name.emit(slot, name)
                self.saved.emit(slot, probs, name)
            finally:
                self.busy_changed.emit(None)
        self._put(HIGH, job)

    def _hold(self, _dev):
        self.held.emit()
        self.release.wait()

    def hold_for_claude(self):
        self.release.clear()
        self.busy_changed.emit("claude")
        self._put(HIGH, self._hold)

    def release_claude(self):
        self.release.set()
        self.busy_changed.emit(None)


# ---------- Workbench ----------
class Workbench(QObject):
    loading = pyqtSignal(int)
    loaded = pyqtSignal(dict)
    changed = pyqtSignal(dict)
    dirty_changed = pyqtSignal(bool)
    block_selected = pyqtSignal(str)
    saved = pyqtSignal(str)
    status = pyqtSignal(str, bool)  # text, is_error
    guard = pyqtSignal(str)  # dirty and another slot requested: label of the dirty slot
    busy_changed = pyqtSignal(object)

    def __init__(self, pedal):
        super().__init__()
        self.pedal, self.slot, self.stored, self.working, self.dirty = pedal, None, None, None, False
        self.selected_block, self.fresh, self.cache, self.busy = "AMP", set(), {}, None
        self.want, self.after_claude, self.was_dirty = None, None, False
        pedal.preset_read.connect(self._read)
        pedal.saved.connect(self._saved)
        pedal.progress.connect(lambda t: self.status.emit(t, False))
        pedal.failed.connect(lambda a, m: a == "workbench" and self.status.emit(f"⚠ {m}", True))
        pedal.busy_changed.connect(self._busy)

    @property
    def factory(self):
        return self.slot is not None and self.slot < FACTORY

    @property
    def label(self):
        return g.slot_label(self.slot)

    # --- opening ---
    def request_open(self, slot):
        if self.dirty and slot != self.slot:
            self.want = slot
            return self.guard.emit(self.label)
        self.open(slot)

    def confirm_switch(self):
        if self.want is not None:
            self.open(self.want)

    def cancel_switch(self):
        self.want = None

    def open(self, slot):
        self.want, self.slot, self.fresh = None, slot, set()
        self._set_dirty(False)
        if self.busy == "claude":  # MIDI is held: show the cached read, read (no select) after the run
            self.after_claude = slot
            cached = self.cache.get(slot)
            self.stored, self.working = (cached, copy.deepcopy(cached)) if cached else (None, None)
            self.loading.emit(slot)
            if cached:
                self.loaded.emit(self.working)
            return self.status.emit(f"Claude está usando la pedalera: {g.slot_label(slot)} se leerá cuando termine", False)
        self.stored = self.working = None
        self.loading.emit(slot)
        self.status.emit(f"Leyendo {g.slot_label(slot)}…", False)
        self.pedal.read(slot, select=True)

    def _read(self, slot, preset):
        self.cache[slot] = preset
        if slot != self.slot:
            return
        self.stored, self.working = preset, copy.deepcopy(preset)
        self.fresh = set()
        was, self.was_dirty = self.was_dirty, False
        self._set_dirty(False)
        self.loaded.emit(self.working)
        self.status.emit(f"Claude ha reescrito {self.label}; tus cambios sin guardar se han sustituido" if was else
                         f"Pedalera en {self.label} · cambios en vivo", False)

    def _busy(self, what):
        was, self.busy = self.busy, what
        self.busy_changed.emit(what)
        if was == "claude" and what is None and self.after_claude is not None:
            self.after_claude = None
            self.pedal.read(self.slot, select=False)

    def reload_after_claude(self, written):
        """Claude ran: reread the current slot if it wrote it (even if it was dirty)."""
        if self.slot in written:
            self.was_dirty = self.dirty
            self.after_claude = self.slot

    # --- edits ---
    def _edit(self, edit, key=None):
        if self.working is None or self.busy:
            return
        try:
            new, msgs = edit_msgs(self.working, edit, self.fresh)
        except ValueError as e:
            self.status.emit(f"⚠ {e}", True)
            return self.changed.emit(self.working)
        if edit[0] == "effect":
            self.fresh.add(edit[1])
        elif edit[0] == "param":
            self.fresh.discard(edit[1])
        self.working = new
        self._set_dirty(new != self.stored)
        self.changed.emit(new)
        self.pedal.apply(msgs, key)

    def set_effect(self, block, name):
        self._edit(("effect", block, name))

    def set_param(self, block, pname, value):
        self._edit(("param", block, pname, value), ("param", block, pname))

    def toggle(self, block, on=None):
        self._edit(("toggle", block, (not self.working["blocks"][block]["on"]) if on is None else on))

    def order(self):
        return self.working.get("order", list(g.BLOCKS))

    def move(self, block, delta):
        self._edit(("order", move_block(self.order(), block, delta)))

    def move_to(self, block, index):
        o = self.order()
        i = o.index(block)
        self.move(block, index - i - (1 if index > i else 0))

    def rename(self, name):
        if not (name.isascii() and name.isprintable() and len(name) <= 16) or self.working is None:
            self.status.emit("⚠ El nombre admite hasta 16 caracteres ASCII", True)
            return False
        self.working["name"] = name
        self._set_dirty(self.working != self.stored)
        self.changed.emit(self.working)
        return True

    def select_block(self, block):
        self.selected_block = block
        self.block_selected.emit(block)

    def _set_dirty(self, d):
        if d != self.dirty:
            self.dirty = d
            self.dirty_changed.emit(d)

    # --- save / discard ---
    def save(self):
        if self.working is None or self.factory:
            return self.status.emit("⚠ Preset de fábrica: guárdalo en un slot libre", True)
        self.target = self.slot
        self.pedal.save(self.slot, self.working)

    def save_as(self, target):
        if target < FACTORY or target >= LAST or self.working is None:
            return self.status.emit("⚠ Ese slot no admite guardar", True)
        self.target = target
        self.pedal.save(target, self.working)

    def _saved(self, slot, probs, name):
        if slot != self.target:
            return
        if probs:
            return self.status.emit(f"⚠ Guardado, pero la relectura difiere: {probs[0]}", True)
        self.status.emit("Guardado y verificado", False)
        self.saved.emit(g.slot_label(slot))
        if slot == self.slot:
            self.stored = copy.deepcopy(self.working)
            self.stored["name"] = name
            self.cache[slot] = self.stored
            self._set_dirty(False)
            self.changed.emit(self.working)
        else:  # saved elsewhere: open the target (the pedal selects it)
            self.open(slot)

    def discard(self):
        if self.slot is None:
            return
        self._set_dirty(False)
        self.pedal.read(self.slot, select=True)
        self.status.emit("Cambios descartados", False)

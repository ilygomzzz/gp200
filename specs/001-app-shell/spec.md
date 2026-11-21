# 001 — App shell: preset list + chat

**What:** PyQt6 desktop app (`app/gp200_app.py`, launcher `bin/gp200-app`, menu entry `gp200.desktop`) with two tabs:
- **Presets**: all 255 slots (1A–85C) read progressively from the pedal; empty ones greyed "(vacío)"; click = chain view (`show_lines`, shared with the CLI); double-click = select on the pedal.
- **Chat**: `claude -p --output-format stream-json` in the repo, one conversation (`--resume`), tools limited to the gp200 CLI + Read/Write/Edit/Skill; tool calls shown as lines; slots touched by `gp200 write/select` are re-read afterwards.

**Why:** use the pedal tool without a terminal; base for tabs→preset (002) and trainer (003).

**Constraints:** raw MIDI is exclusive → one lock; the slot loader stops when a chat run starts and resumes after.

## Acceptance
1. Slots load with factory names, empty ones greyed. ✔ (hardware, 2026-11-21)
2. Click shows the 11 blocks. ✔
3. "¿qué hay en el 34B?" → Spanish answer with the `gp200 show 34B` call visible. ✔ (offscreen run)
4. Asking for a sound → written slot is re-read in the list. (re-read path tested via the loader resume; to confirm by the user)
5. Pedal unplugged → error line in the status bar, no crash.

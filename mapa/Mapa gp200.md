# Mapa gp200

Herramienta para la pedalera Valeton GP-200JR en Linux: leer, crear y escribir presets por USB MIDI. Pensada para decirle a Claude "quiero sonido X", que pregunte el slot y lo escriba.

- [[CLAUDE]]: qué hay, CLI, formato de preset y peculiaridades de la JR → `../CLAUDE.md`
- Skill `gp200` (flujo "quiero sonido X") → `../.claude/skills/gp200/SKILL.md`, enlazada en `~/.claude/skills/gp200`
- CLI `gp200` → `../bin/gp200`, enlazado en `~/.local/bin/gp200`
- Catálogo de 305 efectos con parámetros y equipo real que imitan → `../data/effects.json`
- Presets creados → `../presets/`; copias automáticas antes de cada escritura → `../backups/`
- Protocolo: basado en [Preset Forge](https://github.com/phash/gp200editor) (GPL-3.0)
- Slots: 1A–25C de fábrica, 25D–64C libres

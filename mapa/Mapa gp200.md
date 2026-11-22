# Mapa gp200

Herramienta para la pedalera Valeton GP-200JR en Linux: leer, crear y escribir presets por USB MIDI. Pensada para decirle a Claude "quiero sonido X", que pregunte el slot y lo escriba.

- [[CLAUDE]]: qué hay, CLI, formato de preset y peculiaridades de la JR → `../CLAUDE.md`
- Skill `gp200` (flujo "quiero sonido X") → `../.claude/skills/gp200/SKILL.md`, enlazada en `~/.claude/skills/gp200`
- CLI `gp200` → `../bin/gp200`, enlazado en `~/.local/bin/gp200`
- Catálogo de 305 efectos con parámetros y equipo real que imitan → `../data/effects.json`
- Presets creados → `../presets/`; copias automáticas antes de cada escritura → `../backups/`
- Protocolo: basado en [Preset Forge](https://github.com/phash/gp200editor) (GPL-3.0)
- Slots: 3 por banco (A-C), 85 bancos; 1A–33C de fábrica, 34A–85B libres
- Repo público: https://github.com/ilygomzzz/gp200 (clonado por `~/Vault/bootstrap.sh`)
- SnapTones (capturas NAM de TONE3000): se convierten en VLTN Tone Studio y se suben con `gp200 snaptone N` (la JR necesita ir más lento que VLTN); copias en `~/.local/share/gp200/snaptones/`. App: [VLTN Tone Studio](https://github.com/grzmol/VLTN-Tone-Studio) (`~/Applications/vltn-tone-studio.AppImage`, en el menú de apps; señal de prueba en `~/.local/share/gp200/nam_input_wav.wav`)
- App de escritorio: `gp200-app` (menú de apps «GP-200JR»): banco de trabajo de presets: lista de slots, cadena de 11 pedales (arrastrar/encender/efecto/parámetros en vivo, Guardar verificado, Guardar en… para fábrica) y chat de Claude por slot persistente (`~/.local/share/gp200/chats.json`) + «Chat general». Código en `../app/` (theme, model, chat, bridge, qml). Specs en `specs/` (001 y 002 hechas, `002-preset-workbench/`; 003 cristal; 004 pedalera visual en Qt Quick, fase 1 hecha; 005 tablaturas→preset; 006 aprender guitarra). Desde la spec 003 la UI es de cristal: paleta propia fija en `app/theme.py` (sin leer desk-ui), ventana translúcida con blur de Hyprland (regla `class ^gp200$` en Personalization), colores/glifos por bloque, potenciómetros (`widgets/knob.py`) y slots en rejilla por banco. Desde la 004 la UI es Qt Quick (QML en `app/qml/`, vista-modelos en `app/bridge.py`): pedalera con pedales y cables, primer plano con potenciómetros. Hoja de ruta: 004 pedalera (fases 2 arte de equipo, 3 medidor/afinador), 005 tabs→preset, 006 entrenador de guitarra, pantalla SnapTone más adelante.

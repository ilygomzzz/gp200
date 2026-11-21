---
name: gp200-app-sdd
description: gp200 app spec-driven flow with role agents (gp200-designer → user OK → gp200-implementer → gp200-reviewer). Use for ANY change to the gp200 desktop app (~/projects/gp200/app), or when the user asks for app features/UI there.
---

# gp200 app SDD flow (the main session orchestrates, talks to the user in Spanish)

0. **Size.** Small (one widget, < ~200 lines): you write a brief spec.md + design.md yourself, ask OK, then implementer → reviewer. Large (new view, model changes): full flow.
1. **Prepare.** Next number: `ls specs | grep -E '^[0-9]{3}-' | sort | tail -1`; short kebab-case English name.
2. **Design.** Agent `gp200-designer` with the user's words verbatim, the spec folder, and what you know (files, facts from CLAUDE.md, user's guitar).
3. **User OK.** Show mockup + criteria + open questions. No OK, no implementation.
4. **Implement.** Agent `gp200-implementer` with the spec path. Design questions → designer or user.
5. **Review.** Agent `gp200-reviewer`. `CHANGES` → implementer with `review.md` → reviewer again. Max 2 rounds, then ask the user.
6. **Close.** Run the app for the user, commit `NNN name: summary` (+ attribution trailer) and push; update `mapa/` and CLAUDE.md roadmap.

If the named agent types aren't registered in this session, launch `general-purpose` agents told to read and follow `.claude/agents/gp200-<role>.md`. Subagents can't launch others: all orchestration is yours.

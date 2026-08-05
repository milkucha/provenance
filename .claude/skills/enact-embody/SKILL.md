---
description: Play an enacted character scene and put it straight in the game — runs the full /enact procedure (lore: sampling, the scene, hearsay/criterion/life record-keeping), then the full /embody procedure (Minecraft: Blabber dialog, NPC registration, gesture-baking handoff), back to back in one pass. Equivalent to the old, undivided /enact. Use when the user wants both the lore and the pack content done in the same run, with no separate follow-up step.
disable-model-invocation: true
---

Thin orchestrator, no procedure of its own. Read and run `.claude/skills/enact/SKILL.md` in full,
start to finish, exactly as if the user had invoked `/enact` directly — then, without stopping to ask
whether to continue, read and run `.claude/skills/embody/SKILL.md` in full against the scene that was
just played. The result is identical to what bare `/enact` used to do before the two were split; this
skill exists so a user who wants that combined behavior doesn't have to invoke both separately.

Follow each referenced file's own steps and numbering as written — don't restate or duplicate them
here, and don't skip either half. If the user only wants the lore half, they should invoke `/enact`
directly instead of this skill; if a conversation already ran bare `/enact` and now wants the
Minecraft half finished, that's `/embody` directly, not this skill either.

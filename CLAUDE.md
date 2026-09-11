# Provenance

Agent-driven world-building system: takes a seed (sociocultural parameters, a handful of authored facts) and grows a fictional society organically through procedural and semantic generation — not hand-written end to end. Designed to produce emergent, materially-grounded lore drift, not just mechanically-correct record-keeping.

## Index

**Starting a new session? Read [README.md](README.md)'s intro plus §0–§2 first — that's the compulsory orientation minimum.** Then, task-specific sections as needed:

- **Compulsory:** [Getting started](README.md#getting-started), [§0 System architecture](README.md#0-system-architecture), [§1 Folder structure](README.md#1-folder-structure), [§2 Core concepts](README.md#2-core-concepts)
- **Growing the record:** [§3 Writing lore through enactment](README.md#3-writing-lore-through-enactment)
- **Putting it in motion:** `/enact`, `/simulate`, `/generate` (skills, same docs)
- **Minecraft embodiment:** [§5–§8](README.md#5-building-a-new-npc-start-to-finish) (optional; lore engine is embodiment-agnostic)
- **Design tracking:** [LAB_REPORT.md](LAB_REPORT.md), [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md), [TODO.md](TODO.md)
- **This session's starting point:** [CHRONICLE.md](CHRONICLE.md)

## Four core principles

**1. Nothing gets decided silently.** Open questions go to the user or get logged, never guessed. See [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md) — when a `/simulate` run surfaces a gap or a real disagreement about how something should work, that lands here, not only in chat history.

**2. Script everything that can be scripted; prose only where judgment calls genuinely need it.** Dice rolls, pairing, mechanical sequence — all mechanical. Only the words of a scene (dramatizing an already-fully-decided fact, never deciding it) and the rare name-blend judgment stay in prose. Every script lives in `scripts/lore/` or `scripts/minecraft/`, paired with the skill that calls it. Orchestration prose is cheap; reduce it where possible.

**3. Write in the author's voice.** Project prose (README, TODO, LAB_REPORT, commit messages, in-repo notes) gets written in the author's own register, not default assistant prose. Lore content has its own voice per character. See [.claude/VOICE.md](.claude/VOICE.md) for both.

**4. Keep these files current:** [CHRONICLE.md](CHRONICLE.md) for landmark sessions, [TODO.md](TODO.md) for design decisions and open gaps, [SESSION_LOG.md](SESSION_LOG.md) for where work left off between sessions.

---

**Before ending a session** that covered landmark ground — a design decision, a changed mind, a real disagreement and its resolution, a surprising result, a new open question — append a short entry to [CHRONICLE.md](CHRONICLE.md). Not every session needs one; see that file's own header for what counts.

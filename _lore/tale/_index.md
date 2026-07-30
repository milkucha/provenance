# Tale — Told Directly

This is a third source of truth for Milkantis, alongside the **objective record**
(`_lore/material/` → `_lore/analysis/context.md`/`encodings.json`) and the **in-fiction subjective
record** (`_lore/analysis/hearsay.md` — what a *character* said inside a played dialogue, never
merged into the objective arrays). A tale is told directly by the user, the world's author, outside
of any character's mouth and outside of any excavated document. It is treated as genuine, on-par
source material: folded into `encodings.json`'s objective arrays (`locations`, `characters`,
`concepts`, `routes`, `time_systems`) wherever its content overlaps an existing entry, the same way a
newly-analysed `_lore/material/` file is folded in per `.claude/skills/integrate/SKILL.md` Pass 1 —
new entries can be added, a disagreement gets a `conflicts` entry (never silently resolved), but no
existing entry is ever overwritten to make room for a tale.

Populated by the `/tell` skill (`.claude/skills/tell/SKILL.md`). One file per tale, named for its
slug (`<slug>.md`). Every tale also gets an entry in `encodings.json`'s `tales.entries[]` array — see
that array's own `_method_note` for the exact shape and what `touches` means.

Like every source in this world, this one is partial too — a person only ever tells part of what they
know, at whatever moment they choose to tell it. A tale left unfinished, or one that raises a question
it doesn't answer, is not a defect; the gap is logged in `_lore/analysis/unknown.md` like any other.

## Tales on record

| Told | Title | File | Touches |
|---|---|---|---|
| 2026-07-30 | The Peregrins | `peregrins.md` | new concept `peregrins`; annotated the existing bare "Peregrin"/"Peregrins" census role tags (Terfila, Gorff) |

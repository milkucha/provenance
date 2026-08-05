# Tale — Told Directly

This is a third source of truth for Milkantis, alongside the **objective record**
(`_lore/material/_context.md` → `_lore/encodings.json`) and the **in-fiction subjective
record** (`_lore/characters/hearsay.md` — what a *character* said inside a played dialogue, never
merged into the objective arrays). A tale is told directly by the user, the world's author, outside
of any character's mouth and outside of any excavated document — whether narrated as a story or
stated plainly as a fact now known. Deliberately not distinguishing those with a fact/fiction label on
individual entries — a tale can be partly true, the way a real legend often is, and that ambiguity is
the point. It is treated as genuine, on-par source material: folded into `encodings.json`'s objective arrays
(`locations`, `characters`, `concepts`, `routes`, `time_systems`) wherever its content overlaps an
existing entry, the same way a newly-analysed `_lore/material/` file is folded in per
`.claude/skills/integrate/SKILL.md` Pass 1 — new entries can be added, a disagreement gets a
`conflicts` entry (never silently resolved), but no existing entry is ever overwritten to make room
for a tale.

Populated by the `/tell` skill (`.claude/skills/tell/SKILL.md`). One file per tale, named for its
slug (`<slug>.md`). Every tale also gets an entry in `encodings.json`'s `tales.entries[]` array — see
that array's own `_method_note` for the exact shape and what `touches` means.

Every tale distinguishes two different provenance questions. **`told_by`** (optional, lives in
`encodings.json` — it's lore, and can be sampled) is who is credited *in-fiction* with this telling,
if the tale itself is framed that way; most tales leave it unset, since a tale is normally just told
directly with no in-world frame. **`responsible`** (mandatory, lives in `_lore/tale/_authors.md` —
never in `encodings.json`) is which *real-world user* told the system this tale. That field has no
in-fiction meaning at all and is walled off from `scripts/sample_lore_knowledge.py`'s reach on
purpose, the same way `_lore/facts/facts.json` is — see that file's own `_comment`.

Like every source in this world, this one is partial too — a person only ever tells part of what they
know, at whatever moment they choose to tell it. A tale left unfinished, or one that raises a question
it doesn't answer, is not a defect; the gap is logged in `_lore/unknown.md` like any other.

## Tales on record

| Told | Title | Told by | Responsible | File | Touches |
|---|---|---|---|---|---|
| 2026-07-30 | The Peregrins | — | milkucha | `peregrins.md` | new concept `peregrins`; annotated the existing bare "Peregrin"/"Peregrins" census role tags (Terfila, Gorff) |
| 2026-07-30 | Creepers and Night Monsters | no one; simply now known | milkucha | `creepers_and_night_monsters.md` | new concept `world_hazards` |
| 2026-07-30 | Redstone and Basic Needs | no one; simply now known | milkucha | `redstone_and_basic_needs.md` | new concepts `redstone`, `basic_needs` |

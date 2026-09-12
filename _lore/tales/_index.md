# Tale — Told Directly

This is a third source of truth for this world, alongside the **objective record**
(`_lore/material/_context.md` → `_lore/encodings.json`) and the **in-fiction subjective record**
(`_lore/characters/hearsay.md` — what a *character* said inside a played dialogue, never merged into
the objective categories). A tale is told directly by the user, the world's author, outside of any
character's mouth and outside of any excavated document — whether narrated as a story or stated
plainly as a fact now known. Deliberately not distinguishing those with a fact/fiction label on
individual entries — a tale can be partly true, the way a real legend often is, and that ambiguity is
the point. It is treated as genuine, on-par source material: folded into `encodings.json`'s objective
categories (`locations`, `characters`, `concepts`, `routes`, `time_systems`) wherever its content
overlaps an existing entry, the same way a newly-analysed `_lore/material/` file is folded in per
`.claude/skills/integrate/SKILL.md` Pass 1 — new entries can be added, a disagreement gets a
`conflicts` entry (never silently resolved), but no existing entry is ever overwritten to make room
for a tale.

## Two ways a tale gets created

**Manual**, via the `/tell` skill (`.claude/skills/tell/SKILL.md`) — the user tells something directly,
narrated as a story or stated plainly as a fact, and the skill records it end to end: its own file
here, a manifest entry in `encodings.json`'s `tales.entries[]`, the fold into other categories, and the
row in `_authors.md` below.

**Automatic**, from `/simulate`'s birth and death mechanics — a reproduction (`generate_offspring.py`'s
`write_birth_tale()`) or a death (`record_death.py`'s own tale-writing) is a discrete event in the
world, so each one gets written as a real tale here, in the same shape a manually-told tale would take
(`told_by` left as "no one; simply now known", `responsible` set to whoever ran the pass), rather than
left as an ad-hoc note with no real backing entry. Both paths land in the same place and are
indistinguishable once on record — a reader of `_lore/tales/` can't tell a `/tell`-authored tale from a
`/simulate`-generated one just by its shape.

One file per tale, named for its slug (`<slug>.md`). Every tale also gets an entry in
`encodings.json`'s `tales.entries[]` array — see that array's own `_method_note` for the exact shape
and what `about` means (that field lists every id, in any objective category or `conflicts`, this tale
added or amended — see `_lore/encodings.json`'s `_categories.tale.fields`).

## Told by vs. responsible

Every tale distinguishes two different provenance questions. **`told_by`** (optional, lives in
`encodings.json` — it's lore, and can be sampled) is who is credited *in-fiction* with this telling,
if the tale itself is framed that way; most tales leave it unset, since a tale is normally just told
directly with no in-world frame. **`responsible`** (mandatory, lives in `_lore/tales/_authors.md` —
never in `encodings.json`) is which *real-world user* (or process, for the automatic path) told the
system this tale. That field has no in-fiction meaning at all and is walled off from
`scripts/lore/sample_lore_knowledge.py`'s reach on purpose, the same way `_lore/facts/facts.json` is —
see that file's own `_comment`.

## Folding into the objective record

A tale's content is folded into whichever of `locations`/`characters`/`concepts`/`routes`/
`time_systems` it overlaps: a brand-new entry gets added in the same shape as its neighbors, and an
existing entry gets a `tale:<id>` item appended to its `sources` list — never overwritten, never
rewritten to match the tale's version if the two disagree. A genuine disagreement instead becomes a
new `conflicts` entry (`user_resolution` left unset, never inferred or resolved by the skill that found
it).

Like every source in this world, this one is partial too — a person only ever tells part of what they
know, at whatever moment they choose to tell it. A tale left unfinished, or one that raises a question
it doesn't answer, is not a defect; the gap is logged in `_lore/unknowns.md` like any other.

## Recordkeeping

See `_authors.md` for real-world recordkeeping — which user (or process) told the system each tale,
and when. That file is not lore and is never read by any skill that plays a character.

## Tales on record

| Told | Title | Told by | Responsible | File | About |
|---|---|---|---|---|---|

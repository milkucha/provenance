# Discoveries — What Is Now Known

The fourth source of truth for Milkantis, populated the same way `_lore/tale/` is but for a different
kind of statement: not a story told, but a fact that has become known, plainly asserted as such rather
than narrated. Like a tale (see `_lore/tale/_index.md`), a discovery comes directly from the user, the
world's author, and is treated as genuine, on-par source material — folded into `encodings.json`'s
objective arrays wherever it overlaps an existing entry, new `conflicts` entries raised (never
silently resolved) when it disagrees with something already on record, no existing entry ever
overwritten.

What makes a discovery distinct from a tale is provenance: every discovery names who is responsible
for it — a character, a person, an institution — or, explicitly, that it has no such author and is
simply now known, with nobody credited. That distinction is recorded on the entry itself and is not
optional; "nobody" is a real, deliberate answer here, not a placeholder for an unfilled field.

Populated by the `/discover` skill (`.claude/skills/discover/SKILL.md`). One file per discovery,
named for its slug (`<slug>.md`). Every discovery also gets an entry in `encodings.json`'s
`discoveries.entries[]` array — see that array's own `_method_note` for the exact shape and what
`touches` means. Processed in every other respect exactly like a tale: cross-integration into other
categories, and a notable unresolved thread logged to `_lore/analysis/unknown.md` when one of the
discovery's own implications isn't itself answered by what was said.

## Discoveries on record

| Discovered | Title | Responsible | File | Touches |
|---|---|---|---|---|
| 2026-07-30 | Creepers and Night Monsters | known - no one responsible | `creepers_and_night_monsters.md` | new concept `world_hazards` |
| 2026-07-30 | Redstone and Basic Needs | known - no one responsible | `redstone_and_basic_needs.md` | new concepts `redstone`, `basic_needs` |

# Authors — Real-World Recordkeeping

This file tracks which *real* user told the system each tale, and when — administrative metadata
about the record's own history, not lore, and it has no in-fiction meaning at all. Not to be confused
with a tale's `told_by` in `../encodings.json` (in-world credit, which *is* lore and can be sampled).
`Responsible` here answers a different question entirely: who, in the real world, entered this into
the record.

**Must never be folded into `_lore/encodings.json` and must never reach
`scripts/lore/sample_lore_knowledge.py`'s pool** — same isolation guarantee as `_lore/facts/facts.json`,
for the same reason: this is the floor the record stands on, not part of it. Every tale entry is
required to have one (unlike `told_by`, which is optional). Exists so contributions can be attributed
and audited if this ever becomes a multi-author project — for now, with a single author, every entry
reads the same.

## Authors on record

| Id | Responsible | Recorded |
|---|---|---|
| `peregrins` | milkucha | 2026-07-30 |
| `creepers_and_night_monsters` | milkucha | 2026-07-30 |
| `redstone_and_basic_needs` | milkucha | 2026-07-30 |

# Authors — Real-World Recordkeeping

This file tracks which *real* user (or process) added each grounding entry, and when —
administrative metadata about the record's own history, not lore. Mirrors
`_lore/facts/_authors.md` and `_lore/tales/_authors.md`'s shape and isolation guarantee: never read
by any skill that plays a character, and irrelevant to `scripts/lore/sample_lore_knowledge.py`, since
grounding is never in its pool at all (see `_index.md`). Unlike a tale's `told_by`, grounding has no
in-world attribution counterpart to stay distinct from — a `mechanics.json`/`world_state.json` entry
is either universal or routine-gated, never credited to an in-fiction speaker.

## Authors on record

| Id | File | Responsible | Recorded |
|---|---|---|---|

`world_state.json` has no entries yet — once the external vision pipeline delivers its first output,
record each entry here the same way, with `Responsible` naming whoever ran that pipeline and fed the
result in.

# TODO

Open implementation decisions and work, deferred for later. This is a build/production backlog —
open questions about the lore itself live in `_lore/unknowns.md`, not here.

## Survival mechanism (not yet built)

`scripts/lore/roll_home_visit.py` (added 2026-08-28) decides who's home vs. visiting each pass with
a flat 50/50 coin flip, on purpose — see its own docstring. The intended end state is for a
not-yet-built survival-pressure mechanism to weight that roll instead: a character under survival
pressure (upkeep, resource scarcity — whatever that system ends up meaning) should skew toward
staying home, while one whose arc genuinely needs them elsewhere should skew toward visiting. When
that system exists, this is the one call site to change — `roll_home_visit.py`'s own `--p1`/`--p2`
random.choice, plus whatever new inputs (survival state, arc-need strength) the weighting needs to
read. Nothing else in the pipeline depends on this staying a flat coin flip.

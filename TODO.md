# TODO

Open implementation decisions and work, deferred for later. This is a build/production backlog —
open questions about the lore itself live in `_lore/unknowns.md`, not here.

## Survival mechanism (built 2026-08-28, on `survival-arc-test` — not yet tuned at scale)

Built: `wealth_lib.py`, `roll_survival.py`, `apply_survival.py`, `apply_upkeep.py` (all new), plus
`_lore/tuning.json`'s `survival` block. Each pass, the two drawn participants roll **survive** (net
0 personally, feeds the location's `wealth` pool) or **arc** (costs personal energy and the pool,
gated on actually winning that pass's primacy) — a weighted roll, not free choice, same "skew, never
decide" shape as `roll_contested.py`. `roll_home_visit.py` is now skewed by that choice instead of a
flat coin flip. Energy hitting 0 is a second, independent death vector alongside the rolled lifespan.
Every weight/threshold/cost in `tuning.json` is a first guess, flagged as such — nothing tuned yet.

# TODO

Open implementation decisions and work, deferred for later. This is a build/production backlog —
open questions about the lore itself live in `_lore/unknowns.md`, not here.

## Test suite — deferred items (built 2026-08-30, per `TESTING_BRIEF.md`, vault-side `projects/provenance/`)

- **Semantic drift is not implemented.** `scripts/test/measure_drift.py`/`measure_divergence.py`
  only measure lexically (edit distance, bigram Jaccard, bag-of-words) — an embeddings-based
  semantic-distance measure was explicitly scoped out per the brief's own lean-first constraint
  (§7: no heavy dependencies, keep the token/compute budget down since the whole point is longer
  runs). Both scripts accept `--semantic` but raise `NotImplementedError` rather than silently
  no-opping. Revisit if lexical distance alone turns out to miss genuine paraphrase-level drift.
- **`next_scene_id.py` (a scene-transcript filename collision guard) doesn't exist on this branch,
  despite `LAB_REPORT.md` describing it as built.** Found while writing
  `scripts/test/conformance_report.py`'s scene-id-uniqueness invariant check — that check currently
  only reports numeric collision-recovery suffixes (`_2.md`, etc.) as a best-effort heuristic,
  not a hard guarantee. Out of the test-suite brief's own scope to fix; worth tracing whether this
  script was ever actually promoted from a worktree, per `LAB_REPORT.md`'s own account of it being
  "written ad-hoc... never promoted."

## Survival mechanism (built 2026-08-28, on `survival-arc-test` — not yet tuned at scale)

Built: `wealth_lib.py`, `roll_survival.py`, `apply_survival.py`, `apply_upkeep.py` (all new), plus
`_lore/tuning.json`'s `survival` block. Each pass, the two drawn participants roll **survive** (net
0 personally, feeds the location's `wealth` pool) or **arc** (costs personal energy and the pool,
gated on actually winning that pass's primacy) — a weighted roll, not free choice, same "skew, never
decide" shape as `roll_contested.py`. `roll_home_visit.py` is now skewed by that choice instead of a
flat coin flip. Energy hitting 0 is a second, independent death vector alongside the rolled lifespan.
Every weight/threshold/cost in `tuning.json` is a first guess, flagged as such — nothing tuned yet.

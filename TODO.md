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

- **Orchestrator token-cost tracking, not built (2026-08-30).** The user wants a way to compare a
  `/simulate` run's actual token cost across dispatch models (Local/Ollama vs. the old
  subagent-per-pass Claude design, remembered at ~20k tokens/pass) — confirmed feasible while
  investigating the local-model integration: Claude Code's own session transcript
  (`~/.claude/projects/<project>/<session-id>.jsonl`) logs per-turn `usage` (input/output/
  cache_creation/cache_read tokens) with timestamps, and `isSidechain` distinguishes a subagent's own
  turns from the orchestrator's. Deliberately not built now — the user asked to defer it rather than
  spend more session budget on it. If revisited: a script summing usage between two timestamps
  (start/end of a run's Step 2-4), split by sidechain vs. not, would give the comparison without
  needing anything heavier.

## Survival mechanism (built 2026-08-28, on `survival-arc-test` — first-playtested and retuned 2026-08-29)

Built: `wealth_lib.py`, `roll_survival.py`, `apply_survival.py`, `apply_upkeep.py` (all new), plus
`_lore/tuning.json`'s `survival` block. Each pass, the two drawn participants roll **survive** (net
0 personally, feeds the location's `wealth` pool) or **arc** (costs personal energy and the pool,
gated on actually winning that pass's primacy) — a weighted roll, not free choice, same "skew, never
decide" shape as `roll_contested.py`. `roll_home_visit.py` is now skewed by that choice instead of a
flat coin flip. Energy hitting 0 is a second, independent death vector alongside the rolled lifespan.

**Round-2 debrief (2026-08-29, 50-pass pilot on `survival-arc-test`) — retuned and extended:**
- **Wealth pool went deeply negative with zero mechanical consequence** — an earlier `survive_take`
  retune had silently zeroed survive's own pool contribution
  (`survive_contribute(2) - survive_take(2) = 0`, when the intent was +1), and per-capita upkeep
  drained faster than at most 2 active participants could ever contribute back. Fixed:
  `survive_contribute` 2→3, `upkeep_rate_per_capita` 0.5→0.15, `energy_cap` 5→10 (more runway before
  the fragile low-energy floor).
- **Arc draws on an empty pool now cost the character instead of driving the pool further negative**
  — `arc_extra_cost_scarce` (`apply_survival.py`) replaces `arc_extra_cost` when the pool can't
  afford the draw, reported back as `scarce: true` so it's a real story fact, not a silent number
  change: the town having nothing left to give becomes a felt, in-fiction consequence.
- **New anticipation input, `scarcity_pressure`** (`roll_survival.py`, weight 15) — skews the roll on
  whether the pool's per-capita wealth has been *declining* since `apply_upkeep.py`'s last checkpoint
  for that location (`wealth_lib.wealth_trend()`/`checkpoint_wealth_trend()`), not just its current
  level. Deliberately one-directional: a worsening trend pushes toward "survive," a recovering one
  applies no extra pull toward "arc."
- **Childhood/age — resolved as a real open question, not a judgment call:** there was no design
  decision anywhere for what a character "is" between birth and `child_cooldown_passes` clearing (a
  newborn's inherited `routines` are literal, verbatim copies of a parent's own adult routine text,
  which reads as nonsense for a character who by any reasonable pass-to-time mapping is an infant).
  Resolved directly: **the cooldown period *is* the childhood** — a character exists, may be known of
  or talked about, but never appears in a scene during it. Once `child_cooldown_passes` clears and
  `pick_pair.py` admits them to the pool, they are an ordinary adult participant from that pass on,
  full stop — no infant handling, no parent-carries-them pattern.
- **Architecture: split content-generation from mechanism-execution.** The subagent-per-pass design
  used through round 2 had one subagent both write the scene AND drive every `py scripts/lore/...`
  call itself — auditing an actual run found this cost 3-6x the intended tool calls per pass on top
  of re-sending a long, rule-heavy prompt from scratch every pass, with no cache reuse across passes.
  Redesigned: the **enacter** gets only the brief and standing writing rules, no tools at all, and
  returns one structured reply (scene + hearsay claims + experience/grounded_experience/
  criterion_move) — the one genuine judgment call left in the pipeline, cheap enough in principle to
  eventually run on something small/local. The **orchestrator** does everything else itself,
  deterministically: `pass_prep.py`, writing the scene file, building both driver scripts' JSON
  payloads from the enacter's reply, calling `pass_record.py`/`pass_apply.py`, composing a newborn's
  name on `reproduces: true`. See `.claude/skills/simulate/SKILL.md` Step 3 for the full spec.
- **Correction, same day, 20 passes into the first run under the new split:** the redesign above was
  only half-finished in practice — the orchestrator was still hand-composing the enacter's brief as
  prose paragraphs instead of pasting `pass_prep.py`'s own JSON output directly, and separately
  re-deriving character criterion/arc-premise data via an ad-hoc one-off call every pass. Both fixed:
  `pass_prep.py` now also returns a `characters` block (criterion + arc premise for both
  participants) in the same call, and the enacter dispatch is a direct paste of that JSON plus the
  fixed preamble plus, only when genuinely needed, a 1-2 sentence director's note — never a prose
  retelling. Written up as a standing design principle in `.claude/PRINCIPLES.md`: **script
  everything that can be scripted; prose only where a judgment call genuinely needs it.**

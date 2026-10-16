# TODO

Open implementation decisions and work, deferred for later. This is a build/production backlog —
open questions about the lore itself live in `_lore/unknowns.md`, not here.

## Website and front-end platform (raised 2026-10-16, direction decided, nothing built)

Stage 1: static explainer site (blueprints plus prose), no backend. Stage 2: local web app, a backend
wrapping the existing scripts and `simulate_driver.py`, serving a UI on localhost; worlds stay files
in git so corpus branches keep working. Stage 3: hosted version, only if there's demand.
- Stack: TypeScript and React (the rest of the libraries still to pick).
- Engine and model access stay separate: one small `complete(task, prompt)` interface, providers
  behind it (Ollama, any OpenAI-compatible endpoint). OpenCode is a possible optional adapter, not
  the runtime; its server mode is unverified.
- Parked: a hosted default model for everyone, and who pays for inference. Decide with real
  per-pass token numbers (`simulate_token_usage.py`, `LAB_REPORT.md`).
- Run the test suite per model tier so "supported models" is a measured list.
- Typography: serif (Georgia or similar), matching the banner and blueprints. GitHub's README can't
  change fonts (it strips CSS), so this is a requirement for the site, not the README.
- Prerequisite: audit which skills (`/enact`, `/character`, ...) still need an interactive agent
  and can't run through the headless driver.

## Branch workflow (decided 2026-10-16)

`provenance-standalone` stays engine-only, no corpus, always current. Corpora get their own branch off
it: `corpus-three-cities` exists; a Milkantis branch (Minecraft forever-world lore) is next.
- Open on `corpus-three-cities` (see its `OPEN_QUESTIONS.md`): `criterion.derivation` should be
  `"derived"` for the 15 authored characters, `contexts.json` `provides` vocabulary vs. standalone's
  (OPEN_QUESTIONS.md on standalone), and 9 characters keep `origin` in `criterion.history`.
- Standalone: `provisions_lib.set_provisions` has no floor; `data/` and `_npcs/` still carry named
  NPC dialogue; `GESTURES.md` says 13 gestures, README says 12; `apply_language_layer.py` and
  `simulate_record_run.py` failed `--help` under the corpus agent's run but passed the earlier smoke
  check, so check whether it's the environment; the "not built" headers below for travel and
  provisions are stale after c444b49.

## Audit of one `/simulate` pass after c444b49 (2026-10-16, bugs; design questions went to OPEN_QUESTIONS.md)

Ran the mechanical scripts (no model) on a scratch copy of `corpus-three-cities`, seeded, 40 and 200 passes, plus two fixtures with a travel graph. Marked RAN or READ. The diagram is at the artifact link in the session, not in the repo.
- [ ] **Nobody can pay, so no scene ever happens (RAN).** `provisions` defaults to 2 (`_template.json`, and the `.get` default in `arc_payment_gate`/`roll_survival`), `arc_need_cost` is 3, so the gate answers `cannot_afford` before it rolls. Nothing grants a character provisions either (only the payee gains, `simulate_pass_lib.arc_payment_gate`), so a world seeded with defaults stays stuck. Corpus run: 0 motivated passes in 40. Fixture: `cannot_afford` for the default-2 characters, `paid` only for the ones I hand-set to 8. A source of personal provisions (or a starting value above the cost) is missing.
- [ ] **A locally satisfiable need costs energy and goes nowhere (RAN).** `run_pass_mechanics()` Step 4 returns after the routine roll: no `arc.history` entry, no payment, no scene. 19 of 40 corpus passes and 90 of 200 fixture passes were this, each paying `arc_extra_cost`. In a three-city world every need is provided somewhere in each city (`location_provides` is presence-only), so arcs freeze. Whether that is meant is a question, see OPEN_QUESTIONS.md.
- [ ] **The criterion shock gate isn't in the brief (READ).** SKILL.md Step 3 point 4 says `criterion_move` is for when "the brief's own anchor-reference check flagged it", but `pass_prep.py`/`simulate_pass_brief.py` never run `check_anchor_reference.py`; `pass_record.py` runs it after the scene, and `simulate_driver.py` throws that output (and `check_resonance.py`'s) away. A move is whatever the model volunteers, and `synthesis` never fires on the driver path.
- [ ] **`measure_drift` has no producer (READ + RAN).** `enact_via_ollama.REPLY_SCHEMA` has no `derived_from`, `lineage_coin.py` has no call site on the unattended path, and `pass_prep.py` never samples the hearsay pool into the scene. The instrument ran and found "no retelling edges".
- [ ] **The dead can be met (RAN).** `candidates_at()`, `location_provides()`, `find_supplier_locations()` and `travel_graph`'s known-people lookup never check `life.deceased`. On the corpus copy, 13 of the 35 candidates at one city were dead; a dead character can be rolled as p2, take the payment, get `lived` +1 and be recorded as a partner. Their routines also still make a city "provide" things.
- [ ] **Meetable pool isn't filtered by the need (RAN).** `candidates_at()` takes everyone with a routine at the location; p2 then has to roll that location and a providing context. With one supplier among 22 it was 9 mismatches out of 11 meetings.
- [ ] **A journey resets on a survive roll (READ).** Step 3 rolls the character's own routine, so a traveler mid-route is back at a routine location the next time they choose survive. Also `roll_survival` is handed `p1_char["location"]` as "home", which after a hop is the hop.
- [ ] **Solo-pass death: recorded, not finished (READ).** `apply_solo()` calls `record_death.py`, but shock candidates are never resolved and death-legacy never rolls; the manual path in SKILL.md has no CLI for `apply_solo` at all (`pass_apply.py`/`pass_record.py` still require `--p2`).
- [ ] **`conformance_report.py` flags 69 kin-as-partner failures on the pristine corpus (RAN).** The invariant is `parents & partners`, but `record_partner` now fires on any crossing and pairing no longer excludes kin (the real exclusion is in `simulate_pass_reproduction`). It tests the wrong thing now. Its fixed-odds table also lists `roll_lead_followup` (dead) and misses survive/meetable/payment.
- [ ] **p2 gets no survival step (READ).** No upkeep, eating or energy cost for the person met, only `lived` and the partner bump. A newborn gets no `energy`/`provisions` (defaults), and a dead character's provisions vanish.
- [ ] **Dead or write-only (READ):** `leads` (written by `apply_contested_lead`, read by nothing), `social_circle` (read in 3 places, written by nothing), `last_scene` (no script reads it), tuning keys `lead_expiry_passes`, `home_visit_survival_shift`, `odds_percent.lead_followup`; `arc.context` is only read by death-legacy and `register_arc_concept`.
- [ ] **Stale (READ):** `diagrams/gen_simulate_pass.py` and `simulate-pass.html` still draw the pair model with lead override; `roll_contested.py` and `simulate_pass_reproduction.py` docstrings say `partner_threshold` 5 (tuning says 3); `enact_preamble.md` still talks about "who is home and who is visiting".
- `set_provisions` has no floor: confirmed (RAN, it stores -5), but nothing can reach it today (`apply_survival` only eats when `pool >= eat_amount`, `apply_upkeep` clamps at 0). Latent, not live.

## What the enacter is given: three gaps found reading the brief (raised 2026-10-17, not fixed)

Found while walking through one pass; each confirmed by reading `pass_prep.py`, `enact_preamble.md` and
`simulate_driver.py`, and by running `pass_prep.py` on a scratch corpus copy.
- **No knowledge goes in.** The enacter gets each character's criterion, routine and arc premise, and
  nothing of their education, experience or hearsay, nor anything about the place (what Gorff is).
  `/simulate`'s SKILL.md says this on purpose (short, stable prompt for small models), but the
  preamble still tells it to never invent anything "outside a character's own sample" with no sample
  given, and Part I's "agents only know what their characters know" isn't true of the scene in any
  useful sense.
- **`horizon_pre.ending: true` reaches the enacter.** The lifespan is meant to be secret (the model
  may only be told early/established/late), and the preamble says it can't know whether a scene is a
  last one, yet the JSON it receives carries `ending` and `lived`. Likely a leak; the rest of the
  system treats the field as orchestrator-only.
- **The brief's fields are never explained to the model.** The preamble covers `arc.gate`/`outcome`
  and little else; `motivated`, `matched_need`, `contested`, `survival`, `horizon_pre` are raw flags
  with no legend.
- Failure modes (arrived and nobody there, had the means but didn't find them, can't pay, no route,
  nowhere to look, died on the way) are not named by the code today: each branch only appends a
  free-text line to `notes`. Idea to discuss: each branch sets a structured `pursuit` stage and reason.

## Pursuit redesign: destination choice, failed pursuits as scenes (raised 2026-10-17, direction set, not built)

Author's decisions, from the walk-through of one pass:
- **Destination choice is weighted, not nearest-wins.** Known suppliers (people in the character's own
  circle) skew the dice toward them; general places are weighted by closeness in connections (hops).
  Today it is deterministic: known suppliers always win, then fewest hops, no dice
  (`location_context.resolve_arc_target`, `travel_graph.shortest_path`).
- **A chosen destination is kept.** The character keeps moving that way until arriving and either
  meeting or failing; on a failure while pursuing an arc, the process starts again. (Audit F7: a survive
  roll mid-journey currently resets the journey.)
- **Nobody useful at the place:** a conversation with whoever else is there, their routine rolled too;
  an empty place is a solo scene.
- **Can't pay:** a scene with the provider present. No arc outcome is rolled on a failed-payment scene;
  the arc outcome is rolled only once the purchase conditions with the supplier are met.
- The brief carries what the enacter needs to know about the situation; the facts are rolled first.
- Open: the brief's shape (see what the enacter is given: `pass_prep.py` output = `horizon_pre`,
  `brief`, `characters`); whether a failed-payment scene can roll an outcome that moves provisions
  (favor, debt, work for pay), which would also be the faucet the audit says is missing; token cost,
  since every pursue pass would now spend a model call and lean is a stated objective; tie-breaking in
  the travel graph (neighbours are sets, so order may vary between processes, unverified).

## `leads`/rivalry-followup mechanism orphaned by the asymmetric per-pass rewrite (raised 2026-09-13, not built)

The old pairing model's rivalry-persistence loop — a contested "hinder" outcome writes a `leads`
entry (`apply_contested_lead.py`), and `roll_lead_followup.py` could later override which second
participant got drawn to force a pass toward pursuing an unexpired one — has no call site left
anywhere in the new single-`p1`-draw algorithm (`simulate_pass_lib.run_pass_mechanics()`; see
`simulate_resolve_pair.py`'s own docstring, which first flagged this). `leads` entries still get
written by the unchanged contested/hinder chain, but nothing reads or drains them any more — dead
data quietly accumulating, not a crash risk, but a lost mechanic. Per an earlier audit tonight, this
was the one confirmed-working multi-pass feedback loop in the whole system. Needs a real design
pass before rebuilding it — a plausible third pathfinding tier that prefers an open lead's target
over ordinary need-resolution is one option, not decided here — just flagged so it isn't lost.

## `social_circle` update mechanism not yet decided (raised 2026-09-13, not built)

`_lore/characters/_template.json` now carries a persistent `social_circle` field (extended circle —
scene co-participants + backstory mentions, distinct from `partners`/`parents`), but nothing writes to
it yet. Follow-up design pass needed: which skill/script updates it, and on what trigger (every
`/enact` Step 10? a dedicated script run at batch end?) — deliberately left open here, not decided.

## Machine-generated seeds, as a control for isolating engine quality from seed quality (raised 2026-09-12, not built)

Every seed the engine has grown from so far is hand-authored — twelve years of the user's own
material, or a hand-built test corpus (three-cities-baseline, etc.). That's a confound: when a run's
drift reads as organic and the tasting scores hold up, there's no way yet to tell how much of that is
the mechanism actually working versus the seed material already being unusually rich, since a
sufficiently good hand-authored corpus could make almost any downstream mechanism look decent.

The fix isn't "let the machine invent a world by algorithm" the way Dwarf Fortress or Talk of the Town
generate their towns from a closed rule-set (fixed, enumerable, deterministic given a seed) - see
`CHRONICLE.md`'s 2026-09-12 entry for the fuller distinction. **The seed still has to be made of the
same kind of thing either way: semantic content - facts, sociocultural parameters, character
fragments - not the closed rule-set itself unfolding into content on its own.** What'd change is only
the seed's *source*, not its *nature*: a machine producing that same shape of content unprompted by
real source material, the way `/tell`/`/character`/`/integrate` produce it now from a human, rather
than DF-style world-gen producing history as a side effect of simulating physics forward.

Not scoped yet - open questions before this is buildable:
- What does "the machine invents a seed" actually call, mechanically? Probably a new skill/script
  that prompts for the same handful of parameters `/start`'s door already implies a seed needs
  (sociocultural parameters + a handful of grounding facts), then has a model author plausible-but-
  synthetic answers instead of eliciting them from the user.
- How would a run against a synthetic seed even be compared fairly to a run against the real
  corpus - same test-suite instruments (`measure_derivation.py`/`measure_drift.py`/tasting), but
  probably needs its own LAB_REPORT.md-style bucket so the two populations of runs (real-seed vs.
  synthetic-seed) don't get averaged together and hide the comparison being made.
- Sequencing: likely worth building only after the playability-horizon question above has enough
  offline evidence behind it that this specific confound (mechanism vs. seed quality) becomes the
  actual bottleneck on trusting that evidence, rather than before.

## Open question: what signals "stop testing offline, start building the live/standing world" (raised 2026-09-12, not decided)

The project has two use cases in view that share one mechanism, not two: `/simulate` as an offline
narrative-drift generator (proving the engine works, cheaply, before committing further), and
eventually a live, always-on Minecraft world where characters keep running their own routines whether
or not the user is present, and stepping in as a player adds a participant to an already-running
simulation rather than pausing it — see `CHRONICLE.md`'s 2026-09-12 entry for the fuller reflection
(prompted by an unprompted resemblance to Dwarf Fortress's fortress mode). Explicitly not building the
live version yet — the engine-validation phase needs to run its course first, via the `scripts/test/`
measurement suite (`conformance_report.py`, `measure_derivation.py`, `measure_divergence.py`,
`measure_drift.py`, `record_tasting.py`).

What's missing is a stated threshold: some signal on those instruments that would actually mark "yes,
move on," rather than the validation phase just continuing indefinitely by default. Candidates worth
deciding between (not yet decided): a tasting score (felt contingency specifically) holding up
consistently across several different populations/seeds, not just one hand-tuned cast; a target
derivation-coverage percentage; a run producing an arc outcome or criterion break the user genuinely
didn't see coming, repeated across more than one run. Also unaddressed: the live version's pacing (a
pass shouldn't resolve instantly the way a batch `/simulate` run does — it needs to feel like it's
moving at something closer to a human, inhabitable rate) and its dispatch cost floor (an always-on
world sustaining NPC-to-NPC scenes nobody's watching can't be billed per API call the way a bounded
test run can — the local-model/Ollama dispatch path is closer to a precondition here than a nice-to-have).

## Grounding mechanics need causal/recipe structure, not just vocabulary (design discussion 2026-09-12, not built)

`_lore/grounding/mechanics.json` currently supports exactly two entry shapes: universal/contextual
propositional rules (the old "creepers are dangerous" style, since cleared out) and, per this session's
design conversation, vocabulary grants — naming a concrete thing that exists in the world (e.g.
"cobblestone") so a character can refer to a real material instead of a generic placeholder. Neither
shape alone gets arc resolution to causal specificity: an arc like "build a sword" needs the record to
say a sword requires iron + a stick, not just that "materials" exist as an abstract bucket a character
can dip into.

Proposed direction, not built yet, needs its own design pass before touching code:

- `mechanics.json` entries need at least two distinct shapes: existence/vocabulary entries (a named
  material or item exists in this world) and recipe/causality entries (an item requires a specific list
  of materials).
- Tie into `_lore/contexts.json`'s `provides` field (a minimal 6-value vocabulary as of the 2026-09-12
  rewrite — `materials`, `items`, `transit`, `nourishment`, `records`, `news`): a context's
  `provides: "materials"` names an abstract category, and mechanics.json entries tagged with that
  category are its concrete instances — cobblestone/iron/marble are `materials`, a sword is an `item`.
- `scripts/lore/check_needs_provides.py` currently only runs a semantic yes/no category check (does
  this context provide `materials`). It should eventually pick and name a concrete mechanics.json
  instance the character actually obtained, giving causal specificity ("got iron at the market")
  instead of a generic label ("got materials").
- Sequencing: build this only after the simpler, already-scoped grounding pieces land — `world_state.json`
  entries referencing real `locations[].id` values, and a character-level `places_visited` accumulator
  gating grounding access (both being implemented separately, same session).

## Travel system design sketch (design discussion 2026-09-12/13, refined, still not built)

Arc resolution currently checks a character's context `provides` too abundantly — whatever context
they're already in generally satisfies a requirement, so there's no real scarcity forcing anyone to go
anywhere. The fix under discussion: let some arc requirements demand a *specific location*, not just
"any context providing X" — only what that particular place's context actually offers counts. That's
what would make travel matter mechanically instead of being decorative. None of this is built; sketched
only.

- **Locations form a graph.** Nodes are `_lore/encodings.json` `locations[]` entries; edges are
  `_lore/encodings.json` `routes[]` entries via their `endpoints` field. This isn't an incidental fit —
  `route.endpoints` was deliberately shaped this way in the 2026-09-12 `encodings.json` restructure,
  specifically to serve as the travel graph's edge list later.
- **The `route` context** (one of the 5 elemental contexts, `_lore/contexts.json`,
  `provides: ["transit", "news"]`) is the natural enactment shape for a single hop of a journey — each
  step of a multi-hop trip could be played as a `route`-context routine/scene.
- **Reachability, refined (2026-09-13; supersedes the "adjacent to current location" framing above).**
  A character can pathfind toward: anywhere in their own `places_visited`, anywhere named in their own
  sampled knowledge pool (material/hearsay/tale entries known via `sample_lore_knowledge.py`), **and
  anywhere a person they know (`partners`/`social_circle`/`parents`) is located** — knowing a person is
  itself a route into a place never physically visited. All of this is gated by actual graph
  connectivity (`routes[].endpoints`): a character can't path to a *known* place with no connecting
  route, only to known places reachable by an actual sequence of edges. Realizes the instinct already in
  the user's own working notes about scoping travel to "nodes they've heard about or locations where
  characters they know exist," and making travel to unknown territory costlier.
- **Multi-hop travel is real traversal, not a teleport.** A graph shaped `A - B - C - D` means reaching
  D from A requires passing through B then C in sequence — one step (one pass/turn) per edge, with a
  dice roll each step on whether the trip continues (mirrors the existing advance/stall/reverse/
  transform discipline already used for ordinary arc-advancement rolls elsewhere in this system, e.g.
  `/simulate`'s arc tally mechanic).
- **Staging:** for now, the location graph (the `routes[]` edge set) gets hand-authored in a test seed,
  same discipline as everything else authored rather than generated in this system. Later,
  `_lore/grounding/world_state.json` (once fed by the external map/vision pipeline) becomes the actual
  *input* the location graph is derived from or checked against — not built yet, long-term direction
  only.
- **Dependency order:** builds on `places_visited` (character-level accumulator) and
  `world_state.json`'s real `locations[].id` referencing, both implemented earlier today. Natural
  companion to the "Grounding mechanics need causal/recipe structure" entry above (arc requirements
  checking against concrete `mechanics.json` instances) — both are about making arc resolution
  mechanically specific instead of abstractly semantic.

**Decision-order clarification (2026-09-13 follow-up).** This refines, rather than replaces, the
per-pass `pick_pair` → `roll_survival` → `roll_home_visit` → `roll_routine` sequence already documented
in the "Survival mechanism" entry below — see that entry for the sequence itself, not re-explained here.

1. `pick_pair` stays random/unskewed — explicitly NOT part of this travel-pathfinding change. How the
   *second* participant in a pair relates to a *first* participant's arc-driven travel is still
   genuinely open (see "Still open" below), not resolved by anything here.
2. `roll_survival` proceeds as normal, now also reading the new personal-cushion input from the
   "Personal provisions and inheritance economy" entry below (landing the same day, a parallel track —
   not re-described here).
3. **New: if a character chooses arc**, the normal weighted `roll_routine` pick (among a character's own
   hand-authored routines) is replaced for that pass by a pathfinding-driven check: does completing the
   arc's need require travel? If the need is satisfiable locally (one of the character's own routines
   already matches), that routine gets favored instead. If travel is required, the favored choice
   becomes a `route`-context "transit" step toward the next node on the path to wherever the need can be
   fulfilled.
4. **This is still a genuine dice roll, not a hard commitment.** Pathfinding computes a *favored*
   direction (the shortest/best path's next hop), which skews the roll, but the character can still end
   up somewhere else. This divergence is a deliberate feature: when it happens, the enacting agent has to
   dramatize *why* the character ended up elsewhere despite pursuing their arc — a real judgment call,
   the same category as how an arc's `premise` already gets re-composed after a `transform`, not a new
   kind of agent work.
5. Path recomputation is fresh-favorite-each-turn for now, not committed-until-invalidated — deliberately
   kept simple at this stage; revisit later if it reads as indecisive rather than as organic drift (see
   "Still open" below).

**Multi-destination handling (2026-09-13, minor clarification).** If more than one location could
satisfy an arc's need, pathfinding should compute distance to every valid candidate and take the
minimum — ordinary multi-source shortest path, no added complexity at this graph's likely scale.

**Still open, not decided by any of the above:**
- How the second participant in a pair relates to a first participant's arc-driven travel decision
  (`pick_pair` staying random, above) — genuinely unresolved.
- Whether path recomputation should eventually become commit-until-invalidated rather than
  fresh-favorite-each-turn.

## Personal provisions and inheritance economy (design discussion 2026-09-12/13, not built)

The "Survival mechanism" entry below only has a *communal* provisions pool, one per location. Today's
design conversation sketched a second scope for the same resource: a character can ALSO hold a
**personal** provisions reserve. Not a second resource requiring its own naming scheme — that
collision (two genuinely different things sharing one word) is exactly the kind Task 1's wealth→
provisions rename this session was trying to avoid; this is the same substance held at a different
scope, so scope-qualified names (personal vs. communal/pool) carry the distinction instead of a new noun.

- **Earned by completing an arc**, not by routine survival — arcs could plausibly both cost and grant
  provisions on resolution, not designed yet, needs its own pass once this lands.
- **Inheritance:** a character's personal reserve (or some portion of it) passes to their children at
  birth, via `generate_offspring.py` — the same shape of seeding it already does for a newborn's
  `places_visited`, just for a number instead of a list. A wealthy parent's children start more
  independent of needing to draw from the communal pool, which is the whole point of building this as
  inheritance rather than a flat per-birth grant.
- **Mechanism sketch:** when a character chooses to "eat" (the existing `survive`-choice universal
  eating step in `apply_survival.py`), they'd draw from EITHER their personal reserve OR the location's
  communal pool — personal first falling back to communal, or some other priority, not decided. A
  character with a healthy personal reserve becomes less dependent on the health of wherever they
  happen to be standing, which is the mechanical form Bourdieu's capital conversion takes here.
- **The Bourdieu framing**, raised in the same conversation and worth keeping as the organizing lens
  for arc-economy work going forward, not just color: this models three capital types. Cultural capital
  (`knowledge.education`/`experience` — already built, gates arc possibilities and travel reach).
  Social capital (`partners`/circle plus travel-through-known-people — partially built; "travel to
  where you know someone" is sketched in the Travel system entry above, and a persistent,
  continuously-updating `social_circle` character field was also proposed the same day, neither built
  yet). Economic capital (this personal-provisions system — not built at all). All three should read as
  one structure, not three unrelated mechanics.
- **Related but separate, don't conflate:** `/simulate`'s character-pairing (who gets scened with whom
  each pass) is effectively random today; the same conversation raised weighting it by characters' own
  arc-pursuit calculations instead — a real design point, but its own follow-up, not solved here.
- **Sequencing:** depends on Task 1's wealth→provisions rename (this same session) landing first — this
  is the natural next layer on top of the communal mechanism, not a replacement for it, and needs the
  renamed field names to build against.

## Survival mechanism (designed and built 2026-08-28, on `survival-arc-test` — not yet merged/tested at scale)

Every character now has personal `energy` (`_lore/tuning.json`'s `survival.energy_cap`, default 5;
lazily defaulted on first touch, same as `routines`/`arc`/`partners` before it — not backfilled into
every character file). Every location has a `provisions` pool in the new `_lore/provisions.json`, seeded at
`starting_provisions_per_capita × population` the first time it's read. Full mechanism:

- Each pass, only the two drawn participants resolve **survive** or **arc** (`roll_survival.py`,
  rolled against each one's own home `location`, before `roll_home_visit.py` even runs — matches the
  existing lazy per-character clock pattern; pool upkeep, `apply_upkeep.py`, is the only
  population-wide arithmetic, O(1) per location, applied once per pass to the resolved location, not
  once per participant). A character with no ongoing arc always survives, no roll needed.
- **Survive:** personal net 0 (−1 base, +1 taken from pool). Pool net +1 (contributes 2, taker
  takes 1), before upkeep. **Arc:** personal net −2. Pool net −2 (drawn, uncontributed) —
  `apply_survival.py` applies both, at the pass's RESOLVED location (which may differ from either
  participant's home), once `roll_home_visit.py` has decided where the scene actually happens.
- **`provides` gate, live in `simulate_pass_brief.py`/`simulate_generate_population.py`:**
  `provisions_per_capita ≥ provides_provisions_threshold` (2) before the needs/provides check even runs;
  below it, no bonus regardless of context match.
- **The survive/arc roll is a percentage-point shift off a 50/50 base** (`roll_survival.py`) — same
  unit and clamp [2, 95] every other roll in this pipeline already uses (`roll_contested.py` is the
  closest precedent), not the sigmoid the design conversation first sketched — kept it in-house-style
  instead. Four weighted inputs, all in `tuning.json`'s `survival.weights`: `energy` (normalized
  around the cap's midpoint), `arc_pressure` (`stage_weight[tally stage] + urgency_bonus[horizon
  band]`), `pool_reliance` (`pool_surplus × net_affinity` — a healthy pool only feels safe to lean on
  if actually connected), and `affinity_obligation` (`net_affinity` alone, pulling the other way).
  `net_affinity = Σ(partners_quality[p]) / Σ(partners[p])` across established partners
  (`count ≥ partner_threshold`) — one signed number, two roles, so strong-but-negative bonds push the
  correct direction on both terms.
- **`roll_home_visit.py` is now skewed by each participant's own survival choice**
  (`home_visit_survival_shift`, 20 points) — a participant who chose survive leans toward staying
  home; arc/no-arc contributes no skew.
- **Choosing arc without winning that pass's primacy still costs the full price** — real, not wasted
  bookkeeping. The arc-outcome gate (`simulate_pass_brief.py`/`simulate_generate_population.py`) now
  requires the primacy winner to have specifically rolled "arc" this pass; a primacy winner who rolled
  survive leaves the arc untouched regardless, and the OTHER participant's own "arc" roll (if they
  made one) still cost them the energy/pool price for nothing.
- **Energy hitting 0 is a second, independent death vector** alongside the existing rolled lifespan.
  `/generate` mode (`simulate_generate_population.py`) records it automatically, same post-scene block
  as the existing horizon-death check, with `--cause "exhaustion/starvation - energy depleted"`. The
  interactive path (`/enact` Step 8 point 6b) checks `.simulate_pass_brief.json`'s `survival.<slug>.died`
  and calls `record_death.py` the same way — deliberately NOT called automatically inside
  `simulate_pass_brief.py` itself, matching the existing horizon.py/record_death.py split (a
  mechanical fact stays separate from acting on it).
- **Not yet exercised at any real scale** — verified end-to-end against a handful of manual
  `simulate_pass_brief.py`/`simulate_generate_population.py` calls on the real Tyrnea cast (a
  starvation death fired correctly, tale written, `life.deceased` set, arc-gating and the provisions
  threshold both behaved as designed), then all test-mutated character/lore data was reverted before
  committing. A real multi-hundred-pass run, and actual tuning of the weights/thresholds/costs
  (everything above is a first guess, explicitly flagged as such throughout the design conversation),
  is still ahead.

**Round-2 debrief (2026-08-29, 50 passes, 0 deaths, 2 births) — retuned and extended:**
- **Provisions pool went deeply negative (-350.5) with zero mechanical consequence** — `apply_survival.py`
  let `arc` draws take the pool arbitrarily negative, and `apply_upkeep.py`'s per-capita drain
  (`population_of()` counts every living character registered at the location, not just the active
  cast — 13 at Tyrnea, not 10) ran unconditionally every pass regardless of anyone's choices. Root
  cause of the deficit's *rate*: `survive_take`'s earlier 1→2 retune silently zeroed survive's own
  pool contribution (`survive_contribute(2) - survive_take(2) = 0`, when the intent was +1) — nobody
  re-balanced the pool side after fixing the personal-energy side. Fixed: `survive_contribute` 2→3
  (restores +1 pool/survive without touching personal energy), `upkeep_rate_per_capita` 0.5→0.15
  (0.5 drained ~6.5/pass against at most 2 active participants' worth of contribution — structurally
  unbeatable). Still expected to need another look after a full run at the new numbers.
- **Arc draws on an empty pool now cost the character instead of driving the pool further negative**
  (`arc_extra_cost_scarce`, 2, replaces `arc_extra_cost` when `pool < arc_pool_draw`; reported back as
  `scarce: true` so the brief can hand it to the model as a real story fact, not a silent number
  change) — the town having nothing left to give is now a real, felt, in-fiction consequence, per
  the user's own framing: "if there's nothing in the town, they pay with their own life."
- **New anticipation input, `scarcity_pressure`** (weight 15) — `roll_survival.py` now also skews on
  whether the pool's per-capita provisions has been *declining* since `apply_upkeep.py`'s last checkpoint
  for that location (`provisions_lib.provisions_trend()`/`checkpoint_provisions_trend()`), not just its current
  level — lets characters anticipate trouble ahead instead of only reacting to it. Deliberately
  one-directional: a worsening trend pushes toward "survive," a recovering one applies no extra pull
  toward "arc."
- **Bond quality (`record_bond_quality.py`, `partners_quality{}`) confirmed working as designed** —
  briefly suspected broken (checked two characters whose interactions happened to be `mixed`/`neutral`
  this run, which correctly produce no change) before verifying it against characters with an actual
  `help`/`hinder` gate hit on file. It's fully automatic, wired inside `simulate_pass_brief.py` itself,
  no orchestrator or subagent involvement needed — `BOND_QUALITY_DELTA = {"help": 1, "hinder": -1,
  "mixed": 0, "neutral": 0}`, keyed off `check_arc_alignment.py`'s own `inclined` result.
- **Childhood/age — resolved as a real open question, not a judgment call:** there was no design
  decision anywhere for what a character "is" between birth and `child_cooldown_passes` clearing (a
  newborn's inherited `routines` are literal, verbatim copies of a parent's own adult routine text —
  "closes the stall," "lectures to students" — which reads as nonsense for a character who by any
  reasonable pass-to-time mapping is an infant). Resolved by the user directly: **the cooldown period
  *is* the childhood** — a character exists, may be known of or talked about, but never appears in a
  scene during it. Once `child_cooldown_passes` clears and `pick_pair.py` admits them to the pool,
  they are an ordinary adult participant from that pass on, full stop — no infant handling, no
  parent-carries-them pattern. (One round-2 session had, before this was resolved, treated a
  newly-eligible child as a nonverbal infant carried by a parent across three scenes past their own
  cooldown — kept as a design note, not something retroactively rewritten.)
- **Architecture: split content-generation from mechanism-execution.** The subagent-per-pass design
  used through round 2 had one subagent both write the scene AND drive every `py scripts/lore/...`
  call itself — auditing an actual run found this cost 3-6x the intended tool calls per pass (JSON
  schema retries, unnecessary exploration) on top of re-sending a long, rule-heavy prompt from scratch
  every single pass, with no cache reuse across passes. Redesigned 2026-08-29: the **enacter** gets
  only the brief and standing writing rules, no tools at all, and returns one structured reply (scene
  + hearsay claims + experience/grounded_experience/criterion_move) — this is the one genuine judgment
  call in the whole pipeline (writing prose, and reading a scene closely enough to judge a criterion
  move), and it's now the only thing left needing a language model, cheap enough in principle to
  eventually run on something small/local. The **orchestrator** does everything else itself,
  deterministically: `pass_prep.py`, writing the scene file, building both driver scripts' JSON
  payloads from the enacter's reply, calling `pass_record.py`/`pass_apply.py`, composing a newborn's
  name on `reproduces: true`. See `.claude/skills/simulate/SKILL.md` Step 3 for the full spec.
- **Correction, same day, 20 passes into round 3's own first run under the new split:** the redesign
  above was only half-finished in practice. The orchestrator was still hand-composing the enacter's
  brief as prose paragraphs every pass ("Pass 20. Location: the road between Tyrnea and the harvest
  fields...") instead of pasting `pass_prep.py`'s own JSON output directly — pure overhead, spent in
  the orchestrator's own tokens, restating facts a script had already computed. Caught by the user,
  who also pointed out the character-criterion/arc-premise fetch (a separate ad-hoc `py -c` call every
  pass) was the same class of gap. Both fixed: `pass_prep.py` now also returns a `characters` block
  (criterion + arc premise for both participants) in the same call, and the enacter dispatch is now a
  direct paste of that JSON plus a fixed instruction preamble plus, only when genuinely needed, a
  1-2 sentence director's note — never a prose retelling. Written up as a standing design principle in
  `.claude/PRINCIPLES.md`: **script everything that can be scripted; prose only where a judgment call
  genuinely needs it.** Round 2's own 50 passes, and round 3's first 20, predate this fix.

## Knowledge mutation system (2026-08-01)

Implemented: Step 5 of `/enact` now records hearsay with mutations applied. Each character's
understanding is filtered through their criterion/trusts/distrusts/wasted_life. Original unmutated
versions are not recorded (unless they had separate hearsay entries). The lineage_coin mechanism
already decides traceable vs untraceable origins.

- [ ] **Retroactive mutation.** All existing hearsay entries (Nawom/Morkulo, Feria scenes, Khaoe/Farlis entries) should be reviewed and updated to reflect mutations. Priority: entries that spawned into major characters' education (Bardaglis's song from Khaoe/Farlis; Farlis/Aureobalo bar scene). Lower priority: one-off encounters (Gok/Nerkeli).
- [ ] **Material mutation.** When characters cite objective material (eras, locations), record how they reframed it. Current scenes may have missed this — not retroactive work needed, but forward pattern to apply from now on.
- [ ] **Auroboro III & Farlis hearsay:** Entry rewritten with mutations applied (2026-08-01). Both perspectives recorded; claims reflect each character's interpretation, not objective fact.

## Gesture animation system (resource pack)

Built 2026-07-25/26: a custom EMF/Iris `player.jem`/`player_slim.jem` override giving Taterzens NPCs
(and real players) 7 animated gestures — wave, point, bow, shrug, palms-up (originally prototyped as
"cross-arms", renamed once it visually read as the former instead), scratch-head, and laugh — each
triggered by an invisible `minecraft:stick{CustomModelData:<101-107>}` in the main hand, smoothly eased
via a self-referencing `var.*` low-pass filter pattern (proven more reliable than self-referencing the
bone key directly, which jittered). Coexists with the already-installed Fresh Animations + FA+Player by
forking only `player.jem`/`player_slim.jem` (the two files that needed the gesture hook) rather than the
whole pack — every other file (movement/idle/equipment math, textures, cape) still falls through to
FA+Player underneath, since Minecraft resolves each asset path independently across the active pack
stack. Full technical writeup lives in this conversation's history (2026-07-25/26 session), not yet
copied into README/registry docs.

Wired into Döran's three dialogs (`doran_plaza_orientation`, `doran_four_castles`,
`doran_eras_of_culture`) via 7 new `functions/npcs/_shared/gesture_<name>.mcfunction` files (already
git-tracked, datapack-side) + a shared `gesture_clear.mcfunction`, following the same
tag+`schedule ... replace` pattern as `nod_up_down.mcfunction`. Each wired dialogue state's action
*replaces* its `nod_up_down` call rather than adding to it, so gesture and nod are mutually exclusive by
construction — every other line keeps its ordinary nod untouched.

- [x] **Multi-NPC gesture/nod scheduling collision** (found 2026-07-25 building the jump gesture,
      fixed same day): `schedule function <id> <ticks>t replace` is a single global timer *per
      function ID*, not per-entity — every gesture shared one `gesture_clear` timer and every nod
      direction shared one `_2/_3/_4` continuation-beat timer, so a second NPC gesturing/nodding a few
      ticks after a first one would silently overwrite the first one's pending timing. Replaced with a
      per-entity scoreboard countdown for both systems:
        - `luminacion.gest_timer` / `luminacion.nod_timer` (new `dummy` objectives, `load.mcfunction`).
        - Every `gesture_<name>.mcfunction` now does `scoreboard players set @s luminacion.gest_timer
          <duration>` instead of scheduling `gesture_clear`. `tick.mcfunction` calls the new
          `gesture_tick.mcfunction` every tick, which decrements the score for every
          `@e[tag=luminacion.gesture_active]` and runs `gesture_clear.mcfunction` (now simplified to
          act on `@s` alone) only for entities whose score has reached 0.
        - `nod_up_down.mcfunction`/`nod_left_right.mcfunction` now set `luminacion.nod_timer` to `9`
          instead of scheduling `_2`. The new `nod_tick.mcfunction` (also called from `tick.mcfunction`)
          decrements it per-entity and fires each beat at the score matching 3/6/9 ticks elapsed,
          landing beat 4 in the new `nod_up_down_clear.mcfunction`/`nod_left_right_clear.mcfunction`.
          The old `nod_up_down_2/_3/_4.mcfunction` and `nod_left_right_2/_3/_4.mcfunction` files are
          deleted — superseded by this tick+score design, one shared `nod_timer` objective for both
          directions since an NPC is never tagged mid-nod in both at once.
      Each NPC's hold/beat timing is now fully independent of every other NPC's, regardless of how
      many NPCs gesture/nod concurrently or how staggered their start times are. Docstrings across every
      touched `gesture_*`/`nod_*.mcfunction`, the README (Layer 2 gesture dispatch, the "to call a
      gesture" walkthrough, the Jump reference-table row), and `.claude/skills/spawn/SKILL.md` (which
      named the now-deleted nod continuation files) were updated to match.
- [ ] **Not yet version-controlled**: the resource pack itself (`pack.mcmeta` +
      `assets/minecraft/emf/cem/player.jem`/`player_slim.jem` + the invisible item model/texture under
      `assets/minecraft/models/item/stick.json` + `assets/luminacion/...`) still lives only at
      `resourcepacks/luminacion-gesture-test/` in the PrismLauncher instance — outside this git repo,
      named as a throwaway test folder. User wants it moved into the production/version-controlled
      folder; deferred to decide **where** exactly (2026-07-26 session ran out of day before deciding).
      Two options were on the table, both with real tradeoffs:
        1. New standalone git repo initialized directly at `resourcepacks/<name>/` — mirrors exactly how
           *this* datapack repo already works (the repo IS the live folder Minecraft loads from, no
           symlink/copy step ever needed) — but is a second repo to manage.
        2. Move it into *this* repo as a subfolder (e.g. `assets/` alongside `data/`, matching the
           Localization section's existing plan below — see `scripts/build_resourcepack.py`), then
           symlink `resourcepacks/<name>/` to it — one repo, but needs a working Windows symlink
           (Developer Mode or admin rights) and silently breaks if that link is ever lost/not recreated
           on a new machine.
      **Relevant precedent already on record** (see Localization section immediately below): this
      project already planned for `assets/luminacion/lang/en_us.json` to live alongside `data/` in this
      same repo, plus a future `scripts/build_resourcepack.py` that zips `assets/` + its own
      `pack.mcmeta` into a resource pack — i.e. the project's own established intended pattern already
      leans toward option 2 (single repo). Worth weighing against symlink reliability before deciding.
      Also applies here regardless of which option is picked: the Localization section's "need a second
      `pack.mcmeta` for the resource pack" point is the same constraint the gesture pack already has
      (it already ships its own separate `pack.mcmeta`, currently sitting outside this repo).
- [ ] Once the location is settled: move/copy the pack's contents there, rename away from
      `-gesture-test`/`-test` naming now that it's graduating from prototype, and update this repo's own
      `resourcepacks/` reference (the live folder Minecraft actually loads) to match — either by having
      the new repo live there directly (option 1) or via the symlink (option 2).
- [ ] Still main-hand only (off-hand path never built — would need the trickier
      `Inventory`/slot-`-106` NBT path discovered for real players, unconfirmed for Taterzens).
- [x] **Elbow joint (separate forearm bone) — working, landed 2026-07-25.** `right_arm`/`left_arm` are
      each split at the vertical midpoint into a shortened shoulder segment and a nested `submodels`
      child bone (`right_forearm`/`left_forearm`), pivoted at the elbow. First attempt (same day) used
      absolute-frame-style `translate`/`coordinates` numbers for the nested bone and got the rotation
      approach backwards, causing it to render fully detached — see the README "Elbow joint" writeup for
      what was actually wrong and how it was diagnosed (a real Fresh Animations `wolf.jem` — the same
      author this rig already credits — was pulled from GitHub to reverse-engineer the correct nested
      `translate`/`coordinates` scale). Position tracking through the parent's rotation turned out to be
      automatic; only the pivot's local-frame numbers needed calibrating, which took extensive in-game
      trial and error (see README for final values). A small elbow seam remains and is considered
      acceptable — the blocky character style camouflages it. `cross_arms` (CustomModelData 111) is the
      first gesture using it, bending `right_forearm.rx`/`left_forearm.rx` by `torad(-90)`. Not yet wired
      into any other gesture (scratch-head/palms-up could plausibly use it too, unexplored).
- [ ] Forearm sleeve overlay (`right_forearm_sleeve`/`left_forearm_sleeve`) isn't positionally
      calibrated to match the tuned forearm bone — nesting it under `right_sleeve`/`left_sleeve` the
      same way `right_forearm` nests under `right_arm` was tried and reverted, since that bone only
      inherits the shoulder's rotation (not the forearm's own local elbow bend), breaking `cross_arms`'s
      bend for the sleeve layer specifically. Needs either its own copy of `var.gest_rforearmrx` or
      nesting under `right_forearm` instead of `right_sleeve` (untried). See README "Elbow joint".
- [x] Packaged the manual gesture-selection pass as its own skill, `.claude/skills/bake_dialog/SKILL.md`
      (2026-07-25) — callable standalone on any dialog file, or automatically as `/enact`'s new Step 8.
- [x] Ran `bake_dialog` over every remaining non-template dialog (2026-07-25): `nerkeli_hangar_talk`,
      `nuvilo_scholar_at_the_feria`, `gondarfolas_darnis_and_bracco`, all five `khaoe_*` dialogs,
      `sonoros_lost_traveler`, `nawom_morkulo_first_meeting`. Every dialog in the pack now has at
      least one gesture beyond the uniform default nod. The three `khaoe_farlis_*` states that were
      missing an `action` entirely (see the entry above this one, and the "always a nod" question
      that surfaced it) got filled in as part of this same pass rather than left as a separate gap.
      One pre-existing `nod_left_right` in `khaoe_farlis_el_castillo_que_fue.json` (state `f1`) was
      swapped to `gesture_laugh` — the line ("me da risa") was amusement, not disagreement, and the
      user confirmed the swap before it was made. Any *new* dialog from `/enact` still needs this
      pass — it isn't a one-time fix, `/enact` Step 8 runs it going forward.
- [ ] **`gesture_demo_step.mcfunction`'s self-reschedule doesn't work — cause unconfirmed.** Built
      2026-07-25 as a QA tool (`data/luminacion/functions/admin/gesture_demo_all.mcfunction` +
      `gesture_demo_step.mcfunction`) to auto-play every gesture in sequence on the nearest Taterzen,
      3s apart, via each step scheduling the next with `schedule function
      luminacion:admin/gesture_demo_step 60t replace`. In-game testing (real-time watching, confirmed
      not a window-focus-pause artifact) showed only the *first* gesture ever plays automatically —
      diagnosed via `logs/latest.log` and manual isolation: both the per-index `execute if score ...`
      gesture-selection branches AND the `scoreboard players add` counter increment work correctly
      (calling `function luminacion:admin/gesture_demo_step` by hand repeatedly plays the correct next
      gesture each time), but even `/schedule function luminacion:admin/gesture_demo_step 60t replace`
      run standalone in chat — no `execute if score` wrapper at all — silently does nothing. So the bug
      is specifically in `schedule function` not re-firing this function, not in anything upstream of
      it; root cause (self-referential scheduling from within the function it's scheduling? some
      mod interaction — this is a heavily modded Fabric/Forge pack? a `schedule`-specific quirk in this
      environment?) wasn't pinned down before the user chose to stop debugging and use the tool as a
      manual step-by-step trigger instead (`function luminacion:admin/gesture_demo_step`, called
      repeatedly). The two files' own comments still describe the *intended* auto-advancing behavior,
      not this known-broken state — worth fixing those comments if picked back up.

## Localization (per-player dialog language)

- [ ] Add a top-level `assets/luminacion/lang/en_us.json` (and other language files as they're
      written) alongside `data/` in this same repo. The datapack loader only ever reads `data/`, so
      `assets/` living here during dev is inert to it — no folder split needed for authoring.
- [ ] Write `scripts/extract_dialogue_lang.py`: sweeps `data/luminacion/blabber/dialogues/*.json`
      (templates excluded), derives a deterministic key per line as
      `luminacion.dialogue.<file_stem>.<state_id>` (and `.choice.<n>` for choices), writes/updates
      the key → text entry in `assets/luminacion/lang/en_us.json`, and rewrites the dialogue file's
      `text` field to `{"translate": key}`. Mechanical and re-runnable — authoring stays plain literal
      text (no change to `/enact` Step 4/5 or to how `hearsay.md` gets written), and this only runs
      as a deliberate "finalize for localization" pass over already-written dialogues.
- [ ] Document, in `hearsay.md`'s own preamble and README §8, that once a dialogue has been through
      extraction, `assets/luminacion/lang/en_us.json` (not the dialogue file) is the resolved source
      of truth for what a line actually says — the same role `_lore/material/` plays for `context.md`.
      Only matters for *revisiting* an already-extracted dialogue (e.g. a later `/enact` run
      referencing an existing NPC's old lines); doesn't affect authoring a new dialogue, since the
      English text is still written and read literally before extraction ever runs.
- [ ] Write `scripts/build_resourcepack.py`: zips `assets/` + a resource-pack `pack.mcmeta` into
      `saves/Miniatures/resources.zip` for local per-world testing (Minecraft's per-world resource
      pack mechanism), and separately emits `dist/Luminacion/` (datapack: `data/` + its `pack.mcmeta`)
      and `dist/Luminacion-resourcepack.zip` (resource pack) for release — built only from `data/` and
      `assets/`, leaving `_lore/`, `_npcs/`, `scripts/`, and the docs out of both.
- [ ] Need a second `pack.mcmeta` for the resource pack (own `pack_format`) — the datapack's existing
      root `pack.mcmeta` can't serve both.
- [ ] Convert existing dialogue files to translation keys via the extractor once it exists (currently
      all six non-template dialogues use literal `text`).

## Lore integration skill (`/integrate`)

- [x] Built 2026-07-25: `.claude/skills/integrate/SKILL.md`, documented in README §0 (Layer 1).
      Three passes — analyse new `_lore/material/` into `context.md`/`encodings.json`/`unknowns.md`;
      audit `data/luminacion/blabber/dialogues/` for missing `hearsay.entries` coverage; check for
      drift between what's referenced elsewhere (registries, sampled knowledge) and what's actually
      recorded in `encodings.json`.
- [ ] Not yet run end-to-end against real material or a real drift case — worth a first live pass
      next time material is added or a periodic audit is due, to confirm the three passes hold up in
      practice rather than just on paper.
- [x] **Stale reference fixed, 2026-08-07.** Pass 2 cited "README §8 Step 5" as the shape a hearsay
      entry should match — that step never existed in README; §8 only ever documented Steps 1–4, and
      the hearsay-recording step lives solely in `/enact`'s own Step 5 (added after the `/enact`/
      `/embody` split, never backported into README's numbering). Fixed to point at `/enact` Step 5
      directly. Same pass, every README.md reference was removed from `integrate/SKILL.md` (and every
      other skill — see the dedicated section near the end of this file) — skills are agent-facing and
      now self-contained; README stays the human-facing doc. Doesn't touch the still-open item above,
      or the schema-evolution issue in the next section — neither was in scope.
- [x] **Two-layer `sources` provenance, built 2026-08-07.** New `scripts/lore/build_source_index.py`
      (mechanical, no model judgment): migrates every `locations`/`concepts`/
      `characters.in_world_or_legendary`/`characters.real_world_authors_and_players` entry's `sources`
      from flat strings to `{"category": "material"/"hearsay"/"tale", "document": "..."}`, and links every
      `hearsay.entries[].claims[].about`/`tales.entries[].touches` reference that resolves — exactly, or
      via `difflib` fuzzy match (ratio ≥ 0.77, same-category comparisons only) — into the target node's
      `sources` list. A fuzzy link auto-groups (adds the new spelling to `names[]` so it resolves
      directly next time) but is never treated as settled: it also appends an unconfirmed `CONFLICT-NN`
      ("possible same-entity spelling, auto-grouped"), same as every other conflict — `user_resolution`
      stays the user's call. Wired into Pass 3 step 2 above. Applied once to the live `encodings.json`:
      164 sources migrated, 70 new hearsay/tale links, one real spelling-drift bug caught
      (`balahm`→`balham`, `CONFLICT-18`), 7 references honestly left unresolved rather than guessed
      (one missing `locations` entry — `jardin_de_los_parajes` — and four `concept:` references to
      concepts that don't exist yet: `hotel_kholi`, `preservation`, `memory`, `transformation`). Script
      is idempotent (verified via a second dry run). **Does not touch or resolve any part of the
      "Schema evolution" CRITICAL section below** — that's about the top-level category schema itself
      being able to grow; this works entirely inside the four categories that already exist.

## Schema evolution in `encodings.json` and criterion epistemology (CRITICAL, 2026-08-05)

**IMPORTANT ARCHITECTURAL ISSUE:** The current `/integrate` skill and sampling system assume a fixed
schema (`time_systems`, `locations`, `routes`, `characters`, `concepts`, `conflicts`, `hearsay`,
`tales`) that was established on first material analysis. However, the original design intent was for
the lore structure itself to *emerge organically* from material analysis — categories should not be
frozen in place.

This matters because:

1. **Lore extensibility:** If new material introduces genuinely novel organizational structure (e.g.,
   "alien cultures" that don't fit cleanly into existing categories), the current `/integrate` skill
   has no mechanism to recognize this and propose new categories — it just force-fits into the old
   schema.

2. **Criterion epistemology:** Categories in `encodings.json` drive the sampling categories
   (`era_libro`, `era_ensayo`, `hearsay`, etc.) used by `scripts/lore/sample_lore_knowledge.py`, which in
   turn determine the epistemology anchors (`criterion.trusts`/`distrusts`) that characters derive at
   creation. If the schema evolves, the sampling categories would need to evolve alongside it,
   automatically giving new criteria new epistemologies as new source types emerge.

3. **Current limitation:** The sampling script hardcodes paths into `encodings.json` to extract
   categories (e.g., line 83: `for e in data["time_systems"]["ensayo_i_eras"]`). This is rigid —
   it can't discover categories dynamically.

**What needs to change:**

- [x] **`/integrate` Pass 1 detects novel structure, built 2026-08-07.** New Pass 1 step 2: before
      folding anything in, check whether the material's own structure fits an existing category; if
      not, ask (AskUserQuestion) whether to create a new one, and never continue past that point on the
      skill's own judgment. On approval, also propose an `epistemology_group` for `/character` Step
      4d's trusts/distrusts table (join an existing group, or draft a new row) — confirmed by the user,
      never inferred from category size (Step 4d already documents why that approach failed once).
- [x] **`encodings.json` schema can evolve, built 2026-08-07.** New self-describing `_categories` block
      (added by `scripts/lore/add_categories_schema.py`, a one-time migration) lists every category's
      sampling shape: `path` into the JSON, `shape` (`"list"` for the common flat-list-of-entities case,
      plus two special-cased existing shapes — `"grouped_list"` for `characters.named_inhabitants`,
      `"claims"` for `hearsay.entries`), and `epistemology_group`. A new category registers here
      alongside its own top-level data key — no code change needed if it follows the `"list"` shape.
- [x] **Sampling script discovers categories dynamically, built 2026-08-07.** `sample_lore_knowledge.py`'s
      `flatten_pool()` now iterates `encodings.json`'s own `_categories` block and dispatches by
      `shape` via a small `SHAPE_HANDLERS` registry, instead of 15 hardcoded per-path `for` loops.
      Verified byte-for-byte against a pre-migration baseline: identical 367-item pool, same
      `(category, id)` pairs; the only diffs were internal `text` field formatting for list-valued
      fields (`names`, `places`) — from a stringified Python list to a clean joined string, a disclosed
      cleanup, not a behavior change (`text` is never shown to a user, only substring-matched for
      `--mode skewed`).
      **Honest residual limit, not solved and not claimed to be:** this covers the common case (a flat
      list of `{id, ...}` dicts), which is what every category added via material analysis has looked
      like so far. A genuinely novel structural shape (another nested grouping, another claims-like
      pattern) still needs one new function added to `SHAPE_HANDLERS` by hand — the script refuses to
      sample a category whose shape it doesn't recognize rather than silently skipping it, but "zero
      code for any conceivable shape" was never actually achievable without forcing every future
      category into one canonical shape, which would cut against "let structure emerge organically."

This is a prerequisite for the lore system to grow without architectural friction as new materials
accumulate over time.

- [x] **Cold-start bootstrap, built 2026-08-07.** `scripts/lore/bootstrap_lore.py` creates whichever
      of five structural files don't exist yet (`_lore/encodings.json`, `_lore/material/_context.md`,
      `_lore/unknowns.md`, `_lore/characters/hearsay.md`, `_lore/tales/_index.md` +
      `_lore/tales/_authors.md`), each with an empty/generic header and no content pre-filled in —
      `/integrate` Pass 1 proposes every content category the first time real material calls for it,
      the same way the original schema was built by hand before any of this tooling existed.
      `/integrate`, `/enact`, and `/tell` each got a one-line cold-start pointer at this script.
      Surfaced and fixed a real bug while testing it: `build_source_index.py` hardcoded its own
      4-category list via direct dict access and crashed (`KeyError`) on a fresh/partial project
      instead of no-op'ing — fixed by deriving the list from a new `has_sources` flag on each
      `_categories` entry instead. Verified: bootstrap in an isolated scratch dir (creates correctly,
      idempotent), `sample_lore_knowledge.py` and `build_source_index.py` both run cleanly against the
      fresh file with zero crashes, and both re-verified byte-identical against the live repo
      (zero behavior change there).

## `/embody` can't run cold — no scene transcript is ever persisted (landed 2026-08-07)

**Problem:** `/embody`'s own SKILL.md says it "reads the transcript still sitting in context, not a
file" — confirmed by reading it directly, not assumed. Once an `/enact`-only conversation ends, the
actual turn-by-turn dialogue is gone. What survives on disk (`hearsay.entries[].claims`,
`knowledge.experience`) is not a substitute: both are independently-authored, already-mutated
*summaries* of the same scene from two different angles (the world's sampling pool vs. a character's
own bounded memory) — genuinely different consumers, not redundant with each other, but neither one
is, or was ever meant to be, a verbatim record. Step 5 says so outright: "the original unmutated
version is not recorded." This gap is already visible in this file — see the Feria del Milenio bar
scenes entry above ("Transcripts live in this conversation's history until converted").

**Correction from the first pass at this proposal:** scenes must NOT live under `_lore/` — that
directory is for lore (analysis, sampleable knowledge, the character record), and a raw transcript is
none of those; it only exists to feed `/embody`, which is purely Minecraft-facing. It belongs under
`_npcs/`, alongside `templates/`, `npcs/`, `dialogs/`, `actions/`.

**Boundary check (verified, not assumed):** `/enact`'s own frontmatter says it "touches nothing under
`data/luminacion/` or `_npcs/npcs/registry.json`" — specific to those two, not a blanket ban on
anything under `_npcs/`. A new `_npcs/scenes/` staging directory doesn't violate that. README §0's
higher-level architecture blurb is worded more broadly, though ("`/character` and `/enact` only ever
touch `_lore/` and know nothing of Minecraft") — that line will need a one-line carve-out once this is
built, or the boundary language should be tightened to match what the frontmatters actually say.
Bonus effect of moving it out of `_lore/`: the "must wall this off from `sample_lore_knowledge.py`'s
pool" problem (same isolation `_lore/facts/` and `_authors.md` files need) disappears for free — that
script only ever reads `encodings.json`, so a file under `_npcs/` was never at risk of being sampled
to begin with.

**Shipped shape** (built 2026-08-07):

- [x] New `_npcs/scenes/<scene_id>.md` — one file per enacted scene (same id the hearsay entry gets, so
      the two cross-reference trivially — `/enact` Step 4 now passes this id explicitly into
      `record_hearsay.py` rather than letting it auto-generate one, closing that loop by construction),
      holding the raw turn-by-turn transcript verbatim (dialogue only, no action cues — same rule
      `/enact` already followed), plus participants/format/location metadata. Shape documented in
      `_npcs/scenes/_template.md`.
- [x] New `/enact` Step 4, immediately after the scene is played and *before* Step 5's mutation ever
      throws the original away — saves the transcript first. Same "record immediately, don't batch"
      discipline already in place for hearsay/experience, just started one step earlier. Slots into the
      numbering gap left at "Step 4" when dialog-writing moved out to `/embody`.
- [x] `/embody` Step 1 now reads `_npcs/scenes/<scene_id>.md` instead of "the transcript still sitting
      in context" — the actual unlock. `/embody` is now uniformly file-driven, cold or hot, same
      conversation or months later; if invoked cold without a scene already identified, it asks the user
      which one (character name or scene id).
- [x] README §0 got the carve-out this section flagged as needed: the `/character`/`/enact`
      lore-vs-Minecraft boundary line, plus the `/enact`/`/embody` bullets and the §1 folder tree, now
      all describe `_npcs/scenes/` accurately instead of the old "never touches `_npcs/`" claim.
- [ ] **Limitation, can't be fixed retroactively:** any `/enact`-only scene that predates this change
      still has no recoverable transcript — those would need to be re-enacted from scratch to ever be
      embodied. Applies to every dialog-linked hearsay entry already on record as of 2026-08-07 (see the
      `hearsay.entries` list) and to the two not-yet-embodied `#1`-suffixed entries
      (`gok_milkucha_alcove#1`, `farlis_gok_alcove#1`).
- [x] **Open question resolved (user's call, 2026-08-07): keep permanently.** `/embody` never
      deletes/archives a scene file after conversion — cheap to keep, and it's the only recoverable
      source if a dialogue ever needs re-converting after an editing mistake.

## Conflict-resolution skill (landed 2026-08-07)

No skill existed to help work through `encodings.json`'s `conflicts` array. As of 2026-08-05, 14 of
17 entries (all but `CONFLICT-01`/`03`/`05`) had no `user_resolution` — every disagreement `/tell`
and `/integrate` have ever logged is append-only by design: neither is allowed to set
`user_resolution` themselves, that's the one thing only the user can do (see each skill's own docs).
Previously the only way to resolve one was to notice it while reading the file directly.

- [x] **`/resolve`** (`.claude/skills/resolve/SKILL.md`) surfaces one open item at a time — topic, full
      `detail`, and every place elsewhere in the record that mentions it (a plain substring scan of
      every string field in `encodings.json` plus every matching line in `_lore/unknowns.md`, since no
      structured `conflict_ref` field actually exists — the real convention already in use is a
      free-text `"see CONFLICT-NN"` note, e.g. `isla_de_la_amistad`'s `notes` field) — and, only on the
      user's own explicit call, writes `user_resolution` (dated, "per user, <date>", matching the
      existing convention exactly). Never suggests a resolution, never infers one from
      majority-source-agreement or recency, never resolves more than the one item the user is actively
      looking at. Skipping is a first-class, no-op-safe choice — Step 3 stops cleanly and changes
      nothing if the user isn't ready.
- [x] **Two mechanical scripts, same "mechanize the lookup, keep judgement in prose" pattern as
      `check_anchor_reference.py`.** `scripts/lore/resolve_conflict.py` (`--list` / `<id>` /
      `<id> --set-resolution "..."` [`--force`]) — refuses to silently overwrite an existing
      `user_resolution`. `scripts/lore/list_open_unknowns.py` — lists every `_lore/unknowns.md` heading
      whose own title doesn't say "Resolved"/"Correction" (judged per-heading, not inherited from a
      parent section, so the "Follow-up flag" sub-question nested under the resolved 2026-07-24 section
      correctly still shows as open). Both tested against real data (read-only) and, for the write path,
      a scratch copy — refusal-without-`--force`, success-with-`--force`, and unknown-id refusal all
      confirmed before touching the real file.
- [x] **Real bug found and fixed while testing, not part of the original ask:** this machine's Python
      defaults stdout to `cp1252`, which silently mangled every diacritic this pack's lore is full of
      (Milkäan, Iläria, Aerörea...) once piped through a shell expecting UTF-8 — confirmed by round-
      tripping a redirected script's output back through a UTF-8 decode, which raised
      `UnicodeDecodeError` on byte `0xf6`. Both new scripts now call `sys.stdout.reconfigure(encoding=
      "utf-8")` up front. Pre-existing scripts that print accented text (e.g. `check_anchor_reference.py`
      printing a claim's `about` field) likely have the same latent bug — not fixed here, out of scope
      for this pass, but worth the same one-line fix next time one of them is touched.
- [x] **`_lore/unknowns.md` handled too**, per the open question this section originally raised — same
      "only the user decides, never inferred" rule, via `list_open_unknowns.py` plus `/resolve` Step 4's
      prose procedure (append to a dated `## Resolved by the user (<date>)` section matching the file's
      own established convention, plus a one-line pointer left in the original section — never deleted,
      the underlying documentary content stays on record). Unlike conflicts, there's no script that
      writes the resolution here: the file is free-form markdown, and matching its existing prose style
      is a judgement call each time, not a mechanical transform.

## Random character location selection in `/enact` (pinned 2026-08-01)

**Field note (2026-08-28):** this section originally said `city`; the character schema has since split
that into `origin` (fixed birthplace) and `location` (current whereabouts). Everything below now
refers to `location` — that's the field this mechanism was always actually describing (see
`/character` SKILL.md and `/enact` SKILL.md's Step 1, which already updates it to "wherever the scene
actually put" the character).

When setting a scene location in `/enact` Step 1 (or any step that needs to pick a place), if the character's `location` field lists multiple locations or is blank, use weighted location selection rather than the user specifying it outright or picking at random:

1. **Primary locus:** the character's registered `location` (split on commas if multiple are listed) — each listed location gets equal weight within this group.
2. **Secondary locus:** locations where people the character has shared scenes with are based (drawn from `hearsay.entries` — count unique co-participants and look up their `location` fields) — these are offered at lower weight than primary, and only if the user hasn't overridden the location in the scene prompt.
3. **Rationale:** makes the world feel organically connected — characters naturally gravitate toward places they know or toward people they've already met, rather than appearing randomly across the map. Also prevents unnatural isolation: a character who's been to a place twice already and knows someone there has more reason to return than to go somewhere fresh.
4. **Implementation:** proposed as a heuristic for the human running `/enact` rather than a code-level feature. Decision should come up naturally when the user specifies only characters, not a location (e.g., `Farlis and Gok at his station in the Espiral` over-specifies and doesn't need this logic; `Gok runs into Nuvilo` does).
5. **Open:** should the weight favor the character's *most-visited* location over others in their list? And should repeated co-participants (met in multiple scenes) carry more weight than meeting someone once? Current leaning: keep it simple and equal, let narrative preference override via explicit scene prompts.
6. **Open, added 2026-08-28 — the `transit` context.** A routine tagged `context: transit` names a
   route in its own `location` field (`"Tyrnea <-> Görff"`), not a single point — see `_lore/contexts.json`'s
   own note on it. None of the weighting logic above actually resolves that yet: picking a scene
   location for a character whose primary/only routine is `transit` should mean choosing one end of
   the route (weighted by whether the scene reads as a departure or an arrival), not just handing back
   the raw `"A <-> B"` string as if it were a place name. Not implemented — flagged the moment the
   context was created (Medusan, first character to use it), not yet needed in practice.

## General

- [ ] Once one of the above ships, consider adding it as a second worked example in README §8
      (currently only references the Sonoros dialog).
- [ ] Trading with NPCs: vanilla's trade UI only opens via right-click on an actual
      `villager`/`wandering_trader` entity (custom `Offers` NBT), which doesn't integrate with
      Taterzens' `npc edit commands` action pipeline — would need a paired, disguised villager
      entity kept in sync with the Taterzens NPC. Alternative: a small Fabric mod exposing a command
      (e.g. `luminacion:trade open <trade_table> <player>`) that opens `MerchantScreenHandler`
      directly against a custom `Merchant` implementation, no entity required — see
      [VillagerConfig](https://modrinth.com/mod/villagerconfig)'s `/vc test villager` for a working
      precedent of this pattern. Decide which approach before any NPC needs trading.

## Criterion model — gaps found by using it (2026-07-31)

Surfaced by running the three scenes above; all three are places `/character` Step 6 is
underspecified, not bugs in the data.

- [ ] **The "hardening" rule only fits the *reject* move.** Step 6 says surviving a refutation hardens
      `distrusts` against that kind of source. That's right when a character survives by *dismissing*
      the claim — but when they survive by *accepting and reinterpreting*, hardening against the
      source that just corrected them is backwards. Farlis accepted Khaoe's rebuttal via Aureobalo;
      hardening him against named firsthand testimony would have been wrong, so his trust fields were
      left untouched. Make the rule conditional on the move.
- [ ] **Reaffirmation has no defined outcome.** The gate matched three times this run where the claim
      *confirmed* rather than challenged the anchor (Iläria asked which chronicle is right and
      declined to say; Khaoe's own castle line came up in her presence). The three moves are all
      responses to a refutation, so these were recorded as "no change," which feels right but isn't
      written down anywhere. Decide whether a reaffirmation ever tempers, and say so.
- [x] **No guidance on how often tempering should fire — resolved.** `/character` Step 6 now gates on
      *reference, not intensity*: "a claim... qualifies as a challenge only if it references the
      anchor — same case, same person, same event... Anything else, however dramatic, is not a
      challenge to *this* criterion; it's news." That's the "what does not count" sentence this item
      asked for, phrased as a reference test rather than a frequency rule.

## Criterion / will-to-live system (landed 2026-07-31)

Shipped this round: `_lore/facts/` (the fifth, never-sampled source of truth),
`scripts/lore/roll_lifespan.py`, `criterion`/`life` on the registry `_template`, `/character` Steps 4–7
(derivation, lifespan, and the reference model for how a criterion changes), and `/enact`'s facts
loading, in-scene modulation, and Step 5b shock/drift resolution. Still open:

- [ ] **`/temperament` skill.** The disposition that governs move 2 vs. move 3 when a character
      accepts a refuting claim — rebuild the meaning, or let the criterion go. Deferred by the user
      on 2026-07-31; until it exists, `/character` Step 6 says to decide on provenance, proximity,
      and susceptibility alone and bias toward reinterpretation. Should be set at creation from the
      backstory and drift slowly with `knowledge.experience` (the working split: knowledge changes
      your criterion, experience changes your temperament).
- [ ] **Inherited criteria (place/trade fallback).** `/character` Step 4e currently leaves
      `criterion` blank with `"derivation": "uncollided"` when nothing in the sample touches the
      backstory, origin, or location, because the fallback implies giving every place (and trade) its
      own ambient criterion. Pinned by the user on 2026-07-31. Worth building — it's what produces shared
      culture rather than a hundred idiosyncratic philosophies, and it's the common case for
      ordinary people, who inherit their town's answer rather than authoring one.
- [ ] **No `/fact` skill.** Adding a fact means hand-editing `_lore/facts/facts.json`, a new `.md`,
      and the `_index.md` table. Fine for now given how rarely facts should be added, but the other
      sources of truth all have skills (`/integrate` for material/analysis, `/tell` for tale).
- [x] **Backfilled 2026-07-31:** Bardaglis, Farlis, Khaoe, Khaasan, Aureobalo, Döran, and Iläria all
      have a derived criterion (with anchor, `trusts`/`distrusts`, and a seeded `cost_ledger` drawn
      from what their recorded history already cost them) and a rolled lifespan. `life.lived` was
      backfilled from the hearsay record — one `hearsay.entries[]` record is one scene — per the new
      rule in `/character` Step 5.
- [ ] **Still without a criterion or lifespan:** Gondarfolas, Nuvilo, Nerkeli, Nawom, and Morkulo
      (drawn samples, so derivable now), plus the ~50 entries whose `knowledge.education.percent` is
      still `null` — those can't be derived at all until they have both a backstory and a sample.
      Let it happen lazily as each next comes up in an `/enact` run, or batch them like the seven
      above.
- [ ] **Lifespan range set to 30–60** (author decision, 2026-07-31, replacing the initial 4–14) and
      written into `scripts/lore/roll_lifespan.py`'s defaults. Nobody is anywhere near their span yet —
      the most-lived character, Khaoe, is 7 scenes into 51 — so the endgame path in `/enact` Step 5b
      is written but has never actually fired. Worth testing deliberately with a throwaway character
      on `--min 2 --max 4` rather than waiting for it.
- [x] **Death notification, landed 2026-08-01.** `scripts/lore/notify_death.py` computes a dying
      character's "circle" (scene co-participants + everyone named in their own backstory) and
      mechanically samples 30% of it (min 1) to notify immediately via a forced
      `knowledge.experience` entry; it also flags which notified characters have a `criterion.anchor`
      referencing the deceased, so `/enact` Step 5b point 6 can resolve that as a shock through the
      existing reject/reinterpret/break machinery. Everyone else only learns later, the ordinary way
      — the death is recorded as a `_lore/tales/` entry (same shape `/tell` produces,
      `told_by: null` unless a cause was established in the closing scene) and re-enters the
      normal sampling pool. `life.deceased` (plain, non-secret bool) added to the registry `life`
      object and to every already-touched character (`false`); Step 1 now refuses to re-enact anyone
      with `deceased: true`. Tested against real data: `notify_death.py khaoe`/`bardaglis` correctly
      compute their circles, and the shock flag was confirmed to fire (seed 9 on `khaoe` selects
      Khaasan, whose anchor is `experience: khaoe_khaasan_bar_salthos_cruzados` — Khaoe is a
      participant in that scene, so it flags).
- [ ] **Still open: what a dead character's *NPC* does in-game.** Nothing yet stops a *spawned*
      Taterzen from standing in the world with a working right-click dialog after `life.deceased`
      flips true — this is the Minecraft-facing half the notification mechanism deliberately doesn't
      touch. Decide: despawn, stay as a silent fixture, or get replaced by someone retelling them.
- [x] **Exercised on real deaths since, across multiple `/simulate` runs — resolved.** `LAB_REPORT.md`
      Run 1 recorded 4 natural-lifespan deaths (Auroboro III, Iläria, Khaoe, Nerkeli); a later run logs
      `record_death.py` running cleanly end to end (tale written, circle computed, notification fired)
      and "four of the original six now deceased; three genuine criterion shocks resolved, all as
      reinterpret" — the full procedure (tale-record write, circle notification, real shock
      resolution) has fired repeatedly. None of this reached `provenance-standalone`'s own
      `_lore/characters/*.json` — every death happened inside a disposable `/simulate` worktree, which
      by design never merges back (see README) — so no character here currently has `life.deceased:
      true`, but the mechanism itself is proven, not merely tested hypothetically.
- [x] **`python` on PATH fixed (2026-08-06) — resolved.** Bare `python`/`pip` now resolve to a real
      3.14 install (confirmed: `python --version` and `py -3 --version` both report 3.14.6), not the
      Microsoft Store stub. Skills still call `py -3` by convention rather than bare `python` — a style
      choice now, not a workaround for a broken PATH. The dead `.venv/` Codespace artifact wasn't
      re-checked here.

## Skills decoupled from README + shared house philosophy + `/simulate` scripting (2026-08-07)

Skills are agent-facing; README is human-facing. Every skill previously cited README.md for rules or
procedure it either already restated (redundant) or, in one case, misquoted (see the `/integrate`
entry above). Cleaned up in one pass:

- [x] **Every README.md reference removed from every skill** (`enact`, `embody`, `spawn`, `package`,
      `integrate`, `tell`; `character`/`simulate`/`enact-embody` had none to begin with). Skills no
      longer read or cite README at all. The one line left (`package/SKILL.md` listing `README.md` as
      a filename excluded from the release zip) isn't a documentation dependency, so it stayed.
- [x] **`.claude/PRINCIPLES.md` created** — the "nothing gets decided silently" rule, previously
      restated in slightly different words in six places (`enact`, `embody`, `spawn`, `integrate`,
      `tell`, `character`), now stated once. Each of those six skills points at it with one line and
      keeps only its own domain-specific application (what counts as an open question there, and
      where it gets logged). README §0 Layer 1 now points at it too, for a human reader.
- [x] **Three new scripts wired into `/simulate`**, replacing prose-only steps with the same
      "mechanize the mechanical part, keep the judgment calls in prose" pattern already used for
      `update_character.py`/`record_hearsay.py`/etc.:
      - `scripts/lore/simulate_setup_worktree.py` — collapses Step 2's worktree-create +
        settings-bypass-write into one call, in the exact order previously spelled out (and easy to
        get wrong) across three separate prose steps.
      - `scripts/lore/pick_pair.py` — a genuine `random.sample()` draw for Step 3's pass pairing,
        replacing the model's own "pick randomly" (LLMs are demonstrably non-uniform at this).
      - `scripts/lore/simulate_tally.py` (`snapshot` + `report`) — Step 4's closing tally (deaths,
        criterion moves, final `life.lived`) computed from a before/after diff of the character
        files, instead of hand-counted from up to N pass summaries.
      Tested: `pick_pair.py`'s draw and its too-small-pool error path; `simulate_tally.py`'s
      snapshot→report round trip against real (unmodified) character files, confirmed zero false
      positives. `simulate_setup_worktree.py` is compile-checked only, not run live, since it creates
      a real git worktree + branch — first actual `/simulate` run will exercise it for real.

**Not in scope, still open:** the `/integrate` end-to-end test and the schema-evolution architectural
issue, both under "Lore integration skill (`/integrate`)" above, are unrelated to this pass — neither
was touched.

## Model-agnosticism plan (drafted 2026-08-07, paused — resume when the user is back)

Goal: use this pack with Claude, but also other model providers — commercial and open-source/local.
Researched rather than assumed (web search, not memory) before drafting. Two separate axes, easy to
conflate:

- **Axis A — same harness (Claude Code), different model underneath.** Free: Claude Code always
  offers the same tools (Bash, Read, AskUserQuestion, EnterWorktree, Agent, ...) to whatever model
  answers the API calls; swapping the model doesn't change what tools exist, only whether that model
  calls them well. Ollama v0.14+ ships a *native* Anthropic Messages API endpoint — point Claude Code
  at it via `ANTHROPIC_BASE_URL`, no proxy, no skill changes. Other commercial providers (OpenAI,
  Gemini, ...) aren't Anthropic-API-native, but a LiteLLM proxy translates, same env-var trick pointed
  at the proxy instead.
- **Axis B — leave Claude Code for a different harness** (Cursor, Gemini CLI, Codex CLI, OpenHands,
  Aider, ...). Real work, but less than expected: the `SKILL.md` format itself (folder + frontmatter +
  markdown body) is now an **open standard** (agentskills.io, donated to the Linux Foundation's
  Agentic AI Foundation, Dec 2025), natively supported by 30+ tools including Cursor, Gemini CLI,
  Codex, VS Code, GitHub Copilot, OpenHands, Goose, Roo Code. Our `.claude/skills/*/SKILL.md` files
  already sit in the right shape — no structural migration needed. What's *not* standardized: the
  Claude Code-specific tool names our skill prose calls out directly (`AskUserQuestion`,
  `EnterWorktree`, the `Agent` subagent dispatcher, `TaskCreate`) and the `.claude/settings.json`
  permission-bypass mechanism `/simulate` depends on — no equivalent on most other harnesses.

**User decision (2026-08-07): pursue Axis A first**, see how far it gets before committing to Axis B.

- [x] **Environment prepped for Axis A, 2026-08-07.** Ollama server confirmed running (v0.17.1, past
      the 0.14 threshold). `qwen2.5-coder:14b` pulled (~9 GB) — the top-rated local coding model for a
      12 GB VRAM card (RTX 4070 Super), chosen for tool-calling/agentic reliability over the two
      models already present (`mistral:latest`, `llama3.2:1b` — neither well-suited to this use case).
- [x] **Phase 0 smoke test run, 2026-08-08 — negative result, three distinct failure modes.** Not a
      config problem; a real result. Tested two models across two proxy paths, low-stakes prompts only
      (`.claude/PRINCIPLES.md` read, "what is an apple", no full skill run):
      1. `qwen2.5-coder:14b` via Ollama's native Anthropic-compat endpoint (`ANTHROPIC_BASE_URL` →
         `http://localhost:11434`) — hallucinated fake tool calls on *every* message, including ones
         needing no tool at all (`{"name": "GetModel", "arguments": {}}`,
         `{"name": "Read", "arguments": {"file_path": "/path/to/..."}}` on placeholder paths).
         Confirmed as a known, documented issue: this model's tool calls come back as raw JSON text in
         the response content instead of a structured `tool_calls` block, so Claude Code just prints
         the JSON as if it were the answer rather than executing anything.
      2. `qwen3:8b` via the same Ollama endpoint — stopped hallucinating fake tools, but *under*-triggers
         real ones (asked "what does PRINCIPLES.md say" → claimed it can't access local files at all,
         rather than calling `Read`). When explicitly told to use `Read`, it did — then hit a genuine,
         currently-open Ollama bug (`API Error: Content block not found`, a multi-turn tool-result
         serialization issue, confirmed against a live `ollama/ollama` GitHub issue), and in response to
         *that* error, fabricated an unrelated file as a guessed "fix" and falsely reported the original
         task complete. (Correction: it did ask permission before writing that file — not a silent
         bypass, just an irrelevant, hallucinated action it then lied about the purpose of.)
      3. `qwen3:8b` again, this time via a local LiteLLM proxy (`litellm[proxy]`, config mapping
         `qwen3-8b` → `ollama_chat/qwen3:8b` on port 4000) instead of Ollama's native endpoint — fixed
         the protocol bug (`Read` succeeded cleanly this time) but surfaced two more problems: an
         unprompted, unrelated file write (`example.json`, `{"key": "value"}`) with *no* error to react
         to this time (ruling out "error-driven confabulation" as the explanation — it's a standing
         habit, not error recovery), and then, worse, within the *same conversation*, right after
         successfully using `Read`, it lost all awareness of having file tools at all — denied having
         read the file, asked for an absolute path as if `Read` didn't exist, then flatly claimed it
         "cannot access local files," in three consecutive turns.
      Setup notes for reproducing: `py -m pip install "litellm[proxy]"`; the `litellm` console script
      isn't `python -m`-invokable (no `__main__.py`) — call the installed `.exe` directly, or add
      Python's `Scripts/` dir to PATH. Hit two unrelated environment snags getting it running at all:
      an `ImportError: cannot import name 'get_flat_dependant'` from a too-new `fastapi` (fixed by
      pinning `fastapi==0.115.6`, which in turn downgrades `starlette` below what the locally-installed
      `mcp`/`sse-starlette` packages want — a real, currently-unresolved conflict, just not one that
      broke anything used this session) and a `UnicodeEncodeError` on litellm's own startup banner
      under Windows' default `cp1252` console encoding (fixed with `PYTHONUTF8=1`).
      **Conclusion:** not "wrong model, try another" — three qualitatively different failure modes
      across two models and two proxy paths point at the same root cause: Claude Code's harness (system
      prompt, exact tool schemas, Anthropic Messages API conventions) is shaped around Claude
      specifically, and an 8–14B local model doesn't reliably hold together inside a harness built for a
      different model, even once the API plumbing technically works. Bigger local models (32B+) or an
      agentic-tool-calling-specific fine-tune might fare better, but that's a deliberate hardware/time
      investment, not a quick next swap.
- [ ] **Pivot (2026-08-08, user's own reframe): stop trying to make local models impersonate Claude
      inside Claude Code, and instead pursue Axis B properly** — a harness that's model-agnostic *by
      design* rather than via an Anthropic-API emulation shim. This was always going to be needed for
      other commercial harnesses too, so it isn't wasted work either way. Two concrete candidates,
      researched but not yet tried:
      - **Goose** (Block, open source) — natively lists every installed Ollama model in its own model
        picker (`GOOSE_PROVIDER=ollama`, `OLLAMA_HOST`), no translation shim needed for the local case;
        confirmed Agent Skills support; built on MCP for tools specifically (an open standard, not a
        bespoke harness-specific tool set) — architecturally the closer fit to "generic skills, no
        vendor-specific API." Windows-supported.
      - **OpenHands** — explicitly branded "model-agnostic," routes through LiteLLM for provider choice
        (OpenAI, Anthropic, Ollama, vLLM, ...), confirmed Agent Skills support
        (`docs.openhands.dev/overview/skills`). More established specifically for local-model agentic
        coding; docs recommend a much larger local model (Qwen3.6-35B-A3B) as the first one to try,
        likely too big for 12 GB VRAM comfortably — would need a smaller Qwen3 variant instead.
      Why either should sidestep this session's specific bugs: neither asks the model to speak
      Anthropic's Messages API tool-use format at all — they talk to Ollama via its OpenAI-compatible
      tool-calling path, which has existed since mid-2024 and is far more battle-tested than Ollama's
      ~7-month-old Anthropic-compat endpoint that produced failure modes 1 and 3 above.
      **Decided (2026-08-09): OpenHands.** Chosen over Goose specifically on scalability — Goose
      hard-caps concurrent subagents at 10 with no recursive spawning and a 5-minute/25-turn default
      ceiling per subagent, while OpenHands isolates each task in its own Docker/Kubernetes container
      with no equivalent hard cap, has a headless REST-API mode built for CI/batch use, and an optional
      managed-cloud path if local scale ever isn't enough — the better long-term fit for something
      shaped like `/simulate` (many isolated, potentially parallel passes) even though Goose would have
      been the faster thing to stand up tonight.

### Repo restructuring plan (2026-08-09, planned — NOT YET IMPLEMENTED, do next session)

**The problem with the first draft of this plan:** it pointed OpenHands at `.claude/skills/` (via a
junction) and left `.claude/PRINCIPLES.md` as the canonical philosophy file — which still made the
*project* depend on a `.claude/`-shaped structure, just with another harness bolted on. Correctly
called out by the user: model-agnosticism means the reverse — `.claude/` should hold only what Claude
Code itself hard-pins to that exact path, nothing else, and the project's real content should live
somewhere no single vendor's product name is attached to.

**Corrected target structure:**

```
AGENTS.md              canonical, harness-neutral orientation doc — replaces .claude/PRINCIPLES.md's
                        role (the "nothing decided silently" rule) plus README §0's architecture
                        overview, rewritten for an agent audience. The real cross-tool standard for
                        this role (natively read by Codex/Cursor/Gemini CLI/Windsurf/Aider/15+ others,
                        60,000+ repos on it already).
CLAUDE.md               thin — just imports AGENTS.md (Claude Code doesn't read AGENTS.md natively as
                        of mid-2026, per its own docs).
.agents/
  skills/                canonical home for all 10 skill folders (moved from .claude/skills/ via
                          `git mv`, preserving history) — the actual Agent Skills open-standard
                          location, and OpenHands' own default lookup path, so it needs zero
                          skills-related config on OpenHands' side once files live here for real.
  harness/
    openhands/
      launch.ps1          sets LLM_MODEL/LLM_BASE_URL/LLM_API_KEY env vars + `--override-with-envs`
                          (required — OpenHands silently ignores those env vars without this flag and
                          falls back to the user's global `~/.openhands/settings.json`, which isn't
                          repo-portable), then runs `openhands serve --mount-cwd`. Action-approval
                          stays interactive by default (matching how the main repo's own
                          `.claude/settings.json` behaves today — no bypass); a bypass
                          (`--always-approve`, or `--headless --exit-without-confirmation` for full
                          unattended automation) is an opt-in flag on the script, not the default —
                          same split `/simulate`'s worktree already draws between normal sessions and
                          batch runs, deliberately kept consistent rather than inventing a new rule.
.claude/
  settings.json           stays — genuinely Claude-only, no cross-tool equivalent exists, and it's
                          already repo-committable so Claude Code needs nothing else.
  settings.local.json     stays, same reason.
  skills/                  → directory junction to ../.agents/skills (same proven pattern as this
                          repo's existing `resourcepack/` ↔ `resourcepacks/luminacion/` junction, see
                          README Layer 4) — exists only because Claude Code hardcodes this exact path
                          and can't be told to look elsewhere. Zero real content stored under `.claude/`
                          once this is done.
README.md                unchanged — still the human tutorial, untouched by any of this.
```

**Steps, in order:**
1. `git mv` all 10 skill folders from `.claude/skills/` → `.agents/skills/`.
2. Write `AGENTS.md` at repo root (content sourced from `.claude/PRINCIPLES.md` + README §0).
3. Delete `.claude/PRINCIPLES.md`; update the 6 skills that currently point at it (`enact`, `embody`,
   `spawn`, `integrate`, `tell`, `character`) to point at `AGENTS.md` instead.
4. Write thin `CLAUDE.md` that imports `AGENTS.md`.
5. Create the `.claude\skills` → `..\.agents\skills` junction (`mklink /J`, no admin/Developer Mode
   needed for a directory junction on Windows, unlike a symlink).
6. Fix any other live references to `.claude/skills/` across the repo (README, scripts) —
   `TODO.md`'s own historical entries stay untouched; they're a changelog of what was true when
   written, not living documentation.
7. Write `.agents/harness/openhands/launch.ps1` per the spec above.
8. Install OpenHands (`py -3.12 -m pip install openhands-ai`, sidestepping the machine's default
   Python 3.14 that caused the fastapi/litellm conflict earlier this session) and run the launch
   script from inside the repo.
9. Smoke test: start a fresh OpenHands conversation (required so it rebuilds its skills catalog),
   confirm it lists the skills correctly, then repeat the same low-stakes checks from the Ollama/Claude
   Code round — read `.claude/PRINCIPLES.md` → `AGENTS.md` once moved, then `/tell` — watching
   specifically for whether OpenHands' harness avoids the three failure modes logged above (fake tool
   calls, unprompted irrelevant writes, mid-conversation tool amnesia), since the whole premise of
   switching harnesses is that those were Claude-shaped-harness problems, not Qwen problems.
- [ ] **Cosmetic, low priority:** every skill's `disable-model-invocation: true` frontmatter field is
      a Claude Code extension, not part of the core Agent Skills spec (confirmed against
      agentskills.io/specification — core fields are `name`, `description`, `license`, `compatibility`,
      `metadata`, `allowed-tools`). Likely harmless (unrecognized YAML keys are typically just ignored)
      but a strict validator on another client could flag it. Not worth fixing unless it actually
      breaks something on a real Axis B test.

## Synthesis mechanism — characters forming their own theories (proposed, pinned 2026-08-07)

**Built 2026-08-08.** Design pass, decision pass, spec (`.claude/skills/enact/SKILL.md` Step 5c),
`scripts/lore/check_resonance.py`, and `update_character.py --add-synthesis` are all done — see Step 5c
in `SKILL.md` for the calling convention. Not yet exercised on a real `/enact` run; the mechanical
pre-filter only matches against `knowledge.education.items` (structured `about`-style refs), not
`knowledge.experience`/`backstory` prose, so its candidate recall on a character-heavy scene is
untested until it's actually used. Answers a real gap identified while discussing the "Knowledge
mutation system" section near the
top of this file and the "Schema evolution in `encodings.json`" work done this session: everything
currently in `/enact` — mutation at record time, the criterion shock/reject/reinterpret/break
machinery — reinterprets or resolves *one* input at a time. Nothing currently lets a character combine two things they know into a third belief that isn't
reducible to either parent. The goal: a character can form their own theory about the world (or about
themselves, or about someone else) from what they already knew plus what they just heard, gated so that
this stays rare and meaningful rather than firing on every scene.

**Where it runs:** a new `/enact` step, proposed as Step 5c, immediately after Step 5b's shock
resolution (same "reflect on what this scene did" position, same "default is no change and that will be
the answer almost every time" discipline the shock gate already uses).

**Core shape, agreed so far:** synthesis only considers pairs where one side is something the character
heard/lived *this scene* and the other is already in their standing knowledge (education sample or
prior experience) — never a full sweep of a character's whole life, never two things both freshly heard
in the same breath. A cheap mechanical pre-filter narrows candidates (varies by subtype, see below);
the model then judges, per candidate, whether the pairing actually raises something neither claim states
alone (a gap or tension, not agreement/restatement) — most candidates should produce nothing. Whatever
does synthesize gets written to `knowledge.experience` as `{"kind": "synthesis", "about": [A, B],
"derived_from": [A, B], "text": "..."}` (extending the existing "about can be a list" convention, not a
new field shape) — private knowledge unless the character actually voices it in a later scene, at which
point it becomes an ordinary hearsay claim through the existing recording path, no new sampling-pool
machinery needed. **Credibility inheritance rule:** the synthesized claim inherits the *weaker* of its
two parents' credibility — a synthesis built on a shaky/uncorroborated parent comes out hedged ("maybe,"
"it makes me think"), not asserted, reusing the existing `oral_lore`/traceable ledger rather than
inventing a new certainty scale.

**Subtypes identified so far, each with a different resonance signal — not an exhaustive taxonomy, more
should surface once this is actually tried:**

1. **Causal/narrative.** Two things that already share an `about`/entity reference combine into a new
   claim about meaning, motive, or cause. Worked example discussed: Nerkeli has flown M7 (→ Nvhi) for
   years without ever really seeing the place (his own established backstory); Nuvilo's family claims
   descent from Navalius, Nvhi's founder (freshly heard, uncorroborated). Synthesis: "If M7 always ends
   where Nuvilo's family says they're from, then all these years turning around at the airstrip, I've
   been skipping past the one place that might matter most to him." Mechanical pre-filter: shared
   `about` id (reuse `check_anchor_reference.py`'s matching logic).

2. **Identity/coreference.** Two *differently-named* things share a distinctive (not generic) detail,
   suggesting they might be the same referent. Worked example discussed: a character knows "Sit Nalta"
   has a hot-air-balloon port; a traveler mentions "Sit:Nalta" and its hot-air balloons. Synthesis:
   these may be the same place. Notably, this exact ambiguity is *already* logged as `CONFLICT-07` in
   the objective record — a character reaching this independently, from inside their own bounded
   sample, would be rediscovering a real structural ambiguity without ever having read `conflicts`.
   Proposed check: when an identity-type synthesis fires, look it up against `conflicts` — a match is a
   good, coherent "the character caught something real" outcome worth noting as such; no match is a
   riskier, unbacked guess, held more tentatively (possibly worth its own `unknowns.md` entry if it
   resonates with the corpus, per the same "not every claim produces one" discipline `/enact` Step 5
   already uses). Mechanical pre-filter: name-string similarity (the same `difflib` fuzzy-match already
   built for `build_source_index.py`) plus shared distinctive descriptive content — the distinctiveness
   call (hot-air balloons vs. "has a market") stays a model judgment, not scriptable.

3. **Conflict-explanation** (brainstormed, not yet discussed with the user in depth). A character
   encounters two items that are *already* flagged as disagreeing in the objective record (share a
   `CONFLICT-NN` tag) and invents a personal reconciling story for *why* the disagreement exists —
   without ever officially resolving it; `user_resolution` stays the user's call alone, same as every
   other conflict. Sketch: a character who's sampled both chronicles' conflicting start-years for Era
   del Daax might theorize "maybe one book counts from when the códigos were invented, the other from
   when the government fell — two starting lines for the same age" (Döran's own claim #8 already
   brushes right up against this without taking the last step). Mechanical pre-filter: shared
   `CONFLICT-NN` tag between two known items.

4. **Pattern/generalization.** Not a pairwise collision at all — noticing the *same* thing recurring
   three or more times across a character's own sample and abstracting it into a general belief or
   proverb, not a claim about one specific referent. Sketch: a character who's sampled several
   highway/train segments that all terminate at Nvhi might conclude "seems like every road in this
   world eventually leads to Nvhi." Mechanical pre-filter: frequency (an entity/theme appearing 3+
   times across the sample), not a pairwise `about` match — structurally different from the other four.
   **Decided 2026-08-08: the occurrence that crosses the 3+ threshold must be fresh from the scene that
   just concluded** — the prior N-1 occurrences are already standing knowledge, and generalization only
   fires because *this* scene supplied the tipping instance. Keeps it consistent with every other
   subtype's "something new happened" gating rather than letting a character generalize from pure
   reflection with nothing new. (Like all of Step 5c, this check runs once, post-scene, at record time —
   not live during the scene itself.)

5. **Relational/motive.** Same causal mechanic as (1), but pointed at a *person's*
   motive or history — including the character's own backstory — rather than a place's meaning. Sketch:
   Khaoe's registered backstory already says her family came from Khan Ice before Khol Moshin; if she
   later samples Döran's claim that Khan Icé served as a wartime refuge, she could theorize "maybe
   that's why my family left — the war, not just wanting somewhere new." Mechanical pre-filter: both
   items concern the same person (self or a named third party), not a place.

**Open questions:**

- ~~Should the criterion (`trusts`/`distrusts`) color the *flavor* of a synthesis when one exists (skeptic
  vs. connective framing), or only gate whether it fires at all?~~ **Decided 2026-08-08: both.** Criterion
  affects whether synthesis fires at all (e.g. skeptics synthesize less readily) *and* colors the
  tone/framing of the resulting claim when it does fire. A character with no derived criterion yet
  (several still don't, see the "Criterion / will-to-live system" section above) can presumably still
  synthesize plainly, same as the trust table's ambiguous bottom row.
- ~~Is one synthesis per scene the right cap, or should it scale with how many genuine candidates survive
  the resonance gate?~~ **Decided 2026-08-08: no cap.** Every candidate that survives the mechanical
  pre-filter *and* the model's gap/tension judgment gets written, however many that is in a given scene.
  No tie-break needed since nothing competes for a single slot.
- ~~Subtypes 3–5 are brainstormed, not yet worked through with a concrete example the way 1–2 were.~~
  **Resolved 2026-08-08:** subtypes 3 and 5 already had worked examples and mechanical pre-filters at the
  same depth as 1–2 on inspection — no further pass needed. Subtype 4 was the actual gap (see its own
  entry above for the resolution: this-scene trigger required, evaluated post-scene at record time).
- ~~Whether this needs its own mechanical script (a `check_resonance.py` mirroring
  `check_anchor_reference.py`'s shape) per subtype, or one script with a subtype parameter.~~ **Decided
  2026-08-08: one script, subtype parameter.** The five detection mechanisms differ enough to need
  separate internal logic branches, but share one entry point rather than duplicating I/O/CLI scaffolding
  across five files.
- [ ] **Does a synthesis ever reach `encodings.json`, and by what mechanism?** The spec above says a
  synthesis is "private knowledge unless the character actually voices it in a later scene, at which
  point it becomes an ordinary hearsay claim through the existing recording path, no new sampling-pool
  machinery needed" — but that claim hasn't been checked against how a hearsay claim actually gets folded
  into `encodings.json` (vs. just `hearsay.md`/the character's own `knowledge.experience`). Worth
  confirming, once Step 5c has actually fired at least once and been voiced in a follow-up scene: does
  `record_hearsay.py`/`/enact` Step 5's existing path really carry a `"kind": "synthesis"` claim all the
  way into the world's sampleable pool the same way any other hearsay claim does, or does something
  synthesis-specific (the `derived_from`/`about`-list shape, the inherited-credibility hedging) get lost
  or need special-casing along the way? Unverified either direction — flagged here so it isn't assumed
  either way before a real run tests it.

### /simulate debrief and next-phase design: materiality, arcs, and emergence (2026-08-10, planned — design only, NOT YET IMPLEMENTED)

**Status update, verified against the live code: most of this shipped.** Of the 9 numbered proposals
below, points 1 (routines-as-archetypes), 2 (cycling), 3 (pairing unchanged), 4 (mechanical
coincidence/visit location resolution — `scripts/lore/resolve_location.py`), 6 (arc derived from
routine archetype), and 8 (reproduction, `generate_offspring.py`) are all live in
`.claude/skills/simulate/SKILL.md` and its scripts, and have run through multiple real `/simulate`
extended-mode passes per `LAB_REPORT.md`. Point 5 (group scenes) is confirmed NOT shipped —
`/simulate` still runs strictly two-participant scenes. Point 7 (scene content seeded from the arc's
"last thing done") and point 9 (emergent routine acquisition) also aren't built — no `last_done`-shaped
field exists anywhere in the schema or scripts. This matches the "explicitly still open" list below,
which stays accurate and untouched.

**See `LAB_REPORT.md` (repo root) for the persistent, cross-run assessment log this debrief seeded** —
run-by-run findings against the standing objective, plus open design questions carried forward across
sessions. This section is the original design writeup; that file is where it gets tested and revised.

**Debrief context.** The 50-pass `/simulate` run (2026-08-08/09/10, worktree `simulate-20260808-181023`,
full record in that worktree's `SIMULATION_LOG.md`) worked exactly as designed mechanically — 25
criterion moves, 20 syntheses, hearsay mutation and record-keeping all correct, several real machinery
bugs found and permanently fixed in the skill itself — but the *content* converged heavily on
epistemological discussion (whose account to trust, contradiction-preservation) instead of producing
dramatic emergence. Diagnosed three independent, compounding, structural sources — none a bug in what
was built, all properties of what the tool currently *is*:

1. 3 of the 5 participants (Auroboro III, Ilária, Khaoe) walked in with epistemically-anchored criteria
   from *before* this run — traceable to backstory (Ilária's backstory literally is "wrote one of the
   two contradictory chronicles"), not to anything this run did.
2. `/enact` Step 3's `trusts`/`distrusts` field is explicitly named as the skill's privileged dramatic
   payoff ("nearly invisible until two sources actually disagree in the scene — that's the moment it
   shows"), which structurally channels *every* scene toward epistemic conflict regardless of what a
   character's `standard` is actually about (even Nerkeli's action-flavored standard — "reach places,
   don't just study maps" — got phrased as a *verification*, i.e. epistemic, distrust once run through
   this mechanism).
3. Any future "shared knowledge between two characters" topic-selector would *also* skew epistemic, for
   a third, unrelated reason: checked directly against `encodings.json`, `concepts` (19 entries) and
   `conflicts` (18) are roughly a third the size of `locations` (58) and `named_inhabitants` (69) — so
   two independently-sampled characters are mechanically far more likely to coincidentally share a
   concept or conflict than a specific person or place, purely from smaller-pool collision odds.

**Conclusion:** the tool renders its designed objective correctly — lore evolves, criteria shift, hearsay
mutates, exactly as specified. The underwhelming *drama* isn't a flaw in that design; it's that
everything so far runs on one substrate only (language), with no material consequence, no scarcity, no
clock outside `life.span` (which never fired once in 50 passes), and a content-generation step
(`trusts`/`distrusts`) that was only ever meant to modulate a reaction, not generate a topic.

**Proposed next phase**, worked out collaboratively in the debrief conversation following the run:

1. **Routines as authored archetypes.** Each character gets a small, handcrafted set of home routines —
   a location tied to a role ("works the market," "keeps the workshop in Khan Icé"). The routine *is*
   the archetype: "market" already implies buying, selling, price disputes, scarcity, trust in a trading
   partner — texture for free, without authoring a project per character. Author-placed, not generated,
   same discipline as everything else in this system that's a premise rather than painted detail.
2. **Cycling.** Each pass, a simple mechanical rule (fixed rotation, or an authored skew toward one
   routine) decides which of a character's routines they're currently in. Deliberately not meaningful on
   its own — just needs to run.
3. **Pairing stays exactly as-is** — `pick_pair.py`, unchanged, still a uniform random draw across the
   living pool. No new selection layer; letting a model choose who to visit would just reintroduce the
   same salience bias `pick_pair.py` already exists to prevent.
4. **Location resolves mechanically after the draw:** compare both participants' current routine. Same →
   coincidence (scene happens there, whichever one's "home" it narratively is decided by a coin flip —
   unplanned, ordinary, no criterion or motive required). Different → visit (scene happens at
   participant_2's home; participant_1 traveled). Verified `pick_pair.py`'s `random.sample()` carries no
   positional bias, so the traveler/host role averages out fairly over a long run — no extra fairness
   logic needed.
5. **Group scenes fall out of coincidence for free.** When 2+ participants share a location, check every
   *other* living character's current routine against that spot; each match gets an independent
   dice-roll chance to join. Keeps group scenes rare by construction; the roll probability should get
   tuned down as population grows (see reproduction below), or group scenes stop being rare as the cast
   grows.
6. **Arcs, derived from the routine's archetype, not a separate collision-derivation step.** Authored
   once per place-type (the market archetype, the workshop archetype), not per character. An arc carries
   real progressive state — a "last thing done" that every scene touching that routine advances. This is
   genuinely material: an evolving fact, not a corpus-drawn category (so it doesn't inherit the
   small-pool bias in point 3) and not free model invention (so it doesn't inherit the salience bias
   `pick_pair.py` was built to avoid).
7. **Scene content candidate — proposed, not decided:** anchor each scene on the host's (or shared, in a
   coincidence) "last thing done." The visitor walks into a concrete, already-determined material fact,
   and brings their own last-thing-done into it. `trusts`/`distrusts` still applies, but only to *how*
   each character reacts to what's actually there — it stops being asked to generate the topic too.
   **Unresolved:** how a reaction is supposed to fold back into becoming the arc's *next* "last thing
   done" — flagged in the debrief, not solved.
8. **Reproduction (autopoiesis — self-*re*production).** Rare, selected event, not automatic once a
   threshold (e.g. a minimum shared-conversation count, cheap to check since hearsay entries already
   record participants) is crossed — mirrors how death is gated by `horizon.py`'s own logic, not
   automatic either. **Open: what triggers the birth *check* itself** (every pass? probability-gated?).
   Once selected: mirror `record_death.py`'s existing circle-notification pattern — the parents' circles
   get told immediately ("others know them before they know them"), while the child doesn't enter
   `pick_pair.py`'s eligible pool until a cooldown clears (decided at creation, hand-authored, like
   routine counts). The child's traits should be a genuine mutation/blend of both parents — knowledge
   crossed and mutated, not a fresh `sample_lore_knowledge.py` draw; criterion inherited-then-mutated
   rather than freshly derived; possibly `life.span` itself as a heritable trait — not just "a new NPC,"
   an actual drift of the population's own composition across generations.
9. **Emergent routine acquisition (later idea, not decided):** a location a character keeps ending up at
   via repeated visits could become a de facto additional routine over time, without being authored at
   creation — emergent geography layered on top of the handcrafted starting set.

**Explicitly still open — per this project's own "nothing decided silently" rule, do not resolve these
silently when implementing:**
- Birth-check trigger condition (point 8).
- How a scene's outcome becomes the arc's next "last thing done" (point 7).
- Group scenes need `/enact` Step 3b extended beyond its current strictly-two-participant design —
  multiple `trusts`/`distrusts` pairs interacting at once, and whether an anchor-touching shock is
  visible to everyone present or just whoever it's aimed at.
- Whether `/enact` Step 3 should be rewritten to give material/action friction an equally-weighted
  "moment it shows" alongside epistemic disagreement now that arcs are meant to carry most of that
  weight — or left as-is, since it may end up doing less work once arcs exist regardless.

**Suggested implementation order** — this is a substantial redesign; build and test the smaller piece
before the larger one, not all at once:
1. Add authored `routines` + per-archetype texture to character files (or a shared lookup keyed by
   archetype name), plus the cycling rule.
2. Extend `/simulate` Step 3 to compute each participant's current routine post-pairing and resolve
   coincidence vs. visit into a scene location.
3. Add arc state (a `last_done`-shaped field) and seed scene content from it instead of free invention,
   per point 7.
4. Run a smaller `/simulate` batch on the existing 5-character population against just steps 1–3,
   specifically to test whether this actually breaks the epistemology-convergence pattern, before
   building anything further on top of it.
5. Only after that: reproduction (point 8) and group scenes (point 5), which both depend on the above
   already working and both need `/enact` itself extended — dyadic → variable participant count for
   group scenes; a new record-keeping script mirroring `record_death.py` for births.


## /simulate Run 2 knowledge/corpus-absorption fixes (2026-08-11) - for continuation later

**Where things stand, so the next session can pick this up cold.** This is the eighth+ extension of
Run 2 (`.claude/worktrees/simulate-20260810-164704`, 305 passes as of this session, `LAB_REPORT.md`
has the full mechanical/narrative log). This entry only tracks the corpus-absorption mechanism work
done *after* the 305-pass run itself finished, since it touches shared scripts/schema, not just that
one worktree's own data.

- [x] **Knowledge inheritance retuned** (`generate_offspring.py`, `_lore/tuning.json`'s
      `offspring_knowledge`) - a child now reliably inherits a majority of both parents' education,
      draws a bounded amount of genuinely new material from `encodings.json`'s full corpus (concepts,
      locations, conflicts, tales, inhabitants, routes, eras, hearsay - not just concepts/locations as
      first implemented, corrected same session on user report "when I say general knowledge, I mean
      ALL of the encodings"), skewed toward the child's own inherited criterion, and inherits a
      fraction of both parents' own `knowledge.experience` as wrapped "Grew up hearing: ..." family
      lore. Tested via dry-run births, fully reverted test artifacts each time.
- [x] **Hearsay wasn't actually absorbing into the corpus - the core gap this whole thread chased.**
      `build_source_index.py` existed and worked, but had never been run against this run's 305 new
      hearsay entries, and 325 of 331 resolvable references failed even once run: the 42 arc-concepts
      /simulate's own arcs had been using for hundreds of passes were never registered as real
      `concepts[]` entries - only ever existed as tag strings inside `arc.about`. One-time catch-up
      (`promote_arc_concepts.py`, job-tmp only) registered all 42 (mechanically assembled from each
      arc's own data, never freely authored) and `build_source_index.py` re-run - 318 more links
      folded in. Permanent fix: `scripts/lore/register_arc_concept.py` (new) registers a concept the
      moment its arc is authored, wired into `SKILL.md`'s arc-authoring step; `SKILL.md` Step 17 now
      runs `build_source_index.py` once at the natural end of a batch.
- [x] **`has_sources` was only true for 4 of 14 categories, and the flag alone wasn't sufficient** -
      `resolve_prefixed()` had a *separately* hardcoded prefix map that ignored the flag entirely.
      Fixed both: `_categories` now has `has_sources: true` for every category except `hearsay` itself
      (the source, not a valid target) and `characters.named_inhabitants` (still excluded - see next
      bullet); `resolve_prefixed()`/`build_index()`/`load_categories()` are now fully schema-driven,
      including per-category `id_field` (was hardcoded to assume every entry's identifier was called
      `"id"` - true for `concept`/`location` by coincidence, false for `highway` (`code`), `airport`
      (`location`), `year_esquema` (`year`, an int) - would have KeyError'd the instant any of those
      categories' `has_sources` flag was ever actually exercised).
- [x] **Bare-reference ambiguity default: `location` wins a tie** (2026-08-11, user direction). Several
      locations (Görff, Salthos Cruzados, Khol Moshin) also have an airport of the same name, so a
      bare `about: "gorff"` used to correctly-but-unhelpfully report as ambiguous once `airport` became
      sourced. `resolve_bare()` now prefers a single `location` candidate among tied exact matches;
      still refuses to guess if the tie involves two non-location categories or two location
      candidates.
- [x] **Character births are tales, not concepts** (2026-08-11, user correction). The 14 birth events
      that had been given ad-hoc `concept: X_birth` tags (never a real backing entry, purely a
      scene-writing convention with no script behind it) were converted: each got a real
      `_lore/tales/birth_of_<key>.md` + `tales.entries` row (same shape as a death tale), the 14
      matching concept entries were deleted, and every hearsay claim that referenced
      `concept: X_birth` was repointed to `tale: birth_of_X` (45 claims). Permanent fix:
      `generate_offspring.py` now writes a real birth tale itself at the moment of birth (mirroring
      `record_death.py`'s own tale-writing exactly, via a new `write_birth_tale()`), printing the tale
      id so the caller tags the birth-announcement hearsay claim `about: "tale: <id>"` from the start -
      no future birth should ever need this retroactive treatment again.
- [ ] **`characters.named_inhabitants` still can't receive hearsay/tale sources at all**, even though
      its own `has_sources` flag is now `true` - it's `shape: "grouped_list"` (nested
      `{locality: [people]}`, no flat `id_field`), and `load_categories()` deliberately excludes
      non-`"list"`-shaped categories from the generic linking path to avoid a crash. This is the same
      gap flagged mid-conversation for a name like "Zeya" surfacing only in claim text, never as a
      structured `about: "inhabitant: X (Y)"` reference - two separate problems stacked (the schema
      can't receive the link even if the reference existed; and nothing currently proposes that a name
      mentioned in dialogue deserves a `named_inhabitants` entry in the first place, which is a real
      judgment call, not a mechanical one the way arc-concept promotion was). Not fixed this session -
      would need a real per-person index entry shape decision first.
- [ ] **8 references remain genuinely unresolved**, unrelated to this session's fixes - pre-existing
      gaps predating `/simulate` entirely (`jardin_de_los_parajes` has no `locations` entry at all;
      `hotel_kholi`/`preservation`/`memory`/`transformation` have no `concepts` entries; one bare
      `'Era del Daax'` reference doesn't match `time_systems.ensayo_i_eras`' own naming exactly). Left
      as `build_source_index.py`'s own honest "never guessed" report - worth a look next time someone's
      touching that part of the corpus, not blocking anything from this session.
- [x] **Committed since — resolved.** `scripts/lore/build_source_index.py`, `generate_offspring.py`,
      and `register_arc_concept.py`/`_lore/tuning.json` all show clean, committed history now (last
      touched by `2a2e8f6`, `eac3abb`, and `690f10d` respectively); the main checkout has no leftover
      uncommitted state from this thread.

## `sample_lore_knowledge.py --mode skewed` can't do proportioned multi-topic splits (2026-08-16)

Surfaced auditing `/character` Step 3 with the user (walking Zarkatraz through knowledge sampling from
scratch). The user wanted a 30% draw split into three independently-sized thirds - one skewed toward
Balahm/Salthos Cruzados, one toward trade, one genuinely random. Read `draw_sample()` directly to
confirm rather than guess: every `--topic` value passed is OR'd into a single flat "matching" bucket via
a plain case-insensitive substring check against each pool item's `id + " " + text`; there's no
per-topic weighting and no third bucket - only "matched at least one given topic" vs. "everything else"
(the random fallback fill). A request for N separately-proportioned topic groups in one draw isn't
expressible as a single call today; the closest the tool supports is collapsing every topic into one
skewed group against a single random remainder.

- [ ] **Multi-topic proportioned skew.** Either extend `--mode skewed` to accept repeatable
      `--topic-group "kw1,kw2" --group-percent <N>`-shaped args and allocate the sample across groups
      (falling back to random for whatever's left), or explicitly document the current one-call
      limitation in `/character` Step 3 and have the author hand-merge multiple single-topic draws
      (one `sample_lore_knowledge.py` call per group, each at its own `--percent`) when an exact split
      actually matters. Either way, a deliberate decision, not a silently-discovered gap each time
      someone asks for this.

## VERY IMPORTANT: the player's own lines aren't guaranteed to become claims (2026-08-16)

Surfaced same audit session as the section above, user's explicit priority - this is how the user (the
world's author) can shape canon *through enactment itself*, not just via `/tell` or uploaded material,
so a silent drop here is a real authoring-control gap, not a cosmetic one.

**Current state, checked against real data, not assumed:** the mechanism can already do this -
`khaoe_milkucha_jardin_de_los_parajes` has several claims sourced to Milkucha (the player), e.g. "Milkucha
built the Cinema in Grosslor," "Milkucha can move mountains using mod power..." - captured and folded
into the pool exactly like an NPC's claims would be. But `sonoros_lost_traveler` and every `doran_*`
solo dialogue have **zero** player-attributed claims, and nothing in `/enact` Step 5's text
(`.claude/skills/enact/SKILL.md`) states a rule guaranteeing the player's own assertions get the same
"capture the kernels" treatment an NPC's lines do - it currently rides entirely on the enacting agent's
own per-scene judgment call about whether to bother. That may be correct in the two zero-claim scenes
(the player may have only asked questions there, nothing assertion-worthy said) or may not be - there's
no way to tell after the fact, and that's exactly the problem: nothing forces the question to even be
asked.

- [x] **Resolved.** `/enact` Step 5 now states it outright: "The player is a full participant in this
      step, not an exception... gets a claim exactly as it would for any NPC speaker... held to the
      same 'capture kernels, not connective tissue' bar." Also settles the mutation question: player
      claims "skip this step's mutation machinery entirely and go in as a flat, unmutated report."

## `claim.about` doesn't feed `sample_lore_knowledge.py` - structural tag and keyword match diverge (2026-08-16)

Same audit session. A claim's `about` (single ref or list, e.g. `["location: khan_ice", "concept:
hotel_kholi"]`) links it to a target entry via `build_source_index.py`, but `_flatten_claims()` in
`sample_lore_knowledge.py` only builds a hearsay pool item's matchable text from `claim.text` +
`participants` + the scene's own location label - `about` is never read. So a claim structurally
tagged `about: "location: khan_ice"` whose prose never says "Khan Ice" (e.g. only says "Hotel Kholi")
is invisible to a `--mode skewed --topic "khan ice"` draw even though it's genuinely about that place.
Confirmed real, not hypothetical: `gok_milkucha_alcove#1`'s Hotel Kholi claims are exactly this shape.

- [x] **Resolved.** `sample_lore_knowledge.py`'s `_enrich_hearsay_matching_text()` resolves each
      claim's `about` ref(s) to their target pool item and folds that item's own text in, not just the
      bare id — exactly the "complete fix" described here, including the no-knowledge-cascade
      boundary (`knowledge.education.items` still stores only the bare `"hearsay: <id>#<n>"` pointer;
      this only widens what a draw can *match*, never what a character *knows*). Explicitly scoped as
      best-effort (exact/bare-id match only, not `build_source_index.py`'s fuzzy resolution) per its
      own docstring — a deliberate, disclosed limit, not a gap.

## CRITICAL, user design correction: epistemology should derive from source provenance, not pool category (2026-08-16)

**User's explicit direction, overriding the current design.** `/character` Step 4d currently derives a
criterion's `trusts`/`distrusts` lean from `epistemology_group`, a field assigned per *pool category*
(`location`/`concept`/... -> `ambiguous`; `era_ensayo`/`era_esquema`/`era_libro`/`year_esquema` ->
`chronicles`; `conflict` -> `conflict`; `hearsay` -> `hearsay`; **`tale` -> `hearsay`**). The user wants
this replaced: **epistemology should be derived from `sources[].category` - `material`, `hearsay`, or
`tale` - and nothing else.** Two specific corrections named:

1. **Tale must not share hearsay's epistemology group.** Grouping `tale` under `hearsay` was an agent
   design decision made while building this system, never actually surfaced to the user for
   confirmation, and the user disagrees with it on inspection: a tale is *objective truth* (told
   directly by the world's author, folded into the objective arrays, never subject to the
   `inconsistent_with_record` doubt a hearsay claim can carry) even though it arrives through oral
   tradition/narrative rather than documented material - closer to myth than to gossip. That's a third,
   genuinely distinct epistemology, not a hearsay variant.
2. **Provenance-driven, full stop:** knowing something because it's material, because it's hearsay, or
   because it's a tale should be the *entire* signal - not which top-level array/category the item
   happens to sit in. This removes the current `chronicles`/`conflict`/`ambiguous` groupings as
   independent categories; whatever they get replaced with should fall out of provenance instead (see
   open questions below - not decided here).

**The complication, confirmed against real data, not hypothetical:** an entry's `sources` array can
(and often does) carry more than one category at once. Checked `gorff` directly: 5 `material` sources
(atlas coords, catastro, the libro, dated screenshots, NPC roster - what actually established the
place) plus 10 `hearsay` sources (`khaoe_banco_colectivo#4`, `doran_plaza_orientation#4`, etc. - claims
that later *mentioned* Görff, backlinks only, never merged into its own `names`/`region`/`notes`
fields - this is NOT hearsay content overwriting or corroborating the objective entry, confirmed by
reading the entry directly). 23 `location`/`concept` entries currently carry mixed `material`+`hearsay`
sources this way. **User's resolution: when an item's sources span more than one category, pick one at
random as the leading source for epistemology purposes**, rather than trying to rank or merge them.

- [x] **Implemented 2026-08-16.** `epistemology_group` removed entirely from `_categories` (every
      entry, plus its own method note explaining why a category-level field never worked - two items
      in the same category can have different provenance). New `scripts/lore/anchor_epistemology.py`
      resolves an anchor's provenance mechanically (`material`/`hearsay`/`tale` from `sources[0]`, or
      the trivial self-evident case when the anchor's own category already is one of those). `/character`
      Step 4d rewritten around it, with a `material`/`hearsay`/`tale` trusts/distrusts table replacing
      the old `ambiguous`/`chronicles`/`conflict`/`hearsay` one. Tested against real data including the
      exact Görff mixed-provenance case cited above.
- [x] **Tiebreak resolved: original-source priority**, not random. `sources[]` is append-only
      (`build_source_index.py` only ever adds backlinks onto what's already there), so "recorded
      first" means "what actually established this in the record," not an arbitrary pick - and it
      naturally excludes later backlinks from competing at all, closing the exact "10 hearsay backlinks
      shouldn't outweigh 5 founding material sources" problem this section flagged. Verified: Görff
      resolves to `material` (its first-recorded source), correctly ignoring its 10 later hearsay
      mentions regardless of count.
- [x] **Conflict resolved: kept as a fixed special case, outside the material/hearsay/tale system
      entirely.** A conflict is definitionally two sources disagreeing, not sourced from one
      provenance - `anchor_epistemology.py` reports it as a special case rather than computing
      anything, and Step 4d keeps its existing fixed row unchanged (trusts verification, distrusts
      certainty). (Same treatment extended to `experience`-entry anchors, which aren't in
      `encodings.json` at all and so have no `sources[]` to resolve either - also kept as a fixed
      special case, a call made during implementation, worth confirming.)
- [x] **Era/chronicle distinction eliminated, confirmed by the user.** Era/year items now resolve to
      `material` the same as any other material-sourced item, per "we only want material, hearsay and
      tale" (user, 2026-08-16).
- [ ] **Existing derived criteria are not retroactively affected** (criteria only change via a shock,
      never by re-deriving - `/character` Step 4c/Step 6) but this does change what a *freshly derived*
      criterion looks like from here on, and may be worth a pass over already-derived
      `trusts`/`distrusts` fields to see whether any would read differently under the corrected model,
      once it exists.

## `/simulate` local-model driver for large-N stress runs (planned 2026-08-16, not yet built)

**Goal, user's own framing:** run `/simulate` at thousands-of-passes scale - both to afford volume no
commercial model API budget would cover, and to stress-test the mechanism itself with less reliance on
agents (most of the mechanical work is already scripted per Steps 2/3's Phase A/C and the design debrief
quoted there). Hardware: RTX 4070 Super, 12GB VRAM, 32GB RAM, Ryzen 7 5800XT. Ollama already installed
with `qwen3:8b`, `qwen2.5-coder:14b`, `mistral:latest`, `llama3.2:1b` pulled (see the Model-agnosticism
plan below) - **Mistral-Nemo-12B-Instruct-2407, the model chosen for this, is not pulled yet.**

**Key distinction from the Model-agnosticism plan above - this is neither Axis A nor Axis B.** Axis A
(point a local model at Claude Code's own tool-calling loop) already failed a real smoke test
(2026-08-08, below): three distinct failure modes (hallucinated tool calls, under-triggered real ones,
mid-conversation tool amnesia) across two models and two proxy paths, all pointing at the same root
cause - an 8-14B local model doesn't reliably hold together inside a harness shaped around Claude's own
tool-calling conventions. Axis B (switch to a model-agnostic harness like OpenHands) sidesteps that but
is a real, still-unbuilt repo restructuring. This plan sidesteps both by removing the local model from
any tool-calling loop entirely - it mirrors the pattern `-generate` mode's Step 4g/5g already established
(the one subagent in that mode returns structured content only; a script applies it), extended to cover
base/extended-mode Phase B, which today still has the Claude-dispatched subagent execute `/enact` Steps
5/5b/6 directly via real tool calls. Text/JSON in, text/JSON out, every `py scripts/lore/*.py` call stays
in a deterministic Python driver that always knows its own absolute paths - none of the three logged
failure modes have a tool-calling protocol to fail at in the first place. Whether this reduces the
urgency of the OpenHands pivot for `/simulate` specifically, or whether Axis B is still needed for other
skills that genuinely need a full local agentic loop, is open - not resolved here.

**Model choice: Mistral-Nemo-12B-Instruct-2407**, over `qwen2.5-coder:14b` (already pulled) and
`qwen2.5-14B-Instruct` (not pulled). Once tool execution is off the model's plate, the job is ~pure
two-character dialogue/roleplay plus a small structured judgment payload - coder specialization buys
nothing there and costs prose quality; Nemo-12B is well-regarded specifically for natural two-character
voice and fits the 12GB budget with headroom for context at Q4-Q6.

**Architecture agreed so far:**
- The local model's only job per pass: read the same brief `simulate_pass_brief.py` already produces,
  return one JSON payload - the scene (character-vs-character dialogue, natural stopping point) plus
  whichever judgment fields that pass's brief flags as open (reproduction name-blend, arc `about`/
  `needs`/`archetype`, optional contested-rival name, hearsay mutation/shock-resolution/drift decisions -
  the same four judgment slots Step 3's design debrief already enumerates as the only places a model's
  judgment belongs). Schema/grammar-constrained decoding (GBNF via llama.cpp, or Ollama's JSON mode)
  enforces the shape - not a model-specific concern, works regardless of which model is picked.
- **New script needed, `scripts/lore/`** (location confirmed by the user): an apply script mirroring
  `apply_language_layer.py`'s pattern but broader - Phase B today does the *full* `/enact` Steps 5/5b/6
  (hearsay mutation, shock resolution, drift, record update) via direct tool calls made by the dispatched
  subagent itself; this needs to become a script that takes the model's JSON and calls
  `record_hearsay.py`/`update_character.py`/etc. deterministically instead. Not yet designed in detail -
  see open questions below.
- **New standalone driver loop, also `scripts/lore/`** - can no longer be a Claude Code `Agent` dispatch
  (see above); a plain Python loop calling `simulate_pass_brief.py` -> the local model's API -> the new
  apply script -> `simulate_pass_resolve.py`, per pass, with checkpointing so a multi-thousand-pass run
  survives an interruption rather than losing progress. Not yet started.

**Orchestrator role, once this exists (discussed, not yet spec'd into the skill file itself): shrinks to
bookends, not per-pass dispatch.** The orchestrating model (Sonnet, or whatever this session runs on)
still owns Step 0/1's interactive setup (worktree preconditions, participants/pass-count/pool - genuine
judgment plus `AskUserQuestion`, can't be scripted away) and launches the driver loop - but no longer sits
in the loop per pass. What still needs a capable model, and doesn't shrink with pass count: **Step 4's
closing synthesis.** The tally script's output and the driver's structured pass log are just facts;
turning them into the required prose Narrative report ("the shape of it - steady, volatile, stalled,
resolved," "an honest account of what didn't happen") and any `LAB_REPORT.md` entry is a one-time
synthesis cost regardless of whether N was 50 or 5000, and nothing the mechanical driver output can
substitute for - this is the part of the current design that was never really about dispatching tasks and
logging results, it's the part where the run's outcome actually gets *read and understood*.
**Bonus structural simplification:** Step 3 point 4's git-leak safety net (the relative-path-resolves-
against-the-main-checkout bug, observed at roughly a 1-in-10 pass rate even under maximal prompt
hardening) becomes unnecessary by construction once tool execution moves into a driver script that always
builds its own absolute paths from a known worktree argument - the exact failure class it exists to catch
(a spawned Agent's cwd silently defaulting to the wrong checkout) can't occur without an Agent guessing at
its own cwd in the first place.

**Not yet decided / open questions:**
- [ ] Exact JSON schema for the model's per-pass response (scene-text field, each judgment field's shape).
- [ ] Whether the apply script is one file or split - mutation/shock-resolution/drift/record-update might
      not collapse into one call as cleanly as `-generate` mode's language layer did.
- [ ] How hearsay mutation and shock resolution - genuinely judgment-shaped, not mechanical - translate
      into a JSON schema the driver can apply verbatim, versus needing the driver itself to still make
      some interpretive choice (e.g. resolving `record_hearsay.py`'s exact argument shape from the
      model's freeform mutation description).
- [ ] Checkpointing/resume format for the driver loop across a multi-thousand-pass run.
- [ ] Whether/how this interacts with `-generate` mode's own single batched subagent (Step 4g) - could
      plausibly move to the same local-model pattern once the base-mode driver exists; not scoped here.
- [ ] Cross-reference to the Model-agnosticism plan above: does this reduce the urgency of the OpenHands
      repo-restructuring plan, or is that still needed for other skills? Not resolved.

## Rename `routines[].archetype`/`.specialization` - the field names read backwards (2026-08-16)

Surfaced auditing `/character` Step 8 with the user while hand-authoring Zarkatraz's routines. User's
read, and it's correct: `archetype` is the shared, generic place-type template (texture + `provides`,
identical for every character who has a routine tagged with it, authored once in
`_lore/archetypes.json`) - it's the *context* a routine happens in, not a personality or role.
`specialization` is the one-line personal grounding that makes a routine *this character's own* -
it's what the character actually *does* there, i.e. the routine's own action, not a trait. The current
names invert the intuitive reading (an "archetype" sounds like it describes the character; a
"specialization" sounds like a skill/role label, not a scene of concrete action).

- [x] **Rename `archetype` -> `context`, `specialization` -> `routine_actions`, done 2026-08-16.**
      `_lore/archetypes.json` renamed to `_lore/contexts.json` (old file deleted, content preserved
      plus a note on the rename); `/character` SKILL.md Step 8 and `/simulate` SKILL.md updated
      throughout; every script updated (`write_arc.py`'s `--context` flag, `simulate_pass_lib.py`'s
      `resolve_context_for_location`/`CONTEXTS`, `check_needs_provides.py`,
      `simulate_generate_population.py`, `simulate_pass_brief.py`, `simulate_pass_resolve.py`,
      `apply_language_layer.py`, `register_arc_concept.py`, `roll_death_legacy.py`,
      `generate_offspring.py`, `diagrams/gen_extended_mode_pass.py` + its generated
      `extended-mode-pass.html`); all 13 existing character files' `routines[]`/`arc` keys migrated
      (mechanical script, verified against JSON validity + diacritics after). **Two real bugs caught
      while doing this, not part of the original ask**: `simulate_generate_population.py` had its own
      *second*, separate death-legacy arc-copy implementation (parallel to
      `simulate_pass_resolve.py`'s) that was also missing `premise` entirely - fixed in both places.
      Every touched `.py` file passed a syntax check, a clean import, and (for `write_arc.py`) a real
      end-to-end run against Zarkatraz. `LAB_REPORT.md`'s historical dated entries deliberately left
      unrenamed - it's a run log, not living documentation; those entries describe the mechanism as it
      was named at the time, same discipline as not rewriting history elsewhere in this file.

## User design correction: `arc` should be authored at character creation, same as `routines` (2026-08-16)

Surfaced continuing the Zarkatraz audit into `/character` Step 8's second half. Current Step 8 text
treats `routines` and `arc` asymmetrically: `routines` is authored at character creation, always,
hand-authored, no exceptions stated. `arc`, by contrast, is explicitly deferrable: "A character with
no `arc` yet gets one authored the first time `/simulate`'s extended mode gives them primacy as
`home_frame` - this can be left blank here and filled in then, rather than forced at
character-creation time." **User's correction: this should be the same discipline as `routines` -
authored at character creation as the default, with `/simulate`'s first-primacy-win authoring staying
only as a fallback for a character that reached extended-mode play without ever getting one set.**

- [x] **Resolved (2026-08-28).** `/character` Step 2b item 4 and Step 8 both now state "Required at
      creation... not a deferred/optional step" — `arc` is authored in the same pass as `routines`.
      `/simulate`'s `arc_authoring_needed` path is explicitly reframed as the fallback "for a
      character predating this requirement... or one that arrived some other way," not the normal
      path.
- [x] **Resolved.** `/character` Step 8 calls `write_arc.py` directly (`py scripts/lore/write_arc.py
      <key> --about ... --needs ... --context ... --premise "..."`), same tool `/enact`/`/simulate`
      use.

## CRITICAL, user design correction: arcs have no persistent, concrete premise (2026-08-16)

Surfaced authoring Zarkatraz's arc. Checked directly, not assumed: `character.arc` holds only
`about`/`needs`/`archetype`/`resolution`/`history` - short tags, no prose field anywhere. The
`concept:` entry `register_arc_concept.py` writes into `encodings.json`'s `description` doesn't fill
that gap either - it's a templated sentence that just echoes the tags back ("`{name}`'s
`/simulate`-authored arc project (archetype: `{archetype}`; needs: `{needs}`). Resolution as of this
record: `{resolution}`..."), never a description of what the project concretely *is*. Net effect:
**nothing about an arc's actual premise survives past the conversation that invented it.** Whoever
plays a scene involving that arc later has to reconstruct its meaning fresh from four bare tags, with
no guarantee they land on the same idea twice - and even the prose the agent DOES compose in a given
authoring conversation (e.g. this session's first pass: "he's working toward a source he could stand
behind if pressed") tends to default to something abstract, which stays incomprehensible as a
"concrete project" even if it *were* saved verbatim.

**User's correction is two-part, both required:**

1. **Add a real, persistent prose field** - `arc.premise` (naming TBD) - written once at authoring
   time (character creation, going forward per the `routines`-parity fix above) and re-written only
   on a legitimate `transform`/re-author event, never drifting silently between those. This is the
   actual fix for "the arc changes depending on who's telling it," which should only ever happen
   through the tracked `transform` mechanism (`arc.history`, tally-gated) - never as an artifact of
   nothing being on record to stay consistent with.
2. **The premise must be concrete, not thematic.** User's worked example, replacing this session's
   abstract first draft: not "find a legitimate source for his stones" (a theme/tension, not a
   project), but "find a specific precious stone nobody else has found, and treasure it - a project
   with a real object, a real name, and a real possible outcome (his descendants inheriting it if he
   succeeds)." The stone needs an actual invented name, not a placeholder - **this is exactly the kind
   of texture-invention `/enact`'s own Step 2 already licenses ("personality, mannerisms, small human
   texture - invent freely") applied to arc premises specifically: the agent composing the premise
   should name the object/place/person involved, but stay within what's actually plausible given the
   character's own known knowledge/backstory** - the same "never invent as fact anything that
   contradicts or extends the lore itself" boundary `/enact` Step 2 already states, not a new rule,
   just applied to a spot (arc authoring) that currently has no such discipline attached to it at all.

- [x] **Resolved.** `arc.premise` is a real field now — 21 character files carry one — documented in
      `/character` Step 8.
- [x] **Resolved.** `write_arc.py --premise` is a required argument.
- [x] **New authoring guidance: concreteness bar for `arc.premise` — resolved, both rules present in
      `/character` Step 8 verbatim as "The resolution-moment test" and "Ground the target in something
      already known, when possible." **Diagnosed from a real failure, not hypothetical**: this session's
      first pass at Zarkatraz's arc ("find a legitimate source for his stones he could stand behind")
      read as abstract and had to be redone after the user pushed back - the fix (a specific named
      Órikal specimen, "la Lágrima de Balahm") worked, but nothing in the instructions would have
      caught the first version on its own; it took a human noticing. Two concrete, checkable rules
      worth writing into the instruction itself so this doesn't depend on being caught each time:
      1. **The resolution-moment test.** The premise must support one sentence describing the exact
         moment the arc resolves, success or failure (holds the stone / doesn't). If the honest answer
         is inherently gradual - "builds a better reputation," "improves his standing," "finds better
         sources over time" - it's still a theme wearing a project's clothes, not a concrete arc, and
         needs to be pushed toward an actual object/person/place/event with a sharp yes/no outcome.
      2. **Ground the target in something already known, when possible.** Prefer seeding the arc's
         central object/goal from something already present in the character's own drawn
         `knowledge.education.items` or the objective record (as done here: `concept: orikal` was
         already in Zarkatraz's sample) over inventing a target from nothing - an existing corpus item
         already carries real, checkable specifics (a name, a description, a status) for free, which
         is exactly what made the second attempt concrete and the first one abstract.
- [x] **Resolved.** `/character` Step 8: "On a `transform`... `premise` gets re-composed around
      whatever `about` the transform mechanically injected — same judgment-call moment as re-authoring
      a failed arc, not a separate decision."
- [ ] **Retroactive question, still open.** Checked directly: Aureobalo, Döran, and Khaoe still have no
      `arc.premise` on file. Not blocking, but the pilot characters haven't been backfilled.

## User design correction: `arc.premise` needs the same attribution discipline as everything else invented (2026-08-16)

Surfaced reviewing the drafted Zarkatraz premise (Órikal / "la Lágrima de Balahm"). Real problem
found, not a style nitpick: **every other invented/uncertain claim in this system carries a source and
a confidence status** - hearsay is always "X said Y," gets `traceable`/`untraceable` via
`lineage_coin.py`, and can be flagged `oral_lore`/`inconsistent_with_record`; a criterion's
`cost_ledger` and `about` field exist so nothing floats free of a source. `arc.premise` (the field
logged two sections above) was about to become the **one place in the whole system where invented
content just gets asserted as flat narrator fact, with no speaker and no traceability** - the actual
version of "sloppifying the story" the user flagged, not the specific content itself.

**The fix distinguishes two different things that were being treated the same:**

1. **Texture** (an invented name, a mood, a turn of phrase) - already licensed freely by `/enact`
   Step 2 ("personality, mannerisms, small human texture - invent freely"), doesn't assert anything
   checkable, stays safe to invent without attribution. Worked example: naming the stone "la Lágrima
   de Balahm" is texture - fine as-is.
2. **Claim-shaped content** (provenance, history, "it changed hands twice," "it's from his home
   desert") - a fact-shaped statement about the world, which everywhere else in this system gets a
   source. An `arc.premise` asserting one with no attribution is the actual gap.

- [x] **Resolved.** `/character` Step 8 rule 3, "Texture is free to invent; claim-shaped content is
      not," states exactly this distinction and phrasing.
- [ ] **New mechanism, user's own proposal: a "prone to rumor/embellishment" character trait.**
      Concrete, nameable trait (not vague color) a character can carry, marking them as a legitimate
      in-world source for unconfirmed/embellished claims - gives invented texture a real causal origin
      (a specific unreliable narrator) instead of floating free, mirroring how folklore already spreads
      through this system's hearsay mechanism. Real precedent already exists informally: Sonoros
      already relays an unconfirmed claim without vouching for it
      (`hearsay: sonoros_lost_traveler#5` - "Sálthos Cruzados is rumored to be the biggest town...
      Sonoros does not confirm this, only reports the rumor") - this trait would formalize that
      existing pattern into something explicitly flaggable on a character file, rather than something
      that just happens to read that way in one dialog. Not built - where the trait lives
      (`knowledge`? a new top-level field? `backstory` prose alone?) and how it interacts with
      `lineage_coin.py`'s traceable/untraceable roll are both open, not decided here.

## Bug: a completed arc never gets replaced - asymmetric with the failure path (2026-08-16)

Confirmed by reading both places arc resolution is computed - `simulate_pass_brief.py` (interactive
driver) and `simulate_generate_population.py` (`-generate` mode) - identical logic in both, so this
isn't a one-off. Arc processing for a pass only runs at all when `arc.get("resolution") == "ongoing"`.
When the tally crosses the *negative* threshold with no `matched_about` available, `resolution`
becomes `"failed"` and `arc_authoring_needed`/`queue_arc(..., "reauthor_failed", ...)` fires in the
same pass, immediately queuing a replacement. When the tally crosses the *positive* threshold,
`resolution` becomes `"complete"` - and nothing else happens. No branch anywhere checks for
`"complete"` and queues a fresh arc; the `elif ... == "ongoing"` guard means a completed arc is simply
never touched again, forever, in either the interactive driver or `-generate` mode. **User's
correction: a character who successfully completes their arc should get a new one authored, the same
as a character whose arc fails - completion isn't a valid reason to stop having a project.**

- [x] **Resolved.** Both `simulate_pass_brief.py` and `simulate_generate_population.py` now fire
      `queue_arc(..., "reauthor_complete", ...)` on the `score >= ARC_RESOLUTION_THRESHOLD` branch,
      mirroring the failure path, and `prior_arc` is passed for continuity in both. Checked
      `roll_death_legacy.py`: it copies a deceased's `about`/`needs` tags onto a recipient regardless
      of the source arc's own `resolution` value and simply resets the recipient's copy to `"ongoing"`
      — no assumption found that a source arc must be `"ongoing"` at copy time. Since `reauthor_complete`
      reuses the same `arc_authoring_needed` slot as `"first"`/`reauthor_failed`, it inherits the
      resolution-moment/grounding/attribution rules by construction, per `/character` Step 8.
- [x] **Resolved.** `/enact`'s SKILL.md now states it explicitly: "'advance' and 'complete' are not
      staged the same way... A 'complete' outcome... has to depict the arc's own object/goal actually
      being obtained or resolved *within this one scene*... the culminating action itself... plausible
      as a single-sitting resolution."

## Grounding: mod-sourced mechanics, deferred until a mod is actually added (2026-08-26)

`_lore/grounding/mechanics.json` (design + schema this session, see `_lore/grounding/_index.md`) is
being populated with vanilla Minecraft 1.20.1 mechanics. When mods eventually get added to the
datapack, their own mechanics (new mobs, new crafting, new survival systems) should get added here
too - tagged distinctly from vanilla content so a character's grounding can be scoped to which mods
are actually active in their world, and the vanilla baseline stays swappable/comparable on its own.
Not urgent - no mods are in the datapack as of this entry - flagging now so it isn't rediscovered as
a gap later.

- [ ] Decide the tagging scheme for mod-sourced entries once the first mod's content actually needs
      adding (extend `embodiment` to something like `"minecraft:modname"`, or add a separate `mod`
      field alongside it - not decided, don't guess when the time comes).

# Chronicle

**Purpose.** This is the project's own memory of itself — the landmarks in the conversation that's
been building Luminacion, session to session, kept somewhere durable instead of only living in chat
history that eventually ages out, gets compacted, or simply isn't retrievable across machines. Not a
transcript, not a diff log (`git log` already does that) — the *why* behind the *what*: decisions
made and the reasoning behind them, arguments that shifted the design, things learned the hard way,
and open questions that were live at a given point, even ones later settled elsewhere.

**How to use this file.**
- Not every session needs an entry. Add one when something landmark happened: a design decision, a
  changed mind, a real disagreement and how it resolved, a surprising result, a new open question. A
  session that was pure execution of an already-settled plan doesn't need one.
- Keep entries short — a few lines to a short paragraph, not a full recap. This is a spine of
  landmarks, not thorough documentation; that's what the rest of the repo is for.
- An open question logged here that's actionable also belongs in `TODO.md` or, if it's a
  `/simulate`-design question, `LAB_REPORT.md`'s **Open design questions** — this file just notes
  *when and why* it came up, those files track it to resolution. Don't duplicate the tracking, just
  point to it.
- Newest entry at the top.

---

### 2026-09-13 — Full lore-schema cleanup ahead of the next simulation; grounding, travel, and provisions sketched

A long architecture-tightening pass, prompted by the standalone branch having accumulated entropy
across several earlier sessions' schema changes — stale references, split categories that had never
actually been merged, documentation describing structure that no longer existed. Went through
`_lore/` folder by folder rather than fixing things as they were tripped over.

**`encodings.json` rebuilt from scratch, deliberately lean.** Flattened the old split categories
(`character_legendary`/`character_real`/`inhabitant` → one `character`; four route sub-types → one
`route`; four time-system sub-types → one flat `time_systems`) and stripped the file's own method
notes down to only what an agent deciding where to encode something actually needs — everything else
(sampling mechanics, hearsay consistency tracking, tale-folding rules) moved to `/integrate`'s
`SKILL.md` or the relevant folder's own `_index.md`. Real design tension, resolved: whether categories
should carry a generic `references` field so related entries (a character, their home city, an era)
point at each other. Rejected in favor of **named, specific fields** (`character.origin`,
`route.endpoints`) wherever the relationship is a real attribute, keeping a generic `about` field only
for the "claims" layer (`hearsay`, `tale`, `conflict`), where an entry isn't itself an object with
named attributes — it's inherently a statement *about* other things. The deciding argument: a generic
reference field risks turning "sample one character" into "sample their whole neighborhood" by
cascade; a named field is just an ordinary attribute, sampled or not like any other, and lets deliberate
skewed sampling (e.g. "bias toward Terfila") work as a plain filter instead of a graph traversal.

**Two identical naming collisions found and fixed the same way.** `sources[].origin` (which document)
collided in name with the new `character.origin` (birthplace) — renamed to `sources[].document`.
Later, `criterion.origin` (an enum: `derived`/`uncollided`/legacy `inherited`) turned out to collide
with the same `character.origin` — renamed to `criterion.derivation`. Same lesson both times: `origin`
is an overloaded word in this schema and should probably be avoided for any new field going forward.

**`contexts.json` cut from 16 hand-authored place-types to 5** (`market`, `temple`, `commons` —
renamed from `street`, since the intent was always generic public space, not literally a road —
`home`, and `route` — renamed from `transit`), explicitly as a minimal shippable seed, not a ceiling.
`provides` cut at the same time from a dozen loosely-motivated tags down to 6 (`materials`, `items`,
`transit`, `nourishment`, `records`, `news`), majority-concrete over epistemological on purpose — the
mechanic that will actually consume `provides` values doesn't exist yet, so the tag vocabulary was
built to be minimal and legible rather than speculatively complete.

**Grounding clarified as the ontological counterpart to encodings' epistemological record** —
sharpens the existing Troy distinction (material is the claim, grounding is the ruins) into a working
split: `encodings.json` (fed by material/tale/hearsay) is *what's known*; `_lore/grounding/` is *what
is*, independent of anyone's belief. `mechanics.json` (the world's "laws of nature") turns out to serve
two purposes, not one — propositional rules *and* vocabulary grants (naming a concrete material like
"cobblestone" so a character can refer to it instead of a generic placeholder) — logged as needing a
third, causal/recipe shape (an item requires specific materials) before arc resolution can check
anything more specific than an abstract category (`TODO.md`). Built the simpler pieces now: a
character's `places_visited` accumulates (routine locations plus one-off visits, per `/enact`'s own
home-vs-visiting mechanic), gating `world_state.json` access — corrected mid-design from an initial
"current scene location only" proposal, since knowing what a place *looks like* should require having
actually been there, not just currently standing in it. `world_state.json` itself is the one place in
the whole system where mutation-in-place, not accumulation, is the right discipline — it's a snapshot
of the world's current state, not a record of claims about it.

**Travel system sketched, not built** (`TODO.md`) — and it turns out `_lore/encodings.json`'s
`route.endpoints` field was already shaped, on purpose, to double as the travel graph's edge list; the
`route` context (one of the 5 above) is the natural shape for enacting a single hop. Reachability
isn't just "adjacent to where you are" — a character can also reach anywhere adjacent to somewhere
already in their own lore pool, so what a character knows extends how far they can go. The actual lever
this unlocks: arc requirements currently check `provides` too abundantly to create real scarcity;
gating some arcs to a *specific place's* context, not just any context that happens to provide the
right tag, is what would make travel mechanically necessary rather than decorative.

**A personal provisions/inheritance economy was sketched** (`TODO.md`), triggered by a good pushback:
initially proposed as a personal resource separate from the location-level survival pool (renamed
`wealth` → `provisions` in the same conversation, to stop "wealth" colliding with this new personal
concept before it existed), but corrected to be the *same substance held at two scopes* — a personal
reserve a character earns by completing an arc, can pass to children, and can draw on instead of the
communal pool, rather than a second, differently-named resource. Framed against Bourdieu's three
capitals as an explicit organizing lens, not just decoration: cultural capital is already built
(`knowledge.education`/`experience` gates arc possibility and, per the travel sketch, reach);
social capital is partially built (`partners`, and now a persistent `social_circle` field, update
mechanism deliberately left undecided); economic capital is this new provisions system, not built at
all yet. Character pairing being effectively random right now, versus intentional based on the same
arc-pursuit calculus, was flagged as a related but separate open item.

**Workflow shift, mid-session:** moved from doing the file edits directly to orchestrating — deciding,
reviewing, and delegating well-scoped implementation to subagents, keeping the main thread for
judgment calls and cross-checking their work rather than the mechanics of each edit.

### 2026-09-12 — Talk of the Town comparison; sharpened "seed vs. rules" into "closed rules vs. interpretation"

Continuation of the same day's reflective conversation (see the entry below). The user independently
named Talk of the Town (James Ryan, UC Santa Cruz Expressive Intelligence Studio) as a comparison —
a research project simulating a town's gossip/belief propagation, with every character's belief fully
provenanced back through the conversations that produced it, structurally close to this project's
hearsay/trust-distrust/`produced_by` layer. It never shipped as the intended open-ended town game;
what did get built and played was `Bad News`, one bounded scenario riding the same engine. Talk of the
Town's mechanism is pure closed-form logic throughout, including dialogue generation — no model doing
semantic judgment anywhere, which if anything makes it more mechanically DF-like than this project.

**Real correction, from the user's own pushback:** the "authored/procedural seed vs. content seed"
framing drawn in the entry below was too clean, and so was a first-pass "semantic content vs. rules"
distinction floated in this same conversation — a dice roll and a model's dramatization are both rules
in the loose sense (functions from input to output). What actually separates them is **closed and
enumerable vs. open and underdetermined**: a dice roll or arc-gate threshold produces one determinate
output given a fixed input and seed, and "correct" just means matching the rule; the dramatization/
hearsay-mutation layer doesn't work that way — the same brief handed to the same model twice doesn't
have to produce the same scene, and there's no sense in which one dramatization is *the* correct
unfolding of the mechanical facts and another is wrong. The user named this a hermeneutics question
unprompted, and that's the right frame — closer to Dilthey's *erklären* (explaining via closed causal
law) vs. *verstehen* (understanding via situated interpretation) than to "rules present or absent."
Concretely, this is what `measure_divergence.py` is already instrumenting without having been framed
this way: two runs off the same seed stay identical wherever the closed rules did the work, and
diverge wherever interpretation touched the outcome — the divergence measurement is a real, running
proxy for the ratio of *erklären* to *verstehen* in a given run, not just a bug-check on RNG discipline.

This also sharpened the "machine-generated seed" TODO item logged the same day: the seed's *nature*
(semantic content, not a generative rule-set unfolding into content) is a separate question from
whether *processing* that content is rule-governed — both are, in the loose sense — so the TODO's
"rules vs. content" wording got tightened to "closed rule-set vs. content" to keep the two questions
from collapsing back into each other.

### 2026-09-12 — Rescued the orphaned Ollama/simulate-driver/test-suite architecture; clarified the playability horizon

Two worktree branches carrying real, never-merged work (the Ollama local-model enacter, the
`simulate_driver.py`/`pass_prep.py`/`pass_apply.py` orchestrator split, the survival-mechanism
redesign, and the whole `scripts/test/` measurement suite) had been deleted without merging. Found
`origin/provenance-bare`'s own copy of the enacter was an earlier, already-superseded version; the
true latest state was sitting only as an unreachable local commit (dangling, one `git gc` away from
gone). Pinned it to a branch, then ported the architecture only — not the 237 `_lore/character/*.json`
files or other content that branch's own test population carried — via a 3-way merge against the two
branches' common ancestor, hand-resolving the handful of real conflicts (`simulate/SKILL.md`'s Step 3,
where both branches had independently redesigned it the same way but only this branch went on to build
`simulate_record_run.py`'s LAB_REPORT.md auto-templating). See the `integrate-ollama-architecture`
merge commit for the full inventory of what came back.

Also had a long reflective conversation, prompted by the user independently noticing a resemblance to
Dwarf Fortress despite never having played it — worth recording since it clarified something about
where this project is actually headed, not just what it's built so far. The resemblance isn't in
mechanics (DF's granularity is physical/mechanical; this project's is epistemic — what a mind knows,
believes, trusts, not what's physically true) but in the *relationship between player and simulation*:
a world that keeps running its own routines whether or not anyone's standing in it, where stepping in
adds a participant rather than pausing the clock. The user's own two use cases — `/simulate` as a pure
narrative-drift generator, and eventually walking into a live Minecraft world as one more actor in an
already-running simulation — turn out not to need different mechanisms: `/enact` character-vs-player and
character-vs-character are already the same primitive with a different second participant. **Decided:
don't change how `/simulate` works right now** — the project is still in the engine-validation phase,
proving the drift/immersion properties hold up cheaply and offline (the test suite above is exactly
that evidence) before investing in a live, standing world. But the local-model dispatch work isn't just
a batch-cost optimization for that testing phase — it's close to a precondition for the eventual
always-on embodied version, since a world meant to run indefinitely with NPCs acting on their own can't
depend on per-token API latency for scenes nobody's watching. Open question, logged in `TODO.md`: what
signal on the test-suite instruments (derivation coverage, felt contingency across many seeds,
surprising arc outcomes) would actually mark the transition from "keep testing" to "build the standing
world" — there isn't one yet, and without picking one the validation phase risks never having a natural
exit.

### 2026-08-30 — `survival-arc-test`'s round-2/round-3 architecture work merged in (this branch)

`survival-arc-test` had a real, never-committed 21-pass pilot of the survival mechanism sitting
uncommitted, plus genuine engine improvements found while running it. Ported the architecture only,
not the pilot's own character/scene data (per the user's explicit instruction): three new driver
scripts (`pass_prep.py`, `pass_record.py`, `pass_apply.py` — the token-efficiency pattern
`LAB_REPORT.md` describes as "written ad-hoc, never promoted," rebuilt for the current, larger
mechanism), a bug fix in `simulate_pass_brief.py` (the primacy winner's energy was silently getting
reverted on every gate-hit pass), a pool-exhaustion fix in `apply_survival.py`/`wealth_lib.py`
(`arc_extra_cost_scarce`, a wealth-trend input `scarcity_pressure` for `roll_survival.py`), a dedup
bug fix in `generate_offspring.py`, the retuned `tuning.json` values a real 50-pass playtest
surfaced, a house-wide principle in `PRINCIPLES.md` ("script everything that can be scripted; prose
only where a judgment call genuinely needs it"), and a full redesign of `/simulate` Step 3: the
orchestrator now runs every mechanical script itself and dispatches a subagent only to write scene
text with no tool access at all, eliminating the relative-path-leak failure class entirely.

This branch's own `simulate_pass_brief.py`/`roll_survival.py`/etc. turned out to be byte-identical to
`survival-arc-test`'s own base commit (it branched directly off here, and nothing here had touched
these particular files since) — so unlike the equivalent port to `provenance-bare` earlier today
(which needed hand-merging against that branch's own test-suite work touching the same files), this
was a clean, direct application of the worktree's own diffs, verified via `git diff` against
`survival-arc-test`'s base commit coming back empty for every target file before copying. `TODO.md`'s
matching debrief notes applied the same way, via `git apply` against the same clean base.

Not ported: the pilot's actual character files, scene transcripts, and pass-by-pass decision/hearsay
logs — that data stays in the `survival-arc-test` worktree, untouched. `LAB_REPORT.md` is unaffected
here (this branch keeps the real one; only `provenance-bare` dropped it, being the engine-only line).

### 2026-08-28 — Survival mechanism built on `survival-arc-test`

Implemented the mechanism designed earlier the same day (see the entry directly below) on the new
`survival-arc-test` branch, off `provenance-standalone`. New: `wealth_lib.py` (shared pool I/O,
`_lore/wealth.json`), `roll_survival.py`, `apply_survival.py`, `apply_upkeep.py`. Modified:
`roll_home_visit.py` (now skewable by survival choice), both `simulate_pass_brief.py` and
`simulate_generate_population.py` (survival rolled before home/visit, applied after location
resolves, arc-outcome gated on the primacy winner having actually chosen "arc," needs/provides gated
on location wealth), `simulate_pass_lib.py` (new wrappers), `_lore/tuning.json` (a new `survival`
block, every value a first guess same as everything else in that file).

One real change from the design conversation: swapped the sketched sigmoid for a percentage-point
shift off a 50/50 base, clamped [2, 95] — matches `roll_contested.py`'s existing unit and idiom
rather than introducing a new one, same math shape, simpler to read and tune.

Verified end-to-end against the real Tyrnea cast, not template data — ran `simulate_pass_brief.py`
and a short `simulate_generate_population.py` batch directly, watched a real starvation death fire
correctly (tale written, `life.deceased` set, notified circle computed) and the arc-gating/wealth
threshold both behave as designed, then reverted every test-mutated character/lore file before
committing so the branch starts clean for the user's own first real run. Nothing tuned yet - weights,
thresholds, and costs are all exactly what the design conversation guessed, untested at scale.

### 2026-08-28 — Survival mechanism designed end-to-end (not yet built); `provenance-bare`'s causal-reorder and social-relations work folded into `provenance-standalone`

Long design conversation, working from the user's own rough sketch (locations have an energy pool,
characters spend/replenish it, choosing between "survive" and "follow an arc") through to a complete,
tunable mechanic — see the full spec now logged in `TODO.md`'s "Survival mechanism" section. Landed on
this branch specifically because it needed folding onto real characters (Tyrnea's 12-character revival
cast, already committed here) for `survival-arc-test`, a new branch off this one, to test against.

**Real gaps the user caught mid-design, each one changing the shape of the final mechanic:**
- The first draft's "survive" math was a wash (−1 base, +1 taken back = net 0 forever) — not a bug,
  but nothing was pulling a character toward the costly arc branch instead. Fixed by making the
  choice a weighted roll (matching the project's existing `inclined`/`contested` pattern) instead of
  free will, and by giving the pool per-capita upkeep so it can actually run dry.
- "Provides" (the existing needs/provides gate) needed a concrete threshold, not a vague "enough" —
  landed on per-capita surplus above subsistence, and on arc-following actually drawing from the pool
  too (previously it didn't touch the pool at all), so a starved location's inability to provide has
  real teeth.
- Population-wide per-pass energy resolution would have been expensive *and* semantically broken
  against arc primacy (most rolls would never see a scene at all). Fixed by scoping energy resolution
  to only the characters actually drawn each pass — same lazy-clock precedent `horizon.py` already
  uses — with a losing arc-bet still costing the full price, deliberately, as real stakes rather than
  wasted bookkeeping.
- Social connectedness was being asked to pull toward both *obligation* (survive) and *reliance* (safe
  to gamble) through one raw strength number — split into two roles for one signed `net_affinity`
  value (`Σquality / Σstrength` across established partners) once the actual bond-quality system's
  real field names were checked, rather than assumed.

**Also folded in this session:** `provenance-bare` had independently built two more rounds of engine
work since the last sync — a `/simulate` Step 4 causal reorder (see the entry directly below) and a
social-relations system (`partners_quality`, relationship inheritance, `social_circle.py`,
relationship-aware `contested` odds) — merged into this branch, corpus preserved, same
most-recent-wins-with-real-review approach as the earlier architecture reconciliation.

### 2026-08-28 — `/simulate` Step 4 causal reorder: primacy, location, and reproduction timing all shift (implemented)

User hand-redrew the repo's own auto-generated `diagrams/simulate-pass.html` in Coggle, reordering it
for a reason: wants "more consequential logic" connecting the mechanical roles, which currently run
almost independently of each other. Pulled the diagram's exact structure via Coggle's text-outline
export and diffed it against the real execution order in `simulate_pass_brief.py`/`simulate_pass_lib.py`
to separate genuine reorders from mind-map grouping artifacts.

Confirmed with the user as real design, then built the same session:
- **`contested` now skews `arc-outcome`'s odds, never decides it outright** — the two rolls used to be
  fully decoupled (`roll_contested.py` a flat independent 15%; `roll_arc_outcome.py`'s weights came
  only from `inclined`). Fixed with the same "shifts odds, doesn't decide" pattern the code already
  used for help/hinder: a new `--contested` flag shifts `contested_outcome_shift` (20, `tuning.json`)
  points from advance to reverse.
- **Home-vs-visiting decided first, via a new flat coin-flip roll** (`roll_home_visit.py`) — the
  user's final correction on the first design pass (which had this weighted by leads/arc-needs):
  right now it's genuinely random, full stop. Only the home participant rolls a routine
  (`roll_routine.py`, called once); the visitor just enters whatever context that produces — this
  also retires `resolve_location.py`'s old "coincidence" mode outright, since there's no second
  independently-rolled routine left for it to coincide with. An unexpired lead still overrides the
  roll entirely, as before. Survival isn't built yet, so the odds stay flat on purpose — logged the
  hook in `TODO.md` rather than faking the mechanic.
- **Arc primacy decided after that, independently of who traveled** — the visitor's arc can still be
  the one that leads the scene. Needs/provides, contested, and the alignment gate all key off
  whichever arc primacy actually picked, not "the traveler's" arc as before.
- **Reproduction moved to the end of the pass**, via a new post-scene script
  (`simulate_pass_reproduction.py`) instead of running pre-scene inside `simulate_pass_brief.py` — user
  accepted the consequence that a birth can no longer be dramatized inside that scene's own dialogue;
  it gets a short coda after instead.
- `record_partner.py` moved up to run right after pairing (unconditional the moment a pair is drawn).

**Caught mid-implementation:** `simulate_generate_population.py` (the `/generate` mass-pregeneration
driver) turned out to be a full parallel reimplementation of this same pre-scene logic, including a
direct call to the now-deleted `resolve_location()` — would have silently broken `/generate` if left
alone. Reordered it identically and de-duplicated its reproduction-eligibility check against the new
`simulate_pass_reproduction.py` (threading its `ancestor_cache` through, so the 2026-08-17 perf fix for
long runs wasn't lost).

Touched: `roll_home_visit.py` (new), `simulate_pass_reproduction.py` (new), `resolve_location.py`
(deleted), `roll_arc_outcome.py`, `check_needs_provides.py`, `simulate_pass_brief.py`,
`simulate_pass_lib.py`, `simulate_generate_population.py`, `_lore/tuning.json`, `/enact` SKILL.md
Step 4 and a new Step 8 point 8, `diagrams/gen_simulate_pass.py` (regenerated). Verified by
compiling every touched file and smoke-running the two new scripts standalone — not by an actual
`/enact`/`/generate` run against real character data.

**Still open:** the pre-scene `horizon.py` band check (`/enact` Step 1) remains undiagrammed, and the
exact shape of the survival-mechanism weighting (once that system exists) is still just a `TODO.md`
note, not a design.

### 2026-08-28 — provenance-bare/provenance-standalone architecture reconciled; two independent chronicle mechanisms collapsed to one

`provenance-bare` and `provenance-standalone` had been diverging in isolation, each session unaware of
the other's branch — VOICE.md, the three-tier README reframe, and a session-chronicle mechanism had
all been built *twice*, independently, with real (if small) differences each time. Went through both
branches file-by-file rather than trusting either one wholesale: merged bare's trailing three-tier/
Provenance-rename commits into standalone (one real conflict — bare's tier-reorg had duplicated the
`_lore/` doc bullet with stale pre-origin/location-split content, dropped in favor of standalone's
current one), then reconciled the older architecture backlog (skills, scripts, PRINCIPLES.md,
settings.json) by taking whichever side's version was the more complete, more recent evolution.

The one genuine judgment call: bare had built `conversation.md` (2026-08-28) as its own session-
chronicle file, unaware that standalone already had `CHRONICLE.md` + a `chronicle-nudge.sh` Stop hook
doing the same job a day earlier (2026-08-27) — and that this very file's own header already recorded
having absorbed `conversation.md`'s content and declared itself the survivor. Honored that
already-recorded decision over a raw timestamp comparison: retired `conversation.md`, standardized
both branches on this file and the hook. `TODO.md`/`LAB_REPORT.md` were deliberately left un-reconciled
— `conversation.md` documented that bare intentionally ships them stripped for a lean checkout, a
per-branch content difference rather than architecture drift, same category as the lore corpus itself.

Also verified the "172 characters staged for deletion" open question logged just below (2026-08-28
entry): turned out to be a resolved non-issue — `provenance-standalone` currently holds all 86 expected
character files intact.

Talked through the README §0 diagram out loud: the old "Foundation/Supporting/Datapack/Resource pack"
4-layer split conflated inert content with the process that acts on it, and split shipping across two
layers that are really one export. Reframed as three tiers — **Content** (`_lore/`), **Handlers**
(skills + scripts + the templates/registries they share), **Shipping** (datapack + resource pack) —
and rewrote §0's prose/diagram plus `graphifyish.py`'s concept-graph layer defs to match. Also started
a `Luminacion` → `Provenance` branding sweep (the project's old name), scoped to human-facing text —
`pack.mcmeta` descriptions, script/skill docstrings, in-game chat prefixes, release zip names — while
deliberately leaving the lowercase `luminacion` Minecraft namespace (`data/luminacion/`, `luminacion:`
function calls, `resourcepacks/luminacion/` junction) untouched, since that's load-bearing for the live
world and this repo's own folder name.

Mid-sweep, discovered the checkout wasn't the clean `provenance-bare` state the session opened on: it's
actually on `provenance-standalone-merge-bare`, mid an unresolved merge of `provenance-bare` into it,
with 5 real conflicts (`PRINCIPLES.md`, `VOICE.md`, `TODO.md`, both `graphifyish` outputs) and — far
more alarming — 172 `_lore/characters/*.json` files staged as deletions. Unclear whether that's
intentional (building a lore-stripped template branch) or a merge gone wrong; also explains why several
edits this session weren't persisting to disk. Paused all further changes and asked the user to
confirm — **open question, unresolved as of this entry.**

### 2026-08-27 — Grounding, and why it alone won't fix epistemology dominance

Long dialogic session about the standing "everything reads as verification/epistemology" complaint.
Pushed past the corpus/backstory explanation to a mechanism point: arcs and shocks both still route
through `criterion`, so new content alone can't change the throughline unless it also feeds criterion
derivation itself — genuinely undecided, not resolved this session.

Built grounding anyway (`_lore/grounding/`) as a worthwhile axis on its own: objective, access-gated-
by-routine content, distinct from facts (universal) and material (a claim that may not be true — the
Troy distinction). `mechanics.json` got an exhaustive vanilla-1.20.1 pass (63 entries, wiki-verified);
`world_state.json` waits on an external region-file/vision pipeline the user is building in parallel.
Committed.

Also scoped, not yet built: reflection (three forced triggers — shock, death-notification, a
passes-since-last-one cooldown — plus its own arc-outcome roll, not just solo narration) and a
missing object/possession layer (characters exchange things in scenes with zero persistent trace,
which is what the "dice feels meaningless" complaint actually turned out to be about).

---

### 2026-08-27 — Author's voice, and this file

Started from a question about whether I retain any sense of how the user actually talks, for
writing README/docs prose in their register rather than default assistant prose. Answer at the
time: no — nothing existed to capture that. Built `.claude/VOICE.md` for it: a project-wide, dated,
accumulating list of the user's actual verbal patterns (not a generic "casual tone" description),
wired into `.claude/PRINCIPLES.md` and a new root `CLAUDE.md` so it applies to every agent/session
in this repo, not just one conversation's personal memory.

That led to the same question one level up: is the *conversation itself* — the argument-by-argument
journey of the project, not just the docs voice — retrievable across sessions? Checked: session
transcripts exist locally (`~/.claude/projects/.../*.jsonl`) but aren't a real answer — local-only,
not git-tracked, not something to rely on as the project's record. This file is the fix, modeled on
`LAB_REPORT.md`'s existing pattern (a durable, append-only run log that survives any single
conversation's context) but for the project's decisions/arguments generally rather than `/simulate`
runs specifically.

That open question — how to make appending to this file actually happen reliably, given plain
written instructions can't force it — got resolved same-session: a `Stop` hook
(`.claude/hooks/chronicle-nudge.sh`) now nudges once per session, only when the transcript looks
substantive and `CHRONICLE.md` doesn't already have uncommitted changes, blocking-with-reason so I
get the chance to actually check and append rather than just showing the user a message. Known gap:
the "already touched" check is `git diff`-based, which can't see edits to `CHRONICLE.md` until after
its first commit (it's currently untracked).

---

**Backfilled below: `provenance-bare`'s `conversation.md` Landmarks, folded in here during the
2026-08-28 `provenance-bare` → `provenance-standalone` merge** (see the 2026-08-28 entry above) —
`conversation.md` covered the same "project's own memory of itself" role as this file, independently,
on that branch; rather than keep two competing chronicles going forward, its history moves here and
the file itself is retired. Reordered newest-first to match this file's convention; original entries
otherwise unedited.

### 2026-08-26 to 27 — Provenance, `/start`, and folding extended mode into `/enact`

The project renamed itself from Luminacion to Provenance in the README, leading with the engine rather
than Minecraft. `/start` shipped as a live welcome banner for a fresh checkout. `/simulate`'s extended
mode — until now an optional branch — became the only mode: `/enact` against another character now
always requires routines+arc and always runs the mechanical layer first, with no more freeform
fallback for an incomplete pair. This is also when voice dictation + TTS got wired up for this
project, and when `.claude/VOICE.md` (this branch's own, now superseded above) got built — a direct
response to noticing the README and docs didn't sound like the person building them.

### 2026-08-16 to 17 — Provenance rework, genealogy bugs

Criterion's trust/distrust derivation moved from a hardcoded per-category flag to resolving
mechanically off an anchor's actual source provenance. A 2000-pass `-generate` run then surfaced real
bugs in the reproduction mechanism itself (criterion copied verbatim instead of re-derived, arcs
converging onto ~25 signatures, an unbounded placeholder-slug growth that crashed a deep lineage) —
each one fixed and logged rather than the run just quietly discarded.

### 2026-08-10 to 13 — Extended mode, Runs 2 and 3

The redesign added routines tied to a real place-type archetype, arcs with progressive state
(primacy, gate, outcome, transform), reproduction, and death legacy — the governing rule for the whole
build: minimize the subagent's judgment, so almost every per-pass decision became a script, a dice
roll, or arithmetic, leaving only scene-prose and a newborn's name-blend as genuine model calls. Run 2
piloted it on 6 characters, then got extended in place seven more times up to 305 passes on direct
request rather than as separate runs — and it delivered exactly the material stakes Run 1 was missing:
arcs that stalled, reversed, transformed, and resolved on real dice rather than smooth convergence;
four generations of births; deaths that triggered genuine criterion shocks; one arc that stayed open
for 148 passes before resolving. It also surfaced a real string of bugs worth remembering because of
what they say about the system's own blind spots: an accent mismatch ("Ilaría" vs. "Ilaria") silently
broke an entire character's death-notification circle for 115 passes before anyone noticed; hearsay
was never actually folding back into the concepts it referenced, because `/simulate`'s own recurring
arc topics had never been registered as real `encodings.json` entries — the corpus looked like it was
accreting when 325 of 331 references were silently going nowhere; a scene-transcript filename
collision quietly overwrote earlier dialogue four separate times before a collision guard existed.
Each was root-caused and fixed. Run 3 then validated `/generate` (300 mechanical passes, zero scenes)
as a genuinely faster path to a starting population, at the cost of not testing drift itself — why
`/generate` and `/simulate` stayed two separate commands.

### 2026-08-05 to 09 — `/simulate`, Run 1, and the unattended-run problem

`/simulate` was born to batch `/enact` across a population, run inside a disposable worktree so a
stress-test run couldn't touch real files. Run 1 (97 passes on 5 characters) delivered real, unchosen
material consequence — 4 natural deaths, a keeper network that structurally collapsed as the
population shrank — but also the diagnosis that mattered most: nearly every scene still orbited the
same one conflict (multiplicity vs. singular truth), because routines at that point were bare
`{location: weight}` pairs with no authored practice behind them, and arcs were auto-derived from a
character's existing criterion anchor instead of from what they actually did somewhere. Content
converging like that was structural, not a prompting problem — it's what led straight into the
extended-mode redesign above. Separately, what actually ate the most *time* in this stretch wasn't the
simulation design at all — it was getting a run to survive unattended, overnight, with no permission
prompts: worktree settings written before `EnterWorktree` instead of after, a relative-path leak that
silently wrote real scene content into the main checkout, `cd`-in-Bash hard-blocked with no override.
Each got documented as its own fix rather than papered over, since the failure mode kept recurring in
slightly different shape until it was actually root-caused.

### 2026-07-30 to 31 — Tale, fact, and criterion

`/tell` and `/discover` (later merged into `/tell`) split off a third and fourth source of truth
alongside material and hearsay. The criterion mechanism got designed in real time across one long
session — negative derivation, anchors, the will to live, shocks vs. drift — settling most of the
shape it still has today. Also the first fully bilingual enactments (Khan Icé, la Feria del Milenio,
Gok, Bardaglis, Auroboro III) — the in-character register `.claude/VOICE.md`'s original "world voice"
section was built from.

### 2026-07-24 to 25 — Cold start

First commits: hearsay, the gesture rig, `/character` as a lighter sibling of a full enacted scene.
The gesture work in particular ran through a lot of in-game trial and error (an elbow joint that
wouldn't compose with its parent bone, a shared timer that broke once more than one NPC could gesture
at once) before landing on what's in `GESTURES.md` now.

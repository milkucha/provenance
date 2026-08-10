# /simulate Lab Report

**Purpose.** `/simulate` batch-runs `/enact` scenes to test whether this system's design actually
produces what it's meant to: emergent, materially-grounded lore-drift, not just mechanically-correct
but dramatically repetitive record-keeping. This file is the persistent, core-repo record of that
test across runs — deliberately *not* inside any worktree, so it survives past any single run, any
single conversation's context window, and any single agent. A fresh session or a different agent
should be able to read this file alone and pick up the thread: the standing hypothesis, what's been
tried, what worked, what didn't, and what's still genuinely undecided — without re-deriving any of it
from chat history.

**How to use this file.**
- Before starting a `/simulate` run intended to test or extend the system's design (not a casual
  one-off), read this whole file first.
- After a run's Step 4 tally completes, append a new dated entry under **Run log** — from the
  orchestrating session, using this file's absolute main-repo path. Never write it from inside the
  active worktree itself; see the note in `.claude/skills/simulate/SKILL.md` Step 4 for why.
- Keep entries factual and specific: cite the worktree name, pass counts, concrete outcomes (deaths,
  arc resolutions, emergent structures), not just impressions.
- When a run surfaces a design gap or an open question, log it under **Open design questions** so it
  doesn't live only in chat history and get lost at the next compaction.
- Update **Open design questions** in place as questions get resolved — move a resolved question's
  answer into the relevant run-log entry or into the design itself (`TODO.md`), and remove it from the
  open list rather than leaving stale unresolved-looking questions that were actually settled later.

## Standing objective

Does `/simulate`'s design render its own stated intent — characters whose criteria, knowledge, and
relationships drift over many interactions in a way that's genuinely emergent (organically branched out
of initial conditions) rather than a repeated pattern regurgitated by the model, or a smooth convergence
produced by the model's own bias toward agreement? The mechanism should produce real material
consequence (things that can fail, end, or run out) alongside the language-level consequence (hearsay,
criterion drift) it already reliably produces.

A second, standing methodological concern runs alongside the first: anywhere the system needs a
"random" or "which one matters" decision, that decision must come from a genuine mechanical draw
(`pick_pair.py`'s `random.sample()`, `roll_routine.py`'s `random.choices()`, etc.), never from a model
guessing at what feels salient — the same reasoning that motivated building `pick_pair.py` in the first
place applies to every subsequent mechanic layered on top.

## Methodology

After each run that's testing the design (as opposed to a routine content-generation run):
1. Compare what actually happened against the standing objective above — not against whether the
   *mechanism* ran correctly (that's `simulate_tally.py`'s job and is usually fine), but against
   whether the *content* it produced reflects real emergence and material stakes.
2. Distinguish a mechanism working as designed but producing the wrong content, from a mechanism that
   itself didn't work — these need different fixes.
3. Log concrete evidence for both — what if anything broke narrative-content symmetry (deaths, failed
   arcs, contradictory secondhand accounts, structural collapse), and what stayed suspiciously
   convergent or safe.
4. Carry forward anything left genuinely undecided into **Open design questions** rather than silently
   assuming an answer the next time the system gets extended.

## Run log

### Run 1 — 2026-08-08 to 2026-08-10 — worktree `simulate-20260808-181023`

- **Setup:** Auroboro III, Iläria, Khaoe, Nerkeli, Gondarfolas. Phase 1: 50 passes, 30% Terfila-weighted
  context, one seeded scene (a rumor about a Peregrin from Puerto Varilla and a vision at Eurasori).
  Phase 2: 47 more passes on the same population (97 total, short of the planned 100 — population ran
  out), introducing routines, mechanical location resolution (coincidence/visit), arcs with a
  `resolution` field, and an inclined-to-help/hinder mechanic gating a separately-rolled outcome.
- **What worked:** real, unchosen material consequence — 4 deaths (all natural lifespan completions:
  Auroboro III pass 79, Iläria pass 81, Khaoe pass 85, Nerkeli pass 97), a distributed archive network
  that collapsed for a structural reason (built for ~10 keepers, the population only ever had 5, then
  fewer), and only one clean arc resolution across the whole cast (Gondarfolas, twice). The run stopping
  short of 100 passes because the living pool dropped to 1 is itself direct empirical confirmation of
  the debrief's own diagnosis that the world has no reproduction/autopoiesis mechanism — the population
  can only ever shrink.
- **What didn't move:** the underlying epistemology-bias diagnosed after phase 1 (nearly every scene's
  actual subject matter is still CONFLICT-01 / multiplicity-vs-singular-truth) persisted through phase
  2 — the new mechanics added *stakes* to that same content rather than diversifying the content itself.
  This is traced to an implementation shortcut, not a flaw in the design as originally scoped — see
  below.
- **Implementation gap identified (2026-08-10, in debrief following the run):** the original design
  (`TODO.md`'s "Proposed next phase," points 1 and 6) specified routines as a small, *hand-authored* set
  per character, each tied to a concrete role/archetype ("works the market," "keeps the workshop"), with
  arcs derived from that *place-type* archetype, not from the character's pre-existing criterion anchor.
  What actually shipped, under the same night's time pressure, was thinner: routines are bare
  `{location: weight}` pairs with no authored practice attached (the dominant 75%-weighted Terfila slot
  in particular has no defined content for any character), and `arc.about` was auto-derived from each
  character's existing `criterion.anchor` instead of from a place-type template. This is very likely the
  proximate cause of the persisted epistemology bias above — the arcs inherited the same anchor content
  everything else already gravitated to, instead of introducing new, place-grounded material. Not yet
  fixed; see open questions.
- **Unverified:** whether the inclined-to-hinder branch (`check_arc_alignment.py`'s `hinder` output) was
  ever actually triggered this run. The computed `inclined:` value was never persisted to disk — only
  the resulting `advance`/`stall`/`reverse` outcome survives in `arc.history` — so this run can't
  distinguish "reverses came from genuine peer antagonism" from "reverses came from neutral-odds bad
  rolls or from structural causes (the network's own population shortage)." If this needs to be
  verified specifically, log the `inclined:` value to `arc.history` in a future run rather than
  discarding it.
- **Full record:** `.claude/worktrees/simulate-20260808-181023/SIMULATION_LOG.md` (pass-by-pass log,
  full machinery-incident record, tally output). That worktree is disposable and not guaranteed to
  survive indefinitely — anything worth keeping long-term belongs here or in `TODO.md`, not only there.

## Built, 2026-08-10 — not yet piloted

The full second-phase design, worked out collaboratively across the same debrief conversation that
produced Run 1's entry above, is now implemented as actual scripts and orchestration — not yet run
even once. Treat everything below as a prediction until a pilot proves otherwise; see "next step"
at the end of this section.

**Governing principle established during this build:** minimize the subagent's judgment. Every
per-pass decision that can be mechanical now is — a script, a dice roll, or arithmetic over numbers
already on record. Exactly two exceptions remain, both flagged explicitly where they occur: writing
the actual words of a scene (dramatizing an already-fully-decided sequence of facts, never deciding
them), and composing a plausible name-blend for a newborn character at a reproduction event.

- **Hand-authored routine archetypes** — `_lore/archetypes.json` (market, workshop, archive,
  waystation as a starter set), each carrying prose texture plus a `provides` tag list. Routines
  become `{location, archetype, weight, specialization}` (`.claude/skills/character/SKILL.md` Step
  8) instead of a bare location name.
- **Arcs derived from archetype + specialization + criterion**, not the raw anchor alone, and
  scoped against `horizon.py`'s coarse band (never a literal remaining count) — mirrors how
  criterion ripeness already works.
- **Visit motivation** — `check_needs_provides.py` mechanically checks a visit destination's
  archetype `provides` against the traveler's arc `needs`, after pairing/location are already
  independently decided; only then does a visit get framed as purposeful.
- **Arc primacy is now a 50/50 roll** (`roll_arc_primacy.py`) between whichever two characters are
  in the scene, replacing the old host-only rule outright — resolves the "host vs. traveler" open
  question by making it unnecessary rather than picking a side.
- **Help/hinder is now sequential**: `check_arc_alignment.py` gates on the peer's *knowledge*
  first (idiosyncratic, small-sampled, doesn't converge the way this cast's criteria did in Run 1),
  and only asks the peer's *criteria* to decide direction if something real was already found —
  addresses the "will it always tend toward help" risk flagged after Run 1's 0-rejections tally.
  Also now reports back *which specific knowledge item* matched, so a transform (below) can copy a
  new arc topic mechanically instead of a model composing one.
- **Arc outcome rolls (`roll_arc_outcome.py`) now must run and be known *before* the scene is
  written** — the sequencing fix that resolves the "can the dice produce results that read as
  incoherent" concern: the roll decides the fact, the subagent dramatizes it, never the reverse.
- **Contested friction** (`roll_contested.py`) — a rare roll on top of an already-motivated visit;
  resolves through a fixed lookup over the already-computed `inclined` value (help/hinder/mixed),
  never a separate judgment call. No persistent stock or ledger anywhere — a fresh narrative fact
  each time, same as hearsay is never reconciled against a source of truth. A rival only gets named
  if they already have an existing character file; otherwise stays ambient.
- **Leads and deliberate visits** (`roll_lead_followup.py`) — a named rival from a contested scene
  becomes a lead; only checked when the leading character is independently drawn by `pick_pair.py`
  *and* lands specifically as participant_1 (reuses that existing assignment rather than adding a
  new "who initiates" die). Some leads will simply never get followed before they expire (~8
  passes) — expected, not a bug, especially as the living pool shrinks.
- **Transform** — an arc that would resolve `failed` (net ≤ −3) instead pivots if the exact
  failing scene also gate-matched an alternative: `about` is copied mechanically from the matched
  knowledge item's own tags, `resolution` stays `"ongoing"`, the tally resets from that point.
  `archetype`/routine stay fixed — only the goal changes.
- **Reproduction** (`record_partner.py`, `roll_reproduction.py`, `generate_offspring.py`) —
  eligibility is ≥5 shared scenes between a pair (tracked via a new `partners` count) with neither
  parent on a 10-pass cooldown; crossing the threshold only makes a birth *possible*, a roll
  decides whether it happens. The child is a genuine mutation, not an average: each criterion field
  independently coin-flipped to one parent's exact value, knowledge a random-sized random subset of
  the union of both parents' education items, routines likewise. `knowledge.experience` starts
  empty (a newborn hasn't lived either parent's history) and `arc` is unseeded until they first win
  a primacy roll. The child is pool-ineligible for 10 passes after birth. Life.span is freshly
  rolled, not inherited — an explicit choice, not settled by the original design sketch's own
  "open" note; worth revisiting if it turns out to matter. **Both parents get a direct
  `knowledge.experience` line recording the birth, and their combined circle gets the same
  30%-sampled immediate-notification treatment `record_death.py` gives a death** (added
  2026-08-10, after the first version of this script shipped a birth as a completely silent event —
  a real gap against the original design intent, "so others know them before they know them," not a
  deliberate choice). The one remaining model judgment call (composing the name-blend) is now
  narrowed further: `roll_reproduction.py` mechanically decides which parent's name leads the
  blend via `name_lead`, so the model isn't even choosing that.
- **All tunable numbers now live in one place, `_lore/tuning.json`** (odds, thresholds, cooldowns,
  the lifespan range), read via a shared `scripts/lore/tuning.py` loader rather than each script
  hardcoding its own default (added 2026-08-10, on request — the numbers were scattered across
  script defaults and `SKILL.md` prose before this, an easy way for them to drift out of sync). The
  child's own pool-eligibility cooldown was set to **5** passes here (down from an initial 10),
  deliberately kept **distinct** from the unrelated parent-reproduction cooldown, which stays 10 —
  retune either independently by editing the JSON file, no code or doc changes needed.
- **Death legacy** — reuses `record_death.py`'s existing notified-circle output rather than a new
  "close" definition. "Died early" = `horizon.py`'s band read `established` rather than `late` at
  the exact death-triggering pass (structurally the earliest a rolled span can ever land, so no new
  threshold was needed). On an early death, `roll_death_legacy.py` decides whether the arc passes to
  one circle member, applying the same mechanical about/needs copy a transform uses. The
  criterion-vs-close-ones shock check this was meant to add turned out to already exist —
  `record_death.py`'s `shock_candidates` output already flags exactly this; nothing new was needed
  there beyond confirming it's actually wired into a `/simulate` pass.

**Next step:** everything above builds only on existing structure plus these additions — nothing
here has been run once. Per the original suggested order (`TODO.md`'s "Proposed next phase"), run a
genuinely small pilot (10-15 passes) before trusting any of this at scale, and before layering
anything further (the reflection mechanism, still entirely undesigned) on top.

**Permission review (2026-08-10, on request):** `scripts/lore/simulate_setup_worktree.py`'s blanket
tool-allow list is untouched by this build and already covers every new script — they all follow
the identical `Bash -> py script -> internal file I/O` pattern as the originals, correctly anchor
root via `Path(__file__).resolve().parent.parent.parent`, and introduce no new Claude-tool-level
interaction. What the review actually found and fixed: extended mode can call on the order of 15+
scripts in a single pass (versus base mode's 2-4), so the known relative-path-leak failure mode
(still safely auto-reverted, but wastes a pass) has proportionally more chances to occur per pass -
the extended-mode section only pointed backward at base mode's absolute-path/never-cd/verify-writes
rules rather than restating them where they're actually needed first, and never explicitly required
the safety-net check to run at all. Both fixed directly in `SKILL.md`'s extended-mode section.

## Open design questions (carried forward)

- **Odds and thresholds are all first-guess numbers, untuned by any actual run** — all now
  collected in `_lore/tuning.json`, so retuning any of them after a pilot is a one-file edit, not a
  code change. A pilot should be read partly as a check on whether these probabilities produce a
  believable pace, not just whether the mechanism runs at all.
- **Life.span heritability** — currently rolled fresh for a newborn rather than inherited/blended
  from the parents. Flagged above as a deliberate but reversible choice.
- **`_lore/archetypes.json` only has 4 starter entries** (market, workshop, archive, waystation) —
  expand by hand as new routines need a place-type that isn't covered yet; this registry is meant
  to grow the same way character backstories do, not be treated as a closed set.
- **The reflection mechanism** (a character processing/synthesizing alone, without a peer) remains
  entirely undesigned — the last major piece from the original debrief conversation not yet even
  sketched. Needed for two reasons raised in that conversation: it's the only place a character's
  own interiority can recombine into something new without an external trigger, and it's the
  natural home for actually dramatizing an arc's band-scoped ambition decision on-screen, which
  right now happens invisibly inside a dice roll.

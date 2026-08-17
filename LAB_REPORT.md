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

### Run 2 — 2026-08-10 — worktree `simulate-20260810-164704`

- **Setup:** Khaasan, Doran, Ilaria, Bardaglis, Aureobalo, Khaoe — freshly seeded with hand-authored
  `routines` and a seed `arc` each (this run's own prep), specifically to pilot the extended-mode
  design described in the "Built, 2026-08-10" section, per its own "Next step". 10 passes, no context
  given. First-ever run of extended mode.
- **Arc topics chosen deliberately distinct from each character's `criterion.anchor`**, directly
  applying Run 1's diagnosed fix (arc content must come from archetype+specialization, not the
  anchor) — checked programmatically before writing (a script asserted none of the six `arc.about`
  values equaled that character's own anchor string) rather than trusted by eye.
- **Process deviation:** pass 1's subagent dispatch hit a hard permission denial on its first `Write`
  (the scene transcript to `_npcs/scenes/`), despite the worktree's `settings.json` carrying
  `defaultMode: bypassPermissions` and an explicit `Write` allow entry — this is a genuine, correct
  file (`/enact` Step 4 requires it; `/simulate`'s own one-line "never touches `_npcs/`" summary is
  imprecise here, since `/enact` itself always writes `_npcs/scenes/`). Root cause not diagnosed. The
  rest of the run (passes 1-10 in full) was carried out by the orchestrating session directly instead
  of via subagent dispatch, with no further permission friction at all — every script call,
  transcript, and hearsay record for the whole run went through cleanly. Logged as an open question
  below rather than assumed fixed.
- **What worked:** real, unforced material consequence from the arc mechanism, on the very first
  pilot. Across 10 passes: 4 primacy+gate-hit combinations, producing **3 stalls and 1 reverse** —
  zero advances, zero completions. Khaoe's Collective-hall arc stalled twice in a row (pass 7, 8) for
  a *structural* reason dramatized both times: the two places she looked (a travelers' crowd, a
  written archive) don't actually contain the kind of person she needs (someone still working with
  their hands), which she herself recognized as a pattern via a genuine Step 5c synthesis ("she should
  be asking who's still working, not who's still talking") rather than the mechanism just repeating
  itself. Bardaglis's untraceable-ballad arc got its first roll on pass 10 and immediately **reversed**
  — a crew member present at the song's first test in Görff had been retelling it with his name
  attached, undoing the anonymity the whole project is built on. This produced a second real
  synthesis, connecting an earlier positive belief (the song reaching two other towns, pass 7) to this
  setback into one insight: spread and exposure are the same mechanism, not two unrelated risks.
  `roll_contested.py` also fired twice (passes 3, 4), both resolving as neutral-inclined
  split/deferred outcomes exactly per the fixed lookup table, with no named rival either time (no
  qualifying existing character file was a natural fit) — the ambient/unnamed default path got real
  exercise, not just the named-rival path.
- **What didn't fire, and why (useful, not a failure):** zero criterion **breaks** (one reinterpret,
  one reject, both Khaoe — see below); zero reproduction (no pair crossed the 5-shared-scene
  threshold — Bardaglis, drawn in 7 of 10 passes, topped out around 2-3 shared scenes with any single
  partner); zero deaths, so death-legacy never applicable; Doran was never drawn at all by
  `pick_pair.py` in 10 passes (plain variance over a small pool, not a bug — confirmed by the
  script's own genuine `random.sample()`). Most primacy+gate checks (6 of 10) came back a clean
  **miss**, not because the mechanism is broken but because the cast started this run with **zero**
  tagged/grounded knowledge anywhere — the gate can only match against knowledge items that already
  carry `about` tags, and this six-character cast had none until this run itself started generating
  them. Gate-hit rate visibly climbed over the run's own second half as each pass's grounded
  experience entries accumulated (0 hits in passes 1-6, then 4 hits in passes 7-10) — this looks like
  a cold-start property of the mechanism itself, worth confirming on a longer run rather than an early
  finding to fix.
- **Mechanism note, worth flagging precisely because it wasn't obvious from the docstring alone:**
  `check_arc_alignment.py`'s Layer 1 gate is a coarse word-overlap check between the arc's
  about/needs tag *words* and the peer knowledge item's free *text* (not tag-to-tag matching) — so a
  gate hit can and did fire purely because a character's own name, or a word like "collective,"
  appeared literally in a peer's prose, not because the peer's tags matched the arc's tags exactly.
  This is more permissive than the tag-exact-match reading a first pass through the docstring
  suggests, and worth knowing going in rather than re-deriving mid-run.
- **Two real criterion moves, both Khaoe, both from her own anchor (`location: gorff`) — her home
  turf comes up constantly given her routine's weighting, so this isn't surprising:** a **reinterpret**
  (pass 2, tempered 0→1: her own observation that an unattributed song "standing" on its own is the
  same test she holds a building to — a genuine widening of the standard's scope) and a **reject**
  (pass 5: her own uncontested testimony to Ilaria, which didn't actually challenge anything and was
  judged a non-event rather than a survived refutation). Distinguishing these two cases — a real
  widening versus a same-anchor hit that isn't actually a challenge — was a judgment call the
  mechanism's gate can't make on its own; it only flags that the anchor was *referenced*, never
  whether the reference is adversarial.
- **Full record:** `.claude/worktrees/simulate-20260810-164704/SIMULATION_LOG.md` (pass-by-pass log,
  full mechanical-decision record, tally output).
- **Extended same-session, same-worktree, to 25 passes total (2026-08-10), on request: "will
  characters be born?"** Answer: no, but precisely, not as a shrug. Two pairs (Khaasan-Bardaglis,
  Khaasan-Ilaria) each reached 4 of the 5 shared-scene threshold and stopped there — `pick_pair.py`'s
  own uniform draw across 15 possible pairs simply didn't land a 5th time on either in 15 extension
  passes, which is the mechanism working as designed on a fixed pass budget, not a gap. The extension
  is also where **advances first appeared at all** (0 in the first 10 passes, 4 more gate-hits in
  passes 11-25 producing 4 advances/5 stalls/1 reverse combined across all 25) — Khaasan's way-post
  arc got two advances and sits one good roll short of `"complete"`; Bardaglis's ballad arc swung
  reverse→advance→stall→advance, a real demonstration the mechanism can carry a project through a
  genuine setback-and-recovery cycle rather than only trending one direction. 2 more syntheses fired
  (5 total across the full run), same discipline as before (tied to a real hit or multi-source
  pattern, never bare coincidence). **Recurring process gap found and fixed twice:**
  `record_partner.py` was silently skipped in 4 of the first 10 passes and 3 more of the extension
  passes (7 of 25 total) — unlike the arc-outcome roll, which `SKILL.md` explicitly flags as
  "must run before the scene," partner tracking has no equivalent forcing function in the 17-point
  sequence, so it's the step most likely to get dropped when moving quickly. Backfilled both times by
  replaying the missing `record_partner.py` calls once caught; final counts confirmed against the
  pass-by-pass log before trusting them. Worth a `SKILL.md` fix (an explicit checkpoint note, same
  shape as the arc-outcome-roll one) before the next run rather than relying on manual audit again.

- **Extended a second time, same session/worktree, to 40 passes total (2026-08-10), on request:
  "if a character is born, after their cooldown period they become eligible for conversations."**
  Confirmed `_lore/tuning.json` values first (`partner_threshold: 5`, `odds_percent.reproduction:
  40`, `child_cooldown_passes: 5`) and had the plan ready (exclude the child from `pick_pair.py`
  until `birth_pass + 5`, then add them) — never needed, because no birth occurred. What changed
  from the first extension: **reproduction eligibility fired four separate times** in these 15
  passes (Bardaglis-Khaasan, Aureobalo-Bardaglis, Khaoe-Bardaglis, Khaasan-Doran, each reaching 5/5
  shared scenes), and `roll_reproduction.py`'s genuine 40%-odds draw came back false all four times
  - combined probability of that ≈13%, unlucky but not a mechanism problem; the script's own
  docstring already frames "false" as the expected common outcome. This is a materially different,
  more informative null result than the first extension's "never even became eligible." Bardaglis
  was the common parent in three of the four eligible pairs, simply from being drawn in the majority
  of passes across the whole 40-pass run. Arc activity continued in this batch too: 14 more
  gate-hits (7 advances, 5 reverses, 8 stalls) - Khaasan's way-post-chain arc became the run's
  clearest sustained storyline (built, damaged, repaired, entirely dice-driven), and Aureobalo's
  stall-rebuild arc came closest to full resolution (sum 2 of 3 needed). Full record:
  `.claude/worktrees/simulate-20260810-164704/SIMULATION_LOG.md`'s "Second extension" section.

- **Extended a third time, same session/worktree, to 45 passes total (2026-08-10), on request:
  "keeping fingers crossed."** No further reproduction eligibility events fired (the one pair that
  crossed 5 in the second extension, Aureobalo-Bardaglis, moved to 6 without a new roll, per the
  "just crossed" reading); `khaasan-ilaria` and `khaoe-doran` both sit at 4/5 as the closest open
  pairs. Ilaria's attributed-edition arc had its best stretch of the run here - two advances,
  resolving her own earlier attribution snag and turning a failed lead into a new documented
  category - ending one advance short of `"complete"`, the closest any arc came in the full 45
  passes. **A real process gap found:** at pass 43, a scene transcript filename collided with pass
  33's (`aureobalo_ilaria_feria.md`, reused for a different scene between the same two characters),
  and the `Write` tool silently overwrote the earlier transcript - the append-only hearsay/character
  records were unaffected, but the raw transcript would have been lost without noticing the
  duplicate id and restoring it from the conversation's own context. `record_hearsay.py` already
  guards against id collisions in its own two files; scene transcripts have no equivalent guard.
  Worth fixing in `SKILL.md`'s Step 4 (scene-save) directly - check for an existing file at the
  chosen id before writing, same discipline as the id-uniqueness check that already exists elsewhere
  in this system (e.g. `check_character_name.py`).
- **Process change: `SKILL.md`'s Step 4 now requires a "Narrative report" section** in every
  `SIMULATION_LOG.md` going forward (added 2026-08-10, on request) - prose covering how each arc
  actually developed, relationship changes, criterion moves and their triggers, and an honest
  account of what didn't happen, not just the mechanical pass-by-pass and tally output. See this
  run's own `SIMULATION_LOG.md` for the first example of the shape expected.

- **Design bug found and fixed, 2026-08-10, on user report:** Step 13's reproduction eligibility
  had been read as a one-time event ("only the exact pass a pair's count first crosses 5") rather
  than a recurring state check. Under that reading, all four of this run's eligible pairs got exactly
  one 40%-odds roll each, ever - meeting again after a miss (as Bardaglis-Aureobalo did, reaching 6
  shared scenes with zero further rolls) never gave them another chance. `roll_reproduction.py`'s own
  docstring already framed eligibility as a plain recurring condition ("partners[other] >= 5 shared
  scenes, neither on cooldown"), not a one-shot crossing - the one-shot reading was an
  implementation/interpretation error, not the intended design, and it defeats the mechanic's point
  for a small cast (a birth becomes nearly unreachable, not merely rare). Fixed directly in
  `SKILL.md`'s Step 13: the roll now fires on every pairing of two already-eligible people, cooldown
  permitting, not only the first. Not yet re-piloted under the corrected rule as of this entry.

- **Extended a fourth time, same session/worktree, to 60 passes total (2026-08-10) - the batch
  that validated the reproduction fix.** The very first two reproduction rolls after the Step 13
  correction both came back true: Aureobardis (Aureobalo x Bardaglis, pass 48) and Ilaasan (Khaasan
  x Ilaria, pass 51) - two births in short order, versus zero in the first 45 passes under the buggy
  one-shot reading. Both children were later drawn into their own scenes (Ilaasan pass 56, Aureobardis
  pass 59) and both immediately showed inherited-criterion texture on-screen without being written
  that way deliberately - Ilaasan echoing Khaasan's own arrival-over-record standard unprompted,
  Aureobardis building a wholly new project out of the collision between his two fathers' worldviews
  the first time he won primacy as home_frame (the exact trigger `character/SKILL.md` Step 8
  specifies for authoring a first arc). This is the first time in either pilot run a
  freshly-generated character has been driven far enough to test that inheritance actually reads as
  inheritance in play, not just in the JSON. Two arc resolutions also landed in this batch -
  Aureobalo's stall-rebuild (pass 47, 38 passes to close) and Ilaria's attributed edition (pass 60,
  57 passes to close) - the first `resolution: "complete"` outcomes either pilot has produced.
  Khaoe's hall arc ended the run at tally -2, one reverse from crossing into `"failed"` - the closest
  any arc has come to that branch. **Two new open items found, neither fixed yet:** (1) a parent and
  their own child can accumulate `partners` count toward the reproduction threshold with no exclusion
  in the design - not urgent at 1 shared scene as of this run's end, but a real gap before a longer
  run makes it matter; (2) `generate_offspring.py`'s circle-notification sample appears to include
  the newborn in their own notified list (both children's first `knowledge.experience` entry reads as
  hearing about their own birth, third-person) - worth confirming against the script directly rather
  than assumed from output alone. Full record:
  `.claude/worktrees/simulate-20260810-164704/SIMULATION_LOG.md`'s "Fourth extension" section and its
  narrative continuation.

- **Extended a fifth time, same session/worktree, to 85 passes total (2026-08-10), on request:
  "children cannot have offspring with their parents... let's keep the ball rolling... 25 more
  passes."** The parent/child exclusion (see "Open design questions" below) was exercised for the
  first time this batch and worked cleanly: Aureobardis x Aureobalo (son and father) crossed paths
  twice (passes 75, 84), both correctly skipped for reproduction regardless of partner count. Two
  more births landed: Bardaoe (Bardaglis x Khaoe, pass 65) and Dorasan (Khaasan x Doran, pass 72) -
  four children now living from this one cast. A second arc was authored entirely from inheritance
  the same way Aureobardis's was: Ilaasan's, at pass 82, on his first primacy win as home_frame -
  built directly from his own criterion (trusts disagreeing sources, distrusts secondhand reporting)
  rather than blended from two parents' projects the way Aureobardis's was, a genuinely different
  shape of "inherited arc" than the first example produced. Aureobardis's own ballad-collection arc
  had its worst stretch of the run (two compromised case studies in a row, tally to -2, one roll from
  a forced restart) then its actual breakthrough (a genuinely clean case at pass 83, found via
  Ilaria's own notes on her attribution failures) - the clearest example either run has produced of an
  arc using a near-failure as the input to its eventual recovery rather than the two being unrelated.
  **A recurring process gap escalated, not newly found:** the pass-43 scene-transcript filename
  collision (third extension, above) was not a one-off - it happened three more times this batch
  (passes 73, 78, 81), all under the same `p1_p2_location.md` convention colliding with an earlier
  pass between the same pair at the same place. Each time recovered by reconstructing the lost
  dialogue from its still-intact hearsay summary and re-saving under a numbered suffix; no permanent
  data loss, but four collisions across one run is enough occurrences that manual vigilance alone is
  not a reliable guard - see "Open design questions" below, now promoted to its own bullet.
  **Methodology change mid-batch, not a mechanism change:** partway through this batch, two small
  orchestration scripts (`pass_driver.py`, `finish_pass.py`) were written to batch the same sequence
  of `scripts/lore/*.py` calls Step 3 already specifies into one tool call each, instead of one call
  per mechanical fact. Tool-call count per pass dropped from roughly 15-20 to an average of 5.4 across
  the last 17 passes of the batch, with no change to the dice, odds, or mechanical logic itself - the
  same scripts run in the same sequence, just orchestrated in fewer round-trips. Full record, including
  the per-pass tool-call tally: `.claude/worktrees/simulate-20260810-164704/SIMULATION_LOG.md`'s
  "Fifth extension" section and its narrative continuation.

- **Extended a sixth time, same session/worktree, to 115 passes total (2026-08-10), on request:
  "let's do 30 passes more."** The run's first death landed here: at pass 107, immediately after
  Ilaria and Aureobalo's fifth meeting produced a birth (Ilabalo), Ilaria's post-scene `horizon.py`
  check came back `ending: true` for the first time in 107 passes (secretly-rolled span exactly 34,
  band `established`). `record_death.py` ran cleanly - tale written, circle of only 2, 1 notified
  (Bardaglis), zero shock candidates. Her own attributed-edition arc had already resolved `"complete"`
  at pass 60, so death-legacy was judged inapplicable (no ongoing project to pass on) rather than
  forced against an already-finished arc - a genuine judgment call the mechanism doesn't resolve on
  its own, see "Open design questions" below. Because her circle was so small, most of the cast -
  including her own son Ilaasan - did not learn of her death for several passes; her newborn son
  Ilabalo learned of it from a near-stranger (Dorasan) in the very same scene where his own arc got
  authored, eight passes after her death and zero passes after his own birth. None of this sequencing
  was authored - it's what an honest small-circle notification system produces when a death and a
  birth-triggered arc-authoring event happen to land close together. **Two of the run's longest-open
  arcs both resolved in this batch, by the same mechanism (independent cross-referencing, not
  dramatic resolution):** Khaasan's way-post chain (open since pass 14) resolved at pass 103, 90
  passes to close; Bardaglis's untraceable-ballad arc (open since pass 1, the very first pass of the
  entire run) resolved at pass 111, 111 passes to close - the longest-lived open arc either pilot run
  has produced. **Khaoe's hall arc, frozen at -2 since pass 52 with zero rolls against it for 31
  passes, finally moved - into a genuine `transform`, the first time that specific branch of Step 11
  has ever fired in either pilot.** A reverse at pass 91 crossed -3 on a pass where the gate also hit;
  per `SKILL.md`'s own three-way branch this is a transform, not `"failed"` - `arc.about` was
  mechanically overwritten from that pass's `matched_about` tags (`ilaria_attributed_edition`,
  `ilaasan_route_correction`), not composed freely, and dramatized as Khaoe borrowing Ilaria's and
  Ilaasan's own verification discipline for her stalled hall search. **Three more children authored
  arcs from inheritance** (Dorasan pass 98, Bardaoe pass 99 - on his fifth primacy win overall but
  first as home_frame, after four straight wins as traveler - and Ilabalo pass 115, authored the
  instant he was drawn for the first time), bringing five of the run's six children to a
  self-generated project. **A second child arrived for an already-reproducing pair** - Bardalo (pass
  89), Bardaglis and Aureobalo's second child together after Aureobardis - confirming nothing in the
  design caps a pair to one birth. **A previously-suspected bug in `generate_offspring.py` is now
  directly confirmed, not just inferred from output:** at Ilabalo's birth, the script's own printed
  circle-notification output read `notified: ilabalo` - the newborn appearing in their own notified
  sample, caught live rather than reconstructed afterward from a character file. Full record, including
  the per-pass tool-call comparison (zero scene-id collisions across all 30 passes, the exact gap the
  previous batch's `next_scene_id.py` fix was built to close): `.claude/worktrees/simulate-20260810-164704/SIMULATION_LOG.md`'s "Sixth extension" section and its narrative continuation.

- **Two real design bugs found and fixed, 2026-08-10, on user report (before the seventh extension
  below): the "circle" that death/birth notifications draw from was both silently broken and
  structurally incomplete.** (1) Name matching for co-participation was an exact case-insensitive
  string comparison against a character's canonical `name` field, which can carry accents ("Ilaría")
  that hand-typed scene dialogue doesn't always reproduce ("Ilaria"). This silently broke matching for
  Ilaria across her *entire* 115-pass run - every single one of the 32 hearsay entries she appeared
  in this run used the unaccented spelling and matched nothing, so her death-notification circle at
  pass 107 was built almost entirely from two leftover pre-run lore entries instead of anything from
  the run itself. Fixed with a `normalize()` helper (strip diacritics, lowercase) used everywhere two
  names get compared. (2) Even correct matching only ever produced probabilistic circle membership -
  nothing guaranteed a parent, child, or frequent partner ever actually made the circle; they were
  just as likely to be excluded as a stranger met once by coincidence. Added `compute_relations()`:
  parents, reverse-looked-up children, and partners at/above `partner_threshold` (5) are now
  guaranteed circle members, notified in full every time, with the existing 30%-of-the-rest sampling
  applied only to the genuinely extended circle beyond that. Gated by the existing reproduction
  threshold specifically because `partners` tracks every shared scene regardless of count - an
  established character's partners dict can list nearly the whole cast at 1-2 shared scenes each, so
  including all of them as "guaranteed relations" would have made that tier functionally equal to
  "everyone," defeating the point of distinguishing a close circle from an extended one. Applied to
  `notify_death.py`, `record_death.py`, and `generate_offspring.py` identically (`generate_offspring.py`'s
  version also fixes the separately-flagged self-notification bug outright, by excluding the new
  child's own key from every stage of its circle computation, not just from the two parent keys as
  before). All three scripts synced from the worktree to the main repo for permanence; `SKILL.md`'s
  own prose updated to match. Not yet re-piloted under the corrected mechanism as of this entry - see
  the seventh extension immediately below.

- **Extended a seventh time, same session/worktree, to 205 passes total (2026-08-10/11), on
  request: "let's do a long run, let's do a 90 pass run... run overnight."** First full pilot of the
  circle fix above at real scale, and it held cleanly across all 90 passes: relations correctly spanned
  three generations at every birth (grandparents notified via a parent's own `parents` field), deceased
  characters never reappeared in any subsequent circle, and `next_scene_id.py` (built at the end of the
  sixth extension) produced zero scene-transcript collisions across the entire batch, versus four in
  the 85 passes before it existed. **Three more deaths** (Khaasan pass 121, Khaoe pass 184, Bardaglis
  pass 197 - the character present in the very first scene of the entire run), bringing the total to
  four of the original six now deceased; three genuine criterion shocks resolved, all as reinterpret,
  none as break - Khaasan's own two children each independently concluded his death clarified rather
  than invalidated his standard, and Khaoe's death landed directly on Aureobalo's own anchor (a hearsay
  entry specifically about her) since her `criterion.anchor` referenced her by name from years before
  either death mattered. **Two of the run's three longest-open arcs closed**: Khaoe's hall (open since
  pass 1, transformed at pass 91, resolved at pass 148 - 148 total passes) and Ilabalo's bank audit
  (17 passes) and Bardaoe's own-song project (42 passes) closed alongside it. **Six more arcs
  authored from inheritance**, bringing every single living child to having a self-generated project -
  a first for either pilot run. **Five more births**, two of them the run's first cross-generation
  pairings (Aureobardis x Doran -> Aureoran, pass 176; Bardaglis x Dorasan -> Bardasan, pass 177),
  confirming the design correctly allows reproduction across generations as long as it's not an actual
  parent/child pair - neither pairing was excluded by the parent/child check, only genuine parent/child
  meetings (exercised repeatedly this batch too) were. Full record, including the complete pass-by-pass
  mechanical log (condensed for this batch given its length) and narrative continuation:
  `.claude/worktrees/simulate-20260810-164704/SIMULATION_LOG.md`'s "Seventh extension" section.
- **Extended an eighth time, same session/worktree, to 305 passes total (2026-08-10/11), on request:
  "let's do 100 more."** **Three more births**, including this run's first third-generation birth
  (Bardaoe x Dorasan -> Bardaosan, pass ~218) and a second cross-generation pairing between the same
  two second-generation parents six meetings later (Dorasan x Aureobardis -> Aureosan, pass 278;
  Dorasan x Aureobardis had already produced Dorbardis at pass ~235). **One more death** (Ilaasan, pass
  293) - the first in either run to die at the "established" band with a genuinely ongoing arc, which
  made `roll_death_legacy.py` fire for the first time ever: the roll passed, and Bardasan (in Ilaasan's
  notified circle) inherited the crossing-dispute goal outright, his own unrelated arc set aside with
  its own history preserved. **Two of the run's longest-open arcs resolved**: Aureobardis's
  anonymous-giving project (his very first arc, authored pass 67, resolved pass 258 - 191 passes open)
  and Doraglis's unmapped-stories project (resolved pass 279). **Three more arcs authored from
  inheritance** for the run's newest children (Bardaosan, Dorbardis, Aureosan), each a direct
  extrapolation of an inherited criterion or a parent's own project. Full record, including the
  complete pass-by-pass mechanical log (condensed for this batch given its length) and narrative
  continuation: `.claude/worktrees/simulate-20260810-164704/SIMULATION_LOG.md`'s "Eighth extension"
  section.


## Built, 2026-08-10 — piloted 2026-08-10 (Run 2, above)

The full second-phase design, worked out collaboratively across the same debrief conversation that
produced Run 1's entry above, is now implemented as actual scripts and orchestration, and has now run
once in full (Run 2, above, 10 passes). Treat the mechanism descriptions below as confirmed working as
designed; treat any specific numeric prediction as still only lightly tested at n=10.

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

### Run 3 — 2026-08-13 — worktree `generate-run2` (`/simulate -generate` first real run)

**Different objective from Runs 1-2.** This wasn't testing the standing hypothesis above (emergent
criterion/hearsay drift) — `-generate` mode explicitly skips criterion shocks and hearsay mutation by
design (see `scripts/lore/simulate_generate_population.py`'s own docstring). What this run tested:
does the mechanical pass loop actually run clean at scale with no subagent per pass, and does
deferring name/arc-authoring judgment into one batched subagent pass at the very end produce content
as good as the interactive per-pass version would.

**Setup.** 12 participants: the original 6 piloted characters (Aureobalo, Bardaglis, Döran, Iläria,
Khaasan, Khaoe) plus 6 newly-routined ones authored specifically for this run (Farlis, Gondarfolas,
Nerkeli, Nawom, Saltamontabiras, Gok — 5 Terfila-tied, 1 Khan Ice-tied, picked for depth of existing
backstory/knowledge). 300 mechanical passes, no scene prose, one batched language-layer subagent
(Sonnet) at the end for 7 child names + 12 fresh arcs.

**Outcomes.**
- All 300 passes ran with zero crashes or leaks (this mode has no subagent-per-pass, so the
  relative-path-leak failure mode Runs 1-2 had to guard against structurally doesn't apply here —
  every sibling-script call resolves from this script's own `__file__`, never a subagent's
  possibly-wrong cwd).
- 7 births, 8 deaths (Döran, Iläria, Khaasan, Khaoe, Farlis, Gondarfolas, Nerkeli, Gok — every
  deceased character's final `life.lived` landed exactly on their secretly-rolled span, confirming
  `horizon.py`'s `ending` check fired correctly every time), 0 criterion moves (expected — this mode
  never triggers a shock), 12 arcs queued (all `reason: "first"`, none `"reauthor_failed"` — no
  active arc happened to cross the failure threshold this run), max generation depth 1 (no
  grandchildren — 300 passes across 12 starting slots wasn't enough for a child to itself clear
  `partner_threshold`/cooldowns and reproduce, though the mechanism for it to happen is confirmed
  working via `generate_offspring.py`'s own routine inheritance).
- No death-legacy transfers fired (`roll_death_legacy.py`'s 40% odds simply didn't hit across however
  many "died early" checks ran) — untested this run whether the arc-copy itself is correct; that's
  still only exercised by Runs 1-2's interactive mode so far.
- The one real bug this run caught: `simulate_generate_population.py` didn't precondition-check
  `_lore/characters/lifespans.json` coverage, so a pool member with routines but no rolled lifespan
  crashed the run mid-pass (`horizon.py` exits non-zero rather than returning a usable "no lifespan"
  result) instead of failing fast at startup like the routines/deceased checks already did. Fixed by
  adding the same upfront check for lifespans; also exposed a real data-prep gap (`/character` Step
  8's own "routines only" framing makes it easy to forget Step 5's lifespan roll when adding routines
  to an *existing* character rather than a brand-new one — worth a `/character` Step 8 note if this
  recurs).
- **Language-layer quality, one batched subagent for 19 items (7 names + 12 arcs) vs. the interactive
  mode's one subagent per event:** names read as genuine blends (`Nerkaglis` from Nerkeli+Bardaglis,
  `Khaoran` from Khaoe+Döran, `Aureobaloe` from Aureobalo+Khaoe), all mutually distinct, correctly
  led from `name_lead`'s side. Arcs all used a valid archetype matching one of that character's own
  routines, included a `concept:` tag, and read as grounded in that character's specific
  criterion/backstory rather than generic (e.g. Nawom's `road_to_puerto_tortuga` arc picks up directly
  on his backstory's unresolved search; Gok's `hotel_kholi_grandes_juegos_archive` extends his existing
  criterion about keeping Khan Ice facing its past). No obvious quality drop from batching 19 items in
  one pass versus one-at-a-time — worth watching on a larger run (a much bigger manifest might strain
  a single context window or start producing more generic content toward the end of a long list).

**Assessment against `-generate` mode's own goal** (not the standing objective): confirmed viable as
a way to produce a larger starting population fast. The real open question this run couldn't test is
whether the resulting population, once handed to an ordinary interactive `/simulate` run, produces
material/narrative drift as convincing as a population that was interactively generated throughout —
that requires a follow-up interactive run using this worktree's population as its starting pool.

### Run 4 — 2026-08-17 — worktree `simulate-20260817-012440`

**Objective.** Stress-test `-generate` mode at an order of magnitude past Run 3's scale (2000 passes
vs. 300), specifically to answer the two things Run 3 flagged as untested: whether deep generational
recursion (grandchildren reproducing) works at all, and whether one batched language-layer subagent
holds up past ~20 items.

**Setup.** 8 brand-new characters authored specifically for this run (Farkolus, Forlisen - Dome Market
shopkeepers; Farlan - harbor; Auroben - gardens; Aurora - temple; Krastomus - bank; Terniko, Muli -
municipality, Muli originally from Görff), all Terfila-based, routines deliberately cross-linked so
every character shares at least one location with another (Dome Market/Terfila Harbor/Municipal
Office each tie 3-4 of them together). Five new contexts added (port, temple, gardens, municipality,
bank). 2000 requested passes.

**The mechanism bug this run found and fixed.** The original single-invocation attempt crashed at
pass 561 with a Windows `[Errno 22] Invalid argument` / path-too-long failure writing a birth tale.
Root cause: `simulate_generate_population.py`'s placeholder slug scheme
(`placeholder_{name_lead}_{other_parent}_{counter}`) chains both parents' own slugs into a child's
placeholder, and a placeholder is never renamed (only the human-facing `name` is, by
`apply_language_layer.py`'s own design) - so a grandchild's placeholder embeds its already-chained
parent placeholders, compounding every generation. By generation 5-6 this exceeds Windows' 260-char
path limit. Run 3 never hit this because it only ever reached generation 1. **Fixed** by changing the
scheme to a flat, fixed-width `placeholder_child_{counter:04d}` - bounded length regardless of
generation depth, and the fixed width is also collision-safe against `apply_language_layer.py`'s
plain-substring rename (`child_0003` is never a substring of `child_0037`, unlike unpadded `3`/`37`).
Verified nothing else in the mechanism depends on the placeholder's structure encoding lineage -
`pending["children"]`'s own `parent_a`/`parent_b` fields already carry that for the language layer.
**Fix applied directly to this base branch** (`scripts/lore/simulate_generate_population.py`), same
commit as this log entry - future `-generate` runs of any real size no longer need to rediscover this.

**Operational note, not a mechanism bug: a single 2000-pass background invocation of the script was
killed twice** by the surrounding harness (once with no error, empty log) before completing - unrelated
to the script itself (a shorter 200-pass foreground chunk of the same script, same worktree, ran clean
every time). Worked around by chunking: 10 sequential 200-pass foreground invocations, chaining
`--living-pool-out`'s printed living pool as the next chunk's `--pool`, manually merging each chunk's
`_pending_language.json`/`GENERATION_LOG.md` into running totals, and preserving the *first* chunk's
`.simulate_snapshot.json` (each chunk's own invocation overwrites it, which would otherwise corrupt
the final `simulate_tally.py report` diff). This incidentally exercised `generate_offspring.py`'s
existing slug-collision loop (`while (CHAR_DIR / f"{key}.json").exists()`) for real, since each
chunk's own `child_counter` restarts at 1 and collides with the previous chunk's `placeholder_child_
0001..000N` files - confirmed it correctly suffixes (`_2`, `_3`, ...) rather than overwriting. Worth
promoting chunking to a documented option in `SKILL.md`'s `-generate` mode for any run past a few
hundred passes, independent of whether this particular kill cause recurs.

**Outcomes.**
- All 2000 passes completed (across the 10 chunks) with zero further crashes after the placeholder fix.
- All 8 founders died, every one landing `life.lived` exactly on their secretly-rolled span again
  (Farkolus 35, Forlisen 56, Farlan 58, Auroben 52, Aurora 57, Krastomus 52, Terniko 40, Muli 35) -
  `horizon.py`'s ending check remains reliable at scale.
- 84 births, 146 arcs queued, 0 criterion moves (expected - this mode never triggers a shock).
- **Max generation depth: 22** (computed from the final `parents` chains, not from any single chunk's
  own `state.generation` counter, which resets to 0 at every chunk boundary and so only ever reported
  each chunk's *local* depth - up to 3 - not the true cumulative figure). Directly answers Run 3's open
  question: deep recursive reproduction across many generations works correctly once the placeholder
  bug above is fixed.
- Living pool at the end: 3 (a fast-cycling population with founder spans of 35-58 scenes churns hard
  over 2000 passes on a small pool - expected, not a bug).
- **Language-layer quality at 230 items (84 names + 146 arcs) in one subagent dispatch, directly
  answering Run 3's other open question:** completed cleanly (881s, ~181k tokens, all 230 entries
  resolved, zero skipped). But the failure mode Run 3 predicted ("more generic content toward the end
  of a long list") didn't manifest the way expected - instead, the subagent discovered the 146 queued
  arcs collapsed to only **25 distinct (criterion × primary-routine-context × horizon-band)
  signatures**, because `-generate` mode never runs a criterion shock, so a criterion inherited at
  birth stays byte-identical for that whole lineage's descendants. It authored each signature once and
  reused that content across its instances (still one real, separately-registered arc per character -
  not skipped), which kept every individual arc mechanically valid and well-formed but means a deep,
  fast-cycling lineage's arcs are far less thematically diverse than the count suggests. Also visible
  in `encodings.json`: many near-duplicate `concept:` entries (`dome_pitch_succession`,
  `dome_pitch_succession_1` .. `_19`, etc.) - one real registration per arc instance, as designed, but
  worth knowing this is why the concept registry now has long near-duplicate runs.
- Names: all 84 unique, correctly led from `name_lead`'s side, no collisions.

**Assessment against `-generate` mode's own goal:** confirmed viable at real scale (2000 passes, 22
generations) once the path-length bug is fixed. The population is ready to serve as a starting cast
for an ordinary interactive `/simulate` run, same as Run 3's. The full population lives in worktree
branch `worktree-simulate-20260817-012440` (not merged into this branch).

## Open design questions (carried forward)

- **A deep, fast-cycling `-generate` lineage's arcs converge onto very few distinct signatures**
  (Run 4: 146 queued arcs, only 25 distinct criterion×context×horizon combinations) because
  `-generate` mode by design never runs a criterion shock, so a criterion inherited at birth never
  drifts from its parent's. Each arc instance is still individually authored, valid, and separately
  registered - this isn't wrong content, just thematically narrower than the raw count suggests, and
  it's a direct, probably-unavoidable consequence of pairing "no shocks in this mode" with "many
  generations." Worth deciding whether that's fine as-is (this mode's whole point is a fast
  starting-cast generator, not narrative depth - real drift is meant to come from the *interactive*
  mode that follows) or whether a light mutation on inheritance (e.g. jittering `wasted_life`'s
  wording, or occasionally leaving a child's criterion `origin: "uncollided"` instead of copying the
  parent's) would make the resulting starting cast more varied without reintroducing a full shock
  mechanism into a mode designed specifically to skip them.

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
- ~~No parent/child exclusion in reproduction eligibility.~~ **Fixed 2026-08-10**, on user request,
  before it was ever exercised in a run: `SKILL.md`'s Step 13 now checks both directions of the
  `parents` field (already written by `generate_offspring.py` on every child, `[parent_a, parent_b]`)
  and skips the reproduction check entirely for a parent/child pair, regardless of partner count or
  cooldown. The original hand-authored cast has no `parents` field at all, which reads as empty and
  never blocks them. **Exercised in Run 2's fifth extension** (passes 75, 84 - Aureobardis x
  Aureobalo, son and father) and worked exactly as designed both times.
- ~~`generate_offspring.py`'s circle notification may include the newborn in their own notified
  list.~~ **Confirmed, not fixed, 2026-08-10 (Run 2's sixth extension).** First suspected in the
  fourth extension from character-file output alone (two children's first `knowledge.experience` read
  as hearing about their own birth). Now directly confirmed: at Ilabalo's birth (pass 107), the
  script's own printed output read `notified: ilabalo`, the newborn's own key appearing in its circle
  sample. Root cause not yet diagnosed in the source and no fix applied - worth tracing through
  `generate_offspring.py`'s circle-union logic (it reuses `notify_death.py`'s own function, unioned
  across both parents) the next time this script is touched, since the fix is presumably a one-line
  exclusion (`- {a_key, b_key, new_key}` instead of just `- {a_key, b_key}`) once located.
- **`roll_death_legacy.py` has no guidance for a deceased character whose own arc is already
  `"complete"` at time of death.** First real death in either pilot run (Ilaria, Run 2's sixth
  extension, pass 107) happened to hit exactly this case - her attributed-edition arc had resolved
  back at pass 60, well before her death. Judged death-legacy inapplicable (nothing ongoing to pass
  on) and skipped the roll entirely, but the script itself takes no position on this - its docstring
  only says "died early... passes their arc on," without addressing what "their arc" means once it's
  already finished. Worth an explicit decision before the next death where this matters: either the
  script should refuse to run against a `"complete"` arc (mirroring `record_death.py`'s own refusal to
  run twice against an already-deceased character), or there's a legitimate reading where a legacy
  still passes something forward (the *resolved* project's spirit, not its unfinished work) that
  isn't designed for yet.
- **Subagent dispatch hit a hard `Write` permission denial in Run 2** (`_npcs/scenes/`, a file
  `/enact` Step 4 legitimately requires), despite the worktree's own `settings.json` carrying
  `defaultMode: bypassPermissions` and an explicit `Write` allow entry that covered every other write
  in the run when done by the orchestrating session directly. Root cause not diagnosed — worth
  investigating before the next run defaults back to one-subagent-per-pass dispatch; direct
  orchestration (no subagent) worked cleanly for all 10 passes as a fallback, at the cost of every
  script call and record-keeping write happening in the main conversation instead of being delegated.
- **`check_arc_alignment.py`'s Layer 1 gate matches on free-text word overlap against the peer's
  knowledge-item *text*, not tag-to-tag matching against its `about` refs** (confirmed by reading the
  script directly after an unexpected match in Run 2) — more permissive than the tag-exact reading the
  docstring's own example suggests at a glance. Not necessarily wrong (arguably closer to "does the
  peer's own account plausibly touch this" than strict tag equality would be), but worth a deliberate
  decision rather than leaving the two readings ambiguous for the next person extending this script.
- **Gate-hit rate looked cold-start-dependent in Run 2**: 0 hits in the first 6 of 10 passes (the cast
  started with zero tagged/grounded knowledge anywhere), then 4 hits in the last 4 as each pass's own
  grounded experience entries accumulated. Plausible and probably fine, but only tested at n=10 on a
  cast that started from nothing — a longer run, or a run seeded with some pre-existing grounded
  history, would confirm whether this is a real warm-up curve or an artifact of this particular small
  pilot.
- **Run 1's "was `inclined` ever persisted" question is still open after Run 2** — Run 2's arc.history
  entries recorded the outcome (`stall`/`reverse`) and a free-text note, but not the `inclined` value
  itself as a queryable field, the same gap Run 1 flagged. Still worth fixing in a future run's
  `append_arc_history` step if this needs to be verified precisely rather than reconstructed from
  prose notes.
- **Scene-transcript filenames have no id-collision guard, and this is now a recurring bug, not a
  one-off.** First hit at pass 43 of Run 2's third extension (`aureobalo_ilaria_feria.md` silently
  overwritten by `Write`), then three more times in the fifth extension alone (passes 73, 78, 81 -
  all under the `p1_p2_location.md` naming convention, all a pair reusing a location they'd already
  met at earlier in the same run). Every occurrence was recoverable only because the append-only
  hearsay record survives independently and the lost dialogue could be reconstructed from its summary
  - the actual original wording is never recoverable once overwritten. `record_hearsay.py` already
  refuses a duplicate id outright for its own two files (`_lore/encodings.json`,
  `_lore/characters/hearsay.md`); nothing in `SKILL.md`'s Step 4 (scene-save) does the equivalent
  existence check before writing `_npcs/scenes/<id>.md`. A `next_scene_id.py`-style helper (check for
  an existing file, append a numeric suffix if found) was written ad-hoc in Run 2's fifth extension as
  a workaround but never promoted into `SKILL.md` itself or a real `scripts/lore/` script - that
  promotion should happen before the next long run, given four collisions is well past the point
  where "catch it by eye" is a credible sole safeguard.
- **`record_partner.py` has no forcing function in the 17-point extended sequence and got silently
  skipped 7 times across Run 2's 25 passes** (caught by manual audit both times, backfilled
  correctly). `SKILL.md`'s Step 10 (arc outcome roll) is explicitly marked "MUST run and be known
  before the scene is written" in bold with its own rationale paragraph; Step 12 (partner tracking)
  has no equivalent emphasis despite being just as easy to drop mid-sequence. A small `SKILL.md` edit
  - flagging Step 12 the same way, or folding it into the same checklist moment as the arc-outcome
  roll - would likely prevent this recurring a third time, rather than relying on catching it by
  audit again. No script existed to append `arc.history` entries directly either (unlike every other
  mechanical step, which has a dedicated script) - Run 2 worked around this with an ad-hoc
  orchestrator-side script; worth promoting to a real `scripts/lore/` script if extended mode gets
  used again, for the same "mechanical step, not hand-edited JSON" discipline everything else here
  already has.
- **Hearsay was never actually absorbing into the corpus it was supposedly growing - fixed
  2026-08-11, on user report.** `record_hearsay.py` only ever appended to the flat
  `hearsay.entries` array; a real, already-built tool for folding a claim's `about` reference back
  into the entity it's about (`build_source_index.py`) existed but had never been run against this
  run's output, and even where it was run, 325 of 331 resolvable references failed - because the
  42 distinct concepts /simulate's own arcs had been using for hundreds of passes
  (`bardaglis_untraceable_ballad`, `khaoe_collective_hall`, `aureobardis_giving_ballads`, etc.)
  were never once registered as real `concepts[]` entries in `encodings.json` - they only ever
  existed as tag strings inside individual characters' `arc.about` fields. Nothing could resolve
  into them because they didn't exist as resolvable targets. Fixed in two parts: (1) a one-time
  catch-up (`promote_arc_concepts.py`, job-tmp only, not promoted to `scripts/lore/` since it's a
  backlog-clearing tool, not a recurring one) registered all 42, each description assembled
  mechanically from the owning character's own arc data (archetype/needs/resolution) or, for tags
  with no owning arc (birth announcements, market-season notes), from the claim text itself - never
  freely authored; then `build_source_index.py` re-run, linking 318 more hearsay/tale sources
  (up from 6) across the whole corpus. (2) Permanent automation:
  `scripts/lore/register_arc_concept.py` (new) registers a concept the moment its arc is authored -
  wired into `SKILL.md`'s arc-authoring step, no-ops cleanly on a transform/legacy reusing an
  existing tag - and `SKILL.md`'s Step 17 now runs `build_source_index.py` once at the natural end
  of a batch, closing the loop without requiring a separate `/integrate` invocation. Every new
  concept's `sources[]` stays honestly tagged `{"category": "hearsay", ...}` throughout, per user
  direction - promotion registers a concept's existence, never upgrades its evidentiary status; a
  human author adding real material later is the only thing that would ever add a `"material"`
  source alongside it.
- **`has_sources` was only ever true for 4 of 14 categories, and even flipping it wasn't enough on
  its own - fixed 2026-08-11, on user report ("if something was said by someone, it means there is
  a source, and that source is hearsay").** `conflicts`, `characters.named_inhabitants`, every
  `routes.*` category, and every `time_systems.*` era system all had `has_sources: false` in
  `encodings.json`'s own `_categories` schema - not by oversight documented anywhere, just never
  extended past the original four (`location`/`concept`/`character_legendary`/`character_real`).
  Flipping the flag alone was insufficient: `build_source_index.py`'s `resolve_prefixed()` had a
  *separately* hardcoded prefix map (`concept`/`location` only, plus a special-cased `character`
  branch) that routed every other prefix - `era_ensayo`, `conflict`, `inhabitant`, `highway`, all
  of them - straight to `out_of_scope` regardless of what `has_sources` said, despite the
  function's own docstring claiming this was data-driven. Also found and fixed while extending
  this: `build_index()` assumed every entry's identifier field was literally called "id" - true
  for `concept`/`location` by coincidence, but `highway` uses `code`, `airport` uses `location`,
  `year_esquema` uses `year` (an int) - this would have KeyError'd the instant any of those
  categories' `has_sources` flag was ever actually exercised. Now reads `id_field` from each
  category's own `_categories` spec instead. `characters.named_inhabitants` (`shape:
  "grouped_list"`, nested `{locality: [people]}`, no flat `id_field`) is deliberately still
  excluded from the generic list-handling path even though its own `has_sources` is now true - a
  real per-person index entry would be needed before it's safe to include the same way as
  everything else; still only handled via `resolve_touches_path`'s existing recognize-and-skip
  branch for `tales[].touches`. **A genuine, previously-invisible ambiguity surfaced immediately**:
  several locations (Görff, Salthos Cruzados, Khol Moshin...) also have an airport of the same
  name, so a bare, unprefixed `about: "gorff"` now correctly resolves as ambiguous between
  `location: gorff` and `airport: Gorff` rather than silently picking one - the script's own
  "never guess" rule caught this the instant `airport` became sourced. Left unresolved and
  reported rather than tie-broken by fiat, pending a user decision on whether bare references
  should prefer `location` by default. Net effect after re-running against this run's own
  305-pass corpus: 11 more links folded in (era references that were previously silently
  discarded); against the 27-entry pre-run baseline in the main repo, 10 more.
- **Bare-reference ambiguity now defaults to `location` on a tie, per user direction ("let's
  default them to location when it's ambiguous").** Several locations (Görff, Salthos Cruzados,
  Khol Moshin) also have an airport of the same name, so once `airport` became a sourced category
  a bare, unprefixed `about: "gorff"` correctly-but-unhelpfully reported as ambiguous between
  `location: gorff` and `airport: Gorff`. `resolve_bare()` now attaches to the single `location`
  candidate when exactly one exists among tied exact matches; a tie between two non-location
  categories, or two location candidates, still goes unresolved rather than guessed - the
  "never guess" rule only got an exception for the one case that's actually never wrong in
  practice (a bare slug in this corpus is essentially always a place).
- **Character births are tales, not concepts - corrected 2026-08-11, on user report.** All 14 birth
  events promoted as concepts in the fix above (`aureobardis_birth`, `khaoe_...` no wait, all 14
  `<name>_birth` tags) were the wrong category: a birth is a discrete event, the same shape as a
  death, and belongs in `tales.entries` the way `record_death.py` already treats death - not a
  `concepts[]` entry, which is for durable, recurring topics. Converted retroactively: each got a
  real `_lore/tales/birth_of_<key>.md` + `tales.entries` row (identical template to a death tale),
  the 14 concept entries were deleted, and the 45 hearsay claims that had referenced
  `concept: X_birth` were repointed to `tale: birth_of_X` - `build_source_index.py` then linked all
  45 into their new tale entries' `sources[]`. Permanent fix, so no future birth needs this
  retroactive treatment: `generate_offspring.py` now writes a real tale itself at the moment of
  birth (new `write_birth_tale()`, mirroring `record_death.py`'s own tale-writing exactly - same
  Responsible/Told by/Told on/Encodings id template, same `_authors.md`/`_index.md` rows), and
  prints the new tale's id so the caller tags the birth-announcement hearsay claim
  `about: "tale: <id>"` from the start. Tested via a dry-run birth end-to-end (tale file, encodings
  entry, authors/index rows all verified), fully reverted after.
- **Adding "tale" as a `has_sources: true` `_categories` entry made it resolvable as an about-prefix
  for free** - because `resolve_prefixed()`/`build_index()`/`load_categories()` had already been
  made fully schema-driven earlier this session (see above), registering `tale` in `_categories`
  (`path: "tales.entries"`, `shape: "list"`, `id_field: "id"`) was the only change needed for
  `about: "tale: X"` to become a real, resolvable reference - no new code in the resolution
  functions themselves. This is the same generalization paying for itself a second time.
- **`roll_death_legacy.py` exercised for the first time against a genuinely ongoing arc, and worked
  as designed (Run 2, eighth extension, pass 293).** Ilaasan died at the "established" band with his
  crossing-dispute arc still ongoing at tally 2/3 - the first death in either run to actually meet the
  "died early" precondition the script's own docstring describes (every earlier death was either at
  the "late" band, or - Ilaria's case, logged above - had an already-`"complete"` arc). The roll
  passed, one of the four people in Ilaasan's own notified circle (Bardasan) inherited the goal, and
  the transfer was applied by hand exactly the way the docstring specifies: `about`/`needs` copied
  over, `resolution` reset to `"ongoing"`, archetype/routines left untouched, a new history entry
  appended rather than the prior history erased. No script exists yet to apply this mechanically
  (unlike `record_death.py` itself) - it was done via direct JSON edit this run, the same gap already
  flagged above for `arc.history` appends generally. Worth a `scripts/lore/apply_death_legacy.py` if
  extended mode keeps getting used, both for consistency and so the "reset to ongoing, copy about/needs,
  preserve prior history" rule can't drift from what actually gets typed by hand each time.
- **Doran's orphaned arc (flagged in narration during Run 2's seventh extension, never formally logged
  until now) is still an open gap: a "late"-band death with an ongoing, unresolved arc has no closure
  mechanism at all.** Doran's own western-border-survey project was still `"ongoing"` at his death;
  because his band read "late" rather than "established", death-legacy correctly did not apply per the
  mechanism's own rule (see above) - but nothing then happens to the arc itself. It simply stays
  `"ongoing"` inside a character file whose owner is permanently `life.deceased: true`, with no process
  that will ever touch it again: it can never win a primacy roll (primacy is drawn from the living
  pool), never get a gate check, never resolve, fail, or transform. This is functionally different from
  a death-legacy miss (where the roll was at least attempted and came back false) - here the mechanism
  never even considers the arc once its owner is gone. Whether that's the correct behavior (some
  projects really do just end, unfinished, with their owner) or a gap worth closing (perhaps a
  "late"-band death should still get an *automatic* legacy pass, distinct from the odds-gated
  "established"-band roll, on the theory that late means "ran out of time" rather than "never really
  invested") is a genuine open design question, not yet decided either way.

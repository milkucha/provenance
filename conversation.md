# Project chronicle

Not where a `/simulate` run gets logged — that's still `LAB_REPORT.md`'s job while a run is active.
This is the wider thing: the journey of the *conversation* that built this project — landmarks, why a
given turn got taken, and what's still genuinely open — kept so a session doesn't have to re-derive
the arc of the whole project from chat history that's already gone by the time a new context window
starts. Written in working voice (`.claude/VOICE.md`), not lore voice — this is project
record-keeping, not in-world text.

A run's *findings* do belong here too, once they're history rather than an active run — see
Landmarks below for what `/simulate`'s Runs 1–3 actually found. **Why this branch's own
`LAB_REPORT.md` looks empty:** `provenance-bare` deliberately strips authored lore and run history
for a clean, shippable checkout (see the 2026-08-26/27 landmark below) — the full pass-by-pass logs
survive on the `provenance-standalone` branch and in each run's own disposable worktree
(`SIMULATION_LOG.md`), for whoever needs that level of detail. This file carries the substance
forward regardless of which branch's `LAB_REPORT.md` currently holds it.

**How to keep this current.** At the end of a substantive session — one that actually moved the
project, not a one-off question — append a short, dated paragraph to **Landmarks**, in the same
register as the entries already there: what got decided and why, not a diff of files touched (git
history already has that). Anything discussed but not yet built belongs in **Open threads** instead;
move it into Landmarks once it's actually implemented, and say where.

## Origins

The lore underneath this predates any of the tooling by about 12 years — authored in fragments, long
before there was a system to grow it. What this project is actually testing is whether an
agent-driven system can take that seed and grow it further in a way that still reads as *this*
world's own culture — organic, drifting, full of gaps — rather than generic model output wearing the
world's names. The standing fear driving a lot of design decisions is producing "slop": content that
sounds plausible but isn't actually grounded in anything the record established. Minecraft is where
the characters currently get to stand and be talked to, not what the project is for — the engine is
meant to be embodiment-agnostic, Minecraft swappable for something else entirely.

## The throughline

A handful of ideas repeat across almost every design conversation in this project, worth stating
once here rather than re-deriving them from any one session:

- **Negative space.** A world's real structure is what stays *unsurfaced* — the objective record, the
  pillars a character's convictions stand on. What actually gets said out loud (dialogue, hearsay,
  tales) is a thin, subjective slice drawn from that foundation, never the whole of it. Loosely
  mythemes/monomyth-flavored (Lévi-Strauss came up explicitly, then got revised on the spot — not
  pairs of oppositions so much as different paradigms of existence, layered and juxtaposed).
- **Finitude as the engine of drama.** Characters know two facts, unconditionally: life ends, and
  everyone wants theirs to have been worthwhile. Criterion (what a character counts as a life well
  spent) is derived from those two facts colliding with backstory and knowledge — stated negatively,
  anchored to one concrete case, and it only moves when a shock references that anchor directly.
  Drift (accrued cost, a shortening horizon) never moves it alone — it only changes how susceptible a
  character is when a shock does land.
- **Mechanize the mechanical, keep judgment in prose.** Anywhere a "random" or "which one matters"
  decision is needed, it has to come from a genuine mechanical draw, never a model's guess at what
  feels salient. This shows up over and over as scripts replacing hand-relayed steps (pairing,
  hearsay recording, tallying) while leaving claim mutation, shock resolution, and scene-writing
  itself as prose, exactly where judgment actually belongs.
- **Nothing decided silently.** Stated once in `.claude/PRINCIPLES.md` now, but it was a conversation
  pattern long before it was a rule: a genuine open question gets asked or logged, never guessed.

## Landmarks

**2026-07-24 to 25 — Cold start.** First commits: hearsay, the gesture rig, `/character` as a
lighter sibling of a full enacted scene. The gesture work in particular ran through a lot of
in-game trial and error (an elbow joint that wouldn't compose with its parent bone, a shared timer
that broke once more than one NPC could gesture at once) before landing on what's in `GESTURES.md`
now.

**2026-07-30 to 31 — Tale, fact, and criterion.** `/tell` and `/discover` (later merged into `/tell`)
split off a third and fourth source of truth alongside material and hearsay. The criterion mechanism
got designed in real time across one long session — negative derivation, anchors, the will to live,
shocks vs. drift — settling most of the shape it still has today. Also the first fully bilingual
enactments (Khan Icé, la Feria del Milenio, Gok, Bardaglis, Auroboro III) — the in-character register
that `.claude/VOICE.md`'s "world voice" section is built from.

**2026-08-05 to 09 — `/simulate`, Run 1, and the unattended-run problem.** `/simulate` was born to
batch `/enact` across a population, run inside a disposable worktree so a stress-test run couldn't
touch real files. Run 1 (97 passes on 5 characters) delivered real, unchosen material consequence —
4 natural deaths, a keeper network that structurally collapsed as the population shrank — but also
the diagnosis that mattered most: nearly every scene still orbited the same one conflict
(multiplicity vs. singular truth), because routines at that point were bare `{location: weight}`
pairs with no authored practice behind them, and arcs were auto-derived from a character's existing
criterion anchor instead of from what they actually did somewhere. Content converging like that was
structural, not a prompting problem — it's what led straight into the extended-mode redesign below.
Separately, what actually ate the most *time* in this stretch wasn't the simulation design at all —
it was getting a run to survive *unattended*, overnight, with no permission prompts: worktree
settings written before `EnterWorktree` instead of after, a relative-path leak that silently wrote
real scene content into the main checkout, `cd`-in-Bash hard-blocked with no override. Each one got
documented as its own fix rather than papered over, because the failure mode kept recurring in
slightly different shape until it was actually root-caused.

**2026-08-10 to 13 — Extended mode, Runs 2 and 3.** The redesign added routines tied to a real
place-type archetype, arcs with progressive state (primacy, gate, outcome, transform), reproduction,
and death legacy — the governing rule for the whole build: minimize the subagent's judgment, so
almost every per-pass decision became a script, a dice roll, or arithmetic, leaving only scene-prose
and a newborn's name-blend as genuine model calls. Run 2 piloted it on 6 characters, then got
extended in place seven more times up to 305 passes on direct request ("let's do 30 more," "keeping
fingers crossed") rather than as separate runs — and it delivered exactly the material stakes Run 1
was missing: arcs that stalled, reversed, transformed, and resolved on real dice rather than smooth
convergence; four generations of births; deaths that triggered genuine criterion shocks (reinterpret
and break both fired, not just reject); and one arc that stayed open for 148 passes before resolving.
It also surfaced a real string of bugs worth remembering because of what they say about the
system's own blind spots, not just because they got fixed: an accent mismatch ("Ilaría" vs.
"Ilaria") silently broke an entire character's death-notification circle for 115 passes before
anyone noticed; hearsay was never actually folding back into the concepts it referenced, because
`/simulate`'s own recurring arc topics had never been registered as real `encodings.json` entries in
the first place — the corpus looked like it was accreting when 325 of 331 references were
silently going nowhere; and a scene-transcript filename collision quietly overwrote earlier dialogue
four separate times before a collision guard existed. Each was root-caused and fixed, not patched
around. Run 3 then validated `/generate` (300 mechanical passes, zero scenes, one batched
language-layer pass for names and arcs at the end) as a genuinely faster path to a starting
population, at the cost of not testing drift itself — which is exactly why `/generate` and
`/simulate` stayed two separate commands rather than one mode of the other, at this point in the
project's history.

**2026-08-16 to 17 — Provenance rework, genealogy bugs.** Criterion's trust/distrust derivation moved
from a hardcoded per-category flag to resolving mechanically off an anchor's actual source
provenance. A 2000-pass `-generate` run then surfaced real bugs in the reproduction mechanism itself
(criterion copied verbatim instead of re-derived, arcs converging onto ~25 signatures, an unbounded
placeholder-slug growth that crashed a deep lineage) — each one fixed and logged rather than the run
just quietly discarded.

**2026-08-26 to 27 — Provenance, `/start`, and folding extended mode into `/enact`.** The project
renamed itself from Luminacion to Provenance in the README, leading with the engine rather than
Minecraft. `/start` shipped as a live welcome banner for a fresh checkout. `/simulate`'s extended
mode — until now an optional branch — became the only mode: `/enact` against another character now
always requires routines+arc and always runs the mechanical layer first, with no more freeform
fallback for an incomplete pair. This is also when voice dictation + TTS got wired up for this
project, and when `.claude/VOICE.md` got built — a direct response to noticing the README and docs
didn't sound like the person building them.

## Open threads

Carried forward until built — remove from here and fold into Landmarks once they land, with a note
of where.

- **Grounding.** A proposed new lore category, sitting alongside material/tale/fact/hearsay but
  qualitatively different from all of them: what's true of the world *regardless of who knows it* —
  Minecraft's own game rules (condensed off the wiki) plus a live computer-vision read of the actual
  world's terrain/construction state. The reasoning for keeping it separate from material: material
  is testimony-shaped (it can be wrong, like the legend of Troy), grounding is the state of the ruins
  themselves. Discussed at length 2026-08-26 — shape (a folder, not a single file), why it shouldn't
  be folded into `encodings.json`'s existing categories, and the standing example of characters not
  inferring cardinal directions or approximate town radius from coordinates they already have — not
  yet implemented.
- **Reflection.** A character-alone enactment type — a turn spent in dialogue with themselves,
  synthesizing new information — proposed as both randomly occurring and triggered by specific
  circumstances (a shock, a death in the character's circle, a certain number of passages). Flagged
  as the last major undesigned piece as far back as Run 3's own open questions (2026-08-13): it's the
  only place a character's own interiority can recombine into something new with no external
  trigger, and the natural home for actually dramatizing on-screen what right now happens invisibly
  inside a dice roll. Discussed again, still not designed in detail, as the natural next build after
  grounding on 2026-08-26; not yet wired into `/enact`.
- **Synthesis, refined further.** The 2026-08-07 mechanism (a character combining something they
  already knew with something just heard into a new belief not reducible to either — e.g.
  "Sit Nalta" and "Sit:Nalta" might be the same place) needs to generalize past that one worked
  example into other kinds of theories a character could form. Still looking for more worked
  examples before the rule can be written generally.
- **The missing consequence layer.** Flagged 2026-08-26: characters can give/receive things during a
  scene, but right now that only happens at the language level — it doesn't mechanically connect to
  anything. Intended to be picked up right after reflection lands.
- **Travel constraints.** Scene location assignment is currently unconstrained (a character can end
  up anywhere their routine or an adjacent character puts them); the intent is to gate it by actual
  geographic adjacency and turn-cost, so a trip to a city three turns away carries a real trade-off —
  discussed but not designed in detail yet.

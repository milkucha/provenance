# Project chronicle

Not a run log — that's `LAB_REPORT.md`'s job, scoped to `/simulate` specifically. This is the wider
thing: the journey of the *conversation* that built this project — landmarks, why a given turn got
taken, and what's still genuinely open — kept so a session doesn't have to re-derive the arc of the
whole project from chat history that's already gone by the time a new context window starts. Written
in working voice (`.claude/VOICE.md`), not lore voice — this is project record-keeping, not in-world
text.

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

**2026-08-05 to 09 — `/simulate` and the unattended-run problem.** `/simulate` was born to batch
`/enact` across a population, run inside a disposable worktree so a stress-test run couldn't touch
real files. What actually ate the most time in this stretch wasn't the simulation design — it was
getting a run to survive *unattended*, overnight, with no permission prompts: worktree settings
written before `EnterWorktree` instead of after, a relative-path leak that silently wrote real scene
content into the main checkout, `cd`-in-Bash hard-blocked with no override. Each one got documented
as its own fix rather than papered over, because the failure mode kept recurring in slightly
different shape until it was actually root-caused.

**2026-08-10 to 13 — Extended mode.** The base `/simulate` loop rendered correctly but converged too
heavily on epistemological chat with no material stakes — diagnosed as structural (character
composition, `/enact`'s trust mechanic being the only privileged dramatic payoff, small-pool
collision bias), not a prompting problem. The redesign that followed added routines, arcs with real
progressive state, reproduction, and death legacy — plus `/generate`, a separate scriptable fast-path
for seeding a multi-generation starting population without writing scenes for every step of it.

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
  circumstances (a shock, a death in the character's circle, a certain number of passages).
  Discussed as the natural next build after grounding; not yet wired into `/simulate` or `/enact`.
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

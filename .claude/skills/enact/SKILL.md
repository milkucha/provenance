---
description: Play a lore-only enacted character scene for Luminacion — against the player or against another enacted character — sampling each character's lore knowledge from _lore/encodings.json, then recording what the scene did to that lore (hearsay, criterion, life) and saving the scene's raw transcript to _npcs/scenes/<id>.md so /embody can convert it later, even cold. Purely lore-side otherwise: touches nothing under data/luminacion/ or the _npcs/ registries. Use when the user wants to enact/roleplay a character at the lore level. To also put the scene in the game (Blabber dialog, NPC registration, gestures), follow with /embody, or use /enact-embody to run both in one pass.
disable-model-invocation: true
---

Runs the lore half of the enactment procedure, plus the setup questions and record-keeping steps
below. Three rules govern every scene this skill plays: never invent as fact anything outside a
character's sample; personality and small texture are free to invent; keep every line short,
dialog-box length.

**Write dialogue only, no action cues.** A character's line is only what they say — no
asterisk-delimited stage directions (`*looks up from coiling a rope*`, `*grins*`, `*taps his temple*`)
anywhere in it. Personality comes through word choice and rhythm, not narrated gesture. This matters
here too, not just for the eventual Blabber file: `/embody`'s conversion step strips any stage
direction that slips in, so writing clean from the start avoids losing anything worth keeping.

Two things stay true throughout: a character never knows what another enacted character knows, even
when both are being played in the same scene — each is bounded strictly by their own sample. And per
`.claude/PRINCIPLES.md`, every genuine open question this skill can actually raise (education sample
topic, criterion collision, how the scene resolves) gets asked, never guessed. Minecraft-side open
questions — skin, UUID, movement mode, how a two-NPC dialog gets registered — are `/embody`'s concern,
not this skill's; it doesn't ask about them because it never touches that layer.

A character's knowledge comes in three kinds:

- **`facts`** — `_lore/facts/facts.json`. Universal: **every character knows every fact in full**,
  from creation, regardless of their education percentage. Facts are never sampled, never folded into
  `encodings.json`, never attributed, and never contestable — a character cannot have heard one
  wrong, cannot cite who told them, and cannot dismiss one. Load this file at the start of every run
  and treat its contents as standing knowledge for every character in the scene. See
  `_lore/facts/_index.md`.
- **`education`** — the sample drawn once at creation (Step 1/2), mirrored in
  `_lore/characters/<key>.json`'s `knowledge` object. Fixed for life: never redrawn, never hand-edited,
  on this run or any later one.
- **`experience`** — everything picked up by living through scenes: the `backstory` field (also
  experience-knowledge, conceptually, even though it stays its own top-level field since it predates
  this split) plus `knowledge.experience`, which keeps growing across every `/enact` run this
  character is ever part of again.

Two further fields on the same entry are not knowledge but govern how a character *acts* on it:
`criterion` (what they count as a life well spent) and `life` (`span`/`lived` — how many scenes they
have in them, and how many they've had). Both are owned by the `/character` skill
(`.claude/skills/character/SKILL.md`): Step 4 derives a criterion, Step 5 rolls a lifespan, Step 6 is
the reference for how a criterion changes. This skill points at those rather than restating them —
don't fork the procedure.

## Step 1 — First interlocutor

**Before anything else, slugify the name and look for `_lore/characters/<slug>.json`.**

- **If it exists:** check `life.deceased`. If it's `true`, this character has already had their last
  scene (Step 5b point 6) and cannot be enacted again, full stop — say so plainly and stop, rather
  than proceeding. They still exist in the world as whatever the notified circle now knows and
  whatever entered the discovery/sampling record; a new scene with them is not one of the ways that
  knowledge is allowed to grow.
- **If it doesn't exist, this is a brand-new character — run**
  `py scripts/lore/check_character_name.py "<name>"` **and confirm `AVAILABLE`** before treating it as
  one. This is the same shared uniqueness check `/character` Step 1 uses (every character ever
  created, living or deceased, must have a name that slugifies uniquely). On `TAKEN`, tell the user
  and ask for a distinguishing variant.

Ask, as plain conversation (not multiple-choice):

1. **Name.**
2. **Backstory** — optional. A user-given personal fact (like "family comes from somewhere else"),
   not a lore fact. Hold it as true for this character regardless of what their sample contains.
3. **Location** — optional. Where this character is based/found — fills the `city` field in their
   character file later. Not necessarily their backstory's place of origin (Sonoros's backstory has
   him "out of Görff way," but his registered `city` is Balehm, where the scene actually put him).
4. **Knowledge corpus** — how much of the lore they know, and how it's chosen. **First, check
   `_lore/characters/<slug>.json` for an existing file under this character's key.** If one exists with
   a `knowledge.education` already populated (`percent` not `null`), reuse it as-is — skip the
   percentage/mode/topic questions and the sampling script below entirely, and do not redraw.
   `education` is fixed at creation and never changes after; only `knowledge.experience` and the
   hearsay record (Step 5) are allowed to keep growing across later runs. If no file exists yet, or
   its `knowledge.education` is still the blank `_template` shape, proceed with the questions below:
   - Ask for a **percentage** (open number, e.g. "5", "11", "21").
   - Ask (AskUserQuestion, two options) whether the draw is **random** or **skewed toward a topic**.
   - If skewed, ask for the topic/keyword(s) (e.g. "geography and geology").

Then run the sample (skip this entirely if reusing an existing sample per the guard above):

```bash
py scripts/lore/sample_lore_knowledge.py --percent <N> --mode random
# or
py scripts/lore/sample_lore_knowledge.py --percent <N> --mode skewed --topic "<keyword>" --topic "<keyword2>"
```

Keep the printed list (or the reused list, for a returning character) — it's this character's
entire knowledge of the world for the rest of this run, and it goes into their character file in
Step 6 (or stays untouched there, if reused). Do not reveal the full list to the user unprompted (same
reasoning as §8: better discovered through play than read off a list), but you may describe its
general shape.

Some drawn items will be `category: "hearsay"` (a claim from an earlier dialog's hearsay entry, not
the objective record). Play those as things the character heard, not settled
fact. The moment one of these actually gets voiced in the scene (Step 3), roll
`scripts/lore/lineage_coin.py` right then — the result decides how the line is phrased: a `traceable`
roll lets the character cite the source by name ("I heard Morkulo say..."); an `untraceable` roll
means vague framing only ("they say...," "it's told that...") — no named source, on purpose. Keep
the roll result; it determines `derived_from`/`oral_lore` in Step 5.

### Criterion and lifespan

Still Step 1, once the sample is in hand — both fields live on the same character file and follow the
same first-time-only discipline as `education`:

- **Criterion.** If `criterion.standard` is blank and the character has both a backstory and a drawn
  sample, derive it now per `/character` **Step 4** (find the collision between the sample and the
  backstory/city, pick a refutable anchor, derive negatively from "what would this character consider
  a wasted life?", then derive `trusts`/`distrusts` from the anchor's category per Step 4d). If it's
  already set, **use it as-is** — never re-derive on a later run. If nothing collides, leave it blank
  with `"origin": "uncollided"` and log it in `TODO.md`; do not invent one and do not fall back to a
  city default (`/character` Step 4e).
- **Lifespan.** If the character has no entry in `_lore/characters/lifespans.json`, roll it now per
  `/character` **Step 5**. If they do, never reroll.
- **Horizon.** Run `py scripts/lore/horizon.py <npc_key>` for each character before the scene starts
  and keep the band (`early` / `established` / `late`) for Step 3. Ignore the `ending` line this
  script also prints — before a scene it always reads `false` (see the script's docstring for why),
  and it isn't the concern of the scene at all. It only matters afterward, at Step 5b point 6.

**Never open `_lore/characters/lifespans.json` during an enactment, and never pass `--verbose` to
`horizon.py`.** The span is kept in a separate file precisely so the number cannot end up in the
context of the character it belongs to; reading it here would defeat the whole arrangement. The band
is all you need and all you may have. Likewise never state a character's `lived`, band, or any
remaining count in a dialog line, an in-scene thought, or a narrated aside — they know life ends,
they do not know when.

## Step 2 — Second interlocutor

Ask (AskUserQuestion): is the second interlocutor **the player**, or **another character**?

- **The player:** ask (AskUserQuestion) whether to start the scene now. If yes, go to Step 3a.
- **Another character:** repeat every question in Step 1 for them — name, backstory, location,
  knowledge corpus, sample drawn the same way. Then ask (AskUserQuestion) whether to initiate the
  interaction now. If yes, go to Step 3b.

## Step 3 — How criterion and finitude modulate play

Applies to both 3a and 3b, on top of the ground rules already given above (never invent as fact
outside the sample; personality and texture are free; write short).

- **The criterion shows, it never gets recited.** It shapes what the character steers the
  conversation toward, what they can't let pass uncorrected, what they'd count as having wasted this
  encounter — not what they say about themselves. A character who explains their philosophy of life
  has been played wrong. Nobody announces their standard; they just keep acting like it's obvious.
- **Their `wasted_life` line is the sharper handle of the two.** It tells you what they're steering
  *away* from, which is usually more visible in a conversation than what they're steering toward.
- **Finitude is pressure, not a topic.** Every character knows their life ends (the `life_is_finite`
  fact). That shows up as impatience with what they consider a waste of an encounter, or willingness
  to say the thing now rather than later — not as talk about mortality. An `early` character can
  defer; a `late` one ranks harder and drops what doesn't matter.
- **Never write toward an ending.** Whether this happens to be a character's last scene is not
  knowable until after it's played (see `scripts/lore/horizon.py`'s docstring and Step 5b point 6) — so it
  is written exactly like any other scene, with no foreboding, no valediction, no character sensing
  anything is different. If the author independently wants a scene to carry a reflective or wistful
  tone, that's a legitimate craft choice, but it must be made on its own terms, never because the
  system signaled an ending is coming — structurally, it never can.
- **What they treat as authority follows from `trusts`/`distrusts`.** A character built on the
  chronicles cites what's written and asks where a story came from; one built on testimony names the
  person who told them and finds books bloodless; one built on a `conflict` distrusts anyone who
  sounds certain. This should be nearly invisible until two sources actually disagree in the scene —
  that's the moment it shows, and it shows as *which one they reach for*, never as a character
  explaining their theory of knowledge. Leave it alone entirely when both fields are blank.
- **Facts are never subject to any of this.** A character cannot doubt, attribute, or argue with
  something from `_lore/facts/`, no matter what they distrust.
- **Watch for anchor-touching claims as the scene runs.** Any time something said (by anyone) refers
  to a participant's `criterion.anchor`, note it — that's a shock candidate, and Step 5b resolves it.
  Don't resolve it mid-scene and don't let the character visibly recompute their life in dialogue;
  people don't do that out loud.

## Step 3a — Enact against the player

Play interlocutor 1 in character, turn by turn, waiting for the player's actual input each time —
same shape as the Sonoros conversation. Keep responses to 2–3 sentences. Continue until the user
signals the scene is over.

## Step 3b — Enact both characters

Write the full scene as one message, alternating clearly labeled turns, same shape as the
Nawom/Morkulo conversation — you write one side, then respond to yourself as the other, honoring
each character's own sample independently. Bring it to a natural stopping point rather than
running indefinitely, then check with the user before moving on: satisfied, or continue/adjust?

## Step 4 — Save the scene transcript

Immediately after the scene ends (3a or 3b), before Step 5 ever mutates or discards the original —
the same "record immediately, don't batch" discipline already in force for the hearsay entry, just
started one step earlier. Once Step 5 runs, only the mutated version survives; this is the only point
where the verbatim scene still exists to be saved at all.

**Choose the scene's id now** — the same slug this scene's eventual Blabber dialog file and hearsay
entry will use (e.g. `khaoe_milkucha_jardin_de_los_parajes`): participant keys plus a short location
slug, joined with underscores. Picking it here, once, means the transcript file, the hearsay entry
(Step 5 below — pass this id explicitly rather than letting the script auto-generate one), and the
dialog file `/embody` eventually writes all end up sharing one id by construction, not by coincidence.

Write `_npcs/scenes/<scene_id>.md` (`_npcs/scenes/_template.md` has the exact shape): participants,
location, format (`player-vs-npc` or `two-npc`), and the verbatim turn-by-turn transcript — dialogue
only, no action cues, per the ground rules already in force above (nothing to strip; it was never
written with any). This is the only file under `_npcs/` this skill ever writes — it still never
touches either registry or anything under `data/luminacion/`. The file stays under `_npcs/scenes/`
permanently, even after `/embody` converts it later — cheap to keep, and it's the only recoverable
source if a dialogue ever needs re-converting after an editing mistake.

## Step 5 — Update the hearsay record

**Cold start:** if `_lore/characters/hearsay.md` doesn't exist yet at all (a fresh project), run
`py scripts/lore/bootstrap_lore.py` before the first `record_hearsay.py` call — it writes the file's
explanatory header first, so the file doesn't start headerless with only a bare `## <dialog_id>`
entry and no framing prose above it. Safe to run even if some of the other four files this script
covers already exist; it only creates what's actually missing.

### Mutation at record time

**Record what each character internalized and understood, not what was objectively said.** When a
character hears, experiences, or learns something in a scene, the hearsay entry captures *their
mutated interpretation* of it, filtered through their `criterion`, `trusts`, `distrusts`, and
`wasted_life`. This is not error or noise — it's how knowledge actually travels: Farlis hears about
the Guerras and understands them as oppressive hierarchy; Auroboro III hears the same wars and
understands them as glorious sacrifice. Both understandings go into the hearsay pool. A future
character sampling from the pool gets the already-mutated version verbatim (no re-mutation at
sample time), and if *they* retell it later, their mutations compound.

Apply mutation at three levels:

1. **Framing.** How does this character interpret what they witnessed? Is it heroic or shameful?
   Justified or oppressive? Foolish or wise? The framing reflects their criterion's standard.
2. **Emphasis.** Which details does this character's criterion make matter? A character whose
   life is built on memory emphasizes *what was said*; one built on action emphasizes *what got done*.
3. **Moral judgment.** Is the other person trustworthy, foolish, trapped, enlightened? This flows
   from their `trusts`/`distrusts` and how the encounter tested their criterion.

Material mutations (when a character cites an era, location, or objective fact) work the same way:
record not just "they mentioned the wars," but *how they reframed it* — what emphasis, what judgment,
what specific framing did their criterion impose on the material. This belongs in the claims list
exactly as much as a hearsay-based retelling does.

**The original unmutated version is not recorded** (unless it had its own separate hearsay entry
elsewhere). Only the mutated versions enter the pool. This is why folklore fragments and
diversifies: each person's retelling reflects their own lens, and only their mutation survives.

---

This step is unconditional — it runs for every dialog produced this run, not only ones where a
character explicitly retold something sourced from a sampled hearsay item. A character's own fresh
invention (a venue description the user handed you, a personal theory, an on-the-spot guess) belongs
in the record exactly as much as an attributed retelling does — oral tradition is grounded in truth
as often as embellishment, and an unverified claim is not the same as a false one. Don't gate this
step on "did anyone say 'I heard X say...'" — that test only decides the two optional fields below,
not whether the step happens at all.

Build an entry for this dialog — participants, location, summary, and a `claims` list phrased as
reported assertions (not restated as fact), each with an `about` reference
into the objective arrays where it topically overlaps (a bare era name from `time_systems` is a valid
`about` target too, e.g. `"Era del Daax"`). Check each claim against the record and set
`inconsistent_with_record` (an array of `{about, source_kind, note}` — `source_kind` is
`material`/`tale`, naming which kind of objective source the contradicted entry rests on)
only if it genuinely contradicts something, and `inconsistent_with_facts` (a short string explaining
the contradiction) only if it contradicts one of the two entries in `_lore/facts/facts.json`. Leave
both unset in the ordinary case — that's most claims, and recording "no contradiction found" on every
one of them would just be noise; absence already means that. If a claim raises a genuine question the
objective record has never addressed at all (a gap, not a contradiction) and it resonates with the
existing corpus, log it in `_lore/unknowns.md`, cross-referencing the claim's id, matching the file's
existing shape — not every claim produces one, skip rather than manufacturing a question that isn't
genuinely there. Claims don't need to cover every sentence
spoken — capture the kernels: the ideas someone could plausibly repeat later, not the connective
tissue. A kernel that resurfaces across several entries (restated, elaborated, half-remembered)
naturally ends up with more copies in the sampling pool in `sample_lore_knowledge.py` — that's the
actual mechanism by which an idea becomes folklore and keeps mutating, not a special flag to set.

Two more fields, both optional, both only relevant when this dialog surfaced a claim that came from
a *sampled hearsay item* rather than a fresh read of the objective record (Step 1's note above):

- `derived_from` — the earlier claim's id (`"<hearsay_entry_id>#<n>"`) that this claim grew out of.
  Set it only when Step 1/3's `lineage_coin.py` roll came up `traceable` — that's what makes the
  claim traceable as a retelling rather than an independent report. On an `untraceable` roll, leave
  this unset even though you (the one running the skill) know perfectly well where it came from —
  the character's dialog line didn't cite it, so the record shouldn't either.
- `oral_lore` — `true` whenever the roll came up `untraceable` (no origin on record at all — this
  claim is now folklore, full stop), **or** when a claim that did stay traceable has still grown to
  include specifics that outrun what its `about` grounding actually supports — a new name, a cause,
  a number that isn't in the referenced objective entry. Either way, pair it with a `note` explaining
  which case applies and, for the growth case, what specifically grew. Leave both fields off
  entirely for the common case — a claim freshly drawn from the objective record, or a faithful,
  traceable retelling with nothing added.

Use the same `id` chosen in Step 4 for this entry — pass it explicitly in the JSON (`record_hearsay.py`
only auto-generates one when `id` is omitted, and an auto-generated id could drift from the transcript
filename already on disk).

Once the entry is built, write it to a JSON file (see `record_hearsay.py`'s own docstring for the
exact shape) and run `py scripts/lore/record_hearsay.py --json-file <path>` to record it — it appends
the entry to both `_lore/characters/hearsay.md` and `encodings.json`'s `hearsay.entries` in the same
shape as the existing entries, generates a consistent `id`, and validates both files still parse as
JSON afterward. Everything above this point (what a claim says, how it mutated, which flags apply) is
still entirely yours to decide — the script only owns getting the decided content into the two files
correctly, the mechanical half that used to be a hand-edited JSON diff every single run.

## Step 5b — Resolve shocks, drift, and the scene count

Runs after Step 5 because Step 5's `claims` list is the input. For every character enacted this run:

**1. Reference gate.** For each claim just recorded (and for what the character actually lived
through in the scene), check whether it **references that character's `criterion.anchor`** — same
case, same person, same event, using the claim's `about` refs. This is a pointer comparison, not a
judgment about how upsetting something was. **Never score intensity; there is no magnitude scale
here on purpose.** Run `py scripts/lore/check_anchor_reference.py <npc_key> --hearsay-id <entry_id>`
to do this check mechanically instead of eyeballing every claim's `about` field against the anchor
string — it reports exactly which claims (if any) matched. A claim that doesn't reference the anchor
is news, however dramatic, and stops here.

**2. The default is no change, and it will be the answer almost every time.** Most scenes move
nobody's criterion. Only continue past this point when the gate in (1) actually matched.

**3. Resolve, per `/character` Step 6** — three moves, not a degree: **reject the claim**, **accept
and reinterpret** (increment `criterion.tempered`), or **accept and break** (clear
`standard`/`wasted_life`, leave blank — no replacement, the gap is the point). Weigh provenance,
proximity, and susceptibility; bias toward reinterpretation. Temperament isn't built yet
(`/temperament`, see `TODO.md`), so don't pretend to consult it.

Dismissal is gated by the claim's recorded credibility (`traceable` + no `inconsistent_with_record`/
`inconsistent_with_facts` flag is hard to wave away; `oral_lore`, or a claim that IS flagged
inconsistent, is easy) **combined with whether this character trusts that kind of knowing at all**
(`criterion.trusts`/`distrusts`). Credibility is not objective to the
character: a weak claim from a source they trust can land, and a well-sourced one from a source they
distrust can be waved off — at the usual cost of knowingly carrying something the record contradicts
and retelling it anyway. If both trust fields are blank, judge on credibility alone.

Then update trust per `/character` Step 6: surviving a refutation hardens `distrusts` against the
kind of source it came from; a break usually swings the character the other way. Leave both fields
untouched when the outcome was "no change."

Once the move is decided, record it (and the life.lived increment from point 5 below) in one call:

```bash
py scripts/lore/update_character.py <npc_key> --lived-delta 1 \
    --criterion-move reject|reinterpret|break --dialog <scene id> --cause "<claim id + what it claimed>" \
    --note "<why this move>" [--trusts "..."] [--distrusts "..."]
```

This appends the `criterion.history` entry, increments `tempered` on a reinterpret, clears
`standard`/`wasted_life` (keeping the old values in `history`) on a break, and updates
`trusts`/`distrusts` if given — the outcome you already decided, written correctly, once. Skip
`--criterion-move` entirely on "no change" — nothing here runs then, per point 2 above.

**4. Drift bookkeeping.** If honoring the criterion cost the character something in this scene — time,
a relationship, a chance they passed up, a thing they couldn't say — append one short line via
`py scripts/lore/update_character.py <npc_key> --cost-ledger "<what it cost>"` (combine with
`--lived-delta`/`--criterion-move` in the same call above if this is the same character). This never
changes the criterion by itself; it raises susceptibility for later shocks. Skip it when nothing was
actually paid.

**5. Increment `life.lived` by 1** for every character who was in the scene — `--lived-delta 1` on
`update_character.py`, folded into whichever call above already touches that character, or on its own
(`py scripts/lore/update_character.py <npc_key> --lived-delta 1`) when nothing else changed for them
this scene.

**6. Now, and only now, run `py scripts/lore/horizon.py <npc_key>` again and check `ending`.** Before
Step 5 it could only ever read `false`; now that `life.lived` reflects the scene just played, it can
truthfully say the character's life is complete. If it does, that scene — already written, already
closed, with nothing in it played any differently — turns out to have been their last. Nothing about
the scene itself changes retroactively; only what happens next does. The character must not be
enacted again: `knowledge.experience` is closed, no further `/enact` run may include them, and they
survive from here only as other people's hearsay — which the record already supports, since every
claim they ever made is still in the pool for future characters to draw. Note the ending in `TODO.md`
along with anything it leaves open (a dialog that assumed they'd be available, an NPC still to be
spawned). Tell the user plainly that this character has had their last scene; don't bury it.

Death propagates in two tiers — a guaranteed circle and everyone else — rather than being announced
to the world at large. Run:

```bash
py scripts/lore/record_death.py <npc_key> [--cause "<only if the scene actually established one>"]
```

This does the entire mechanical procedure in one call: sets `life.deceased: true` on the character's
file (a plain, non-secret fact — unlike `life.span`, nothing about death itself is hidden, and it's
what stops a future `/enact` run from accidentally reusing them, see the Step 1 guard below); records
it as an objective fact of the world in the same shape `/tell` produces (a new
`_lore/tales/<slug>.md` file, a matching `tales.entries` manifest row in `encodings.json`, and rows
in `_lore/tales/_authors.md`/`_index.md`) — this is what makes death re-enter the ordinary sampling
pool for characters created later, at ordinary odds, the *only* channel anyone outside the circle
below has; computes the character's *circle* (everyone they've shared a recorded scene with, plus
everyone named in their own backstory) and mechanically samples 30% of it (minimum 1 if the circle
isn't empty) as who learns immediately; and appends a plain "learned of the death" line to every
notified character's `knowledge.experience` — reported fact, no attribution needed, written
immediately regardless of whether that character is ever enacted again soon.

The one thing the script does **not** do, and prints back to you explicitly, is flag which notified
characters are shock candidates (their `criterion.anchor` references the deceased directly, same
scene, same hearsay entry — a pointer check the script makes for you). **For every one of those,
resolve it now, per `/character` Step 6** — the same reject / accept-and-reinterpret / accept-and-break
judgement as point 3 above, using the news itself as the shock ("lived falsification... the
character's own experience referencing their own anchor" already covers this) — via
`py scripts/lore/update_character.py <npc_key> --criterion-move ... --dialog ... --cause ...` exactly
as point 3. This is real judgement, not mechanical — the script only tells you *who* qualifies, never
how they take it.

**Everyone the script did not notify simply doesn't know yet.** Don't write anything for them. They
find out later only the ordinary way: sampled into a new character's education, or told by someone
from the circle in a future scene (subject to the usual `lineage_coin.py` traceable/untraceable
rule on that retelling, same as any other claim).

## Step 5c — Synthesis: characters forming their own theories

Runs immediately after Step 5b's shock resolution, same "reflect on what this scene did" position. For
every character enacted this run:

**1. Candidate gathering (mechanical).** Run `py scripts/lore/check_resonance.py <npc_key> --hearsay-id
<entry_id>` — it checks all five subtypes at once and reports candidate pairs (one fresh-this-scene
item, one standing-knowledge item) per subtype, using each subtype's own mechanical filter (shared
`about` id, name-string similarity, shared `CONFLICT-NN` tag, 3+ frequency with a fresh tipping
instance, shared person). It reports pairs only — it never judges whether a pairing actually means
anything.

**2. The default is nothing, and it will be the answer almost every time** — same discipline as Step 5b
point 2. Most reported candidates should produce no synthesis. Only continue past this point for
candidates the script actually surfaced.

**3. Judge each surviving candidate.** Does pairing it raise a gap or tension neither item states alone
— not agreement, not restatement? This is real judgment, same division of labor as everywhere else in
`/enact`: the script narrows, the model decides.

**4. Criterion gates and flavors.** A character's `criterion.trusts`/`distrusts` biases whether a
candidate fires at all (a character who distrusts the kind of connection being drawn synthesizes less
readily) and colors the tone of the text when it does fire (skeptical hedge vs. confident, connective
framing). A character with no derived criterion yet synthesizes plainly.

**5. Credibility inheritance.** The synthesized claim inherits the *weaker* of its two parents'
credibility — built on a shaky/uncorroborated parent, it comes out hedged ("maybe," "it makes me
think"), not asserted. Reuses the existing `oral_lore`/traceable ledger; no new certainty scale.

**6. No cap.** Every candidate that survives points 3–5 gets written, however many that is this scene.

**7. Identity-subtype special case.** When an identity-type synthesis fires, check it against
`conflicts`: a match means the character independently caught a real structural ambiguity — worth
noting as such. No match is a riskier, unbacked guess, held more tentatively (possibly its own
`unknowns.md` entry if it resonates with the corpus, same "not every claim produces one" discipline as
Step 5).

**8. Write each surviving synthesis** to `knowledge.experience`:

```bash
py scripts/lore/update_character.py <npc_key> --add-synthesis \
    --about "<A>" --about "<B>" --text "<synthesized claim text>"
```

(repeatable per synthesis this scene) — stored as `{"kind": "synthesis", "about": [A, B],
"derived_from": [A, B], "text": "..."}`, appended alongside the plain-string entries
`knowledge.experience` already holds. Stays private unless the character actually voices it in a later
scene, at which point it becomes an ordinary hearsay claim through the existing Step 5 recording path —
no new sampling-pool machinery.

`knowledge.experience` held plain strings only before this; synthesis entries (`kind: synthesis`) and
grounded entries (Step 6's `--add-grounded-experience`, no `kind` key) are both object-shaped, so
anything iterating the list (Step 6's cross-check, future exports) needs an `isinstance(entry, dict)`
check, and a dict check needs `entry.get("kind") == "synthesis"` to tell the two apart. See `TODO.md`'s
"Synthesis mechanism" entry for the full subtype breakdown (worked examples, each mechanical
pre-filter) and design history.

## Step 6 — Update the character record

For every character enacted this run, add/update their file at `_lore/characters/<key>.json`
(key = lowercased, slugified name). **`criterion` and `life` are typically already written** by the
`update_character.py`/`record_death.py` calls made during Step 5b — don't hand-edit those fields again
here, since a fresh JSON write could clobber what those calls just did. What's left for this step:

- `name` — set once, for a first-time character. Never rewritten on a returning character.
- `city` — the location from Step 1/2, or `""` if none was given.
- `backstory` — the backstory from Step 1/2, or `""` if none was given. Experience-knowledge,
  conceptually (see the intro), but its own top-level field. For a returning character, only append
  or amend this if the user gives *new* backstory in this run (as with Döran's added hologram/pedestal
  detail) — don't touch it otherwise.
- `knowledge.education` — `{percent, mode, topic, items}` exactly as drawn by the script in Step 1/2,
  for a first-time character. For a returning character reusing an existing sample (per the guard in
  Step 1), **leave this field untouched** — never redraw or overwrite it on a later run.
- `knowledge.experience` — anything that came up in the scene beyond the original sample: personal
  texture established for this character (something they revealed about themselves, an action they
  took), or — for the *other* character in a two-NPC scene — anything they said or did that this
  character would now plausibly have picked up just from being present. Both directions and both
  speech and witnessed action are in scope — per Step 5's "Mutation at record time," a claim captures
  *what got done* as much as *what was said*, so this isn't limited to things the character was told.

  **Cross-check against the hearsay entry's `claims` from Step 5, and when the experience entry
  describes the same fact as a claim, reuse that claim's `about` ref** rather than writing a plain
  string — this is what lets `check_resonance.py` (Step 5c) find it later. Real example: Aureobalo
  voicing his own backstory ("Told Farlis, for the first time aloud, that his surname resembles the
  losing side of the Guerras de Gorff...") is both his own experience entry *and* claim #6 of
  `aureobalo_farlis_castillo_en_miniatura`, `about: "Las Guerras de Gorff"` — the experience entry
  should carry that same ref:

  ```bash
  py scripts/lore/update_character.py <npc_key> --add-grounded-experience \
      --about "<ref, repeatable if the entry draws on more than one claim>" --text "<entry>"
  ```

  Some experience entries genuinely have no claim to point to — a narrated action nobody voiced (e.g.
  Aureobalo "postponed his drive back to Khol Moshin by a day to stay a second day at the Feria," which
  no hearsay claim anywhere records). That's a legitimate outcome, not a recording failure — write
  those with plain `--add-experience` instead, unchanged:

  ```bash
  py scripts/lore/update_character.py <npc_key> --add-experience "<entry>" [--add-experience "<entry 2>"...]
  ```

  Either call is repeatable per entry (one `--add-grounded-experience` call per grounded entry;
  `--add-experience` takes several at once) — fold whichever apply into the same Step 5b call for this
  character when there is one, rather than a separate write. Both append to the existing list; a
  returning character's prior entries are never touched or retroactively grounded.
- `criterion`/`life` — already handled by Step 5b's `update_character.py`/`record_death.py` calls for
  every character whose criterion changed, cost something, or advanced `life.lived`/`life.deceased`
  this scene. Only touch these fields by hand for a first-time character's *initial* criterion (the
  whole object as derived in Step 1) — never re-derive on a later run, and never re-write what a
  script call already recorded.
  If this run rolled a first lifespan (Step 1), the span went into
  `_lore/characters/lifespans.json`, never here.

This is the last step `/enact` performs — nothing here (or anywhere in this skill, past Step 4's
transcript) touches `_npcs/npcs/registry.json`, `_npcs/dialogs/registry.json`, or any file under
`data/luminacion/`. To convert this scene into a registered Blabber dialog, register the NPC(s) in the
Minecraft layer, and bake gestures, run `/embody` now (it reads the transcript Step 4 saved to
`_npcs/scenes/<scene_id>.md`, so this works whether run right away or picked back up cold, in a later
session), or use `/enact-embody` next time to run both skills back to back in one pass.

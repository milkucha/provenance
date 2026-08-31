---
description: Create or update a character's entry in _lore/characters/<key>.json — backstory, location, knowledge, criterion, and lifespan — without running a full /enact conversation. Use when the user wants to flesh out a character's sheet on its own, ahead of (or instead of) enacting a dialog.
disable-model-invocation: false
---

Lighter-weight sibling of `/enact` Step 1/Step 6: this skill only maintains a character's file in
`_lore/characters/<key>.json` — purely lore, no Minecraft-facing field anywhere in it. It never
touches `_npcs/npcs/registry.json`, `_npcs/dialogs/registry.json`, or writes a dialog file — a
character can exist here fully fleshed out with no in-game representation at all. If the user wants an
actual conversation, point them at `/enact` instead once the sheet is in good shape; if they want this
character embodied in-game, that's `/embody` or `/spawn`, never this skill.

This skill also **owns the criterion model** (Steps 4 and 6 below). `/enact` derives and revises
criteria by pointing back here rather than restating the procedure — keep the canonical version in
this file and don't fork it.

## Step 1 — Name

Ask for the character's name. Slugify it (lowercase, diacritics folded, non-alphanumerics →
underscore — see `scripts/lore/check_character_name.py`) and look for `_lore/characters/<slug>.json`.

If no such file exists, this is a brand-new character — **before proceeding, run**
`py scripts/lore/check_character_name.py "<name>"` **and confirm it reports `AVAILABLE`.** This is the
single shared enforcement point for name uniqueness (`/enact` Step 1 calls the same script the same
way) — every character ever created, living or deceased, must have a name that slugifies uniquely. If
it reports `TAKEN`, tell the user and ask for a distinguishing variant (a surname or epithet — e.g.
`"Character C Gorfalis"` alongside an existing `"Character C"` is fine, since they slugify differently). Skip
this check entirely when the file already exists — that's Step 2a, not a new name.

## Step 2a — Existing entry

If the file exists, show the user its current non-blank fields (`name`, `origin`, `location`,
`backstory`, `knowledge.education` summary if populated, `knowledge.experience` count,
`criterion.standard`, `life.lived`, whether `routines`/`arc` are set, and `scripts/lore/horizon.py`'s
band) as context, then ask, as plain conversation, what needs to be updated.
Don't presuppose which fields — the user might want to amend the backstory, add/change the
origin/location, draw or redo their knowledge, or just fix a typo.

- **Backstory** — if the user is adding to an existing non-empty backstory, append/amend rather than
  replace, same as `/enact` Step 6. If they're giving it fresh, just set it.
- **Origin** — where this character was born/from. Fixed once set, same discipline as
  `knowledge.education` — a birthplace doesn't change. The one exception is a corrective: if the user
  says it was simply wrong, fix it in place (same exception `criterion` gets below).
- **Location** — where this character currently is. Unlike `origin`, set freely from whatever the
  user says, any time — this is expected to move as the character's story does (see `/enact` Step 1,
  which updates it whenever a scene actually places the character somewhere).
- **Knowledge** — if `knowledge.education.percent` is already set (non-null), never redraw it; that
  field is fixed for life. Only offer to draw it if it's still the blank `_template` shape
  (`percent: null`) — follow the sampling flow in Step 3 below. `knowledge.experience` only grows
  through actually living a scene (`/enact`), so don't hand-invent entries for it here.
- **Criterion** — if `criterion.standard` is blank and the character now has both a backstory and a
  drawn education sample, derive it (Step 4). If it's already set, **do not re-derive it here.** A
  criterion changes only through a shock in a lived scene (Step 6), never by being recomputed on a
  sheet edit. The one exception is a corrective: if the user says the derivation was simply wrong,
  fix it in place and note the correction in `criterion.history` with `"cause": "author correction"`.
- **Lifespan** — if the character has no entry in `_lore/characters/lifespans.json`, roll it (Step 5).
  If they do, never reroll.
- **Routines and arc** — required on every character going forward (Step 2b item 4), so a character
  reaching this step still missing either is a pre-2026-08-28 character, or one that arrived some
  other way (`/enact` directly, or a `generate_offspring.py` newborn). Offer to author them now (Step
  8) — this is what makes the character eligible to face another character in `/enact` or take part
  in `/simulate`. This is the system's backfill path for an incomplete character, not a separate
  mechanism. Once authored, never redrawn/re-derived in this step; only `/enact`'s own mechanical
  block advances `arc` further from here.

## Step 2b — New entry

If no file exists for this slug, this is a brand-new character — confirm the Step 1 uniqueness check
came back `AVAILABLE` before going any further. Ask, as plain conversation (not multiple-choice):

1. **Backstory** — optional.
2. **Origin** — optional, fills `origin`. Where this character was born/from — this is the one
   question this skill asks at creation time; `location` (where they currently are) isn't asked here
   and defaults blank, since it's ordinarily set later by whatever scene first actually places the
   character somewhere (see `/enact` Step 1). If the user volunteers a current location too, set both.
3. **Knowledge** — how much of the lore they know. Follow the sampling flow in Step 3.
4. **Routines and arc — required (2026-08-28), not optional.** Follow Step 8 below. When asking the
   user to pick a context, list every context in `_lore/contexts.json` by name with a short (2-3 word)
   gloss of its texture — not the full `texture` paragraph — so the question stays scannable.

Then run Step 4 (criterion), Step 5 (lifespan), and Step 8 (routines/arc) before writing the entry.

## Step 3 — Knowledge sampling (shared)

Only runs when education knowledge is being drawn for the first time (new entry, or an existing entry
whose `knowledge.education` is still blank):

- Ask for a **percentage** (open number, e.g. "5", "11", "21").
- Ask (AskUserQuestion, two options) whether the draw is **random** or **skewed toward a topic**.
- If skewed, ask for the topic/keyword(s).
- Run:
  ```bash
  py scripts/lore/sample_lore_knowledge.py --percent <N> --mode random
  # or
  py scripts/lore/sample_lore_knowledge.py --percent <N> --mode skewed --topic "<keyword>" --topic "<keyword2>"
  ```
- Keep the printed list — it goes into `knowledge.education.items` in Step 6. Don't reveal the full
  list to the user unprompted; you may describe its general shape.

## Step 4 — Derive the criterion

A **criterion** is what this character counts as a life well spent. It is not a personality trait and
not a goal — it's the standard they measure their own life against, and it's what makes two
characters with the same knowledge in the same situation choose differently.

Every character wants their life to be worthwhile and knows it will end: those are the two universal
facts in `_lore/facts/facts.json`, which every character knows in full regardless of their education
percentage (read that file before deriving — and note it is deliberately outside `encodings.json` and
must never be sampled). The facts supply the *impulse*. The criterion is this character's particular
answer to it, and unlike the facts, it can be argued with, defended, and lost.

Only derive when the character has **both** a backstory and a drawn `knowledge.education` sample.
Without both there's nothing to collide, so leave `criterion` blank and say so.

### 4a — Find the collision

Scan `knowledge.education.items` for entries that touch the `backstory`, `origin`, or `location` —
same place, same trade, same family, same route, same wound. Those three fields are the collision
surface; an item that touches none of them is just something the character knows, and can't ground a
standard for *their* life.

**Do not derive from the whole sample.** "Given these forty facts, what does she live for" produces a
balanced synthesis, which is mush. The derivation has to anchor to one thing.

### 4b — Pick the anchor

From the colliding items, pick one **case**: something concrete and singular that a standard can be
read off. A person and how they lived is the clearest kind, but it does not have to be a person — an
event, a place, a founding, a practice, a catastrophe all work.

The one hard requirement: **the anchor must be something that could turn out to be wrong.** "The sea
provides" is a usable anchor because a famine refutes it; "freedom matters" is not, because nothing
can. That refutability is what makes the criterion contestable later (Step 6), and it's what keeps
the whole model from drifting into characters who walk around espousing philosophies.

Record the anchor as the item's id from the sample (`hearsay: <entry>#<n>`, `location: <id>`,
`character_legendary: <id>`, `inhabitant: <name (locality)>`, ...) so a later claim can be checked
against it by reference.

### 4c — Derive negatively

Now ask, with exactly four inputs — the anchor, the backstory, the origin, the location:

> **What would this character consider a wasted life?**

Ask it in that direction, not "what does this character value." The positive form reliably produces
abstractions ("authenticity", "connection") that are useless at runtime. The failure condition is the
operative half: it's what makes a decision come out one way rather than another. Write it in the
character's own concrete terms, referring to the anchor.

Then state the positive `standard` as the short complement of it. Both stay one line.

Good: `wasted_life: "one spent somewhere easier than where you were needed"` /
`standard: "counts leaving the work as failure"`.
Bad: `standard: "values duty and perseverance"` — that's a description of a person, not a measure
they hold themselves to.

### 4d — Derive what they trust

A criterion implies an epistemology. What a character believes a life is *for* shapes what they'd
trust to tell them how to live it — so the same anchor that gives them a standard also gives them a
lean about which **kind of knowing** carries weight.

**Derived from provenance, and only provenance (design correction, 2026-08-16)** — knowing something
because it's `material`, because it's `hearsay`, or because it's a `tale` is the entire signal. This
replaced an earlier pool-category-based table (ambiguous/chronicles/conflict/hearsay groupings) that
never actually worked: two items in the same pool category — two locations, say — can have completely
different provenance, which a category-level classification could never express.

Run `py scripts/lore/anchor_epistemology.py "<anchor>"` to resolve it mechanically — the script only
computes the signal, same discipline as every other script in this pack. Four cases:

1. **The anchor's own category already IS a provenance.** `hearsay: <entry>#<n>` resolves trivially to
   `hearsay` — the item *is* a hearsay claim. `tale: <id>` resolves trivially to `tale`. No lookup.
2. **`conflict: CONFLICT-NN` is a fixed special case, outside this system entirely** — a conflict is
   definitionally two sources disagreeing, not sourced from one provenance itself, so it doesn't get
   a material/hearsay/tale derivation at all. Kept exactly as before: `trusts: "verification"` /
   `distrusts: "anyone who sounds certain"`.
3. **An `experience` entry is also a fixed special case**, for the same structural reason: it lives in
   the character's own file, not in `encodings.json`, so there's no `sources[]` to resolve at all —
   it's the character's own firsthand witness, full stop. Kept exactly as before: `trusts: "firsthand
   presence"` / `distrusts: "anything nobody present can vouch for"`.
4. **Everything else** (`location`, `concept`, `era_*`, `character_*`, route/airport categories, ...) —
   the script reads the item's own `sources[]` array and reports the *first-recorded* entry's
   category. `sources[]` is append-only (`build_source_index.py` only ever adds hearsay/tale
   backlinks onto what's already there), so "recorded first" means "what actually established this
   in the record" — not an arbitrary pick among however many backlinks have since accumulated.
   Checked against real mixed-provenance data: City B carries 5 `material` sources (what actually put
   it on the map) plus 10 `hearsay` backlinks (later conversations that happened to mention it) — the
   script correctly reports `material`, ignoring the later backlinks regardless of their count.
   If `sources[]` is empty (a freshly arc-authored concept with no link yet), the script says so
   plainly — **leave `trusts`/`distrusts` blank rather than guess**, same discipline as
   `origin: "uncollided"` elsewhere in this file. A character with no particular epistemology is
   perfectly normal.

**Do not derive this from which category the character holds most of, and do not use
`baseline_stats.py` for this anymore** — that script backed the old ambiguous-category tiebreaker,
which no longer exists now that every anchor resolves to a definite provenance (or genuinely has none
to derive from). Raw distribution across a character's sample measures how it was drawn (a
`--mode skewed` topic), not who the character is — that critique of category-counting still holds,
it's just no longer solved by a tiebreaker script, since there's no tie left to break.

Write `trusts` and `distrusts` as one line each, in the character's own terms, the same way
`standard`/`wasted_life` are written:

| Provenance | Trusts | Distrusts |
|---|---|---|
| `material` | what's written down and can be checked against the record | a claim with no paper trail, however sincerely told |
| `hearsay` | a name attached to a story — someone who was there and can be asked | the written record, as bloodless or secondhand |
| `tale` | a story that's been carried and retold and still holds together | a record that insists on a precision no one who was actually there ever needed |

`tale` is deliberately its own row, not folded into `hearsay` — a tale is *objective truth* (told
directly by the world's author, never subject to the `inconsistent_with_record` doubt a hearsay claim
can carry) even though it arrives through oral narrative rather than documented material, closer to
myth than to gossip. Fold it into `hearsay`'s row and that distinction disappears.

Three hard limits:

- **Facts are exempt.** A character cannot distrust a fact (`_lore/facts/`). That is what makes facts
  the floor rather than part of the argument, and this mechanic must never erode it.
- **This never changes what a character knows.** It changes what a claim *weighs* when it collides
  with something else. Their `education` sample is untouched.
- **It's a lean, not a rule**, and it should mostly be invisible until two sources actually conflict.
  A character who announces their theory of knowledge is as badly played as one who recites their
  criterion.

### 4e — When nothing collides

If no item in the sample touches the backstory, origin, or location, **do not invent a criterion and
do not fall back to a place-level or trade-level default** — inherited criteria are a real part of the model but
are deliberately not built yet (see `TODO.md`). Leave `criterion` blank with
`"origin": "uncollided"`, and log the character in `TODO.md` as awaiting one. Same rule as
`.claude/PRINCIPLES.md`: nothing gets decided silently.

## Step 5 — Roll the lifespan

Only when the character has no entry in `_lore/characters/lifespans.json`. Once rolled, never
rerolled — same discipline as `knowledge.education`.

```bash
py scripts/lore/roll_lifespan.py
# or, to reach a character's last scene quickly while testing:
py scripts/lore/roll_lifespan.py --min 2 --max 4
```

**The span goes in `_lore/characters/lifespans.json`, never in the character's own file.** This is
structural, not stylistic: the character's own file is what `/enact` loads in order to *play* them, so
a span sitting there would put the number in that character's own context at exactly the moment it
must not be. Keeping it in a separate file that the enactment never opens is what actually makes it
inaccessible; a written rule alone did not.

The character file's `life` object therefore holds only `lived` — how many scenes they've had, which
is just their history and no secret at all.

Anything that needs to know how far through a life a character is asks `scripts/lore/horizon.py`, which
answers with a coarse band and never the number:

```bash
py scripts/lore/horizon.py <npc_key>     # -> band: early | established | late, plus ending: true|false
```

`--verbose` will print the raw span, and exists only for author-side bookkeeping like this step.
Never use it during an enactment.

The default range is **30–60** (author decision, 2026-07-31). If the user asks for a different range,
use their numbers and record them in that character's `range` field in `lifespans.json`, so it's
clear later why one character got three scenes and another got fifty.

**Backfilling `lived` for a character who already has a history.** `life.lived` starts at 0 only for
a genuinely new character. For one who predates these fields, count the scenes they have actually
been in: **one `encodings.json` `hearsay.entries[]` record is one scene**, so `lived` is the number
of entries listing them in `participants`. (Match on the display name including diacritics — `Character E`
and `Iläria` won't match an ASCII search.) Don't count `knowledge.experience` lines; several of those
can come out of a single scene. Run `py scripts/lore/backfill_lived.py <npc_key>` to do this count
instead of searching the array by hand — it also checks the count against the rolled `span` and tells
you directly if a reroll is needed. If a backfilled `lived` would meet or exceed the rolled `span`, roll
again with `--min <lived+1>` — the character is demonstrably still alive after that many scenes, so a
span at or below their history is simply wrong, and this is the one case where rerolling is correct.

## Step 6 — Reference: how a criterion changes

Not run on a sheet edit — this is the model `/enact` applies after a scene, kept here because this
skill owns the criterion. Do not re-derive a criterion from the sample; it changes only like this.

**A criterion changes only when a shock lands on a susceptible character.** Two separate things:

**Shocks** are events, and the gate is *reference, not intensity*. A claim (or a lived experience)
qualifies as a challenge only if it **references the anchor** — same case, same person, same event.
That's a pointer comparison against `criterion.anchor`, using the `about` refs the hearsay record
already carries. Anything else, however dramatic, is not a challenge to *this* criterion; it's news.
Never try to score how radically something challenges a standard — there's no magnitude scale here on
purpose.

Once a claim passes that gate, there are exactly three moves, and the outcome is **one of three, not
a degree**:

1. **Reject the claim.** The refutation never lands because it isn't believed. Gated by two things
   together:
   - *The claim's own credibility*, already recorded: a named, `traceable` source whose claim carries
     no `inconsistent_with_record`/`inconsistent_with_facts` flag is hard to wave away; an
     `oral_lore`/`untraceable` "they say," or a claim that IS flagged inconsistent, is easy.
   - *Whether this character trusts that kind of knowing at all* (`criterion.trusts`/`distrusts`,
     Step 4d). **Credibility is not objective to the character.** Someone whose life is built on
     testimony finds an unattributed "they say" more moving than a chronicle that contradicts it, and
     will reject the chronicle; someone built on the record does the reverse. Combine the two — a
     weak claim from a trusted kind of source can still land, and a strong one from a distrusted kind
     can still be waved off.

   Rejection is **not free** — the character now knowingly holds something the record contradicts,
   and will go on retelling it. That's denial becoming folklore, and it needs no new machinery.
   Rejecting on epistemology rather than evidence is the most common way a character ends up doing
   this, and it should be recorded exactly the same way.
2. **Accept the claim, keep the criterion.** Reread the case rather than abandon it ("so she suffered
   for it; that makes it worth more, not less"). This is the common outcome for a strong claim, and
   it **tempers** the criterion: increment `criterion.tempered`. A high count means later shocks
   bounce off — characters who've been tested become rigid.
3. **Accept and break.** The criterion loses its footing. Clear `standard`/`wasted_life`, keep the
   old values in `history`, and **leave it blank** — do not immediately issue a replacement. A
   character between criteria is adrift and maximally susceptible to adopting someone else's, which
   is exactly when conversion happens. That gap is a state worth playing, not a hole to patch.

**Trust shifts with the outcome, and it's the one part of the criterion that moves without a break.**
A character who survives a refutation that came from a given kind of source hardens against that
kind — amend `distrusts` and note it in `history` with `"move": "reinterpreted"`. A character whose
criterion breaks because of a source they'd been dismissing usually swings the other way, and their
new `trusts`/`distrusts` are derived fresh alongside whatever criterion eventually replaces it. Don't
touch these fields when the outcome was "no change."

**Drift** is accumulation, and it does **not** change the criterion by itself — it changes
*susceptibility*, i.e. whether an arriving shock lands at all. Two contributors:

- `criterion.cost_ledger` — one short line per scene where honoring the standard cost the character
  something. A long ledger means they've been bleeding for this for a long time.
- The horizon: `scripts/lore/horizon.py <key>`'s band, read against the scale of what the criterion
  demands. A character whose standard needs a lifetime and comes back `late` is ripe; one at `early`
  is armored. Use the band, never a remaining count — the count is not available to an enactment by
  design.

Same refuting claim, same anchor: bounces off a character who's been paid well for their criterion,
breaks one who's been paying for it for years.

**Proximity** — how much of the self is invested in that particular anchor (their own family's story
versus an admired stranger's) — pushes both ways: high proximity makes the character fight harder to
reject the claim, *and* does more damage if it lands anyway. Read it off the backstory.

**Lived falsification counts as a shock** even though it isn't a claim: honoring the criterion and
getting misery, or violating it and finding nothing broke. That's the character's own experience
referencing their own anchor, so it passes the same gate.

**Not yet built: temperament.** The disposition governing move 2 versus move 3 when a strong claim is
accepted — whether a cornered character rebuilds the meaning or lets it go — is deferred to a future
`/temperament` skill (see `TODO.md`). Until it exists, decide between reinterpretation and breaking
on provenance, proximity, and susceptibility alone, and bias toward **reinterpretation**: breaking a
criterion should stay rare enough that when it happens it's the event of that character's life.

## Step 7 — Write the character file

Update (or create) `_lore/characters/<slug>.json`:

- `name` — the character's name, if not already set. This is the canonical name — if the character is
  later embodied in-game (`/embody` or `/spawn`), it gets copied into
  `_npcs/npcs/registry.json`'s `display_name`/`taterzen_name` at that point, not authored there
  independently.
- `origin` — from Step 2, if given. Where they were born/from; fixed once set.
- `location` — where they currently are, if given (Step 2 or a later Step 2a update). Otherwise left
  blank until a scene (`/enact` Step 1) or another `/character` pass sets it.
- `backstory` — from Step 2, appended/amended per the rule above.
- `knowledge.education` — `{percent, mode, topic, items}` exactly as drawn in Step 3, only if this was
  a fresh draw. Otherwise leave untouched.
- `criterion` — `{standard, wasted_life, anchor, origin, trusts, distrusts, tempered, cost_ledger,
  history}` from Step 4, only if this was a fresh derivation. `origin` is `"derived"` (from a
  collision) or `"uncollided"` (Step 4e). `trusts`/`distrusts` may legitimately be blank even on a
  derived criterion (Step 4d's ambiguous case). Otherwise leave untouched.
- `life` — `{lived, deceased}`. `lived` starts at 0 for a new character, is backfilled from the
  hearsay record for an existing one (Step 5), and is otherwise only ever incremented by `/enact`.
  `deceased` starts `false` and is only ever set by `/enact`. **The span does not go here** — it goes
  in `_lore/characters/lifespans.json` (Step 5).

This skill never touches `_npcs/npcs/registry.json` — `skin`, `taterzen_uuid`, `spawn_position`,
`display_name`, `taterzen_name` are entirely `/embody`'s and `/spawn`'s concern.

Validate the file still parses as JSON before finishing.

## Step 8 — Routines and arc

**Required at creation (2026-08-28) — this is Step 2b's item 4, not a deferred/optional step.** Both
`/enact` and `/simulate` require `routines`+`arc` on **every** NPC participant unconditionally
(`.claude/skills/enact/SKILL.md`'s mechanical block), so authoring them here, in the same pass as
backstory/origin/knowledge, means a character is never left half-finished — there's no longer a
"pure lore-only figure not meant to be enacted" carve-out; every context in `_lore/contexts.json`
exists precisely so a routine is always quick to author. Author `routines` and `arc` together, in the
same pass — see `arc` below for why this is no longer split across two different moments/skills.

**Completing this later, for a character predating this requirement (or one that arrived some other
way — `/enact` directly, or a `generate_offspring.py` newborn, which never assigns an arc):** if
`/character` is invoked again on a character who already has a file but is missing `routines`/`arc`,
Step 2a's field list already covers offering to run this step now, the same as any other still-blank
field — this is the system's flag-and-point solution for an incomplete character, not a separate
mechanism.

- `routines` — a small (2-4), **hand-authored** array of `{location, context, weight,
  routine_actions}` (renamed 2026-08-16 from `archetype`/`specialization` — those names read
  backwards: `context` is the shared place-type the routine happens in, `routine_actions` is what
  *this* character actually does there). `context` must be a key already present in
  `_lore/contexts.json` — read the file fresh each time rather than trusting a remembered list, since
  it grows by hand; as of 2026-08-28 it ships ten starter contexts (market, workshop, archive,
  waystation, port, temple, gardens, municipality, bank, factory, tavern). Add a new one there by hand if none
  fits, rather than stretching an existing context to cover a place-type it doesn't describe. When
  asking the user to pick, list every context by name with a short (2-3 word) gloss of its `texture`
  field, not the field verbatim — e.g. "workshop — hands-on making, craft" — so the question stays
  scannable rather than reciting nine paragraphs. **`routine_actions` is a short progression of actions this specific character
  actually does within that context — not a trait or description, and not a restatement of the
  context's own generic texture** (corrected 2026-08-27 — the field was drifting toward
  identity-labels like "blacksmith, values good craft," which describes a person rather than what
  they do). For a `market` routine: *"opens the stall at dawn, greets regulars, haggles with a
  supplier midday, closes up at dusk."* For a `workshop` routine: *"stokes the forge before first
  light, takes custom orders through the morning, hammers out the day's work through the
  afternoon."* Weights should sum to roughly 100. This is deliberately never auto-generated by
  `/simulate` itself — same discipline as `backstory` and `criterion`: authored here, consumed
  there.
- `arc` — **authored at character creation, same discipline as `routines`, not deferred.** Seeded
  from the routine's context + routine_actions + criterion, not restated from `criterion.anchor`
  alone: `{about, needs, context, premise, resolution: "ongoing", history: []}`. `about` is the
  project's topic tags (at least one `concept: <id>` tag for a genuinely new project — run
  `py scripts/lore/write_arc.py <key> --about ... --needs ... --context ... --premise
  "..."` to write it and register the concept in one call, same tool `/enact` uses). `needs` is
  what it currently requires (checked against other routines' `provides` tags by
  `check_needs_provides.py`, part of `/enact`'s own mechanical block). Scope the ambition against
  `scripts/lore/horizon.py`'s band for this
  character (never the literal span) — a character reading `early` can be given something
  ambitious; one reading `established`/`late` should get something realistically closer to
  finishable, the same logic Step 6 already uses for how ripe a criterion is for change.

  `premise` is the arc's actual content — the one place its concrete project lives in prose. Without
  it, an arc is four bare tags and nothing else: the `concept:` entry `write_arc.py` registers only
  echoes those same tags back, it never restates what the project *is*. Two hard requirements for
  `premise`, both diagnosed from a real failure, not hypothetical (an early draft of Character J's arc
  read as "find a legitimate source for his stones he could stand behind" — abstract, and nothing
  caught it until a human did):
  1. **The resolution-moment test.** `premise` must support one sentence describing the exact moment
     the arc resolves, success or failure. If the honest answer is inherently gradual ("builds a
     better reputation," "finds better sources over time"), it's a theme wearing a project's
     clothes — push toward an actual object/person/place/event with a sharp yes/no outcome. Same
     underlying discipline as Step 4b's "the anchor must be something that could turn out to be
     wrong," applied here to arcs for the first time.
  2. **Ground the target in something already known, when possible.** Prefer seeding the arc's
     central object/goal from something already present in the character's own drawn
     `knowledge.education.items` or the objective record, over inventing a target from nothing — an
     existing corpus item already carries real, checkable specifics (a name, a description, a
     status) for free.
  3. **Texture is free to invent; claim-shaped content is not.** An invented name, mood, or turn of
     phrase is licensed the same way `/enact` Step 2 already licenses it ("personality, mannerisms,
     small human texture — invent freely"), and can be asserted directly. A claim-shaped detail —
     provenance, history, "it's changed hands twice," anything fact-shaped about the world — must be
     phrased as something a character heard/believes/reported ("he's heard, secondhand and
     unconfirmed, that...") rather than stated as settled fact in the premise's own voice. This is
     the same epistemic status hearsay already has everywhere else in this system (a source, a
     confidence status) applied here for the first time — an unattributed claim-shaped assertion in
     `premise` is the one gap in this discipline this system had, and it stays a gap if `premise`
     doesn't follow it too.

  On a `transform` (see `/enact`'s mechanical block), `premise` gets re-composed around whatever
  `about` the transform mechanically injected — same judgment-call moment as re-authoring a failed
  arc, not a separate decision.

  A character reaching `/enact`'s mechanical block with no `arc` on file yet (one that slipped
  through this step, or a newborn from `generate_offspring.py`, which never assigns one) still gets
  one authored the first time they win primacy as `home_frame` — but that path is now the
  **fallback** for a character who reached that mechanism without one, not the normal way arcs
  come to exist.

Both fields are entirely `/enact`'s (and, through it, `/simulate`'s) concern once set — this skill
never rolls dice against them or advances an arc's `history`; it only ever authors the starting
values.

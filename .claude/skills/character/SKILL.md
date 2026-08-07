---
description: Create or update a character's entry in _lore/characters/<key>.json — backstory, location, knowledge, criterion, and lifespan — without running a full /enact conversation. Use when the user wants to flesh out a character's sheet on its own, ahead of (or instead of) enacting a dialog.
disable-model-invocation: true
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
`"Farlis Gorfalis"` alongside an existing `"Farlis"` is fine, since they slugify differently). Skip
this check entirely when the file already exists — that's Step 2a, not a new name.

## Step 2a — Existing entry

If the file exists, show the user its current non-blank fields (`name`, `city`, `backstory`,
`knowledge.education` summary if populated, `knowledge.experience` count, `criterion.standard`,
`life.lived`, and `scripts/lore/horizon.py`'s band) as context, then ask, as plain conversation, what
needs to be updated.
Don't presuppose which fields — the user might want to amend the backstory, add/change the city, draw
or redo their knowledge, or just fix a typo.

- **Backstory** — if the user is adding to an existing non-empty backstory, append/amend rather than
  replace, same as `/enact` Step 6. If they're giving it fresh, just set it.
- **City** — set directly from what the user says.
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

## Step 2b — New entry

If no file exists for this slug, this is a brand-new character — confirm the Step 1 uniqueness check
came back `AVAILABLE` before going any further. Ask, as plain conversation (not multiple-choice):

1. **Backstory** — optional.
2. **Location** — optional, fills `city`.
3. **Knowledge** — how much of the lore they know. Follow the sampling flow in Step 3.

Then run Step 4 (criterion) and Step 5 (lifespan) before writing the entry.

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

Scan `knowledge.education.items` for entries that touch the `backstory` and `city` — same place, same
trade, same family, same route, same wound. Those two fields are the collision surface; an item that
touches neither is just something the character knows, and can't ground a standard for *their* life.

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

Now ask, with exactly three inputs — the anchor, the backstory, the city:

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

The signal is already in the anchor, because every anchor carries its pool category:

| Anchor category | The character built their life on… | Leans toward | Leans against |
|---|---|---|---|
| `hearsay: <entry>#<n>` | what someone said | testimony, especially named and firsthand | the written record, as bloodless or secondhand |
| `era_ensayo`, `era_libro`, `era_esquema`, `year_esquema` | the chronicles | what's written down and checkable | gossip, rumor, "they say" |
| `conflict: CONFLICT-NN` | two records disagreeing | verification; distrusts confident answers of any kind | anyone who sounds certain |
| an `experience` entry | what they saw themselves | firsthand presence | anything nobody present can vouch for |
| `location`, `inhabitant`, `concept`, route/airport categories | ambiguous on its own | — | — |

This table's rows are the four `epistemology_group` values `_lore/encodings.json`'s own `_categories`
block tags each pool category with (`hearsay`, `chronicles`, `conflict`, plus `ambiguous` for the
bottom row — an `experience` entry isn't a pool category at all, it's `knowledge.experience`, but gets
the same firsthand-presence lean regardless). When `/integrate` approves a genuinely new category, it
either joins one of these groups or proposes a new row here — never invent one without that proposal
being confirmed first, same as every other judgment call in this pack.

For the ambiguous bottom row, don't force it — read the lean off the **backstory** instead (a
seafarer who reads history trusts differently from a bard who collects what people say), or leave
both fields blank. A character with no particular epistemology is perfectly normal.

**Do not derive this from which category the character holds most of.** That was tried and it fails:
one dialog yields many `hearsay` claims while an era yields one item, so the pool is hearsay-heavy
for everybody, and raw counts made five of the first seven characters "testimony-trusters" —
including Iläria, who *wrote one of the chronicles* and holds 15 of the corpus's conflicts. Raw
distribution measures how the sample was drawn (your own `--mode skewed` topics, e.g. a "15%
hearsay-only" slice), not who the character is.

What *is* usable, and only as a tiebreaker when the anchor lands in the ambiguous row:
**over-representation against the other characters' baseline.** Döran holding 12% chronicle items
where everyone else holds 2–7%, or Iläria holding 15 conflicts where others hold 0–6, is a real
signal. "Has more hearsay than anything else" is not — everyone does. Run
`py scripts/lore/baseline_stats.py <npc_key>` to compute this instead of eyeballing item lists across
every character file — it reports each category's count/percentage for this character against the
corpus-wide average and range, flagged where this character sits well above the average (Iläria's
`conflict` category is the worked example the flag actually catches). The script only computes the
signal; whether it's a strong enough tiebreaker for *this* character, and how `trusts`/`distrusts`
end up phrased, stays entirely a judgement call.

Write `trusts` and `distrusts` as one line each, in the character's own terms, the same way
`standard`/`wasted_life` are written. Good: `trusts: "a name attached to a story - someone who was
there and can be asked"` / `distrusts: "chronicles, which he'll say were written by people who
weren't"`.

Three hard limits:

- **Facts are exempt.** A character cannot distrust a fact (`_lore/facts/`). That is what makes facts
  the floor rather than part of the argument, and this mechanic must never erode it.
- **This never changes what a character knows.** It changes what a claim *weighs* when it collides
  with something else. Their `education` sample is untouched.
- **It's a lean, not a rule**, and it should mostly be invisible until two sources actually conflict.
  A character who announces their theory of knowledge is as badly played as one who recites their
  criterion.

### 4e — When nothing collides

If no item in the sample touches the backstory or city, **do not invent a criterion and do not fall
back to a city-level or trade-level default** — inherited criteria are a real part of the model but
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
of entries listing them in `participants`. (Match on the display name including diacritics — `Döran`
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
- `city` — from Step 2, if given.
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

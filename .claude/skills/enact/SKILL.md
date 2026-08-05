---
description: Play a lore-only enacted character scene for Luminacion — against the player or against another enacted character — sampling each character's lore knowledge from _lore/encodings.json, then recording what the scene did to that lore (hearsay, criterion, life). Purely lore-side: touches nothing under data/luminacion/ or _npcs/npcs/registry.json. Use when the user wants to enact/roleplay a character at the lore level. To also put the scene in the game (Blabber dialog, NPC registration, gestures), follow with /embody, or use /enact-embody to run both in one pass.
disable-model-invocation: true
---

Runs the lore half of the enactment procedure documented in `README.md` §8, plus the setup questions
and record-keeping steps below. Read §8 first if it hasn't been read yet this session — this skill
assumes its rules (never invent as fact anything outside a character's sample; personality and small
texture are free to invent; keep every line short, dialog-box length).

**Write dialogue only, no action cues.** A character's line is only what they say — no
asterisk-delimited stage directions (`*looks up from coiling a rope*`, `*grins*`, `*taps his temple*`)
anywhere in it. Personality comes through word choice and rhythm, not narrated gesture. This matters
here too, not just for the eventual Blabber file: `/embody`'s conversion step strips any stage
direction that slips in, so writing clean from the start avoids losing anything worth keeping.

Two things stay true throughout: a character never knows what another enacted character knows, even
when both are being played in the same scene — each is bounded strictly by their own sample. And
nothing here is decided silently; every genuine open question this skill can actually raise (education
sample topic, criterion collision, how the scene resolves) gets asked, never guessed. Minecraft-side
open questions — skin, UUID, movement mode, how a two-NPC dialog gets registered — are `/embody`'s
concern, not this skill's; it doesn't ask about them because it never touches that layer.

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
  `python scripts/check_character_name.py "<name>"` **and confirm `AVAILABLE`** before treating it as
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
python scripts/sample_lore_knowledge.py --percent <N> --mode random
# or
python scripts/sample_lore_knowledge.py --percent <N> --mode skewed --topic "<keyword>" --topic "<keyword2>"
```

Keep the printed list (or the reused list, for a returning character) — it's this character's
entire knowledge of the world for the rest of this run, and it goes into their character file in
Step 6 (or stays untouched there, if reused). Do not reveal the full list to the user unprompted (same
reasoning as §8: better discovered through play than read off a list), but you may describe its
general shape.

Some drawn items will be `category: "hearsay"` (a claim from an earlier dialog's hearsay entry, not
the objective record — see README §8 Step 1). Play those as things the character heard, not settled
fact. The moment one of these actually gets voiced in the scene (Step 3), roll
`scripts/lineage_coin.py` right then — the result decides how the line is phrased: a `traceable`
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
- **Horizon.** Run `python scripts/horizon.py <npc_key>` for each character before the scene starts
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

Applies to both 3a and 3b, on top of README §8 Step 2's existing rules (never invent as fact outside
the sample; personality and texture are free; write short).

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
  knowable until after it's played (see `scripts/horizon.py`'s docstring and Step 5b point 6) — so it
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

## Step 5 — Update the hearsay record

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

Add an entry to `_lore/characters/hearsay.md` and to `encodings.json`'s `hearsay.entries` array for
this dialog, in the same shape as the existing entries: participants, location, summary, and a
`claims` list phrased as reported assertions (not restated as fact), each with an `about` reference
into the objective arrays where it topically overlaps (a bare era name from `time_systems` is a valid
`about` target too, e.g. `"Era del Daax"`). Check each claim against the record and set
`inconsistent_with_record` (an array of `{about, source_kind, note}` — `source_kind` is
`material`/`tale`, naming which kind of objective source the contradicted entry rests on)
only if it genuinely contradicts something, and `inconsistent_with_facts` (a short string explaining
the contradiction) only if it contradicts one of the two entries in `_lore/facts/facts.json`. Leave
both unset in the ordinary case — that's most claims, and recording "no contradiction found" on every
one of them would just be noise; absence already means that. If a claim raises a genuine question the
objective record has never addressed at all (a gap, not a contradiction) and it resonates with the
existing corpus, log it in `_lore/unknown.md`, cross-referencing the claim's id, matching the file's
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

## Step 5b — Resolve shocks, drift, and the scene count

Runs after Step 5 because Step 5's `claims` list is the input. For every character enacted this run:

**1. Reference gate.** For each claim just recorded (and for what the character actually lived
through in the scene), check whether it **references that character's `criterion.anchor`** — same
case, same person, same event, using the claim's `about` refs. This is a pointer comparison, not a
judgment about how upsetting something was. **Never score intensity; there is no magnitude scale
here on purpose.** A claim that doesn't reference the anchor is news, however dramatic, and stops
here.

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

Append an entry to `criterion.history` for anything other than "no change":
`{ "dialog": "<dialog file or scene id>", "was": "<previous standard, if it changed>", "move":
"rejected|reinterpreted|broke", "cause": "<claim id that referenced the anchor>" }`.

**4. Drift bookkeeping.** If honoring the criterion cost the character something in this scene — time,
a relationship, a chance they passed up, a thing they couldn't say — append one short line to
`criterion.cost_ledger`. This never changes the criterion by itself; it raises susceptibility for
later shocks. Skip it when nothing was actually paid.

**5. Increment `life.lived` by 1** for every character who was in the scene.

**6. Now, and only now, run `python scripts/horizon.py <npc_key>` again and check `ending`.** Before
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
to the world at large. Do all of the following:

- **Set `life.deceased: true`** on their character file. This is a plain, non-secret fact — unlike
  `life.span`, nothing about death itself is hidden — and it's what stops a future `/enact` run from
  accidentally reusing them (see the Step 1 guard below).
- **Record it as an objective fact of the world**, in the same shape `/tell` produces (see
  `.claude/skills/tell/SKILL.md`) but written directly rather than asked for interactively, since every
  fact needed is already known at this point: a new `_lore/tale/<slug>.md` file (title, `**Told by:**
  no one; simply now known` in the ordinary case — a named cause only if the scene actually
  established one — the fact of the death itself as the tale's content), a matching `tales.entries`
  manifest row in `encodings.json`, a `_lore/tale/_authors.md` row, and a `characters` entry update if
  one exists for them. This is what makes death re-enter the ordinary sampling pool for characters
  created later, at ordinary odds — the *only* channel anyone outside the circle below has.
- **Run `python scripts/notify_death.py <npc_key>`.** It computes the character's *circle* — everyone
  they've shared a recorded scene with, plus everyone named in their own backstory — and mechanically
  samples 30% of it (minimum 1 if the circle isn't empty) as who learns immediately. It also flags
  which of those notified have a `criterion.anchor` that references the deceased directly (same
  scene, same hearsay entry) — a pointer check, not a judgement call.
- **For every notified character, append one line to `knowledge.experience`** recording that they
  learned of the death — plain reported fact, no attribution needed (it wasn't told to them by
  anyone in particular; word simply reached them). This is written immediately regardless of whether
  that character is ever enacted again soon; it's part of their standing knowledge from now on.
- **For every notified character flagged as a shock candidate, resolve it now, per `/character`
  Step 6** — the same reject / accept-and-reinterpret / accept-and-break judgement as point 3 above,
  using the news itself as the shock ("lived falsification... the character's own experience
  referencing their own anchor" already covers this). Update `tempered`/`cost_ledger`/`history`/
  `trusts`/`distrusts` exactly as point 3 does. This is real judgement, not mechanical — the script
  only tells you *who* qualifies, never how they take it.
- **Everyone the script did not notify simply doesn't know yet.** Don't write anything for them. They
  find out later only the ordinary way: sampled into a new character's education, or told by someone
  from the circle in a future scene (subject to the usual `lineage_coin.py` traceable/untraceable
  rule on that retelling, same as any other claim).

## Step 6 — Update the character record

For every character enacted this run, add/update their file at `_lore/characters/<key>.json`
(key = lowercased, slugified name):

- `name` — set once, for a first-time character. Never rewritten on a returning character.
- `city` — the location from Step 1/2, or `""` if none was given.
- `backstory` — the backstory from Step 1/2, or `""` if none was given. Experience-knowledge,
  conceptually (see the intro), but its own top-level field. For a returning character, only append
  or amend this if the user gives *new* backstory in this run (as with Döran's added hologram/pedestal
  detail) — don't touch it otherwise.
- `knowledge.education` — `{percent, mode, topic, items}` exactly as drawn by the script in Step 1/2,
  for a first-time character. For a returning character reusing an existing sample (per the guard in
  Step 1), **leave this field untouched** — never redraw or overwrite it on a later run.
- `knowledge.experience` — anything that came up in the scene beyond the original sample: invented
  personal texture that's now established for this character (Sonoros's "out of Görff way," his
  crossing-walker job), or — for the *other* character in a two-NPC scene — anything they said that
  this character would now plausibly have picked up just from being present. Cross-check against the
  hearsay entry's `claims` from Step 5. For a returning character, **append** new entries to the
  existing list rather than replacing it.
- `criterion` — for a first-time character, the whole object as derived in Step 1. For a returning
  character, write only what Step 5b actually changed (`standard`/`wasted_life` on a break,
  `tempered` on a reinterpretation, `trusts`/`distrusts` if the outcome moved them, plus the
  `history` and `cost_ledger` appends). **Never re-derive a criterion from the sample on a later
  run** — it changes only through a shock that referenced its anchor.
- `life` — `{lived, deceased}`. `lived` incremented per Step 5b; `deceased` set per Step 5b point 6.
  If this run rolled a first lifespan (Step 1), the span went into
  `_lore/characters/lifespans.json`, never here.

This is the last step `/enact` performs — nothing here touches `_npcs/npcs/registry.json`,
`_npcs/dialogs/registry.json`, or any file under `data/luminacion/`. To convert this scene into a
registered Blabber dialog, register the NPC(s) in the Minecraft layer, and bake gestures, run
`/embody` now (it picks up the scene from this same conversation), or use `/enact-embody` next time
to run both skills back to back in one pass.

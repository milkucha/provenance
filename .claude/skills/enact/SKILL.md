---
description: Set up and run an enacted character conversation for Luminacion — against the player or against another enacted character — sampling each character's lore knowledge from _lore/analysis/encodings.json, then convert the result into a registered Blabber dialog. Use when the user wants to enact/roleplay an NPC and turn it into pack content.
disable-model-invocation: true
---

Runs the enactment-to-dialog procedure documented in `README.md` §8, plus the setup questions and
registration steps below. Read §8 first if it hasn't been read yet this session — this skill assumes
its rules (never invent as fact anything outside a character's sample; personality and small texture
are free to invent; keep every line short, dialog-box length), plus three hard formatting rules that
apply to every dialog this skill produces:

- **Dialog only, no action cues.** A character's line is only what they say — no asterisk-delimited
  stage directions (`*looks up from coiling a rope*`, `*grins*`, `*taps his temple*`) anywhere in it,
  in-scene or in the converted `text`/`choices[].text` fields. Personality comes through word choice
  and rhythm, not narrated gesture. If the enactment transcript slips into third-person action text,
  strip it when converting — don't carry it into the Blabber dialog.
- **300-character hard cap per line.** No single `text` value or `choices[].text` value in the
  converted dialog may exceed 300 characters. See Step 4 for how to split a line that runs long.
- **RPG layout, always.** Every converted dialog file gets a top-level `"layout": { "type":
  "blabber:rpg" }` right after `"$schema"` — never leave it unset (Blabber falls back to its classic
  box style without it). All four templates already carry this field; when starting a new dialog from
  scratch instead of a template, add it by hand.

Two things stay true throughout: a character never knows what another enacted character knows, even
when both are being played in the same scene — each is bounded strictly by their own sample. And
nothing here is decided silently; every genuine open question (skin, UUID, movement mode, how a
two-NPC dialog gets registered) gets asked or logged in `TODO.md`, never guessed.

A character's knowledge splits into two kinds, mirrored in `_maps/npcs/registry.json`'s
`knowledge` object:

- **`education`** — the sample drawn once at creation (Step 1/2). Fixed for life: never redrawn,
  never hand-edited, on this run or any later one.
- **`experience`** — everything picked up by living through scenes: the `backstory` field (also
  experience-knowledge, conceptually, even though it stays its own top-level field since it predates
  this split) plus `knowledge.experience`, which keeps growing across every `/enact` run this
  character is ever part of again.

## Step 1 — First interlocutor

Ask, as plain conversation (not multiple-choice):

1. **Name.**
2. **Backstory** — optional. A user-given personal fact (like "family comes from somewhere else"),
   not a lore fact. Hold it as true for this character regardless of what their sample contains.
3. **Location** — optional. Where this character is based/found — fills the `city` field in the
   registry later. Not necessarily their backstory's place of origin (Sonoros's backstory has him
   "out of Görff way," but his registered `city` is Balehm, where the scene actually put him).
4. **Knowledge corpus** — how much of the lore they know, and how it's chosen. **First, check
   `_maps/npcs/registry.json` for an existing entry under this character's key.** If one exists with
   a `knowledge.education` already populated (`percent` not `null`), reuse it as-is — skip the
   percentage/mode/topic questions and the sampling script below entirely, and do not redraw.
   `education` is fixed at creation and never changes after; only `knowledge.experience` and the
   hearsay record (Step 5) are allowed to keep growing across later runs. If no entry exists yet, or
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
entire knowledge of the world for the rest of this run, and it goes into the registry in Step 6 (or
stays untouched there, if reused). Do not reveal the full list to the user unprompted (same
reasoning as §8: better discovered through play than read off a list), but you may describe its
general shape.

Some drawn items will be `category: "hearsay"` (a claim from an earlier dialog's hearsay entry, not
the objective record — see README §8 Step 1). Play those as things the character heard, not settled
fact. The moment one of these actually gets voiced in the scene (Step 3), roll
`scripts/lineage_coin.py` right then — the result decides how the line is phrased: a `traceable`
roll lets the character cite the source by name ("I heard Morkulo say..."); an `untraceable` roll
means vague framing only ("they say...," "it's told that...") — no named source, on purpose. Keep
the roll result; it determines `derived_from`/`oral_lore` in Step 5.

## Step 2 — Second interlocutor

Ask (AskUserQuestion): is the second interlocutor **the player**, or **another character**?

- **The player:** ask (AskUserQuestion) whether to start the scene now. If yes, go to Step 3a.
- **Another character:** repeat every question in Step 1 for them — name, backstory, location,
  knowledge corpus, sample drawn the same way. Then ask (AskUserQuestion) whether to initiate the
  interaction now. If yes, go to Step 3b.

## Step 3a — Enact against the player

Play interlocutor 1 in character, turn by turn, waiting for the player's actual input each time —
same shape as the Sonoros conversation. Keep responses to 2–3 sentences. Continue until the user
signals the scene is over.

## Step 3b — Enact both characters

Write the full scene as one message, alternating clearly labeled turns, same shape as the
Nawom/Morkulo conversation — you write one side, then respond to yourself as the other, honoring
each character's own sample independently. Bring it to a natural stopping point rather than
running indefinitely, then check with the user before moving on: satisfied, or continue/adjust?

## Step 4 — Convert to a Blabber dialog

Per README §8 Step 3: compress the transcript, don't add to it; rename states to short meaningful
ids; wire the final `end_dialogue` state per the existing templates.

- **Strip action cues.** Drop any `*...*` stage direction that made it into the transcript during
  Step 3 — only the spoken words become the state's `text` (or, for two-NPC dialogs, the `"Name: "`
  prefix plus the spoken words).
- **Enforce the 300-character cap.** If a line's `text` (after stripping cues) is over 300 characters,
  split it at a natural sentence or clause boundary into two or more states, chained together with a
  single `"..."` choice that just advances to the next part — the same connector pattern already used
  between full turns (see `nawom_morkulo_first_meeting.json`). The reader/player never sees a visible
  choice for these — it's a pure continuation, not a fork. Keep splitting until every piece is under
  the cap; don't try to cram a long line under the limit by trimming content, since Step 3 already
  says not to add to (or subtract from) what was actually said.

- **If Step 3a (vs. player):** each state's `text` is the NPC's line; each `choices[].text` is the
  player's actual line. (`sonoros_lost_traveler.json` is the reference shape.)
- **If Step 3b (vs. another character):** Blabber has **no per-state speaker field** — confirmed
  from the mod's own source (`DialogueState.java`: fields are `text`, `illustrations`, `choices`,
  `action`, `type`; the display name is fixed once for the whole file via `DialogueTemplate.name`).
  So: prefix each state's `text` with `"Name: "`, and give every state a single `"..."` choice that
  just advances to the next state — no real options. Set the file's top-level `"name"` to something
  like `"<Char1> & <Char2>"` rather than let it default to `"Dialogue with <interlocutor>"`, which
  would be misleading with two speakers. (`nawom_morkulo_first_meeting.json` is the reference shape.)

Validate before moving on — every `choices[].next` must resolve to a real state, `start_at` must be
valid, and the top-level `"layout": { "type": "blabber:rpg" }` is present. Save to
`data/luminacion/blabber/dialogues/<descriptive_name>.json`.

## Step 5 — Update the hearsay record

This step is unconditional — it runs for every dialog produced this run, not only ones where a
character explicitly retold something sourced from a sampled hearsay item. A character's own fresh
invention (a venue description the user handed you, a personal theory, an on-the-spot guess) belongs
in the record exactly as much as an attributed retelling does — oral tradition is grounded in truth
as often as embellishment, and an unverified claim is not the same as a false one. Don't gate this
step on "did anyone say 'I heard X say...'" — that test only decides the two optional fields below,
not whether the step happens at all.

Add an entry to `_lore/analysis/hearsay.md` and to `encodings.json`'s `hearsay.entries` array for
this dialog, in the same shape as the existing entries: participants, location, summary, and a
`claims` list phrased as reported assertions (not restated as fact), each with an `about` reference
into the objective arrays where it topically overlaps (a bare era name from `time_systems` is a valid
`about` target too, e.g. `"Era del Daax"`), and a `consistent_with_context` flag (`true`/`false`/
`null` — `null` when there's nothing to check the claim against either way, which is not the same as
confirming it). Claims don't need to cover every sentence spoken — capture the kernels: the ideas
someone could plausibly repeat later, not the connective tissue. A kernel that resurfaces across
several entries (restated, elaborated, half-remembered) naturally ends up with more copies in the
sampling pool in `sample_lore_knowledge.py` — that's the actual mechanism by which an idea becomes
folklore and keeps mutating, not a special flag to set.

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

## Step 6 — Register the NPC(s)

For every character enacted this run, add/update their entry in `_maps/npcs/registry.json`
(key = lowercased name):

- `display_name`, `taterzen_name` — the name.
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
- `skin`, `taterzen_uuid`, `spawn_position` — leave blank/null. Not this skill's job.

Then, for the dialog itself:

- **If Step 3a (vs. player):** register it normally in `_maps/dialogs/registry.json` under that
  NPC's key, per README §3 Step 3.
- **If Step 3b (vs. another character):** do **not** guess how to register a dialog that belongs to
  two NPCs — the registry format assumes one dialog per NPC key. Ask the user how they want it
  handled, or leave it open in TODO.md (see Step 7) exactly like the Nawom & Morkulo precedent.

## Step 7 — Log what's still open

Add or update a section in `TODO.md` for each newly-enacted character (and the dialog, if its
registration was left unresolved in Step 6): skin, movement mode, `spawn_position`,
`spawn.mcfunction`, UUID capture — the same shape as the existing Sonoros and Nawom & Morkulo
sections. Don't silently resolve anything there either.

## Step 8 — Bake gestures

Every dialog this skill produces starts uniform — `nod_up_down` on every non-`end` state, straight
from the templates. Invoke the `bake_dialog` skill (Skill tool, `skill: "bake_dialog"`, `args:` the
dialog file's path from Step 4) to replace a minority of those with an emotionally-matched gesture
where the line's own text supports it — the same manual pass Döran's dialogues and
`nuvilo_nerkeli_feria_del_milenio.json` got, now packaged so it doesn't depend on being asked for by
name each time. `bake_dialog` handles its own confirmation with the user before writing anything;
nothing further needed here once it returns.

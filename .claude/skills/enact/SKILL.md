---
description: Set up and run an enacted character conversation for Luminacion — against the player or against another enacted character — sampling each character's lore knowledge from _lore/analysis/encodings.json, then convert the result into a registered Blabber dialog. Use when the user wants to enact/roleplay an NPC and turn it into pack content.
disable-model-invocation: true
---

Runs the enactment-to-dialog procedure documented in `README.md` §8, plus the setup questions and
registration steps below. Read §8 first if it hasn't been read yet this session — this skill assumes
its rules (never invent as fact anything outside a character's sample; personality and small texture
are free to invent; keep every line short, dialog-box length).

Two things stay true throughout: a character never knows what another enacted character knows, even
when both are being played in the same scene — each is bounded strictly by their own sample. And
nothing here is decided silently; every genuine open question (skin, UUID, movement mode, how a
two-NPC dialog gets registered) gets asked or logged in `TODO.md`, never guessed.

## Step 1 — First interlocutor

Ask, as plain conversation (not multiple-choice):

1. **Name.**
2. **Backstory** — optional. A user-given personal fact (like "family comes from somewhere else"),
   not a lore fact. Hold it as true for this character regardless of what their sample contains.
3. **Location** — optional. Where this character is based/found — fills the `city` field in the
   registry later. Not necessarily their backstory's place of origin (Sonoros's backstory has him
   "out of Görff way," but his registered `city` is Balehm, where the scene actually put him).
4. **Knowledge corpus** — how much of the lore they know, and how it's chosen:
   - Ask for a **percentage** (open number, e.g. "5", "11", "21").
   - Ask (AskUserQuestion, two options) whether the draw is **random** or **skewed toward a topic**.
   - If skewed, ask for the topic/keyword(s) (e.g. "geography and geology").

Then run the sample:

```bash
python scripts/sample_lore_knowledge.py --percent <N> --mode random
# or
python scripts/sample_lore_knowledge.py --percent <N> --mode skewed --topic "<keyword>" --topic "<keyword2>"
```

Keep the printed list — it's this character's entire knowledge of the world for the rest of this
run, and it goes into the registry in Step 6. Do not reveal the full list to the user unprompted
(same reasoning as §8: better discovered through play than read off a list), but you may describe
its general shape.

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
valid. Save to `data/luminacion/blabber/dialogues/<descriptive_name>.json`.

## Step 5 — Update the hearsay record

Add an entry to `_lore/analysis/hearsay.md` and to `encodings.json`'s `hearsay.entries` array for
this dialog, in the same shape as the existing two entries: participants, location, summary, and a
`claims` list phrased as reported assertions (not restated as fact), each with an `about` reference
into the objective arrays where it topically overlaps, and a `consistent_with_context` flag
(`true`/`false`/`null` — `null` when there's nothing to check the claim against either way, which is
not the same as confirming it).

## Step 6 — Register the NPC(s)

For every character enacted this run, add/update their entry in `_maps/npcs/registry.json`
(key = lowercased name):

- `display_name`, `taterzen_name` — the name.
- `city` — the location from Step 1/2, or `""` if none was given.
- `backstory` — the backstory from Step 1/2, or `""` if none was given.
- `knowledge.sample` — `{percent, mode, topic, items}` exactly as drawn by the script in Step 1/2.
- `knowledge.surfaced_in_dialog` — anything that came up in the scene beyond the original sample:
  invented personal texture that's now established for this character (Sonoros's "out of Görff
  way," his crossing-walker job), or — for the *other* character in a two-NPC scene — anything they
  said that this character would now plausibly have picked up just from being present. Cross-check
  against the hearsay entry's `claims` from Step 5.
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

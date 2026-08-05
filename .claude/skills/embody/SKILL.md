---
description: Convert an already-enacted scene (from /enact, run earlier in this same conversation) into pack content — a registered Blabber dialog, an NPC registration in _npcs/npcs/registry.json, and a gesture-baking handoff. Purely Minecraft/NPC-facing: never touches _lore/characters/. Use right after /enact when the user wants the scene actually put in the game, for a conversation that only ran bare /enact so far. Use /enact-embody instead to run both skills back to back in one pass.
disable-model-invocation: true
---

Runs the Minecraft-facing half of the enactment-to-dialog procedure documented in `README.md` §8,
completing a scene that `/enact` already played and recorded in this same conversation — this skill
reads the transcript still sitting in context, not a file, so it only makes sense run as the next step
after `/enact`, not cold in an unrelated session.

Three hard formatting rules apply to every dialog this skill produces:

- **Dialog only, no action cues.** A character's line is only what they say — no asterisk-delimited
  stage directions (`*looks up from coiling a rope*`, `*grins*`, `*taps his temple*`) anywhere in the
  converted `text`/`choices[].text` fields. If the enactment transcript slipped into third-person
  action text despite `/enact`'s own instruction to avoid it, strip it here — don't carry it into the
  Blabber dialog.
- **300-character hard cap per line.** No single `text` value or `choices[].text` value in the
  converted dialog may exceed 300 characters. See Step 1 for how to split a line that runs long.
- **RPG layout, always.** Every converted dialog file gets a top-level `"layout": { "type":
  "blabber:rpg" }` right after `"$schema"` — never leave it unset (Blabber falls back to its classic
  box style without it). All four templates already carry this field; when starting a new dialog from
  scratch instead of a template, add it by hand.

Nothing here is decided silently; every genuine open question (skin, UUID, movement mode, how a
two-NPC dialog gets registered) gets asked or logged in `TODO.md`, never guessed.

## Step 1 — Convert to a Blabber dialog

Per README §8 Step 3: compress the transcript, don't add to it; rename states to short meaningful
ids; wire the final `end_dialogue` state per the existing templates.

- **Strip action cues.** Drop any `*...*` stage direction that made it into the transcript — only the
  spoken words become the state's `text` (or, for two-NPC dialogs, the `"Name: "` prefix plus the
  spoken words).
- **Enforce the 300-character cap.** If a line's `text` (after stripping cues) is over 300 characters,
  split it at a natural sentence or clause boundary into two or more states, chained together with a
  single `"..."` choice that just advances to the next part — the same connector pattern already used
  between full turns (see `nawom_morkulo_first_meeting.json`). The reader/player never sees a visible
  choice for these — it's a pure continuation, not a fork. Keep splitting until every piece is under
  the cap; don't try to cram a long line under the limit by trimming content, since the scene was
  already finalized by `/enact` and shouldn't be added to or subtracted from now.

- **If the scene was against the player:** each state's `text` is the NPC's line; each
  `choices[].text` is the player's actual line. (`sonoros_lost_traveler.json` is the reference shape.)
- **If the scene was between two enacted characters:** Blabber has **no per-state speaker field** —
  confirmed from the mod's own source (`DialogueState.java`: fields are `text`, `illustrations`,
  `choices`, `action`, `type`; the display name is fixed once for the whole file via
  `DialogueTemplate.name`). So: prefix each state's `text` with `"Name: "`, and give every state a
  single `"..."` choice that just advances to the next state — no real options. Set the file's
  top-level `"name"` to something like `"<Char1> & <Char2>"` rather than let it default to
  `"Dialogue with <interlocutor>"`, which would be misleading with two speakers.
  (`nawom_morkulo_first_meeting.json` is the reference shape.)

Validate before moving on — every `choices[].next` must resolve to a real state, `start_at` must be
valid, and the top-level `"layout": { "type": "blabber:rpg" }` is present. Save to
`data/luminacion/blabber/dialogues/<descriptive_name>.json`.

## Step 2 — Register the NPC(s) and the dialog

For every character in the scene, add/update their entry in `_npcs/npcs/registry.json`
(key = same slug as their `_lore/characters/<key>.json` file):

- **If no entry exists yet for this key** (the character has never been embodied before): create one,
  copying `name` from `_lore/characters/<key>.json` into both `display_name` and `taterzen_name`.
  Leave `skin`, `taterzen_uuid`, `spawn_position` blank/null — not this skill's job either; that's
  `/spawn`'s.
- **If an entry already exists:** leave `display_name`/`taterzen_name`/`skin`/`taterzen_uuid`/
  `spawn_position` untouched. This skill never rewrites them — a character's Minecraft-side name is
  set once, the first time they're embodied, from the lore file's canonical `name`.

Then, for the dialog itself:

- **If the scene was against the player:** register it normally in `_npcs/dialogs/registry.json`
  under that NPC's key, per README §3 Step 3.
- **If the scene was between two enacted characters:** do **not** guess how to register a dialog that
  belongs to two NPCs — the registry format assumes one dialog per NPC key. Ask the user how they want
  it handled, or leave it open in TODO.md (see Step 3) exactly like the Nawom & Morkulo precedent.

## Step 3 — Log what's still open

Add or update a section in `TODO.md` for each newly-embodied character (and the dialog, if its
registration was left unresolved in Step 2): skin, movement mode, `spawn_position`,
`spawn.mcfunction`, UUID capture — the same shape as the existing Sonoros and Nawom & Morkulo
sections. Don't silently resolve anything there either.

## Step 4 — Bake gestures

Every dialog this skill produces starts uniform — `nod_up_down` on every non-`end` state, straight
from the templates. The `bake_dialog` skill (`.claude/skills/bake_dialog/SKILL.md`) replaces a
minority of those with an emotionally-matched gesture where the line's own text supports it — the
same manual pass Döran's dialogues and `nuvilo_nerkeli_feria_del_milenio.json` got.

**Known blocker, confirmed 2026-07-31:** this step cannot currently be run from inside `/embody`.
`bake_dialog/SKILL.md` sets `disable-model-invocation: true`, so calling it with the Skill tool is
refused outright. Until that flag is dropped or this step is rewritten (see `TODO.md`), the only way
to bake is for the user to run `/bake_dialog <path>` themselves. So: tell them the file is ready for
it, log it in `TODO.md`, and don't attempt the invocation. This isn't conditional on a flag — it
always ends this way, since the blocker applies regardless of intent.

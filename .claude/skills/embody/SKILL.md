---
description: Convert an already-enacted scene (from /enact, run earlier in this same conversation) into pack content — a registered Blabber dialog with its gestures already baked, and an NPC registration in _npcs/npcs/registry.json. Purely Minecraft/NPC-facing: never touches _lore/characters/. Use right after /enact when the user wants the scene actually put in the game, for a conversation that only ran bare /enact so far. Use /enact-embody instead to run both skills back to back in one pass.
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

Save to `data/luminacion/blabber/dialogues/<descriptive_name>.json`, then validate it:

```bash
py scripts/minecraft/validate_dialog.py data/luminacion/blabber/dialogues/<descriptive_name>.json
```

It checks exactly the structural rules above by construction rather than by eye — every
`choices[].next` resolves to a real state, `start_at` is valid, the top-level
`"layout": { "type": "blabber:rpg" }` is present, no line exceeds the 300-character cap, no stage
cue leaked through, and flags any state nothing ever links to. A clean pass means the file won't break
when Blabber loads it — it has no opinion on writing quality or gesture choice, both still Step 3's
job.

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
  it handled, or leave it open in TODO.md (see Step 4) exactly like the Nawom & Morkulo precedent.

## Step 3 — Bake gestures

Every dialog Step 1 just wrote starts uniform — `nod_up_down` on every non-`end` state, straight from
the templates. This step replaces a minority of those with an emotionally-matched gesture wherever a
line's own text supports it, so the conversation reads as staged rather than uniformly nodding through
every line — the same judgment call Döran's dialogues and `nuvilo_nerkeli_feria_del_milenio.json` got
by hand. It runs on **every** dialog this skill produces — there is no path through `/embody` (or,
transitively, `/enact-embody`) that leaves a fresh dialog on the uniform default.

(This step used to just hand off to a standalone `bake_dialog` skill and stop there, blocked on that
skill's `disable-model-invocation: true` flag refusing an internal Skill-tool call — see `TODO.md` for
the history. That blocker is now moot: the procedure is inlined below instead of invoked. `bake_dialog`
itself has since been deleted — every dialog in this pack is produced by `/enact`/`/embody` (or their
pre-split ancestor), none hand-written, so there was no remaining case for a standalone baking skill to
serve once this step started running automatically. A handful of pre-existing dialogs that predated
this change and were still uniform got a one-time manual baking pass instead (2026-08-05, see
`TODO.md`) rather than being left stranded.)

Since the dialog just came out of Step 1, it's always freshly uniform — skip straight to selection
below, no need to check for pre-existing gestures the way a from-scratch bake pass would.

**`look_up`/`look_down` are a separate, deliberate mechanism — never touch them.** No template Step 1
converts from ever emits one of these (they're a hand-authored choice made later, on a state where an
NPC is looking at something large right in front of them — confirmed by reading the mechanism itself:
`look_up`/`look_down` is a single one-shot `tp` that sets an absolute head pitch and holds it
indefinitely, while a `gesture_*` auto-clears after 2.5s and can't be paired with a nod on the same
state, so converting one to the other would cut short a pose meant to hold and block the nod from
playing during it — a regression, not a consistency win, tried and reverted 2026-07-25), so this should
never come up on a freshly-converted dialog. Noted here only so a future edit to Step 1's templates
doesn't accidentally make this step overwrite one.

Read every non-`end`/`end_dialogue` state's `text` (strip a two-NPC dialog's `"Name: "` prefix only
for reading — never edit it). For each, judge whether the line's content reads as something more
specific than a neutral "I am currently talking" nod:

| Reads as... | Keywords | Gesture |
|---|---|---|
| Greeting, farewell, beckoning someone in | greeting, farewell, hello, beckoning, goodbye | `gesture_wave` (`gesture_wave_left` for variety when a scene already used the right-handed wave) |
| Making a point, an enthusiastic reveal, "here's the thing" | emphasis, insistence, revelation, "here's the thing", calling-out | `gesture_point` (`gesture_point_left` for variety when a scene already used the right-handed point) |
| Formal, solemn, showing respect | respect, formality, solemnity, deference, ceremony | `gesture_bow` |
| Not sure / doesn't know / indifferent / conceding a point | uncertainty, indifference, "who knows", concession, nonchalance | `gesture_shrug` |
| Open explanation, presenting or inviting, "who's to say" | openness, explanation, invitation, reassurance, "who's to say" | `gesture_palms_up` |
| Musing, admitting a gap, a surprised realization | musing, puzzlement, realization, forgetfulness, "huh" | `gesture_scratch_head` (`gesture_scratch_head_left` for variety when a scene already used the right-handed scratch-head) |
| Humor, teasing, a self-deprecating aside, "Ha" | humor, teasing, amusement, self-deprecation, mirth | `gesture_laugh` |
| Mild disagreement or correction | mild-disagreement, correction, "not quite", second-guessing, gentle-pushback | `nod_left_right` |
| Firm refusal or rejection | refusal, rejection, denial, disapproval, "absolutely not" | `gesture_no` |
| Deadpan disbelief, exasperation, secondhand embarrassment | disbelief, exasperation, embarrassment, frustration, "unbelievable" | `gesture_face_palm` |
| Skeptical, defensive, or prideful stance | skepticism, defensiveness, pride, stubbornness, wariness | `gesture_cross_arms` |
| Triumph, excitement | triumph, excitement, celebration, victory, elation | `gesture_jump` |
| Playful bragging, showing off, a boastful tease | bragging, showing-off, playful-pride, confidence, teasing-boast | `gesture_flex_arm` |

Everything else stays the default `nod_up_down` — most lines are informational connective tissue and
should. Calibrate against dialogs that already have this treatment (`doran_four_castles.json`: 3 of
7 states; `doran_eras_of_culture.json`: 2 of 8; `nuvilo_nerkeli_feria_del_milenio.json`: 6 of 15) —
roughly a quarter to two-fifths of eligible states, never a blanket rewrite. A state whose only
choice is `"..."` (a pure continuation, no real player decision) is still eligible.

For a **two-NPC dialog**, each state already has an explicit per-NPC selector
(`execute as @e[type=taterzens:npc,name=<Name>,limit=1] run function ...`) instead of
`@interlocutor` — keep that selector exactly as-is and only swap the function path. Never let one
speaker's line end up pointed at the other NPC's selector.

Never assign a gesture to an `end`/`end_dialogue` state — its `action` (if any) is
`resume_routine`/`end_with_gift`, not performance, and stays untouched.

**Sounds** — no-op today. `resourcepack/`'s custom-sound layer is listed "planned" in README Layer 4
and nothing in this pack calls `playsound` or ships a `sounds.json` yet. Don't build one here to fill
the gap.

**Confirm before writing.** Present the chosen upgrades as a short list (state id → gesture → the
clause that justified it) and confirm (AskUserQuestion: proceed / let me adjust) before editing the
file — the same lightweight checkpoint `nuvilo_nerkeli_feria_del_milenio.json` got. Content changes
inside a dialog file are easy to miss in a raw JSON diff, so this is worth the one extra round trip
even though it's now part of the same skill run rather than a separate invocation.

Apply the confirmed changes and validate the file is still well-formed JSON before moving on to Step
4. Never invent a gesture a line's text doesn't actually support just to hit a ratio, and never touch
any NPC's `spawn.mcfunction` for this — confirmed by reading `load.mcfunction`, `tick.mcfunction`, and
every `gesture_*.mcfunction`: the whole gesture system is wired once, globally (scoreboard objectives
in `load.mcfunction`; `gesture_tick`/`nod_tick` called every tick for every entity, not per-NPC) and
activates dynamically the instant a dialogue action fires — no per-NPC registration needed.

## Step 4 — Log what's still open

Add or update a section in `TODO.md` for each newly-embodied character (and the dialog, if its
registration was left unresolved in Step 2): skin, movement mode, `spawn_position`,
`spawn.mcfunction`, UUID capture — the same shape as the existing Sonoros and Nawom & Morkulo
sections. Gesture-baking is no longer one of these open items — Step 3 already did it — so don't log
it as pending. Don't silently resolve anything else here either.

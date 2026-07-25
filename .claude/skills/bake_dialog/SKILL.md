---
description: Add expressive gestures (and, once the pack has a sound system, sounds) to a Blabber dialog file — replacing a chosen minority of its default nod_up_down actions with an emotionally-matched gesture. Use right after /enact produces a fresh dialog, or standalone on any existing dialog in data/luminacion/blabber/dialogues/ that still only has the uniform default nod.
disable-model-invocation: true
---

Bakes performance into an already structurally-complete Blabber dialog: swaps a minority of its
states' default `nod_up_down` action for a specific gesture (`gesture_wave`, `gesture_point`, ...)
wherever a line's own text supports it, so the conversation reads as staged rather than uniformly
nodding through every line. This is the pass Döran's three dialogues and
`nuvilo_nerkeli_feria_del_milenio.json` got by hand; this skill packages that same judgment call so
it doesn't depend on being asked for by name each time, and can run on any dialog, not only
immediately after an enactment.

Sound hooks are the same idea in principle — Step 4 below is a placeholder for when they arrive —
but `resourcepack/`'s custom-sound layer is still "planned, not started" (README Layer 4): there is
no `sounds.json` and no `playsound` call anywhere in this pack yet. Don't invent one; Step 4 stays a
no-op until that system actually exists.

## Step 0 — Resolve the target dialog

- **Called from `/enact`:** operate on the dialog file that skill's Step 4 just wrote — no extra
  question needed.
- **Invoked directly with an argument:** resolve it against `data/luminacion/blabber/dialogues/`
  (accept a bare file name with or without `.json`, or a full path).
- **Invoked directly with no argument:** list the non-template files in that folder (exclude
  `_template_*.json`) and ask (AskUserQuestion) which one to bake.

## Step 1 — Check what's already there

Read every state's `action.value` in the target file. A dialog counts as **already baked** the
moment any state's action calls something other than the uniform default — `gesture_wave`,
`gesture_point`, `gesture_shrug`, `nod_left_right` used for an actual negation, etc. Every
freshly-`/enact`ed or freshly-templated dialog is uniform `nod_up_down` on every non-`end` state
(see the templates' own `_usage` notes), so "uniform" is the unbaked signal — not "has any action at
all."

- **Already baked:** show the user a compact list of every state that currently carries a
  non-default gesture (state id, one-clause gist of the line, current gesture), then ask
  (AskUserQuestion): leave it alone, review/adjust specific states, or add more coverage. Don't redo
  a human's earlier choices without being asked — stop here unless they pick one of the change
  options.
- **Not yet baked** (uniform `nod_up_down`, or an `action` missing entirely on some states): go to
  Step 2.

**`look_up`/`look_down` are a separate, deliberate mechanism — never touch them.** A handful of
dialogs (the `khaoe_farlis_*` scenes, `khaoe_calendario_mecanografico`) use these instead of
`nod_up_down` on a state where the NPC is looking at something large right in front of them (a
tower, a castle miniature, a ruin). Confirmed by reading the functions themselves: `look_up`/
`look_down` is a single one-shot `tp` that sets an absolute head pitch and holds it *indefinitely*
(no timer, no per-tick cost) until something else changes it — and `nod_up_down`'s own header says
its dip is a *relative* delta specifically so a prior `look_up`/`look_down` pose survives the nod
on top of it. A `gesture_*`, by contrast, auto-clears after 2.5s and explicitly can't be paired with
a nod on the same state. Converting one of these to a gesture would both cut short a pose meant to
hold through the whole beat and block the nod from playing during it — a regression, not a
consistency win (this exact swap was tried and reverted 2026-07-25). Leave any `look_up`/`look_down`
state exactly as-is in every step below; it doesn't count as "unbaked," and it's not a candidate for
Step 2's table even when a line's content would otherwise suggest one of that table's gestures.

## Step 2 — Choose which states get an upgraded gesture

Read every non-`end`/`end_dialogue` state's `text` (strip a two-NPC dialog's `"Name: "` prefix only
for reading — never edit it). For each, judge whether the line's content reads as something more
specific than a neutral "I am currently talking" nod:

| Reads as... | Gesture |
|---|---|
| Greeting, farewell, beckoning someone in | `gesture_wave` (`gesture_wave_left` for variety when a scene already used the right-handed wave) |
| Making a point, an enthusiastic reveal, "here's the thing" | `gesture_point` / `gesture_point_left` |
| Formal, solemn, showing respect | `gesture_bow` |
| Not sure / doesn't know / indifferent / conceding a point | `gesture_shrug` |
| Open explanation, presenting or inviting, "who's to say" | `gesture_palms_up` |
| Musing, admitting a gap, a surprised realization | `gesture_scratch_head` / `gesture_scratch_head_left` |
| Humor, teasing, a self-deprecating aside, "Ha" | `gesture_laugh` |
| Mild disagreement or correction | `nod_left_right` |
| Firm refusal or rejection | `gesture_no` |
| Deadpan disbelief, exasperation, secondhand embarrassment | `gesture_face_palm` |
| Skeptical, defensive, or prideful stance | `gesture_cross_arms` |
| Triumph, excitement | `gesture_jump` |

Everything else stays the default `nod_up_down` — most lines are informational connective tissue and
should. Calibrate against dialogs that already have this treatment (`doran_four_castles.json`: 3 of
7 states; `doran_eras_of_culture.json`: 2 of 8; `nuvilo_nerkeli_feria_del_milenio.json`: 6 of 15) —
roughly a quarter to two-fifths of eligible states, never a blanket rewrite. A state whose only
choice is `"..."` (a pure continuation, no real player decision) is still eligible — the two-NPC
dialog above gestures freely on those.

For a **two-NPC dialog**, each state already has an explicit per-NPC selector
(`execute as @e[type=taterzens:npc,name=<Name>,limit=1] run function ...`) instead of
`@interlocutor` — keep that selector exactly as-is and only swap the function path. Never let one
speaker's line end up pointed at the other NPC's selector.

Never assign a gesture to an `end`/`end_dialogue` state — its `action` (if any) is
`resume_routine`/`end_with_gift`, not performance, and stays untouched.

## Step 3 — Confirm before writing

Present the chosen upgrades as a short list (state id → gesture → the clause that justified it) and
confirm (AskUserQuestion: proceed / let me adjust) before editing the file — the same lightweight
checkpoint that worked for `nuvilo_nerkeli_feria_del_milenio.json`. Content changes inside a dialog
file are easy to miss in a raw JSON diff, so this is worth the one extra round trip.

## Step 4 — Sounds (placeholder)

No-op today. `resourcepack/`'s custom-sound layer is listed "planned" in README Layer 4 and nothing
in this repo calls `playsound` or ships a `sounds.json` yet. Once that system exists, this step
becomes the sound equivalent of Steps 1–3: detect what's already wired, propose additions per-state
matched to the line's content, confirm, write. Don't build a sound mechanism here to fill the gap —
flag it in `TODO.md` instead if the user wants it prioritized.

## Step 5 — Write and report

Apply the confirmed changes, validate the file is still well-formed JSON, and report back which
states changed and to what. No registry/hearsay/TODO updates here — that's `/enact`'s job (its
Steps 5–7) or, for a hand-written dialog, whatever process created it; this skill only ever touches
the one dialog file's `action` fields.

Never touch any NPC's `spawn.mcfunction` for this — confirmed by reading `load.mcfunction`,
`tick.mcfunction`, and every `gesture_*.mcfunction`: the whole gesture system is wired once,
globally (scoreboard objectives in `load.mcfunction`; `gesture_tick`/`nod_tick` called every tick
for every entity, not per-NPC) and activates dynamically — a gesture's own `tag @s add
luminacion.gesture_active` and marker-item swap happen the instant the dialogue action fires, with
nothing pre-registered on that entity beforehand. `npc_routine_tick.json` is the one tag file that
*does* need a per-NPC entry, but that's the roaming pause/resume system (`check_proximity`), an
unrelated mechanism — no spawn function in this pack has ever mentioned a gesture. Any NPC that can
already run a dialogue can already run every gesture in the table above.

## What this skill never does

- Never invents a gesture a line's text doesn't actually support, just to hit a ratio.
- Never overwrites an already-baked state without the user explicitly choosing to change it.
- Never touches an `end`/`end_dialogue` state's action.
- Never builds a sound mechanism that doesn't exist yet in the pack.
- Never repoints a two-NPC dialog's gesture at the wrong NPC's selector.

---
description: Build a Taterzens spawn function (and every supporting function) for an NPC that's already registered in _maps/npcs/registry.json with at least one written Blabber dialog. Follows README §3/§4 and the _action_templates conventions in _maps/actions/registry.json. Use when the user wants to spawn/wire up an NPC that doesn't have a spawn.mcfunction yet, or add a new dialog/state to one that does.
disable-model-invocation: true
---

Builds `functions/npcs/<npc_key>/spawn.mcfunction` and whatever else it needs (routine
pause/resume, states, paths, random-dialog wiring) from the templates in `_templates/npcs/`, per
README §3 ("Building a new NPC, start to finish") and §4 ("Routine pause/resume"), plus the
`_action_templates` conventions documented in `_maps/actions/registry.json`. This is a
file-authoring skill — it does not run Minecraft commands or touch a live server. Every run ends
with the user manually running `/function luminacion:npcs/<npc_key>/spawn` in-game.

Nothing here gets decided silently. Ask (AskUserQuestion where the choice has clean discrete
options, plain conversation otherwise) for anything not already pinned down in the registry, the
dialog file(s), or TODO.md — movement mode, position/waypoints, and what fires on right-click are
never guessed.

## Step 0 — Preconditions

Confirm before starting, and stop to resolve any gap rather than guessing past it:

1. **NPC is registered.** `_maps/npcs/registry.json` has an entry for this NPC (`display_name` at
   minimum). If `skin` is blank, ask for a mineskin URL now or confirm the user wants to leave it
   for later (matching the Nuvilo precedent — spawn.mcfunction can note the skin line as a TODO
   and skip `heal_skin.mcfunction` until it's filled in).
2. **At least one dialog exists** in `data/luminacion/blabber/dialogues/` for this NPC, or the
   user is fine with a spawn function that has no dialog wired yet (rare — most NPCs exist to
   talk). If this NPC needs a dialog written first, point to the three templates in that folder
   (`_template_one_off`/`_template_linear`/`_template_branching`) or the `/enact` skill, and pause
   here until at least one exists.

## Step 1 — Verify the nod standard on every dialog involved

Every non-`end_dialogue` state in every Luminacion dialog fires an action on entry — this is the
house style, not optional per-dialog flavor. The baseline is `nod_up_down`:

```json
"action": {
  "type": "blabber:command",
  "value": "execute as @interlocutor run function luminacion:npcs/_shared/nod_up_down"
}
```

but a minority of states in a fully-baked dialog carry a more specific gesture instead
(`gesture_wave`, `gesture_shrug`, `nod_left_right` for a negation, ...) where the line's own text
supports it — see the `bake_dialog` skill for the full gesture vocabulary and how that selection is
made. Never call `nod_up_down_clear`, `nod_left_right_clear`, or `nod_tick` directly from a dialog —
those are internal, fired only from `nod_tick.mcfunction`'s own per-entity countdown, not standalone
gestures; see `_shared/nod_up_down.mcfunction`'s header.

If any non-end state is missing an `action` entirely, that's a gap, not a stylistic choice — add
`nod_up_down` as the safe default, then run `bake_dialog` on the file if it hasn't been through that
pass yet (check by the same signal `bake_dialog` uses: uniform `nod_up_down` everywhere means
unbaked). Don't second-guess an existing non-default gesture already on a state — leave it, same as
you'd leave a deliberate `give` or scoreboard-set action untouched.

## Step 2 — Movement mode

Ask (AskUserQuestion) if not already decided in TODO.md or stated by the user:

- `NONE` — stationary. Simplest: no routine pause/resume machinery needed at all.
- `FORCED_LOOK` — stands in place, turns to face nearby players. Good for a stationary-feeling NPC
  that still needs the roaming pause/resume machinery for some other reason (rare — usually just
  use `NONE` unless there's a specific reason to want the face-tracking).
- `PATH` / `FORCED_PATH` — follows waypoints (with vs. without rests/look-arounds).
- `FOLLOW` — pursues a named/UUID target.
- `FREE` — wanders within an enclosed area.

If the NPC needs to switch between multiple movement modes at different times (e.g. a stationary
"scene" state and a solo roaming state, like Nuvilo/Nerkeli), that's the `multi_state_npc` pattern
— see `_maps/actions/registry.json` → `_action_templates.multi_state_npc` — and uses
`_templates/npcs/states/stationary_state.mcfunction` / `roaming_state.mcfunction` instead of a
plain `spawn.mcfunction` right-click block. Ask which case this is before proceeding.

## Step 3 — Position and waypoints (only if movement isn't a trivial NONE-forever case)

Ask (AskUserQuestion): will the user position the NPC manually in-game after running
`spawn.mcfunction` (leave `spawn_position` null, matching Gondarfolas/Sonoros), or provide exact
coordinates now (fill `spawn_position` in the registry and uncomment the `npc tp` line)?

If movement is `PATH`/`FORCED_PATH`/part of a roaming state: ask whether waypoints are known yet.
If yes, build `functions/npcs/<npc_key>/paths/<path_name>.mcfunction` from
`_templates/npcs/paths/select_path.mcfunction` now. If not, leave the NPC standing still in PATH
mode (note this explicitly in the spawn function's comments, matching Gondarfolas) and log the gap
in TODO.md — do not invent waypoints.

## Step 4 — Right-click actions

Ask (AskUserQuestion) what fires when a player right-clicks this NPC:

- **A single dialog** — the common case. First command is
  `npc edit commands add minecraft function luminacion:npcs/_shared/enter_dialog` (always, even
  for `NONE` movement — costs nothing, keeps every NPC consistent per README §3), then
  `npc edit commands add minecraft blabber dialogue start luminacion:<dialog_id> --clicker--
  @e[name=<display_name>,limit=1,sort=nearest]`.
- **One of several independent dialogs, picked at random** — use the `random_dialog` pattern (see
  `_maps/actions/registry.json` → `_action_templates.random_dialog`): the roll lives in its own
  `roll_dialog.mcfunction`, called via a single directly-added `function` command. Do NOT use the
  vanilla `/random` command anywhere in it — confirmed in-game (twice: once nested inside `npc edit
  commands add`, once as a plain top-level `.mcfunction` line) that `/random` doesn't resolve at all
  in this pack's actual server environment, for reasons not worth chasing further. Use `time query
  gametime` reduced mod N via a scoreboard operation instead (see the action template for the exact
  four-line pattern) — every vanilla-compatible server has `time query`, no mod-specific risk. The N
  dispatch commands (`execute if score ... matches <i> run blabber dialogue start ...`) DO stay
  directly-added, one per dialog — never wrapped in a called function, since `--clicker--`
  substitution only applies to directly-added command text. Ask whether the options are equally
  likely or weighted (see the action template for how weighting works) if the user hasn't already
  said.
- **Anything additional** — give an item, set a scoreboard flag, etc. Ask explicitly; don't assume
  none. If an ending needs to combine a side effect with `resume_routine`, route it through a
  per-NPC `end_with_gift.mcfunction`-style function (Blabber's `end_dialogue` action can only run
  one command) — see `_templates/npcs/end_with_gift.mcfunction`.

## Step 5 — Build the files

From `_templates/npcs/`, filling every `<placeholder>` using the registry entry and the answers
above:

- `spawn.mcfunction` — always. Follow the exact structure of an existing one for this NPC's shape
  (`data/luminacion/functions/npcs/gondarfolas/spawn.mcfunction` for a plain single-state roaming
  NPC, `nuvilo/spawn.mcfunction` + `nuvilo/states/*.mcfunction` for multi-state).
- If movement isn't `NONE` (or this NPC has any roaming state): `resume_routine.mcfunction`,
  `check_proximity.mcfunction`, `heal_skin.mcfunction` (skip if skin is still blank),
  `heal_path.mcfunction` (header-only stub if no path exists yet, per Gondarfolas's).
  **`check_proximity.mcfunction`'s two distance checks are NOT the same radius**: the pause trigger
  (`if entity @a[distance=..2] run pause_routine`) stays at 2 blocks, but the resume safety-net
  (`unless entity @a[distance=..6] run resume_routine`) must be 6 — confirmed in-game (Döran,
  2026-07-25) that leaving it at 2 lets a click from beyond 2 blocks (trivial in creative — Taterzens
  has no interact-range override, so it's plain vanilla reach, 6 blocks in creative) undo the pause
  on the very next tick while the dialog is still open, visibly resuming the NPC's roaming mode
  mid-conversation and swallowing its nod animations in the process (see
  `_action_templates.routine_pause_resume` for the full mechanism). Match the current template
  exactly here rather than copying an older already-built NPC's file verbatim.
- If multi-state: one `states/<state_name>.mcfunction` per state instead of inlining movement/
  right-click setup directly in `spawn.mcfunction` (which should just call the default state at
  the end — see `nuvilo/spawn.mcfunction`).
- If this NPC needs a path: `paths/<path_name>.mcfunction` per named route (Step 3).

Match the comment-header style of the existing per-NPC files exactly (built-from-template note,
call-context notes where relevant) — don't drop the documentation just because it feels repetitive
between NPCs; it's what makes each file readable in isolation.

**Quote any `display_name` containing characters outside Brigadier's unquoted-string charset**
(letters, digits, `_`, `-`, `.`, `+`) in every **vanilla `@e[...]` selector** referencing it — an
umlaut/diaeresis included (`Döran`, `Dägna`). Confirmed in-game on Döran: an unquoted `ö` inside
`@e[name=Döran,...]` breaks the selector parse (`Expected end of options`), failing the whole
function's load. Fix is `@e[name="Döran",...]` — every selector occurrence, in every file
(`spawn.mcfunction`, `check_proximity.mcfunction`, `heal_skin.mcfunction`, `heal_path.mcfunction`'s
example line).

**Do NOT quote `npc create <name>` itself** — confirmed in-game this is the opposite mistake and
actively breaks the NPC: `npc create` is Taterzens' own argument, not a vanilla selector, and
doesn't strip quote characters — `npc create "Döran"` creates an NPC whose real name literally
contains the quote marks, silently mismatching every `@e[name="Döran",...]` selector elsewhere
(they're looking for the name without quotes). Leave `npc create Döran` unquoted; this argument
takes non-ASCII characters raw with no issue and was never the source of any parse error.

ASCII-only names never need any of this, but check every name against the charset above rather
than assuming.

## Step 6 — Register everything

1. If movement isn't `NONE`: add `luminacion:npcs/<npc_key>/check_proximity` to the `"values"`
   array in `data/luminacion/tags/functions/npc_routine_tick.json`.
2. Confirm every dialog used is registered under this NPC's key in `_maps/dialogs/registry.json`
   (add entries if missing — `id`, `trigger: "right_click"`, `condition: null`, a short
   `description`). For a random-dialog NPC, list all N dialogs under the one key with a `_comment`
   noting they're randomly picked (see the `doran` entry for the exact shape).
3. Update `TODO.md`'s section for this NPC (create one if it doesn't exist, matching the existing
   per-NPC sections' format): mark decided items `[x]` with what was decided and when, keep
   genuinely open items (in-game spawning, manual positioning, waypoint recording, UUID capture)
   as `[ ]`.

## Step 7 — Hand back to the user

This skill never runs Minecraft commands itself. End by telling the user, plainly, what's left for
them to do in-game:

1. `/reload` first, then check `logs/latest.log` for `Failed to load function
   luminacion:npcs/<npc_key>/...` before doing anything else. Minecraft rejects a whole
   `.mcfunction` file — not just the bad line — on a single syntax error, so a broken function is
   silently just absent (no error shown in-game), not partially working. This is how the `/random`
   and unquoted-`ö` bugs on Döran were actually found — grep the log for the NPC's key rather than
   assuming a clean load. If anything failed, read the reported line/position and fix it before
   continuing. Two confirmed standing risks, not npc-specific: **never use the vanilla `/random`
   command anywhere in this pack** (confirmed unavailable in this server environment entirely — not
   a nesting quirk, it fails identically as a plain top-level `.mcfunction` line too; use the
   `time query gametime` + scoreboard-modulo pattern in `_action_templates.random_dialog` instead),
   and **quote any display name containing non-ASCII characters** in every selector/raw-argument use
   (Step 5 above has the full list of files to check).
2. Stand at the spawn spot (if `spawn_position` is null) or confirm the fixed position.
3. `/function luminacion:npcs/<npc_key>/spawn` as an operator.
4. If a path was left unrecorded: run `functions/npcs/<npc_key>/paths/<path_name>.mcfunction` once
   waypoints are decided.
5. Capture the UUID per README §5 (`scripts/update_uuids.py generate` → `/reload` →
   `/function luminacion:admin/export_npc_uuids` → `scripts/update_uuids.py update --log ...`) —
   never copy it by hand.
6. Before testing the right-click dialog/action yourself: deselect the NPC. `npc create` (step 1 of
   `spawn.mcfunction`) auto-selects the new NPC for whoever ran it, and Taterzens shows its edit GUI
   on right-click *for that player specifically* while it's selected, instead of running its
   right-click actions — this is expected Taterzens behavior, not a bug, and every already-built NPC
   in this pack behaves normally only because its creator selected something else afterward (or
   deselected) at some point. Select a different NPC (or however you normally clear selection)
   before right-clicking to test.

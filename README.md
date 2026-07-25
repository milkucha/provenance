# Luminacion

Luminacion is the AI-assisted NPC storytelling system for **Milkantis** (a 12-year-old Minecraft world). Raw lore material gets analysed into structured encodings, NPCs are enacted and wired up through Claude Code skills, and the system outputs two packs that ship together: a **datapack** (this repo's `data/`) and a **resource pack** (gestures, localization, sounds). NPCs are Taterzens that react to player right-clicks, run Blabber dialogs, and follow their own routines (paths, wandering, etc.) — pausing to talk, then picking their routine back up.

This document is a practical, step-by-step guide to building things with the pack, plus (§0) the architecture of the system as a whole — read that first in a new session to get oriented without having to re-read the whole codebase. The rest assumes you already know *what* NPC or story you want to add — it's about *how* to wire it up.

- Minecraft 1.20.1, datapack pack format 15
- Namespace: `luminacion`
- Requires: [Taterzens](https://modrinth.com/mod/taterzens) 1.11.7, [Blabber](https://modrinth.com/mod/blabber) 1.6.2

## Index

**Starting a new session? Read the intro above plus §0–§2 first — that's the compulsory minimum for
orientation.** Everything past that, read only the section(s) the task at hand actually needs.

- [§0 System architecture](#0-system-architecture) — the four-layer system, start here every session
  - [Layer 1 — Foundation: skills + lore](#layer-1--foundation-skills--lore)
  - [Layer 2 — Supporting functions](#layer-2--supporting-functions)
  - [Layer 3 — Datapack](#layer-3--datapack)
  - [Layer 4 — Resource pack](#layer-4--resource-pack)
- [§1 Folder structure](#1-folder-structure) — compulsory: the literal `data/`/`_maps/`/`_templates/` tree
- [§2 Core concepts](#2-core-concepts) — compulsory: NPC / Dialog / Action / routine pause-resume, defined
- [§3 Building a new NPC, start to finish](#3-building-a-new-npc-start-to-finish) — the manual walkthrough (`/spawn` automates this)
  - [Step 1 — Register it](#step-1--register-it)
  - [Step 2 — Create the spawn function](#step-2--create-the-spawn-function)
  - [Step 3 — Write the dialog](#step-3--write-the-dialog)
  - [Step 4 — Spawn it in-game](#step-4--spawn-it-in-game)
  - [Step 5 — Capture its UUID](#step-5--capture-its-uuid)
  - [Step 6 — Set up routine pause/resume](#step-6--set-up-routine-pauseresume-only-if-movement-isnt-none)
- [§4 Routine pause/resume (roaming NPCs only)](#4-routine-pauseresume-roaming-npcs-only) — read only if the NPC you're touching roams
- [§5 Capturing NPC UUIDs](#5-capturing-npc-uuids) — the `scripts/update_uuids.py` workflow
- [§6 Reference](#6-reference) — lookup tables: scoreboard objectives, entity tags, movement modes, Blabber selectors, command cheat sheet
- [§7 Where design decisions live](#7-where-design-decisions-live) — why lore/story content isn't in this file
- [§8 Writing a dialog through enactment](#8-writing-a-dialog-through-enactment) — the manual walkthrough (`/enact` automates this)
  - [Step 1 — Bound the character's knowledge](#step-1--bound-the-characters-knowledge)
  - [Step 2 — Enact the conversation](#step-2--enact-the-conversation)
  - [Step 3 — Convert the transcript into a Blabber dialog](#step-3--convert-the-transcript-into-a-blabber-dialog)
  - [Step 4 — Register it](#step-4--register-it)

---

## 0. System architecture

The system has four layers, each authored from the one below it:

```
4. Resource pack      gestures (EMF/Iris model overrides), localization, custom sounds
        ↑
3. Datapack           data/luminacion/ — functions, predicates, tags, dialogues Minecraft loads
        ↑
2. Supporting layer   _templates/, _maps/actions/registry.json (_action_templates), gesture dispatch
        ↑
1. Foundation         skills (/enact, /spawn, /integrate) + _lore/ (material → analysis)
```

### Layer 1 — Foundation: skills + lore

- **Skills** (`.claude/skills/`) — repeatable procedures, invoked as slash commands:
  - **`/enact`** (`enact/SKILL.md`) — plays an NPC in a live conversation, sampled from a bounded
    slice of the lore, then converts the transcript into a registered Blabber dialog. See §8.
  - **`/spawn`** (`spawn/SKILL.md`) — builds a registered NPC's `spawn.mcfunction` (and every
    supporting function) from `_templates/npcs/`. See §3/§4.
  - **`/integrate`** (`integrate/SKILL.md`) — three independent passes: analyse newly-added
    `_lore/material/` files into `context.md`/`encodings.json`/`unknown.md` per the conventions those
    files already establish (below); audit every dialogue under `data/luminacion/blabber/dialogues/`
    for a matching `hearsay.entries` record (§8 Step 5 — unconditional by rule, but easy to miss on a
    hand-written dialogue that skipped `/enact`); and check for drift between what's referenced
    elsewhere (registries, sampled knowledge) and what's actually recorded in `encodings.json`. Run
    whichever pass(es) fit the situation, not necessarily all three.
- **`_lore/`** — the raw material and its analysis:
  - `_lore/material/` — source artifacts as uploaded: screenshots of in-game books, maps,
    spreadsheets (`Luminacion Register [Code].xlsx`, `Catastro Milkaan y Platinhëa.xlsx`, ...),
    documents. Treated as excavated primary sources — never edited, only read.
  - `_lore/analysis/context.md` — one section per material artifact, transcribing only what that
    specific source says or shows, with no cross-source reconciliation. Contradictions between
    sources are noted here, not resolved.
  - `_lore/analysis/encodings.json` — the structured, queryable form of the same material:
    `time_systems`, `locations`, `routes`, `characters`, `concepts`, `conflicts` (cross-source
    disagreements, each with a `user_resolution` once settled), and `hearsay` (claims made *in*
    dialogues — §8 Step 5). This is what `scripts/sample_lore_knowledge.py` draws an NPC's knowledge
    pool from.
  - `_lore/analysis/unknown.md` — gaps and open questions the material itself doesn't answer, plus a
    log of which have since been resolved by the user.
  - `_lore/analysis/hearsay.md` — the human-readable counterpart to `encodings.json`'s `hearsay`
    array: what's been said, by whom, where, and whether it checked out against the record.

### Layer 2 — Supporting functions

Reusable patterns every NPC/dialog is built from, so each new one doesn't reinvent structure:

- `_templates/npcs/` — placeholder-filled `.mcfunction` patterns (`spawn.mcfunction`,
  `resume_routine.mcfunction`, `check_proximity.mcfunction`, `end_with_gift.mcfunction`, plus
  `paths/` and `states/` variants for roaming/multi-state NPCs) — copied per NPC, never called
  directly. See §1.
- `data/luminacion/blabber/dialogues/_template_*.json` — the three dialog shapes (one-off, linear,
  branching). See §1/§3.
- `_maps/actions/registry.json`'s `_action_templates` — documents every right-click action pattern
  (`movement`, `give_item`, `blabber_dialog`, `routine_pause_resume`, `scripted_path`,
  `multi_state_npc`, `random_dialog`, `scoreboard_set`) with copy-paste command patterns and, for
  several, hard-won in-game debugging notes (why `/random` never resolves in this environment, why
  the pause/resume radii must differ).
- **Gesture dispatch** — `data/luminacion/functions/npcs/_shared/gesture_<name>.mcfunction` (wave,
  point, bow, shrug, palms-up, scratch-head, laugh, jump, cross-arms, no, face-palm, plus left-arm
  mirror variants `wave_left`, `point_left`, and `scratch_head_left`) plus `gesture_clear.mcfunction`
  and the `nod_up_down`/`nod_left_right` family: datapack-side functions that trigger the
  resource-pack animations below via a tag + per-entity scoreboard countdown, ticked every game tick
  from `tick.mcfunction` via `gesture_tick.mcfunction`/`nod_tick.mcfunction` — each NPC's hold/beat
  timing is independent of every other NPC's. (Replaced an earlier
  `schedule function ... replace` design, which used one datapack-wide timer shared by every gesture
  and every nod; see TODO.md "Multi-NPC gesture/nod scheduling collision" for why that broke once
  more than one NPC could gesture/nod at a time.) They physically live under `data/luminacion/`
  (layer 3) but belong here conceptually — templated dispatch for content that's actually defined one
  layer up.

### Layer 3 — Datapack

`data/luminacion/` — the pack Minecraft actually loads and calls: `functions/` (per-NPC and shared
`.mcfunction` files), `predicates/`, `tags/functions/` (load/tick hooks, the routine-tick registry),
and `blabber/dialogues/` (the written dialogs). This is what gets built *from* layers 1–2 for a given
NPC — see §1 for the full folder breakdown and §3 for the build sequence.

### Layer 4 — Resource pack

Custom client-side content shipped alongside the datapack, version-controlled in this repo's
`resourcepack/` folder (own `pack.mcmeta` + `assets/`, same idea as `data/` is to the datapack).
Currently:

- **Gestures** — a forked `player.jem`/`player_slim.jem` EMF/Iris override giving Taterzens NPCs (and
  real players) 13 animated poses, each triggered by a `CustomModelData`-tagged invisible stick in the
  main hand. Coexists with the installed Fresh Animations + FA+Player pack by forking only the two
  files that need the gesture hook — every other file (movement math, textures, cape) still falls
  through to FA+Player underneath. Full breakdown below.
- **Localization** (planned) — `assets/luminacion/lang/*.json`, generated from dialogue files by a
  not-yet-written `scripts/extract_dialogue_lang.py`.
- **Custom sounds** (planned) — not yet started.

**Wiring: repo ↔ live pack.** `resourcepack/` in this repo *is* the pack — there's no build/copy/zip
step for local dev. The live folder Minecraft/PrismLauncher actually reads from,
`resourcepacks/luminacion/`, is a Windows directory **junction** pointing back at `resourcepack/` here
(created with `New-Item -ItemType Junction`; unlike a symbolic link this needs no admin rights or
Developer Mode, since both paths are on the same local drive). Editing a file under `resourcepack/`
edits the live pack instantly — reload with `F3+T`, or a full restart if that doesn't pick it up. A
zip-based `scripts/build_resourcepack.py` (see `TODO.md`) is a separate, not-yet-built concern for
*distributing* a finished pack — irrelevant to day-to-day gesture editing.

**Gestures: how they're built, modified, and called.** Each gesture is a held **pose**, not a
keyframed animation: giving the NPC (or a real player) an invisible
`minecraft:stick{CustomModelData:<N>}` in `weapon.mainhand` makes `player.jem`/`player_slim.jem`
override that limb's rotation to a fixed (or, for wave/shrug/scratch-head/laugh, `sin()`-oscillating)
angle for as long as the item is held. Both `.jem` files are a single minified JSON line each — the
whole rig (head, body, both arms, both legs, all 13 gestures) lives in one blob of nested
`if(nbt(SelectedItem.tag.CustomModelData,<N>), <pose>, <next gesture's case>)` expressions per axis
(`right_arm.rx`/`.ry`/`.rz`, `var.body_rx`, `var.gest_headrx`, ...), eased in over a few frames by a
self-referencing `var.*` low-pass filter (proven more reliable than easing the bone key directly,
which jittered). See §6 for the `CustomModelData` value of each gesture.

- *To modify a pose* (e.g. the wave's arm-height/outward-swing adjustment made 2026-07-25): find the
  gesture's `CustomModelData` number in the §6 table, then in **both** `player.jem` and
  `player_slim.jem` locate every `if(nbt(...,<N>), torad(<deg>), ...)` branch for the axis you want to
  change (`rx` = raise/lower, `ry` = swing in/out sideways, `rz` = twist, or the oscillation term for
  gestures that move) and edit the `torad(<deg>)` value. The two `.jem` files aren't generated from one
  another — keep them in sync by hand. Because each file is one line with every gesture's branches
  nested together, edit by exact substring match (e.g. `CustomModelData,101),torad(-130)`) rather than
  by line/offset, and re-parse the file as JSON afterward — a stray bracket silently breaks a
  *different* gesture's branch instead of erroring.
- *To call a gesture* on an NPC mid-dialogue: `execute as @interlocutor run function
  luminacion:npcs/_shared/gesture_<name>` (see "Gesture dispatch" in Layer 2 above) — tags the NPC
  `luminacion.gesture_active`, gives it the marker stick, and sets that NPC's own
  `luminacion.gest_timer` score to the gesture's hold duration (2.5s/50 ticks for most); every tick,
  `gesture_tick.mcfunction` counts it down and runs `gesture_clear.mcfunction` on that NPC alone once
  it reaches 0. Never call a gesture on an NPC already mid-gesture, and never pair a gesture
  action with a `nod_up_down`/`nod_left_right` action on the same dialogue state — gestures fully own
  the pose while active (worst case for laugh, which also overrides head pitch).
- *To test a gesture* without going through a dialog, either target the nearest Taterzen directly:

  ```
  execute as @e[type=taterzens:npc,sort=nearest,limit=1] run function luminacion:npcs/_shared/gesture_wave
  ```

  or give yourself the marker item to preview the pose on your own model — a faster loop when you're
  just iterating on numbers, since the `.jem` logic keys off whoever's holding the item, NPC or player:

  ```
  item replace entity @s weapon.mainhand with minecraft:stick{CustomModelData:101}
  ```

- *Elbow joint* (working, landed 2026-07-25 — first used by the `cross_arms` gesture): `right_arm`/
  `left_arm` are each split at the vertical midpoint into a shortened shoulder segment (unchanged
  pivot) and a nested `submodels` child bone, `right_forearm`/`left_forearm`, added to that part's own
  `"submodels"` array (alongside `right_item`/`left_item`, left untouched — vanilla's held-item
  attachment is keyed to those exact names, so don't move them onto the forearm). A gesture bends the
  elbow by setting `right_forearm.rx`/`left_forearm.rx` (currently only `rx` is used — a real elbow is
  a one-axis hinge, unlike the shoulder's three); see `var.gest_rforearmrx`/`var.gest_lforearmrx` for
  the pattern (gated on a `CustomModelData` check, eased via `var.gest_rate`, identical structure to
  every other gesture var).
  - *The one true lesson*: for a nested `submodels` bone, both `translate` **and** `boxes.coordinates`
    must be small numbers in the *parent's own local frame* — not the large absolute/skin-space numbers
    top-level parts like `right_arm` itself use (e.g. `[4,12,-2,4,12,4]`). The first attempt reused
    those large numbers directly for the forearm and it rendered fully detached, because a small
    parent-relative `translate` combined with a huge box shape doesn't mean what it looks like it
    means. This was confirmed by pulling a real, shipped `wolf.jem` from Fresh Animations' own GitHub
    repo (the same author this rig already credits) and inspecting its `tail`/`tail2` nested-bone
    pair — its child bone's `translate` and `boxes.coordinates` are both small numbers in the same
    handful-of-units range, nothing like the parent's own absolute-frame box.
  - *Position and rotation both compose automatically* once nested correctly — a plain reattachment
    (forearm `rx` always 0, no gesture) needs zero extra formula work; the child just rides along with
    whatever the parent's current rotation is. Don't manually add `right_arm.rx` into the forearm's own
    rotation formula — that double-applies the parent's rotation on top of the automatic composition
    and makes things worse, not better (confirmed the hard way).
  - *Getting the exact pivot right had no shortcut* — the local-frame scale/sign/axis isn't derivable
    from the file alone; it took extensive in-game trial and error (probe values, screenshots, bisecting
    magnitude and each axis independently) to land on the final numbers: `right_forearm` translate
    `[7,17.5,0]`, `left_forearm` translate `[-4,17.5,0]`, both with `boxes.coordinates`
    `[-4,-6,-2,4,6,4]` (classic) / `[-3,-6,-2,3,6,4]` (slim) — i.e. extending from the pivot in
    *negative* local Y. A small seam remains at the elbow; accepted as fine given the blocky art style.
  - *Texture*: both segments reuse the arm's existing UV block (no skin edits). The auto-net's "cap"
    faces read top-to-bottom in **screen space** matching shoulder-to-wrist on the body — the first
    attempt had the shoulder and wrist segments' `textureOffset`s backwards (a real, visible bug, not
    just positional) and needed swapping; see the current `[40,16]`/`[40,22]`-style offset pairs on
    `right_arm`/`right_forearm` for the corrected assignment.
  - *Known imperfection*: the second-layer sleeve overlay (`right_forearm_sleeve`/`left_forearm_sleeve`)
    is **not** positionally calibrated to match the forearm — it's a flat sibling part (like
    `right_sleeve`) using its own separate, never-tuned `translate`, left over from an earlier attempt.
    Nesting it under `right_sleeve`/`left_sleeve` the same way `right_forearm` nests under `right_arm`
    was tried and reverted: it broke `cross_arms`'s elbow bend, because a bone nested under `right_sleeve`
    only inherits `right_sleeve`'s rotation (a copy of the *shoulder's* rotation only — see
    `"right_sleeve.rx":"right_arm.rx"` — never the forearm's own local bend), so the sleeve stayed
    straight while the real arm folded. Fixing this properly means either giving the sleeve's forearm
    bone its own copy of `var.gest_rforearmrx`, or nesting it under `right_forearm` instead of
    `right_sleeve` (untried) — deferred, see TODO.md.

---

## 1. Folder structure

```
Luminacion/
├── pack.mcmeta
├── data/
│   ├── minecraft/tags/functions/
│   │   ├── load.json                  → calls luminacion:load
│   │   └── tick.json                  → calls luminacion:tick
│   └── luminacion/
│       ├── functions/
│       │   ├── load.mcfunction        (registers scoreboard objectives — runs once on load/reload)
│       │   ├── tick.mcfunction        (runs every tick — drives the routine pause/resume checks)
│       │   ├── admin/
│       │   │   └── export_npc_uuids.mcfunction   (auto-generated — see §5)
│       │   └── npcs/
│       │       ├── _shared/           (used by every NPC as-is — never copied)
│       │       │   ├── pause_routine.mcfunction
│       │       │   └── enter_dialog.mcfunction
│       │       └── <npc_key>/         (one real folder per NPC you've built)
│       ├── predicates/
│       ├── tags/functions/
│       │   └── npc_routine_tick.json  (registry: which NPCs get checked each tick)
│       └── blabber/
│           └── dialogues/
│               ├── _template_one_off.json
│               ├── _template_linear.json
│               └── _template_branching.json
├── _maps/
│   ├── npcs/registry.json             (master NPC data: name, skin, city, UUID, spawn position)
│   ├── dialogs/registry.json          (NPC key → dialog IDs)
│   └── actions/registry.json          (NPC key → actions, plus reference templates for every action type)
├── _templates/
│   └── npcs/                          (copy these into data/luminacion/functions/npcs/<npc_key>/ per NPC)
│       ├── spawn.mcfunction
│       ├── resume_routine.mcfunction
│       ├── check_proximity.mcfunction
│       └── end_with_gift.mcfunction
├── resourcepack/                      (the resource pack — §0 Layer 4; junctioned into
│   │                                   resourcepacks/luminacion/ in the PrismLauncher instance)
│   ├── pack.mcmeta
│   └── assets/
│       ├── luminacion/                (invisible gesture-marker item model + texture)
│       └── minecraft/emf/cem/         (player.jem, player_slim.jem — the gesture pose overrides)
└── scripts/
    └── update_uuids.py                (automates NPC UUID capture — see §5)
```

`_templates/` holds placeholder-filled patterns to copy — kept outside `data/` on purpose, since Minecraft
parses every `.mcfunction` file it finds under `data/`, and these still have unfilled `<placeholders>` that
aren't valid command syntax. The Blabber dialogue templates (`_template_one_off.json` etc.) are the
exception: they stay under `data/luminacion/blabber/dialogues/` since their placeholders live inside JSON
string values, which parse fine either way. Anything named `_shared` is called directly and never copied.

---

## 2. Core concepts

**NPC** — a Taterzen entity. Everything about it (identity, skin, movement, right-click actions) is set once via `/npc edit` commands in that NPC's `spawn.mcfunction`.

**Dialog** — a Blabber conversation, defined as JSON in `blabber/dialogues/`. Started from an NPC's right-click actions.

**Action** — anything a right-click triggers: opening a dialog, giving an item, setting a scoreboard flag, etc. `_maps/actions/registry.json` documents every action type with copy-paste command patterns.

**Routine pause/resume** — if an NPC roams (has a movement mode other than `NONE`), it automatically stops within 2 blocks of a player or when clicked, and resumes its route afterwards. Covered in full in §4.

---

## 3. Building a new NPC, start to finish

### Step 1 — Register it

Add an entry to `_maps/npcs/registry.json` under `"npcs"`:

```json
"maren": {
  "display_name": "Maren",
  "skin": "https://www.mineskin.org/...",
  "city": "Milkaan",
  "taterzen_name": "Maren",
  "taterzen_uuid": "",
  "spawn_position": null,
  "backstory": "",
  "knowledge": {
    "education": { "percent": null, "mode": "", "topic": null, "items": [] },
    "experience": []
  }
}
```

Leave `taterzen_uuid` empty for now — that's filled in automatically at the end (§5). `backstory` and
`knowledge` are optional for a hand-built NPC like this one — they exist for enacted characters (§8)
and are always filled in by the `/enact` skill. `knowledge.education` is the lore sample drawn once
at creation and never changed after; `knowledge.experience` (plus `backstory`, conceptually) is
everything the character has picked up living through scenes, and keeps growing over time.

### Step 2 — Create the spawn function

Copy `_templates/npcs/spawn.mcfunction` to `data/luminacion/functions/npcs/maren/spawn.mcfunction`, then fill in every `<placeholder>` using the registry entry from Step 1. This file sets: identity, skin, movement mode, permission level, and right-click actions.

Read the comments in the template as you go — they explain each section. In particular:

- **Movement**: pick `NONE` (stationary) or one of `FORCED_LOOK` / `PATH` / `FORCED_PATH` / `FOLLOW` / `FREE` (roaming). If it's not `NONE`, you'll need §4 as well.
- **Right-click actions**: the first line should always be `npc edit commands add minecraft function luminacion:npcs/_shared/enter_dialog` when a dialog is involved — it pauses the NPC and marks it mid-conversation before the dialog opens. Don't skip it, even for stationary NPCs — it costs nothing and keeps every NPC consistent.

### Step 3 — Write the dialog

Copy one of the three dialog templates into `blabber/dialogues/`:

| Template | Use for |
|---|---|
| `_template_one_off.json` | A single line the NPC says, no branching |
| `_template_linear.json` | A short back-and-forth with no choices |
| `_template_branching.json` | Player picks between options, leading to different endings |

Fill in the text, rename states to something meaningful, and — important — replace `<npc_key>` in every `end_dialogue` action with the key from Step 1 (`maren`). That's what lets the dialog hand the NPC's routine back when the conversation ends. If the NPC's movement mode is `NONE`, this doesn't matter functionally, but leave it filled in anyway for consistency.

If an ending needs to give an item *and* resume the routine, route it through `end_with_gift.mcfunction` (see the branching template — it already does this for you).

Then register the dialog in `_maps/dialogs/registry.json` under this NPC's key.

### Step 4 — Spawn it in-game

Stand at the spawn location (or set `spawn_position` in the registry and uncomment the `npc tp` line), then as an operator:

```
/function luminacion:npcs/maren/spawn
```

### Step 5 — Capture its UUID

See §5 below — don't do this by hand.

### Step 6 — Set up routine pause/resume (only if movement isn't NONE)

See §4 below.

---

## 4. Routine pause/resume (roaming NPCs only)

If an NPC's movement mode is anything other than `NONE`, it needs two more files so it stops for conversations instead of walking through them.

1. Copy `_templates/npcs/resume_routine.mcfunction` → `data/luminacion/functions/npcs/<npc_key>/resume_routine.mcfunction`. Fill in `<MODE>` to match the movement mode you set in spawn.mcfunction (for `FOLLOW`, use the `FOLLOW <name>` / `FOLLOW UUID <uuid>` form shown in the comments).

2. Copy `_templates/npcs/check_proximity.mcfunction` → `data/luminacion/functions/npcs/<npc_key>/check_proximity.mcfunction`. Fill in `<display_name>` and `<npc_key>`.

3. Add that file's path to the `"values"` array in `data/luminacion/tags/functions/npc_routine_tick.json`:

   ```json
   { "values": ["luminacion:npcs/maren/check_proximity"] }
   ```

That's it. From then on, the tick loop stops the NPC the moment a player gets within 2 blocks (or clicks it), and resumes its route once no player is within 6 blocks or the dialog ends.

**Why both a click-pause and a proximity-pause?** So the NPC doesn't keep wandering off mid-approach before the player gets a chance to click it — it settles as soon as someone's nearby, not only once they've already interacted.

**Why the tick check also handles resuming, not just the dialog ending?** Blabber does not run its end-of-dialog action if a player exits early (Escape key, disconnect, etc.) — so a "resume when the dialog action fires" rule alone can leave an NPC stuck paused forever. The tick check is the safety net: it resumes any paused NPC the moment no player is within range, regardless of how the conversation ended.

**Why the resume radius (6 blocks) is wider than the pause trigger (2 blocks) — don't make these match.** Blabber freezes the player's movement while its screen is open, so distance from the NPC can't grow *during* a conversation — but that only guarantees the resume check stays quiet if the player was already inside its radius the moment they clicked. Taterzens has no interact-range override (`config/Taterzens/config.json` doesn't set one), so a click can land from plain vanilla reach — 3 blocks survival, 6 creative. A resume radius of 2 would read a click from 3+ blocks away as "nobody nearby" on the very next tick and undo the pause while the dialog is still open — confirmed in-game (Döran, 2026-07-25): he visibly wandered off mid-conversation, and the resulting movement swallowed his nod animations too (walking overwrites head rotation every tick, fighting the nod's own writes). 6 blocks covers creative reach with no margin to spare — see `_maps/actions/registry.json` → `_action_templates.routine_pause_resume` for the full writeup.

Full technical rationale (with source references) lives in `_maps/actions/registry.json` under `_action_templates.routine_pause_resume`.

---

## 5. Capturing NPC UUIDs

Taterzens NPCs need their UUID recorded in the registry so other functions (paths, follow targets, etc.) can reference them reliably. This is scripted — never copy a UUID by hand.

After spawning one or more NPCs and filling in their registry entries:

```bash
python scripts/update_uuids.py generate
```

Then in-game, as an operator:

```
/reload
/function luminacion:admin/export_npc_uuids
```

Then back on the command line:

```bash
python scripts/update_uuids.py update --log "<path to logs/latest.log>"
```

Not sure where your log file is? Run `python scripts/update_uuids.py locate-log`.

This updates `taterzen_uuid` for every NPC in the registry that was exported. Safe to re-run any time you add new NPCs — it only touches entries it finds a fresh export for.

---

## 6. Reference

### Scoreboard objectives (registered in `load.mcfunction`)

| Objective | Type | Use |
|---|---|---|
| `luminacion.bool` | dummy | 0/1 flags (score holder name = variable name) |
| `luminacion.int` | dummy | arbitrary integers |

### Entity tags used by the routine system

| Tag | Meaning |
|---|---|
| `luminacion.paused` | This NPC's movement is currently stopped (dialog or proximity) |
| `luminacion.in_dialog` | This NPC is mid-conversation — the tick check won't try to resume it |

### Taterzens movement modes

| Mode | Behaviour |
|---|---|
| `NONE` | Stationary (default) |
| `FORCED_LOOK` | Looks at players within 4 blocks, doesn't move |
| `PATH` | Follows its path, with rests and look-arounds |
| `FORCED_PATH` | Follows its path strictly, no rests |
| `FOLLOW` | Pursues a named/UUID target |
| `FREE` | Wanders freely within an enclosed area |

### Gesture `CustomModelData` values (see Layer 4 for how these work)

| Gesture | `CustomModelData` | `mcfunction` | Pose |
|---|---|---|---|
| Wave | 101 | `gesture_wave` | Right arm raised + swung outward; `rz` oscillates (`sin(age*0.65)`) for the side-to-side wave motion |
| Point | 102 | `gesture_point` | Right arm extended forward, static |
| Bow | 103 | `gesture_bow` | Body pitches forward 25°; arms untouched, hang naturally |
| Shrug | 104 | `gesture_shrug` | Both arms raised symmetrically, with a small idle bounce (`sin(age*0.4)`) |
| Palms-up | 105 | `gesture_palms_up` | Both arms raised + rotated, static — originally prototyped as "cross-arms", renamed once it visually read as palms-up instead |
| Scratch-head | 106 | `gesture_scratch_head` | Right arm to head height, with an intermittent scratching wobble |
| Laugh | 107 | `gesture_laugh` | Both arms + body + head all animated — overrides head pitch too, so never pair with a `nod_*` action on the same dialogue state |
| No | 108 | `gesture_no` | Both arms raised in front of the chest and swept side to side in sync (`ry` oscillates, `sin(age*1)`, mirrored between arms) while the head shakes side to side (`sin(age*1.3)`) via a new `var.gest_headry` low-pass filter — the yaw counterpart to Laugh's `var.gest_headrx` pitch override, since no earlier gesture touched head yaw. A "no, no" rejection gesture. Rates started much higher (`age*3`/`age*4`) and were slowed down after in-game testing read as a tremor/panic shake rather than a deliberate "no". Overrides head yaw as well as both arms, so never pair with a `nod_left_right` action on the same dialogue state, same caveat as Laugh/`nod_up_down` |
| Face-palm | 109 | `gesture_face_palm` | Right arm raised to head height and swung inward across the face (`ry` at -20°, shallower than Scratch-head's outward +55° — pulled back from an initial -40° after in-game testing showed the hand clipping into the head mesh), while the head pitches down statically via `var.gest_headrx` (the same variable Laugh already overrides) and shakes slowly side to side instead of nodding, via `var.gest_headry` (`sin(age*0.6)`) — the yaw variable "No" introduced. Own slower `var.gest_rate` of 3 (vs. the default 6) for a smoother ease-in. Reads as quiet disapproval/disappointment. Right hand only for now; a left-hand mirror (209, following the established +100 convention) is planned but not yet built |
| Jump | 110 | `gesture_jump` | Right arm raised straight overhead (fist-pump; own faster `var.gest_rate` of 10 so the arm snaps up quickly), `body.ty`/`right_leg.ty`/`left_leg.ty` all share a new `var.gest_bodyty` term — a Mario level-clear-style victory jump. Unlike the other 7 gestures, this one moves body **translation**, not just limb rotation, and it's a genuine one-shot: `var.gest_jumpclock` is a self-resetting per-gesture stopwatch (`if(CMD110, var.gest_jumpclock+frame_time, 0)`, in real seconds via `frame_time`, not the entity's global `age`) driving a single `sin()` hump clamped at its peak (`min(var.gest_jumpclock,pi/9)*9`) so the bounce fires exactly once, in sync with the arm raising, instead of repeating or drifting out of phase with an arbitrary `age` offset the way a naive `sin(age*rate)` would. Also the only gesture with a non-standard hold: `gesture_jump.mcfunction` sets `luminacion.gest_timer` to `12` (0.6s) instead of the usual `50` (2.5s), so the arm drops the instant the ~7-tick hop lands instead of staying pumped for a held pose — safe to vary per-gesture like this since the timer is per-entity (see "Gesture dispatch" in Layer 2) |
| Wave (left) | 201 | `gesture_wave_left` | Left-arm mirror of Wave: `left_arm.rx` shares Wave's `rx` (unmirrored — raise/lower reads the same on either arm), `ry`/`rz` are sign-flipped from Wave's values, including the `sin(age*0.65)` oscillation term. Mirror-variant `CustomModelData` numbering convention: base gesture's number + 100 |
| Point (left) | 202 | `gesture_point_left` | Left-arm mirror of Point, same convention as Wave (left) |
| Scratch-head (left) | 206 | `gesture_scratch_head_left` | Left-arm mirror of Scratch-head, same convention as Wave (left) |
| Cross-arms | 111 | `gesture_cross_arms` | Both arms raised and swung in across the chest, **and** both elbows bend via the `right_forearm`/`left_forearm` bones (the first gesture to use them — see "Elbow joint" above) |

### Blabber special selectors

| Selector | Resolves to |
|---|---|
| `@s` | The player, inside a dialog's `blabber:command` action |
| `@interlocutor` | The NPC entity — only resolves while the command's executor is still the player, so never nest it inside an `execute as ...` that's already switched away from the player |

### Key commands cheat sheet

```
/npc create <name>                          create + select an NPC
/npc select name <name>                     select an existing NPC
/npc list                                   list all loaded NPCs
/npc edit skin <mineskin URL or player>     set skin
/npc edit movement <MODE>                   set movement mode
/npc edit commands add minecraft <command>  add a right-click action
/npc edit commands setPermissionLevel <0-4> set execution authority for right-click actions
/blabber dialogue start <id> <target> [interlocutor]   start a dialog
```

---

## 7. Where design decisions live

This README documents *how the pack works*. Story content, NPC personalities, routes, and dialog writing are design decisions — they live in `_lore/` and the maps under `_maps/`, not in this file.

---

## 8. Writing a dialog through enactment

One way to write a Blabber dialog: play the NPC in a live conversation first, then convert the transcript. This is how `sonoros_lost_traveler.json` was written. Steps below are the manual version — the `/enact` skill (`.claude/skills/enact/SKILL.md`) runs this whole procedure, including the setup questions, the two-interlocutor branching (player vs. another enacted character), registration, and — as its final step — the `/bake_dialog` skill (`.claude/skills/bake_dialog/SKILL.md`), which replaces a minority of the dialog's default `nod_up_down` states with an emotionally-matched gesture from §6's table. `/bake_dialog` also runs standalone on any existing dialog file, not only right after an enactment — useful for the older dialogs still waiting on this pass (see `TODO.md`). `/enact` (plus its `bake_dialog` step) is the recommended way to do all of this now; the steps below are still worth knowing, since the skills just automate them.

### Step 1 — Bound the character's knowledge

Before playing the NPC, decide what slice of `_lore/analysis/` (`context.md`, `encodings.json`, `unknown.md`) they actually know. Don't hand-pick a flattering or convenient subset — flatten every atomic fact across the analysis (locations, concepts, characters, routes, era entries, conflicts...) into one pool and randomly sample a small percentage of it. 5% produced a character who was coherent but genuinely, unevenly gapped — knowledgeable about a handful of unrelated things, ignorant of most everything else — which is a far more natural starting point than a hand-curated backstory. Keep the sample somewhere referenceable for the length of the session, since you'll be checking answers against it constantly.

The pool also includes every individual claim from `encodings.json`'s `hearsay.entries` (one pool item per claim, tagged category `hearsay`), at the same odds as any objective-record fact. This is deliberate: a claim one NPC made in a past dialogue can resurface as something a new character has "heard," exactly like real gossip — including claims that were invented character texture, not lore (Gondarfolas's Bracco, Nuvilo's Navalius), and claims already flagged `consistent_with_context: false` or `null`. A sampled `hearsay` item is never upgraded to fact by being sampled — play it as something the character heard, attributed to whoever said it if pressed ("I heard Gondarfolas say once that..."), never as settled history. This is how the lore is meant to accrete emergent, subjective material on top of the fixed objective record over time.

### Step 2 — Enact the conversation

Play the NPC strictly within that sample.

- **Never invent as fact anything that contradicts or extends the lore itself.** If a question falls outside the sample, the character genuinely doesn't know — say so, in character, rather than papering over the gap with new "lore." Don't volunteer the boundary unprompted either; the honesty is about never lying when it matters, not about narrating your own limits at every turn.
- **Personality, mannerisms, small human texture — invent freely.** A reason for being somewhere, a job, a turn of phrase, a mood: a person is more than their entry in the record, and the lore was never going to specify any of that anyway.
- **Write short.** Blabber's dialog boxes are small. Keep both sides of the conversation to a few sentences per turn from the start — it saves a rewrite later, and it's closer to how the final dialog will actually read in-game.

### Step 3 — Convert the transcript into a Blabber dialog

Once the conversation feels complete, restructure it — don't add to it:

- Each NPC line becomes a state's `"text"`.
- Each player line becomes a `"choices"[].text` leading to the next state.
- Where the conversation had a genuine fork — a moment where a different in-character reaction would plausibly lead somewhere slightly different — render it as a real multiple-choice branch (see `_template_branching.json`). Converge branches back into a shared state as soon as the divergent flavor is spent; don't let the tree sprawl past what the actual conversation supported.
- Rename every state to a short, meaningful id (never leave `state_1`, `state_2`...).
- Wire up the final `end_dialogue` state per the existing templates, including the `resume_routine` call *only if* the NPC ends up with a roaming movement mode (§4) — if it's stationary (`NONE`), drop that action entirely.

### Step 4 — Register it

Same as §3 Step 1 and Step 3 above: add the NPC to `_maps/npcs/registry.json` (a blank `skin`/`taterzen_uuid`/`spawn_position` is fine — the dialog can exist before the NPC is spawned) and register the dialog itself under that NPC's key in `_maps/dialogs/registry.json`.

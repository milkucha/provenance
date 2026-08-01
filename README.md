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
- [§4 Routine pause/resume (every NPC)](#4-routine-pauseresume-every-npc) — read for every NPC, including stationary (`NONE`) ones
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
    elsewhere (registries, sampled knowledge, and `tales`/`discoveries` `touches` refs) and what's
    actually recorded in `encodings.json`. Run whichever pass(es) fit the situation, not necessarily
    all three.
  - **`/tell`** (`tell/SKILL.md`) — records a tale the user tells directly, outside any excavated
    document or character's mouth, into `_lore/tale/` and `encodings.json`'s `tales` category.
  - **`/discover`** (`discover/SKILL.md`) — records a discovery the user states directly, with its own
    credited (or explicitly uncredited) responsible party, into `_lore/discoveries/` and
    `encodings.json`'s `discoveries` category.
  - **`/character`** (`character/SKILL.md`) — maintains a character's sheet in
    `_maps/npcs/registry.json` on its own, without running a conversation: backstory, city, knowledge
    sample, **criterion**, and **lifespan**. It owns the criterion model — Step 4 derives one, Step 5
    rolls a lifespan, and Step 6 is the canonical reference for how a criterion changes. `/enact`
    points back at those rather than restating them.
- **`_lore/`** — the raw material and its analysis, plus three further sources of truth: two told
  directly by the user, and one (`facts/`) that is universal and never sampled:
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
  - `_lore/tale/` — a third source of truth, populated by `/tell`: tales told directly by the user,
    the world's author, one file per tale (`<slug>.md`). Unlike hearsay, a tale **is** folded into the
    objective arrays above (via a `tale:<id>` source tag), never overwriting an existing entry. See
    `_lore/tale/_index.md` and `encodings.json`'s `tales` category.
  - `_lore/discoveries/` — a fourth source of truth, populated by `/discover`: things the user states
    directly as now known, each crediting a responsible party or explicitly none. Processed
    identically to a tale. See `_lore/discoveries/_index.md` and `encodings.json`'s `discoveries`
    category. (Not to be confused with `_lore/facts/` below — a discovery is lore, and gets sampled
    like all lore.)
  - `_lore/facts/` — a fifth source of truth, and the only one that is **never sampled**. The handful
    of things true of being a person in this world at all: that life ends, and that everyone wants
    theirs to have been worthwhile. Every character knows every fact in full, from creation,
    regardless of their education percentage — so facts live in their own `facts.json`, deliberately
    outside `encodings.json`, and must never be folded into it (`sample_lore_knowledge.py` raises if
    they are). Unlike every other category, a fact has no provenance, cannot be attributed, and
    cannot be dismissed: it's the floor a character's contestable criterion stands on, not part of
    the argument. Loaded unconditionally by `/enact` for every character in every scene. See
    `_lore/facts/_index.md`.

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
  point, bow, shrug, palms-up, scratch-head, laugh, jump, cross-arms, no, face-palm, flex-arm, plus
  left-arm mirror variants `wave_left`, `point_left`, and `scratch_head_left`) plus `gesture_clear.mcfunction`
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

- **Gestures** — 13 animated poses (plus left-arm mirror variants) for Taterzens NPCs and real
  players: a forked `player.jem`/`player_slim.jem` EMF/Iris override, each pose triggered by a
  `CustomModelData`-tagged invisible stick in the main hand, coexisting with the installed Fresh
  Animations + FA+Player pack. **All detail lives in `GESTURES.md`** — the per-gesture
  `CustomModelData` table, how to modify/call/test a pose, the elbow-joint rig, and the hard-won
  `.jem` lessons. Read that file when (and only when) working on gestures — it's reference
  material, not session orientation.
- **Localization** (planned) — `assets/luminacion/lang/*.json`, generated from dialogue files by a
  not-yet-written `scripts/extract_dialogue_lang.py`.
- **Custom sounds** (planned) — not yet started.

**Wiring: repo ↔ live pack.** `resourcepack/` in this repo *is* the pack — no build/copy/zip step
for local dev. The folder Minecraft actually reads, `resourcepacks/luminacion/`, is a Windows
directory junction pointing back at `resourcepack/` here, so edits apply instantly (reload with
`F3+T`, or a full restart if that doesn't pick it up). The full wiring rationale — why a junction,
and the separate not-yet-built distribution zip — is in `GESTURES.md`.

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
├── _lore/
│   ├── material/                      (excavated primary sources — read-only)
│   ├── analysis/                      (context.md, encodings.json, unknown.md, hearsay.md)
│   ├── tale/                          (told directly by the user — /tell, see _index.md)
│   ├── discoveries/                   (stated directly by the user — /discover, see _index.md)
│   └── facts/                         (universal, NEVER sampled — facts.json + one .md per fact,
│                                       see _index.md; deliberately outside encodings.json)
├── _maps/
│   ├── npcs/registry.json             (master NPC data: name, skin, city, UUID, spawn position,
│   │                                   backstory, knowledge, criterion, life.lived)
│   ├── npcs/lifespans.json            (SECRET — each character's total span, kept out of the
│   │                                   registry so /enact never loads it; ask scripts/horizon.py)
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
    ├── update_uuids.py                (automates NPC UUID capture — see §5)
    ├── sample_lore_knowledge.py       (draws a character's education sample — §8 Step 1)
    ├── lineage_coin.py                (rolls traceable/untraceable when a hearsay claim is retold)
    ├── roll_lifespan.py               (rolls how many scenes a character has in them, 30–60 —
    │                                   written to lifespans.json, never to the registry)
    ├── horizon.py                     (the only thing /enact may ask about a life's horizon —
    │                                   answers early/established/late/final, never the number)
    └── notify_death.py                (on a character's death, computes their "circle" and
                                        mechanically samples 30% of it to notify immediately)
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

**Routine pause/resume** — every NPC, regardless of movement mode (including `NONE`), stops within 2 blocks of a player or when clicked, self-heals its skin (and path, if it has one) periodically, and resumes afterwards. Covered in full in §4.

**Fact** — one of the handful of things true of being a person in this world at all, living in `_lore/facts/`. Every character knows every fact in full; facts are never sampled, never attributed, and never contestable. Currently two: life ends, and everyone wants theirs to have been worthwhile. Together they're the will to live. See §0 Layer 1 and `_lore/facts/_index.md`.

**Criterion** — what a character counts as a life well spent, on their registry entry as `criterion`. Derived once at creation from the collision of their knowledge sample with their backstory, stated negatively (what they'd count as a *wasted* life) and anchored to one concrete, refutable case. It's what makes two characters with the same knowledge in the same situation choose differently. Owned by `/character` (Step 4 derives, Step 6 is the reference for how it changes).

**Trust (`criterion.trusts`/`distrusts`)** — a criterion also implies an epistemology, since what you think a life is *for* shapes what you'd trust to tell you how to live it. Derived from the anchor's own pool category: a life built on `hearsay` leans toward testimony and finds chronicles bloodless, one built on `era_libro`/`era_ensayo` leans the other way, one built on a `conflict` distrusts anyone who sounds certain. This makes a claim's credibility **subjective to the character** — it modulates whether they can dismiss a refuting claim (`/character` Step 6, move 1), so a weak claim from a trusted kind of source can land where a well-sourced one from a distrusted kind gets waved off. Facts are exempt: nothing about a character's epistemology touches them.

**Shock and drift** — the only two ways a criterion moves. A *shock* is a claim or lived experience that **references the criterion's anchor** (a pointer check, never a judgment about how upsetting something was), resolving to one of three moves: reject the claim, accept and reinterpret, or accept and break. *Drift* — accrued cost plus a shortening horizon — never changes a criterion by itself; it changes how susceptible the character is when a shock does arrive. Applied by `/enact` Step 5b.

**Lifespan** — how many scenes a character has in them, rolled once by `scripts/roll_lifespan.py` (default range 30–60) and **structurally hidden from them**: the span lives in `_maps/npcs/lifespans.json`, *not* on the registry entry, because the registry entry is what `/enact` loads in order to play the character. An enactment asks `scripts/horizon.py` instead, which answers with a coarse band — `early`, `established`, `late`, `final` — and never the number. Only `life.lived` (their history, no secret) stays on the registry entry. A `final` band means this scene is their last; afterwards `life.deceased` is set `true` and they're never enacted again.

**Death and its circle** — a character's death isn't announced to the world, it propagates in two tiers. `scripts/notify_death.py` computes their *circle* (everyone they've shared a recorded scene with, plus everyone named in their own backstory) and mechanically notifies 30% of it immediately — a forced `knowledge.experience` entry, no attribution needed. Anyone notified whose `criterion.anchor` referenced the deceased gets that resolved as a shock, same reject/reinterpret/break machinery as any other (`/enact` Step 5b point 6). Everyone outside the circle only finds out the ordinary way: the death is recorded as a `_lore/discoveries/` entry (see `/discover`), which re-enters the normal sampling pool at ordinary odds, or they hear it from someone in the circle later, subject to the same `lineage_coin.py` traceable/untraceable rule as any retelling.

**Three mutability classes.** Worth holding onto, since they're easy to conflate: `knowledge.education` is **frozen** at creation, `knowledge.experience` **appends freely** every scene, and `criterion` is **sticky-but-revisable** — it changes only when a referencing shock lands on a susceptible character, and the default outcome of any given scene is no change at all.

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

## 4. Routine pause/resume (every NPC)

Every NPC needs two more files, regardless of movement mode — including a stationary `NONE` NPC. This used to be scoped to "roaming NPCs only," which was wrong: the skin self-heal race (Taterzens fetches skins asynchronously from mineskin.org, and the fetch can lose the race against anything else touching the NPC) applies just as much to a `NONE` NPC as a roaming one, and confirmed the hard way — Khaoe shipped without this machinery first, under the old rule, and her skin never healed after a failed fetch. For a `NONE` NPC, `resume_routine.mcfunction`'s movement line is just `npc edit movement NONE` again (a no-op on behavior) — it's the tag cleanup and the periodic heal calls that actually matter there.

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

### Gesture `CustomModelData` values

Moved to `GESTURES.md` — the full table (each gesture's `CustomModelData` value, its `.mcfunction`,
pose description, and pairing caveats) lives there, next to the mechanics it depends on. For
matching a gesture to a dialogue line's emotional content, use the keyword table in
`.claude/skills/bake_dialog/SKILL.md`.

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
/npc edit pose <EntityPose name>            set pose (e.g. STANDING, SITTING) - persisted as TaterzenNPCTag.Pose,
                                             readable from a command via "if data entity <selector> {TaterzenNPCTag:{Pose:"<NAME>"}}"
/npc edit commands add minecraft <command>  add a right-click action
/npc edit commands setPermissionLevel <0-4> set execution authority for right-click actions
/blabber dialogue start <id> <target> [interlocutor]   start a dialog
```

---

## 7. Where design decisions live

This README documents *how the pack works*. Story content, NPC personalities, routes, and dialog writing are design decisions — they live in `_lore/` and the maps under `_maps/`, not in this file.

---

## 8. Writing a dialog through enactment

One way to write a Blabber dialog: play the NPC in a live conversation first, then convert the transcript. This is how `sonoros_lost_traveler.json` was written. Steps below are the manual version — the `/enact` skill (`.claude/skills/enact/SKILL.md`) runs this whole procedure, including the setup questions, the two-interlocutor branching (player vs. another enacted character), registration, and — as its final step — the `/bake_dialog` skill (`.claude/skills/bake_dialog/SKILL.md`), which replaces a minority of the dialog's default `nod_up_down` states with an emotionally-matched gesture from the vocabulary in `GESTURES.md`. `/bake_dialog` also runs standalone on any existing dialog file, not only right after an enactment — useful for the older dialogs still waiting on this pass (see `TODO.md`). `/enact` (plus its `bake_dialog` step) is the recommended way to do all of this now; the steps below are still worth knowing, since the skills just automate them.

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

# Luminacion

Luminacion is the NPC storytelling system for **Milkantis** (a 12-year-old Minecraft world). NPCs are Taterzens that react to player right-clicks, run Blabber dialogs, and follow their own routines (paths, wandering, etc.) — pausing to talk, then picking their routine back up.

This document is a practical, step-by-step guide to building things with the pack. It assumes you already know *what* NPC or story you want to add — this is about *how* to wire it up.

- Minecraft 1.20.1, datapack pack format 15
- Namespace: `luminacion`
- Requires: [Taterzens](https://modrinth.com/mod/taterzens) 1.11.7, [Blabber](https://modrinth.com/mod/blabber) 1.6.2

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
│       │       ├── _template/         (copy these into a new folder per NPC)
│       │       │   ├── spawn.mcfunction
│       │       │   ├── resume_routine.mcfunction
│       │       │   ├── check_proximity.mcfunction
│       │       │   └── end_with_gift.mcfunction
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
└── scripts/
    └── update_uuids.py                (automates NPC UUID capture — see §5)
```

Anything named `_template` is a pattern to copy and fill in. Anything named `_shared` is called directly and never duplicated.

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
    "sample": { "percent": null, "mode": "", "topic": null, "items": [] },
    "surfaced_in_dialog": []
  }
}
```

Leave `taterzen_uuid` empty for now — that's filled in automatically at the end (§5). `backstory` and
`knowledge` are optional for a hand-built NPC like this one — they exist for enacted characters (§8)
and are always filled in by the `/enact` skill.

### Step 2 — Create the spawn function

Copy `functions/npcs/_template/spawn.mcfunction` to `functions/npcs/maren/spawn.mcfunction`, then fill in every `<placeholder>` using the registry entry from Step 1. This file sets: identity, skin, movement mode, permission level, and right-click actions.

Read the comments in the template as you go — they explain each section. In particular:

- **Movement**: pick `NONE` (stationary) or one of `FORCED_LOOK` / `PATH` / `FORCED_PATH` / `FOLLOW` / `FREE` (roaming). If it's not `NONE`, you'll need §4 as well.
- **Right-click actions**: the first line should always be `npc edit commands add function luminacion:npcs/_shared/enter_dialog` when a dialog is involved — it pauses the NPC and marks it mid-conversation before the dialog opens. Don't skip it, even for stationary NPCs — it costs nothing and keeps every NPC consistent.

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

1. Copy `functions/npcs/_template/resume_routine.mcfunction` → `functions/npcs/<npc_key>/resume_routine.mcfunction`. Fill in `<MODE>` to match the movement mode you set in spawn.mcfunction (for `FOLLOW`, use the `FOLLOW <name>` / `FOLLOW UUID <uuid>` form shown in the comments).

2. Copy `functions/npcs/_template/check_proximity.mcfunction` → `functions/npcs/<npc_key>/check_proximity.mcfunction`. Fill in `<display_name>` and `<npc_key>`.

3. Add that file's path to the `"values"` array in `data/luminacion/tags/functions/npc_routine_tick.json`:

   ```json
   { "values": ["luminacion:npcs/maren/check_proximity"] }
   ```

That's it. From then on, the tick loop stops the NPC the moment a player gets within 2 blocks (or clicks it), and resumes its route once the player walks away or the dialog ends.

**Why both a click-pause and a proximity-pause?** So the NPC doesn't keep wandering off mid-approach before the player gets a chance to click it — it settles as soon as someone's nearby, not only once they've already interacted.

**Why the tick check also handles resuming, not just the dialog ending?** Blabber does not run its end-of-dialog action if a player exits early (Escape key, disconnect, etc.) — so a "resume when the dialog action fires" rule alone can leave an NPC stuck paused forever. The tick check is the safety net: it resumes any paused NPC the moment no player is within 2 blocks, regardless of how the conversation ended.

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
/npc edit commands add <command>            add a right-click action
/npc edit commands setPermissionLevel <0-4> set execution authority for right-click actions
/blabber dialogue start <id> <target> [interlocutor]   start a dialog
```

---

## 7. Where design decisions live

This README documents *how the pack works*. Story content, NPC personalities, routes, and dialog writing are design decisions — they live in `_lore/` and the maps under `_maps/`, not in this file.

---

## 8. Writing a dialog through enactment

One way to write a Blabber dialog: play the NPC in a live conversation first, then convert the transcript. This is how `sonoros_lost_traveler.json` was written. Steps below are the manual version — the `/enact` skill (`.claude/skills/enact/SKILL.md`) runs this whole procedure, including the setup questions, the two-interlocutor branching (player vs. another enacted character), and registration, and is the recommended way to do this now. The steps below are still worth knowing, since the skill just automates them.

### Step 1 — Bound the character's knowledge

Before playing the NPC, decide what slice of `_lore/analysis/` (`context.md`, `encodings.json`, `unknown.md`) they actually know. Don't hand-pick a flattering or convenient subset — flatten every atomic fact across the analysis (locations, concepts, characters, routes, era entries, conflicts...) into one pool and randomly sample a small percentage of it. 5% produced a character who was coherent but genuinely, unevenly gapped — knowledgeable about a handful of unrelated things, ignorant of most everything else — which is a far more natural starting point than a hand-curated backstory. Keep the sample somewhere referenceable for the length of the session, since you'll be checking answers against it constantly.

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

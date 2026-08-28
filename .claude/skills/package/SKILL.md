---
description: Package the current datapack (data/ + pack.mcmeta) and resource pack (resourcepack/) into two standalone zips for dropping into a different world/server, stripped of every dev-only folder (_lore/, _npcs/, scripts/, docs) and the placeholder dialogue templates. Use when shipping the pack somewhere other than this repo's own junctioned dev environment (e.g. a server, or a different Minecraft world).
disable-model-invocation: true
---

Produces two release zips from the current state of this repo — nothing here is a dev
convenience the destination world needs, only what Minecraft actually loads. This is
the "ship it" counterpart to the dev setup that keeps `resourcepack/` junctioned into
`resourcepacks/luminacion/` for local editing: that junction is for editing gestures live in *this*
world; this skill is for handing the finished pack to a *different* world or server that has no such
junction.

## Step 0 — Resolve the destination

Ask (AskUserQuestion) where to write the two zips. Default suggestion: the Desktop
(`$env:USERPROFILE\Desktop` on this machine). Accept any other absolute path the user
gives instead.

## Step 1 — Run the packaging script

```
py scripts/minecraft/package.py "<destination>"
```

This writes/overwrites (never timestamps — re-running always replaces the previous
export at that destination):

- `Provenance.zip` — the datapack: `pack.mcmeta` + `data/`, excluding the three
  `_template_*.json` dialogue placeholders (`_template_one_off.json`,
  `_template_linear.json`, `_template_branching.json` — unfilled `<placeholder>` text,
  authoring scaffolding only).
- `Provenance-resourcepack.zip` — the resource pack: `resourcepack/pack.mcmeta` +
  `resourcepack/assets/`.

Both zips are flat at the root — `pack.mcmeta` sits at the top level of the zip, not
inside a subfolder — which is what lets Minecraft recognize them as a datapack/resource
pack whether they're dropped in zipped or unzipped into a folder first.

`_lore/`, `_npcs/`, `scripts/`, `.claude/`, `.venv/`, `.git/`,
`README.md`, and `TODO.md` are never part of either zip — the script only ever reads
from `data/`, `pack.mcmeta`, and `resourcepack/`.

## Step 2 — Report and remind

Report the two output paths and sizes (the script prints both). Remind the user:

- Datapack: `<world>/datapacks/Provenance.zip` (server or singleplayer world save),
  then `/reload` or restart to load it.
- Resource pack: `resourcepacks/Provenance-resourcepack.zip` in the client's `.minecraft`
  folder (or the world's per-world resource pack mechanism), enabled via
  Options → Resource Packs.
- The destination world/server needs [Taterzens](https://modrinth.com/mod/taterzens)
  1.11.7 and [Blabber](https://modrinth.com/mod/blabber) 1.6.2 installed — the datapack
  won't function without both.
- Both packs are `pack_format` 15 (Minecraft 1.20.1) — a different game version on the
  destination server needs that checked before it'll load without a format warning.

## What this skill never does

- Never edits anything in this repo — it only reads `data/`/`pack.mcmeta`/
  `resourcepack/` and writes to the chosen destination.
- Never includes `_lore/`, `_npcs/`, `scripts/`, `.claude/`, or the docs
  in either zip.
- Never includes the three `_template_*.json` dialogue placeholders in the datapack
  zip.
- Never timestamps or versions the output — always the same two filenames, overwritten.

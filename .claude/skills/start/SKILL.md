---
description: Show the welcome banner for a new session or a new user of this repo - a live count of what's already in this copy of the world, plus the two doors in (growing the record vs. putting it in motion) each pointing at the skill that owns it. Use when the user opens a fresh checkout/worktree and asks how to get started, what the entry points are, or literally runs /start.
disable-model-invocation: false
---

Purely a display skill: it never writes anything, never asks a question, and touches no file under
`_lore/`, `_npcs/`, or `data/`. Its only job is to run the one script that owns all the mechanical
work - counting what's in the world and aligning the banner - and print that output back verbatim.

## Step 1 — Run the banner script

```bash
py scripts/lore/print_start_banner.py
```

All counting (characters, tales, hearsay claims, open conflicts, material sources) and all
box-drawing/padding happens inside that script, not here - the same "let a script own anything
mechanical" discipline as every other `scripts/lore/` tool in this pack. Never hand-recompute or
hand-align a version of this banner from memory; if the script's wording ever needs to change, edit
`scripts/lore/print_start_banner.py` itself, not this file.

## Step 2 — Print it back verbatim

Paste the script's stdout into the reply inside a fenced code block (so the box-drawing characters
stay aligned in a monospace font), with nothing else inside that fence. A short line of your own
prose before or after the block is fine (e.g. pointing at README.md for the full picture, or asking
what the user wants to start with) - the block itself must stay exactly what the script printed.

## Step 3 — Offer, don't decide

Don't pick a door for the user and don't start walking through one unprompted. The banner's whole
point is to lay out the options and then wait - the same "nothing gets decided silently" rule as
everywhere else in this pack (`.claude/PRINCIPLES.md`). If the user then names a door (a character to
create, material to integrate, a scene to enact), hand off to that door's own skill normally.

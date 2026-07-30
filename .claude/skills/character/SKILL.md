---
description: Create or update a character's entry in _maps/npcs/registry.json — backstory, location, and knowledge — without running a full /enact conversation. Use when the user wants to flesh out a character's sheet on its own, ahead of (or instead of) enacting a dialog.
disable-model-invocation: true
---

Lighter-weight sibling of `/enact` Step 1/Step 6: this skill only maintains a character's entry in
`_maps/npcs/registry.json`. It never touches `_maps/dialogs/registry.json` or writes a dialog file —
if the user wants an actual conversation, point them at `/enact` instead once the sheet is in good
shape.

## Step 1 — Name

Ask for the character's name. Look it up (case-insensitively, lowercased key) in
`_maps/npcs/registry.json`.

## Step 2a — Existing entry

If the key exists, show the user its current non-blank fields (`display_name`, `city`, `backstory`,
`knowledge.education` summary if populated, `knowledge.experience` count) as context, then ask, as
plain conversation, what needs to be updated. Don't presuppose which fields — the user might want to
amend the backstory, add/change the city, draw or redo their knowledge, or just fix a typo.

- **Backstory** — if the user is adding to an existing non-empty backstory, append/amend rather than
  replace, same as `/enact` Step 6. If they're giving it fresh, just set it.
- **City** — set directly from what the user says.
- **Knowledge** — if `knowledge.education.percent` is already set (non-null), never redraw it; that
  field is fixed for life. Only offer to draw it if it's still the blank `_template` shape
  (`percent: null`) — follow the sampling flow in Step 3 below. `knowledge.experience` only grows
  through actually living a scene (`/enact`), so don't hand-invent entries for it here.

## Step 2b — New entry

If the key doesn't exist, this is a brand-new character. Ask, as plain conversation (not
multiple-choice):

1. **Backstory** — optional.
2. **Location** — optional, fills `city`.
3. **Knowledge** — how much of the lore they know. Follow the sampling flow in Step 3.

## Step 3 — Knowledge sampling (shared)

Only runs when education knowledge is being drawn for the first time (new entry, or an existing entry
whose `knowledge.education` is still blank):

- Ask for a **percentage** (open number, e.g. "5", "11", "21").
- Ask (AskUserQuestion, two options) whether the draw is **random** or **skewed toward a topic**.
- If skewed, ask for the topic/keyword(s).
- Run:
  ```bash
  python scripts/sample_lore_knowledge.py --percent <N> --mode random
  # or
  python scripts/sample_lore_knowledge.py --percent <N> --mode skewed --topic "<keyword>" --topic "<keyword2>"
  ```
- Keep the printed list — it goes into `knowledge.education.items` in Step 4. Don't reveal the full
  list to the user unprompted; you may describe its general shape.

## Step 4 — Write the registry entry

Update (or create) the character's entry in `_maps/npcs/registry.json`, key = lowercased name:

- `display_name`, `taterzen_name` — the name, if not already set.
- `city` — from Step 2, if given.
- `backstory` — from Step 2, appended/amended per the rule above.
- `knowledge.education` — `{percent, mode, topic, items}` exactly as drawn in Step 3, only if this was
  a fresh draw. Otherwise leave untouched.
- `skin`, `taterzen_uuid`, `spawn_position` — leave blank/null. Not this skill's job.

Validate the file still parses as JSON before finishing.

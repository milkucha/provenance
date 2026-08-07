---
description: Surface one open item — a conflicts-array disagreement from _lore/encodings.json, or an open question from _lore/unknowns.md — for the user to resolve, with full context and every place elsewhere in the record that mentions it, so nothing gets missed. Writes a resolution only on the user's own explicit call, never suggested or inferred. Use when the user wants to resolve/settle/decide a conflict or unknown, review what's still open, or asks what conflicts are unresolved.
disable-model-invocation: true
---

Works through `encodings.json`'s `conflicts` array or `_lore/unknowns.md` one item at a time. Per
`.claude/PRINCIPLES.md`: never suggest a resolution, never infer one from majority-source-agreement or
recency, and never resolve more than the one item the user is actively looking at right now. Skipping
an item — not ready to decide — is a first-class, no-op-safe choice, not a failure to push through.

## Step 1 — Pick a source and an item

If the user already named a specific id or described a specific question, skip straight to Step 2 for
that one. Otherwise ask (AskUserQuestion): **conflicts** or **unknowns**?

- **Conflicts:** run `py scripts/lore/resolve_conflict.py --list` — every id, OPEN/RESOLVED status,
  and topic. Ask the user which OPEN one they want to look at (or offer the first few if the list is
  long; don't dump all 18 and expect them to scan unprompted).
- **Unknowns:** run `py scripts/lore/list_open_unknowns.py` — every still-open section heading with its
  line number. Same offer-a-few, don't-dump-everything approach. A heading not saying
  "Resolved"/"Correction" is a candidate, not a guarantee — some are genuine gaps the material simply
  never addresses, not decisions the user can actually make (see the script's own closing note). Use
  judgement about which are worth putting to the user versus flagging as "this isn't really
  resolvable, it's just a gap" and moving on.

## Step 2 — Show the full picture

- **Conflict:** run `py scripts/lore/resolve_conflict.py <CONFLICT-ID>` — prints the topic, full
  `detail`, current `user_resolution` (if any), and every other place in `encodings.json` and
  `_lore/unknowns.md` that mentions this id. Present all of it; don't trim for length.
- **Unknown:** read the section in full (`_lore/unknowns.md`, the line number `list_open_unknowns.py`
  reported). If it names a `CONFLICT-NN`, also run `resolve_conflict.py` on that id — an unknown and a
  conflict can be two views of the same underlying disagreement, and the user should see both.

## Step 3 — Ask, plainly

Put the actual question to the user in plain conversation — what does the record show, what's
unresolved about it, what would settling it mean. Do not propose an answer, do not lead with "it's
probably X because most sources agree." If the user isn't ready, that's the end of this item: change
nothing, say so, move on (Step 5).

## Step 4 — Record the decision

- **Conflict:** `py scripts/lore/resolve_conflict.py <CONFLICT-ID> --set-resolution "<the user's
  decision, in their words or a faithful paraphrase>"`. The script refuses to overwrite an existing
  `user_resolution` unless `--force` is passed — only pass it if the user explicitly wants to amend a
  prior decision, never to push through a "already has an answer" refusal by assumption. It appends
  `(per user, <date>)` automatically if the text doesn't already carry that framing, matching every
  existing entry's style — don't hand-write the date yourself.
- **Unknown:** append the decision as a new bullet under a `## Resolved by the user (<today>)` section
  — reuse today's section if one was already created earlier in this run, otherwise add a new one,
  matching the file's own established convention exactly (see the existing 2026-07-24 section: a short
  bold label, then the resolution in a sentence or two, `(per user, <date>)` at the end). Then, in the
  original section this question came from, add one short line at the top — "**Resolved (see 'Resolved
  by the user (<date>)' above).**" — without deleting or rewriting anything else in that section: the
  underlying documentary content (what the material actually says) stays on record even once the open
  question about it is settled, exactly as the file's own preamble describes for conflicts.
  `_lore/unknowns.md` has no script for this — it's markdown prose, and the exact wording of both the
  new bullet and the pointer is a judgement call each time, not a mechanical transform.

## Step 5 — One at a time

After recording (or skipping) one item, stop. Ask (AskUserQuestion: resolve another / stop) rather
than looping through the rest of the backlog unprompted — the user came here to make specific
decisions, not to be walked through all eighteen conflicts in one sitting unless they say so.

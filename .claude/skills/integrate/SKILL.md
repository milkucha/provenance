---
description: Integrate newly-added _lore/material/ into the analysis (_lore/material/_context.md, _lore/encodings.json, _lore/unknowns.md), audit that every dialogue has a matching hearsay entry, check for drift between what's referenced elsewhere in the pack and what's actually recorded in encodings.json — including that every _lore/tales/ file has a matching manifest entry — and audit _lore/unknowns.md for entries the rest of the project has since answered. Use when new material has been uploaded to _lore/material/, or for a periodic consistency pass over the lore analysis.
disable-model-invocation: true
---

Four independent passes — run whichever the situation calls for, not necessarily all four. If it's
not obvious from how the skill was invoked, ask (AskUserQuestion): new material just added → Pass 1;
"did we miss a hearsay entry" / periodic audit → Pass 2; "check the encodings are still accurate" →
Pass 3; "check unknowns.md is still current" → Pass 4. Default to running all four when unsure — a
pass with nothing to do is cheap to finish quickly.

Nothing here silently resolves a judgment call. Every place the existing analysis files (`_context.md`,
`encodings.json`, `unknowns.md`) already draw a line between "recorded fact" and "open question" (see
README §0 Layer 1), this skill holds that same line — new material can add entries and flag conflicts,
never overwrite an existing entry or invent a resolution.

## Pass 1 — Analyse new material

**Trigger:** one or more files in `_lore/material/` aren't reflected yet in `_lore/material/_context.md`
(diff the material folder's contents against that file's section headers to find them).

1. For each new/unanalysed file, add a section to `_context.md`, following the method note at the top
   of that file exactly: treat the source as an independently recovered artifact; transcribe only
   what it actually says or shows; preserve the source's own blanks/open questions as gaps rather
   than filling them in; note (don't resolve) any disagreement with other sources.
2. Fold the transcribed material into `encodings.json`'s objective arrays (`time_systems`,
   `locations`, `routes`, `characters`, `concepts`) in the same shape as their existing entries.
   Never edit or remove an existing entry to make room for a new one. If the new material disagrees
   with something already encoded, add a `conflicts` entry instead — next `CONFLICT-NN` id, `topic`,
   `detail` — and leave `user_resolution` unset. That field is set by the user only; every current
   entry that has one records it as "(per user, <date>)" — never fill it in on this skill's own
   judgment.
3. Log anything the new material poses as a question but doesn't answer in `unknowns.md`, matching the
   shape of its existing entries (cross-reference a `CONFLICT-##` id when it's a disagreement between
   sources; otherwise it's a standalone gap).
4. Report a short summary back to the user: what was added, how many new entries per array, how many
   new conflicts (if any) and what they're about, how many new open questions. Flag every new
   conflict explicitly — don't bury one in a large diff.

## Pass 2 — Hearsay coverage audit

**Trigger:** on request, or as a periodic check even when Pass 1 found nothing — a hand-written
dialogue (not produced via `/enact`) can skip README §8 Step 5 entirely without anyone noticing.

1. List every non-template file in `data/luminacion/blabber/dialogues/` (exclude `_template_*.json`).
2. Cross-check each against `encodings.json`'s `hearsay.entries` array (`source_file` field) and
   `_lore/characters/hearsay.md`. Both are meant to mirror each other exactly (see
   `hearsay._method_note` in `encodings.json`) — a dialogue needs a matching entry in *both*.
3. For any dialogue missing coverage, build the entry per README §8 Step 5: `participants`,
   `location`, `summary`, and a `claims` list phrased as reported assertions (not restated as fact),
   each with an `about` reference into the objective arrays (or a bare era/`CONFLICT-##` name). Check
   each claim against the record and add `inconsistent_with_record` (array of `{about, source_kind,
   note}`, `source_kind` one of `material`/`tale`) or `inconsistent_with_facts` (a short
   string) only when a genuine contradiction is found — leave both unset in the ordinary case, since
   absence already means "no contradiction found" and recording that explicitly on every claim would
   just be noise. Read the dialogue's actual `text`/`choices[].text` fields to extract claims — don't
   invent ones that weren't actually said. Set `derived_from`/`oral_lore` only where the dialogue's own
   content makes the lineage clear (a line citing a named source, or vague "they say..." framing); when
   it's genuinely ambiguous, leave both unset rather than guess. If a claim raises a genuine question
   the objective record has never addressed at all (not a contradiction — a gap) and it resonates with
   the existing corpus, log it in `_lore/unknowns.md`, cross-referencing the claim's id, matching the
   file's existing shape. Not every claim produces one; skip rather than manufacturing a question that
   isn't genuinely there.
4. If the two copies of an existing entry (the JSON array vs. `hearsay.md`) have drifted apart,
   reconcile them — but flag the discrepancy to the user rather than silently picking one side when
   it's not obvious which is current.
5. Report which dialogues were missing coverage and what was added, plus any reconciled drift.

## Pass 3 — Encodings drift check

**Trigger:** on request, or periodically alongside Pass 2.

1. **Tale coverage.** List every file in `_lore/tales/` (excluding `_index.md` and `_authors.md`).
   Cross-check it against `encodings.json`'s `tales.entries` array (`source_file` field), against
   `_lore/tales/_authors.md`'s table, and against `_lore/tales/_index.md`'s table — all three are
   meant to carry a row for every tale, the same "both copies must mirror" discipline Pass 2 already
   applies to hearsay, just three-wide instead of two. For any tale file missing a manifest entry,
   build one per `/tell` Step 4: `id`/`source_file` from the filename, `told_by`/`told_date` from the
   tale file's own `**Told by:**`/`**Told on:**` header lines, and `touches` transcribed from that
   file's own "Where this lands in the record" section — never re-derive `touches` by re-reading the
   tale's prose from scratch, since that was already a judgment call made once when the tale was
   written (`/tell` Step 5). If that section is still placeholder text, leave `touches: []` and flag
   the tale as never having been folded into the other categories at all — that means Step 5 was
   skipped, not just Step 4. Build any missing `_authors.md`/`_index.md` row the same transcribing way.
   Never invent a `told_by`/`Responsible` value that isn't already written in the tale file.
2. Walk every `_lore/characters/*.json` file's `knowledge.education.items` and
   `knowledge.experience` (skip `_template.json`), plus every `hearsay.entries[].claims[].about`
   reference in `encodings.json`. Confirm every `about` id that isn't `null` or a bare era/
   `CONFLICT-##` name resolves to a real entry somewhere in `locations`/`characters`/`concepts`/etc.
3. Walk every `tales.entries[].touches` array. Confirm each id listed actually exists where it claims
   to (an added/amended entry in `locations`/`characters`/`concepts`/`routes`/`time_systems`, or a
   `CONFLICT-##` id in `conflicts`), and that the referenced entry actually carries the matching
   `tale:<id>` source tag. Flag either direction of drift: a `touches` id that doesn't resolve, or a
   `tale:` source tag in the objective arrays with no corresponding id in that tale's own `touches`
   list.
4. Cross-check `_npcs/dialogs/registry.json` against `data/luminacion/blabber/dialogues/`: flag any
   registered dialog id with no matching file, and any dialogue file with no registry entry (the
   latter is expected for a few in-flight two-NPC scenes still open in `TODO.md` — check there before
   flagging one as a bug).
5. Report every dangling reference found, with enough detail (file, field, the id in question) that
   the user can decide the fix. Never auto-repair a dangling `about`/`touches` reference by guessing
   the intended target — a wrong guess corrupts the provenance the hearsay/encodings system depends
   on; surface it instead. (Step 1's tale-coverage builds are the one exception — those transcribe
   data the tale file already states outright, the same way Pass 2 builds a missing hearsay entry
   straight from a dialogue's own text; nothing there is guessed.)

## Pass 4 — Unknowns staleness audit

**Trigger:** on request, or periodically alongside Passes 2–3.

1. Read every entry in `_lore/unknowns.md`. Note what each one is actually asking, and any id it
   already cross-references (a `CONFLICT-##`, a hearsay claim id, a tale id, a material section).
2. Check whether the rest of the project has since answered it:
   - A cross-referenced `CONFLICT-##` now carrying `user_resolution` in `encodings.json` — but confirm
     the resolution text actually settles the *question the unknown asks*, not just that the conflict
     entry got touched at all; a conflict can be resolved on one axis while the unknown it spawned
     stays open on another.
   - A newer entry in `encodings.json`'s objective arrays, a `_lore/tales/` file, or
     `_lore/characters/hearsay.md` that names the same subject and states something that reads as a
     direct answer, even when nothing formally links it back to the unknowns entry.
3. For every entry that looks answered, flag it to the user with the answering source (file/id) —
   never remove or edit an `_lore/unknowns.md` entry on this skill's own judgment. Whether an apparent
   answer is conclusive enough to actually close the question is the user's call, the same discipline
   `conflicts.user_resolution` already gets.
4. Report: which entries look answered (with source), and how many remain genuinely open — a count is
   enough for the still-open ones, don't enumerate every one of them.

## What this skill never does

- Never sets a `conflicts` entry's `user_resolution` — that's the user's call alone, every time.
- Never edits `_lore/material/` — source files are read-only, excavated artifacts.
- Never invents lore to close a gap in `unknowns.md` — a gap stays a gap until the user resolves it.
- Never fabricates a hearsay claim that wasn't actually said in the dialogue it's covering.
- Never closes or edits an `_lore/unknowns.md` entry on its own judgment — Pass 4 only flags
  candidates for the user to confirm.
- Never rebuilds a tale's `touches` list by re-reading its prose from scratch — only transcribes what
  the tale file's own "Where this lands in the record" section already states.

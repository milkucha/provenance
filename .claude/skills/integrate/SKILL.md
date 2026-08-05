---
description: Integrate newly-added _lore/material/ into the analysis (_lore/material/_context.md, _lore/encodings.json, _lore/unknown.md), audit that every dialogue has a matching hearsay entry, and check for drift between what's referenced elsewhere in the pack and what's actually recorded in encodings.json. Use when new material has been uploaded to _lore/material/, or for a periodic consistency pass over the lore analysis.
disable-model-invocation: true
---

Three independent passes — run whichever the situation calls for, not necessarily all three. If it's
not obvious from how the skill was invoked, ask (AskUserQuestion): new material just added → Pass 1;
"did we miss a hearsay entry" / periodic audit → Pass 2; "check the encodings are still accurate" →
Pass 3. Default to running all three when unsure — a pass with nothing to do is cheap to finish
quickly.

Nothing here silently resolves a judgment call. Every place the existing analysis files (`_context.md`,
`encodings.json`, `unknown.md`) already draw a line between "recorded fact" and "open question" (see
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
3. Log anything the new material poses as a question but doesn't answer in `unknown.md`, matching the
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
   the existing corpus, log it in `_lore/unknown.md`, cross-referencing the claim's id, matching the
   file's existing shape. Not every claim produces one; skip rather than manufacturing a question that
   isn't genuinely there.
4. If the two copies of an existing entry (the JSON array vs. `hearsay.md`) have drifted apart,
   reconcile them — but flag the discrepancy to the user rather than silently picking one side when
   it's not obvious which is current.
5. Report which dialogues were missing coverage and what was added, plus any reconciled drift.

## Pass 3 — Encodings drift check

**Trigger:** on request, or periodically alongside Pass 2.

1. Walk every `_lore/characters/*.json` file's `knowledge.education.items` and
   `knowledge.experience` (skip `_template.json`), plus every `hearsay.entries[].claims[].about`
   reference in `encodings.json`. Confirm every `about` id that isn't `null` or a bare era/
   `CONFLICT-##` name resolves to a real entry somewhere in `locations`/`characters`/`concepts`/etc.
2. Walk every `tales.entries[].touches` array. Confirm each id listed actually exists where it claims
   to (an added/amended entry in `locations`/`characters`/`concepts`/`routes`/`time_systems`, or a
   `CONFLICT-##` id in `conflicts`), and that the referenced entry actually carries the matching
   `tale:<id>` source tag. Flag either direction of drift: a `touches` id that doesn't resolve, or a
   `tale:` source tag in the objective arrays with no corresponding id in that tale's own `touches`
   list.
3. Cross-check `_npcs/dialogs/registry.json` against `data/luminacion/blabber/dialogues/`: flag any
   registered dialog id with no matching file, and any dialogue file with no registry entry (the
   latter is expected for a few in-flight two-NPC scenes still open in `TODO.md` — check there before
   flagging one as a bug).
4. Report every dangling reference found, with enough detail (file, field, the id in question) that
   the user can decide the fix. Never auto-repair a dangling `about` reference by guessing the
   intended target — a wrong guess corrupts the provenance the hearsay/encodings system depends on;
   surface it instead.

## What this skill never does

- Never sets a `conflicts` entry's `user_resolution` — that's the user's call alone, every time.
- Never edits `_lore/material/` — source files are read-only, excavated artifacts.
- Never invents lore to close a gap in `unknown.md` — a gap stays a gap until the user resolves it.
- Never fabricates a hearsay claim that wasn't actually said in the dialogue it's covering.

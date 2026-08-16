---
description: Integrate newly-added _lore/material/ into the analysis (_lore/material/_context.md, _lore/encodings.json, _lore/unknowns.md), audit that every dialogue has a matching hearsay entry, check for drift between what's referenced elsewhere in the pack and what's actually recorded in encodings.json — including that every _lore/tales/ file has a matching manifest entry — and audit _lore/unknowns.md for entries the rest of the project has since answered. Use when new material has been uploaded to _lore/material/, or for a periodic consistency pass over the lore analysis.
disable-model-invocation: true
---

Four independent passes — run whichever the situation calls for, not necessarily all four. If it's
not obvious from how the skill was invoked, ask (AskUserQuestion): new material just added → Pass 1;
"did we miss a hearsay entry" / periodic audit → Pass 2; "check the encodings are still accurate" →
Pass 3; "check unknowns.md is still current" → Pass 4. Default to running all four when unsure — a
pass with nothing to do is cheap to finish quickly.

Per `.claude/PRINCIPLES.md`: every place the existing analysis files (`_context.md`, `encodings.json`,
`unknowns.md`) already draw a line between "recorded fact" and "open question," this skill holds that
same line — new material can add entries and flag conflicts, never overwrite an existing entry or
invent a resolution.

## Pass 1 — Analyse new material

**Trigger:** one or more files in `_lore/material/` aren't reflected yet in `_lore/material/_context.md`
(diff the material folder's contents against that file's section headers to find them).

**Cold start:** if `_lore/encodings.json`, `_lore/material/_context.md`, or `_lore/unknowns.md` doesn't
exist yet at all (a fresh project, not just fresh material), run `py scripts/lore/bootstrap_lore.py`
first — it creates whichever of the three is missing with empty, generic structure (an empty
`_categories` block, `conflicts: []`, `hearsay`/`tales` skeletons) and deliberately does NOT pre-create
any content category. This mirrors how the schema was actually built the first time: nothing was
seeded in advance, every category got proposed once real material called for it. Then continue into
step 1 below as normal — with `_categories` empty, essentially everything the first files introduce
will hit step 2's "doesn't fit any existing category" branch, which is expected, not a bug.

1. For each new/unanalysed file, add a section to `_context.md`, following the method note at the top
   of that file exactly: treat the source as an independently recovered artifact; transcribe only
   what it actually says or shows; preserve the source's own blanks/open questions as gaps rather
   than filling them in; note (don't resolve) any disagreement with other sources.
2. **Check whether the material's own structure fits an existing category before folding anything
   in.** The schema (`time_systems`, `locations`, `routes`, `characters`, `concepts`, `conflicts`,
   `hearsay`, `tales`, and whatever else `encodings.json`'s `_categories` block already lists — which
   may be nothing at all, on a freshly bootstrapped project) is not frozen — the original intent was
   for it to emerge from what the material actually contains, not force every source into fixed boxes
   forever. If an entry genuinely doesn't belong under any existing category (not "it's a slightly
   awkward fit," a real structural mismatch — e.g. material describing something like "alien cultures"
   with no analog in anything encoded so far, or literally any entry at all when `_categories` is
   still empty), ask (AskUserQuestion): *"This material introduces [novel structure]. Create a new
   category for it[, or does it belong under [closest existing category]]?"* — drop the second half of
   the question entirely when there's no existing category close enough to offer, rather than forcing
   a comparison that doesn't make sense yet. Only continue past this point once the user decides —
   never silently squeeze novel structure into an existing box, and never silently create a category
   either.
   - **If the user approves a new category:** add its data under a new top-level key in
     `encodings.json`, in whatever shape the material actually supports (most naturally a flat list of
     `{"id": ..., "names": [...], ...}` dicts — the same shape `locations`/`concepts` already use).
     Then register it in `_categories` (see that key's own `_categories_method_note` for the exact
     spec fields): `"shape": "list"` if it followed the flat-list convention above — nothing else
     needs to change, `scripts/lore/sample_lore_knowledge.py` picks it up automatically next run. If
     the material's own shape doesn't fit `"list"` (a nested grouping, something claim-like), say so
     explicitly to the user — that shape needs a new handler written into that script's
     `SHAPE_HANDLERS` by hand before the category can be sampled, and sampling will refuse to run
     until one exists rather than silently skip the category.
   - **No epistemology proposal needed anymore (2026-08-16).** `/character` Step 4d used to need a
     per-category `epistemology_group` classification here; it now derives trusts/distrusts per item
     from that item's own `sources[]` provenance instead (`scripts/lore/anchor_epistemology.py`), so a
     newly-registered category needs nothing beyond the `_categories` spec above — `has_sources: true`
     (the default for any category that carries a `sources` list, per point 3 below) is all Step 4d
     needs to work with it.
3. Fold the transcribed material into `encodings.json`'s objective arrays (`time_systems`,
   `locations`, `routes`, `characters`, `concepts`) in the same shape as their existing entries. For the
   four categories that carry a `sources` list (`locations`, `concepts`,
   `characters.in_world_or_legendary`, `characters.real_world_authors_and_players`), each entry is
   `{"category": "material", "origin": "<doc (detail)>"}` — the two-layer shape (what kind of source,
   then which specific one) that also carries `tale`/`hearsay` provenance once Pass 3's script runs (see
   Pass 3 step 2). Never edit or remove an existing entry to make room for a new one. If the new
   material disagrees with something already encoded, add a `conflicts` entry instead — next
   `CONFLICT-NN` id, `topic`, `detail` — and leave `user_resolution` unset. That field is set by the
   user only; every current entry that has one records it as "(per user, <date>)" — never fill it in on
   this skill's own judgment.
4. Log anything the new material poses as a question but doesn't answer in `unknowns.md`, matching the
   shape of its existing entries (cross-reference a `CONFLICT-##` id when it's a disagreement between
   sources; otherwise it's a standalone gap).
5. Report a short summary back to the user: what was added, how many new entries per array, how many
   new conflicts (if any) and what they're about, how many new open questions, and whether a new
   category was created (with its `_categories` spec). Flag every new conflict and every new category
   explicitly — don't bury either in a large diff.

## Pass 2 — Hearsay coverage audit

**Trigger:** on request, or as a periodic check even when Pass 1 found nothing — a hand-written
dialogue (not produced via `/enact`) can skip `/enact`'s Step 5 hearsay recording entirely without
anyone noticing.

1. List every non-template file in `data/luminacion/blabber/dialogues/` (exclude `_template_*.json`).
2. Cross-check each against `encodings.json`'s `hearsay.entries` array (`source_file` field) and
   `_lore/characters/hearsay.md`. Both are meant to mirror each other exactly (see
   `hearsay._method_note` in `encodings.json`) — a dialogue needs a matching entry in *both*.
3. For any dialogue missing coverage, build the entry in the same shape `/enact` Step 5 writes: `participants`,
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
2. **Run `py scripts/lore/build_source_index.py`** — mechanical, no judgment involved, so it costs no
   model reasoning to run. It (a) migrates any leftover flat-string `sources` entries into the
   two-layer `{category, origin}` shape, (b) links every `hearsay.entries[].claims[].about` and
   `tales.entries[].touches` reference that resolves — exactly, or within `difflib` similarity 0.77
   compared only within one category at a time (never a location against a character, for instance) —
   into the target node's `sources` list, and (c) prints what it could not resolve. A fuzzy link is
   never treated as settled fact: it also appends a new `CONFLICT-NN` entry ("possible same-entity
   spelling, auto-grouped (unconfirmed)") with `user_resolution` left unset, same as every other
   conflict — flag every one of these in this pass's report, same as a brand-new conflict from Pass 1.
3. **Everything the script reports as unresolved needs a human read, not a guess.** For each one,
   figure out which case it is: a genuinely new entity that was never folded into the objective arrays
   (needs a Pass-1-style entry), a spelling too different from anything existing to fuzzy-match (needs
   a manual `names[]`/`about` fix), or a reference into a category the script doesn't index yet
   (`routes`, `time_systems` eras, `characters.named_inhabitants` — `about`/`touches` values there are
   still checked by eye: confirm each resolves to a real entry, the same way this pass always has).
   Also confirm, for the `tale:<id>` provenance the script attaches, that the referenced entry actually
   carries it and the tale's own `touches` list agrees — flag either direction of drift.
4. Cross-check `_npcs/dialogs/registry.json` against `data/luminacion/blabber/dialogues/`: flag any
   registered dialog id with no matching file, and any dialogue file with no registry entry (the
   latter is expected for a few in-flight two-NPC scenes still open in `TODO.md` — check there before
   flagging one as a bug).
5. Report every dangling reference found (with enough detail — file, field, the id in question — that
   the user can decide the fix), plus every auto-grouped conflict from step 2. Never auto-repair a
   dangling `about`/`touches` reference by guessing beyond what the script's fuzzy step already does at
   its fixed, disclosed threshold — below 0.77 similarity, a guess is more likely to corrupt provenance
   than fix it, so it stays a human call. (Step 1's tale-coverage builds are the other exception — those
   transcribe data the tale file already states outright, the same way Pass 2 builds a missing hearsay
   entry straight from a dialogue's own text; nothing there is guessed.)

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

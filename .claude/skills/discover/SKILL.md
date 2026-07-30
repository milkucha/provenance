---
description: Record a discovery stated directly by the user - a fourth source of truth for Milkantis, processed like /tell's tales but as a plain statement of fact with its own credited (or explicitly uncredited) responsible party. Registers the discovery in its own file under _lore/discoveries/, adds a manifest entry to encodings.json's discoveries category, folds its content into other encodings categories where it overlaps, and logs any notable unresolved thread to unknown.md. Use when the user wants to record something that has been discovered/found out about the world.
disable-model-invocation: true
---

Read `_lore/discoveries/_index.md` first if it hasn't been read yet this session. A discovery is
processed exactly like a tale (`.claude/skills/tell/SKILL.md`) - told directly by the user, folded
into the objective record via a source tag, conflicts raised rather than silently resolved, nothing
ever overwritten - except for one addition: every discovery names who is responsible for it, or
explicitly names no one.

## Step 1 — Ask what they discovered

Ask, as plain conversation: **"What have you discovered?"** Let them state it fully before moving on -
don't impose structure while they're still stating it.

## Step 2 — Ask who is responsible

Ask directly: **"Who is responsible for this discovery?"** A name (character, person, institution) is
one valid answer. The user may also say it's simply something that is now known, with nobody
responsible - that is an equally valid, deliberate answer, not a gap to chase down. Record whichever
it is; never guess a name that wasn't given and never leave this ambiguous.

## Step 3 — Title and slug

Ask for a short title if one hasn't already come up naturally. Derive a `snake_case` slug (same
convention as `/tell` Step 2) - short, descriptive, unique against every existing file in
`_lore/discoveries/`.

## Step 4 — Write the discovery's own file

Create `_lore/discoveries/<slug>.md`:

```markdown
# <Title>

**Discovered by:** <name> — OR — no one; simply now known
**Discovered on:** <date>
**Encodings id:** `discoveries.entries[].id = "<slug>"`

## The discovery

<what was stated, transcribed close to verbatim - light editing for readability only>

## Where this lands in the record

- Touches: <ids added/amended elsewhere in encodings.json, or "none yet">
- Conflicts raised: <CONFLICT-NN id(s), or "none">
- Open questions logged: <unknown.md reference, or "none">
```

Leave "Where this lands" as placeholders until Steps 5-7 below are done.

## Step 5 — Add the manifest entry to `encodings.json`

Add to the `discoveries.entries` array (currently empty - this may be the first):

```json
{
  "id": "<slug>",
  "source_file": "_lore/discoveries/<slug>.md",
  "discovered_date": "<date>",
  "responsible": "<name>",
  "responsible_note": null,
  "summary": "<one or two sentences - what was actually stated, not editorializing>",
  "touches": []
}
```

If nobody is responsible, set `"responsible": null` and `"responsible_note": "known - no one
responsible"` instead - both fields exist so "no data yet" and "deliberately nobody" are never
confused with each other.

## Step 6 — Fold into the other categories

Identical procedure to `/tell` Step 5: read `locations`/`characters`/`concepts`/`routes`/
`time_systems` for thematic overlap. New entries get added in-shape with a `"discovery:<slug> (<short
note>)"` source tag; new detail on an existing entry gets appended, never overwriting; a genuine
disagreement gets a new `conflicts` entry (next `CONFLICT-NN`, `user_resolution` left unset). Record
every id touched in this entry's `touches` array and the file's own "Touches"/"Conflicts raised"
lines.

## Step 7 — Notable unknowns

Same rule as `/tell` Step 6: if the discovery raises a question it doesn't itself answer and that
resonates with the existing corpus, log it in `_lore/analysis/unknown.md`, cross-referencing this
discovery's id. Skip if nothing genuinely qualifies.

## Step 8 — Update the index and report back

Add a row to `_lore/discoveries/_index.md`'s table (discovered date, title, responsible, filename, a
short `touches` summary). Report back: what was recorded, who (if anyone) was credited, what it
touched or added, every new conflict raised, and any notable unknown logged.

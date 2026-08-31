---
description: Record a tale told directly by the user - a third source of truth for this world, alongside the excavated objective record (_lore/material/_context.md, _lore/encodings.json) and the in-fiction subjective record (_lore/characters/hearsay.md). Covers both a narrated story and a plain statement of fact now known. Registers the tale in its own file under _lore/tales/, adds a manifest entry to encodings.json's tales category, folds its content into other encodings categories where it overlaps, records real-world provenance in _lore/tales/_authors.md, and logs any notable unresolved thread to _lore/unknowns.md. Use when the user wants to tell a tale, or state something as now known, to add to the world's lore.
disable-model-invocation: true
---

**Cold start:** if `_lore/tales/_index.md` or `_lore/tales/_authors.md` doesn't exist yet at all (a
fresh project), run `py scripts/lore/bootstrap_lore.py` first - it writes both files with their
explanatory header and an empty table, ready for Step 4/7 below to append a row into. Without it,
there'd be no table header to append a row under on the very first tale.

Read `_lore/tales/_index.md` first if it hasn't been read yet this session - it states the rule this
skill exists to enforce: a tale is told directly by the user, outside any character's mouth and
outside any excavated document - narrated as a story or stated plainly as a fact, both the same
category - and unlike `hearsay` it **is** folded into the objective record, the same way a
newly-analysed `_lore/material/` file is per `.claude/skills/integrate/SKILL.md` Pass 1. Per
`.claude/PRINCIPLES.md`: a genuine disagreement with something already on record becomes a new
`conflicts` entry, never a silent overwrite, and `user_resolution` is never set by this skill.

## Step 1 — Ask what they want to tell

Ask, as plain conversation, not multiple-choice: **"What would you like to tell?"** Then let them
actually tell it - don't summarize preemptively, don't interrupt to impose structure, don't ask
clarifying questions mid-telling unless they stall and ask you to prompt them. Wait for a clear signal
the telling is over (they say so, or trail off with nothing more to add) before moving on. This works
whether what comes out is a narrated story or a short, plainly stated fact - don't push a flat
statement into narrative shape, and don't cut a real telling short because it turned out longer than a
one-liner.

## Step 1a — Ask about in-world credit

Ask directly: **"Is this credited to anyone or anything in-world, or is it just known?"** A name
(character, person, institution) is one valid answer; "nobody in particular," or the question simply
not applying, is equally valid - this is `told_by`, and it's optional. Don't force an answer or invent
one that wasn't given.

## Step 2 — Title and slug

Ask for a short title if one hasn't already come up naturally in the telling. Derive a `snake_case`
slug from it (matching the convention already used for dialogue filenames, e.g.
`character_l_lost_traveler`) - short, descriptive, unique against every existing file in `_lore/tales/`.

## Step 3 — Write the tale's own file

Create `_lore/tales/<slug>.md`:

```markdown
# <Title>

**Responsible:** <user's name/handle> - real-world provenance only, never an in-fiction detail
**Told by:** <in-world source, if the tale itself is framed as coming through one - a character, an
institution, a legend> - optional; omit this line entirely when there isn't one (the common case: most
tales are just told directly, with no in-world frame)
**Told on:** <date>
**Encodings id:** `tales.entries[].id = "<slug>"`

## The tale

<the telling, transcribed close to verbatim - light editing for readability only, never adding
content the user didn't actually say, never softening a genuine gap into an invented resolution>

## Where this lands in the record

- Touches: <ids added/amended elsewhere in encodings.json, or "none yet">
- Conflicts raised: <CONFLICT-NN id(s), or "none">
- Open questions logged: <unknowns.md reference, or "none">
```

Leave the "Where this lands" section as placeholders for now - fill it in after Steps 4-6 below, once
you actually know what happened.

## Step 4 — Add the manifest entry to `encodings.json`

Add to the `tales.entries` array (currently empty - this may be the first):

```json
{
  "id": "<slug>",
  "source_file": "_lore/tales/<slug>.md",
  "told_date": "<date>",
  "told_by": <in-world source as a string, or null>,
  "summary": "<one or two sentences - what the tale actually says, not editorializing>",
  "touches": []
}
```

`touches` gets filled in as Step 5 proceeds - it's the manifest's whole point: a list of every id (in
`locations`/`characters`/`concepts`/`routes`/`time_systems`/`conflicts`) this tale added or amended,
so a later `/integrate` Pass 3 drift check can confirm the manifest matches reality without re-reading
the tale's full text.

Then add a row to `_lore/tales/_authors.md`'s table:

```markdown
| `<slug>` | <user's name/handle> | <date> |
```

Default `responsible` to the current git `user.name` (`git config user.name`) unless the person
telling the tale identifies themselves as someone else - this field exists so a multi-author project
can later tell who recorded what. **Never write `responsible` into `encodings.json`.** It has no
in-fiction meaning and must stay structurally out of `scripts/lore/sample_lore_knowledge.py`'s reach, the
same way `_lore/facts/facts.json` is kept out of `encodings.json` - see `_lore/tales/_authors.md`'s own
intro.

## Step 5 — Fold into the other categories

Read through `locations`, `characters`, `concepts`, `routes`, and `time_systems` for anything the
tale's content overlaps thematically - a place, a person, an era, a route, a concept it names,
describes, or adds detail to.

- **New entry entirely** (a place/character/concept never on record before): add it in the same shape
  as its neighbors in that array, with `"tale:<slug> (<short note of what the tale said)"` added to
  its `sources` list (or wherever that array records provenance - `characters`/`routes` may nest
  differently than `locations`; match the existing shape exactly rather than inventing a new field).
- **Adds detail to an existing entry**: append the new detail (a note, an additional source-list
  item) - never remove or rewrite what's already there, even if the tale describes the same thing
  differently. That's what conflicts are for, next bullet.
- **Disagrees with an existing entry**: add a new entry to `conflicts` (next `CONFLICT-NN` id -
  the next unused `CONFLICT-NN` number, read from `encodings.json`'s current `conflicts` array),
  `topic` and `detail` describing the disagreement, `user_resolution` left unset. Never resolve it
  yourself, and never quietly prefer the tale's version over the existing one (or vice versa).

Record every id touched (including any new `CONFLICT-NN`) in the `touches` array from Step 4, and in
the tale file's own "Touches"/"Conflicts raised" lines from Step 3.

## Step 6 — Notable unknowns

If the tale poses a question it doesn't itself answer, and that question resonates with the existing
corpus - either it extends a gap already logged in `_lore/unknowns.md`, or it's clearly the
kind of thing the rest of the record would want an answer to - log it there, matching the file's
existing shape (cross-reference the tale's id, and a `CONFLICT-##` id if applicable). Not every tale
produces one; skip this step rather than manufacturing a question that isn't genuinely there. Update
the tale file's "Open questions logged" line accordingly.

## Step 7 — Update the index and report back

Add a row to `_lore/tales/_index.md`'s table (told date, title, told by, responsible, filename, a short
`touches` summary). Then report back to the user: what was recorded, who (if anyone) was credited
in-world, what it touched or added, every new conflict raised (don't bury one in a large diff), and
any notable unknown logged.

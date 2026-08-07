"""
Cold-start bootstrap for the whole lore system: creates whichever of five structural files don't
exist yet, with empty/generic content - never with any of Luminacion's own categories, material,
hearsay, or tales pre-filled in. Three belong to /integrate Pass 1 (`_lore/encodings.json`,
`_lore/material/_context.md`, `_lore/unknowns.md`); two are companion manifests /enact and /tell write
to (`_lore/characters/hearsay.md`, `_lore/tales/_index.md` + `_lore/tales/_authors.md`) that need the
same treatment for the same reason - both skills either assume the file already has a header/table to
append into (`/tell`'s manifests), or would otherwise create a file with no explanatory framing at all
on its very first write (`/enact`'s `record_hearsay.py`, which opens `hearsay.md` in append mode and
so technically survives a missing file, just headerless).

This exists because the original encodings.json was hand-built once, outside any tooling, by reading
all the material fresh and inferring the schema as it went - there was never a repeatable procedure
for it. This script mechanizes only the STRUCTURAL scaffolding every later piece of tooling
(sample_lore_knowledge.py, build_source_index.py, check_anchor_reference.py, record_hearsay.py, /tell,
/character, /enact) already assumes exists, even when empty: `_categories`, `conflicts`, `hearsay`,
`tales`. It deliberately does NOT pre-create `locations`/`concepts`/`characters`/`routes`/
`time_systems` or seed `_categories` with any entries - those are content categories meant to emerge
from real material via /integrate Pass 1's own novel-structure-detection step (see
.claude/skills/integrate/SKILL.md), the same way they did the first time, just asked-and-confirmed
instead of done informally.

Each of the five files is created independently and only if missing - safe to run against a project
that already has some of them (e.g. encodings.json exists but unknowns.md was deleted).

Usage:
    py scripts/lore/bootstrap_lore.py
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
ENCODINGS_PATH = ROOT / "_lore" / "encodings.json"
CONTEXT_PATH = ROOT / "_lore" / "material" / "_context.md"
UNKNOWNS_PATH = ROOT / "_lore" / "unknowns.md"
HEARSAY_MD_PATH = ROOT / "_lore" / "characters" / "hearsay.md"
TALES_INDEX_PATH = ROOT / "_lore" / "tales" / "_index.md"
TALES_AUTHORS_PATH = ROOT / "_lore" / "tales" / "_authors.md"

METHOD_NOTE = (
    "Structured cross-references between whatever entity kinds the material actually contains. "
    "`_categories` (below) describes the current schema and starts empty - it grows as /integrate "
    "Pass 1 analyzes real material and proposes categories, confirmed by the user each time (see "
    ".claude/skills/integrate/SKILL.md). Every entry lists its source file(s). Nothing here is "
    "asserted beyond what a source states; where sources disagree, both values are kept and a "
    "matching entry is added to 'conflicts'. Full prose per source lives in "
    "_lore/material/_context.md; this file is the associative index. IMPORTANT: everything under a "
    "category `_categories` describes is the OBJECTIVE record - reconstructed from primary "
    "materials, per the archaeologist method (see _context.md's own method note), never invented; "
    "disagreements are logged in 'conflicts', never silently resolved. A second, SUBJECTIVE record "
    "sits alongside it: the top-level 'hearsay' array, logging what characters have actually said in "
    "play - never merged into the objective categories and never treated as corroborating them, even "
    "when they happen to agree; see hearsay's own '_method_note'. A third, OBJECTIVE-track array is "
    "'tales', fed by the /tell skill: told directly by the world's author, folded into the objective "
    "categories via a 'tale:<id>' source tag, and into 'conflicts' on disagreement, by the same rules "
    "as any material source; see tales' own '_method_note'."
)

CATEGORIES_METHOD_NOTE = (
    "Describes how scripts/lore/sample_lore_knowledge.py flattens each category below into "
    "sample-able pool items, so the set of categories is read from this data rather than hardcoded "
    "per-path loops in the script. Starts empty - /integrate Pass 1 adds an entry here each time it "
    "analyzes material that doesn't fit an existing category and the user approves a new one (see "
    ".claude/skills/integrate/SKILL.md). 'shape' selects a handler: 'list' (a flat list of dicts at "
    "'path', identified by 'id_field', pool text built by joining 'text_fields') is the default for "
    "any category shaped like that and needs no code change to register; 'grouped_list' and 'claims' "
    "are pre-built handlers for two structural shapes this framework already anticipated (a "
    "dict-of-lists grouping, and a claims-per-entry log like hearsay) - use one of those only if a "
    "new category's shape genuinely matches, otherwise flag that a new handler is needed rather than "
    "force-fitting. 'epistemology_group' ties the category to a row in /character Step 4d's "
    "trusts/distrusts table (.claude/skills/character/SKILL.md) - 'ambiguous' for a category with no "
    "inherent epistemological lean (read it from backstory instead), or a named group shared with "
    "other categories that imply the same kind of trust. 'has_sources' (bool) marks whether entries "
    "in this category carry a 'sources' list (provenance - see "
    ".claude/skills/integrate/SKILL.md Pass 1 step 3) - scripts/lore/build_source_index.py reads "
    "this to know which categories it should link hearsay/tale references into."
)

HEARSAY_METHOD_NOTE = (
    "SUBJECTIVE record, distinct from every objective category. Meant to mirror "
    "_lore/characters/hearsay.md exactly, one entry per real (non-template) played dialogue - see "
    "/enact Step 5 (.claude/skills/enact/SKILL.md) for the recording procedure. 'claims' are what a "
    "character asserted, not verified facts; 'about' cross-references an id in an objective category "
    "ONLY to mark topical overlap, never as corroboration. Consistency is recorded INCONSISTENT-ONLY: "
    "a field is present on a claim only when a genuine contradiction was actually found; absence "
    "means either 'checked and matches' or 'nothing to check against yet.' Two independent flags: (1) "
    "'inconsistent_with_record', an array of {about, source_kind, note} objects, present only when "
    "the claim contradicts something in the objective categories ('source_kind' is 'material'/'tale'); "
    "(2) 'inconsistent_with_facts', a plain string, present only when the claim contradicts one of "
    "the universal facts in _lore/facts/facts.json. Individual claims are drawn into a new "
    "character's knowledge pool by scripts/lore/sample_lore_knowledge.py at the same odds as any "
    "objective-record fact - a claim can be retold and logged again as a fresh claim, and "
    "scripts/lore/lineage_coin.py decides on each retelling whether the origin stays traceable "
    "('derived_from' set to the earlier claim's id) or becomes untraceable oral lore "
    "('oral_lore': true, 'derived_from' left unset)."
)

TALES_METHOD_NOTE = (
    "A THIRD kind of source, distinct from both the objective categories and 'hearsay'. A tale is "
    "told directly by the user, the world's author, outside any character's mouth and outside any "
    "excavated document. Unlike hearsay, a tale IS folded into the objective categories wherever it "
    "overlaps an existing entry, via a 'tale:<id>' item added to that entry's 'sources' list, exactly "
    "like a material-file abbreviation - never by overwriting an existing entry. A genuine "
    "disagreement with something already on record gets a new 'conflicts' entry, 'user_resolution' "
    "left unset. Populated by the /tell skill (.claude/skills/tell/SKILL.md). Each entry here is a "
    "manifest of one tale, not a duplicate of its content: 'touches' lists every id (in any category "
    "above, including 'conflicts') this tale added or amended - the full text lives in "
    "_lore/tales/<id>.md. 'told_by' (nullable) names who is credited IN-FICTION with this tale, if "
    "it's framed that way."
)

CONTEXT_MD_TEMPLATE = """# Context — Excavation Log of `_lore/material/`

Method note: this document treats each source file as an artifact recovered independently, with no
assumption that different artifacts agree with each other or with any outside knowledge. Only what is
written or drawn in the source is recorded here. Where a source poses its own open question or leaves
a blank, that is preserved as a gap, not filled in. Contradictions between sources are noted but not
resolved — resolution is left to the associations in `encodings.json` (flagged) and to `unknowns.md`.

---
"""

UNKNOWNS_MD_TEMPLATE = """# Unknowns

Open questions the objective record (`encodings.json`), the subjective record (`hearsay`), or a told
tale has raised but not yet answered — a gap, not a contradiction (a contradiction between sources goes
in `encodings.json`'s `conflicts` array instead). Never closed on a skill's own judgment; see
`.claude/skills/integrate/SKILL.md` Pass 4 for how an entry here gets flagged as answered.

---
"""

HEARSAY_MD_TEMPLATE = """# Hearsay — What Has Been Said

This is the second of two sources of truth in this world's lore, and it is deliberately not the same
kind of source as the first.

`_context.md` (and the associative index built from it, `encodings.json`) is the **objective
record**. It was built the way an archaeologist reconstructs a civilization: read every primary
document in `_lore/material/`, transcribe only what is actually there, flag contradictions instead of
resolving them, never invent.

`hearsay.md` is the **subjective record** — a running log of what individual characters have actually
said, in played-out dialogues, to each other or to a player. A character's knowledge is bounded,
personal, sometimes secondhand, and never guaranteed complete or correct, exactly like a real person's
(see `.claude/skills/character/SKILL.md` Step 3 for how that bound is set). Nothing in this file is
evidence for what actually happened in the world — it is evidence only for what a specific character,
at a specific moment, said they believed. When a claim here ever contradicts `_context.md`, that is not
an error to reconcile — it's the interesting part, and it should be logged as a divergence, not
silently fixed.

Individual claims here are also part of the knowledge pool a new character can sample from
(`scripts/lore/sample_lore_knowledge.py`), at the same odds as any objective-record fact — so a claim
can be repeated by a character who never touched the objective record at all, only heard it from
someone who'd heard it. Every time that happens, a coin flip (`scripts/lore/lineage_coin.py`, flat
50/50) decides whether the retelling stays traceable or loses its origin.

Every dialog gets an entry here, full stop — not only the ones where a character explicitly retells
something they heard from someone else. A character's own fresh invention (a venue's description, a
personal theory, an on-the-spot guess) belongs in the record exactly as much as an attributed retelling
does. An unverified claim sits at unresolved until something confirms or contradicts it, not at
"assumed false."

Each entry below covers one dialog. "Claims on record" are phrased as reported assertions, not
restated as fact, on purpose.

---
"""

TALES_INDEX_MD_TEMPLATE = """# Tale — Told Directly

This is a third source of truth for this world, alongside the **objective record**
(`_lore/material/_context.md` → `_lore/encodings.json`) and the **in-fiction subjective record**
(`_lore/characters/hearsay.md` — what a *character* said inside a played dialogue, never merged into
the objective categories). A tale is told directly by the user, the world's author, outside of any
character's mouth and outside of any excavated document — whether narrated as a story or stated
plainly as a fact now known. It is treated as genuine, on-par source material: folded into
`encodings.json`'s objective categories wherever its content overlaps an existing entry, the same way
a newly-analysed `_lore/material/` file is folded in per `.claude/skills/integrate/SKILL.md` Pass 1 —
new entries can be added, a disagreement gets a `conflicts` entry (never silently resolved), but no
existing entry is ever overwritten to make room for a tale.

Populated by the `/tell` skill (`.claude/skills/tell/SKILL.md`). One file per tale, named for its
slug (`<slug>.md`). Every tale also gets an entry in `encodings.json`'s `tales.entries[]` array — see
that array's own `_method_note` for the exact shape and what `touches` means.

Every tale distinguishes two different provenance questions. **`told_by`** (optional, lives in
`encodings.json` — it's lore, and can be sampled) is who is credited *in-fiction* with this telling, if
the tale itself is framed that way. **`responsible`** (mandatory, lives in `_lore/tales/_authors.md` —
never in `encodings.json`) is which *real-world user* told the system this tale, walled off from
`scripts/lore/sample_lore_knowledge.py`'s reach on purpose, the same way `_lore/facts/facts.json` is.

## Tales on record

| Told | Title | Told by | Responsible | File | Touches |
|---|---|---|---|---|---|
"""

TALES_AUTHORS_MD_TEMPLATE = """# Authors — Real-World Recordkeeping

This file tracks which *real* user told the system each tale, and when — administrative metadata about
the record's own history, not lore, and it has no in-fiction meaning at all. Not to be confused with a
tale's `told_by` in `../encodings.json` (in-world credit, which *is* lore and can be sampled).
`Responsible` here answers a different question entirely: who, in the real world, entered this into the
record.

**Must never be folded into `_lore/encodings.json` and must never reach
`scripts/lore/sample_lore_knowledge.py`'s pool** — same isolation guarantee as `_lore/facts/facts.json`,
for the same reason: this is the floor the record stands on, not part of it. Every tale entry is
required to have one.

## Authors on record

| Id | Responsible | Recorded |
|---|---|---|
"""


def main() -> None:
    created = []

    if not ENCODINGS_PATH.exists():
        skeleton = {
            "_method_note": METHOD_NOTE,
            "_categories_method_note": CATEGORIES_METHOD_NOTE,
            "_categories": {},
            "conflicts": [],
            "hearsay": {"_method_note": HEARSAY_METHOD_NOTE, "entries": []},
            "tales": {"_method_note": TALES_METHOD_NOTE, "entries": []},
        }
        ENCODINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(ENCODINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(skeleton, f, indent=2, ensure_ascii=False)
        created.append(str(ENCODINGS_PATH))

    if not CONTEXT_PATH.exists():
        CONTEXT_PATH.parent.mkdir(parents=True, exist_ok=True)
        CONTEXT_PATH.write_text(CONTEXT_MD_TEMPLATE, encoding="utf-8")
        created.append(str(CONTEXT_PATH))

    if not UNKNOWNS_PATH.exists():
        UNKNOWNS_PATH.parent.mkdir(parents=True, exist_ok=True)
        UNKNOWNS_PATH.write_text(UNKNOWNS_MD_TEMPLATE, encoding="utf-8")
        created.append(str(UNKNOWNS_PATH))

    if not HEARSAY_MD_PATH.exists():
        HEARSAY_MD_PATH.parent.mkdir(parents=True, exist_ok=True)
        HEARSAY_MD_PATH.write_text(HEARSAY_MD_TEMPLATE, encoding="utf-8")
        created.append(str(HEARSAY_MD_PATH))

    if not TALES_INDEX_PATH.exists():
        TALES_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
        TALES_INDEX_PATH.write_text(TALES_INDEX_MD_TEMPLATE, encoding="utf-8")
        created.append(str(TALES_INDEX_PATH))

    if not TALES_AUTHORS_PATH.exists():
        TALES_AUTHORS_PATH.parent.mkdir(parents=True, exist_ok=True)
        TALES_AUTHORS_PATH.write_text(TALES_AUTHORS_MD_TEMPLATE, encoding="utf-8")
        created.append(str(TALES_AUTHORS_PATH))

    if created:
        print("Created:")
        for c in created:
            print(f"  {c}")
        print(
            "\nNo content categories (locations/concepts/characters/routes/time_systems) and no "
            "hearsay/tale entries were pre-created - /integrate Pass 1 proposes each category the "
            "first time real material calls for it, and /enact/`/tell` populate their own manifests "
            "the first time they actually run."
        )
    else:
        print("Nothing to bootstrap - all five files already exist.")


if __name__ == "__main__":
    main()

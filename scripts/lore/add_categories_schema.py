"""
One-time migration: add the `_categories` schema block to `_lore/encodings.json`, describing how
`scripts/lore/sample_lore_knowledge.py` should flatten each existing category into sample-able pool
items. This is the TODO item "encodings.json schema must be able to evolve" / "sampling script must
discover categories dynamically" (see TODO.md, "Schema evolution in encodings.json" section).

Every entry here reproduces `sample_lore_knowledge.py`'s previous hardcoded `flatten_pool()` logic
exactly - this migration changes WHERE the shape is described (data, not code), not what the pool
actually contains. Verified via scripts/lore/compare_pool.py against a pre-migration baseline.

Historical note (2026-08-16): this migration originally also stamped each category with an
`epistemology_group` field, tying it to a row in /character Step 4d's old trusts/distrusts table.
That field has since been removed entirely - Step 4d now derives trusts/distrusts per item from that
item's own `sources[]` provenance (`scripts/lore/anchor_epistemology.py`), not from a per-category
classification, so the CATEGORIES dict below no longer needs one and this script won't reintroduce it
if ever re-run. When `/integrate` Pass 1 approves a genuinely new category, it registers a spec here
(`shape: "list"` covers a flat list of `{id-ish field, ...}` dicts automatically; a structurally novel
shape needs a new handler added to `sample_lore_knowledge.py`'s SHAPE_HANDLERS by hand - this
migration doesn't remove that limit, it only removes hardcoded per-path iteration for every category
that already follows the common shape) - nothing else needs authoring alongside it anymore.

Usage:
    py scripts/lore/add_categories_schema.py
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
ENCODINGS_PATH = ROOT / "_lore" / "encodings.json"

CATEGORIES = {
    "location": {
        "path": "locations", "shape": "list", "id_field": "id",
        "text_fields": ["names", "region", "type_catastro", "notes"],
    },
    "concept": {
        "path": "concepts", "shape": "list", "id_field": "id",
        "text_fields": ["names", "description", "notes"],
    },
    "conflict": {
        "path": "conflicts", "shape": "list", "id_field": "id",
        "text_fields": ["topic", "detail"],
    },
    "character_legendary": {
        "path": "characters.in_world_or_legendary", "shape": "list", "id_field": "id",
        "text_fields": ["names", "role", "notes"],
    },
    "character_real": {
        "path": "characters.real_world_authors_and_players", "shape": "list", "id_field": "id",
        "text_fields": ["names", "role"],
    },
    "inhabitant": {
        "path": "characters.named_inhabitants.by_locality", "shape": "grouped_list",
    },
    "highway": {
        "path": "routes.highways", "shape": "list", "id_field": "code",
        "text_fields": ["name"],
    },
    "train_segment": {
        "path": "routes.trains.segments", "shape": "list", "id_field": "name",
        "text_fields": ["name"],
    },
    "airport": {
        "path": "routes.airports", "shape": "list", "id_field": "location",
        "text_fields": ["location"],
    },
    "route_named": {
        "path": "routes.named_but_unplotted", "shape": "list", "id_field": "name",
        "text_fields": ["name"],
    },
    "era_ensayo": {
        "path": "time_systems.ensayo_i_eras", "shape": "list", "id_field": "name",
        "text_fields": ["name"],
    },
    "era_esquema": {
        "path": "time_systems.esquema_poster_eras.era_row", "shape": "list", "id_field": "name",
        "text_fields": ["name"],
    },
    "year_esquema": {
        "path": "time_systems.esquema_poster_eras.year_by_year_foundations", "shape": "list",
        "id_field": "year", "text_fields": ["places"],
    },
    "era_libro": {
        "path": "time_systems.libro_venidas_eras.list", "shape": "list", "id_field": "name",
        "text_fields": ["name"],
    },
    "hearsay": {
        "path": "hearsay.entries", "shape": "claims",
    },
}

_SOURCED = {"location", "concept", "character_legendary", "character_real"}
for _key, _spec in CATEGORIES.items():
    _spec["has_sources"] = _key in _SOURCED

METHOD_NOTE = (
    "Describes how scripts/lore/sample_lore_knowledge.py flattens each category below into "
    "sample-able pool items, so the set of categories is read from this data rather than hardcoded "
    "per-path loops in the script. 'shape' selects a handler: 'list' (a flat list of dicts at 'path', "
    "identified by 'id_field', pool text built by joining 'text_fields') covers most categories and is "
    "the default shape for any new category with that structure; 'grouped_list' and 'claims' are "
    "special-cased for characters.named_inhabitants.by_locality and hearsay.entries respectively, since "
    "neither is a flat list. 'epistemology_group' ties the category to a row in /character Step 4d's "
    "trusts/distrusts table (.claude/skills/character/SKILL.md) - 'ambiguous' for categories in that "
    "table's bottom row (read the lean from backstory instead), or a named group matching one of its "
    "other rows. When /integrate approves a genuinely new category, it adds an entry here (and, if the "
    "shape isn't 'list', a new handler in SHAPE_HANDLERS) plus either an existing epistemology_group or "
    "a newly-drafted, user-confirmed Step 4d table row. 'has_sources' (bool) marks whether entries in "
    "this category carry a 'sources' list (provenance) - scripts/lore/build_source_index.py reads this "
    "to know which categories it should link hearsay/tale references into, instead of a hardcoded list."
)


def main() -> None:
    with open(ENCODINGS_PATH, encoding="utf-8") as f:
        data = json.load(f)

    if "_categories" in data:
        raise SystemExit("_categories already present - this migration has already run.")

    # Insert right after _method_note, before the data arrays, preserving key order for readability.
    new_data = {}
    for k, v in data.items():
        new_data[k] = v
        if k == "_method_note":
            new_data["_categories_method_note"] = METHOD_NOTE
            new_data["_categories"] = CATEGORIES

    with open(ENCODINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(new_data, f, indent=2, ensure_ascii=False)

    print(f"Added _categories ({len(CATEGORIES)} entries) and _categories_method_note to {ENCODINGS_PATH}")


if __name__ == "__main__":
    main()

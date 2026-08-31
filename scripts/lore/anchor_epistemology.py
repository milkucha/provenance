"""
Resolve a criterion anchor's provenance-based epistemology - the mechanical half of /character Step
4d's trusts/distrusts derivation (design correction, 2026-08-16, replacing the old per-category
`epistemology_group` system - see _lore/encodings.json's `_categories_method_note` for why a
category-level classification never actually worked: two items in the same category, e.g. two
locations, can have completely different provenance).

This script only ever computes the signal. It does NOT decide trusts/distrusts wording - that stays
Step 4d's own judgment call, same discipline as every other script in this pack (baseline_stats.py,
check_anchor_reference.py, ...).

Three cases, in order:
1. The anchor's own category IS a provenance already - `hearsay: <id>#<n>` resolves trivially to
   "hearsay" (the item IS a hearsay claim), `tale: <id>` resolves trivially to "tale" (the item IS a
   tale). No lookup needed.
2. `conflict: CONFLICT-NN` is a fixed special case, entirely outside the material/hearsay/tale
   system: a conflict anchor is definitionally two sources disagreeing, not sourced from one
   provenance itself. Prints a note pointing at Step 4d's own fixed conflict row rather than
   computing anything.
3. Everything else (location, concept, era_*, character_*, ...) - look up the item's own `sources[]`
   array in encodings.json and take the FIRST entry's `category` (material/hearsay/tale).
   `sources[]` is append-only (build_source_index.py only ever adds backlinks onto what's already
   there), so "first recorded" means "what actually established this in the record" - not a random
   pick among however many backlinks have since accumulated. If `sources[]` is empty (e.g. a
   freshly arc-authored concept with no material/hearsay/tale link yet), there is nothing to derive
   from: report that plainly rather than guessing, same as any other "leave it blank" case in this
   system (`origin: "uncollided"` for a criterion, `origin: "inherited"` for a child's).

Usage:
    py scripts/lore/anchor_epistemology.py "location: city_b"
    py scripts/lore/anchor_epistemology.py "hearsay: character_a_shared_fund#4"
    py scripts/lore/anchor_epistemology.py "concept: la_lagrima_de_balahm"
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
ENCODINGS_PATH = ROOT / "_lore" / "encodings.json"
SCRIPTS_DIR = Path(__file__).resolve().parent

sys.path.insert(0, str(SCRIPTS_DIR))
import sample_lore_knowledge as slk  # noqa: E402 - reuse its _get_path, not reimplement lookup


def find_item(data: dict, category: str, item_id: str) -> dict | None:
    spec = data["_categories"].get(category)
    if spec is None:
        return None
    if spec["shape"] != "list":
        return None  # grouped_list/claims items are handled as trivial cases before this is called
    id_field = spec["id_field"]
    for entry in slk._get_path(data, spec["path"]):
        entry_id = entry[id_field]
        if not isinstance(entry_id, str):
            entry_id = str(entry_id)
        if entry_id == item_id:
            return entry
    return None


def resolve_epistemology(anchor: str, data: dict) -> dict:
    """The importable half of this script (2026-08-17, extracted so generate_offspring.py's own
    mechanical criterion derivation can call this directly instead of shelling out once per child) -
    same three-case logic the CLI below just prints. Returns
    `{"epistemology": "material"/"hearsay"/"tale"/"conflict"/None, "reason": "..."}`.
    `epistemology: None` means there's nothing to derive from (unregistered item, or a real item with
    an empty `sources[]`) - the caller must leave trusts/distrusts blank rather than guess, same
    discipline as every other 'nothing to derive from' case in this system."""
    if ": " not in anchor:
        raise ValueError(f"'{anchor}' doesn't look like a '<category>: <id>' anchor reference.")
    category, item_id = anchor.split(": ", 1)
    category, item_id = category.strip(), item_id.strip()

    if category == "hearsay":
        return {"epistemology": "hearsay", "reason": "the anchor IS a hearsay claim - trivial, no lookup needed"}
    if category == "tale":
        return {"epistemology": "tale", "reason": "the anchor IS a tale - trivial, no lookup needed"}
    if category == "conflict":
        return {
            "epistemology": "conflict",
            "reason": (
                "a conflict is definitionally two sources disagreeing, not sourced from one "
                "provenance itself - use /character Step 4d's own fixed conflict row "
                '("trusts verification, distrusts anyone who sounds certain") unchanged.'
            ),
        }

    item = find_item(data, category, item_id)
    if item is None:
        return {"epistemology": None, "reason": f"no '{category}' entry with id '{item_id}' found in encodings.json"}

    sources = item.get("sources", [])
    if not sources:
        return {"epistemology": None, "reason": "no sources on record for this item"}

    leading = sources[0]
    return {
        "epistemology": leading["category"],
        "reason": f"first-recorded source ({leading['category']}: {leading.get('origin', '?')})",
        "other_sources": [s["category"] for s in sources[1:]],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("anchor", help='Anchor reference, e.g. "location: city_b" or "hearsay: character_a_shared_fund#4"')
    args = parser.parse_args()

    with open(ENCODINGS_PATH, encoding="utf-8") as f:
        data = json.load(f)

    try:
        result = resolve_epistemology(args.anchor, data)
    except ValueError as e:
        raise SystemExit(str(e))

    if result["epistemology"] is None:
        print(f"epistemology: none - {result['reason']}")
        print("reason: leave trusts/distrusts blank, same as any other 'nothing to derive from' case")
        print("        (do not guess or fall back to a default)")
        return

    print(f"epistemology: {result['epistemology']}")
    print(f"reason: {result['reason']}")
    others = result.get("other_sources") or []
    if others:
        print(f"note: {len(others)} later-linked source(s) also present ({', '.join(others)}) - ignored,")
        print("      per the original-source-priority rule (later backlinks don't compete)")


if __name__ == "__main__":
    main()

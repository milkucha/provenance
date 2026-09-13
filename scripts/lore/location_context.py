"""
Derive what a location actually IS, and resolve an arc's `needs` tag to a real travel target - built
on top of `scripts/lore/travel_graph.py` (Wave 1's pathfinding infrastructure; read that module's
docstring before this one, its function signatures are a fixed contract here).

Design decision this module implements (see the task brief this was written from, and TODO.md/
CHRONICLE.md for the surrounding travel-system design conversation): a location has no stored
"context" field of its own. What kind of place it is - a market town, a quiet residential spot,
a temple town - is a DERIVED fact, computed by tallying every character's `routines[]` entries set
at that location and seeing which `context` values (from `_lore/contexts.json`) show up, and at what
combined weight. No hand-authoring, no `/integrate` inference from prose: a location becomes a
market town because enough characters' routines say so, nothing more.

Separately, an arc's `needs` tag (one of `_lore/contexts.json`'s minimal `provides` vocabulary -
materials, items, transit, nourishment, records, news) has to resolve to an actual target location
when the arc's owner can't satisfy it where they currently are. There are two tiers, and they are a
real epistemic distinction, not two ways of finding the same thing:

  - **Tier 3 (known supplier).** A traveler paths toward a location where they specifically know a
    supplier - someone in their own `partners`/`social_circle`/`parents` whose own routine matches
    the need. This is preferred whenever it's available: it's a warm lead, not a rumor.
  - **Tier 4 (general/heard-about).** Falls back to "I've just heard this place has it" - any
    reachable location whose derived `location_provides()` covers the need, or whose encodings.json
    `description`/`composition` text word-overlaps the need - only used when tier 3 comes back empty.

This module is pure/testable: every function takes already-loaded data as arguments (the caller does
its own file I/O), same discipline `travel_graph.py`'s `build_graph()`/`reachable_set()` follow at
the seams that matter, even though (like `travel_graph.py`) it still loads individual character
files itself where it needs to walk a person's own social ties (see `_load_character` reuse below).

Usage (from a sibling script, once a later wave wires this into /simulate's arc-needs handling):
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import location_context
    result = location_context.resolve_arc_target(traveler, need, encodings_data, all_characters, contexts_data)
    if result:
        target, path = result
        hop = travel_graph.next_hop(path)

Standalone test/demo:
    python scripts/lore/location_context.py
"""

import argparse
import json
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT = SCRIPTS_DIR.parent.parent
CHAR_DIR = ROOT / "_lore" / "characters"
CONTEXTS_PATH = ROOT / "_lore" / "contexts.json"
ENCODINGS_PATH = ROOT / "_lore" / "encodings.json"

sys.path.insert(0, str(SCRIPTS_DIR))
import travel_graph  # noqa: E402
from check_arc_alignment import significant_words  # noqa: E402


def _load_character(key: str) -> dict | None:
    """Load one character file by key - identical lookup to travel_graph.py's own `_load_character`
    (not imported from there since it's a private helper, not part of that module's documented
    contract; duplicating one four-line function is cheaper than reaching into another module's
    underscore-prefixed internals)."""
    path = CHAR_DIR / f"{key}.json"
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def location_context_tally(location_id: str, all_characters: list[dict]) -> dict[str, float]:
    """Tally every character's routines[] entries set at `location_id`, weighted by each routine's
    own `weight` field, grouped by that routine's `context`. Returns {context_name: total_weight}.

    Deliberately RAW-SUMMED, not normalized to any total (e.g. not divided by 100 or by number of
    contributing characters): normalizing would need a decision about what the denominator even
    means (per-character weights aren't guaranteed to sum to 100 the way roll_routine.py's own
    per-character routine weights conventionally do - see darius.json, a single 100-weight routine -
    and summing across an arbitrary number of characters has no natural ceiling). Raw sums keep this
    function honest about what it actually knows: "this many combined routine-weight-points of
    evidence point at this context," nothing more. A caller wanting a normalized share (e.g. for
    display) can trivially divide by the tally's own sum(); baking that in here would just delete
    information for a use case this module doesn't have.
    """
    tally: dict[str, float] = {}
    for character in all_characters:
        for routine in character.get("routines") or []:
            if routine.get("location") != location_id:
                continue
            context = routine.get("context")
            if not context:
                continue
            weight = routine.get("weight", 0) or 0
            tally[context] = tally.get(context, 0) + weight
    return tally


def location_provides(location_id: str, all_characters: list[dict], contexts_data: dict) -> set[str]:
    """The union of `provides` tags for every context that has ANY nonzero tally weight at this
    location (per location_context_tally()) - a single character's single routine is enough to put
    that context's whole `provides` list on the table.

    Deliberate simplification, stated explicitly: this does NOT threshold by weight magnitude. One
    stray "context": "market" routine with weight 1 grants the same `provides` set as a location
    where every character's routine is "market". A real magnitude-aware version (e.g. "market" only
    counts once it clears some share of the tally) is a plausible future refinement, but nothing in
    the design conversation this module implements calls for it, and presence-only is the simpler,
    more legible rule: a location provides what SOME real routine there provides, full stop.
    """
    tally = location_context_tally(location_id, all_characters)
    provides: set[str] = set()
    for context, weight in tally.items():
        if weight <= 0:
            continue
        provides.update((contexts_data.get(context) or {}).get("provides") or [])
    return provides


def _known_keys(traveler: dict) -> set[str]:
    """Every character key in the traveler's own partners/social_circle/parents - the traveler's
    "own circle" for tier-3 known-supplier lookups. Same three fields travel_graph.py's own
    `_known_people_locations` reads, for the same reason (see that function's docstring)."""
    keys: set[str] = set()
    keys.update((traveler.get("partners") or {}).keys())
    keys.update(traveler.get("social_circle") or [])
    keys.update(traveler.get("parents") or [])
    return keys


def find_supplier_locations(traveler: dict, need: str, all_characters: list[dict], contexts_data: dict) -> set[str]:
    """Tier 3: known-supplier locations. For every character in the traveler's own circle
    (partners/social_circle/parents), load that person's own file and check whether any of THEIR
    routines[] has a context whose `provides` list contains `need`. Collect that routine's
    `location` as a candidate. `all_characters` is accepted (matching the task's declared signature)
    but not needed here beyond the traveler's own circle - each known person is loaded fresh by key
    via `_load_character` since a known person may not be in whatever slice of the population the
    caller happened to pass as `all_characters`."""
    candidates: set[str] = set()
    for key in _known_keys(traveler):
        other = _load_character(key)
        if not other:
            continue
        for routine in other.get("routines") or []:
            context = routine.get("context")
            location = routine.get("location")
            if not context or not location:
                continue
            provides = (contexts_data.get(context) or {}).get("provides") or []
            if need in provides:
                candidates.add(location)
    return candidates


def find_general_locations(
    traveler: dict, need: str, encodings_data: dict, reachable: set[str],
    all_characters: list[dict], contexts_data: dict,
) -> set[str]:
    """Tier 4: the "I've just heard this place has it" fallback, only meant to be tried once tier 3
    comes back empty. Among `reachable` (travel_graph.reachable_set()'s own output, passed in rather
    than recomputed - this function does no graph work of its own), a location counts if EITHER:
      - `location_provides()` for it already includes `need` (some routine there matches), OR
      - its `_lore/encodings.json` `description`/`composition` text has significant word-overlap
        with `need`, via check_arc_alignment.significant_words() (imported directly rather than
        mirrored - it's a plain, dependency-free function importable with no side effects, so
        reimplementing it would just be duplication for no reason).
    `traveler` is accepted (matching the task's declared signature) but unused: tier 4 is
    traveler-agnostic by design - it's the "public knowledge" tier, not keyed to who's asking.
    """
    del traveler  # tier 4 is deliberately traveler-agnostic; see docstring
    need_words = significant_words(need)
    locations_by_id = {loc.get("id"): loc for loc in encodings_data.get("locations", []) or [] if loc.get("id")}

    matches: set[str] = set()
    for location_id in reachable:
        if need in location_provides(location_id, all_characters, contexts_data):
            matches.add(location_id)
            continue
        loc = locations_by_id.get(location_id) or {}
        text = f"{loc.get('description', '')} {loc.get('composition', '')}"
        if need_words & significant_words(text):
            matches.add(location_id)
    return matches


def resolve_arc_target(
    traveler: dict, need: str, encodings_data: dict, all_characters: list[dict], contexts_data: dict,
) -> tuple[str, list[str]] | None:
    """Top-level entry point: resolve an arc's `need` tag to an actual pathfinding target for
    `traveler`. Known-supplier (tier 3) locations are strictly preferred over general/heard-about
    (tier 4) ones whenever tier 3 has ANY reachable candidate - even if a tier-4 candidate would be
    closer. That preference is the real epistemic distinction the task calls for: a known supplier is
    worth a longer walk over a rumor. Returns (target_id, full_path) exactly matching
    travel_graph.shortest_path()'s own return shape, or None if neither tier has a reachable target.
    """
    graph = travel_graph.build_graph(encodings_data)
    reachable = travel_graph.reachable_set(traveler, encodings_data)
    start = traveler.get("location")

    supplier_targets = find_supplier_locations(traveler, need, all_characters, contexts_data) & reachable
    if supplier_targets:
        result = travel_graph.shortest_path(graph, start, supplier_targets)
        if result:
            return result

    general_targets = find_general_locations(traveler, need, encodings_data, reachable, all_characters, contexts_data)
    if not general_targets:
        return None
    return travel_graph.shortest_path(graph, start, general_targets)


def _demo() -> None:
    """Hardcoded in-memory fixture exercising all five functions, including one case where tier 3
    (known supplier) succeeds outright, and one where it's empty and tier 4 (general fallback) has
    to catch it instead."""
    encodings_data = {
        "locations": [
            {"id": "terfila", "description": "A crossing town.", "composition": ""},
            {"id": "gorff", "description": "", "composition": "Known for its rare ore deposits and trade in materials."},
            {"id": "lundria", "description": "A quiet farming village.", "composition": ""},
        ],
        "routes": [
            {"id": "r1", "endpoints": ["terfila", "gorff"]},
            {"id": "r2", "endpoints": ["gorff", "lundria"]},
        ],
    }
    contexts_data = {
        "market": {"provides": ["materials", "items"]},
        "home": {"provides": ["nourishment", "records"]},
        "route": {"provides": ["transit", "news"]},
    }

    # --- location_context_tally / location_provides ---
    print("=== location_context_tally / location_provides ===")
    all_characters = [
        {"routines": [{"location": "gorff", "context": "market", "weight": 60}]},
        {"routines": [{"location": "gorff", "context": "market", "weight": 40}]},
        {"routines": [{"location": "gorff", "context": "home", "weight": 5}]},
        {"routines": [{"location": "lundria", "context": "home", "weight": 100}]},
    ]
    tally = location_context_tally("gorff", all_characters)
    print(f"  gorff tally: {tally}")
    assert tally == {"market": 100, "home": 5}
    provides = location_provides("gorff", all_characters, contexts_data)
    print(f"  gorff provides: {sorted(provides)}")
    assert provides == {"materials", "items", "nourishment", "records"}
    print("  OK: raw-summed tally; presence-only provides union (weight-5 'home' still counts in full)")
    print()

    # --- find_supplier_locations: tier 3 succeeds ---
    print("=== find_supplier_locations (tier 3 hit) ===")
    traveler = {
        "location": "terfila",
        "places_visited": ["gorff", "lundria"],
        "knowledge": {"education": {"items": []}, "experience": []},
        "partners": {"orenna": 3},
        "social_circle": ["belken"],
        "parents": [],
    }
    supplier_fixtures = {
        "orenna": {"routines": [{"location": "gorff", "context": "market", "weight": 100}]},
        "belken": {"routines": [{"location": "lundria", "context": "home", "weight": 100}]},
    }
    original_load = _load_character
    globals()["_load_character"] = lambda key: supplier_fixtures.get(key)
    try:
        suppliers = find_supplier_locations(traveler, "materials", all_characters, contexts_data)
    finally:
        globals()["_load_character"] = original_load
    print(f"  suppliers for 'materials': {sorted(suppliers)}")
    assert suppliers == {"gorff"}
    print("  OK: orenna's own market routine at gorff surfaced; belken's home routine did not")
    print()

    # --- resolve_arc_target: tier 3 path (known supplier preferred) ---
    print("=== resolve_arc_target (tier 3 succeeds) ===")
    globals()["_load_character"] = lambda key: supplier_fixtures.get(key)
    try:
        result = resolve_arc_target(traveler, "materials", encodings_data, all_characters, contexts_data)
    finally:
        globals()["_load_character"] = original_load
    print(f"  result: {result}")
    assert result == ("gorff", ["terfila", "gorff"])
    print("  OK: pathed to known supplier's location")
    print()

    # --- find_general_locations + resolve_arc_target: tier 3 empty, tier 4 catches it ---
    print("=== find_general_locations / resolve_arc_target (tier 3 empty -> tier 4 fallback) ===")
    lonely_traveler = {
        "location": "terfila",
        "places_visited": ["gorff", "lundria"],
        "knowledge": {"education": {"items": []}, "experience": []},
        "partners": {},
        "social_circle": [],
        "parents": [],
    }
    globals()["_load_character"] = lambda key: None
    try:
        suppliers_empty = find_supplier_locations(lonely_traveler, "materials", all_characters, contexts_data)
        print(f"  suppliers (no circle): {suppliers_empty}")
        assert suppliers_empty == set()

        reachable = travel_graph.reachable_set(lonely_traveler, encodings_data)
        print(f"  reachable: {sorted(reachable)}")
        general = find_general_locations(lonely_traveler, "materials", encodings_data, reachable, all_characters, contexts_data)
        print(f"  general matches for 'materials': {sorted(general)}")
        # gorff matches via location_provides (market routines); also gorff's own composition text
        # ("materials") word-overlaps - either reason alone would qualify it.
        assert general == {"gorff"}

        result2 = resolve_arc_target(lonely_traveler, "materials", encodings_data, all_characters, contexts_data)
        print(f"  resolve_arc_target result: {result2}")
        assert result2 == ("gorff", ["terfila", "gorff"])
    finally:
        globals()["_load_character"] = original_load
    print("  OK: no known circle -> tier 3 empty -> tier 4 general fallback found gorff")
    print()

    # --- resolve_arc_target: neither tier has anything ---
    print("=== resolve_arc_target (no target at all) ===")
    globals()["_load_character"] = lambda key: None
    try:
        # "news" isn't in any fixture context's `provides` (only market/home are populated here,
        # neither offers it) and word-overlaps none of the fixture locations' description/composition
        # text - unlike "records" it genuinely matches nothing in either tier, even though lundria
        # (which DOES provide "records" via its home routine) is actually reachable in this fixture.
        result3 = resolve_arc_target(lonely_traveler, "news", encodings_data, all_characters, contexts_data)
    finally:
        globals()["_load_character"] = original_load
    print(f"  result: {result3}")
    assert result3 is None
    print("  OK: 'news' matches nothing in either tier -> correctly None")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--live", action="store_true",
        help="Compute location_provides() for every real location in _lore/encodings.json against "
             "every real character file, instead of running the demo fixture.",
    )
    args = parser.parse_args()

    if args.live:
        with open(ENCODINGS_PATH, encoding="utf-8") as f:
            encodings_data = json.load(f)
        with open(CONTEXTS_PATH, encoding="utf-8") as f:
            contexts_data = json.load(f)
        all_characters = []
        for path in CHAR_DIR.glob("*.json"):
            if path.stem == "lifespans":
                continue
            with open(path, encoding="utf-8") as f:
                all_characters.append(json.load(f))

        for loc in encodings_data.get("locations", []) or []:
            loc_id = loc.get("id")
            if not loc_id:
                continue
            tally = location_context_tally(loc_id, all_characters)
            provides = location_provides(loc_id, all_characters, contexts_data)
            print(f"{loc_id}: tally={tally} provides={sorted(provides)}")
        return

    _demo()


if __name__ == "__main__":
    main()

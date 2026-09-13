"""
Location travel graph and pathfinding - foundational infrastructure only. This module does not
wire into /simulate's pass sequence itself (a separate, later implementation wave owns that); it
just gives that wave a working graph + BFS to build on, so the mechanical "how do I get from here
to there" question has one settled answer instead of getting reinvented ad hoc wherever travel
comes up.

Design conversation 2026-09-12/13 (see TODO.md's "Travel system design sketch" entry and
CHRONICLE.md's matching 2026-09-13 entry) settled the shape this module implements:

  - **Locations form a graph.** Nodes are `_lore/encodings.json` `locations[].id` values; edges are
    `_lore/encodings.json` `routes[].endpoints`. This isn't incidental - `route.endpoints` was
    deliberately shaped in the 2026-09-12 encodings.json restructure specifically to double as the
    travel graph's edge list (see `_categories.route` in encodings.json, and TODO.md).
  - **Reachability** for a character is: everywhere in their own `places_visited`, everywhere named
    in their own knowledge (education + experience), and everywhere a person they know (`partners`,
    `social_circle`, `parents`) currently is - all filtered down to only what's actually graph-
    connected to the character's OWN current location. Knowing about a place, or knowing someone
    who's there, is what makes it a *candidate* destination; connectivity is what makes it a
    *reachable* one. A known-but-disconnected location is knowledge, not a destination.
  - **Travel is unweighted BFS**, not a shortest-distance-in-miles calculation - nothing in the
    design conversation introduced edge weights/distances, so none are invented here. Every route is
    one hop, full stop.

Assumptions made explicit here rather than guessed silently (both confirmed by reading the actual
current schema and `scripts/graphs/graphifyish.py`, which already treats `routes[].endpoints` as an
edge list, before writing any code):

  1. **`route.endpoints` shape.** `_lore/encodings.json`'s `_categories.route.fields` lists
     `endpoints` with no cardinality constraint, and nothing in TODO.md/CHRONICLE.md restricts a
     route to exactly two points - a route is documented as a "way between places" (plural), and
     `graphifyish.py` iterates `endpoints` as an arbitrary-length list. So `build_graph()` below
     treats `endpoints` as a list of `>= 2` location ids and connects EVERY pair of those ids to each
     other (a multi-stop route becomes a small clique, not a chain) - deliberately the more general
     reading, since nothing in the schema orders `endpoints` as a sequence of hops, and an unordered
     "these places are all reachable via this one route" is the only claim `endpoints` unambiguously
     makes. If real data later wants a route to mean an ORDERED chain (A-B-C-D as three hops, not one
     clique), that's a real design decision for whoever populates `routes[]` - not one to guess here.
  2. **Location identity.** Graph nodes are `locations[].id` strings, and a character's own
     `location` field is assumed to already hold that same id string (the same assumption
     `provisions_lib.py`/`roll_survival.py` already make about `location` being a stable key to
     compare against). `graphifyish.py` additionally resolves free-text place names onto location
     ids via a names/aliases index, for rendering a graph off hand-authored prose; this module does
     NOT do that resolution - it is pathfinding infrastructure, not a name-matching layer, and
     resolving display names to ids is a concern for whoever populates `character.location`
     consistently in the first place. If that turns out to be wrong once real data lands, the fix
     belongs in front of this module (normalize `character.location` to an id before calling in),
     not inside it.
  3. **Knowledge location-references.** A knowledge item names a location via a `"location: <id>"`
     ref string, same convention `check_resonance.py`/`check_arc_alignment.py` already parse
     (`category_of()`/`id_part()`: split once on `": "`, prefix is the category, suffix is the id).
     `knowledge.education.items` is always ref-shaped (per `sample_lore_knowledge.py` /
     `check_resonance.py`'s own docstrings). `knowledge.experience` entries are either a legacy plain
     string (ungrounded - no ref, skipped) or a dict with an `about` field holding one ref or a list
     of refs (grounded, per `check_resonance.py`'s `standing_refs()`) - only the `location:`-prefixed
     refs are pulled out here.

Usage (from a sibling script, once the second implementation wave wires this in):
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import travel_graph
    graph = travel_graph.build_graph(encodings_data)
    known = travel_graph.reachable_set(character, encodings_data)
    result = travel_graph.shortest_path(graph, character["location"], known)
    if result:
        target, path = result
        hop = travel_graph.next_hop(path)

Standalone test/demo:
    python scripts/lore/travel_graph.py
"""

import argparse
import json
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
CHAR_DIR = ROOT / "_lore" / "characters"
ENCODINGS_PATH = ROOT / "_lore" / "encodings.json"


def _load_character(key: str) -> dict | None:
    """Load one character file by key, same lookup pattern notify_death.py's load() uses (skips
    the non-character files in _lore/characters/). Returns None rather than raising if the key
    doesn't resolve to a file - a partner/social_circle/parent reference pointing at a character
    who was never fleshed out into a file of their own is a real, unremarkable gap, not an error."""
    path = CHAR_DIR / f"{key}.json"
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_graph(encodings_data: dict) -> dict[str, set[str]]:
    """Parse `locations[]` and `routes[].endpoints` into an adjacency map: {location_id: {ids of
    every location directly reachable via one route}, ...}. Every location gets a node (even one
    with no routes at all yet, i.e. an empty adjacency set) so lookups against a known location id
    never KeyError. See module docstring assumption 1 for why a route with more than two endpoints
    connects every pair of its points rather than chaining them in order."""
    graph: dict[str, set[str]] = {}

    for loc in encodings_data.get("locations", []) or []:
        loc_id = loc.get("id")
        if loc_id:
            graph.setdefault(loc_id, set())

    for route in encodings_data.get("routes", []) or []:
        endpoints = [e for e in (route.get("endpoints") or []) if e]
        for i, a in enumerate(endpoints):
            graph.setdefault(a, set())
            for b in endpoints[i + 1:]:
                graph.setdefault(b, set())
                graph[a].add(b)
                graph[b].add(a)

    return graph


def _bfs_reachable(graph: dict[str, set[str]], start: str) -> set[str]:
    """Every location id reachable from `start` by some sequence of edges, start included. Plain
    BFS over the unweighted adjacency map - no distances tracked, this is a reachability check
    only."""
    if start not in graph:
        return set()
    seen = {start}
    queue = deque([start])
    while queue:
        current = queue.popleft()
        for neighbor in graph.get(current, ()):
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)
    return seen


def _location_refs_from_knowledge(character: dict) -> set[str]:
    """Every location id named in this character's own knowledge - education.items (always
    ref-shaped) plus grounded knowledge.experience entries' `about` ref(s). See module docstring
    assumption 3 for the "category: id" ref convention this reuses verbatim from
    check_resonance.py/check_arc_alignment.py rather than inventing a new parse."""
    refs: list[str] = []
    knowledge = character.get("knowledge", {}) or {}

    education_items = (knowledge.get("education") or {}).get("items") or []
    refs.extend(education_items)

    for entry in knowledge.get("experience") or []:
        if not isinstance(entry, dict):
            continue  # legacy/ungrounded plain string - no ref to extract
        about = entry.get("about")
        if about is None:
            continue
        refs.extend(about if isinstance(about, list) else [about])

    locations: set[str] = set()
    for ref in refs:
        if not isinstance(ref, str) or ": " not in ref:
            continue
        category, _, loc_id = ref.partition(": ")
        if category.strip().lower() == "location":
            locations.add(loc_id.strip())
    return locations


def _known_people_locations(character: dict) -> set[str]:
    """Current `location` of every character in this character's own `partners`, `social_circle`,
    and `parents` fields - their own known people's whereabouts. `partners`/`partners_quality` are
    dicts keyed by character key (see roll_survival.py's net_affinity()); `social_circle`/`parents`
    are plain key lists (see notify_death.py's compute_relations())."""
    keys: set[str] = set()
    keys.update((character.get("partners") or {}).keys())
    keys.update(character.get("social_circle") or [])
    keys.update(character.get("parents") or [])

    locations: set[str] = set()
    for key in keys:
        other = _load_character(key)
        if other and other.get("location"):
            locations.add(other["location"])
    return locations


def reachable_set(character: dict, encodings_data: dict) -> set[str]:
    """The set of location ids this character can currently consider as pathfinding destinations:
    their own places_visited, everywhere named in their own knowledge, and everywhere a known
    person (partner/social_circle/parent) currently is - intersected with actual graph connectivity
    from the character's OWN current `location`. A known-but-disconnected location is filtered out:
    it's knowledge, not a reachable destination. See module docstring for the full rule and its
    2026-09-13 design-conversation source."""
    known: set[str] = set()
    known.update(character.get("places_visited") or [])
    known.update(_location_refs_from_knowledge(character))
    known.update(_known_people_locations(character))

    start = character.get("location")
    if not start:
        return set()

    graph = build_graph(encodings_data)
    connected = _bfs_reachable(graph, start)
    return known & connected


def shortest_path(graph: dict[str, set[str]], start: str, targets: set[str]) -> tuple[str, list[str]] | None:
    """Multi-source-target BFS: the caller passes whichever target location ids currently count as
    valid (e.g. reachable_set()'s output filtered by whatever need-satisfaction check the caller
    cares about - this function is pure graph math, it has no opinion on what makes a target
    valid). Returns (best_target, full_path_start_to_target_inclusive), or None if no target is
    reachable from `start` at all. Unweighted BFS, per the design conversation - no edge
    weights/distances exist anywhere in this graph, so "best" just means "fewest hops," and BFS's
    own level-order exploration guarantees the first target hit is a nearest one."""
    if not targets:
        return None
    if start not in graph:
        return None
    if start in targets:
        return start, [start]

    visited = {start}
    queue = deque([start])
    parent: dict[str, str] = {}

    while queue:
        current = queue.popleft()
        for neighbor in graph.get(current, ()):
            if neighbor in visited:
                continue
            visited.add(neighbor)
            parent[neighbor] = current
            if neighbor in targets:
                path = [neighbor]
                while path[-1] != start:
                    path.append(parent[path[-1]])
                path.reverse()
                return neighbor, path
            queue.append(neighbor)

    return None


def next_hop(path: list[str]) -> str | None:
    """The very next location id to move toward this pass, i.e. `path[1]` - what a caller uses to
    decide "this pass's routine becomes a transit step toward `next_hop`." None if already at the
    destination (a one-node or empty path)."""
    if path and len(path) > 1:
        return path[1]
    return None


def _demo() -> None:
    """Hardcoded in-memory fixture exercising all four functions - there's no real location/route
    data in _lore/encodings.json yet (fresh-start project ahead of a new simulation), so this is the
    test scaffolding standing in for it until there is."""
    encodings_data = {
        "locations": [
            {"id": "terfila"},
            {"id": "gorff"},
            {"id": "lundria"},
            {"id": "khan_ice"},
            {"id": "isolatia"},  # deliberately unreachable - no route touches it
        ],
        "routes": [
            {"id": "r1", "endpoints": ["terfila", "gorff"]},
            {"id": "r2", "endpoints": ["gorff", "lundria"]},
            # a 3-point route: exercises the "connect every pair" multi-endpoint rule
            {"id": "r3", "endpoints": ["lundria", "khan_ice", "terfila"]},
        ],
    }

    character = {
        "location": "terfila",
        "places_visited": ["gorff"],
        "knowledge": {
            "education": {"items": ["location: khan_ice", "concept: trade"]},
            "experience": [
                "an ungrounded legacy note, no ref here",
                {"text": "heard about a market", "about": "location: lundria"},
                {"text": "no location content", "about": "concept: historiography"},
            ],
        },
        "partners": {"navalius": 3},
        "social_circle": ["ilaria"],
        "parents": [],
    }

    print("=== build_graph ===")
    graph = build_graph(encodings_data)
    for loc_id in sorted(graph):
        print(f"  {loc_id}: {sorted(graph[loc_id])}")
    assert graph["terfila"] == {"gorff", "khan_ice", "lundria"}
    assert graph["lundria"] == {"gorff", "khan_ice", "terfila"}
    assert graph["isolatia"] == set()
    print("  OK: r3's 3 endpoints formed a clique; isolatia has no edges")
    print()

    print("=== reachable_set (with fake partner/social_circle files) ===")
    # navalius is at "khan_ice" (known-and-connected); ilaria is at "isolatia" (known-but-NOT-
    # connected to terfila) - proves the connectivity filter actually excludes it.
    fixtures = {
        "navalius": {"location": "khan_ice"},
        "ilaria": {"location": "isolatia"},
    }
    original_load = _load_character
    globals()["_load_character"] = lambda key: fixtures.get(key)
    try:
        known = reachable_set(character, encodings_data)
    finally:
        globals()["_load_character"] = original_load
    print(f"  {sorted(known)}")
    assert known == {"gorff", "khan_ice", "lundria"}, known
    print("  OK: gorff (places_visited), khan_ice (knowledge + partner loc), lundria (knowledge)")
    print("  OK: isolatia correctly excluded (known-about via ilaria, but not graph-connected)")
    print()

    print("=== shortest_path + next_hop ===")
    result = shortest_path(graph, "terfila", {"lundria"})
    print(f"  terfila -> {{lundria}}: {result}")
    assert result == ("lundria", ["terfila", "lundria"])
    print(f"  next_hop: {next_hop(result[1])}")
    assert next_hop(result[1]) == "lundria"

    result2 = shortest_path(graph, "terfila", {"terfila"})
    print(f"  terfila -> {{terfila}} (already there): {result2}")
    assert next_hop(result2[1]) is None

    result3 = shortest_path(graph, "terfila", {"isolatia"})
    print(f"  terfila -> {{isolatia}} (unreachable): {result3}")
    assert result3 is None
    print("  OK: all path/next_hop cases behave as expected")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--live", action="store_true",
        help="Run build_graph() against the real _lore/encodings.json instead of the demo fixture "
             "(mostly useful once real locations/routes exist; today the arrays are empty).",
    )
    args = parser.parse_args()

    if args.live:
        with open(ENCODINGS_PATH, encoding="utf-8") as f:
            encodings_data = json.load(f)
        graph = build_graph(encodings_data)
        print(f"{len(graph)} location(s) loaded from {ENCODINGS_PATH}")
        for loc_id in sorted(graph):
            print(f"  {loc_id}: {sorted(graph[loc_id])}")
        return

    _demo()


if __name__ == "__main__":
    main()

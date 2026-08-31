"""
Build the two-layer `sources` index across every category encodings.json's own `_categories` block
marks `"has_sources": true` (as of this writing: locations, concepts,
characters.in_world_or_legendary, characters.real_world_authors_and_players - but read from the data,
not hardcoded here, so a category /integrate registers later with `has_sources: true` picks this up
automatically, and a freshly-bootstrapped project with an empty `_categories` block no-ops cleanly
instead of crashing).

Two things happen, both purely mechanical - this script never decides what a claim or tale means,
only where an already-written `about`/`touches` reference resolves to:

1. Migration: every entry's old flat `sources: ["ensayo_i (...)", ...]` shape becomes
   `sources: [{"category": "material", "origin": "ensayo_i (...)"}, ...]` - a literal wrap, no
   parsing, so nothing is lost or misparsed (some source strings, e.g. screenshot provenance notes,
   don't follow a clean "doc (detail)" pattern and can't be split apart reliably).

2. Cross-linking: every `hearsay.entries[].claims[].about` and `tales.entries[].touches` reference
   that resolves to one of the four sourced categories gets folded into that node's `sources` list as
   `{"category": "hearsay"/"tale", "origin": "<hearsay_id>#<claim_n>" / "<tale_id>"}`.
   - An EXACT match (against the entry's `id` or any of its `names[]`, accent/case/underscore-
     insensitive) is linked directly.
   - A NEAR match (difflib ratio >= 0.77, compared only within one category at a time - never a
     location against a character, see the false-positive risk this was built to avoid) is auto-
     grouped rather than left dangling: the unresolved spelling is added to the matched entry's
     `names[]` so it resolves exactly next time, AND a new `conflicts` entry is written - topic
     "possible same-entity spelling, auto-grouped (unconfirmed)" - with `user_resolution` left unset,
     exactly like every other conflict. This script never sets that field; only the user does. The
     grouping takes effect immediately (nothing blocks on it), but it stays visibly provisional until
     someone reviews it.
   - Anything that resolves in more than one category, or fuzzy-matches in zero or more-than-one
     category, is left unresolved and reported - never guessed.

Never touches `conflicts[].user_resolution`, never invents a claim/tale meaning, never edits
`_lore/material/`. See .claude/skills/integrate/SKILL.md for where this runs as a pass.

Also indexes `_lore/grounding/{mechanics,world_state}.json` as a third sourced category, `grounding`,
alongside whatever `_categories` marks `has_sources: true` (added 2026-08-26). This can't reuse
`load_categories()`'s data-driven path resolution, since that only ever reads paths inside
`encodings.json` itself, and grounding deliberately lives outside it (never sampled, never folded in -
see `_lore/grounding/_index.md`) - so `load_grounding()` below does a small, explicit parallel load
instead, in the exact shape `build_index()` already expects, so every downstream resolution function
(`find_exact`, `find_fuzzy`, `resolve_prefixed`, `resolve_bare`) works on it identically with no
further changes. A `hearsay`/`tale` claim can now resolve `about: "grounding: <id>"` the same way it
resolves `about: "location: <id>"`.

Usage:
    py scripts/lore/build_source_index.py            # apply and write encodings.json
    py scripts/lore/build_source_index.py --dry-run  # report only, no write
"""

import argparse
import json
import re
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
ENCODINGS_PATH = ROOT / "_lore" / "encodings.json"
GROUNDING_MECHANICS_PATH = ROOT / "_lore" / "grounding" / "mechanics.json"
GROUNDING_WORLD_STATE_PATH = ROOT / "_lore" / "grounding" / "world_state.json"

FUZZY_THRESHOLD = 0.77

CONFLICT_ID_RE = re.compile(r"^CONFLICT-\d+$")
CHAIN_REF_RE = re.compile(r"^([a-z0-9_]+)#(\d+)$")


def normalize(s: str) -> str:
    """Accent/case/underscore-insensitive form used for exact-match comparison."""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = s.replace("_", " ").lower()
    return re.sub(r"\s+", " ", s).strip()


def _get_path(data: dict, path: str):
    obj = data
    for part in path.split("."):
        obj = obj[part]
    return obj


def load_categories(data: dict) -> dict:
    """Every category encodings.json's own `_categories` block marks `has_sources: true` - not a
    hardcoded list, so this stays correct as new categories get registered (or, on a freshly
    bootstrapped project with no categories yet, simply returns nothing to attach into).

    Only `shape: "list"` categories are handled here - a flat list of dicts, each carrying its own
    `id_field` (see build_index, which reads that instead of assuming a hardcoded "id" key; not
    every category calls its identifier "id" - highways use "code", airports "location", years
    "year"). `"inhabitant"` is `shape: "grouped_list"` (nested `{locality: [people]}`, no flat
    id_field) and is deliberately excluded even though its own `has_sources` is true (corrected
    2026-08-11, on user report - see resolve_touches_path's own named_inhabitants branch for that
    category's real, still-partial handling) - a real generic-list entry per person would be
    needed before this function could safely include it the same way as everything else."""
    if "_categories" not in data:
        raise SystemExit(
            "encodings.json has no '_categories' schema block - run\n"
            "scripts/lore/bootstrap_lore.py or scripts/lore/add_categories_schema.py first."
        )
    return {
        cat_key: _safe_get_path(data, spec["path"], [])
        for cat_key, spec in data["_categories"].items()
        if spec.get("has_sources") and spec.get("shape") == "list"
    }


def migrate_sources(categories: dict, report: dict) -> None:
    for cat_key, entries in categories.items():
        for entry in entries:
            sources = entry.get("sources")
            if not sources:
                continue
            migrated = []
            for s in sources:
                if isinstance(s, str):
                    migrated.append({"category": "material", "origin": s})
                    report["migrated"] += 1
                else:
                    migrated.append(s)  # already migrated, idempotent rerun
            entry["sources"] = migrated


def _safe_get_path(data: dict, path: str, default):
    """Like `_get_path`, but returns `default` instead of raising on a missing key - these
    categories may genuinely not exist yet on a project where /integrate hasn't registered them
    (including a freshly bootstrapped one with none registered at all)."""
    obj = data
    for part in path.split("."):
        if not isinstance(obj, dict) or part not in obj:
            return default
        obj = obj[part]
    return obj


def build_other_known_ids(data: dict) -> set:
    """Normalized ids/names for every category NOT marked `has_sources: true`, used only to tell a
    recognized-but-out-of-scope reference apart from a genuinely dangling one. Tolerant of any of
    these categories not existing yet - they're optional content, not guaranteed scaffolding."""
    known = set()
    for c in data.get("conflicts", []):
        known.add(normalize(c["id"]))
    for e in _safe_get_path(data, "time_systems.ensayo_i_eras", []):
        known.add(normalize(e["name"]))
    for e in _safe_get_path(data, "time_systems.esquema_poster_eras.era_row", []):
        known.add(normalize(e["name"]))
    for e in _safe_get_path(data, "time_systems.esquema_poster_eras.year_by_year_foundations", []):
        known.add(normalize(str(e["year"])))
    for e in _safe_get_path(data, "time_systems.libro_venidas_eras.list", []):
        known.add(normalize(e["name"]))
    for h in _safe_get_path(data, "routes.highways", []):
        known.add(normalize(h["code"]))
        known.add(normalize(h["name"]))
    for t in _safe_get_path(data, "routes.trains.segments", []):
        known.add(normalize(t["name"]))
    for a in _safe_get_path(data, "routes.airports", []):
        known.add(normalize(a["location"]))
    for n in _safe_get_path(data, "routes.named_but_unplotted", []):
        known.add(normalize(n["name"]))
    for locality, people in _safe_get_path(data, "characters.named_inhabitants.by_locality", {}).items():
        known.add(normalize(locality))
        for p in people:
            name = p if isinstance(p, str) else (p.get("name") or "")
            if name:
                known.add(normalize(f"{name} ({locality})"))
                known.add(normalize(name))
    return known


def load_grounding() -> tuple[list, dict | None, dict | None]:
    """Loads _lore/grounding/{mechanics,world_state}.json as one combined 'grounding' category. See
    the module docstring's grounding paragraph for why this can't reuse load_categories(). Returns
    (entries, mechanics_data, world_state_data) - the two data dicts are returned (not just entries)
    so main() can write mutations (attach_source/add_name_if_new act on the entry dicts in place, and
    `entries` holds the same object references, but the file needs its own dict to write back)."""
    entries: list = []
    mechanics_data = None
    world_state_data = None
    if GROUNDING_MECHANICS_PATH.exists():
        with open(GROUNDING_MECHANICS_PATH, encoding="utf-8") as f:
            mechanics_data = json.load(f)
        entries.extend(mechanics_data.get("entries", []))
    if GROUNDING_WORLD_STATE_PATH.exists():
        with open(GROUNDING_WORLD_STATE_PATH, encoding="utf-8") as f:
            world_state_data = json.load(f)
        entries.extend(world_state_data.get("entries", []))
    return entries, mechanics_data, world_state_data


def build_index(categories: dict, specs: dict) -> list:
    """One record per entry: (category, entry, {normalized keys: display form}).

    Reads each category's own `id_field` from `_categories` (`specs`) instead of assuming every
    entry calls its identifier "id" - corrected 2026-08-11, on user report: `concept`/`location`
    both happen to use "id", but `highway` uses "code", `airport` "location", `year_esquema`
    "year" (an int - stringified before normalizing), etc. Assuming "id" universally would have
    KeyError'd the instant a non-concept/location category's `has_sources` flag actually got used."""
    index = []
    for cat_key, entries in categories.items():
        id_field = specs.get(cat_key, {}).get("id_field") or "id"
        for entry in entries:
            entry_id = str(entry[id_field])
            keys = {normalize(entry_id): entry_id}
            for n in entry.get("names", []):
                keys[normalize(n)] = n
            index.append((cat_key, entry, keys))
    return index


def find_exact(value: str, index: list, category_hint: str = None) -> list:
    target = normalize(value)
    hits = []
    for cat_key, entry, keys in index:
        if category_hint and cat_key != category_hint:
            continue
        if target in keys:
            hits.append((cat_key, entry))
    return hits


def find_fuzzy(value: str, index: list, category_hint: str = None):
    """Best match per category (score, cat_key, entry, matched_display_name). Returns the list of
    categories whose best score clears FUZZY_THRESHOLD - caller decides what to do with >1."""
    target = normalize(value)
    best_per_category = {}
    for cat_key, entry, keys in index:
        if category_hint and cat_key != category_hint:
            continue
        for norm_key, display in keys.items():
            score = SequenceMatcher(None, target, norm_key).ratio()
            cur = best_per_category.get(cat_key)
            if cur is None or score > cur[0]:
                best_per_category[cat_key] = (score, entry, display)
    qualifying = [
        (cat_key, score, entry, display)
        for cat_key, (score, entry, display) in best_per_category.items()
        if score >= FUZZY_THRESHOLD
    ]
    return qualifying


def next_conflict_id(data: dict) -> str:
    nums = [int(c["id"].split("-")[1]) for c in data["conflicts"] if c["id"].startswith("CONFLICT-")]
    return f"CONFLICT-{max(nums) + 1 if nums else 1}"


def attach_source(entry: dict, category: str, origin: str) -> bool:
    entry.setdefault("sources", [])
    for s in entry["sources"]:
        if isinstance(s, dict) and s.get("category") == category and s.get("origin") == origin:
            return False  # already attached, idempotent rerun
    entry["sources"].append({"category": category, "origin": origin})
    return True


def add_name_if_new(entry: dict, raw_name: str) -> bool:
    entry.setdefault("names", [])
    if normalize(raw_name) in {normalize(n) for n in entry["names"]}:
        return False
    entry["names"].append(raw_name)
    return True


def resolve_prefixed(prefix: str, value: str, index: list, sourced_keys: set):
    """Returns ('scope', ...) tuple: 'attach' (category, entry, exact_or_fuzzy, score, display),
    'out_of_scope', or 'unresolved'. Driven entirely by `sourced_keys` (every category key with
    `has_sources: true` in encodings.json's own `_categories` block) rather than a hardcoded prefix
    list - corrected 2026-08-11, on user report ("if something was said by someone, it means there
    is a source, and that source is hearsay"): this function used to only ever attempt `concept`/
    `location`/`character` prefixes, silently routing every other prefix (`era_ensayo`,
    `conflict`, `inhabitant`, `highway`, ...) to `out_of_scope` regardless of what `has_sources`
    said - the flag alone was never sufficient, this is the other half of that fix."""
    if prefix == "character":
        exact = find_exact(value, index, "character_legendary") + find_exact(value, index, "character_real")
        if len(exact) == 1:
            return ("attach", exact[0][0], exact[0][1], "exact", 1.0, value)
        return ("unresolved", None, None, None, None, None)
    if prefix in sourced_keys:
        exact = find_exact(value, index, prefix)
        if len(exact) == 1:
            return ("attach", exact[0][0], exact[0][1], "exact", 1.0, value)
        if len(exact) > 1:
            return ("unresolved", None, None, None, None, None)
        fuzzy = find_fuzzy(value, index, prefix)
        if len(fuzzy) == 1:
            cat_key, score, entry, _ = fuzzy[0]
            return ("attach", cat_key, entry, "fuzzy", score, value)
        return ("unresolved", None, None, None, None, None)
    return ("out_of_scope", None, None, None, None, None)


def resolve_bare(value: str, index: list, other_known: set):
    exact = find_exact(value, index)
    if len(exact) == 1:
        return ("attach", exact[0][0], exact[0][1], "exact", 1.0, value)
    if len(exact) > 1:
        # Default to "location" on a tie (added 2026-08-11, on user direction) - a bare,
        # unprefixed about-reference is overwhelmingly a place name in practice, and several
        # locations double as an airport of the same name (City B, City F, City D
        # Moshin...), which is what actually produces these ties. Only ties involving exactly one
        # location candidate get resolved this way - a genuine ambiguity between two non-location
        # categories, or two location candidates, still goes unresolved rather than guessed.
        location_hits = [h for h in exact if h[0] == "location"]
        if len(location_hits) == 1:
            return ("attach", location_hits[0][0], location_hits[0][1], "exact", 1.0, value)
        return ("unresolved", None, None, None, None, None)
    if normalize(value) in other_known:
        return ("out_of_scope", None, None, None, None, None)
    fuzzy = find_fuzzy(value, index)
    if len(fuzzy) == 1:
        cat_key, score, entry, _ = fuzzy[0]
        return ("attach", cat_key, entry, "fuzzy", score, value)
    return ("unresolved", None, None, None, None, None)


def resolve_touches_path(value: str, index: list, other_known: set):
    parts = value.split(".")
    head = parts[0]
    rest = ".".join(parts[1:])
    if head == "concepts":
        exact = find_exact(rest, index, "concept")
        if len(exact) == 1:
            return ("attach", exact[0][0], exact[0][1], "exact", 1.0, rest)
        return ("unresolved", None, None, None, None, None)
    if head == "locations":
        exact = find_exact(rest, index, "location")
        if len(exact) == 1:
            return ("attach", exact[0][0], exact[0][1], "exact", 1.0, rest)
        return ("unresolved", None, None, None, None, None)
    if head == "characters":
        # e.g. "named_inhabitants.by_locality.City A (Census Role, Character K)" - no `sources` field
        # on named_inhabitants entries yet; recognize and skip rather than report as dangling.
        locality_field = rest.split(" (")[0].split(".")[-1]
        if normalize(locality_field) in other_known or normalize(rest) in other_known:
            return ("out_of_scope", None, None, None, None, None)
        return ("unresolved", None, None, None, None, None)
    return resolve_bare(value, index, other_known)


def resolve_ref(raw: str, index: list, other_known: set, hearsay_ids: set, sourced_keys: set):
    s = raw.strip()
    if CONFLICT_ID_RE.match(s):
        return ("out_of_scope", None, None, None, None, None)
    m = CHAIN_REF_RE.match(s)
    if m and m.group(1) in hearsay_ids:
        return ("out_of_scope", None, None, None, None, None)  # inter-claim chain ref, not a node
    if ": " in s:
        prefix, value = s.split(": ", 1)
        return resolve_prefixed(prefix.strip().lower(), value.strip(), index, sourced_keys)
    if "." in s and s.split(".", 1)[0] in ("concepts", "locations", "characters"):
        return resolve_touches_path(s, index, other_known)
    return resolve_bare(s, index, other_known)


def process_refs(data: dict, index: list, other_known: set, hearsay_ids: set, sourced_keys: set, specs: dict, report: dict) -> None:
    def handle(raw: str, origin_category: str, origin: str, source_label: str):
        if not raw:
            return
        status, cat_key, entry, match_kind, score, display = resolve_ref(raw, index, other_known, hearsay_ids, sourced_keys)
        if status == "out_of_scope":
            return
        if status == "unresolved":
            report["unresolved"].append((source_label, raw))
            return
        # status == "attach"
        if match_kind == "fuzzy":
            add_name_if_new(entry, display)  # `display` is the resolved candidate value, not the matched entry's own name
            id_field = specs.get(cat_key, {}).get("id_field") or "id"
            entry_id = str(entry[id_field])
            conflict_id = next_conflict_id(data)
            data["conflicts"].append({
                "id": conflict_id,
                "topic": "possible same-entity spelling, auto-grouped (unconfirmed)",
                "detail": (
                    f"'{raw}' (from {source_label}) auto-grouped with existing {cat_key} "
                    f"'{entry_id}' at similarity {score:.2f} (threshold {FUZZY_THRESHOLD}) via "
                    f"build_source_index.py. Unconfirmed - needs user review."
                ),
            })
            report["fuzzy_grouped"].append((source_label, raw, entry_id, round(score, 2), conflict_id))
        did_attach = attach_source(entry, origin_category, origin)
        if did_attach:
            report["linked"] += 1

    for e in data["hearsay"]["entries"]:
        for i, claim in enumerate(e["claims"], start=1):
            origin = f"{e['id']}#{i}"
            about = claim.get("about")
            values = about if isinstance(about, list) else ([about] if about else [])
            for v in values:
                handle(v, "hearsay", origin, f"hearsay:{origin}")

    for t in data["tales"]["entries"]:
        for touches in t.get("touches", []):
            handle(touches, "tale", t["id"], f"tale:{t['id']}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true", help="Report only, do not write encodings.json")
    args = parser.parse_args()

    with open(ENCODINGS_PATH, encoding="utf-8") as f:
        data = json.load(f)

    categories = load_categories(data)
    report = {"migrated": 0, "linked": 0, "fuzzy_grouped": [], "unresolved": []}

    migrate_sources(categories, report)
    other_known = build_other_known_ids(data)
    hearsay_ids = {e["id"] for e in data["hearsay"]["entries"]}
    specs = data["_categories"]
    index = build_index(categories, specs)

    grounding_entries, mechanics_data, world_state_data = load_grounding()
    if grounding_entries:
        migrate_sources({"grounding": grounding_entries}, report)
        index += build_index({"grounding": grounding_entries}, specs)

    sourced_keys = set(categories.keys()) | ({"grounding"} if grounding_entries else set())
    process_refs(data, index, other_known, hearsay_ids, sourced_keys, specs, report)

    print(f"Migrated source strings to {{category, origin}}: {report['migrated']}")
    print(f"Newly linked hearsay/tale sources: {report['linked']}")
    print(f"Fuzzy auto-groupings (new CONFLICT entries): {len(report['fuzzy_grouped'])}")
    for source_label, raw, matched_id, score, conflict_id in report["fuzzy_grouped"]:
        print(f"  {conflict_id}: {source_label} '{raw}' -> '{matched_id}' (score {score})")
    print(f"Unresolved references (need human judgment): {len(report['unresolved'])}")
    for source_label, raw in report["unresolved"]:
        print(f"  {source_label}: '{raw}'")

    if args.dry_run:
        print("\n--dry-run: no changes written.")
        return

    with open(ENCODINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\nWrote {ENCODINGS_PATH}")

    if mechanics_data is not None:
        with open(GROUNDING_MECHANICS_PATH, "w", encoding="utf-8") as f:
            json.dump(mechanics_data, f, indent=2, ensure_ascii=False)
        print(f"Wrote {GROUNDING_MECHANICS_PATH}")
    if world_state_data is not None:
        with open(GROUNDING_WORLD_STATE_PATH, "w", encoding="utf-8") as f:
            json.dump(world_state_data, f, indent=2, ensure_ascii=False)
        print(f"Wrote {GROUNDING_WORLD_STATE_PATH}")


if __name__ == "__main__":
    main()

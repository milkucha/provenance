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
    bootstrapped project with no categories yet, simply returns nothing to attach into)."""
    if "_categories" not in data:
        raise SystemExit(
            "encodings.json has no '_categories' schema block - run\n"
            "scripts/lore/bootstrap_lore.py or scripts/lore/add_categories_schema.py first."
        )
    return {
        cat_key: _get_path(data, spec["path"])
        for cat_key, spec in data["_categories"].items()
        if spec.get("has_sources")
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


def build_index(categories: dict) -> list:
    """One record per entry: (category, entry, {normalized keys: display form})."""
    index = []
    for cat_key, entries in categories.items():
        for entry in entries:
            keys = {normalize(entry["id"]): entry["id"]}
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


def resolve_prefixed(prefix: str, value: str, index: list):
    """Returns ('scope', ...) tuple: 'attach' (category, entry, exact_or_fuzzy, score, display),
    'out_of_scope', or 'unresolved'."""
    prefix_map = {
        "concept": "concept",
        "location": "location",
    }
    if prefix in prefix_map:
        cat_hint = prefix_map[prefix]
        exact = find_exact(value, index, cat_hint)
        if len(exact) == 1:
            return ("attach", exact[0][0], exact[0][1], "exact", 1.0, value)
        if len(exact) > 1:
            return ("unresolved", None, None, None, None, None)
        fuzzy = find_fuzzy(value, index, cat_hint)
        if len(fuzzy) == 1:
            cat_key, score, entry, _ = fuzzy[0]
            return ("attach", cat_key, entry, "fuzzy", score, value)
        return ("unresolved", None, None, None, None, None)
    if prefix == "character":
        exact = find_exact(value, index) if False else (
            find_exact(value, index, "character_legendary") + find_exact(value, index, "character_real")
        )
        if len(exact) == 1:
            return ("attach", exact[0][0], exact[0][1], "exact", 1.0, value)
        return ("unresolved" if not exact else "unresolved", None, None, None, None, None)
    # era_ensayo / era_esquema / era_libro / year_esquema / highway / train / airport / route / etc.
    return ("out_of_scope", None, None, None, None, None)


def resolve_bare(value: str, index: list, other_known: set):
    exact = find_exact(value, index)
    if len(exact) == 1:
        return ("attach", exact[0][0], exact[0][1], "exact", 1.0, value)
    if len(exact) > 1:
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
        # e.g. "named_inhabitants.by_locality.Terfila (Peregrin, Zarkapulos)" - no `sources` field
        # on named_inhabitants entries yet; recognize and skip rather than report as dangling.
        locality_field = rest.split(" (")[0].split(".")[-1]
        if normalize(locality_field) in other_known or normalize(rest) in other_known:
            return ("out_of_scope", None, None, None, None, None)
        return ("unresolved", None, None, None, None, None)
    return resolve_bare(value, index, other_known)


def resolve_ref(raw: str, index: list, other_known: set, hearsay_ids: set):
    s = raw.strip()
    if CONFLICT_ID_RE.match(s):
        return ("out_of_scope", None, None, None, None, None)
    m = CHAIN_REF_RE.match(s)
    if m and m.group(1) in hearsay_ids:
        return ("out_of_scope", None, None, None, None, None)  # inter-claim chain ref, not a node
    if ": " in s:
        prefix, value = s.split(": ", 1)
        return resolve_prefixed(prefix.strip().lower(), value.strip(), index)
    if "." in s and s.split(".", 1)[0] in ("concepts", "locations", "characters"):
        return resolve_touches_path(s, index, other_known)
    return resolve_bare(s, index, other_known)


def process_refs(data: dict, index: list, other_known: set, hearsay_ids: set, report: dict) -> None:
    def handle(raw: str, origin_category: str, origin: str, source_label: str):
        if not raw:
            return
        status, cat_key, entry, match_kind, score, display = resolve_ref(raw, index, other_known, hearsay_ids)
        if status == "out_of_scope":
            return
        if status == "unresolved":
            report["unresolved"].append((source_label, raw))
            return
        # status == "attach"
        if match_kind == "fuzzy":
            add_name_if_new(entry, display)  # `display` is the resolved candidate value, not the matched entry's own name
            conflict_id = next_conflict_id(data)
            data["conflicts"].append({
                "id": conflict_id,
                "topic": "possible same-entity spelling, auto-grouped (unconfirmed)",
                "detail": (
                    f"'{raw}' (from {source_label}) auto-grouped with existing {cat_key} "
                    f"'{entry['id']}' at similarity {score:.2f} (threshold {FUZZY_THRESHOLD}) via "
                    f"build_source_index.py. Unconfirmed - needs user review."
                ),
            })
            report["fuzzy_grouped"].append((source_label, raw, entry["id"], round(score, 2), conflict_id))
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
    index = build_index(categories)
    process_refs(data, index, other_known, hearsay_ids, report)

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


if __name__ == "__main__":
    main()

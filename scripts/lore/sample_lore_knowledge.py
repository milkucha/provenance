"""
Draw a bounded knowledge sample for an enacted character from _lore/encodings.json.

Used by the /enact skill (.claude/skills/enact/SKILL.md) and documented in README.md §8.
Every atomic fact in encodings.json (locations, concepts, conflicts, characters, routes, eras...)
is flattened into one pool. Sampling from that pool, rather than hand-picking, is the whole point:
it produces a character with real, uneven gaps instead of a curated highlight reel.

Individual hearsay claims (encodings.json -> hearsay.entries[].claims) are flattened into the same
pool as their own "hearsay" category items, one per claim, sitting at equal odds alongside every
objective-record fact. This is deliberate: a claim another NPC once made in a dialogue can become
part of a new character's knowledge exactly as if they'd heard it secondhand - which is how rumor
and half-remembered gossip actually spread, and how the lore is meant to accrete new, emergent
"fact-shaped" material over time on top of the fixed objective record. A "hearsay" item is NOT
upgraded to objective truth by being sampled - the character knows it only as something claimed by
someone, in some dialogue, possibly wrong. Play it that way: attributed ("I heard Gondarfolas say
once that..."), not asserted as settled history.

NOT sampled, ever: _lore/facts/facts.json. Facts are the handful of things true of being a person in
this world at all (life ends; a life should be worthwhile) - every character knows every one of them
in full, regardless of their education percentage, so drawing them at 5% odds would be a bug. They
live outside encodings.json on purpose and must never be folded into it; /enact loads them
separately. See _lore/facts/_index.md.

The set of categories is read from encodings.json's own `_categories` block, not hardcoded here (see
that key's `_categories_method_note` for the shape convention) - this is what lets /integrate register
a genuinely new category (new material that doesn't fit the existing schema) without a code change,
as long as it follows the common "list" shape. A structurally novel shape still needs a new function
added to SHAPE_HANDLERS below by hand; this script raises rather than silently skipping one it doesn't
recognize.

Usage:
    python scripts/lore/sample_lore_knowledge.py --percent 11 --mode random
    python scripts/lore/sample_lore_knowledge.py --percent 21 --mode skewed --topic geography --topic geology
    python scripts/lore/sample_lore_knowledge.py --percent 5 --mode random --seed 42   # reproducible draw
"""

import argparse
import json
from pathlib import Path
from random import Random

ROOT = Path(__file__).resolve().parent.parent.parent
ENCODINGS_PATH = ROOT / "_lore" / "encodings.json"


def _get_path(data: dict, path: str):
    obj = data
    for part in path.split("."):
        obj = obj[part]
    return obj


def _normalize_field(value):
    """A list-valued field (e.g. 'names', 'places') is joined into one string rather than passed
    through raw - `add()`'s own join would otherwise stringify the whole list as a Python repr
    ("['Vortex', ...]"), which still keyword-matches but is noisier than it needs to be. 'text' is
    never shown to a user, only substring-matched for --mode skewed, so this is a pure cleanup."""
    if isinstance(value, list):
        return " ".join(str(v) for v in value)
    return value


def _flatten_list(data: dict, cat_key: str, spec: dict, add) -> None:
    """Default shape: a flat list of dicts at `spec['path']`, identified by `spec['id_field']`,
    pool text built by joining `spec['text_fields']`. Covers every category added so far except the
    two special-cased below."""
    id_field = spec["id_field"]
    for entry in _get_path(data, spec["path"]):
        item_id = entry[id_field]
        if not isinstance(item_id, str):
            item_id = str(item_id)
        add(cat_key, item_id, *(_normalize_field(entry.get(f)) for f in spec["text_fields"]))


def _flatten_grouped_list(data: dict, cat_key: str, spec: dict, add) -> None:
    """Special-cased: characters.named_inhabitants.by_locality - a dict keyed by locality, values are
    lists of bare strings or small {name, role/route} dicts. Not a flat list, so it can't use the
    default handler."""
    for locality, people in _get_path(data, spec["path"]).items():
        for p in people:
            if isinstance(p, str):
                name, role = p, ""
            else:
                name = p.get("name") or f"the {p.get('role', 'unnamed')}"
                role = str(p.get("role") or p.get("route") or "")
            add(cat_key, f"{name} ({locality})", name, locality, role)


def _flatten_claims(data: dict, cat_key: str, spec: dict, add) -> None:
    """Special-cased: hearsay.entries[].claims - one pool item per claim, not per entry, so it can't
    use the default handler either."""
    for entry in _get_path(data, spec["path"]):
        participants = " ".join(entry.get("participants", []))
        location = (entry.get("location") or {}).get("as_named_in_dialog")
        for i, claim in enumerate(entry["claims"], start=1):
            add(cat_key, f"{entry['id']}#{i}", claim.get("text"), participants, location)


SHAPE_HANDLERS = {
    "list": _flatten_list,
    "grouped_list": _flatten_grouped_list,
    "claims": _flatten_claims,
}


def flatten_pool(data: dict) -> list[dict]:
    """Every atomic fact in encodings.json, as {category, id, text} dicts. 'text' is a loose
    bag of words used only for --mode skewed keyword matching, not shown to the user."""
    pool: list[dict] = []

    if "facts" in data:
        raise SystemExit(
            "encodings.json contains a 'facts' key. Facts are universal knowledge and must never be\n"
            "sampled - every character knows all of them in full. Move them back to\n"
            "_lore/facts/facts.json and out of encodings.json. See _lore/facts/_index.md."
        )
    if "_categories" not in data:
        raise SystemExit(
            "encodings.json has no '_categories' schema block - run\n"
            "scripts/lore/add_categories_schema.py before sampling."
        )

    def add(category: str, item_id: str, *text_parts) -> None:
        text = " ".join(str(p) for p in text_parts if p)
        pool.append({"category": category, "id": item_id, "text": text})

    for cat_key, spec in data["_categories"].items():
        handler = SHAPE_HANDLERS.get(spec["shape"])
        if handler is None:
            raise SystemExit(
                f"Category '{cat_key}' declares shape '{spec['shape']}', which has no handler in "
                f"SHAPE_HANDLERS. Add one before sampling - never silently skip a registered category."
            )
        handler(data, cat_key, spec, add)

    return pool


def draw_sample(pool: list[dict], percent: float, mode: str, topics: list[str], rng: Random) -> list[dict]:
    n = max(1, round(len(pool) * percent / 100))

    if mode == "random" or not topics:
        return rng.sample(pool, n)

    keywords = [t.lower() for t in topics]
    matching = [p for p in pool if any(k in (p["id"] + " " + p["text"]).lower() for k in keywords)]
    rest = [p for p in pool if p not in matching]

    take_matching = min(n, len(matching))
    sample = rng.sample(matching, take_matching)
    remaining = n - take_matching
    if remaining > 0:
        sample += rng.sample(rest, min(remaining, len(rest)))
    rng.shuffle(sample)
    return sample


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--percent", type=float, required=True, help="Percent of the pool to draw, e.g. 11")
    parser.add_argument("--mode", choices=["random", "skewed"], default="random")
    parser.add_argument("--topic", action="append", default=[], help="Keyword to skew toward (only with --mode skewed; repeatable)")
    parser.add_argument("--seed", type=int, default=None, help="Optional seed, for a reproducible draw")
    args = parser.parse_args()

    if args.mode == "skewed" and not args.topic:
        parser.error("--mode skewed requires at least one --topic")

    rng = Random(args.seed)

    with open(ENCODINGS_PATH, encoding="utf-8") as f:
        data = json.load(f)

    pool = flatten_pool(data)
    sample = draw_sample(pool, args.percent, args.mode, args.topic, rng)

    print(f"Pool size: {len(pool)}")
    print(f"Sample size ({args.percent:.0f}%): {len(sample)}")
    if args.mode == "skewed":
        print(f"Skewed toward: {', '.join(args.topic)}")
    print()
    for item in sorted(sample, key=lambda p: (p["category"], p["id"])):
        print(f"{item['category']}: {item['id']}")


if __name__ == "__main__":
    main()

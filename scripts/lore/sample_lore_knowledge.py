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

    def add(category: str, item_id: str, *text_parts) -> None:
        text = " ".join(str(p) for p in text_parts if p)
        pool.append({"category": category, "id": item_id, "text": text})

    for loc in data["locations"]:
        add("location", loc["id"], loc.get("names"), loc.get("region"), loc.get("type_catastro"), loc.get("notes"))
    for c in data["concepts"]:
        add("concept", c["id"], c.get("names"), c.get("description"), c.get("notes"))
    for c in data["conflicts"]:
        add("conflict", c["id"], c.get("topic"), c.get("detail"))
    for c in data["characters"]["in_world_or_legendary"]:
        add("character_legendary", c["id"], c.get("names"), c.get("role"), c.get("notes"))
    for c in data["characters"]["real_world_authors_and_players"]:
        add("character_real", c["id"], c.get("names"), c.get("role"))
    for locality, people in data["characters"]["named_inhabitants"]["by_locality"].items():
        for p in people:
            if isinstance(p, str):
                name, role = p, ""
            else:
                name = p.get("name") or f"the {p.get('role', 'unnamed')}"
                role = str(p.get("role") or p.get("route") or "")
            add("inhabitant", f"{name} ({locality})", name, locality, role)
    for h in data["routes"]["highways"]:
        add("highway", h["code"], h["name"])
    for t in data["routes"]["trains"]["segments"]:
        add("train_segment", t["name"], t["name"])
    for a in data["routes"]["airports"]:
        add("airport", a["location"], a["location"])
    for n in data["routes"]["named_but_unplotted"]:
        add("route_named", n["name"], n["name"])
    for e in data["time_systems"]["ensayo_i_eras"]:
        add("era_ensayo", e["name"], e["name"])
    for e in data["time_systems"]["esquema_poster_eras"]["era_row"]:
        add("era_esquema", e["name"], e["name"])
    for e in data["time_systems"]["esquema_poster_eras"]["year_by_year_foundations"]:
        add("year_esquema", str(e["year"]), " ".join(e.get("places", [])))
    for e in data["time_systems"]["libro_venidas_eras"]["list"]:
        add("era_libro", e["name"], e["name"])
    for entry in data["hearsay"]["entries"]:
        participants = " ".join(entry.get("participants", []))
        location = (entry.get("location") or {}).get("as_named_in_dialog")
        for i, claim in enumerate(entry["claims"], start=1):
            add("hearsay", f"{entry['id']}#{i}", claim.get("text"), participants, location)

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

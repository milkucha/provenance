"""
Generate a new character as a genuine mutation of two parents - design debrief 2026-08-10. Not an
average: every inherited field is either copied whole from a randomly-chosen parent, or drawn as a
random-sized random subset of the union of both parents' pools. Which specific combination a given
child ends up with is itself the randomness - two agreeing parents can still produce a child who
inherits one's `standard` and the other's `distrusts`, a combination neither parent would have
authored, without any text being freely invented to make it happen.

What's inherited and how:
- `criterion.standard` / `wasted_life` / `anchor` / `trusts` / `distrusts` - each field
  independently coin-flipped to one parent's exact value. `origin` is set to "inherited" (a new
  value, distinct from "derived"/"uncollided") so this is visibly not a fresh Step 4 derivation.
  `tempered`, `cost_ledger`, `history` all start empty - nothing has tested this criterion yet.
- `knowledge.education.items` - a random-sized random subset of the UNION of both parents' items
  (not a fixed fraction - the sample size itself is randomized). `percent`/`mode`/`topic` copied
  whole from a coin-flipped parent, since those describe how the sample was drawn, not its content.
- `knowledge.experience` - starts empty. The child hasn't lived either parent's experiences; this
  is deliberately NOT inherited, only the factual education pool is.
- `routines` - a random-sized random subset of the union of both parents' routine entries, weights
  renormalized to sum to 100. Still a placeholder in the sense that routines are meant to be
  hand-authored (see _lore/archetypes.json) - there's no author present mid-run, so this is the
  honest fallback, not a substitute for eventually hand-revising a child's routines.
- `arc` - none at birth. Seeded the normal way (archetype + specialization + criterion) the first
  time this character is actually a scene's home_frame, same as any character.
- `city` - copied whole from a coin-flipped parent.
- `backstory` - deliberately minimal and factual ("Child of X and Y."), not invented prose. Left
  open for a human/`/character` session to enrich later, same as any other placeholder in this
  system that's honest about being unfinished rather than papering over it.
- `life.span` - freshly rolled via the same range as any character (_lore/tuning.json's
  lifespan_range - not inherited from either parent) - open question left in the original design
  sketch, resolved here as "fresh roll" rather than "heritable trait" for now.

Cooldowns (both from _lore/tuning.json, and deliberately distinct from each other): a **parent**
can't reproduce again for `parent_cooldown_passes` (checked by the caller before this script ever
runs, using `last_reproduced_pass` this script writes) - this stays separate from how soon the
**child** themselves enters `pick_pair.py`'s pool, `child_cooldown_passes` after `birth_pass`
(printed by this script, so the caller never needs to duplicate the number).

Who learns of it, mirroring record_death.py's own circle-notification pattern (per the original
design sketch: "the parents' circles get told immediately, so others know them before they know
them"):
- Both **parents** get a plain `knowledge.experience` line recording the birth directly - this was
  missing from the first version of this script and is not optional; the two people it happened to
  are not "circle" members, they're the event itself.
- The **circle** - reusing notify_death.py's own logic, unioned across both parents (everyone
  either parent has shared a scene with, or is named in either parent's backstory), minus the
  parents and the child themselves - gets the same 30%-sampled, immediate-notification treatment
  a death gets. Everyone else outside that 30% may still hear later the ordinary way (a future
  hearsay draw), same as death's own "remainder" tier.

What this script deliberately does NOT decide: the child's **name**. That's the one place in this
whole mechanism where a model's judgment is the right tool, not a dice roll - composing a name that
reads as a plausible blend of both parents' names isn't something word-overlap or random sampling
can do coherently. Pass the model-composed name in with --name (see roll_reproduction.py's
`name_lead` output for the one piece of that decision that IS dice-driven - which parent's name
leads the blend). The slug is derived from --name automatically (same convention as
record_death.py's own slugify), not a second thing the caller has to decide separately.

Usage:
    py scripts/lore/generate_offspring.py --parent-a khaoe --parent-b gondarfolas \\
        --name "Khordarel" --pass-number 63
"""

import argparse
import json
import random
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import notify_death  # noqa: E402  (sibling module, sys.path adjusted above)
import tuning  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent.parent
CHAR_DIR = ROOT / "_lore" / "characters"
LIFESPANS_PATH = CHAR_DIR / "lifespans.json"
_TUNING = tuning.load()
SPAN_MIN, SPAN_MAX = _TUNING["lifespan_range"]["min"], _TUNING["lifespan_range"]["max"]
CHILD_COOLDOWN_PASSES = _TUNING["child_cooldown_passes"]


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return "_".join(words)


def load_char(key: str) -> dict:
    path = CHAR_DIR / f"{key}.json"
    if not path.exists():
        raise SystemExit(f"No character file for '{key}'.")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_char(key: str, character: dict) -> None:
    path = CHAR_DIR / f"{key}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(character, f, indent=2, ensure_ascii=False)
        f.write("\n")


def coin(a, b):
    return random.choice([a, b])


def sample_union(pool_a: list, pool_b: list) -> list:
    union = list(dict.fromkeys(pool_a + pool_b))  # de-duplicated, order-preserving
    if not union:
        return []
    size = random.randint(1, len(union))
    return random.sample(union, size)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--parent-a", required=True)
    parser.add_argument("--parent-b", required=True)
    parser.add_argument("--name", required=True, help="Model-composed name blend - the one judgment call this script doesn't make")
    parser.add_argument("--pass-number", type=int, required=True, help="Current /simulate pass number, recorded as birth_pass and on both parents as last_reproduced_pass")
    parser.add_argument("--seed", type=int, default=None, help="Also seeds the circle-notification sample")
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    a_key, b_key = args.parent_a.lower(), args.parent_b.lower()
    parent_a, parent_b = load_char(a_key), load_char(b_key)
    key = slugify(args.name)
    base_key, n = key, 2
    while (CHAR_DIR / f"{key}.json").exists():
        key = f"{base_key}_{n}"
        n += 1

    edu_a = parent_a.get("knowledge", {}).get("education", {})
    edu_b = parent_b.get("knowledge", {}).get("education", {})
    edu_source = coin(edu_a, edu_b)
    items = sample_union(edu_a.get("items", []), edu_b.get("items", []))

    crit_a = parent_a.get("criterion", {})
    crit_b = parent_b.get("criterion", {})
    criterion = {
        "standard": coin(crit_a.get("standard", ""), crit_b.get("standard", "")),
        "wasted_life": coin(crit_a.get("wasted_life", ""), crit_b.get("wasted_life", "")),
        "anchor": coin(crit_a.get("anchor", ""), crit_b.get("anchor", "")),
        "origin": "inherited",
        "trusts": coin(crit_a.get("trusts", ""), crit_b.get("trusts", "")),
        "distrusts": coin(crit_a.get("distrusts", ""), crit_b.get("distrusts", "")),
        "tempered": 0,
        "cost_ledger": [],
        "history": [],
    }

    routines_pool_a = parent_a.get("routines", [])
    routines_pool_b = parent_b.get("routines", [])
    routines = sample_union(
        [json.dumps(r, sort_keys=True) for r in routines_pool_a],
        [json.dumps(r, sort_keys=True) for r in routines_pool_b],
    )
    routines = [json.loads(r) for r in routines]
    if routines:
        equal_weight = round(100 / len(routines), 2)
        for r in routines:
            r["weight"] = equal_weight

    span = random.randint(SPAN_MIN, SPAN_MAX)
    name_a, name_b = parent_a.get("name", a_key), parent_b.get("name", b_key)

    child = {
        "name": args.name,
        "city": coin(parent_a.get("city", ""), parent_b.get("city", "")),
        "backstory": f"Child of {name_a} and {name_b}.",
        "knowledge": {
            "education": {
                "percent": edu_source.get("percent"),
                "mode": edu_source.get("mode"),
                "topic": edu_source.get("topic"),
                "items": items,
            },
            "experience": [],
        },
        "criterion": criterion,
        "life": {"lived": 0, "deceased": False},
        "routines": routines,
        "parents": [a_key, b_key],
        "birth_pass": args.pass_number,
    }
    save_char(key, child)

    with open(LIFESPANS_PATH, encoding="utf-8") as f:
        lifespans_doc = json.load(f)
    lifespans_doc["lifespans"][key] = {"span": span, "range": f"{SPAN_MIN}-{SPAN_MAX}"}
    with open(LIFESPANS_PATH, "w", encoding="utf-8") as f:
        json.dump(lifespans_doc, f, indent=2, ensure_ascii=False)
        f.write("\n")

    # Parents: not circle members, the event itself - always notified, no sampling.
    for parent_key, parent_char, other_name in ((a_key, parent_a, name_b), (b_key, parent_b, name_a)):
        parent_char["last_reproduced_pass"] = args.pass_number
        parent_char.setdefault("knowledge", {}).setdefault("experience", [])
        parent_char["knowledge"]["experience"].append(f"Had a child with {other_name}, named {args.name}.")
        save_char(parent_key, parent_char)

    # Circle: reuse notify_death.py's own logic, unioned across both parents.
    characters, enc = notify_death.load()
    entries = enc["hearsay"]["entries"]
    name_to_key = notify_death.name_to_key_map(characters)

    circle_keys = set()
    for parent_name in (name_a, name_b):
        for _scene_id, others in notify_death.scene_participants_of(parent_name, entries):
            for other_name in others:
                k = name_to_key.get(other_name.lower())
                if k and k not in (a_key, b_key):
                    circle_keys.add(k)
    for other_key, other_char in characters.items():
        if other_key in (a_key, b_key):
            continue
        backstory = (other_char.get("backstory") or "").lower()
        if name_a.lower() in backstory or name_b.lower() in backstory:
            circle_keys.add(other_key)

    circle = sorted(circle_keys)
    n_notify = 0 if not circle else max(1, round(0.30 * len(circle)))
    from random import Random
    rng = Random(args.seed)
    notified = sorted(rng.sample(circle, n_notify)) if n_notify else []

    for k in notified:
        notified_char = load_char(k)
        notified_char.setdefault("knowledge", {}).setdefault("experience", [])
        notified_char["knowledge"]["experience"].append(
            f"Heard that {name_a} and {name_b} now have a child, {args.name}."
        )
        save_char(k, notified_char)

    print(f"born: {key} ({args.name})")
    print(f"parents: {a_key}, {b_key}  (last_reproduced_pass = {args.pass_number} on both, both notified directly)")
    print(f"circle size: {len(circle)}  ->  notified {len(notified)} (30%)")
    for k in notified:
        print(f"  notified: {k}")
    if circle and not notified:
        print("  (circle non-empty but sample came back empty - shouldn't happen, check n_notify logic)")
    print(f"knowledge.education.items: {len(items)} inherited")
    print(f"routines: {len(routines)} inherited")
    print("life.span: rolled fresh, written to lifespans.json - never into the child's own file")
    print(f"pool-eligible (pick_pair.py) once current pass number >= {args.pass_number + CHILD_COOLDOWN_PASSES}"
          f"  (child_cooldown_passes={CHILD_COOLDOWN_PASSES}, from _lore/tuning.json)")


if __name__ == "__main__":
    main()

"""
Compute a character's currently-accessible grounding - objective, "true regardless of anyone's
knowledge" content (embodiment mechanics + world state), gated by their own routines. Not sampled at
random like _lore/encodings.json's pool (sample_lore_knowledge.py) and not universal like
_lore/facts/facts.json - see _lore/grounding/_index.md for the full design.

Used by /enact (.claude/skills/enact/SKILL.md) alongside the existing facts/education/experience
knowledge kinds.

Computed live, every call, never cached into the character file: a character's routines can change
after creation (unlike knowledge.education, which is frozen for life), so a creation-time snapshot
would go stale the first time routines are edited. This is a cheap filtered lookup over two small
JSON files, not an expensive computation - nothing here is worth caching against.

Two access rules, deliberately different from sample_lore_knowledge.py's random-percentage draw -
grounding isn't meant to create narrative gaps, it's meant to reflect what a character would
obviously know or have seen given where they actually spend their time:

- mechanics.json: a "universal" entry is known by every character, always (same shape as
  _lore/facts/, but embodiment-specific rather than a fact of being a person at all). A "contextual"
  entry is known only if it's tagged with something the character's own routine contexts provide,
  read from _lore/contexts.json's `grounding_provides` (a separate field from that file's existing
  `provides`, which drives arc-need matching via check_needs_provides.py - a different concern).
- world_state.json: an entry is known if its `location` matches one of the character's own routine
  locations. (Once travel exists as a mechanic, this should also include anywhere the character has
  actually traveled to - not built yet, see TODO.md.)

Usage:
    python scripts/lore/sample_grounding.py --character khaoe
"""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
CHARACTERS_DIR = ROOT / "_lore" / "characters"
CONTEXTS_PATH = ROOT / "_lore" / "contexts.json"
MECHANICS_PATH = ROOT / "_lore" / "grounding" / "mechanics.json"
WORLD_STATE_PATH = ROOT / "_lore" / "grounding" / "world_state.json"


def load_json(path: Path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--character", required=True, help="Character key, e.g. khaoe")
    args = parser.parse_args()

    char_path = CHARACTERS_DIR / f"{args.character}.json"
    if not char_path.exists():
        raise SystemExit(f"No character file at {char_path}")
    character = load_json(char_path)
    routines = character.get("routines", [])

    context_keys = {r["context"] for r in routines if "context" in r}
    locations = {r["location"] for r in routines if "location" in r}

    contexts = load_json(CONTEXTS_PATH)
    provides: set[str] = set()
    for ctx_key in context_keys:
        ctx = contexts.get(ctx_key)
        if ctx is None:
            print(f"Warning: routine context '{ctx_key}' not found in {CONTEXTS_PATH}")
            continue
        provides.update(ctx.get("grounding_provides", []))

    mechanics = load_json(MECHANICS_PATH)["entries"]
    known_mechanics = [
        m for m in mechanics
        if m.get("distribution") == "universal" or set(m.get("tags", [])) & provides
    ]

    world_state = load_json(WORLD_STATE_PATH)["entries"]
    known_world_state = [w for w in world_state if w.get("location") in locations]

    print(f"Grounding for {args.character}:")
    print(f"  Routine contexts: {sorted(context_keys) or '(none)'}")
    print(f"  Routine locations: {sorted(locations) or '(none)'}")
    print(f"  Grounding-provides tags in scope: {sorted(provides) or '(none)'}")
    print()
    print(f"Mechanics known ({len(known_mechanics)} of {len(mechanics)}):")
    for m in known_mechanics:
        print(f"  [{m['id']}] ({m.get('distribution')}) {m['text']}")
    print()
    print(f"World state known ({len(known_world_state)} of {len(world_state)}):")
    for w in known_world_state:
        print(f"  [{w['id']}] {w['text']}")
    if not world_state:
        print("  (world_state.json is empty - nothing fed in yet from the external vision pipeline)")


if __name__ == "__main__":
    main()

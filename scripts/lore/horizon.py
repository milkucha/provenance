"""
Report how far through their life a character is - as a coarse band, never as a number. Separately,
report whether their life has just ended - a fact that structurally cannot be true before their scene
count reaches it.

This script exists so that the number itself never has to be loaded during an enactment. A
character's exact lifespan lives in _lore/characters/lifespans.json, which /enact must NEVER open; the
character file the enactment does read carries only `life.lived`, which is just their history and no
secret at all. Ask this script instead, and it answers with the least it can:

    band: early | established | late
    ending: true | false

`band` is NOT "what fraction of my personal countdown is left" - a character can't feel that any more
than a person can. It's built only from things a character could plausibly know about themselves: how
many scenes they've lived (`life.lived`, no secret), and the world-normal lifespan range for their
kind (`range` in lifespans.json, e.g. "30-60" - a world fact, not a roll). `early` means younger than
the range even starts; `established`/`late` split the range itself in half. It's for the
drift/susceptibility judgement in .claude/skills/character/SKILL.md Step 6 - a character further into
the range is riper for having their criterion broken - and is deliberately too coarse to reconstruct a
count from.

`ending` is `lived >= span` against the secretly-rolled `span`. Call this script before a scene and
it will always read `false` - the scene that turns out to be the character's last still has
`lived == span - 1` going in, so there is nothing to detect yet. Only after /enact Step 8 increments
`life.lived` for the scene just played does `ending` become knowable - because it isn't a fact until
then. There is no character-side knowledge to protect here the way there is with `band`: a character
does not experience their own death, and their last scene is not written any differently from any
other. What changes is what happens *after* it closes - see .claude/skills/enact/SKILL.md Step 8
point 6 and _lore/facts/life_is_finite.md. `ending` must never be consulted before Step 8, and its
pre-scene value must never be treated as informative (it always says the same thing: not yet).

Usage:
    python scripts/lore/horizon.py character_a
    python scripts/lore/horizon.py character_a --verbose   # includes the raw span; NEVER use during /enact
"""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
CHAR_DIR = ROOT / "_lore" / "characters"
LIFESPANS_PATH = CHAR_DIR / "lifespans.json"


def band_for(lived: int, range_min: int, range_max: int) -> str:
    if lived < range_min:
        return "early"
    midpoint = (range_min + range_max) / 2
    if lived < midpoint:
        return "established"
    return "late"


def is_ending(lived: int, span: int) -> bool:
    return lived >= span


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("npc_key", help="Character key, e.g. 'character_a'")
    parser.add_argument("--verbose", action="store_true", help="Also print the raw span. Never use this during an enactment.")
    args = parser.parse_args()

    key = args.npc_key.lower()

    char_path = CHAR_DIR / f"{key}.json"
    if not char_path.exists():
        raise SystemExit(f"No character file for '{key}'.")
    with open(char_path, encoding="utf-8") as f:
        character = json.load(f)
    with open(LIFESPANS_PATH, encoding="utf-8") as f:
        lifespans = json.load(f)["lifespans"]

    if key not in lifespans:
        raise SystemExit(f"No lifespan rolled for '{key}' yet - run scripts/lore/roll_lifespan.py and record it in _lore/characters/lifespans.json.")

    lived = character.get("life", {}).get("lived", 0)
    span = lifespans[key]["span"]
    range_min, range_max = (int(x) for x in lifespans[key]["range"].split("-"))

    print(f"band: {band_for(lived, range_min, range_max)}")
    print(f"lived: {lived}")
    print(f"ending: {'true' if is_ending(lived, span) else 'false'}")
    if args.verbose:
        print(f"span: {span}   <-- secret; must not enter an enactment's context")


if __name__ == "__main__":
    main()

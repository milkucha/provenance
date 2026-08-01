"""
Report how far through their life a character is - as a coarse band, never as a number.

This script exists so that the number itself never has to be loaded during an enactment. A
character's lifespan lives in _maps/npcs/lifespans.json, which /enact must NEVER open; the registry
entry the enactment does read carries only `life.lived`, which is just their history and no secret at
all. Ask this script instead, and it answers with the least it can:

    band: early | established | late | final

`final` means this next scene is their last, and is the one and only moment a character may know
anything about their own horizon (see _lore/facts/life_is_finite.md). The other three bands are for
the drift/susceptibility judgement in .claude/skills/character/SKILL.md Step 6 - a character running
short is riper for having their criterion broken - and are deliberately too coarse to reconstruct a
count from.

Usage:
    python scripts/horizon.py khaoe
    python scripts/horizon.py khaoe --verbose   # includes the raw span; NEVER use during /enact
"""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = ROOT / "_maps" / "npcs" / "registry.json"
LIFESPANS_PATH = ROOT / "_maps" / "npcs" / "lifespans.json"


def band_for(lived: int, span: int) -> str:
    if lived + 1 >= span:
        return "final"
    remaining = span - lived
    fraction = remaining / span
    if fraction <= 0.25:
        return "late"
    if fraction <= 0.60:
        return "established"
    return "early"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("npc_key", help="Registry key, e.g. 'khaoe'")
    parser.add_argument("--verbose", action="store_true", help="Also print the raw span. Never use this during an enactment.")
    args = parser.parse_args()

    key = args.npc_key.lower()

    with open(REGISTRY_PATH, encoding="utf-8") as f:
        npcs = json.load(f)["npcs"]
    with open(LIFESPANS_PATH, encoding="utf-8") as f:
        lifespans = json.load(f)["lifespans"]

    if key not in npcs:
        raise SystemExit(f"No registry entry for '{key}'.")
    if key not in lifespans:
        raise SystemExit(f"No lifespan rolled for '{key}' yet - run scripts/roll_lifespan.py and record it in _maps/npcs/lifespans.json.")

    lived = npcs[key].get("life", {}).get("lived", 0)
    span = lifespans[key]["span"]

    print(f"band: {band_for(lived, span)}")
    print(f"lived: {lived}")
    if args.verbose:
        print(f"span: {span}   <-- secret; must not enter an enactment's context")


if __name__ == "__main__":
    main()

"""
Count how many scenes a character has actually been in, for /character Step 5's backfill rule:
"one encodings.json hearsay.entries[] record is one scene, so `lived` is the number of entries
listing them in `participants`" - matched on display name, diacritics and all, since a plain ASCII
search misses "Döran" or "Iläria".

This script only counts. It does not write life.lived, and does not reroll a lifespan even when the
count meets or exceeds the rolled span - Step 5 is explicit that a reroll (with --min <lived+1>) is
the right call in that case, and that's an author decision to make deliberately, not something to
happen silently as a side effect of counting.

Usage:
    py scripts/lore/backfill_lived.py <npc_key>
"""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
CHAR_DIR = ROOT / "_lore" / "characters"
ENCODINGS_PATH = ROOT / "_lore" / "encodings.json"
LIFESPANS_PATH = CHAR_DIR / "lifespans.json"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("npc_key", help="Character key, e.g. 'doran'")
    args = parser.parse_args()

    key = args.npc_key.lower()
    char_path = CHAR_DIR / f"{key}.json"
    if not char_path.exists():
        raise SystemExit(f"No character file for '{key}'.")
    with open(char_path, encoding="utf-8") as f:
        character = json.load(f)
    name = character.get("name")
    if not name:
        raise SystemExit(f"'{key}' has no name set yet.")

    with open(ENCODINGS_PATH, encoding="utf-8") as f:
        entries = json.load(f)["hearsay"]["entries"]

    matches = [e["id"] for e in entries if any(p.lower() == name.lower() for p in e.get("participants", []))]

    current_lived = character.get("life", {}).get("lived", 0)

    print(f"character: {key} ({name})")
    print(f"scenes found: {len(matches)}")
    for m in matches:
        print(f"  {m}")
    print()
    print(f"current life.lived on file: {current_lived}")
    if len(matches) != current_lived:
        print(f"MISMATCH - consider setting life.lived to {len(matches)}")
    else:
        print("matches life.lived on file - no change needed")

    if LIFESPANS_PATH.exists():
        with open(LIFESPANS_PATH, encoding="utf-8") as f:
            lifespans = json.load(f).get("lifespans", {})
        span = lifespans.get(key, {}).get("span")
        if span is not None and len(matches) >= span:
            print()
            print(f"NOTE: counted {len(matches)} scenes >= rolled span {span}. Per Step 5, this character is")
            print(f"demonstrably still alive after that many scenes - reroll with:")
            print(f"  py scripts/lore/roll_lifespan.py --min {len(matches) + 1}")


if __name__ == "__main__":
    main()

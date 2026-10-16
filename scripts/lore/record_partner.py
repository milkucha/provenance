"""
Increment how many scenes two characters have shared - mechanical bookkeeping for reproduction
eligibility (design debrief, 2026-08-10), the same discipline as update_character.py's --lived-delta:
this script makes no judgement calls, it only records a count that already happened. It also
puts the other person in the character's stored social_circle as `met` (update_social_circle.py).

Call once per character, per scene they shared with someone (so twice total for a two-person scene -
once from each side), same as life.lived already gets bumped once per participant per pass.

Usage:
    py scripts/lore/record_partner.py kristok_jakur --with some_trader
    py scripts/lore/record_partner.py some_trader --with kristok_jakur
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import update_social_circle  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent.parent
CHAR_DIR = ROOT / "_lore" / "characters"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("npc_key", help="Character key whose file gets updated")
    parser.add_argument("--with", dest="partner", required=True, help="The other participant's key")
    args = parser.parse_args()

    key = args.npc_key.lower()
    char_path = CHAR_DIR / f"{key}.json"
    if not char_path.exists():
        raise SystemExit(f"No character file for '{key}'.")
    with open(char_path, encoding="utf-8") as f:
        character = json.load(f)

    partners = character.setdefault("partners", {})
    partners[args.partner] = partners.get(args.partner, 0) + 1
    update_social_circle.add_tie(character, args.partner, "met")  # the circle writer's "met": two people who shared a scene

    with open(char_path, "w", encoding="utf-8") as f:
        json.dump(character, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"{key}: partners.{args.partner} = {partners[args.partner]}")


if __name__ == "__main__":
    main()

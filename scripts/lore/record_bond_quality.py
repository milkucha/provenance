"""
Increment (or decrement) a signed running quality score for one character's tie to another -
mechanical bookkeeping, the same discipline as record_partner.py's own strength counter, added
alongside it 2026-08-28 (design debrief): `partners{}` already tracks how OFTEN two characters have
shared a scene (strength); this tracks whether those scenes have generally gone well or badly
(quality). Two separate numbers on purpose - a pair can meet constantly and mostly clash (high
strength, negative quality), or barely meet and always get along (low strength, positive quality).

Deliberately asymmetric, same as the signal that drives it: `check_arc_alignment.py`'s `inclined`
result describes ONE participant's own disposition toward the OTHER's arc (help/hinder/mixed/
neutral), not a shared "how do these two feel about each other" value - so only the peer's own
record of the primacy winner updates each time, never both directions at once the way
record_partner.py's strength bump always does. Over many passes, primacy alternates between the two
(an independent roll, not fixed), so both directions still accumulate their own quality history over
time - just not in the same call.

Called with delta=0 is a legitimate no-op the caller should just skip instead (see
simulate_pass_brief.py's own site) - this script doesn't special-case it, but there's no reason to
spend a file write recording "nothing happened."

Usage:
    py scripts/lore/record_bond_quality.py kristok_jakur --with some_trader --delta 1
    py scripts/lore/record_bond_quality.py some_trader --with kristok_jakur --delta -1
"""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
CHAR_DIR = ROOT / "_lore" / "characters"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("npc_key", help="Character key whose file gets updated")
    parser.add_argument("--with", dest="partner", required=True, help="The other participant's key")
    parser.add_argument("--delta", type=int, required=True, help="Signed amount to add to this tie's quality score")
    args = parser.parse_args()

    key = args.npc_key.lower()
    char_path = CHAR_DIR / f"{key}.json"
    if not char_path.exists():
        raise SystemExit(f"No character file for '{key}'.")
    with open(char_path, encoding="utf-8") as f:
        character = json.load(f)

    quality = character.setdefault("partners_quality", {})
    quality[args.partner] = quality.get(args.partner, 0) + args.delta

    with open(char_path, "w", encoding="utf-8") as f:
        json.dump(character, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"{key}: partners_quality.{args.partner} = {quality[args.partner]}")


if __name__ == "__main__":
    main()

"""
Check whether any claims from a just-recorded scene reference a character's criterion.anchor - the
"reference gate" that opens /enact Step 5b: "a pointer comparison, not a judgement about how upsetting
something was... never score intensity." That comparison is exactly what this script does, mechanically,
so the model's job starts at "does the gate matter here" already answered, not at reading every claim's
`about` field against the anchor string by eye.

This script does NOT decide whether a gated claim gets rejected, reinterpreted, or accepted-and-broken -
that judgement (provenance, proximity, susceptibility, trust) stays entirely with whoever is running
/enact, per .claude/skills/character/SKILL.md Step 6. It only tells you which claims, if any, are even
in play.

Usage:
    py scripts/lore/check_anchor_reference.py <npc_key> --hearsay-id <entry_id>
    py scripts/lore/check_anchor_reference.py <npc_key> --about "era_ensayo: Las Guerras de Gorff" --about "CONFLICT-01"
"""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
CHAR_DIR = ROOT / "_lore" / "characters"
ENCODINGS_PATH = ROOT / "_lore" / "encodings.json"


def anchor_id_part(anchor: str) -> str:
    return anchor.split(": ", 1)[1].strip() if ": " in anchor else anchor.strip()


def references(anchor: str, about) -> bool:
    if not anchor or not about:
        return False
    about = str(about).strip()
    anchor = anchor.strip()
    anchor_id = anchor_id_part(anchor)
    return about.lower() == anchor.lower() or about.lower() == anchor_id.lower()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("npc_key", help="Character key, e.g. 'khaoe'")
    parser.add_argument("--hearsay-id", default=None, help="A hearsay.entries id - checks all of that entry's claims")
    parser.add_argument("--about", action="append", default=[], help="An 'about' ref to check directly. Repeatable.")
    args = parser.parse_args()

    key = args.npc_key.lower()
    char_path = CHAR_DIR / f"{key}.json"
    if not char_path.exists():
        raise SystemExit(f"No character file for '{key}'.")
    with open(char_path, encoding="utf-8") as f:
        character = json.load(f)

    anchor = character.get("criterion", {}).get("anchor", "") or ""

    claims = []
    if args.hearsay_id:
        with open(ENCODINGS_PATH, encoding="utf-8") as f:
            entries = json.load(f)["hearsay"]["entries"]
        entry = next((e for e in entries if e["id"] == args.hearsay_id), None)
        if entry is None:
            raise SystemExit(f"No hearsay entry with id '{args.hearsay_id}'.")
        for i, c in enumerate(entry["claims"]):
            claims.append((f"{entry['id']}#{i}", c.get("about")))
    for about in args.about:
        claims.append((None, about))

    if not claims:
        raise SystemExit("Nothing to check - pass --hearsay-id or one or more --about.")

    print(f"character: {key}")
    print(f"anchor: {anchor or '(none set)'}")
    print()

    if not anchor:
        print("No anchor set for this character - gate cannot match. No shock possible.")
        return

    matches = [(claim_id, about) for claim_id, about in claims if references(anchor, about)]

    if matches:
        print(f"GATE MATCHED - {len(matches)} claim(s) reference the anchor:")
        for claim_id, about in matches:
            label = claim_id or about
            print(f"  {label}  (about: {about})")
        print()
        print("Resolve per /character Step 6: reject / reinterpret / break. Not a magnitude judgement -")
        print("weigh provenance, proximity, susceptibility, and this character's trusts/distrusts.")
    else:
        print("No claim references the anchor. Default applies: no change.")


if __name__ == "__main__":
    main()

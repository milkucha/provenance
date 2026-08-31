"""
Apply the two mechanical consequences of a contested visit resolving "hinder" against a NAMED
rival - folds what SKILL.md's old Step 9 described as two separate hand-edits (append a `leads`
entry to the traveler's own file; write one attributed note to the rival's own knowledge.experience)
into one call (design debrief 2026-08-13).

Only ever relevant when: check_arc_alignment.py's `inclined` came back "hinder", roll_contested.py
came back true, AND the scene's own subagent chose to dramatize the contest as being against a
SPECIFIC rival who already has a character file (`_lore/characters/<slug>.json` exists) - that
file-existence check, and the choice of whether to name anyone at all, is the one piece of this
still left to the subagent; nothing here is a dice roll or a lookup that could replace it. If the
scene kept the rival ambient/unnamed (the default, and the common case), this script is never called.

The note text is fixed, not composed - "never invented prose" per the original design debrief:
    "According to <supplier>, <rival> already claimed <matched_provide> before <traveler> arrived."

Usage:
    py scripts/lore/apply_contested_lead.py --traveler bardaglis --rival character_b \\
        --supplier character_a --matched-provide "news" --pass-number 24
"""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
CHAR_DIR = ROOT / "_lore" / "characters"


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


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--traveler", required=True, help="The visitor whose claim lost this contest")
    parser.add_argument("--rival", required=True, help="The named prior claimant - must already have a character file")
    parser.add_argument("--supplier", required=True, help="Who the traveler heard it from (usually the home_frame character)")
    parser.add_argument("--matched-provide", required=True, help="The specific provide tag both parties were after")
    parser.add_argument("--pass-number", type=int, required=True)
    args = parser.parse_args()

    traveler_key, rival_key = args.traveler.lower(), args.rival.lower()

    traveler = load_char(traveler_key)
    rival_path = CHAR_DIR / f"{rival_key}.json"
    if not rival_path.exists():
        raise SystemExit(f"'{rival_key}' has no character file - a rival can only be named this way if their file already exists (plain file-existence check, per SKILL.md Step 9).")
    rival = load_char(rival_key)

    traveler.setdefault("leads", []).append({"target": rival_key, "created_pass": args.pass_number})
    save_char(traveler_key, traveler)

    note = f"According to {args.supplier}, {args.rival} already claimed {args.matched_provide} before {args.traveler} arrived."
    rival.setdefault("knowledge", {}).setdefault("experience", [])
    rival["knowledge"]["experience"].append(note)
    save_char(rival_key, rival)

    print(f"{traveler_key}: leads += {{target: {rival_key}, created_pass: {args.pass_number}}}")
    print(f"{rival_key}: knowledge.experience += 1 (\"{note}\")")


if __name__ == "__main__":
    main()

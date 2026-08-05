"""
Check whether a candidate character name is available, before /character or /enact treats it as a
brand-new character.

This is the single shared enforcement point for name uniqueness across every character ever created
in _lore/characters/ - living or deceased, since nothing there is ever deleted. A name is available
only if no existing character slugifies to the same key. A genuine namesake is still fine ("Farlis
Gorfalis" alongside "Farlis") since the two slugify differently - the check is plain string equality
on the slug, not a judgment about whether two names "feel" too similar.

Slugification matches the convention already used for dialogue/tale filenames throughout the pack
(see .claude/skills/tell/SKILL.md Step 2): lowercase, diacritics folded to their nearest ASCII
equivalent, anything that isn't a letter/digit collapsed to a single underscore. This is also exactly
how existing registry/character keys were already derived (e.g. "Döran" -> "doran"), so this check
doubles as "does _lore/characters/<slug>.json already exist" - no separate index needed.

Usage:
    python scripts/lore/check_character_name.py "Doran"
    python scripts/lore/check_character_name.py "Farlis Gorfalis"
"""

import argparse
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
CHAR_DIR = ROOT / "_lore" / "characters"


def slugify(name: str) -> str:
    folded = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    folded = folded.lower().strip()
    folded = re.sub(r"[^a-z0-9]+", "_", folded)
    return folded.strip("_")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("name", help="Candidate character name")
    args = parser.parse_args()

    slug = slugify(args.name)
    if not slug:
        raise SystemExit(f"'{args.name}' doesn't slugify to anything usable - pick a name with at least one letter or digit.")

    candidate = CHAR_DIR / f"{slug}.json"
    if candidate.exists():
        import json

        with open(candidate, encoding="utf-8") as f:
            existing_name = json.load(f).get("name", "")
        print(f"TAKEN ({candidate.relative_to(ROOT)}, name: \"{existing_name}\")")
    else:
        print(f"AVAILABLE (slug: {slug})")


if __name__ == "__main__":
    main()

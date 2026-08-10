"""
Check whether a visit destination's archetype happens to supply what the traveler's arc currently
needs - mechanical, not a model deciding "this visit feels purposeful." A match means the visit
gets framed as motivated; no match means it's an ordinary, unmotivated visit, same as always.

The reason isn't invented - it's checked for, after the fact of pick_pair.py/roll_routine.py/
resolve_location.py having already, independently, decided who's visiting whom. This runs strictly
after those, never instead of them.

Usage:
    py scripts/lore/check_needs_provides.py --needs "rare ore" --needs "expertise" \
        --provides "rare ore" --provides "goods" --provides "materials"
"""

import argparse
import re

STOPWORDS = {
    "a", "an", "the", "of", "to", "in", "on", "at", "by", "for", "with", "without", "and", "or",
    "but", "not", "is", "are", "was", "were", "be", "been", "being", "this", "that", "their",
}


def significant_words(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z']+", text.lower())
    return {w for w in words if w not in STOPWORDS and len(w) > 2}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--needs", action="append", default=[], required=True, help="Traveler's arc.needs tag(s), repeatable")
    parser.add_argument("--provides", action="append", default=[], required=True, help="Destination archetype's provides tag(s), repeatable")
    args = parser.parse_args()

    for need in args.needs:
        need_words = significant_words(need)
        for provide in args.provides:
            if need_words & significant_words(provide) or need.strip().lower() == provide.strip().lower():
                print("match: true")
                print(f"matched_need: {need}")
                print(f"matched_provide: {provide}")
                return

    print("match: false")


if __name__ == "__main__":
    main()

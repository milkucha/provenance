"""
Check whether the scene's own context happens to supply what the arc-primacy winner currently
needs - mechanical, not a model deciding "this visit feels purposeful." A match means the scene
gets framed as motivated; no match means it's ordinary and unmotivated, same as always.

Design debrief 2026-08-28: keyed to whichever participant WON arc primacy, not "the traveler" -
primacy is now decided independently of home/visiting (roll_home_visit.py), so the primacy winner
can just as easily be the home participant as the one visiting. The reason isn't invented - it's
checked for, after the fact of roll_home_visit.py/roll_routine.py/roll_arc_primacy.py having already,
independently, decided who's where and whose arc leads. This runs strictly after those, never
instead of them.

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
    parser.add_argument("--needs", action="append", default=[], required=True, help="Arc-primacy winner's arc.needs tag(s), repeatable")
    parser.add_argument("--provides", action="append", default=[], required=True, help="Scene context's provides tag(s), repeatable")
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

"""
Roll a character's lifespan - how many scenes they have left in them, total.

Used by the /character skill when a character's sheet is first created (and by /enact when it creates
one), writing the result to _lore/characters/lifespans.json - NOT to the character's own file, which is
what /enact loads in order to play them. Rolled once, never rerolled - same discipline as
knowledge.education. Anything needing to know how far through a life a character is asks
scripts/horizon.py, which answers with a coarse band and never the number.

The character is never told the number. They know life is finite (that's the `life_is_finite` fact in
_lore/facts/, which every character knows in full), but not how much of it is left - exactly the way
people actually live. There is no exception, not even for the scene that turns out to be the last:
that scene is played exactly like any other, and whether it was the last is only knowable afterward,
mechanically, once it has already closed. See _lore/facts/life_is_finite.md and scripts/horizon.py.

The range is a tuning knob, not a world fact. Narrow it for testing when you want to actually reach a
character's last scene without playing a dozen of them first:

Usage:
    python scripts/roll_lifespan.py                      # 30-60 scenes, the world's normal range
    python scripts/roll_lifespan.py --min 2 --max 4      # short lives, for testing the endgame
    python scripts/roll_lifespan.py --seed 42            # reproducible roll

The 30-60 default was set by the author on 2026-07-31, replacing an initial 4-14: a character should
have room for a real life's worth of encounters, not run out inside a session's worth of scenes.
"""

import argparse
from random import Random

DEFAULT_MIN = 30
DEFAULT_MAX = 60


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--min", type=int, default=DEFAULT_MIN, dest="minimum", help=f"Fewest scenes a life can run to (default {DEFAULT_MIN})")
    parser.add_argument("--max", type=int, default=DEFAULT_MAX, dest="maximum", help=f"Most scenes a life can run to (default {DEFAULT_MAX})")
    parser.add_argument("--seed", type=int, default=None, help="Optional seed, for a reproducible roll")
    args = parser.parse_args()

    if args.minimum < 1:
        parser.error("--min must be at least 1")
    if args.maximum < args.minimum:
        parser.error("--max must be greater than or equal to --min")

    rng = Random(args.seed)
    span = rng.randint(args.minimum, args.maximum)

    print(f"span: {span}")
    print(f"range: {args.minimum}-{args.maximum}")
    print()
    print("Write to _lore/characters/lifespans.json - never to the character's own file, which /enact")
    print("loads to play them. Do not reveal this number to them and never let it into a dialog line.")
    print("See _lore/facts/life_is_finite.md and scripts/horizon.py.")


if __name__ == "__main__":
    main()

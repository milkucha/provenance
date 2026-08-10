"""
Resolve a scene's location from two participants' current routines - mechanical, not a model
judgment call, same reasoning as pick_pair.py and roll_routine.py.

Rule (decided in the /simulate design debrief, 2026-08-10):
- Same routine -> coincidence. Unplanned, ordinary, no criterion or motive required. A coin flip
  decides whose "home ground" it narratively is, purely for framing (the place is the same either
  way).
- Different routines -> visit. participant_2's routine is always the scene location; participant_1
  is the one who traveled. This is a fixed convention, not a random pick - pick_pair.py's own
  participant_1/participant_2 assignment is already a genuine uniform draw, so over a long run each
  character ends up traveler and host roughly equally without needing a second random choice here.

Usage:
    py scripts/lore/resolve_location.py --p1 khaoe --p1-routine Terfila --p2 nerkeli --p2-routine Terfila
    py scripts/lore/resolve_location.py --p1 khaoe --p1-routine Terfila --p2 nerkeli --p2-routine "Sid Nalta"
"""

import argparse
import random


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--p1", required=True)
    parser.add_argument("--p1-routine", required=True)
    parser.add_argument("--p2", required=True)
    parser.add_argument("--p2-routine", required=True)
    args = parser.parse_args()

    if args.p1_routine == args.p2_routine:
        host = random.choice([args.p1, args.p2])
        print("mode: coincidence")
        print(f"location: {args.p1_routine}")
        print(f"home_frame: {host}")
        print("traveler: none")
    else:
        print("mode: visit")
        print(f"location: {args.p2_routine}")
        print(f"home_frame: {args.p2}")
        print(f"traveler: {args.p1}")


if __name__ == "__main__":
    main()

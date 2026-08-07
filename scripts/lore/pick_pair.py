"""
Draw one uniformly random pair of two distinct participants from a living pool, for
.claude/skills/simulate/SKILL.md Step 3 point 2 ("pick 2 participants from the living pool uniformly
at random").

This exists because a model asked to "pick randomly" is not actually a uniform random source - it
tends toward recency, salience, or whatever it mentioned last, in ways a real PRNG doesn't. Over a
50-pass run that bias would quietly skew which pairs of characters actually get scenes together,
which is exactly the kind of thing /simulate is trying to measure honestly. random.sample() carries
no judgement and needs none - this script makes no decision beyond the draw itself.

Usage:
    py scripts/lore/pick_pair.py khaoe gondarfolas auroboro_iii nerkeli
"""

import argparse
import random


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pool", nargs="+", help="Living pool: every participant slug still eligible this pass")
    args = parser.parse_args()

    pool = list(dict.fromkeys(args.pool))  # de-dup, keep order, in case a slug was passed twice
    if len(pool) < 2:
        raise SystemExit(f"Need at least 2 distinct participants in the pool; got {len(pool)}.")

    a, b = random.sample(pool, 2)
    print(f"participant_1: {a}")
    print(f"participant_2: {b}")


if __name__ == "__main__":
    main()

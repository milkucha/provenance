"""
Draw ONE uniformly random participant from a living pool, for the asymmetric per-pass model
(design session 2026-09-13 - see TODO.md's "asymmetric per-pass rewrite" entry and CHRONICLE.md's
matching entry). Retired this file's old "draw two" behavior: under the new model there is no
pre-selected second participant any more - only `p1` is picked up front, unweighted, and whoever
else ends up in the pass (if anyone) is *discovered* later, via the arc-needs/travel/meetable chain
(see `location_context.py`/`travel_graph.py`/`roll_meetable.py` and `simulate_pass_lib.run_pass_mechanics()`).

Kept in this file rather than moved, per the rewrite's own instruction to keep the draw here unless
there's a strong reason not to - there isn't one: this is still exactly the same "a model asked to
pick randomly isn't a uniform random source" problem pick_pair.py always solved, just over a draw of
1 instead of 2. random.choice() carries no judgement and needs none - this script makes no decision
beyond the draw itself.

Usage:
    py scripts/lore/pick_pair.py khaoe gondarfolas auroboro_iii nerkeli
"""

import argparse
from random import Random


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pool", nargs="+", help="Living pool: every participant slug still eligible this pass")
    parser.add_argument("--seed", type=int, default=None, help="Optional seed, for a reproducible draw")
    args = parser.parse_args()

    pool = list(dict.fromkeys(args.pool))  # de-dup, keep order, in case a slug was passed twice
    if not pool:
        raise SystemExit("Need at least 1 participant in the pool; got 0.")

    rng = Random(args.seed)
    chosen = rng.choice(pool)
    print(f"participant: {chosen}")


if __name__ == "__main__":
    main()

"""
Drain one location's wealth pool by its per-capita upkeep for this pass - the one thing in the
survival mechanism that runs regardless of any individual's choice, same as a town needs feeding
whether or not anyone worked today. Per-capita, not flat (design session 2026-08-28): a flat drain
would be meaningless at 100 population and crushing at 2 - `upkeep_rate_per_capita` (0.5,
_lore/tuning.json's `survival` block) scales with however many living characters are currently
registered at this exact location string (wealth_lib.population_of()).

Call this ONCE per pass, for the pass's resolved location - not once per participant, and not for
every location in the world every pass (locations nobody's touched this pass just don't tick; same
lazy-clock precedent horizon.py already uses for life.lived).

Usage:
    py scripts/lore/apply_upkeep.py --location City C
"""

import argparse
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT = SCRIPTS_DIR.parent.parent

sys.path.insert(0, str(SCRIPTS_DIR))
import tuning  # noqa: E402
import wealth_lib  # noqa: E402

_S = tuning.load()["survival"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--location", required=True)
    args = parser.parse_args()

    pop = wealth_lib.population_of(args.location)
    pool = wealth_lib.get_wealth(args.location)
    upkeep = pop * _S["upkeep_rate_per_capita"]
    pool -= upkeep
    wealth_lib.set_wealth(args.location, pool)
    wealth_lib.checkpoint_wealth_trend(args.location)

    print(f"population: {pop}")
    print(f"upkeep: {round(upkeep, 2)}")
    print(f"pool: {round(pool, 2)}")


if __name__ == "__main__":
    main()

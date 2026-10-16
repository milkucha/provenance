"""
Drain one location's provisions pool by its per-capita upkeep for this pass - the one thing in the
energy/eating mechanism that runs regardless of any individual's choice, same as a town needs feeding
whether or not anyone worked today. Per-capita, not flat (design session 2026-08-28): a flat drain
would be meaningless at 100 population and crushing at 2 - `upkeep_rate_per_capita` (0.15,
_lore/tuning.json's `survival` block) scales with however many living characters are currently
registered at this exact location string (provisions_lib.population_of()).

Call this ONCE per pass, for the pass's resolved location - not once per participant, and not for
every location in the world every pass (locations nobody's touched this pass just don't tick; same
lazy-clock precedent horizon.py already uses for life.lived).

**Floored at 0, added 2026-08-31 (user correction, not a tuning change)** - upkeep used to have no
floor at all, so a populous location's pool would free-fall arbitrarily negative (-430 observed on
Salthos Cruzados after ~340 combined passes) with zero further mechanical effect once it dropped
below `eat_amount`: the "can anyone eat here" check is a plain `pool >= eat_amount`, so -2 and -430
behave identically downstream. The deep negative number was pure noise, not a harsher penalty, and
made recovery effectively impossible - a work pass's pool contribution (then a flat +3) could never claw
back out of a hole that deep. Clamping the drain at 0 keeps every existing downstream behavior
unchanged (nothing reads the *magnitude* of a negative pool, only whether it's below `eat_amount`)
while leaving recovery back to positive at least reachable. This is a floor, not a tuning change -
`upkeep_rate_per_capita` and `eat_amount` are untouched.

Still flat per capita under the economy rewrite (author's call 2026-10-17): no proportional decay on
the pool, none on personal provisions. The arithmetic is economy_rules.upkeep(), shared with the
balance script.

A road node (`road:<a>--<b>`, travel_graph.is_road) has no pool and no upkeep: this script reports
zeros and touches nothing.

Usage:
    py scripts/lore/apply_upkeep.py --location Tyrnea
"""

import argparse
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT = SCRIPTS_DIR.parent.parent

sys.path.insert(0, str(SCRIPTS_DIR))
import tuning  # noqa: E402
import provisions_lib  # noqa: E402
import economy_rules  # noqa: E402

_S = tuning.load()["survival"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--location", required=True)
    args = parser.parse_args()

    if not provisions_lib.has_pool(args.location):
        # a road node: no pool, so nothing to drain and nothing to checkpoint (and none is created)
        print(f"population: {provisions_lib.population_of(args.location)}")
        print("upkeep: 0")
        print("pool: 0")
        return

    pop = provisions_lib.population_of(args.location)
    pool = provisions_lib.get_provisions(args.location)
    upkeep = pop * _S["upkeep_rate_per_capita"]
    pool = economy_rules.upkeep(pool, pop, _S["upkeep_rate_per_capita"])
    provisions_lib.set_provisions(args.location, pool)
    provisions_lib.checkpoint_provisions_trend(args.location)

    print(f"population: {pop}")
    print(f"upkeep: {round(upkeep, 2)}")
    print(f"pool: {round(pool, 2)}")


if __name__ == "__main__":
    main()

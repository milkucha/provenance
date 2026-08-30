"""
Apply a survive/arc choice already decided by roll_survival.py - writes the character's own energy
delta and the resolved location's wealth-pool delta, and reports whether this character just died of
exhaustion. Split from the roll itself because the roll runs against a character's own HOME location
(before this pass's actual location is known), while the cost has to land on wherever the scene
actually resolved to - see roll_survival.py's own docstring.

Costs (design session 2026-08-28, all in _lore/tuning.json's `survival` block):
  - Every pass: -1 energy, unconditional (`base_cost`).
  - **survive**: +1 energy taken back from the pool (`survive_take`), which the character also
    contributes +2 to (`survive_contribute`) - net personal 0, net pool +1 before upkeep.
  - **arc**: draws `arc_pool_draw` (2) from the pool and costs `arc_extra_cost` (1) extra energy -
    UNLESS the pool doesn't have `arc_pool_draw` to give (design session 2026-08-29), in which case
    the pool is left untouched (never driven further negative by a draw it can't support) and the
    character pays `arc_extra_cost_scarce` (2) instead of `arc_extra_cost` - the town has nothing to
    give, so the cost comes out of the character's own energy instead. Reported back as `scarce:
    true`, a real story fact the brief can hand the model, not a silent number change. This does NOT
    include per-capita upkeep - call apply_upkeep.py once per pass per location separately, not once
    per participant, or the same location gets charged twice in a two-participant pass.

Energy hitting 0 or below is a death, independent of the existing rolled-lifespan clock (horizon.py)
- a second, separate cause, not merged into it. This script does NOT call record_death.py itself
(same split horizon.py/record_death.py already use: this only reports the fact, the caller decides
when to act on it, so a scene's own JUDGEMENT-level consequences aren't hidden inside a mechanical
apply step).

Usage:
    py scripts/lore/apply_survival.py --key degustarios --location Tyrnea --choice survive
    py scripts/lore/apply_survival.py --key degustarios --location Tyrnea --choice arc
"""

import argparse
import json
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT = SCRIPTS_DIR.parent.parent
CHAR_DIR = ROOT / "_lore" / "characters"

sys.path.insert(0, str(SCRIPTS_DIR))
import tuning  # noqa: E402
import wealth_lib  # noqa: E402

_S = tuning.load()["survival"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--key", required=True)
    parser.add_argument("--location", required=True, help="The pass's resolved location, not necessarily this character's home")
    parser.add_argument("--choice", choices=["survive", "arc"], required=True)
    args = parser.parse_args()

    key = args.key.lower()
    char_path = CHAR_DIR / f"{key}.json"
    if not char_path.exists():
        raise SystemExit(f"No character file for '{key}'.")
    with open(char_path, encoding="utf-8") as f:
        character = json.load(f)

    energy = character.get("energy", _S["energy_cap"])
    pool = wealth_lib.get_wealth(args.location)

    energy -= _S["base_cost"]
    scarce = False
    if args.choice == "survive":
        energy += _S["survive_take"]
        pool += _S["survive_contribute"] - _S["survive_take"]
    else:
        if pool >= _S["arc_pool_draw"]:
            pool -= _S["arc_pool_draw"]
            energy -= _S["arc_extra_cost"]
        else:
            # Nothing left in the pool to draw on - the town has nothing to give, so the cost
            # comes out of the character instead (arc_extra_cost_scarce replaces, not adds to,
            # arc_extra_cost). Pool is left untouched, not driven further negative by a draw it
            # can't actually support.
            scarce = True
            energy -= _S["arc_extra_cost_scarce"]

    energy = min(energy, _S["energy_cap"])
    character["energy"] = energy
    with open(char_path, "w", encoding="utf-8") as f:
        json.dump(character, f, indent=2, ensure_ascii=False)
        f.write("\n")
    wealth_lib.set_wealth(args.location, pool)

    died = energy <= 0
    print(f"energy: {energy}")
    print(f"died: {'true' if died else 'false'}")
    print(f"pool: {round(pool, 2)}")
    print(f"scarce: {'true' if scarce else 'false'}")


if __name__ == "__main__":
    main()

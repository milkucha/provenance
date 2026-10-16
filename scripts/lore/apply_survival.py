"""
Apply a work/arc choice already decided by roll_survival.py - writes the character's own energy and
personal provisions, and the resolved location's provisions pool, and reports whether this character
just died of exhaustion. Split from the roll itself because the roll runs against a character's own
HOME location (before this pass's actual location is known), while the cost has to land on wherever
the scene actually resolved to - see roll_survival.py's own docstring. The arithmetic itself is
economy_rules.resolve_pass(), pure, shared with the balance script (scripts/test/balance_economy.py).

Rules (economy rewrite 2026-10-17, all numbers in _lore/tuning.json's `survival` block; history of
the earlier design is in git and TODO.md):
  - Every pass: -`base_cost` energy, unconditional.
  - Eating is universal and independent of the choice: `eat_amount` (2) units, one from the
    character's own provisions and one from the pool; a shortfall on one side is filled from the
    other; if both can't cover it it is a half meal (whatever exists is taken, energy +1 per unit).
    Reported as `ate: full | half | none`.
  - **work**: pays the worker. `work_personal` (2) to the character's own provisions, `work_pool`
    (1) to the location's pool.
  - **arc**: costs `arc_extra_cost` (1) extra personal energy. Pays nothing. What an arc costs in
    food is the payment gate's (simulate_pass_lib.arc_payment_gate), in provisions you could have
    eaten.
  - **On a road node** (`road:<a>--<b>`): there is no pool (provisions_lib.has_pool), so eating takes
    from the character's own provisions only: with none, no meal or half a meal, and the character can
    starve on the road. Work there pays the worker as usual; the pool's share has nowhere to go.
  - **eat** (the second participant of a pair scene, 2026-10-17): base cost and the meal, nothing
    else. No work pay, no arc cost.
  Personal provisions and the pool never go negative. This does NOT include per-capita upkeep -
  call apply_upkeep.py once per pass per location, not once per participant.

Energy hitting 0 or below is a death, independent of the rolled-lifespan clock (horizon.py) - a
second, separate cause. This script only reports it (same split horizon.py/record_death.py use).
The old choice value `survive` is read as `work`.

Usage:
    py scripts/lore/apply_survival.py --key degustarios --location Tyrnea --choice work
    py scripts/lore/apply_survival.py --key degustarios --location Tyrnea --choice arc
    py scripts/lore/apply_survival.py --key farlis --location Tyrnea --choice eat
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
import provisions_lib  # noqa: E402
import economy_rules  # noqa: E402

_S = tuning.load()["survival"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--key", required=True)
    parser.add_argument("--location", required=True, help="The pass's resolved location, not necessarily this character's home")
    parser.add_argument("--choice", choices=["work", "survive", "arc", "eat"], required=True)
    args = parser.parse_args()

    key = args.key.lower()
    char_path = CHAR_DIR / f"{key}.json"
    if not char_path.exists():
        raise SystemExit(f"No character file for '{key}'.")
    with open(char_path, encoding="utf-8") as f:
        character = json.load(f)

    energy = character.get("energy", _S["energy_cap"])
    personal = character.get("provisions", _S["starting_provisions_per_capita"])
    pool = provisions_lib.get_provisions(args.location)

    out = economy_rules.resolve_pass(energy, personal, pool, args.choice, _S)
    energy = out["energy"]
    character["energy"] = energy
    character["provisions"] = out["personal"]
    with open(char_path, "w", encoding="utf-8") as f:
        json.dump(character, f, indent=2, ensure_ascii=False)
        f.write("\n")
    pool = out["pool"] if provisions_lib.has_pool(args.location) else 0
    provisions_lib.set_provisions(args.location, pool)

    died = energy <= 0
    print(f"energy: {energy}")
    print(f"died: {'true' if died else 'false'}")
    print(f"pool: {round(pool, 2)}")
    print(f"ate: {out['ate']}")
    print(f"provisions: {round(out['personal'], 2)}")


if __name__ == "__main__":
    main()

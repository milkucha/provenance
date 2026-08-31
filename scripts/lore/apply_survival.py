"""
Apply a survive/arc choice already decided by roll_survival.py - writes the character's own energy
delta and the resolved location's wealth-pool delta, and reports whether this character just died of
exhaustion. Split from the roll itself because the roll runs against a character's own HOME location
(before this pass's actual location is known), while the cost has to land on wherever the scene
actually resolved to - see roll_survival.py's own docstring.

Costs (redesigned 2026-08-31 - "eating" decoupled from the survive/arc choice, on user correction:
the prior design let `survive` restore energy unconditionally regardless of the pool's own health,
so a depleted pool never actually starved anyone directly, only skewed behavior indirectly. All in
_lore/tuning.json's `survival` block):
  - Every pass: -1 energy, unconditional (`base_cost`).
  - **Eating is now universal, gated on the pool alone, independent of choice.** If the location's
    pool has at least `eat_amount` (2) to give, this character takes it: pool -= eat_amount,
    energy += eat_amount (net personal: 0, same math the old `survive`-only path used). If the pool
    can't cover it, nobody eats this pass regardless of what they chose - reported back as `ate:
    false`, a real story fact (the town has nothing to give, and it costs YOU, not just whoever
    happened to choose "arc").
  - **survive**: contributes `survive_contribute` (3) to the pool - pure contribution, no longer
    bundled with eating (that's step 1, above, and happens either way).
  - **arc**: costs `arc_extra_cost` (1) extra personal energy, unconditionally - pursuing your own
    project instead of working, on top of whatever step 1's eating did or didn't cover. No longer
    draws anything extra from the pool itself (retired `arc_pool_draw`/`arc_extra_cost_scarce` -
    the pool has exactly one interaction now, eating, so an arc-choosing character in a starved town
    already feels it twice: failing to eat, then still paying the extra personal cost anyway).
    This does NOT include per-capita upkeep - call apply_upkeep.py once per pass per location
    separately, not once per participant, or the same location gets charged twice in a
    two-participant pass.

Energy hitting 0 or below is a death, independent of the existing rolled-lifespan clock (horizon.py)
- a second, separate cause, not merged into it. This script does NOT call record_death.py itself
(same split horizon.py/record_death.py already use: this only reports the fact, the caller decides
when to act on it, so a scene's own JUDGEMENT-level consequences aren't hidden inside a mechanical
apply step).

Usage:
    py scripts/lore/apply_survival.py --key character_d --location City C --choice survive
    py scripts/lore/apply_survival.py --key character_d --location City C --choice arc
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

    # Step 1: eating - universal, pool-gated, independent of choice.
    ate = pool >= _S["eat_amount"]
    if ate:
        pool -= _S["eat_amount"]
        energy += _S["eat_amount"]

    # Step 2: the choice - pool contribution (survive) or extra personal cost (arc). Eating
    # above already happened either way; this no longer touches the pool for "arc" at all.
    if args.choice == "survive":
        pool += _S["survive_contribute"]
    else:
        energy -= _S["arc_extra_cost"]

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
    print(f"ate: {'true' if ate else 'false'}")


if __name__ == "__main__":
    main()

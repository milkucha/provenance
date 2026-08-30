"""
Roll whether a character spends this pass surviving (working, replenishing their own energy and
the local wealth pool) or pursuing their arc (spending extra energy and the pool's own wealth, on a
bet that this pass advances something) - a weighted dice roll, not a model's judgment call, same
"skew, never decide" philosophy as every other roll in this pipeline (roll_contested.py in
particular is the closest precedent: a base percentage, shifted point-by-point by each real input,
clamped, then rolled).

Design session 2026-08-28 - see TODO.md's "Survival mechanism" entry for the full worked-through
math and CHRONICLE.md's matching entry for how each input got settled. Four inputs, each contributing
a percentage-point shift toward "arc" (or away from it, negative):

  - **energy** - more personal buffer, safer to gamble. Normalized around the cap's midpoint.
  - **arc_pressure** - how much this arc wants pursuing right now: its own tally stage (early/mid/
    about to resolve) plus how much time this character reads as having left (horizon.py's band -
    a character who's "late" leans harder into their arc, less to lose).
  - **pool_reliance** - a healthy local wealth pool only feels like a safety net if this character is
    actually connected to the people sharing it (net_affinity) - reliance is pool_surplus AMPLIFIED
    by affinity, not an input on its own. An isolated character in a wealthy town doesn't get to lean
    on wealth they don't feel part of.
  - **affinity_obligation** - the SAME net_affinity number, independently, pulling the other way: the
    more bonded a character is, the more duty-bound to work for the collective, regardless of the
    pool's own health.

net_affinity itself is Sum(partners_quality[p]) / Sum(partners[p]) across ESTABLISHED partners only
(count >= partner_threshold, same bar roll_contested.py already uses) - a character with many strong
but negative bonds gets pushed the correct direction on both terms, not just one, since it's one
signed number playing two roles.

A character with no ongoing arc has nothing to pursue this pass - always survives, no roll needed.

Called BEFORE roll_home_visit.py (this pass's location isn't known yet) - `--location` is this
character's own registered `location` field (their home base), used as a proxy for "is where I'm
based doing okay," not the pass's eventual resolved location. The actual energy/pool costs get
applied later, at the resolved location, by apply_survival.py - this script only decides and never
writes anything to disk.

Usage:
    py scripts/lore/roll_survival.py --key degustarios
"""

import argparse
import json
import random
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT = SCRIPTS_DIR.parent.parent
CHAR_DIR = ROOT / "_lore" / "characters"
LIFESPANS_PATH = CHAR_DIR / "lifespans.json"

sys.path.insert(0, str(SCRIPTS_DIR))
import tuning  # noqa: E402
import wealth_lib  # noqa: E402
from horizon import band_for  # noqa: E402

_T = tuning.load()
_ARC_THRESHOLD = _T["arc_resolution_threshold"]
_PARTNER_THRESHOLD = _T["partner_threshold"]
_S = _T["survival"]


def net_affinity(character: dict) -> float:
    partners = character.get("partners", {})
    quality = character.get("partners_quality", {})
    established = [p for p, n in partners.items() if n >= _PARTNER_THRESHOLD]
    if not established:
        return 0.0
    total_strength = sum(partners[p] for p in established)
    total_quality = sum(quality.get(p, 0) for p in established)
    return total_quality / total_strength if total_strength else 0.0


def _tally(history: list) -> int:
    """Mirrors simulate_pass_lib.tally() exactly - duplicated rather than imported, since this
    script only needs the one small function and importing the full lib pulls in contexts.json and
    every sibling-script wrapper for no reason."""
    last_transform = -1
    for i, h in enumerate(history):
        if h.get("outcome") == "transform":
            last_transform = i
    relevant = history[last_transform + 1:]
    score = {"advance": 1, "stall": 0, "reverse": -1}
    return sum(score.get(h.get("outcome"), 0) for h in relevant)


def arc_stage(arc: dict) -> str:
    score = abs(_tally(arc.get("history", [])))
    if score == 0:
        return "early"
    if score >= _ARC_THRESHOLD - 1:
        return "late"
    return "mid"


def character_band(character: dict, key: str) -> str:
    if not LIFESPANS_PATH.exists():
        return "early"
    with open(LIFESPANS_PATH, encoding="utf-8") as f:
        lifespans = json.load(f)["lifespans"]
    if key not in lifespans:
        return "early"
    lived = character.get("life", {}).get("lived", 0)
    range_min, range_max = (int(x) for x in lifespans[key]["range"].split("-"))
    return band_for(lived, range_min, range_max)


def arc_pressure(character: dict, key: str) -> float:
    arc = character.get("arc") or {}
    stage = arc_stage(arc)
    band = character_band(character, key)
    pressure = _S["arc_pressure_stage_weight"][stage] + _S["arc_pressure_urgency_bonus"][band]
    return max(0.0, min(1.0, pressure))


def roll(character: dict, key: str, home_location: str) -> dict:
    arc = character.get("arc") or {}
    if arc.get("resolution") != "ongoing":
        return {"choice": "survive", "reason": "no_ongoing_arc", "odds_used": None}

    energy = character.get("energy", _S["energy_cap"])
    affinity = net_affinity(character)
    pressure = arc_pressure(character, key)
    per_capita = wealth_lib.wealth_per_capita(home_location)
    threshold = _S["provides_wealth_threshold"]
    pool_surplus = max(-1.0, min(1.0, (per_capita - threshold) / threshold)) if threshold else 0.0

    w = _S["weights"]
    pct = _S["odds_percent"]["arc_base"]
    pct += w["energy"] * (energy / _S["energy_cap"] - 0.5) * 2
    pct += w["arc_pressure"] * (pressure * 2 - 1)
    pct += w["pool_reliance"] * pool_surplus * affinity
    pct -= w["affinity_obligation"] * affinity
    pct = max(_S["odds_percent"]["min"], min(_S["odds_percent"]["max"], pct))

    choice = "arc" if random.random() < (pct / 100.0) else "survive"
    return {
        "choice": choice, "reason": None, "odds_used": round(pct, 1),
        "energy": energy, "arc_pressure": round(pressure, 2),
        "pool_surplus": round(pool_surplus, 2), "net_affinity": round(affinity, 2),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--key", required=True)
    parser.add_argument("--location", required=True, help="This character's own home location (their `location` field), not the pass's eventual resolved location")
    args = parser.parse_args()

    key = args.key.lower()
    char_path = CHAR_DIR / f"{key}.json"
    if not char_path.exists():
        raise SystemExit(f"No character file for '{key}'.")
    with open(char_path, encoding="utf-8") as f:
        character = json.load(f)

    result = roll(character, key, args.location)
    print(f"choice: {result['choice']}")
    if result["reason"]:
        print(f"reason: {result['reason']}")
    if result["odds_used"] is not None:
        print(f"odds_used: {result['odds_used']}")
        print(f"energy: {result['energy']}")
        print(f"arc_pressure: {result['arc_pressure']}")
        print(f"pool_surplus: {result['pool_surplus']}")
        print(f"net_affinity: {result['net_affinity']}")


if __name__ == "__main__":
    main()

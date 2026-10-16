"""
Roll whether a character spends this pass working (which pays them provisions and feeds the local
pool) or pursuing their arc (spending extra energy, on a bet that this pass advances something) - a weighted dice roll, not a model's judgment call, same
"skew, never decide" philosophy as every other roll in this pipeline (roll_contested.py in
particular is the closest precedent: a base percentage, shifted point-by-point by each real input,
clamped, then rolled).

Design session 2026-08-28 - see TODO.md's "Survival mechanism" entry for the full worked-through
math and CHRONICLE.md's matching entry for how each input got settled. Six inputs, each contributing
a percentage-point shift toward "arc" (or away from it, negative; the arithmetic is the pure `arc_odds()` below, shared with
scripts/test/balance_economy.py):

  - **energy** - more personal buffer, safer to gamble. Normalized around the cap's midpoint.
  - **arc_pressure** - how much this arc wants pursuing right now: its own tally stage (early/mid/
    about to resolve) plus how much time this character reads as having left (horizon.py's band -
    a character who's "late" leans harder into their arc, less to lose).
  - **pool_reliance** - a healthy local provisions pool only feels like a safety net if this character
    is actually connected to the people sharing it (net_affinity) - reliance is pool_surplus AMPLIFIED
    by affinity, not an input on its own. An isolated character in a well-provisioned town doesn't get
    to lean on provisions they don't feel part of.
  - **affinity_obligation** - the SAME net_affinity number, independently, pulling the other way: the
    more bonded a character is, the more duty-bound to work for the collective, regardless of the
    pool's own health.
  - **scarcity_pressure** (added 2026-08-29) - lets a character anticipate trouble ahead, not just
    react to the pool's current level: how much the pool's own per-capita provisions has fallen since
    apply_upkeep.py's last checkpoint for this location (provisions_lib.provisions_trend()). Deliberately
    one-directional, same asymmetry pool_reliance/affinity_obligation already apply to net_affinity -
    a declining trend pushes toward "work" (contribute now, before it's worse), but a recovering
    trend applies no extra pull toward "arc" at all.
  - **personal_cushion** (added 2026-09-13, see TODO.md's "Personal provisions and inheritance
    economy" entry) - the opposite economic intuition from pool_reliance: a character's OWN
    `provisions` field (lazily defaulted, `_lore/characters/_template.json`), normalized the same way
    pool_reliance's pool_surplus is (against provides_provisions_threshold), but pushing toward "arc"
    rather than "work" - a healthy personal reserve is what makes gambling on the arc feel safe
    this pass, independent of the communal pool's own health or who this character is bonded to.
    Distinct scope from pool_reliance/affinity_obligation on purpose: those two are about the
    *communal* pool and this character's ties to the people sharing it; this one is about what this
    character holds personally, and nothing else.

Temperament (added 2026-10-17, TODO.md 'Temperament traits and recent trends in the work roll'): four
per-character traits (risk, thrift, communality, persistence) scale the weights above, and a short
window of the character's own recent observations (`recent`) generalizes `scarcity_pressure` into
rates of change of the pool and of the character's own provisions. See arc_odds()'s docstring and
temperament.py; the knobs are `_lore/tuning.json` `temperament`. A character with neither is rolled
as before. The roll is still one seeded draw against the odds.

net_affinity itself is Sum(partners_quality[p]) / Sum(partners[p]) across ESTABLISHED partners only
(count >= partner_threshold, same bar roll_contested.py already uses) - a character with many strong
but negative bonds gets pushed the correct direction on both terms, not just one, since it's one
signed number playing two roles.

A character with no ongoing arc has nothing to pursue this pass - always works, no roll needed.

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
import sys
from pathlib import Path
from random import Random

SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT = SCRIPTS_DIR.parent.parent
CHAR_DIR = ROOT / "_lore" / "characters"
LIFESPANS_PATH = CHAR_DIR / "lifespans.json"

sys.path.insert(0, str(SCRIPTS_DIR))
import tuning  # noqa: E402
import provisions_lib  # noqa: E402
import temperament  # noqa: E402
from horizon import band_for  # noqa: E402

_T = tuning.load()
_ARC_THRESHOLD = _T["arc_resolution_threshold"]
_PARTNER_THRESHOLD = _T["partner_threshold"]
_S = _T["survival"]
_TEMP = _T["temperament"]


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
        lifespans = json.load(f).get("lifespans", {})
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


def arc_odds(s: dict, energy: float, affinity: float, pressure: float,
             per_capita: float, trend: float, provisions: float,
             traits: dict | None = None, recent: list | None = None, t: dict | None = None) -> dict:
    """The work-vs-arc odds as a pure function: `s` is tuning's `survival` block, the rest are the
    raw inputs (`per_capita` and `trend` are the location pool's per-capita provisions and its change
    since the last checkpoint; `provisions` is the character's own). Returns the clamped percentage
    chance of "arc" and the normalized terms. No I/O - the balance script calls this same function.

    Temperament (TODO.md, 'Temperament traits and recent trends'): `t` is tuning's `temperament`
    block, `traits` the character's {risk, thrift, communality, persistence} (missing = 0) and `recent`
    its window of own observations. With `t` None the roll is exactly the pre-temperament one. With
    neutral traits and no window it is that roll too, except that the pool term is centred on the
    world's `pool_comfortable_meals` instead of the old threshold. The traits only scale weights above:
      - risk: the personal cushion is centred on the reserve wanted (arc_need_cost + margin meals), as a
        difference from a neutral character's; the threat terms (negative energy, falling pool or purse)
        are scaled by 1 - threat_k x risk; the bold are pulled a little by a RISE (rise_pull).
      - communality scales the affinity-obligation term only, never pool reliance.
      - persistence adds to the arc-pressure term.
      - thrift scales how much a falling purse (the character's own provisions) weighs.
    The trend: with a window of two or more observations, the pool's rate and the purse's rate come from
    it (temperament.rates, window lengths by risk and thrift); without one, the old checkpoint trend."""
    threshold = s["provides_provisions_threshold"]
    tr = temperament.traits_of(traits) if t else dict(temperament.NEUTRAL)
    eat = s["eat_amount"]
    comfortable = t["pool_comfortable_meals"] * eat if t else threshold
    pool_surplus = max(-1.0, min(1.0, (per_capita - comfortable) / comfortable)) if comfortable else 0.0
    trend_normalized = max(-1.0, min(1.0, trend / threshold)) if threshold else 0.0
    shift = temperament.reserve_shift(tr["risk"], eat, t["risk"]) if t else 0.0
    personal_cushion = max(-1.0, min(1.0, (provisions - threshold - shift) / threshold)) if threshold else 0.0
    threat = temperament.threat_factor(tr["risk"], t["risk"]) if t else 1.0

    w = s["weights"]
    pct = s["odds_percent"]["arc_base"]
    energy_term = w["energy"] * (energy / s["energy_cap"] - 0.5) * 2
    if energy_term < 0:
        energy_term *= threat
    pct += energy_term
    pressure_term = (pressure * 2 - 1) + (t["persistence"]["pressure_k"] * tr["persistence"] if t else 0.0)
    pct += w["arc_pressure"] * max(-1.0, min(1.0, pressure_term))
    pct += w["pool_reliance"] * pool_surplus * affinity
    pct -= w["affinity_obligation"] * affinity * (temperament.obligation_factor(tr["communality"], t["communality"]) if t else 1.0)

    pool_rate = personal_rate = None
    if t and recent:
        scale = t["trend_scale_meals"] * eat
        pool_rate, personal_rate = temperament.rates(
            recent, scale, temperament.pool_window(tr["risk"], t), temperament.personal_window(tr["thrift"], t))
    pool_effective = pool_rate if pool_rate is not None else trend_normalized
    pct += w["scarcity_pressure"] * min(0.0, pool_effective) * threat
    personal_term = pull = 0.0
    if personal_rate is not None:
        personal_term = (t["personal_trend_weight"] * min(0.0, personal_rate)
                         * temperament.personal_trend_factor(tr["thrift"], t["thrift"]) * threat)
    if pool_rate is not None or personal_rate is not None:
        rise = (max(0.0, pool_rate or 0.0) + max(0.0, personal_rate or 0.0)) / 2
        pull = t["risk"]["rise_pull"] * max(0.0, tr["risk"]) * rise
    pct += personal_term + pull
    pct += w["personal_cushion"] * personal_cushion
    pct = max(s["odds_percent"]["min"], min(s["odds_percent"]["max"], pct))
    return {"pct": pct, "pool_surplus": pool_surplus, "trend": pool_effective,
            "personal_trend": personal_rate or 0.0, "rise_pull": pull,
            "personal_cushion": personal_cushion}


def roll(character: dict, key: str, home_location: str, rng: Random | None = None) -> dict:
    rng = rng or Random()
    arc = character.get("arc") or {}
    if arc.get("resolution") != "ongoing":
        return {"choice": "work", "reason": "no_ongoing_arc", "odds_used": None}

    energy = character.get("energy", _S["energy_cap"])
    affinity = net_affinity(character)
    pressure = arc_pressure(character, key)
    odds = arc_odds(
        _S, energy, affinity, pressure,
        provisions_lib.provisions_per_capita(home_location),
        provisions_lib.provisions_trend(home_location),
        character.get("provisions", _S["starting_provisions_per_capita"]),
        traits=character.get("temperament"), recent=character.get("recent"), t=_TEMP,
    )
    pct = odds["pct"]

    choice = "arc" if rng.random() < (pct / 100.0) else "work"
    return {
        "choice": choice, "reason": None, "odds_used": round(pct, 1),
        "energy": energy, "arc_pressure": round(pressure, 2),
        "pool_surplus": round(odds["pool_surplus"], 2), "net_affinity": round(affinity, 2),
        "scarcity_trend": round(odds["trend"], 2), "personal_trend": round(odds["personal_trend"], 2),
        "rise_pull": round(odds["rise_pull"], 1),
        "personal_cushion": round(odds["personal_cushion"], 2),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--key", required=True)
    parser.add_argument("--location", required=True, help="This character's own home location (their `location` field), not the pass's eventual resolved location")
    parser.add_argument("--seed", type=int, default=None, help="Optional seed, for a reproducible roll")
    args = parser.parse_args()

    key = args.key.lower()
    char_path = CHAR_DIR / f"{key}.json"
    if not char_path.exists():
        raise SystemExit(f"No character file for '{key}'.")
    with open(char_path, encoding="utf-8") as f:
        character = json.load(f)

    result = roll(character, key, args.location, rng=Random(args.seed))
    print(f"choice: {result['choice']}")
    if result["reason"]:
        print(f"reason: {result['reason']}")
    if result["odds_used"] is not None:
        print(f"odds_used: {result['odds_used']}")
        print(f"energy: {result['energy']}")
        print(f"arc_pressure: {result['arc_pressure']}")
        print(f"pool_surplus: {result['pool_surplus']}")
        print(f"net_affinity: {result['net_affinity']}")
        print(f"scarcity_trend: {result['scarcity_trend']}")
        print(f"personal_cushion: {result['personal_cushion']}")
        print(f"personal_trend: {result['personal_trend']}")
        print(f"rise_pull: {result['rise_pull']}")


if __name__ == "__main__":
    main()

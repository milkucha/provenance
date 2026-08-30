"""
Shared plumbing for the survival mechanism's location wealth pool - not a standalone script, import
from a sibling driver (roll_survival.py, apply_survival.py, apply_upkeep.py, simulate_pass_lib.py).

A location's wealth is a plain counter in _lore/wealth.json, keyed by the exact location string a
routine/character uses (e.g. "Tyrnea") - the same string roll_home_visit.py/assemble_location()
already resolve a scene to, no separate location-id scheme invented. A location with no entry yet
defaults to `starting_wealth_per_capita * population` the first time it's read (get_wealth), not to
zero - a town nobody's touched yet isn't assumed to already be starving.

Population is never stored - it's derived live from how many living characters (`life.deceased` not
true) currently have `location` set to that exact string, same lazy-clock precedent horizon.py
already uses for life.lived (nothing here maintains a running count; it's recomputed by scanning
_lore/characters/*.json each time it's asked, cheap at this population size).

Usage (from a sibling script in this same directory):
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import wealth_lib
    pop = wealth_lib.population_of("Tyrnea")
    per_capita = wealth_lib.wealth_per_capita("Tyrnea")
"""

import json
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT = SCRIPTS_DIR.parent.parent
CHAR_DIR = ROOT / "_lore" / "characters"
WEALTH_PATH = ROOT / "_lore" / "wealth.json"

sys.path.insert(0, str(SCRIPTS_DIR))
import tuning  # noqa: E402

_T = tuning.load()["survival"]
STARTING_WEALTH_PER_CAPITA = _T["starting_wealth_per_capita"]


def _load() -> dict:
    if not WEALTH_PATH.exists():
        return {"pools": {}}
    with open(WEALTH_PATH, encoding="utf-8") as f:
        return json.load(f)


def _save(data: dict) -> None:
    with open(WEALTH_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def population_of(location: str) -> int:
    """Living characters currently at exactly this location string. A transit-context route string
    (e.g. "Tyrnea <-> the harvest fields") is its own bucket, same pre-existing gap TODO.md's
    "transit context" entry already flags - not resolved here."""
    count = 0
    for path in CHAR_DIR.glob("*.json"):
        if path.name in ("hearsay.md", "lifespans.json", "_template.json"):
            continue
        with open(path, encoding="utf-8") as f:
            try:
                char = json.load(f)
            except json.JSONDecodeError:
                continue
        if char.get("location") == location and not char.get("life", {}).get("deceased"):
            count += 1
    return count


def get_wealth(location: str) -> float:
    data = _load()
    if location in data["pools"]:
        return data["pools"][location]
    seeded = STARTING_WEALTH_PER_CAPITA * max(1, population_of(location))
    data["pools"][location] = seeded
    _save(data)
    return seeded


def set_wealth(location: str, value: float) -> None:
    data = _load()
    data["pools"][location] = value
    _save(data)


def wealth_per_capita(location: str) -> float:
    pop = population_of(location)
    if pop == 0:
        return 0.0
    return get_wealth(location) / pop


def wealth_trend(location: str) -> float:
    """Current per-capita wealth minus whatever it was the last time apply_upkeep.py checkpointed
    this location (checkpoint_wealth_trend(), below) - positive means recovering, negative means
    declining, 0.0 if no checkpoint exists yet (first time this location is ever touched). Read-only,
    never advances the checkpoint itself - only apply_upkeep.py does that, once per pass per location,
    same discipline population_of()'s own lazy-clock precedent already uses."""
    data = _load()
    previous = data.get("previous_per_capita", {}).get(location)
    if previous is None:
        return 0.0
    return wealth_per_capita(location) - previous


def checkpoint_wealth_trend(location: str) -> None:
    """Record this location's current per-capita wealth as the new baseline the next
    wealth_trend() call for it will compare against. Call exactly once per pass per location, from
    apply_upkeep.py only (the same single once-per-pass-per-location site the upkeep drain itself
    already uses) - never from roll_survival.py, which only ever reads the trend, not advances it."""
    data = _load()
    data.setdefault("previous_per_capita", {})[location] = wealth_per_capita(location)
    _save(data)

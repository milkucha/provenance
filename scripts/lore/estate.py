"""
Economic inheritance: what a character's personal provisions do when they die. The one function
every death goes through - record_death.py calls it, and every death path (pass_apply.py, the
driver's apply_solo(), /generate's run_pass(), the horizon-ending check, a death in a scene) already
calls record_death.py, so there is no second place to forget.

The author's rule (TODO.md, "Travel as nodes, social circle writer, class through inheritance"):
class works through inheritance of three capitals, each at its own moment - economic (personal
provisions) when a parent dies, social (the circle) at birth, cultural (an arc's tale) when a parent
completes an arc. This is the first one.

THE BEQUEATHAL TAX (the author's answer, 2026-10-17): when there are living children, `estate.bequest_tax`
(tuning.json, 0.5, global) of the estate goes to the provisions pool of the place the character died in
(their `location` string) and the rest is split equally among the living children. It is the sink the
reward-driven wealth growth needed: a bequest feeds the commons first. With no living children the
whole estate goes to that same pool (it already did). A death on a road has no pool to give to
(provisions_lib.has_pool), so what was due to it is lost there. A completion bonus is not a separate
estate item: it is part of the completer's own provisions already (arc_completion.py) and so
inherited (and taxed) like the rest.

The dead character's own `provisions` is set to 0 afterwards, so nothing is counted twice. Splitting
is exact (a 5 among 2 heirs is 2.5 each); eating floors to whole units already, so a half unit waits
until it adds up.

Usage (import):
    import estate
    result = estate.inherit("khaoe")
    # {"amount": 5, "heirs": ["a", "b"], "to_heirs": 2.5, "pool": "Tyrnea", "to_pool": 2.5}
CLI (for inspection, writes the same way):
    py scripts/lore/estate.py khaoe
"""

import json
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT = SCRIPTS_DIR.parent.parent
CHAR_DIR = ROOT / "_lore" / "characters"

sys.path.insert(0, str(SCRIPTS_DIR))
import provisions_lib  # noqa: E402
import tuning  # noqa: E402

_SKIP = {"_template", "lifespans"}


def _load(key: str) -> dict:
    with open(CHAR_DIR / f"{key}.json", encoding="utf-8") as f:
        return json.load(f)


def _save(key: str, character: dict) -> None:
    with open(CHAR_DIR / f"{key}.json", "w", encoding="utf-8") as f:
        json.dump(character, f, indent=2, ensure_ascii=False)
        f.write("\n")


def living_children(key: str) -> list:
    """Sorted keys of every living character whose `parents` names `key`."""
    out = []
    for path in sorted(CHAR_DIR.glob("*.json")):
        if path.stem in _SKIP:
            continue
        with open(path, encoding="utf-8") as f:
            try:
                other = json.load(f)
            except json.JSONDecodeError:
                continue
        if key in (other.get("parents") or []) and not (other.get("life") or {}).get("deceased"):
            out.append(path.stem)
    return out


def split(amount: float, n_heirs: int, tax: float) -> tuple:
    """(to_pool, to_each_heir): the tax share off the top to the pool, the rest equally among the heirs.
    With no heirs everything goes to the pool. Pure, so the balance script calls this same rule."""
    if n_heirs <= 0:
        return amount, 0.0
    to_pool = amount * tax
    return to_pool, (amount - to_pool) / n_heirs


def inherit(key: str) -> dict:
    """Settle `key`'s personal provisions: `estate.bequest_tax` of it to the pool of the place they died
    in and the rest in equal shares to their living children, or all of it to that pool with no living
    children. Returns {"amount", "heirs", "to_heirs", "pool", "to_pool"}: `pool` is the location string
    that received something, else None; `to_heirs` and `to_pool` are the totals moved. Safe to call on
    someone with nothing: amount 0, nothing moves."""
    character = _load(key)
    cfg = tuning.load()
    default = cfg["survival"]["starting_provisions_per_capita"]
    tax = float((cfg.get("estate") or {}).get("bequest_tax", 0.0))
    amount = character.get("provisions", default)
    result = {"amount": amount, "heirs": [], "to_heirs": 0, "pool": None, "to_pool": 0}
    if amount <= 0:
        return result

    heirs = living_children(key)
    to_pool, share = split(amount, len(heirs), tax)
    if heirs:
        for heir in heirs:
            h = _load(heir)
            h["provisions"] = h.get("provisions", default) + share
            _save(heir, h)
        result["heirs"] = heirs
        result["to_heirs"] = share * len(heirs)
    if to_pool > 0:
        location = character.get("location") or ""
        provisions_lib.set_provisions(location, provisions_lib.get_provisions(location) + to_pool)
        result["pool"] = location
        result["to_pool"] = to_pool

    character["provisions"] = 0
    _save(key, character)
    return result


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    print(json.dumps(inherit(sys.argv[1].lower())))

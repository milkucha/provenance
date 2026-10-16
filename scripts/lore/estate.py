"""
Economic inheritance: what a character's personal provisions do when they die. The one function
every death goes through - record_death.py calls it, and every death path (pass_apply.py, the
driver's apply_solo(), /generate's run_pass(), the horizon-ending check, a death in a scene) already
calls record_death.py, so there is no second place to forget.

The author's rule (TODO.md, "Travel as nodes, social circle writer, class through inheritance"):
class works through inheritance of three capitals, each at its own moment - economic (personal
provisions) when a parent dies, social (the circle) at birth, cultural (an arc's tale) when a parent
completes an arc. This is the first one: the estate is split equally among the LIVING children.

Where the author's spec was silent (logged in OPEN_QUESTIONS.md, "Class through inheritance"): with
no living children the estate goes to the provisions pool of the place the character died in (their
`location` string), so the food stays where they lived instead of vanishing. A completion bonus is
not a separate estate item: it is part of the completer's own provisions already (arc_completion.py)
and so inherited like the rest.

The dead character's own `provisions` is set to 0 afterwards, so nothing is counted twice. Splitting
is exact (a 5 among 2 heirs is 2.5 each); eating floors to whole units already, so a half unit waits
until it adds up.

Usage (import):
    import estate
    result = estate.inherit("khaoe")   # {"amount": 5, "heirs": ["a", "b"], "pool": None}
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


def inherit(key: str) -> dict:
    """Move `key`'s personal provisions to their living children (equal shares) or, with none, to the
    pool of the place they died in. Returns {"amount", "heirs", "pool"} (`pool` is the location
    string that received it, else None). Safe to call on someone with nothing: amount 0, nothing moves."""
    character = _load(key)
    default = tuning.load()["survival"]["starting_provisions_per_capita"]
    amount = character.get("provisions", default)
    result = {"amount": amount, "heirs": [], "pool": None}
    if amount <= 0:
        return result

    heirs = living_children(key)
    if heirs:
        share = amount / len(heirs)
        for heir in heirs:
            h = _load(heir)
            h["provisions"] = h.get("provisions", default) + share
            _save(heir, h)
        result["heirs"] = heirs
    else:
        location = character.get("location") or ""
        provisions_lib.set_provisions(location, provisions_lib.get_provisions(location) + amount)
        result["pool"] = location

    character["provisions"] = 0
    _save(key, character)
    return result


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    print(json.dumps(inherit(sys.argv[1].lower())))

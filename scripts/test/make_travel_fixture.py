"""
Builds a throwaway TEST root with a chain of connected places and a population that has to walk it, so
travel (roads as nodes, meetings on the road, eating from your own provisions) can be exercised without
any lore in the repo. Nothing is added to the engine's own _lore/: the root is written to --out (a new,
empty directory, outside the repo), made of a copy of this checkout's scripts/ and _lore/ plus generated
encodings, characters and lifespans. The place names are placeholders (alpha, beta, ...).

Shape (seeded, generic):
  - N places in a chain, `routes[]` with two endpoints each; the roads between them are NOT written
    anywhere, the engine derives them (travel_graph.build_graph).
  - The last place is the only one with a market routine (provides `materials`); everyone elsewhere has
    home and commons routines and an ongoing arc that needs `materials`, so they set out for the far
    end. The last place's people have a market routine only and an arc that needs `records` (a home
    context provides it), so they walk the other way: opposing traffic, which is what puts two
    travellers on one road.
  - Everyone knows every place (`places_visited`), so every place is a reachable destination.
  - Half of each travelling group starts with provisions to pay with (--rich), the rest with the default.

Usage:
    py scripts/test/make_travel_fixture.py --out /tmp/travel_root --places 4 --per-place 6 --seed 3
Then, e.g.:
    py scripts/test/audit_simulate.py --root /tmp/travel_root --passes 150 --seed 5 --fixture none
"""

import argparse
import json
import shutil
import sys
from pathlib import Path
from random import Random

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
GREEK = ["alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta"]


def build(out: Path, places: int = 4, per_place: int = 6, seed: int = 1, rich: float = 0.5, repo: Path = REPO) -> dict:
    """Writes the root and returns {"places": [...], "characters": [...], "need": ..., "far_need": ...}."""
    if out.exists() and any(out.iterdir()):
        raise SystemExit(f"{out} is not empty; give --out a new directory.")
    out.mkdir(parents=True, exist_ok=True)
    ign = shutil.ignore_patterns("__pycache__", ".git")
    shutil.copytree(repo / "scripts", out / "scripts", ignore=ign)
    shutil.copytree(repo / "_lore", out / "_lore", ignore=shutil.ignore_patterns("__pycache__", ".git", "characters"))
    chars_dir = out / "_lore" / "characters"
    chars_dir.mkdir()
    for name in ("_template.json", "lifespans.json", "_index.md", "hearsay.md"):
        if (repo / "_lore" / "characters" / name).exists():
            shutil.copy(repo / "_lore" / "characters" / name, chars_dir / name)

    rng = Random(seed)
    ids = GREEK[:places]
    enc_path = out / "_lore" / "encodings.json"
    enc = json.loads(enc_path.read_text(encoding="utf-8"))
    enc["locations"] = [{"id": i, "names": [i.capitalize()], "description": f"{i.capitalize()}, a test place.", "sources": []} for i in ids]
    enc["routes"] = [{"id": f"link_{a}_{b}", "endpoints": [a, b], "sources": []} for a, b in zip(ids, ids[1:])]
    enc_path.write_text(json.dumps(enc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    template = json.loads((chars_dir / "_template.json").read_text(encoding="utf-8"))
    lifespans = {}
    made = []
    for pi, place in enumerate(ids):
        far = pi == places - 1
        for n in range(per_place):
            key = f"{place}_{n}"
            c = json.loads(json.dumps(template))
            c.update(name=key.replace("_", " ").title(), origin=place, location=place, places_visited=list(ids))
            c["backstory"] = f"A test resident of {place}."
            c["criterion"].update(standard="keeps to the work", wasted_life="a life spent idle", trusts="neighbours", distrusts="strangers", anchor="the work")
            c["routines"] = (
                [{"location": place, "context": "market", "weight": 100, "routine_actions": "trades at the stalls"}] if far else
                [{"location": place, "context": "home", "weight": 60, "routine_actions": "keeps house"},
                 {"location": place, "context": "commons", "weight": 40, "routine_actions": "crosses the square"}]
            )
            c["arc"].update(
                about=["concept: test"], needs=["records" if far else "materials"], resolution="ongoing",
                context="market" if far else "home", premise="Wants what only the other end has.",
            )
            if rng.random() < rich:
                c["provisions"] = 8
            c["life"] = {"lived": 0, "deceased": False}
            (chars_dir / f"{key}.json").write_text(json.dumps(c, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            lifespans[key] = {"span": 400, "range": "300-500"}
            made.append(key)
    (chars_dir / "lifespans.json").write_text(json.dumps({"lifespans": lifespans}, indent=2) + "\n", encoding="utf-8")
    return {"places": ids, "characters": made, "need": "materials", "far_need": "records"}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True, help="a new, empty directory (outside the repo)")
    ap.add_argument("--places", type=int, default=4)
    ap.add_argument("--per-place", type=int, default=6)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--rich", type=float, default=0.5, help="share of characters starting with provisions to pay with")
    a = ap.parse_args()
    info = build(Path(a.out).resolve(), a.places, a.per_place, a.seed, a.rich)
    print(json.dumps({"out": a.out, **{k: info[k] for k in ("places", "need", "far_need")}, "characters": len(info["characters"])}))


if __name__ == "__main__":
    sys.exit(main())

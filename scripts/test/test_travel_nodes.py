"""
Mechanical checks for travel as nodes (TODO.md, "Travel as nodes"): roads are derived nodes between
places, a road has no provisions pool, and a seeded run over a travel fixture replays exactly. No model,
no Ollama; every roll goes through the seeded rng_context.

  1. Unit: A to B is 2 hops, B to C through A is 4; the road id is the same whichever way a connection
     is written; the destination weight is unchanged per CONNECTION (it was per hop when a hop was a
     connection).
  2. Economy: on a road, apply_upkeep.py and apply_survival.py create no pool and drain nothing; with
     no provisions a traveller gets no meal and loses energy, and can die.
  3. Seeded pair: scripts/test/audit_simulate.py run twice on a generated travel root with the same seed
     under two different PYTHONHASHSEEDs (--dump keeps the end state): the draw audit (minus its wall
     clock timestamp), every character file and the pools must be identical. Prints the pursuit-stage
     distribution of the run.

Usage:
    py scripts/test/test_travel_nodes.py                 # all three
    py scripts/test/test_travel_nodes.py --skip-pair     # only the quick ones
    py scripts/test/test_travel_nodes.py --passes 150 --seed 5
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "scripts" / "lore"))
sys.path.insert(0, str(HERE))
import travel_graph as tg  # noqa: E402
import location_context as lc  # noqa: E402
import make_travel_fixture  # noqa: E402


def check(label: str, ok: bool) -> None:
    print(("  OK   " if ok else "  FAIL ") + label)
    if not ok:
        raise SystemExit(1)


def test_graph() -> None:
    print("graph")
    enc = {"locations": [{"id": i} for i in "abc"], "routes": [{"endpoints": ["a", "b"]}, {"endpoints": ["c", "a"]}]}
    g = tg.build_graph(enc)
    _, p_ab = tg.shortest_path(g, "a", {"b"})
    _, p_bc = tg.shortest_path(g, "b", {"c"})
    check(f"A to B is 2 hops: {p_ab}", len(p_ab) - 1 == 2)
    check(f"B to C through A is 4 hops: {p_bc}", len(p_bc) - 1 == 4)
    check("connections(): 2 hops = 1, 4 hops = 2", tg.connections(p_ab) == 1 and tg.connections(p_bc) == 2)
    rev = tg.build_graph({"locations": enc["locations"], "routes": [{"endpoints": ["b", "a"]}, {"endpoints": ["a", "c"]}]})
    check("road ids do not depend on the order endpoints are written", set(rev) == set(g))
    check("a road joins exactly its two ends", g["road:a--b"] == {"a", "b"} and tg.road_endpoints("road:a--c") == ("a", "c"))
    check("two routes on one pair share one road", len([n for n in tg.build_graph({"locations": enc["locations"], "routes": [{"endpoints": ["a", "b"]}, {"endpoints": ["b", "a"]}]}) if tg.is_road(n)]) == 1)
    try:
        tg.build_graph({"routes": [{"endpoints": ["a--x", "b"]}]})
        check("an id with '--' is refused", False)
    except ValueError:
        check("an id with '--' is refused", True)
    d = tg.describe_road("road:a--b", {"locations": [{"id": "a", "names": ["Aa"]}, {"id": "b", "names": ["Bb"]}], "routes": []})
    check(f"place block from a template on the endpoints' names: {d['name']!r}", d["name"] == "The road between Aa and Bb")

    # distance weight per connection: a chain 1, 2, 3 connections away, all general; weights 2, 1, 0.5
    chain = {"locations": [{"id": i} for i in "abcd"], "routes": [{"endpoints": [x, y]} for x, y in zip("abc", "bcd")]}
    ctx = {"market": {"provides": ["materials"]}}
    people = [{"routines": [{"location": loc, "context": "market", "weight": 100}]} for loc in "bcd"]
    trav = {"location": "a", "places_visited": list("bcd"), "partners": {}, "social_circle": [], "parents": []}
    opts = {o["location"]: o for o in lc.destination_options(trav, "materials", chain, people, ctx, {"known_supplier_weight": 6, "general_weight": 2, "hop_decay": 0.5})}
    check(f"weights per connection: {[(k, o['hops'], o['connections'], o['weight']) for k, o in opts.items()]}",
          [opts[k]["weight"] for k in "bcd"] == [2.0, 1.0, 0.5] and [opts[k]["hops"] for k in "bcd"] == [2, 4, 6])


def _run(root: Path, *argv) -> str:
    r = subprocess.run([sys.executable, *map(str, argv)], capture_output=True, text=True, cwd=root)
    if r.returncode:
        raise SystemExit(f"FAILED {argv}\n{r.stderr[-800:]}")
    return r.stdout


def kv(out: str) -> dict:
    return {k.strip(): v.strip() for k, _, v in (l.partition(":") for l in out.splitlines() if l and l[0] not in " \t")}


def test_economy() -> None:
    print("economy on a road")
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "root"
        make_travel_fixture.build(root, places=2, per_place=2, seed=1)
        road = tg.road_id("alpha", "beta")
        S = root / "scripts" / "lore"
        cp = root / "_lore" / "characters" / "alpha_0.json"
        c = json.loads(cp.read_text())
        c.update(location=road, provisions=0, energy=6)
        cp.write_text(json.dumps(c))
        pools = root / "_lore" / "provisions.json"
        up = kv(_run(root, S / "apply_upkeep.py", "--location", road))
        check(f"upkeep on a road: nothing drains ({up})", up["upkeep"] == "0" and up["pool"] == "0")
        check("... and no pool file or entry appears", not pools.exists())
        out = kv(_run(root, S / "apply_survival.py", "--key", "alpha_0", "--location", road, "--choice", "arc"))
        check(f"no provisions, no pool: no meal, energy 6 -1 -1 = 4 ({out})", out["ate"] == "none" and out["energy"] == "4" and out["died"] == "false")
        check("... and still no pool", not pools.exists() or road not in json.loads(pools.read_text()).get("pools", {}))
        c = json.loads(cp.read_text())
        c.update(provisions=2, energy=6)
        cp.write_text(json.dumps(c))
        out = kv(_run(root, S / "apply_survival.py", "--key", "alpha_0", "--location", road, "--choice", "arc"))
        check(f"with 2 provisions on the road both units come from them ({out})", out["ate"] == "full" and out["provisions"] == "0" and out["energy"] == "6")
        c = json.loads(cp.read_text())
        c.update(provisions=0, energy=2)
        cp.write_text(json.dumps(c))
        out = kv(_run(root, S / "apply_survival.py", "--key", "alpha_0", "--location", road, "--choice", "arc"))
        check(f"a hungry traveller can starve on the road ({out})", out["died"] == "true")
        # the pass itself: a hungry traveller steps from alpha onto the road with nothing to eat, journey kept,
        # dies en route. The work-or-arc roll is forced to arc (an exhausted character almost never rolls arc).
        c = json.loads(cp.read_text())
        c.update(location="alpha", provisions=0, energy=2, pursuit={"need": "materials", "target": "beta", "origin": "alpha", "since_pass": 1})
        c["life"] = {"lived": 0, "deceased": False}
        cp.write_text(json.dumps(c))
        code = ("import json, sys; sys.path.insert(0, 'scripts/lore'); import simulate_pass_lib as lib; "
                "lib.roll_survival = lambda k, h: {'choice': 'arc'}; "
                "b = lib.run_pass_mechanics('alpha_0', 1); print(json.dumps({'stage': b['pursuit']['stage'], 'location': b['location'], 'scene': b['scene']}))")
        r = json.loads(subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, cwd=root, check=True).stdout)
        check(f"died_en_route on the first road node, no scene ({r})", r == {"stage": "died_en_route", "location": road, "scene": None})
        import pass_prep
        enc = json.loads((root / "_lore" / "encodings.json").read_text())
        pb = pass_prep.place_block(road, enc)
        check(f"the enacter's place block for a road is the template: {pb['name']!r}", pb["name"] == "The road between Alpha and Beta")
        check("population_of works for a road", __import__("subprocess").run(
            [sys.executable, "-c", f"import sys; sys.path.insert(0, {str(S)!r}); import provisions_lib as p; print(p.population_of({road!r}))"],
            capture_output=True, text=True, cwd=root).stdout.strip() == "1")


def test_pair(passes: int, seed: int) -> None:
    print(f"seeded pair, {passes} passes, seed {seed}, PYTHONHASHSEED 1 vs 2")
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        make_travel_fixture.build(td / "root", places=4, per_place=6, seed=3)
        outs = []
        for hs in ("1", "2"):
            env = {**os.environ, "PYTHONHASHSEED": hs}
            r = subprocess.run(
                [sys.executable, str(HERE / "audit_simulate.py"), "--root", str(td / "root"), "--passes", str(passes), "--seed", str(seed),
                 "--fixture", "none", "--dump", str(td / f"dump{hs}"), "--json-out", str(td / f"run{hs}.json")],
                capture_output=True, text=True, env=env)
            if r.returncode:
                raise SystemExit(r.stderr[-1500:])
            outs.append(json.loads((td / f"run{hs}.json").read_text()))

        def log(d: Path) -> list:
            rows = [json.loads(l) for l in (d / ".simulate_draw_audit.jsonl").read_text().splitlines()]
            for row in rows:
                row.pop("timestamp", None)
            return rows

        a, b = td / "dump1", td / "dump2"
        la, lb = log(a), log(b)
        check(f"draw logs identical ({len(la)} draws)", la == lb and len(la) > 0)
        names = sorted(p.name for p in (a / "characters").glob("*.json"))
        check(f"character files identical ({len(names)})", names == sorted(p.name for p in (b / "characters").glob("*.json"))
              and all((a / "characters" / n).read_bytes() == (b / "characters" / n).read_bytes() for n in names))
        pa, pb = a / "provisions.json", b / "provisions.json"
        check("provisions pools identical", pa.read_bytes() == pb.read_bytes())
        check("observed counts identical", outs[0]["observed"] == outs[1]["observed"])
        obs = outs[0]["observed"]
        stages = {k[len("stage_"):]: v for k, v in sorted(obs.items()) if k.startswith("stage_")}
        print("  pursuit stages:", stages)
        print("  scenes:", {k: v for k, v in obs.items() if k.startswith("scene_")}, "| road hops:", obs.get("road_hops", 0),
              "| longest journey (passes):", obs.get("longest_journey_passes", 0), "| died_en_route:", obs.get("died_en_route", 0))
        check("no purchase and no arc outcome on a road scene", obs.get("road_meetings_with_outcome", 0) == 0 and obs.get("met_on_road_with_payment", 0) == 0)
        check("no road pool, road in places_visited, or direct place-to-place edge", not obs.get("road_pools_created") and not obs.get("roads_in_places_visited") and not obs.get("direct_place_to_place_edges"))
        check("the run had multi-hop journeys and road meetings", obs.get("longest_journey_passes", 0) >= 4 and obs.get("stage_met_on_road", 0) > 0)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--skip-pair", action="store_true")
    ap.add_argument("--passes", type=int, default=120)
    ap.add_argument("--seed", type=int, default=5)
    a = ap.parse_args()
    test_graph()
    test_economy()
    if not a.skip_pair:
        test_pair(a.passes, a.seed)
    print("all travel checks passed")


if __name__ == "__main__":
    main()

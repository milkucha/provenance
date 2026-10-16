"""
Balance script for the economy (TODO.md, "Economy rewrite"). Runs a small town through the REAL
rules and prints what happens, so the numbers in _lore/tuning.json get tuned by running them, not by
arguing. No files are read except tuning.json and none are written; seedable; fast.

Real, imported, not copied:
  - economy_rules.resolve_pass / eat / upkeep   (what apply_survival.py and apply_upkeep.py run)
  - roll_survival.arc_odds                      (the work-vs-arc odds, scarcity and cushion feedback included)

SIMPLIFICATIONS (everything the town does that the engine would do differently):
  1. One town, one pool. Population is the number alive; no births, no natural deaths, no migration.
     The only way out is starvation (energy at 0). A dead character's personal provisions vanish.
  2. Each pass one living character is drawn uniformly and is the only one who eats, works or pays
     (as in the engine: p2 gets no energy effect). Order inside a pass is the engine's: upkeep on the
     pool, then base cost, eating, then the choice.
  3. Everyone always has an ongoing arc, so the work-vs-arc roll is always made. The roll's other
     inputs are held fixed for every character: net affinity (--affinity, 0.0) and arc pressure
     (--pressure, 0.5, which cancels out of the odds). Energy, the pool's per-capita level and its
     trend since the last upkeep checkpoint, and the character's own provisions are the real, live values.
  4. An arc pass skips all the travel/meeting/gate machinery: with probability --pay-rate (0.35) the
     character reaches a supplier and tries to pay `arc_need_cost`; the payment goes through whenever
     their provisions (after eating) cover it, and the cost is handed to a uniformly drawn other
     living character. Suppliers' hoards are not spent on anything else. No payment gate roll, no arc
     outcomes, no completed or new arcs.
  5. Upkeep is the engine's flat per-capita drain (`upkeep_rate_per_capita` x population, floor 0),
     taken from the pool every pass. Nothing decays on personal provisions.
  6. Start: pool = 2 x population, personal provisions 2, energy at the cap (the engine's defaults).

Metrics (means over seeds): `alive` fraction at the end; `pc_mean`/`pc_end` pool per capita averaged
over the run / at the end; `pers_mean`/`pers_med` personal provisions of the living at the end;
`work` share of passes in which the choice rolled was work; `starved` deaths per run; `can_pay` share
of ARC passes whose character held at least `arc_need_cost` after eating; `fed` share of passes
in which the pool still held a unit when the meal came (after that pass's upkeep).

Usage:
    py scripts/test/balance_economy.py --pop 12 --seeds 8
    py scripts/test/balance_economy.py --pop 6 12 25 --grid work_pool=0,1,2 upkeep_rate_per_capita=0.05,0.15
    py scripts/test/balance_economy.py --pop 12 --trace          # the run's trajectory, 10 checkpoints
    py scripts/test/balance_economy.py --scan                    # the stable region, N in 6, 12, 25
Parameters (for --grid / --set): work_pool, work_personal, upkeep_rate_per_capita, eat_amount,
arc_need_cost, or any other key of tuning's `survival` block.
"""

import argparse
import itertools
import statistics
import sys
from pathlib import Path
from random import Random

HERE = Path(__file__).resolve().parent
LORE = HERE.parent / "lore"
sys.path.insert(0, str(LORE))
import tuning  # noqa: E402
import economy_rules  # noqa: E402
from roll_survival import arc_odds  # noqa: E402

TUNING = tuning.load()
BASE_S = TUNING["survival"]
BASE_COST = TUNING["arc_payment"]["arc_need_cost"]
CORE = ["work_pool", "work_personal", "upkeep_rate_per_capita", "eat_amount", "arc_need_cost"]
SCAN_GRID = {
    "work_pool": [0, 1, 2, 3, 5, 8],
    "work_personal": [1, 2, 3],
    "upkeep_rate_per_capita": [0.0, 0.05, 0.1, 0.15, 0.2, 0.3],
    "eat_amount": [1, 2, 3],
    "arc_need_cost": [1, 3, 5],
}
SCAN_POPS = [6, 12, 25]


def today() -> dict:
    d = {k: BASE_S[k] for k in CORE if k in BASE_S}
    d["arc_need_cost"] = BASE_COST
    return d


def simulate(pop: int, passes: int, seed: int, params: dict, affinity: float = 0.0,
             pressure: float = 0.5, pay_rate: float = 0.35, trace: int = 0) -> dict:
    s = dict(BASE_S)
    s.update({k: v for k, v in params.items() if k != "arc_need_cost"})
    cost = params.get("arc_need_cost", BASE_COST)
    rng = Random(seed)
    start = s["starting_provisions_per_capita"]
    energy = [s["energy_cap"]] * pop
    personal = [start] * pop
    alive = list(range(pop))
    pool = start * pop
    ckpt = None
    works = arcs = can = starved = fed = 0
    pc_sum = 0.0
    traj = []
    step = max(1, passes // trace) if trace else 0
    for t in range(passes):
        if not alive:
            break
        i = rng.choice(alive)
        n = len(alive)
        per_capita = pool / n
        trend = 0.0 if ckpt is None else per_capita - ckpt
        pct = arc_odds(s, energy[i], affinity, pressure, per_capita, trend, personal[i])["pct"]
        choice = "arc" if rng.random() < pct / 100.0 else "work"
        pool = economy_rules.upkeep(pool, n, s["upkeep_rate_per_capita"])
        ckpt = pool / n
        fed += pool >= 1
        r = economy_rules.resolve_pass(energy[i], personal[i], pool, choice, s)
        energy[i], personal[i], pool = r["energy"], r["personal"], r["pool"]
        if choice == "work":
            works += 1
        else:
            arcs += 1
            if personal[i] >= cost:
                can += 1
                if rng.random() < pay_rate and n > 1:
                    personal[i] -= cost
                    j = rng.choice([k for k in alive if k != i])
                    personal[j] += cost
        if r["died"]:
            alive.remove(i)
            starved += 1
        n = len(alive)
        pc_sum += pool / n if n else 0.0
        if step and (t + 1) % step == 0:
            traj.append((t + 1, n / pop, pool / n if n else 0.0,
                         statistics.mean(personal[k] for k in alive) if alive else 0.0))
    n = len(alive)
    plist = [personal[k] for k in alive]
    done = works + arcs
    return {
        "alive": n / pop, "pc_mean": pc_sum / max(1, passes), "pc_end": pool / n if n else 0.0,
        "pers_mean": statistics.mean(plist) if plist else 0.0,
        "pers_med": statistics.median(plist) if plist else 0.0,
        "work": works / done if done else 0.0, "starved": starved,
        "can_pay": can / arcs if arcs else 0.0, "fed": fed / max(1, passes), "traj": traj,
    }


def average(runs: list) -> dict:
    keys = [k for k in runs[0] if k != "traj"]
    return {k: statistics.mean(r[k] for r in runs) for k in keys}


def run_cell(pop, passes, seeds, seed_base, params, **kw) -> dict:
    n_passes = passes or 40 * pop
    return average([simulate(pop, n_passes, seed_base + s, params, **kw) for s in range(seeds)])


def stable(m: dict, a) -> bool:
    return (m["alive"] >= a.alive_min and a.pc_min <= m["pc_end"] <= a.pc_max and m["pc_mean"] >= a.pc_min
            and m["can_pay"] >= a.can_pay_min)


def parse_values(text: str) -> list:
    out = []
    for v in text.split(","):
        f = float(v)
        out.append(int(f) if f == int(f) and "." not in v else f)
    return out


def parse_grid(items) -> dict:
    grid = {}
    for item in items or []:
        key, _, vals = item.partition("=")
        grid[key] = parse_values(vals)
    return grid


def fmt(v) -> str:
    return f"{v:g}"


def table(rows: list, varying: list) -> None:
    head = ["N"] + varying + ["alive", "pc_mean", "pc_end", "pers_mean", "pers_med", "work", "starved", "can_pay", "fed"]
    lines = [head]
    for pop, params, m in rows:
        lines.append([str(pop)] + [fmt(params[k]) for k in varying] + [
            f"{m['alive']:.2f}", f"{m['pc_mean']:.2f}", f"{m['pc_end']:.2f}", f"{m['pers_mean']:.2f}",
            f"{m['pers_med']:.1f}", f"{m['work']:.2f}", f"{m['starved']:.1f}", f"{m['can_pay']:.2f}", f"{m['fed']:.2f}"])
    widths = [max(len(r[c]) for r in lines) for c in range(len(head))]
    for r in lines:
        print("  ".join(x.rjust(w) for x, w in zip(r, widths)))


def scan(a) -> None:
    grid = parse_grid(a.grid) or SCAN_GRID
    names = list(grid)
    pops = a.pop or SCAN_POPS
    base = today()
    combos = [dict(base, **dict(zip(names, vals))) for vals in itertools.product(*grid.values())]
    print(f"scan: {len(combos)} combos x N {pops} x {a.seeds} seeds; passes = {a.passes or '40 x N'}")
    print(f"stable = alive >= {a.alive_min}, {a.pc_min} <= pool/capita (end) <= {a.pc_max}, pool/capita (mean) >= {a.pc_min}, can_pay >= {a.can_pay_min}")
    ok = {n: set() for n in pops}
    for n in pops:
        for idx, p in enumerate(combos):
            m = run_cell(n, a.passes, a.seeds, a.seed_base, p, affinity=a.affinity, pressure=a.pressure, pay_rate=a.pay_rate)
            if stable(m, a):
                ok[n].add(idx)
        print(f"N={n}: {len(ok[n])}/{len(combos)} stable")
    every = set.intersection(*ok.values())
    print(f"stable at every N: {len(every)}/{len(combos)}")
    for n in pops + [None]:
        sel = every if n is None else ok[n]
        label = "all N" if n is None else f"N={n}"
        print(f"\n{label}: share of stable combos holding each value")
        for name in names:
            parts = []
            for v in grid[name]:
                have = sum(1 for i in sel if combos[i][name] == v)
                tot = sum(1 for p in combos if p[name] == v)
                parts.append(f"{fmt(v)}: {have}/{tot}")
            print(f"  {name:24s} " + "   ".join(parts))
    if every:
        print("\nrange of the stable-at-every-N set: " + "; ".join(
            f"{k} {fmt(min(combos[i][k] for i in every))}..{fmt(max(combos[i][k] for i in every))}" for k in names))
    mine = [i for i, p in enumerate(combos) if all(p[k] == base[k] for k in names)]
    if mine:
        i = mine[0]
        print("\ntoday's values " + ", ".join(f"{k}={fmt(base[k])}" for k in names) + ": "
              + ", ".join(f"N={n} {'stable' if i in ok[n] else 'NOT stable'}" for n in pops))
    else:
        print("\ntoday's values are not a point of this grid")
    if every:
        def dist(i):
            return sum(abs(combos[i][k] - base[k]) / (max(grid[k]) - min(grid[k]) or 1) for k in names)
        print("\nstable at every N, the 8 nearest to today's values:")
        rows = []
        for i in sorted(every, key=dist)[:8]:
            for n in pops:
                rows.append((n, combos[i], run_cell(n, a.passes, a.seeds, a.seed_base, combos[i],
                                                    affinity=a.affinity, pressure=a.pressure, pay_rate=a.pay_rate)))
        table(rows, names)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pop", type=int, nargs="+", default=None, help="population(s); default 12 (scan: 6 12 25)")
    ap.add_argument("--passes", type=int, default=0, help="total passes per run; 0 = 40 x population")
    ap.add_argument("--seeds", type=int, default=6)
    ap.add_argument("--seed-base", type=int, default=1)
    ap.add_argument("--grid", nargs="*", help="key=v1,v2,... for any of the parameters; the table is the product")
    ap.add_argument("--set", nargs="*", help="key=value overrides for every cell")
    ap.add_argument("--affinity", type=float, default=0.0)
    ap.add_argument("--pressure", type=float, default=0.5)
    ap.add_argument("--pay-rate", type=float, default=0.35, help="chance an arc pass reaches a supplier and tries to pay")
    ap.add_argument("--trace", action="store_true", help="print the trajectory of the first cell, 10 checkpoints")
    ap.add_argument("--scan", action="store_true", help="scan the grid for the stable region (default grid: see SCAN_GRID)")
    ap.add_argument("--alive-min", type=float, default=0.9)
    ap.add_argument("--pc-min", type=float, default=0.5, help="pool per capita below this = collapsed")
    ap.add_argument("--can-pay-min", type=float, default=0.0, help="optional extra bar for --scan: share of arc passes able to pay")
    ap.add_argument("--pc-max", type=float, default=8.0, help="pool per capita above this = runaway (4 x the start)")
    a = ap.parse_args()

    if a.scan:
        return scan(a)
    pops = a.pop or [12]
    base = today()
    base.update({k: v[0] for k, v in parse_grid(a.set).items()})
    grid = parse_grid(a.grid)
    names = list(grid)
    cells = [dict(base, **dict(zip(names, vals))) for vals in itertools.product(*grid.values())] or [base]
    kw = dict(affinity=a.affinity, pressure=a.pressure, pay_rate=a.pay_rate)
    rows = [(n, p, run_cell(n, a.passes, a.seeds, a.seed_base, p, **kw)) for n in pops for p in cells]
    print("params: " + ", ".join(f"{k}={fmt(v)}" for k, v in base.items() if k not in names)
          + f" | {a.seeds} seeds, passes {a.passes or '40 x N'}")
    table(rows, names)
    if a.trace:
        n, p = pops[0], cells[0]
        runs = [simulate(n, a.passes or 40 * n, a.seed_base + s, p, trace=10, **kw) for s in range(a.seeds)]
        print(f"\ntrajectory (N={n}, mean over seeds): pass, alive, pool/capita, personal mean")
        for k in range(len(runs[0]["traj"])):
            col = [r["traj"][k] for r in runs if len(r["traj"]) > k]
            print(f"  {col[0][0]:5d}  {statistics.mean(c[1] for c in col):.2f}  "
                  f"{statistics.mean(c[2] for c in col):6.2f}  {statistics.mean(c[3] for c in col):6.2f}")


if __name__ == "__main__":
    main()

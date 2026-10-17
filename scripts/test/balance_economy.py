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

JOURNEYS (--journey, roads as nodes, TODO.md "Travel as nodes"): a walk of k connections is 2k passes of
`arc` for the traveller, road, place, road, place, ... Roads have NO pool, so on a road the meal comes from
the traveller's own provisions only (economy_rules.eat with pool 0); at a place it is the usual meal from
the place's pool (--stop-pool, units, default 4). Worst case on purpose: every pass of the walk is an arc
pass (a work roll mid-journey would feed them, 2 provisions each). Deterministic, no dice; the same
resolve_pass the engine runs. Prints energy on arriving by starting energy and provisions, and the
lowest starting energy that gets there.

Usage:
    py scripts/test/balance_economy.py --journey

GENERATIONS (added 2026-10-17, class through inheritance; `--gens`): the same toy town, now with
births, natural deaths, arcs that complete, and inheritance. Everything below is stated, not
measured; the rules it calls are the real ones (economy_rules, roll_survival.arc_odds,
arc_completion.reward_for, roll_arc_outcome.WEIGHTS).
  G1. Lifespan: each person lives a number of OWN turns drawn uniformly from tuning's
      `lifespan_range` (30 to 60), then dies. (The engine counts scenes lived, which includes turns
      as someone else's p2; own turns are the number the reward is read from, so the two are kept apart.)
  G2. Births: whenever a living adult (5+ own turns, the engine's child cooldown) is drawn and is off
      their parent cooldown (10 passes), they have a child with probability `--birth-rate` (0.04 per
      drawn turn, a stated rate: with the cooldowns it keeps a town that has room at the cap, 0.022 let
      it die out) with
      a random other adult who is not their parent or child. The town is capped at `--cap` x the
      starting population (default 1.5), a stated ceiling. A newborn has
      personal provisions 2 (the engine's default for a field nobody wrote) and joins the draw
      pool 5 passes later. This birth gift is a faucet the engine really has.
  G3. Arcs: everyone starts with an arc, 0 turns. Each own turn on it adds 1. An arc pass that reaches a
      supplier and pays (the existing --pay-rate rule) rolls an outcome with the "neutral" inclination
      (40 advance, 40 stall, 20 reverse, roll_arc_outcome.WEIGHTS); the tally is advances minus
      reverses; at +3 (arc_resolution_threshold) the arc COMPLETES, at -3 it fails. Either way a new
      arc starts at 0 turns. No transform, no contested, no help or hinder: one fixed inclination.
  G4. Completion reward: on a completion only, personal provisions += arc_completion_reward
      (clamp(base + per_turn x turns, min, max)); `--reward off` leaves it out, `--reward uncapped`
      removes the max.
  G5. Death: from age (G1) or starvation. `--inheritance on` settles the dead's personal provisions with
      the real rule (estate.split): `--tax` (default tuning's `estate.bequest_tax`, 0.5) of it into the pool
      and the rest equally among living children, or all of it into the pool if there are none; `off` is the
      old rule, they vanish. `--tax 0` is the old inheritance without the tax. The completion bonus is not a
      separate item, it is in the personal provisions.
Metrics (mean over seeds, at the end and at four checkpoints): `gini` and `top10` (share of all personal
provisions held by the richest tenth of the living), `mean`/`max` personal provisions, `lineage_top`
(share held by the richest founder LINE: each living person is credited to the founder who is
the majority of their ancestry, found by averaging both parents' founder weights), `completions`
and `turns` (mean own turns per completed arc), `born`, `alive`, `gen` (deepest generation alive).

Usage:
    py scripts/test/balance_economy.py --gens 6 --pop 12 --seeds 6
    py scripts/test/balance_economy.py --gens 6 --pop 12 --seeds 6 --compare   # the five cases side by side
    py scripts/test/balance_economy.py --pop 12 --seeds 8
    py scripts/test/balance_economy.py --pop 6 12 25 --grid work_pool=0,1,2 upkeep_rate_per_capita=0.05,0.15
    py scripts/test/balance_economy.py --pop 12 --trace          # the run's trajectory, 10 checkpoints
    py scripts/test/balance_economy.py --scan                    # the stable region, N in 6, 12, 25
TEMPERAMENT (added 2026-10-17; `--traits on|off`, `--traits-report`, `--calibrate`): the same toy town with
the real temperament machinery, so the numbers in tuning's `temperament` block get tuned by running them.
Real, imported: `roll_survival.arc_odds` with traits and the window of recent observations,
`economy_rules.payment_odds` (the payment gate's odds, thrift included), `temperament.*`. Stated, not measured:
  T1. Traits: with `--traits on` each character's four traits are drawn uniformly in [-1, 1] (seeded, its own
      stream so the dice of the town are the same as with `off`); with `off` every trait is 0 (the middle of
      each scale, NOT a neutral that reproduces the old roll: since 2026-10-17 nothing is centred on a neutral
      character, the risk margin runs from 0 meals to 5 and the thrift keep-level from 0 to 3, so a 0 character
      has a 2.5-meal margin and a 1.5-meal keep-level; it is a comparison column, not a baseline).
  T2. Each character keeps up to `recent_window_max` of its own observations (pool per capita, own provisions,
      energy) on its own turns, as the engine does; the roll reads them. `--trend off` gives no window, so the
      old checkpoint scarcity term. `--window global` forces one window length (the neutral 5) on everybody
      with traits otherwise on, to measure what the per-character windows add. `--legacy` is the roll before
      temperament existed (arc_odds with t=None), for the baseline.
  T1b. Each character has a fixed net affinity, `--affinity` (0) plus a uniform draw in [0, 0.5] (its own stream,
      the same on and off), so that the communality and pool-reliance terms, which are multiplied by it, act at all.
  T3. A reached supplier (probability --pay-rate) is a pair scene: if the character holds `arc_need_cost` it
      rolls the REAL payment odds (arc tally 0), thrift hesitation included; and the other participant, drawn
      uniformly, eats (Part A: p2 eats, no pay, no arc cost). Everything else as above (one town, no births).
Metrics added: `work_sd` standard deviation across characters of each one's work share (the point of traits is
variety; over characters with at least 8 turns), `surv_sd` the same for the fraction of the run each lived,
`osc` pool-per-capita amplitude (sd / mean of the per-round means, a round = N passes, first two rounds left
out), `ac1` its lag-1 autocorrelation (a negative one is a swing back and forth), `sync` the sd of the
per-round work share over what independent coin flips would give (about 1 = no synchronization),
`pc_med` the median pool per head (units), `info` the share of own turns on which the pool term was strictly between -1 and +1 (informative), `floor`/`ceil` the share on which it sat at -1 / +1 (pinned; -1 means an empty pool whatever the comfortable level, so the level can only move the other two), `rate_pin` the share of
turns on which the pool rate was at +/-1.

Usage:
    py scripts/test/balance_economy.py --traits on --pop 12 --seeds 10
    py scripts/test/balance_economy.py --traits-report                 # the full comparison, both economies
    py scripts/test/balance_economy.py --calibrate                     # the comfortable pool level

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
import arc_completion  # noqa: E402
import estate  # noqa: E402
import temperament  # noqa: E402
from roll_arc_outcome import WEIGHTS as ARC_WEIGHTS  # noqa: E402
from roll_survival import arc_odds  # noqa: E402

TUNING = tuning.load()
BASE_S = TUNING["survival"]
BASE_COST = TUNING["arc_payment"]["arc_need_cost"]
TEMP = TUNING["temperament"]
PAY = TUNING["arc_payment"]
RICH = {"work_pool": 6, "upkeep_rate_per_capita": 0.05, "work_personal": 3}  # a setting where the pool is a commons, for calibration only
PROPOSAL = {"work_pool": 4, "upkeep_rate_per_capita": 0.05, "work_personal": 3}  # adopted 2026-10-17 (the first adoption), the economy BEFORE the calibration for variation, kept for the tables
OLD = {"work_pool": 1, "upkeep_rate_per_capita": 0.15, "work_personal": 2}  # the numbers before that adoption
# The temperament numbers BEFORE the calibration for variation (2026-10-17, second pass): the cushion divided by the
# 2-unit threshold (no cushion_scale_meals), the cautious margin 5 meals, persistence pressure 0.3. Everything else was and is as tuning.json.
BEFORE_TEMP = {**TUNING["temperament"], "cushion_scale_meals": 0,
               "risk": {**TUNING["temperament"]["risk"], "margin_meals_cautious": 5},
               "persistence": {**TUNING["temperament"]["persistence"], "pressure_k": 0.3}}
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


def _sd(xs):
    xs = list(xs)
    return statistics.pstdev(xs) if len(xs) > 1 else 0.0


def _autocorr(xs, lag=1):
    xs = list(xs)
    if len(xs) <= lag + 1:
        return 0.0
    m = statistics.mean(xs)
    den = sum((x - m) ** 2 for x in xs)
    return sum((xs[i] - m) * (xs[i + lag] - m) for i in range(len(xs) - lag)) / den if den else 0.0


def simulate_t(pop: int, passes: int, seed: int, params: dict, traits: str = "on", trend: bool = True,
               window: str = "trait", legacy: bool = False, affinity: float = 0.0, pressure: float = 0.5,
               pay_rate: float = 0.35, temp: dict | None = None, p2_eats: bool = True,
               affinity_spread: float = 0.5) -> dict:
    """The town with temperament (see TEMPERAMENT above). `temp` overrides tuning's `temperament` block."""
    s = dict(BASE_S)
    s.update({k: v for k, v in params.items() if k != "arc_need_cost"})
    cost = params.get("arc_need_cost", BASE_COST)
    t = None if legacy else dict(temp or TEMP)
    if t and window == "global":
        mid = round((t["recent_window_min"] + t["recent_window_max"]) / 2)
        t = {**t, "recent_window_min": mid, "recent_window_max": mid}
    keep = (temp or TEMP)["recent_window_max"]
    rng = Random(seed)
    trng = Random(seed * 7919 + 13)  # the traits' own stream: the town's dice are the same on and off
    start = s["starting_provisions_per_capita"]
    tr = [temperament.draw_random(trng) if traits == "on" else dict(temperament.NEUTRAL) for _ in range(pop)]
    # every character also has a fixed net affinity, `affinity` plus a uniform draw in [0, affinity_spread]
    # from the same stream (after the traits, so the traits are the same whatever it is), because the
    # communality and pool-reliance terms are multiplied by it and would otherwise never act
    aff = [affinity + trng.uniform(0.0, affinity_spread) for _ in range(pop)]
    recent = [[] for _ in range(pop)]
    energy = [s["energy_cap"]] * pop
    personal = [start] * pop
    alive = list(range(pop))
    died_at = {}
    pool = start * pop
    ckpt = None
    turns = [0] * pop
    works_i = [0] * pop
    pct_sum = [0.0] * pop
    works = arcs = can = starved = 0
    floor = ceil = rate_pin = rate_n = info = 0
    cfloor = cceil = 0  # personal cushion term pinned at -1 / +1
    pcs, round_work, cur = [], [], [0, 0]
    round_pc = []
    for tpass in range(passes):
        if not alive:
            break
        i = rng.choice(alive)
        n = len(alive)
        per_capita = pool / n
        tr_ = 0.0 if ckpt is None else per_capita - ckpt
        if trend and not legacy:
            recent[i] = temperament.observe(recent[i], per_capita, personal[i], energy[i], keep)
        out = arc_odds(s, energy[i], aff[i], pressure, per_capita, tr_, personal[i],
                       traits=tr[i], recent=recent[i] if (trend and not legacy) else None, t=t, cost=cost)
        pct = out["pct"]
        turns[i] += 1
        pct_sum[i] += 100.0 - pct
        floor += out["pool_surplus"] <= -1.0
        ceil += out["pool_surplus"] >= 1.0
        info += -1.0 < out["pool_surplus"] < 1.0
        cfloor += out["personal_cushion"] <= -1.0
        cceil += out["personal_cushion"] >= 1.0
        if trend and not legacy and len(recent[i]) >= 2:
            rate_n += 1
            rate_pin += abs(out["trend"]) >= 1.0
        choice = "arc" if rng.random() < pct / 100.0 else "work"
        pool = economy_rules.upkeep(pool, n, s["upkeep_rate_per_capita"])
        ckpt = pool / n
        r = economy_rules.resolve_pass(energy[i], personal[i], pool, choice, s)
        energy[i], personal[i], pool = r["energy"], r["personal"], r["pool"]
        if choice == "work":
            works += 1
            works_i[i] += 1
            cur[0] += 1
        else:
            arcs += 1
            if personal[i] >= cost:
                can += 1
        cur[1] += 1
        if choice == "arc" and rng.random() < pay_rate and n > 1:
            j = rng.choice([k for k in alive if k != i])
            if p2_eats:  # the second participant of a pair scene eats (Part A)
                e = economy_rules.resolve_pass(energy[j], personal[j], pool, "eat", s)
                energy[j], personal[j], pool = e["energy"], e["personal"], e["pool"]
                if e["died"]:
                    alive.remove(j)
                    died_at[j] = tpass
                    starved += 1
            if personal[i] >= cost:
                od = economy_rules.payment_odds(personal[i], cost, 0.0, tr[i]["thrift"], PAY, s, t)
                if rng.random() < od["pct"] / 100.0 and j in alive:
                    personal[i] -= cost
                    personal[j] += cost
        if r["died"] and i in alive:
            alive.remove(i)
            died_at[i] = tpass
            starved += 1
        n = len(alive)
        pcs.append(pool / n if n else 0.0)
        if (tpass + 1) % pop == 0:
            round_pc.append(statistics.mean(pcs[-pop:]))
            round_work.append(cur[0] / cur[1] if cur[1] else 0.0)
            cur = [0, 0]
    plist = [personal[k] for k in alive]
    done = works + arcs
    total = max(1, passes)
    shares = [works_i[k] / turns[k] for k in range(pop) if turns[k] >= 8]
    odds = [pct_sum[k] / turns[k] / 100.0 for k in range(pop) if turns[k] >= 8]  # each character's mean chance of work: the share without the dice's noise
    surv = [(died_at.get(k, total) / total) for k in range(pop)]
    rp = round_pc[2:]
    rw = round_work[2:]
    w_mean = statistics.mean(rw) if rw else 0.0
    binom = (w_mean * (1 - w_mean) / pop) ** 0.5 if rw else 0.0
    return {
        "alive": len(alive) / pop, "pc_mean": statistics.mean(pcs) if pcs else 0.0, "pc_end": pool / len(alive) if alive else 0.0,
        "pers_mean": statistics.mean(plist) if plist else 0.0, "pers_med": statistics.median(plist) if plist else 0.0,
        "work": works / done if done else 0.0, "starved": starved, "can_pay": can / arcs if arcs else 0.0,
        "work_sd": _sd(shares), "odds_sd": _sd(odds), "surv_sd": _sd(surv),
        "osc": (_sd(rp) / statistics.mean(rp)) if rp and statistics.mean(rp) > 0 else 0.0,
        "ac1": _autocorr(rp, 1), "sync": (_sd(rw) / binom) if binom else 0.0,
        "pc_med": statistics.median(pcs) if pcs else 0.0, "info": info / max(1, done),
        "floor": floor / max(1, done), "ceil": ceil / max(1, done), "rate_pin": rate_pin / max(1, rate_n),
        "cfloor": cfloor / max(1, done), "cceil": cceil / max(1, done),
        "dead_frac": starved / pop, "extinct": float(not alive),
        "pc_series": rp,
        "chars": [(tr[k]["risk"], tr[k]["thrift"], float(k not in alive), turns[k]) for k in range(pop)],
    }


def average(runs: list) -> dict:
    keys = [k for k in runs[0] if k not in ("traj", "pc_series", "chars")]
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


def journey(connections: int, energy: float, personal: float, stop_pool: float, s: dict | None = None) -> dict:
    """A walk of `connections` connections, all arc passes: road (no pool), place (pool of `stop_pool`
    units, refilled for every stop: someone else's town), ending with the arrival pass at a place.
    Returns {"energy", "personal", "died_at": pass number or None, "passes"}."""
    s = s or BASE_S
    passes = 2 * connections
    for i in range(1, passes + 1):
        on_road = i % 2 == 1
        out = economy_rules.resolve_pass(energy, personal, 0 if on_road else stop_pool, "arc", s)
        energy, personal = out["energy"], out["personal"]
        if out["died"]:
            return {"energy": energy, "personal": personal, "died_at": i, "passes": passes}
    return {"energy": energy, "personal": personal, "died_at": None, "passes": passes}


def journeys(stop_pool: float) -> None:
    print(f"journeys: k connections = 2k arc passes (road, place, ...), roads without a pool, places with a pool of {stop_pool:g}")
    ks = [1, 2, 3, 4, 6]
    print(f"{'provisions':>10s} {'energy':>6s} | " + "  ".join(f"k={k:<2d}" for k in ks) + "   (energy on arrival, x = died on pass n)")
    for personal in (2, 0):
        for energy in (20, 12, 8, 5, 3):
            cells = []
            for k in ks:
                r = journey(k, energy, personal, stop_pool)
                cells.append(f"{r['energy']:>4g}" if r["died_at"] is None else f"x{r['died_at']:<3d}")
            print(f"{personal:>10d} {energy:>6d} | " + "  ".join(cells))
    for personal in (2, 0):
        need = {}
        for k in ks:
            need[k] = next((e for e in range(1, 21) if journey(k, e, personal, stop_pool)["died_at"] is None), None)
        print(f"lowest starting energy that arrives, {personal} provisions: " + ", ".join(f"k={k}: {v}" for k, v in need.items()))


# --------------------------------------------------------------------------------------------
# Generations
# --------------------------------------------------------------------------------------------

def gini(values: list) -> float:
    v = sorted(values)
    n, total = len(v), sum(v)
    if n == 0 or total <= 0:
        return 0.0
    return sum((2 * (i + 1) - n - 1) * x for i, x in enumerate(v)) / (n * total)


def top_share(values: list, frac: float = 0.1) -> float:
    v = sorted(values, reverse=True)
    total = sum(v)
    if not v or total <= 0:
        return 0.0
    k = max(1, round(frac * len(v)))
    return sum(v[:k]) / total


def simulate_generations(pop: int, gens: int, seed: int, params: dict, inheritance: bool = True,
                         reward: str = "on", tax: float = 0.0, birth_rate: float = 0.04, cap: float = 1.5,
                         affinity: float = 0.0, pressure: float = 0.5, pay_rate: float = 0.35,
                         traits: str | None = None, temp: dict | None = None, affinity_spread: float = 0.5) -> dict:
    """The generations model. `traits` None is the model as it was (no temperament: the pre-temperament
    roll, the cushion against the old threshold); "on"/"off" is the temperament model (T1 to T3 below):
    traits drawn for founders and inherited (mean of the parents plus noise) by children, the window of
    recent observations, the thrift-weighted payment odds, the second participant eating."""
    s = dict(BASE_S)
    s.update({k: v for k, v in params.items() if k != "arc_need_cost"})
    cost = params.get("arc_need_cost", BASE_COST)
    life_lo, life_hi = TUNING["lifespan_range"]["min"], TUNING["lifespan_range"]["max"]
    threshold = TUNING["arc_resolution_threshold"]
    child_cd, parent_cd = TUNING["child_cooldown_passes"], TUNING["parent_cooldown_passes"]
    rcfg = dict(TUNING["arc_completion_reward"])
    if reward == "uncapped":
        rcfg["max"] = 10 ** 9
    rng = Random(seed)
    trng = Random(seed * 7919 + 13)  # the traits' own stream
    tcfg = dict(temp or TEMP) if traits else None
    keep = (temp or TEMP)["recent_window_max"]
    start = s["starting_provisions_per_capita"]

    people = []

    def new_person(parents, weights, t, personal):
        tr_ = None
        if traits:
            if parents and traits == "on":
                tr_ = temperament.inherit(people[parents[0]]["tr"], people[parents[1]]["tr"], trng, tcfg["inherit_noise"])
            else:
                tr_ = temperament.draw_random(trng) if traits == "on" else dict(temperament.NEUTRAL)
        people.append({"id": len(people), "energy": s["energy_cap"], "personal": personal, "turns": 0, "span": rng.randint(life_lo, life_hi),
                       "parents": parents, "alive": True, "ready": t, "last_birth": -10 ** 9, "arc_turns": 0, "tally": 0, "w": weights,
                       "tr": tr_, "recent": [], "aff": affinity + trng.uniform(0.0, affinity_spread) if traits else affinity,
                       "gen": 1 + max((people[q].get("gen", 0) for q in parents), default=-1), "cause": None})
        return len(people) - 1

    for i in range(pop):
        new_person([], {i: 1.0}, 0, start)
    pool = start * pop
    ckpt = None
    t = 0
    total_passes = gens * int(round((life_lo + life_hi) / 2)) * pop
    marks = [round(total_passes * q / 4) for q in (1, 2, 3, 4)]
    snaps = []
    stats = {"completions": 0, "comp_turns": 0, "failed": 0, "born": 0, "starved": 0, "aged": 0, "to_children": 0.0, "to_pool": 0.0, "vanished": 0.0, "reward_paid": 0.0, "extinct": 0}

    def alive_ids():
        return [p["id"] for p in people if p["alive"]]

    def snapshot():
        live = [p for p in people if p["alive"]]
        vals = [p["personal"] for p in live]
        founders = {}
        for p in live:
            for f, w in p["w"].items():
                founders[f] = founders.get(f, 0.0) + w * p["personal"]
        tot = sum(vals)
        by_gen = {}
        for p in live:
            by_gen.setdefault(p["gen"], []).append(p["personal"])
        return {"alive": len(live), "gini": gini(vals), "top10": top_share(vals), "mean": statistics.mean(vals) if vals else 0.0,
                "max": max(vals) if vals else 0.0, "lineage_top": (max(founders.values()) / tot) if founders and tot > 0 else 0.0,
                "gen": max(p.get("gen", 0) for p in live) if live else 0,
                "by_gen": {g: {"n": len(v), "mean": statistics.mean(v), "max": max(v), "gini": gini(v)} for g, v in by_gen.items()}}

    def die(p, cause):
        p["alive"] = False
        p["cause"] = cause
        stats[cause] += 1
        amount = p["personal"]
        kids = [q for q in people if q["alive"] and p["id"] in q["parents"]]
        if inheritance and amount > 0:
            nonlocal pool
            to_pool, share = estate.split(amount, len(kids), tax)  # the real rule
            for q in kids:
                q["personal"] += share
            if kids:
                stats["to_children"] += share * len(kids)
            if to_pool:
                pool += to_pool
                stats["to_pool"] += to_pool
        else:
            stats["vanished"] += amount
        p["personal"] = 0

    for t in range(1, total_passes + 1):
        live = [p for p in people if p["alive"]]
        if not live:
            stats["extinct"] = 1
            break
        drawable = [p for p in live if p["ready"] <= t]
        if not drawable:
            continue
        p = rng.choice(drawable)
        n = len(live)
        per_capita = pool / n
        trend = 0.0 if ckpt is None else per_capita - ckpt
        if traits:
            p["recent"] = temperament.observe(p["recent"], per_capita, p["personal"], p["energy"], keep)
            pct = arc_odds(s, p["energy"], p["aff"], pressure, per_capita, trend, p["personal"], traits=p["tr"], recent=p["recent"], t=tcfg, cost=cost)["pct"]
        else:
            pct = arc_odds(s, p["energy"], affinity, pressure, per_capita, trend, p["personal"])["pct"]
        choice = "arc" if rng.random() < pct / 100.0 else "work"
        pool = economy_rules.upkeep(pool, n, s["upkeep_rate_per_capita"])
        ckpt = pool / n
        r = economy_rules.resolve_pass(p["energy"], p["personal"], pool, choice, s)
        p["energy"], p["personal"], pool = r["energy"], r["personal"], r["pool"]
        p["turns"] += 1
        p["arc_turns"] += 1
        reached = choice == "arc" and p["personal"] >= cost and rng.random() < pay_rate and n > 1
        paid = False
        if reached:
            other = rng.choice([q for q in live if q is not p])
            if traits:  # T3: the other participant eats; the payment goes through at the thrift-weighted odds
                e = economy_rules.resolve_pass(other["energy"], other["personal"], pool, "eat", s)
                other["energy"], other["personal"], pool = e["energy"], e["personal"], e["pool"]
                if e["died"] and other["alive"]:
                    die(other, "starved")
                od = economy_rules.payment_odds(p["personal"], cost, 0.0, p["tr"]["thrift"], PAY, s, tcfg)
                paid = rng.random() < od["pct"] / 100.0 and other["alive"]
            else:
                paid = True
            if paid:
                p["personal"] -= cost
                other["personal"] += cost
        if paid:
            weights = ARC_WEIGHTS["neutral"]
            outcome = rng.choices(["advance", "stall", "reverse"], weights=weights, k=1)[0]
            p["tally"] += {"advance": 1, "stall": 0, "reverse": -1}[outcome]
            if p["tally"] >= threshold:
                stats["completions"] += 1
                stats["comp_turns"] += p["arc_turns"]
                if reward != "off":
                    bonus = arc_completion.reward_for(p["arc_turns"], rcfg)
                    p["personal"] += bonus
                    stats["reward_paid"] += bonus
                p["arc_turns"], p["tally"] = 0, 0
            elif p["tally"] <= -threshold:
                stats["failed"] += 1
                p["arc_turns"], p["tally"] = 0, 0
        # births: a drawn adult off cooldown, with a random adult who is not their parent or child
        if (p["alive"] and p["turns"] >= child_cd and t - p["last_birth"] >= parent_cd and rng.random() < birth_rate
                and len([q for q in people if q["alive"]]) < cap * pop):
            mates = [q for q in live if q is not p and q["turns"] >= child_cd and q["alive"] and q["id"] not in p["parents"]
                     and p["id"] not in q["parents"] and t - q["last_birth"] >= parent_cd]
            if mates:
                m = rng.choice(mates)
                w = {}
                for src in (p, m):
                    for f, x in src["w"].items():
                        w[f] = w.get(f, 0.0) + x / 2
                cid = new_person([p["id"], m["id"]], w, t + child_cd, start)
                people[cid]["gen"] = 1 + max(p.get("gen", 0), m.get("gen", 0))
                p["last_birth"] = m["last_birth"] = t
                stats["born"] += 1
        if r["died"]:
            die(p, "starved")
        elif p["turns"] >= p["span"]:
            die(p, "aged")
        if t in marks:
            snaps.append(snapshot())
    final = snapshot() if not snaps or len(snaps) < 4 else snaps[-1]
    while len(snaps) < 4:
        snaps.append(final)
    done = stats["completions"]
    return {"final": snaps[-1], "snaps": snaps, "stats": stats, "turns_per_completion": (stats["comp_turns"] / done) if done else 0.0,
            "passes": t, "total_passes": total_passes,
            # (risk, thrift, generation, cause of death or None) of every person ever born: the death/trait correlations
            "people": [((p["tr"] or {}).get("risk", 0.0), (p["tr"] or {}).get("thrift", 0.0), p["gen"], p["cause"]) for p in people]}


def run_generations(a) -> None:
    pops = a.pop or [12]
    base = today()
    base.update({k: v[0] for k, v in parse_grid(a.set).items()})
    tax = a.tax if a.tax is not None else float((TUNING.get("estate") or {}).get("bequest_tax", 0.0))
    cases = [("old rule (estate vanishes, no reward)", False, "off", 0.0),
             ("inheritance only (no tax, no reward)", True, "off", 0.0),
             ("inheritance + reward, no tax", True, "on", 0.0),
             (f"inheritance + reward + tax {tax:g} (tuning.json)", True, "on", tax),
             (f"... tax {tax:g}, reward NO cap", True, "uncapped", tax)] if a.compare else [
             (f"inheritance {a.inheritance}, reward {a.reward}, tax {tax:g}", a.inheritance == "on", a.reward, tax)]
    if a.traits:
        return run_generations_traits(a, pops, base, tax)
    cfg = TUNING["arc_completion_reward"]
    print(f"generations: {a.gens} x ~45 own turns x N passes; birth-rate {a.birth_rate}, cap {a.cap} x N, pay-rate {a.pay_rate}, {a.seeds} seeds")
    print("economy: " + ", ".join(f"{k}={fmt(v)}" for k, v in base.items()))
    print(f"reward: base {cfg['base']}, per_turn {cfg['per_turn']}, min {cfg['min']}, max {cfg['max']}  (arc_need_cost {base['arc_need_cost']}, 3 paid advances to complete)")
    for n in pops:
        print(f"\nN = {n}")
        head = ["case", "alive", "gen", "born", "compl", "turns/c", "failed", "gini", "top10", "lineage", "mean", "max", "to_kids", "to_pool", "vanish", "reward"]
        rows = [head]
        for label, inh, rw, tx in cases:
            runs = [simulate_generations(n, a.gens, a.seed_base + sd, base, inheritance=inh, reward=rw, tax=tx, birth_rate=a.birth_rate, cap=a.cap,
                                         affinity=a.affinity, pressure=a.pressure, pay_rate=a.pay_rate) for sd in range(a.seeds)]
            m = lambda f: statistics.mean(f(r) for r in runs)
            rows.append([label, f"{m(lambda r: r['final']['alive']):.1f}", f"{m(lambda r: r['final']['gen']):.1f}", f"{m(lambda r: r['stats']['born']):.0f}", f"{m(lambda r: r['stats']['completions']):.1f}",
                         f"{m(lambda r: r['turns_per_completion']):.0f}", f"{m(lambda r: r['stats']['failed']):.1f}",
                         f"{m(lambda r: r['final']['gini']):.2f}", f"{m(lambda r: r['final']['top10']):.2f}", f"{m(lambda r: r['final']['lineage_top']):.2f}",
                         f"{m(lambda r: r['final']['mean']):.2f}", f"{m(lambda r: r['final']['max']):.1f}",
                         f"{m(lambda r: r['stats']['to_children']):.0f}", f"{m(lambda r: r['stats']['to_pool']):.0f}", f"{m(lambda r: r['stats']['vanished']):.0f}",
                         f"{m(lambda r: r['stats']['reward_paid']):.0f}"])
            if a.trace:
                rows.append(["  gini at 1/4, 2/4, 3/4, 4/4"] + [f"{statistics.mean(r['snaps'][q]['gini'] for r in runs):.2f}" for q in range(4)] + [""] * 11)
                rows.append(["  max wealth at 1/4 .. 4/4"] + [f"{statistics.mean(r['snaps'][q]['max'] for r in runs):.1f}" for q in range(4)] + [""] * 11)
        widths = [max(len(r[c]) for r in rows) for c in range(len(head))]
        for r in rows:
            print("  ".join(x.ljust(w) if i == 0 else x.rjust(w) for i, (x, w) in enumerate(zip(r, widths))))


def _corr(xs, ys):
    if len(xs) < 3:
        return 0.0
    mx, my = statistics.mean(xs), statistics.mean(ys)
    sx = sum((x - mx) ** 2 for x in xs) ** 0.5
    sy = sum((y - my) ** 2 for y in ys) ** 0.5
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sx * sy) if sx and sy else 0.0


def run_generations_traits(a, pops, base, tax) -> None:
    temp = BEFORE_TEMP if a.before else None
    if a.before:
        base = dict(base, **PROPOSAL)
    """--gens with --traits: the generations model WITH temperament (T1 to T3 apply, children inherit the traits),
    inheritance, tax and reward on (or as set by --inheritance/--reward/--tax). Prints, per N: survival
    (`extinct` share of runs, `starved` share of finished lifetimes, the correlation of starvation with risk
    and with thrift over everyone ever born who died or lived on), the wealth of the living at the end, and
    a by-generation table (mean, max personal provisions and Gini within each generation alive at the end)."""
    print(f"generations with temperament (traits {a.traits}): {a.gens} x ~45 own turns x N passes; birth-rate {a.birth_rate}, cap {a.cap} x N, pay-rate {a.pay_rate}, {a.seeds} seeds; "
          f"inheritance {a.inheritance}, reward {a.reward}, tax {tax:g}")
    print("economy: " + ", ".join(f"{k}={fmt(v)}" for k, v in base.items()))
    for n in pops:
        runs = [simulate_generations(n, a.gens, a.seed_base + sd, base, inheritance=a.inheritance == "on", reward=a.reward, tax=tax, birth_rate=a.birth_rate,
                                     cap=a.cap, affinity=a.affinity, pressure=a.pressure, pay_rate=a.pay_rate, traits=a.traits, temp=temp) for sd in range(a.seeds)]
        m = lambda f: statistics.mean(f(r) for r in runs)
        ended = lambda r: r["stats"]["starved"] + r["stats"]["aged"]
        fin = sum(ended(r) for r in runs)
        starved_share = sum(r["stats"]["starved"] for r in runs) / fin if fin else 0.0
        ppl = [x for r in runs for x in r["people"]]
        flag = [1.0 if x[3] == "starved" else 0.0 for x in ppl]
        print(f"\nN = {n}: extinct {m(lambda r: r['stats']['extinct']):.2f} of runs; alive at end {m(lambda r: r['final']['alive']):.1f}; born {m(lambda r: r['stats']['born']):.0f}; "
              f"completions {m(lambda r: r['stats']['completions']):.1f}; starved {starved_share * 100:.1f}% of finished lifetimes; "
              f"correlation of starving with risk {_corr([x[0] for x in ppl], flag):+.2f}, with thrift {_corr([x[1] for x in ppl], flag):+.2f}")
        print(f"  all living at the end: gini {m(lambda r: r['final']['gini']):.2f}, top10 {m(lambda r: r['final']['top10']):.2f}, mean {m(lambda r: r['final']['mean']):.2f}, max {m(lambda r: r['final']['max']):.1f}; "
              f"gini at 1/4..4/4: " + ", ".join(f"{statistics.mean(r['snaps'][q]['gini'] for r in runs):.2f}" for q in range(4)) +
              "; mean at 1/4..4/4: " + ", ".join(f"{statistics.mean(r['snaps'][q]['mean'] for r in runs):.2f}" for q in range(4)) +
              "; max at 1/4..4/4: " + ", ".join(f"{statistics.mean(r['snaps'][q]['max'] for r in runs):.1f}" for q in range(4)))
        gens = sorted({g for r in runs for g in r["final"]["by_gen"]})
        print("  by generation (living at the end; mean over the runs that have one): gen  runs  n/run  mean  max  gini  starved-of-lifetimes%")
        for g in gens:
            have = [r for r in runs if g in r["final"]["by_gen"]]
            mm = lambda k: statistics.mean(r["final"]["by_gen"][g][k] for r in have)
            born_g = [x for x in ppl if x[2] == g]
            done_g = [x for x in born_g if x[3]]
            sp = (sum(1 for x in done_g if x[3] == "starved") / len(done_g) * 100) if done_g else 0.0
            print(f"    {g:3d}  {len(have):4d}  {mm('n'):5.1f}  {mm('mean'):5.2f}  {mm('max'):5.1f}  {mm('gini'):4.2f}  {sp:5.1f}")


T_COLS = ["alive", "pc_mean", "pc_med", "can_pay", "work", "work_sd", "odds_sd", "surv_sd", "starved", "osc", "ac1", "sync", "info", "floor", "ceil", "cfloor", "cceil", "rate_pin", "dead_frac", "extinct", "r_risk", "r_thrift"]


def t_rows(label_kw: list, pops, seeds, seed_base, params, passes, kw) -> list:
    rows = []
    for n in pops:
        for label, extra in label_kw:
            runs = [simulate_t(n, passes or 40 * n, seed_base + sd, params, **{**kw, **extra}) for sd in range(seeds)]
            m = average(runs)
            ch = [c for r in runs for c in r["chars"]]  # (risk, thrift, died, turns) of every character in every run
            m["r_risk"] = _corr([c[0] for c in ch], [c[2] for c in ch])
            m["r_thrift"] = _corr([c[1] for c in ch], [c[2] for c in ch])
            m["extinct"] = statistics.mean(r["extinct"] for r in runs)
            rows.append((n, label, m))
    return rows


def print_t(rows) -> None:
    head = ["N", "case"] + T_COLS
    lines = [head] + [[str(n), label] + [f"{m[c]:.2f}" for c in T_COLS] for n, label, m in rows]
    widths = [max(len(r[c]) for r in lines) for c in range(len(head))]
    for r in lines:
        print("  ".join(x.ljust(w) if i == 1 else x.rjust(w) for i, (x, w) in enumerate(zip(r, widths))))


CASES = [
    ("legacy (no temperament)", dict(legacy=True, traits="off")),
    ("traits all 0 (mid-scale)", dict(traits="off")),
    ("traits on", dict(traits="on")),
    ("on, one global window", dict(traits="on", window="global")),
    ("on, trend off", dict(traits="on", trend=False)),
]


def traits_report(a) -> None:
    pops = a.pop or [6, 12, 25]
    kw = dict(affinity=a.affinity, pressure=a.pressure, pay_rate=a.pay_rate)
    for name, extra, temp in (("CURRENT tuning.json (the calibration for variation, 2026-10-17)", {}, None),
                              ("BEFORE the calibration: the first-adopted economy (work_pool 4, work_personal 3, upkeep 0.05) with the old temperament numbers (cushion over the 2-unit threshold, cautious margin 5 meals, persistence pressure 0.3)", PROPOSAL, BEFORE_TEMP),
                              ("TODAY'S OLD NUMBERS before any adoption (work_pool 1, work_personal 2, upkeep 0.15), current temperament", OLD, None)):
        params = dict(today(), **extra)
        t = temp or TEMP
        print(f"\n== {name}: " + ", ".join(f"{k}={fmt(v)}" for k, v in params.items()) + f" | {a.seeds} seeds, passes {a.passes or '40 x N'}; comfortable pool {t['pool_comfortable_meals']:g} meal(s)/head, window {t['recent_window_min']}..{t['recent_window_max']}, trend scale {t['trend_scale_meals']:g} meals, cautious margin {t['risk']['margin_meals_cautious']:g} meals, cushion scale {t.get('cushion_scale_meals') or 'the 2-unit threshold'}, persistence pressure {t['persistence']['pressure_k']:g}")
        print_t(t_rows(CASES, pops, a.seeds, a.seed_base, params, a.passes, dict(kw, temp=temp) if temp else kw))


def calibrate(a) -> None:
    pops = a.pop or [6, 12, 25]
    kw = dict(affinity=a.affinity, pressure=a.pressure, pay_rate=a.pay_rate)
    print("pool-term calibration: share of own turns with the pool term pinned at -1 (floor) / +1 (ceil), traits on")
    for name, extra in (("CURRENT", {}), ("PROPOSAL", PROPOSAL), ("RICH POOL (work_pool 6, upkeep 0.05, work_personal 3)", RICH)):
        params = dict(today(), **extra)
        print(f"\n{name}: " + ", ".join(f"{k}={fmt(v)}" for k, v in params.items()))
        pcs = [simulate_t(n, a.passes or 40 * n, a.seed_base + sd, params, **kw)["pc_mean"] for n in pops for sd in range(a.seeds)]
        print(f"  pool per head, mean over runs: {statistics.mean(pcs):.2f} units = {statistics.mean(pcs) / params['eat_amount']:.2f} meals")
        rows = []
        for c in (0.5, 1, 1.5, 2, 3, 4):
            for n in pops:
                runs = [simulate_t(n, a.passes or 40 * n, a.seed_base + sd, params, temp={**TEMP, "pool_comfortable_meals": c}, **kw) for sd in range(a.seeds)]
                rows.append((n, f"comfortable {c:g} meal(s)", average(runs)))
        print_t(rows)
    print("\ntrend scale (meals): share of turns with the pool rate pinned at +/-1, PROPOSAL economy")
    params = dict(today(), **PROPOSAL)
    rows = []
    for sc in (1, 2, 3, 4):
        for n in pops:
            runs = [simulate_t(n, a.passes or 40 * n, a.seed_base + sd, params, temp={**TEMP, "trend_scale_meals": sc}, **kw) for sd in range(a.seeds)]
            rows.append((n, f"trend scale {sc} meal(s)", average(runs)))
    print_t(rows)


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
    ap.add_argument("--gens", type=int, default=0, help="run the generations model for this many generations (see GENERATIONS above)")
    ap.add_argument("--compare", action="store_true", help="with --gens: the five cases (old rule, inheritance, + reward, + bequest tax, tax with no cap) side by side")
    ap.add_argument("--inheritance", choices=["on", "off"], default="on", help="with --gens (without --compare)")
    ap.add_argument("--reward", choices=["on", "off", "uncapped"], default="on", help="with --gens (without --compare)")
    ap.add_argument("--tax", type=float, default=None, help="with --gens: the bequest tax (default tuning's estate.bequest_tax); 0 = none")
    ap.add_argument("--birth-rate", type=float, default=0.04, help="with --gens: chance per drawn adult turn of a birth")
    ap.add_argument("--cap", type=float, default=1.5, help="with --gens: the town's size cap, as a multiple of the starting population")
    ap.add_argument("--scan", action="store_true", help="scan the grid for the stable region (default grid: see SCAN_GRID)")
    ap.add_argument("--alive-min", type=float, default=0.9)
    ap.add_argument("--pc-min", type=float, default=0.5, help="pool per capita below this = collapsed")
    ap.add_argument("--can-pay-min", type=float, default=0.0, help="optional extra bar for --scan: share of arc passes able to pay")
    ap.add_argument("--pc-max", type=float, default=8.0, help="pool per capita above this = runaway (4 x the start)")
    ap.add_argument("--traits", choices=["on", "off"], default=None, help="the town with temperament (see TEMPERAMENT above): traits drawn uniformly in [-1, 1] per character (on) or all neutral (off)")
    ap.add_argument("--trend", choices=["on", "off"], default="on", help="with --traits: the window of recent observations (off: the old checkpoint scarcity term)")
    ap.add_argument("--window", choices=["trait", "global"], default="trait", help="with --traits: window length by risk/thrift, or the neutral one for everybody")
    ap.add_argument("--legacy", action="store_true", help="with --traits: the roll as it was before temperament (baseline)")
    ap.add_argument("--traits-report", action="store_true", help="the full comparison (legacy / off / on / global window / trend off), current defaults and the proposal")
    ap.add_argument("--calibrate", action="store_true", help="the comfortable pool level and the trend scale: how often the terms sit at their limits")
    ap.add_argument("--before", action="store_true", help="with --traits or --gens: the numbers BEFORE the 2026-10-17 calibration for variation (the first-adopted economy and the old temperament numbers), for the before/after tables")
    ap.add_argument("--journey", action="store_true", help="roads as nodes: energy on arriving after k connections of arc passes")
    ap.add_argument("--stop-pool", type=float, default=4.0, help="--journey: units in the pool of every place stopped at")
    a = ap.parse_args()

    if a.journey:
        return journeys(a.stop_pool)
    if a.traits_report:
        return traits_report(a)
    if a.calibrate:
        return calibrate(a)
    if a.gens:
        return run_generations(a)
    if a.traits:
        pops = a.pop or [12]
        base = dict(today(), **{k: v[0] for k, v in parse_grid(a.set).items()})
        kw = dict(affinity=a.affinity, pressure=a.pressure, pay_rate=a.pay_rate)
        if a.before:
            base.update(PROPOSAL)
            kw["temp"] = BEFORE_TEMP
        case = [(f"traits {a.traits}, window {a.window}, trend {a.trend}" + (", legacy" if a.legacy else ""),
                 dict(traits=a.traits, trend=a.trend == "on", window=a.window, legacy=a.legacy))]
        print("params: " + ", ".join(f"{k}={fmt(v)}" for k, v in base.items()) + f" | {a.seeds} seeds, passes {a.passes or '40 x N'}")
        return print_t(t_rows(case, pops, a.seeds, a.seed_base, base, a.passes, kw))

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

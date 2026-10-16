"""
The economy's pure rules - eating, working, upkeep, one pass's net effect on one character and one
pool. No file I/O, no tuning load, no dice: every number comes in as an argument, so the real rule
can be called from apply_survival.py / apply_upkeep.py and, unchanged, from the balance simulation
(scripts/test/balance_economy.py). Never a copy of the rule; the one rule.

One substance at two scopes (TODO.md, "Economy rewrite"): a character's `provisions` and a
location's pool are the same food, held personally or in common.

  - Work pays the worker: `work_personal` to the character, `work_pool` to the location's pool.
  - Eating is universal, every pass, whatever was chosen. It needs `eat_amount` units, half from the
    character's own provisions and half from the pool; a shortfall on one side is filled from the
    other if it has any left; if both together can't cover it, it is a half meal: take what exists,
    energy rises by 1 per unit actually eaten.
  - Units are whole. A pool that sits at 0.45 after upkeep has no unit to give yet.
"""

from math import floor

import temperament


def eat(personal: float, pool: float, eat_amount: int) -> dict:
    """Take `eat_amount` units from the two sources. Returns what was taken from each, the units
    eaten, and `ate`: "full" (all of it), "half" (some of it) or "none".

    One rule: each side first gives up to half of the amount; whatever is still missing is taken
    from whichever side has some left. The four cases fall out of it: both stocked -> 1 + 1; no
    provisions -> 2 from the pool; empty pool -> 2 from provisions; both short -> whatever exists."""
    avail_p = max(0, floor(personal))
    avail_c = max(0, floor(pool))
    half = int(eat_amount) // 2  # whole units; an odd amount's last unit comes out of the shortfall step
    eat_amount = int(eat_amount)
    take_p = min(avail_p, half)
    take_c = min(avail_c, half)
    short = eat_amount - take_p - take_c
    if short > 0:
        extra_p = min(avail_p - take_p, short)
        take_p += extra_p
        short -= extra_p
    if short > 0:
        take_c += min(avail_c - take_c, short)
    units = take_p + take_c
    ate = "full" if units >= eat_amount else ("half" if units > 0 else "none")
    return {"from_personal": take_p, "from_pool": take_c, "units": units, "ate": ate}


def upkeep(pool: float, population: int, rate_per_capita: float) -> float:
    """The pool after this pass's flat per-capita drain, floored at 0."""
    return max(0.0, pool - population * rate_per_capita)


def resolve_pass(energy: float, personal: float, pool: float, choice: str, s: dict) -> dict:
    """One pass for one character: base cost, then eating, then the choice (work pays, arc costs
    extra energy), energy capped. `s` is tuning's `survival` block (or any dict with the same keys).
    `choice` is "work" or "arc" (the old "survive" is read as "work"), or "eat": the second
    participant of a pair scene (2026-10-17), who pays the base cost and eats but earns nothing and
    pays no arc cost. Personal provisions and the pool never come out negative. Reports `died`
    (energy 0 or below) and `ate`."""
    energy = energy - s["base_cost"]
    meal = eat(personal, pool, s["eat_amount"])
    personal = max(0, personal - meal["from_personal"])
    pool = max(0, pool - meal["from_pool"])
    energy += meal["units"]
    if choice in ("work", "survive"):
        personal += s["work_personal"]
        pool += s["work_pool"]
    elif choice == "arc":
        energy -= s["arc_extra_cost"]
    energy = min(energy, s["energy_cap"])
    return {"energy": energy, "personal": personal, "pool": pool, "ate": meal["ate"],
            "units": meal["units"], "died": energy <= 0}


def payment_odds(provisions: float, cost: float, ratio: float, thrift: float, pay: dict, s: dict,
                 t: dict | None = None) -> dict:
    """The payment gate's graded odds as a pure function (simulate_pass_lib.arc_payment_gate rolls
    them; the balance script calls this same one). `provisions` is the payer's own (the hard gate,
    provisions >= cost, is the caller's), `ratio` how near the arc is to resolving (0..1), `pay` is
    tuning's `arc_payment` block, `s` its `survival` block, `t` its `temperament` block (None: no
    thrift, today's odds exactly). Odds are `base + surplus_weight x surplus_norm x (1 - ratio)`, less a
    soft hesitation for thrift: `hesitation_per_meal` for each meal paying leaves the payer below their
    keep-level (temperament.hesitation), reported so the gate can show it. Returns the clamped
    percentage `pct` and the `hesitation` in points (positive took odds off, negative a spender's bonus)."""
    threshold = s["provides_provisions_threshold"]
    surplus = provisions - cost
    surplus_norm = min(1.0, surplus / threshold) if threshold else 0.0
    odds = pay["odds_percent"]
    pct = odds["base"] + pay["surplus_weight"] * surplus_norm * (1 - ratio)
    held = temperament.hesitation(thrift, surplus, s["eat_amount"], t["thrift"]) if t else 0.0
    pct -= held
    return {"pct": max(odds["min"], min(odds["max"], pct)), "hesitation": held}

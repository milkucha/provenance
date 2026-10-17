"""
Temperament: four continuous traits per character, each in [-1, 1], and the pure helpers
the work-or-pursue roll (roll_survival.arc_odds), the payment gate (economy_rules.payment_odds),
the destination draw (simulate_pass_lib), the birth draw (generate_offspring.py), the enacter's brief
(pass_prep.py) and the balance script all share. No file I/O, no tuning load, no dice of its own:
every number comes in as an argument, every random draw takes the caller's `Random` (seeded through
rng_context by the caller, so it lands in the draw audit). Design: TODO.md, "Temperament traits and
recent trends in the work roll"; every default is in `_lore/tuning.json` `temperament`.

The traits, on `character["temperament"]` = {risk, thrift, communality, persistence}. EVERY character gets
one (author's call 2026-10-17: no neutrals): a `/generate` cast is drawn, a child is its parents' mean plus
noise, `/character` authors or draws it. Only OLD data can lack the field, and then, so nothing crashes, a
missing field or a missing key reads 0.0 on that trait. There is no neutral CENTRE any more: 0 is an
ordinary value in the middle of a scale whose ends are defined directly (below), not "the old roll".

  risk         bold (+) / cautious (-). When I start: the reserve wanted before pursuing an arc, in
               meals of margin on top of the cost, from 0 (bold, +1) to 5 (cautious, -1), and how loudly
               the threat terms (low energy, a falling pool or purse) speak.
  thrift       thrifty (+) / free with money (-). What I keep when I pay: a soft hesitation in the
               payment odds for each meal that paying leaves them under their keep-level, from 0 meals
               (spender, -1) to 3 (saver, +1), and how much a falling purse worries me.
  communality  communal (+) / self-reliant (-). The weight of "us": scales the affinity OBLIGATION
               term only; leaning on the pool is not scaled (the free rider still takes the net).
  persistence  persistent (+) / restless (-). Adds to arc pressure, and after a failed pursuit
               retries the same destination (+) or redraws (-).

Recent trends: a character keeps `recent`, a short list (last `recent_window` entries) of what it saw
on its own turns, {"pc": pool per capita at its home place or None, "p": own provisions, "e": energy}.
The list is kept up to `recent_window_max` long; how much of it a character LOOKS at varies with who
they are (author's addition 2026-10-17): the pool-trend window follows risk (bold short, cautious long),
the own-provisions window follows thrift (spender short, saver long), each min(window, available).
`rates()` turns the windows into two normalized rates of change, latest against earliest, both in
[-1, 1]: the pool's per-capita level and the character's own provisions. All knobs are global (one
`temperament` block in tuning.json); there are no per-location or per-town overrides.
"""

TRAITS = ("risk", "thrift", "communality", "persistence")
NEUTRAL = {k: 0.0 for k in TRAITS}  # what old data without the field reads as; nothing new is made this way


def clamp(x: float, lo: float = -1.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def traits_of(source) -> dict:
    """The four traits as floats in [-1, 1]. `source` is a character dict (its `temperament` field is
    read), a temperament dict itself, or None; anything missing reads 0.0 (old data only: every character
    made since 2026-10-17 has all four)."""
    if not source:
        return dict(NEUTRAL)
    block = source.get("temperament", source) if isinstance(source, dict) else {}
    if not isinstance(block, dict):
        return dict(NEUTRAL)
    return {k: clamp(float(block.get(k, 0.0) or 0.0)) for k in TRAITS}


def lerp(trait: float, at_minus_one: float, at_plus_one: float) -> float:
    """Linear in the trait: `at_minus_one` at -1, `at_plus_one` at +1."""
    return at_minus_one + (at_plus_one - at_minus_one) * (clamp(trait) + 1.0) / 2.0


# --- the knobs turned into per-character numbers --------------------------------------------------

def margin_meals(risk: float, cfg: dict) -> float:
    """Meals of safety margin wanted before pursuing: cautious maximum at risk -1, bold minimum at +1."""
    return lerp(risk, cfg["margin_meals_cautious"], cfg["margin_meals_bold"])


def reserve_wanted(risk: float, cost: float, eat_amount: float, cfg: dict) -> float:
    """The reserve a character wants in hand before pursuing: arc_need_cost + margin_meals x eat_amount,
    margin from 0 meals (bold) to 5 (cautious). The personal-cushion term of the work-or-arc roll is
    computed against exactly this; nothing is centred on a neutral character."""
    return cost + margin_meals(risk, cfg) * eat_amount


def threat_factor(risk: float, cfg: dict) -> float:
    """Multiplier on the threat terms (negative contributions of energy and of a falling pool or purse):
    1 - k x risk, so bold shrugs them off and cautious feels them more. Never below 0."""
    return max(0.0, 1.0 - cfg["threat_k"] * risk)


def obligation_factor(communality: float, cfg: dict) -> float:
    """Multiplier on the affinity-obligation term: 1 + k x communality, never below 0 (the free rider
    feels no duty, never a negative one)."""
    return max(0.0, 1.0 + cfg["obligation_k"] * communality)


def personal_trend_factor(thrift: float, cfg: dict) -> float:
    """Multiplier on the decline of the character's own provisions: the thrifty worry more."""
    return max(0.0, 1.0 + cfg["trend_k"] * thrift)


def keep_meals(thrift: float, cfg: dict) -> float:
    """Meals a character wants left in hand after paying: saver at thrift +1, spender at -1."""
    return lerp(thrift, cfg["keep_meals_spender"], cfg["keep_meals_saver"])


def hesitation(thrift: float, left_after_paying: float, eat_amount: float, cfg: dict) -> float:
    """Percentage points taken off the payment odds: `hesitation_per_meal` for each meal that paying
    leaves the payer below their keep-level (keep_meals: 0 for a spender, 3 for a saver, linear between).
    Not relative to anyone: the middle of the scale (thrift 0, keep 1.5 meals) hesitates too when paying
    leaves them under it, and a spender, whose keep-level is 0, never does. `left_after_paying` is
    provisions minus cost, in units."""
    left_meals = left_after_paying / eat_amount if eat_amount else 0.0
    return cfg["hesitation_per_meal"] * max(0.0, keep_meals(thrift, cfg) - left_meals)


# --- recent trends ---------------------------------------------------------------------------------

def window_for(trait: float, cfg: dict, short_when_high: bool) -> int:
    """How many of its own last observations a character looks at, whole observations, linear across the
    trait from `recent_window_min` to `recent_window_max` (the middle of the scale is their midpoint, 5 by default).
    The pool window follows risk with `short_when_high` (bold looks at a short stretch, cautious a long
    one); the personal-provisions window follows thrift the other way (a spender short, a saver long)."""
    lo, hi = cfg["recent_window_min"], cfg["recent_window_max"]
    w = lerp(trait, hi, lo) if short_when_high else lerp(trait, lo, hi)
    return int(round(w))


def pool_window(risk: float, cfg: dict) -> int:
    return window_for(risk, cfg, short_when_high=True)


def personal_window(thrift: float, cfg: dict) -> int:
    return window_for(thrift, cfg, short_when_high=False)


def observe(recent, pool_per_capita, provisions: float, energy: float, keep: int) -> list:
    """The list with one more observation, trimmed to the last `keep` entries (the largest window any
    character can use, `recent_window_max`). Values rounded to two places to keep the stored list tiny."""
    entry = {
        "pc": None if pool_per_capita is None else round(float(pool_per_capita), 2),
        "p": round(float(provisions), 2), "e": round(float(energy), 2),
    }
    return (list(recent or []) + [entry])[-max(1, int(keep)):]


def rates(recent, scale: float, pool_win: int, personal_win: int) -> tuple:
    """(pool_rate, personal_rate): the change from the earliest to the latest observation inside each
    window, divided by `scale` (units) and clamped to [-1, 1]. A window is min(its length, observations
    available), so a character with few turns uses what it has; None when that is fewer than two entries
    or, for the pool, when either end has no pool figure (standing on a road)."""
    if not recent or not scale:
        return None, None

    def span(win):
        n = min(int(win), len(recent))
        return (recent[-n], recent[-1]) if n >= 2 else (None, None)

    pool = personal = None
    first, last = span(pool_win)
    if first and first.get("pc") is not None and last.get("pc") is not None:
        pool = clamp((last["pc"] - first["pc"]) / scale)
    first, last = span(personal_win)
    if first:
        personal = clamp((last.get("p", 0.0) - first.get("p", 0.0)) / scale)
    return pool, personal


# --- the destination draw --------------------------------------------------------------------------

def retry_adjust(options: list, retry, need: str, persistence: float, cfg: dict) -> list:
    """After a failed pursuit the previous destination (`retry` = {"need", "place"}) gets
    `retry_weight x persistence` added to its weight: a persistent character is pulled back to it, an
    impulsive one pushed off it (never below `retry_min_fraction` of its weight, so it stays possible).
    Returns new option dicts; the input is left alone. No retry for another need, or a place that is not
    an option, changes nothing."""
    if not retry or not persistence or retry.get("need") != need:
        return options
    out = []
    for o in options:
        if o["location"] == retry.get("place"):
            w = max(o["weight"] * cfg["retry_min_fraction"], o["weight"] + cfg["retry_weight"] * persistence)
            o = {**o, "weight": round(w, 4), "retry": True}
        out.append(o)
    return out


# --- words for the enacter -------------------------------------------------------------------------

_WORDS = {
    "risk": ("cautious", "bold"),
    "thrift": ("free with money", "thrifty"),
    "communality": ("self-reliant", "communal"),
    "persistence": ("restless", "persistent"),
}


def words(source, threshold: float) -> str:
    """A few words for the brief, in the order risk, thrift, communality, persistence; nothing for a
    trait within `threshold` of zero (so "" for a character whose traits all sit near the middle)."""
    tr = traits_of(source)
    out = []
    for k in TRAITS:
        if tr[k] > threshold:
            out.append(_WORDS[k][1])
        elif tr[k] < -threshold:
            out.append(_WORDS[k][0])
    return ", ".join(out)


# --- the draws (the caller supplies a seeded Random) -----------------------------------------------

def draw_random(rng) -> dict:
    """A generated character's traits: each uniform in [-1, 1], rounded to two places."""
    return {k: round(rng.uniform(-1.0, 1.0), 2) for k in TRAITS}


def inherit(parent_a, parent_b, rng, noise: float) -> dict:
    """A child's traits: the mean of the parents' (a parent from old data with no field counts as 0) plus gaussian noise with
    standard deviation `noise`, clamped to [-1, 1], rounded to two places. Habitus: it runs in a family,
    and it wanders."""
    a, b = traits_of(parent_a), traits_of(parent_b)
    return {k: round(clamp((a[k] + b[k]) / 2.0 + rng.gauss(0.0, noise)), 2) for k in TRAITS}


def fmt(traits: dict) -> str:
    """One line for a script's stdout (and so for the draw audit): risk=0.12,thrift=-0.3,..."""
    return ",".join(f"{k}={traits[k]:g}" for k in TRAITS)

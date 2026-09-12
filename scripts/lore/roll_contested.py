"""
Roll whether an already-motivated visit (check_needs_provides.py already matched) is ALSO
contested by someone else's prior claim - a rare, genuine dice roll, not a model deciding a
complication would be dramatically convenient right now.

This is deliberately the only thing that gets rolled here. It does NOT decide who wins a contested
claim - that reuses the inclined value check_arc_alignment.py already computes for the help/hinder
question (see .claude/skills/simulate/SKILL.md's orchestration section for the fixed lookup table:
help -> visitor's claim wins, hinder -> the prior claim holds, mixed/neutral -> split or deferred).
Keeping the resolution as a lookup over an already-computed value, instead of a second free
judgment call, means nothing about a contested outcome is invented in the moment.

No persistent stock/inventory is tracked anywhere - "contested" is a fresh narrative fact each time
this rolls true, never a number that depletes. Same principle as hearsay: never verified or
reconciled against a ledger, just generated and played.

Default odds come from _lore/tuning.json (odds_percent.contested) - override with --odds only for a
one-off test, not to retune the mechanism (change the JSON file for that).

**Relationship-aware as of 2026-08-28** (design debrief - "crucial," per the user's own framing):
`--strength`/`--quality` describe the peer's own established tie to the arc-primacy winner (their
`partners`/`partners_quality` entry for them - see simulate_pass_brief.py's own call site). Only an
ESTABLISHED relationship shifts the odds at all - strength has to already cross `partner_threshold`
(5, same bar every other "more than a passing acquaintance" check in this codebase uses; a stranger
or a passing acquaintance gets no skew either way, regardless of a single lucky/unlucky quality
value). Once established, quality's SIGN decides the direction: positive shifts the odds down by
`contested_relationship_shift` (10, `_lore/tuning.json`) - people who know each other well and get
along make a rival's claim less likely to matter; negative shifts them up by the same amount - a
history of friction makes one more likely; exactly 0 (established but neutral) shifts nothing.
Clamped to [2, 95] either way - never a sure thing, never impossible, same "skew, never decide"
philosophy as everywhere else this pattern is used (arc-outcome's own `--contested` flag included).
Omit both (or pass 0/0) for the old flat-odds behavior - a standalone test call, or a scene with no
established relationship between the two, doesn't need to know about either flag.

Usage:
    py scripts/lore/roll_contested.py [--odds 15]
    py scripts/lore/roll_contested.py --strength 7 --quality 4    # established, positive -> less likely
    py scripts/lore/roll_contested.py --strength 6 --quality -3   # established, negative -> more likely
"""

import argparse
import sys
from pathlib import Path
from random import Random

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tuning  # noqa: E402

_T = tuning.load()
_DEFAULT_ODDS = _T["odds_percent"]["contested"]
_PARTNER_THRESHOLD = _T["partner_threshold"]
_RELATIONSHIP_SHIFT = _T["contested_relationship_shift"]
_MIN_ODDS, _MAX_ODDS = 2, 95


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--odds", type=float, default=_DEFAULT_ODDS, help=f"Percent chance of a contest firing (default {_DEFAULT_ODDS}, from _lore/tuning.json)")
    parser.add_argument("--strength", type=int, default=0, help="Peer's partners[primacy_winner] count - 0 means no established relationship")
    parser.add_argument("--quality", type=int, default=0, help="Peer's partners_quality[primacy_winner] score - sign decides the skew direction")
    parser.add_argument("--seed", type=int, default=None, help="Optional seed, for a reproducible roll")
    args = parser.parse_args()

    odds = args.odds
    if args.strength >= _PARTNER_THRESHOLD:
        if args.quality > 0:
            odds -= _RELATIONSHIP_SHIFT
        elif args.quality < 0:
            odds += _RELATIONSHIP_SHIFT
    odds = max(_MIN_ODDS, min(_MAX_ODDS, odds))

    rng = Random(args.seed)
    contested = rng.random() < (odds / 100.0)
    print(f"contested: {'true' if contested else 'false'}")
    print(f"odds_used: {odds}")


if __name__ == "__main__":
    main()

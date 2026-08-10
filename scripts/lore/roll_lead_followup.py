"""
Decide whether an open lead (a named rival surfaced by a contested-friction scene, see
check_arc_alignment.py and roll_contested.py) gets followed up on this pass - design debrief
2026-08-10.

This only ever gets called when the character holding the lead has ALREADY been drawn by
pick_pair.py's normal uniform draw and landed specifically as participant_1 - that's what keeps
this rare in practice, not this roll alone. Reusing pick_pair.py's own participant_1/participant_2
assignment as the gate (instead of adding a third die to decide "who might be pursuing something")
means this needs no extra randomness of its own for that part - see .claude/skills/simulate/
SKILL.md's extended orchestration section for the full sequence this fits into.

If the character has more than one open lead, this also decides which one is even in play this
pass, uniformly - a character doesn't get to consciously prioritize between rivals, that's the
model's judgment sneaking back in through the side door.

Default odds come from _lore/tuning.json (odds_percent.lead_followup) - override with --odds only
for a one-off test, not to retune the mechanism (change the JSON file for that).

Usage:
    py scripts/lore/roll_lead_followup.py --leads bardaglis
    py scripts/lore/roll_lead_followup.py --leads bardaglis some_other_rival [--odds 30]
"""

import argparse
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tuning  # noqa: E402

_DEFAULT_ODDS = tuning.load()["odds_percent"]["lead_followup"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--leads", nargs="+", required=True, help="Open lead target key(s) on this character's file")
    parser.add_argument("--odds", type=float, default=_DEFAULT_ODDS, help=f"Percent chance the selected lead gets followed this pass (default {_DEFAULT_ODDS}, from _lore/tuning.json)")
    args = parser.parse_args()

    lead = random.choice(args.leads)
    followed = random.random() < (args.odds / 100.0)
    print(f"lead: {lead}")
    print(f"followed: {'true' if followed else 'false'}")


if __name__ == "__main__":
    main()

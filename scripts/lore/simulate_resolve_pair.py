"""
Resolve which participant a /simulate pass starts from - now just `p1` (design session 2026-09-13,
asymmetric per-pass rewrite; see TODO.md's "asymmetric per-pass rewrite" entry and CHRONICLE.md's
matching entry). Retired this file's old dual role (draw a PAIR, then check for a lead-override that
could reassign participant_2) - under the new model there is no participant_2 to pre-resolve at all;
whoever else ends up in the pass, if anyone, is discovered inside simulate_pass_brief.py itself (see
`simulate_pass_lib.run_pass_mechanics()`'s own docstring for the full chain).

**Known gap, flagged rather than silently papered over (see this rewrite's own report):** the old
lead-override mechanic (`leads`/roll_lead_followup.py/apply_contested_lead.py's "does p1 chase down a
named rival" half) has no natural home left in the new asymmetric algorithm, which the rewrite's own
spec never mentions integrating. This script now only draws `p1`; it does not touch `leads` at all
any more (neither expiring them nor rolling a follow-up), so a character's `leads` entries persist
indefinitely until some future wave decides how "follow a lead" fits the new model (a plausible third
tier alongside resolve_arc_target()'s known-supplier/general tiers, but that's new design, not
something to invent here). `.claude/skills/simulate/SKILL.md`'s own Step 3 still describes the old
draw-a-pair-plus-lead-override contract and needs a follow-up documentation pass to match.

Usage:
    py scripts/lore/simulate_resolve_pair.py --pool khaoe farlis nerkeli --pass-number 12
"""

import argparse
import json
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))
import simulate_pass_lib as lib  # noqa: E402


def resolve_pair(pool: list, pass_number: int) -> dict:
    p1 = lib.draw_participant(pool)
    return {"participant_1": p1, "notes": []}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--pool", nargs="+", required=True, help="Every slug still in the living pool")
    parser.add_argument("--pass-number", type=int, required=True)
    args = parser.parse_args()

    lib.rng_context.set_current_pass(args.pass_number)
    pool = [s.lower() for s in args.pool]
    result = resolve_pair(pool, args.pass_number)

    print(f"participant_1: {result['participant_1']}")
    for n in result["notes"]:
        print(f"  note: {n}")
    print(json.dumps(result))


if __name__ == "__main__":
    main()

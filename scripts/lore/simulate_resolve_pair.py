"""
Resolve which two participants a /simulate pass actually involves - draw + lead-override, in one
mechanical call - before /enact's own eligibility gate and mechanical block ever run against them
(.claude/skills/enact/SKILL.md's Step 2/4). Extracted 2026-08-27 when /simulate stopped calling
simulate_pass_brief.py with a whole pool: that script now only ever takes an already-fixed --pair,
so drawing the pair and resolving lead-override has to happen here instead, as its own one-call
mechanical step, same "don't hand-relay a mechanical fact across several calls" discipline as
everywhere else in this pack.

Draws uniformly from the living pool (pick_pair.py's own logic, reused via simulate_pass_lib.py),
then checks participant_1's file for an unexpired `leads` entry (younger than
lead_expiry_passes - 8, from _lore/tuning.json). Any expired leads found are dropped from the file
right here, whether or not one gets followed. If at least one is still fresh, rolls
roll_lead_followup.py's own logic against them; a `followed: true` result overrides participant_2 to
the lead's target (only if that target is actually in the pool and isn't participant_1) and consumes
that lead entry from participant_1's file - the one piece of file mutation this script does, since
nothing else in this pack exposes "remove one lead entry" as its own call.

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
    notes = []
    p1, p2 = lib.pick_pair(pool)
    p1_char = lib.load_char(p1)

    forced_visit = False
    leads = p1_char.get("leads", [])
    fresh_leads = [l for l in leads if pass_number - l["created_pass"] < lib.LEAD_EXPIRY_PASSES]
    if len(fresh_leads) != len(leads):
        p1_char["leads"] = fresh_leads
        lib.save_char(p1, p1_char)

    if fresh_leads:
        res = lib.roll_lead_followup([l["target"] for l in fresh_leads])
        if res["followed"] == "true":
            target = res["lead"]
            if target in pool and target != p1:
                p2 = target
                p1_char["leads"] = [l for l in fresh_leads if l["target"] != target]
                lib.save_char(p1, p1_char)
                forced_visit = True
                notes.append(f"{p1} followed a lead to {p2}")

    return {"participant_1": p1, "participant_2": p2, "forced_visit": forced_visit, "notes": notes}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--pool", nargs="+", required=True, help="Every slug still in the living pool")
    parser.add_argument("--pass-number", type=int, required=True)
    args = parser.parse_args()

    pool = [s.lower() for s in args.pool]
    result = resolve_pair(pool, args.pass_number)

    print(f"pair: {result['participant_1']} x {result['participant_2']}")
    print(f"forced_visit: {result['forced_visit']}")
    for n in result["notes"]:
        print(f"  note: {n}")
    print(json.dumps(result))


if __name__ == "__main__":
    main()

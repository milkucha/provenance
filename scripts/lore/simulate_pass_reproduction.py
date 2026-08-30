"""
Post-scene reproduction check - eligibility, then the roll itself - run AFTER the scene is written
instead of before it. Design debrief 2026-08-28: this used to run pre-scene inside
simulate_pass_brief.py, letting a birth get dramatized inside that same scene; moved here so it runs
once the scene - and this pass's partner-count bump, which simulate_pass_brief.py still does at the
very top of its own run - are both already on record. The cost is real: a birth this pass now gets a
short coda written after the scene instead of being woven into its dialogue.

Eligibility is plain arithmetic over already-known numbers, no roll needed for this part: partner
count >= partner_threshold (5, _lore/tuning.json), neither parent within parent_cooldown_passes (10)
of their last birth, and the pair not already related (parent/child/ancestor at any depth, or full/
half siblings - see simulate_pass_lib.already_related()'s own docstring for why cousins are still
allowed). Only when all three hold does roll_reproduction.py actually run - crossing the threshold
makes a birth POSSIBLE, this script decides whether it happens now.

On a true roll, prints a judgment slot: the caller composes the child's name (a blend leading from
name_lead's side - the one thing about a birth that can't be scripted, same as always) and calls
generate_offspring.py itself.

Usage:
    py scripts/lore/simulate_pass_reproduction.py --p1 khaoe --p2 farlis --pass-number 12
"""

import argparse
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))
import simulate_pass_lib as lib  # noqa: E402


def check_and_roll(p1: str, p2: str, pass_number: int, ancestor_cache: dict | None = None) -> dict:
    """`ancestor_cache`, if given, is passed straight through to lib.already_related() - lets a
    caller running many passes in one process (simulate_generate_population.py) memoize the
    ancestor walk across calls instead of re-walking/re-loading the same lineage from disk every
    time (see lib.ancestors_of()'s own docstring for why that matters at scale). A one-off CLI call
    has no such cache and doesn't need one."""
    p1_char, p2_char = lib.load_char(p1), lib.load_char(p2)
    count_ab = p1_char.get("partners", {}).get(p2, 0)
    count_ba = p2_char.get("partners", {}).get(p1, 0)
    threshold_met = max(count_ab, count_ba) >= lib.PARTNER_THRESHOLD
    cooldown_ok = all(
        c.get("last_reproduced_pass") is None
        or pass_number - c["last_reproduced_pass"] >= lib.PARENT_COOLDOWN_PASSES
        for c in (p1_char, p2_char)
    )
    already_related = lib.already_related(p1, p1_char, p2, p2_char, cache=ancestor_cache)

    result = {
        "eligible": threshold_met and cooldown_ok and not already_related,
        "reproduces": False, "name_lead": None, "other_parent": None,
    }
    if not result["eligible"]:
        return result

    repro = lib.roll_reproduction(p1, p2)
    if repro["reproduces"] == "true":
        name_lead = repro["name_lead"]
        result["reproduces"] = True
        result["name_lead"] = name_lead
        result["other_parent"] = p2 if name_lead == p1 else p1
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--p1", required=True)
    parser.add_argument("--p2", required=True)
    parser.add_argument("--pass-number", type=int, required=True)
    args = parser.parse_args()

    lib.rng_context.set_current_pass(args.pass_number)
    p1, p2 = args.p1.lower(), args.p2.lower()
    result = check_and_roll(p1, p2, args.pass_number)

    print(f"eligible: {'true' if result['eligible'] else 'false'}")
    print(f"reproduces: {'true' if result['reproduces'] else 'false'}")
    if result["reproduces"]:
        print(f"name_lead: {result['name_lead']}")
        print(f"other_parent: {result['other_parent']}")
        print(
            f"JUDGMENT NEEDED - child name: blend for {p1}+{p2}, leading from {result['name_lead']}'s "
            f"name, then run generate_offspring.py --parent-a {p1} --parent-b {p2} "
            f'--name "<composed name>" --pass-number {args.pass_number}'
        )


if __name__ == "__main__":
    main()

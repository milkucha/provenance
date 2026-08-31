"""
Driver script for /simulate's unattended batch mode - collapses every mechanical, pre-scene call a
pass needs into one: both participants' pre-scene horizon band (/enact Step 1's "Horizon" bullet)
plus the whole of simulate_pass_brief.py (/enact Step 4). Chains the real scripts via subprocess,
exactly like write_arc.py already chains to register_arc_concept.py - this never reimplements their
logic, it only collapses how many separate tool-call round-trips a subagent pays for reaching it.

Why this exists: a /simulate subagent dispatched fresh per pass shares no context or cache with any
other pass, so every separate Bash call re-pays that pass's entire growing context. See the repo's own
memory note "simulate-token-efficiency" (2026-08-10 pilot) - batching mechanical calls into driver
scripts cut tool calls per pass from ~15-20 to ~5.4 and kept a 115-pass run inside one usage window.
This script (plus pass_record.py and pass_apply.py) is that same pattern rebuilt for the current
mechanism, which has grown since (survival/energy, death-legacy, reproduction moved post-scene,
resonance/synthesis) - the 2026-08-10 versions never covered any of that.

Prints one combined JSON block (never write it to a file yourself - the model reads this call's own
stdout) with both participants' pre-scene band plus the full brief simulate_pass_brief.py already
wrote to .simulate_pass_brief.json. Nothing here makes a judgment call; everything decidable by a
script already was, by the scripts this only sequences.

Also includes a `characters` block (added 2026-08-29, round-3 debrief) - each participant's
criterion (standard/wasted_life/trusts/distrusts/anchor) and, if they have one, their arc's own
premise/about/needs. This was the one piece of the design principle "script everything that can be
scripted" this driver hadn't actually reached yet: the orchestrator was re-deriving this every pass
with an ad-hoc `py -c` one-liner and then hand-composing it into prose for the enacter dispatch -
both steps mechanical, neither one needing a judgment call, so both belong here instead. The enacter
should now receive this script's raw JSON output directly (plus the fixed instruction preamble and,
when a gate hit needs one, a short one-sentence director's note) - never a hand-paraphrased retelling
of it. See `.claude/PRINCIPLES.md`'s "script everything that can be scripted" principle.

Usage:
    py scripts/lore/pass_prep.py --p1 character_a --p2 character_c --pass-number 12 [--forced-visit]
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT = SCRIPTS_DIR.parent.parent
BRIEF_PATH = ROOT / ".simulate_pass_brief.json"
CHAR_DIR = ROOT / "_lore" / "characters"


def run(args: list) -> str:
    result = subprocess.run([sys.executable, *args], capture_output=True, text=True)
    if result.returncode != 0:
        raise SystemExit(f"{' '.join(args)} failed (exit {result.returncode}):\n{result.stderr}")
    return result.stdout


def parse_horizon(output: str) -> dict:
    fields = {}
    for line in output.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fields[k.strip()] = v.strip()
    return {"band": fields.get("band"), "lived": int(fields.get("lived", 0)), "ending": fields.get("ending") == "true"}


def load_character_brief(slug: str, context: str) -> dict:
    """Everything a scene needs about a character that isn't already in the mechanical brief: their
    criterion (the thing their whole standard is judged against), their routine for THIS pass's own
    `context` if one exists (added 2026-08-29, same debrief as the criterion/arc_premise fields below
    - a routine's own `routine_actions` text is exactly what grounds a character's ordinary behavior
    in a given setting, and picking the one matching the pass's context is itself mechanical, not a
    judgment call), and, if they have one, their arc's own premise text - never the character's full
    file, which is far more than an enacter needs and would just cost tokens re-sending it."""
    path = CHAR_DIR / f"{slug}.json"
    if not path.exists():
        return {}
    char = json.loads(path.read_text(encoding="utf-8"))
    criterion = char.get("criterion") or {}
    result = {
        "criterion": {
            "standard": criterion.get("standard"),
            "wasted_life": criterion.get("wasted_life"),
            "trusts": criterion.get("trusts"),
            "distrusts": criterion.get("distrusts"),
            "anchor": criterion.get("anchor"),
        }
    }
    routine = next((r for r in char.get("routines", []) if r.get("context") == context), None)
    if routine:
        result["routine"] = {"location": routine.get("location"), "routine_actions": routine.get("routine_actions")}
    arc = char.get("arc")
    if arc and arc.get("resolution") == "ongoing":
        result["arc_premise"] = {
            "about": arc.get("about"),
            "needs": arc.get("needs"),
            "premise": arc.get("premise"),
        }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--p1", required=True)
    parser.add_argument("--p2", required=True)
    parser.add_argument("--pass-number", type=int, required=True)
    parser.add_argument("--forced-visit", action="store_true")
    args = parser.parse_args()

    p1, p2 = args.p1.lower(), args.p2.lower()

    horizon_pre = {
        p1: parse_horizon(run([str(SCRIPTS_DIR / "horizon.py"), p1])),
        p2: parse_horizon(run([str(SCRIPTS_DIR / "horizon.py"), p2])),
    }

    brief_cmd = [str(SCRIPTS_DIR / "simulate_pass_brief.py"), "--pair", p1, p2, "--pass-number", str(args.pass_number)]
    if args.forced_visit:
        brief_cmd.append("--forced-visit")
    run(brief_cmd)

    brief = json.loads(BRIEF_PATH.read_text(encoding="utf-8"))

    context = brief.get("context")
    characters = {p1: load_character_brief(p1, context), p2: load_character_brief(p2, context)}

    combined = {"horizon_pre": horizon_pre, "brief": brief, "characters": characters}
    print(json.dumps(combined, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

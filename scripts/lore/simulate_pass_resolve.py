"""
Run the post-scene mechanics for one /simulate extended-mode pass - the old Step 3 points 15-16
(death check, death-legacy) - after the pass's subagent has finished writing the scene and running
/enact Steps 5/5b/6 underneath it. Reads participant_1/participant_2 straight back out of
.simulate_pass_brief.json (written by simulate_pass_brief.py earlier this same pass) rather than
having the caller retype slugs it already handed over once this pass.

Never touches life.lived - that increment happens inside /enact's own Step 5b work (via
update_character.py --lived-delta), same as always; horizon.py is only ever called here to read
what's already on record by the time this script runs, per horizon.py's own docstring ("ending" isn't
knowable until after that increment).

Usage:
    py "<worktree>/scripts/lore/simulate_pass_resolve.py"
    py "<worktree>/scripts/lore/simulate_pass_resolve.py" --brief "<worktree>/.simulate_pass_brief.json"
"""

import argparse
import json
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT = SCRIPTS_DIR.parent.parent
BRIEF_PATH = ROOT / ".simulate_pass_brief.json"

sys.path.insert(0, str(SCRIPTS_DIR))
import simulate_pass_lib as lib  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--brief", default=str(BRIEF_PATH), help="Path to this pass's brief, default: worktree root's .simulate_pass_brief.json")
    args = parser.parse_args()

    brief_path = Path(args.brief)
    if not brief_path.exists():
        raise SystemExit(f"No pass brief at {brief_path} - run simulate_pass_brief.py first.")
    brief = json.loads(brief_path.read_text(encoding="utf-8"))
    pass_number = brief["pass"]
    p1, p2 = brief["participant_1"], brief["participant_2"]

    died = []
    for participant in (p1, p2):
        h = lib.horizon(participant)
        if h["ending"] != "true":
            print(f"{participant}: band={h['band']}  lived={h['lived']}  ending=false")
            continue

        death = lib.record_death(participant)
        died.append(participant)
        sys.stdout.write(death["stdout"])

        if h["band"] == "established" and death["notified"]:
            legacy = lib.roll_death_legacy(death["notified"])
            if legacy["passes"] == "true":
                recipient = legacy["recipient"]
                deceased_char = lib.load_char(participant)
                deceased_arc = deceased_char.get("arc")
                if deceased_arc:
                    recipient_char = lib.load_char(recipient)
                    prev_arc = recipient_char.get("arc") or {}
                    archetype = prev_arc.get("archetype")
                    if not archetype:
                        routines = recipient_char.get("routines", [])
                        if routines:
                            archetype = max(routines, key=lambda r: r.get("weight", 0))["archetype"]
                    recipient_char["arc"] = {
                        "about": list(deceased_arc.get("about", [])),
                        "needs": list(deceased_arc.get("needs", [])),
                        "archetype": archetype or deceased_arc.get("archetype"),
                        "resolution": "ongoing",
                        "history": [],
                    }
                    lib.save_char(recipient, recipient_char)
                    print(f"death-legacy: {participant}'s arc passed to {recipient}")
            else:
                print(f"death-legacy: rolled false (candidates: {death['notified']})")
        elif h["band"] == "established":
            print("death-legacy: no notified circle to receive it")

    print()
    print(f"pass {pass_number} resolved.")
    print(f"died this pass: {died if died else '(none)'}")


if __name__ == "__main__":
    main()

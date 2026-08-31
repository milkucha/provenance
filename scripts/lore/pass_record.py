"""
Driver script for /simulate's unattended batch mode - the scene-just-written half. Collapses:
optional arc authoring (write_arc.py, /enact Step 5b's arc_authoring_needed slot), optional
contested-hinder note (apply_contested_lead.py, Step 5b's contested_hinder_slot), hearsay recording
(record_hearsay.py, Step 7), and both participants' anchor-reference (check_anchor_reference.py,
Step 8 point 1) and resonance (check_resonance.py, Step 9 point 1) checks - into one call. See
pass_prep.py's docstring for why this collapsing matters (one subagent per pass, no shared context or
cache across passes) and the "simulate-token-efficiency" memory this whole driver-script trio follows.

Every piece of *content* below (the hearsay claims, the arc's about/needs/premise, the contested
note's target) is still entirely the model's to compose - this script only owns sequencing the
mechanical calls once that content is decided and getting the two mechanical, script-only checks
(anchor reference, resonance) back to the model in one round-trip instead of four.

Input: --json-file pointing at the hearsay payload (exact shape record_hearsay.py itself documents -
this script hands it through unchanged). Optionally:
  --arc-authoring-json <path>  - {"character_slug": "...", "about": [...], "needs": [...],
                                   "context": "...", "premise": "..."}
  --contested-hinder-json <path> - {"traveler": "...", "rival": "...", "supplier": "...",
                                      "matched_provide": "..."}
Only pass these when simulate_pass_brief.py's own output flagged the matching slot AND the model
decided to fill it (arc authoring is not optional when flagged; contested-hinder is, per its own
"ambient is the default" rule - omit the flag entirely to leave it ambient).

Prints one combined JSON block: the hearsay entry id, then per participant the raw
check_anchor_reference.py / check_resonance.py stdout (still text, not reparsed - these already read
clearly and the model needs to make judgment calls from prose, not from a rigid schema this script
would have to reverse-engineer their own output to build).

Usage:
    py scripts/lore/pass_record.py --json-file hearsay.json --p1 character_a --p2 character_c --pass-number 12
    py scripts/lore/pass_record.py --json-file hearsay.json --p1 character_a --p2 character_c --pass-number 12 \\
        --arc-authoring-json arc.json --contested-hinder-json hinder.json
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent


def run(args: list) -> str:
    result = subprocess.run([sys.executable, *args], capture_output=True, text=True)
    if result.returncode != 0:
        raise SystemExit(f"{' '.join(args)} failed (exit {result.returncode}):\n{result.stderr}")
    return result.stdout


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--json-file", required=True, help="Hearsay payload, exact shape record_hearsay.py expects")
    parser.add_argument("--p1", required=True)
    parser.add_argument("--p2", required=True)
    parser.add_argument("--pass-number", type=int, required=True)
    parser.add_argument("--arc-authoring-json", default=None)
    parser.add_argument("--contested-hinder-json", default=None)
    args = parser.parse_args()

    p1, p2 = args.p1.lower(), args.p2.lower()
    report = {}

    if args.arc_authoring_json:
        a = json.loads(Path(args.arc_authoring_json).read_text(encoding="utf-8"))
        cmd = [str(SCRIPTS_DIR / "write_arc.py"), a["character_slug"]]
        for tag in a["about"]:
            cmd += ["--about", tag]
        for tag in a["needs"]:
            cmd += ["--needs", tag]
        cmd += ["--context", a["context"], "--premise", a["premise"]]
        report["arc_authoring"] = run(cmd)

    if args.contested_hinder_json:
        c = json.loads(Path(args.contested_hinder_json).read_text(encoding="utf-8"))
        cmd = [
            str(SCRIPTS_DIR / "apply_contested_lead.py"),
            "--traveler", c["traveler"], "--rival", c["rival"],
            "--supplier", c["supplier"], "--matched-provide", c["matched_provide"],
            "--pass-number", str(args.pass_number),
        ]
        report["contested_hinder"] = run(cmd)

    hearsay_out = run([str(SCRIPTS_DIR / "record_hearsay.py"), "--json-file", args.json_file])
    report["hearsay"] = hearsay_out
    entry_id = next(line.split(":", 1)[1].strip() for line in hearsay_out.splitlines() if line.startswith("id:"))
    report["hearsay_id"] = entry_id

    report["anchor_reference"] = {
        p1: run([str(SCRIPTS_DIR / "check_anchor_reference.py"), p1, "--hearsay-id", entry_id]),
        p2: run([str(SCRIPTS_DIR / "check_anchor_reference.py"), p2, "--hearsay-id", entry_id]),
    }
    report["resonance"] = {
        p1: run([str(SCRIPTS_DIR / "check_resonance.py"), p1, "--hearsay-id", entry_id]),
        p2: run([str(SCRIPTS_DIR / "check_resonance.py"), p2, "--hearsay-id", entry_id]),
    }

    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

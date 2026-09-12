"""
Records one immersion tasting - instrument (c) of the Provenance test suite (see TESTING_BRIEF.md,
vault-side `projects/provenance/`). Appends one rater's 0-10 scores (legibility, aliveness incl. felt
contingency, curiosity, specificity) plus free-text notes into the run manifest's `tastings: []`
array - append-only, so multiple raters accumulate rather than overwrite (TESTING_BRIEF.md §4.3/§6
acceptance criterion #5).

Never asks the questions itself - that's `.claude/skills/taste/SKILL.md`'s job, as plain
conversation (a 0-10 integer isn't a clean small discrete set for AskUserQuestion). This script only
owns the mechanical append, same "the model decides, the script records" split as `record_hearsay.py`.

Usage:
    py scripts/test/record_tasting.py --manifest <path> --rater milkucha \\
        --legibility 7 --aliveness 8 --curiosity 9 --specificity 6 \\
        --note "aliveness: the archive collapse felt like a real structural surprise"
"""

import argparse
import json
import time
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--manifest", type=Path, required=True, help="Path to the run's .simulate_run_manifest.json")
    parser.add_argument("--rater", required=True)
    parser.add_argument("--legibility", type=int, required=True, choices=range(0, 11), metavar="[0-10]")
    parser.add_argument("--aliveness", type=int, required=True, choices=range(0, 11), metavar="[0-10]")
    parser.add_argument("--curiosity", type=int, required=True, choices=range(0, 11), metavar="[0-10]")
    parser.add_argument("--specificity", type=int, required=True, choices=range(0, 11), metavar="[0-10]")
    parser.add_argument("--note", action="append", default=[], help="Free-text note, repeatable (one per dimension, or general)")
    args = parser.parse_args()

    if not args.manifest.exists():
        raise SystemExit(f"No run manifest at {args.manifest}.")
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    manifest.setdefault("tastings", [])

    tasting = {
        "rater": args.rater,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "legibility": args.legibility, "aliveness": args.aliveness,
        "curiosity": args.curiosity, "specificity": args.specificity,
        "notes": args.note,
    }
    manifest["tastings"].append(tasting)
    args.manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"recorded tasting from {args.rater} against {args.manifest}")
    print(f"  legibility={args.legibility} aliveness={args.aliveness} curiosity={args.curiosity} specificity={args.specificity}")
    print(f"  total tastings on this run: {len(manifest['tastings'])}")


if __name__ == "__main__":
    main()

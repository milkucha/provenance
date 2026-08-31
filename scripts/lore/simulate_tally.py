"""
Compute the closing tally .claude/skills/simulate/SKILL.md Step 4 needs for SIMULATION_LOG.md -
deaths, criterion moves (rejected/reinterpreted/broke), and final life.lived per participant -
straight from the character files, instead of the model hand-counting across up to 50 pass
summaries it only has as running-log text.

Two-phase, since a character's criterion.history and life.lived carry their whole history, not just
this run's: `snapshot` records where each participant stood right after Step 1's setup, before any
pass has run; `report` re-reads the same participants' current files and diffs against that snapshot
to isolate what changed *this run* only.

Usage:
    py scripts/lore/simulate_tally.py snapshot character_a character_b character_n_iii --out .simulate_snapshot.json
    py scripts/lore/simulate_tally.py report .simulate_snapshot.json
"""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
CHAR_DIR = ROOT / "_lore" / "characters"


def _load(key: str) -> dict:
    char_path = CHAR_DIR / f"{key}.json"
    if not char_path.exists():
        raise SystemExit(f"No character file for '{key}'.")
    with open(char_path, encoding="utf-8") as f:
        return json.load(f)


def cmd_snapshot(args: argparse.Namespace) -> None:
    snapshot = {}
    for key in args.pool:
        character = _load(key)
        life = character.get("life", {"lived": 0, "deceased": False})
        criterion = character.get("criterion", {})
        snapshot[key] = {
            "lived": life.get("lived", 0),
            "deceased": life.get("deceased", False),
            "history_len": len(criterion.get("history", [])),
        }
    out_path = Path(args.out)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"Snapshot written for {len(snapshot)} participant(s): {out_path}")


def cmd_report(args: argparse.Namespace) -> None:
    snap_path = Path(args.snapshot)
    if not snap_path.exists():
        raise SystemExit(f"No snapshot file at '{snap_path}' - run the 'snapshot' subcommand at the start of the run first.")
    with open(snap_path, encoding="utf-8") as f:
        before = json.load(f)

    deaths, moves, final_lived = [], [], []
    move_counts = {"rejected": 0, "reinterpreted": 0, "broke": 0}
    move_by_char = {"rejected": [], "reinterpreted": [], "broke": []}

    for key, was in before.items():
        character = _load(key)
        life = character.get("life", {"lived": 0, "deceased": False})
        criterion = character.get("criterion", {})
        lived_now = life.get("lived", 0)
        deceased_now = life.get("deceased", False)

        if deceased_now and not was["deceased"]:
            deaths.append(f"{key} (life.lived {was['lived']} -> {lived_now})")

        history = criterion.get("history", [])
        new_entries = history[was["history_len"]:]
        for entry in new_entries:
            move = entry.get("move")
            if move in move_counts:
                move_counts[move] += 1
                move_by_char[move].append(key)

        final_lived.append((key, lived_now, deceased_now))

    print(f"Participants: {', '.join(before.keys())}")
    print()
    print(f"Deaths this run: {', '.join(deaths) if deaths else 'none'}")
    print()
    print("Criterion moves this run:")
    for move, count in move_counts.items():
        who = f" ({', '.join(move_by_char[move])})" if move_by_char[move] else ""
        print(f"  {move}: {count}{who}")
    print()
    print("Final life.lived:")
    for key, lived_now, deceased_now in final_lived:
        tag = " (deceased)" if deceased_now else ""
        print(f"  {key}: {lived_now}{tag}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p_snap = sub.add_parser("snapshot", help="Record each participant's state before the run starts")
    p_snap.add_argument("pool", nargs="+", help="Every participant slug entering the run")
    p_snap.add_argument("--out", default=".simulate_snapshot.json", help="Where to write the snapshot")
    p_snap.set_defaults(func=cmd_snapshot)

    p_report = sub.add_parser("report", help="Diff current character files against a snapshot")
    p_report.add_argument("snapshot", help="Path to the snapshot file written by 'snapshot'")
    p_report.set_defaults(func=cmd_report)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

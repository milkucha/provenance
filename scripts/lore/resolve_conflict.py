"""
Surface one encodings.json conflicts-array entry for the user to resolve, or list all of them - the
mechanical half of /resolve (.claude/skills/resolve/SKILL.md). This script never decides a resolution
itself: it only shows the full picture (the conflict's own topic/detail, plus every other place in
encodings.json and _lore/unknowns.md that mentions this id) and, once the user has actually decided,
writes their exact words into `user_resolution` - the one field only the user may set, per every
skill's own append-only rule around this array (see .claude/PRINCIPLES.md).

Usage:
    py scripts/lore/resolve_conflict.py --list
    py scripts/lore/resolve_conflict.py CONFLICT-13
    py scripts/lore/resolve_conflict.py CONFLICT-13 --set-resolution "Aerorea is ..."
    py scripts/lore/resolve_conflict.py CONFLICT-13 --set-resolution "..." --force   # amend an existing resolution
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path

# This machine's Python defaults stdout to cp1252, which mangles the diacritics all over this
# pack's Spanish-language lore (Milkäan, Iläria, Aerórea...) once piped through a shell expecting
# UTF-8. Force it explicitly rather than let every caller rediscover this.
sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent.parent
ENCODINGS_PATH = ROOT / "_lore" / "encodings.json"
UNKNOWNS_PATH = ROOT / "_lore" / "unknowns.md"


def load_encodings() -> dict:
    with open(ENCODINGS_PATH, encoding="utf-8") as f:
        return json.load(f)


def walk_strings(node, path=""):
    """Yield (path, string_value) for every string anywhere in node, skipping the top-level
    'conflicts' array itself - the caller already has that entry directly, and every conflict's
    own 'id' field would otherwise trivially match itself."""
    if isinstance(node, dict):
        for k, v in node.items():
            if path == "" and k == "conflicts":
                continue
            yield from walk_strings(v, f"{path}.{k}" if path else k)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            label = v["id"] if isinstance(v, dict) and "id" in v else str(i)
            yield from walk_strings(v, f"{path}[{label}]")
    elif isinstance(node, str):
        yield path, node


def find_references(conflict_id: str, encodings: dict):
    hits = []
    for path, value in walk_strings(encodings):
        if conflict_id in value:
            snippet = value if len(value) <= 160 else value[:157] + "..."
            hits.append((path, snippet))
    return hits


def find_unknowns_mentions(conflict_id: str):
    hits = []
    heading = None
    for i, line in enumerate(UNKNOWNS_PATH.read_text(encoding="utf-8").splitlines(), start=1):
        if line.startswith("#"):
            heading = line.lstrip("#").strip()
        if conflict_id in line:
            hits.append((i, heading, line.strip()))
    return hits


def list_conflicts(encodings: dict) -> None:
    for c in encodings["conflicts"]:
        status = "RESOLVED" if c.get("user_resolution") else "OPEN"
        topic = c["topic"] if len(c["topic"]) <= 70 else c["topic"][:67] + "..."
        print(f"{c['id']:<14} {status:<9} {topic}")


def get_conflict(conflict_id: str, encodings: dict) -> dict:
    entry = next((c for c in encodings["conflicts"] if c["id"] == conflict_id), None)
    if entry is None:
        raise SystemExit(f"No conflict with id '{conflict_id}'. Run --list to see valid ids.")
    return entry


def show_conflict(conflict_id: str, encodings: dict) -> None:
    entry = get_conflict(conflict_id, encodings)

    print(f"id: {entry['id']}")
    print(f"topic: {entry['topic']}")
    print(f"detail: {entry['detail']}")
    print(f"user_resolution: {entry.get('user_resolution') or '(none - OPEN)'}")

    refs = find_references(conflict_id, encodings)
    print()
    print(f"Referenced elsewhere in encodings.json ({len(refs)}):")
    for path, snippet in refs:
        print(f"  {path}: {snippet}")

    mentions = find_unknowns_mentions(conflict_id)
    print()
    print(f"Referenced in _lore/unknowns.md ({len(mentions)}):")
    for line_no, heading, text in mentions:
        print(f"  line {line_no} (under '{heading}'): {text}")


def set_resolution(conflict_id: str, resolution: str, force: bool, encodings: dict) -> None:
    entry = get_conflict(conflict_id, encodings)
    if entry.get("user_resolution") and not force:
        raise SystemExit(
            f"'{conflict_id}' already has a user_resolution:\n  {entry['user_resolution']}\n"
            "Pass --force to overwrite it with a new decision."
        )

    text = resolution.strip()
    if "(per user" not in text.lower():
        text = f"{text.rstrip('.')} (per user, {date.today().isoformat()})."
    entry["user_resolution"] = text

    with open(ENCODINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(encodings, f, indent=2, ensure_ascii=False)
        f.write("\n")

    # Round-trip validate before declaring success, same discipline as record_hearsay.py.
    with open(ENCODINGS_PATH, encoding="utf-8") as f:
        json.load(f)

    print(f"{conflict_id} resolved:")
    print(f"  {text}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("conflict_id", nargs="?", default=None, help="e.g. CONFLICT-13")
    parser.add_argument("--list", action="store_true", help="List every conflict id, status, and topic.")
    parser.add_argument("--set-resolution", default=None, help="Write this text as user_resolution.")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing user_resolution.")
    args = parser.parse_args()

    encodings = load_encodings()

    if args.list:
        list_conflicts(encodings)
        return

    if not args.conflict_id:
        raise SystemExit("Pass a conflict id (e.g. CONFLICT-13) or --list.")

    if args.set_resolution:
        set_resolution(args.conflict_id, args.set_resolution, args.force, encodings)
    else:
        show_conflict(args.conflict_id, encodings)


if __name__ == "__main__":
    main()

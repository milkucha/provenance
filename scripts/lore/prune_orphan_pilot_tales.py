"""
One-off cleanup: removes encodings.json tales.entries whose `source_file` doesn't exist on disk -
dead data from an early reproduction pass (before /generate's current character-file-creation
behavior existed) that logged a birth/death tale-event without ever creating a real character file
for the child. Found 2026-08-31, in the original Luminacion test population, while fixing the
unrelated stale-tale-reference bug (fix_stale_tale_refs.py) - a genuinely different gap: those
children were never named because they were never created as characters at all, not because a later
rename pass missed them.

Also strips any `tale: <orphan_id>` string value found anywhere in a character file (recursive exact
match, same discipline as fix_stale_tale_refs.py) rather than leaving a dangling reference - since
there is nothing real left for it to point at, removal (not substitution) is correct here.

Usage:
    py scripts/lore/prune_orphan_pilot_tales.py            # apply
    py scripts/lore/prune_orphan_pilot_tales.py --dry-run  # report only, write nothing
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
CHARACTERS_DIR = ROOT / "_lore" / "characters"
ENCODINGS_PATH = ROOT / "_lore" / "encodings.json"


def remove_from_lists(obj, dead_refs, counter):
    """Recursively drop any string value exactly equal to 'tale: <dead_id>' from lists; for a bare
    dict field (e.g. criterion.anchor) holding such a string, clear it to ''."""
    if isinstance(obj, dict):
        for k, v in list(obj.items()):
            if isinstance(v, str) and v in dead_refs:
                obj[k] = ""
                counter[0] += 1
            else:
                remove_from_lists(v, dead_refs, counter)
    elif isinstance(obj, list):
        kept = []
        for v in obj:
            if isinstance(v, str) and v in dead_refs:
                counter[0] += 1
                continue
            if not isinstance(v, str):
                remove_from_lists(v, dead_refs, counter)
            kept.append(v)
        obj[:] = kept


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    encodings = json.loads(ENCODINGS_PATH.read_text(encoding="utf-8"))
    entries = encodings["tales"]["entries"]

    orphans = []
    other_missing = []
    kept_entries = []
    for e in entries:
        src = ROOT / e["source_file"]
        if not src.exists():
            if "placeholder" in e["id"]:
                orphans.append(e)
            else:
                # A real, named character's tale entry with no .md on disk - a different bug
                # (the file is simply missing), never pilot debris. Report only, never delete.
                other_missing.append(e)
                kept_entries.append(e)
        else:
            kept_entries.append(e)

    print(f"Found {len(orphans)} orphaned placeholder tale entr(ies) with no backing file (will remove):")
    for e in orphans:
        print(f"  {e['id']}  ({e['source_file']})")

    if other_missing:
        print(f"\nFound {len(other_missing)} entr(ies) for a REAL named tale with a missing .md file "
              f"(NOT touched - different bug, needs its own fix):")
        for e in other_missing:
            print(f"  {e['id']}  ({e['source_file']})")

    dead_refs = {f"tale: {e['id']}" for e in orphans}

    touched = []
    for p in CHARACTERS_DIR.glob("*.json"):
        if p.name in ("_template.json", "lifespans.json"):
            continue
        data = json.loads(p.read_text(encoding="utf-8"))
        counter = [0]
        remove_from_lists(data, dead_refs, counter)
        if counter[0]:
            touched.append((p, counter[0]))
            if not args.dry_run:
                with open(p, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                    f.write("\n")

    print(f"\nStripped {sum(n for _, n in touched)} stale reference(s) across {len(touched)} character file(s):")
    for p, n in touched:
        print(f"  {p.name}: {n}")

    if not args.dry_run:
        encodings["tales"]["entries"] = kept_entries
        with open(ENCODINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(encodings, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"\nRemoved {len(orphans)} orphaned entries from encodings.json (tales.entries: {len(entries)} -> {len(kept_entries)}).")
    else:
        print(f"\n[dry-run] Would remove {len(orphans)} orphaned entries from encodings.json.")


if __name__ == "__main__":
    main()

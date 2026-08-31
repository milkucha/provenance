"""
One-off retroactive cleanup for a population that already went through /generate's naming pass
before apply_language_layer.py's cross-reference walk covered `tale: <id>`-shaped references
(criterion.anchor, arc.about, knowledge.experience[].about, grounded_experience[].about, encodings.json
hearsay/conflicts/tales.touches - any exact `"tale: <old_id>"` string value anywhere under _lore/).

The gap: apply_language_layer.py renames a birth/death tale's own file, its encodings.json entry, and
does a literal NAME-string substitution in a fixed list of known fields - but never walked the tale's
own ID as it's referenced elsewhere via an `about`-tag-shaped string (`"tale: birth_of_placeholder_child_0004"`).
Once the tale itself is renamed (`birth_of_placeholder_child_0004` -> `birth_of_aurebako`), every other
character's criterion.anchor or arc.about that pointed at the OLD id via that tag form goes stale -
a dangling reference to a tale id that no longer exists in encodings.json. See
apply_language_layer.py's own docstring for the rename walk this gap sits next to, and the companion
fix landed there (2026-08-31) so this never happens again on a fresh /generate run - this script only
cleans up debt from before that fix existed.

Recovery trick: each renamed tale .md file's own header still carries a **stale** `Encodings id:` line
(a straight copy-paste artifact from the writer, never itself updated by the rename) - e.g.
`tales.entries[].id = "birth_of_placeholder_child_0008_2"` sitting inside `birth_of_aurebako.md`. That
line IS the old id, still on record, right next to the file it used to belong to. Cross-referencing it
against encodings.json's own entry for that same `source_file` (which IS correctly renamed) recovers
the full old_id -> new_id mapping with no guessing.

What this script does:
1. Build the old_id -> new_id mapping from every tale .md's stale header vs. its real encodings.json id.
2. Walk every _lore/characters/*.json and _lore/encodings.json, replacing any string value that is
   EXACTLY "tale: <old_id>" with "tale: <new_id>" (exact match only - never a substring/prose replace).
3. Fix each tale .md's own stale header line to show its real current id, so the audit trail stops
   lying about itself.
4. Report every file touched and how many references were fixed.

Usage:
    py scripts/lore/fix_stale_tale_refs.py            # apply
    py scripts/lore/fix_stale_tale_refs.py --dry-run  # report only, write nothing
"""
import argparse
import glob
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
TALES_DIR = ROOT / "_lore" / "tales"
CHARACTERS_DIR = ROOT / "_lore" / "characters"
ENCODINGS_PATH = ROOT / "_lore" / "encodings.json"

HEADER_RE = re.compile(r'(\*\*Encodings id:\*\*\s*`tales\.entries\[\]\.id\s*=\s*")([^"]+)("`)')


def build_mapping():
    encodings = json.loads(ENCODINGS_PATH.read_text(encoding="utf-8"))
    entries = encodings["tales"]["entries"]
    by_source = {e["source_file"].replace("\\", "/"): e["id"] for e in entries}

    mapping = {}
    stale_headers = []  # (md_path, old_id, new_id)
    for md_path in sorted(TALES_DIR.glob("*.md")):
        text = md_path.read_text(encoding="utf-8")
        m = HEADER_RE.search(text)
        if not m:
            continue
        header_id = m.group(2)
        rel = f"_lore/tales/{md_path.name}"
        real_id = by_source.get(rel)
        if real_id is None:
            continue
        if header_id != real_id:
            mapping[header_id] = real_id
            stale_headers.append((md_path, header_id, real_id))

    return mapping, stale_headers, encodings


def replace_in_place(obj, mapping, counter):
    """Recursively replace any string value exactly equal to 'tale: <old>' with 'tale: <new>'."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str):
                for old_id, new_id in mapping.items():
                    old_ref = f"tale: {old_id}"
                    if v == old_ref:
                        obj[k] = f"tale: {new_id}"
                        counter[0] += 1
                        break
            else:
                replace_in_place(v, mapping, counter)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            if isinstance(v, str):
                for old_id, new_id in mapping.items():
                    old_ref = f"tale: {old_id}"
                    if v == old_ref:
                        obj[i] = f"tale: {new_id}"
                        counter[0] += 1
                        break
            else:
                replace_in_place(v, mapping, counter)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true", help="Report what would change, write nothing.")
    args = parser.parse_args()

    mapping, stale_headers, encodings = build_mapping()
    if not mapping:
        print("No stale tale-id headers found - nothing to do.")
        return

    print(f"Recovered {len(mapping)} old-id -> new-id mapping(s):")
    for old_id, new_id in mapping.items():
        print(f"  {old_id}  ->  {new_id}")
    print()

    touched_files = []

    # 1. Character files
    char_paths = sorted(CHARACTERS_DIR.glob("*.json"))
    for p in char_paths:
        if p.name in ("_template.json", "lifespans.json"):
            continue
        data = json.loads(p.read_text(encoding="utf-8"))
        counter = [0]
        replace_in_place(data, mapping, counter)
        if counter[0]:
            touched_files.append((p, counter[0]))
            if not args.dry_run:
                with open(p, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                    f.write("\n")

    # 2. encodings.json itself (hearsay.about, conflicts, tales.touches, concepts.sources, etc.)
    counter = [0]
    replace_in_place(encodings, mapping, counter)
    if counter[0]:
        touched_files.append((ENCODINGS_PATH, counter[0]))
        if not args.dry_run:
            with open(ENCODINGS_PATH, "w", encoding="utf-8") as f:
                json.dump(encodings, f, indent=2, ensure_ascii=False)
                f.write("\n")

    total_refs = sum(n for _, n in touched_files)
    print(f"Fixed {total_refs} stale reference(s) across {len(touched_files)} file(s):")
    for p, n in touched_files:
        rel = os.path.relpath(p, ROOT)
        print(f"  {rel}: {n}")

    # 3. Fix each tale .md's own stale header line
    print()
    if not args.dry_run:
        for md_path, old_id, new_id in stale_headers:
            text = md_path.read_text(encoding="utf-8")
            fixed = HEADER_RE.sub(lambda m, nid=new_id: f'{m.group(1)}{nid}{m.group(3)}', text)
            md_path.write_text(fixed, encoding="utf-8")
        print(f"Corrected {len(stale_headers)} tale file header(s) to show their real current id.")
    else:
        print(f"[dry-run] Would correct {len(stale_headers)} tale file header(s).")

    if args.dry_run:
        print("\n[dry-run] No files were written.")


if __name__ == "__main__":
    main()

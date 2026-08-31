"""
Third retroactive cleanup pass: encodings.json's own `tales.entries[].summary` field duplicates the
same "<Name> was born, child of {a} and {b}." prose write_birth_tale() writes into the tale's own .md
file - a separate copy, never touched by fix_placeholder_backstory_text.py (which only patched
character.backstory and the tale .md body). Same Gap A bug, same fix: cross-reference the entry's own
child character's `parents` list to recover each parent's real current name and substitute any raw
placeholder_child_N token still sitting in the summary.

Usage:
    py scripts/lore/fix_encodings_summary_text.py            # apply
    py scripts/lore/fix_encodings_summary_text.py --dry-run  # report only, write nothing
"""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
CHARACTERS_DIR = ROOT / "_lore" / "characters"
ENCODINGS_PATH = ROOT / "_lore" / "encodings.json"

PLACEHOLDER_TOKEN_RE = re.compile(r"placeholder_child_\d+", re.IGNORECASE)


def load_all_characters():
    chars = {}
    for p in CHARACTERS_DIR.glob("*.json"):
        if p.name in ("_template.json", "lifespans.json"):
            continue
        chars[p.stem] = json.loads(p.read_text(encoding="utf-8"))
    return chars


def resolve_ab_placeholders(text, lead_in, parents, chars):
    idx = text.find(lead_in)
    if idx == -1 or len(parents) < 2:
        return text, False
    start = idx + len(lead_in)
    and_idx = text.find(" and ", start)
    if and_idx == -1:
        return text, False
    a_text = text[start:and_idx]

    changed = False
    new_text = text

    if PLACEHOLDER_TOKEN_RE.fullmatch(a_text.strip()):
        real_name = chars.get(parents[0], {}).get("name")
        if real_name:
            new_text = new_text[:start] + real_name + new_text[and_idx:]
            changed = True

    idx2 = new_text.find(lead_in)
    start2 = idx2 + len(lead_in)
    and_idx2 = new_text.find(" and ", start2)
    b_start2 = and_idx2 + len(" and ")
    m = PLACEHOLDER_TOKEN_RE.match(new_text[b_start2:])
    if m:
        real_name = chars.get(parents[1], {}).get("name")
        if real_name:
            new_text = new_text[:b_start2] + real_name + new_text[b_start2 + m.end():]
            changed = True

    return new_text, changed


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    chars = load_all_characters()
    encodings = json.loads(ENCODINGS_PATH.read_text(encoding="utf-8"))
    entries = encodings["tales"]["entries"]

    fixed = []
    for e in entries:
        eid = e["id"]
        summary = e.get("summary", "")

        if eid.startswith("birth_of_"):
            slug = eid[len("birth_of_"):]
            char = chars.get(slug)
            if not char:
                continue
            parents = char.get("parents") or []
            new_summary, changed = resolve_ab_placeholders(summary, "child of ", parents, chars)
            if changed:
                fixed.append((eid, summary, new_summary))
                e["summary"] = new_summary

        elif eid.startswith("death_of_"):
            # "{name} has died." - the subject's own name, stale the same way if it was still a raw
            # placeholder slug at death time and never revisited once the character was later renamed.
            slug = eid[len("death_of_"):]
            char = chars.get(slug)
            if not char:
                continue
            real_name = char.get("name")
            m = PLACEHOLDER_TOKEN_RE.match(summary)
            if m and real_name:
                new_summary = real_name + summary[m.end():]
                fixed.append((eid, summary, new_summary))
                e["summary"] = new_summary

    print(f"Fixed {len(fixed)} encodings.json tale summar(ies):")
    for eid, before, after in fixed:
        print(f"  {eid}")
        print(f"    before: {before}")
        print(f"    after:  {after}")

    if not args.dry_run and fixed:
        with open(ENCODINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(encodings, f, indent=2, ensure_ascii=False)
            f.write("\n")
    elif args.dry_run:
        print("\n[dry-run] No files were written.")


if __name__ == "__main__":
    main()

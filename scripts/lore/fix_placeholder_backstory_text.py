"""
Second retroactive cleanup pass, companion to fix_stale_tale_refs.py - closes two more leftover
placeholder-text gaps in `backstory`, the one field apply_language_layer.py's rename walk never
touches at all (its own docstring's substitution scope is: the child's own name, tale content/index/
encodings entries, and OTHER characters' knowledge.experience entries - never backstory).

**Run this BEFORE fix_stale_tale_refs.py**, not after - both derive their old_id -> new_id mapping
the same way (each renamed tale .md's own stale `Encodings id:` header line vs. its real current
encodings.json entry), and fix_stale_tale_refs.py corrects those header lines as its own last step,
which destroys the recovery signal this script also needs.

Gap A - raw parent slug baked into prose: generate_offspring.py's compose_backstory() and
write_birth_tale() both interpolate `parent.get("name", parent_key)` at birth time. If a parent was
itself still an unnamed placeholder child then (name == its own slug, e.g. "placeholder_child_0002"),
that raw slug got baked verbatim into "Child of {a} and {b}..." (character backstory) and
"{name} was born, child of {a} and {b}." (the birth tale's own body) and stays there forever, even
after the parent is later renamed - because both are free prose, never revisited by
apply_language_layer.py's substitution scope. Fix: the child's own `parents` list IS already
correctly renamed (apply_language_layer.py does walk that structural field) - cross-reference it to
recover each parent's real current name and substitute the raw slug token for it. Position in
`parents` matches position in the "... child of {a} and {b}" text, because generate_offspring.py
writes both from the same (a_key, b_key) pair in the same order (see its own `parents: [a_key, b_key]`
and the `compose_backstory`/`write_birth_tale` call sites). `resolve_ab_placeholders()` locates the a/b
slots by the " and " separator rather than assuming single-word tokens, since a real name can be
multi-word (e.g. "Prince Doran") - it only pattern-matches the placeholder shape itself
(placeholder_child_N), never assumes anything about the shape of a real name on either side.

Gap B - Title-Case tale-reference leftover: the same backstory templates also interpolate a random
knowledge item's humanized text (`{item}`), which for a still-placeholder-named birth/death tale
reads as e.g. "Birth Of Placeholder Child 0008 2" - the Title-Case display form of the OLD tale id.
Once that tale is renamed, this display form goes stale the same way raw tale-id references did, but
as a substring inside free prose rather than an exact-match tag value, so it needs its own substring
pass. The mapping is recovered dynamically (imported from fix_stale_tale_refs.py's own build_mapping())
rather than hardcoded, so this script stays reusable across any affected population instead of
carrying one specific population's id table.

Note: apply_language_layer.py itself was fixed 2026-08-31/2026-09-01 to close both gaps at the source
(walks backstory + every birth/death tale + exact tag references at rename time), so a fresh
population run through the current /generate never accumulates this debt in the first place. This
script - like fix_stale_tale_refs.py - is only for reconciling a population that already went through
the OLD, gapped version of that pipeline.

Usage:
    py scripts/lore/fix_placeholder_backstory_text.py            # apply
    py scripts/lore/fix_placeholder_backstory_text.py --dry-run  # report only, write nothing
"""
import argparse
import json
import re
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT = SCRIPTS_DIR.parent.parent
CHARACTERS_DIR = ROOT / "_lore" / "characters"
TALES_DIR = ROOT / "_lore" / "tales"

sys.path.insert(0, str(SCRIPTS_DIR))
import fix_stale_tale_refs  # noqa: E402

PLACEHOLDER_TOKEN_RE = re.compile(r"placeholder_child_\d+", re.IGNORECASE)


def load_all_characters():
    chars = {}
    for p in CHARACTERS_DIR.glob("*.json"):
        if p.name in ("_template.json", "lifespans.json"):
            continue
        chars[p.stem] = (p, json.loads(p.read_text(encoding="utf-8")))
    return chars


def resolve_ab_placeholders(text, lead_in, parents, chars):
    """Find `<lead_in>{a} and {b}` in text (a/b may be multi-word real names or a single-word
    placeholder_child_N token) and return (new_text, changed) with any placeholder token in the a/b
    slots replaced by parents[0]/parents[1]'s real current name. Robust to multi-word names (e.g.
    "Prince Doran") since it only pattern-matches the placeholder shape, never assumes single-word
    tokens on either side."""
    idx = text.find(lead_in)
    if idx == -1 or len(parents) < 2:
        return text, False
    start = idx + len(lead_in)
    and_idx = text.find(" and ", start)
    if and_idx == -1:
        return text, False
    a_text = text[start:and_idx]
    b_start = and_idx + len(" and ")

    changed = False
    new_text = text

    if PLACEHOLDER_TOKEN_RE.fullmatch(a_text.strip()):
        parent_entry = chars.get(parents[0])
        real_name = parent_entry[1].get("name") if parent_entry else None
        if real_name:
            new_text = new_text[:start] + real_name + new_text[and_idx:]
            changed = True

    # Re-locate b's start in case a's replacement shifted offsets.
    idx2 = new_text.find(lead_in)
    start2 = idx2 + len(lead_in)
    and_idx2 = new_text.find(" and ", start2)
    b_start2 = and_idx2 + len(" and ")
    m = PLACEHOLDER_TOKEN_RE.match(new_text[b_start2:])
    if m:
        parent_entry = chars.get(parents[1])
        real_name = parent_entry[1].get("name") if parent_entry else None
        if real_name:
            new_text = new_text[:b_start2] + real_name + new_text[b_start2 + m.end():]
            changed = True

    return new_text, changed


def fix_parent_slug_leftovers(chars, dry_run):
    fixed = []
    for slug, (path, data) in chars.items():
        backstory = data.get("backstory") or ""
        parents = data.get("parents") or []
        new_backstory, changed = resolve_ab_placeholders(backstory, "Child of ", parents, chars)
        if changed:
            fixed.append((path, backstory, new_backstory))
            if not dry_run:
                data["backstory"] = new_backstory
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                    f.write("\n")

        tale_path = TALES_DIR / f"birth_of_{slug}.md"
        if tale_path.exists():
            tale_text = tale_path.read_text(encoding="utf-8")
            new_tale_text, tale_changed = resolve_ab_placeholders(tale_text, "child of ", parents, chars)
            if tale_changed:
                fixed.append((tale_path, tale_text, new_tale_text))
                if not dry_run:
                    tale_path.write_text(new_tale_text, encoding="utf-8")
    return fixed


def fix_display_leftovers(chars, display_mapping, dry_run):
    fixed = []
    for slug, (path, data) in chars.items():
        raw = json.dumps(data, ensure_ascii=False)
        hit = any(old_disp in raw for old_disp in display_mapping)
        if not hit:
            continue

        def walk(obj):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if isinstance(v, str):
                        new_v = v
                        for old_disp, new_disp in display_mapping.items():
                            if old_disp in new_v:
                                new_v = new_v.replace(old_disp, new_disp)
                        if new_v != v:
                            obj[k] = new_v
                    else:
                        walk(v)
            elif isinstance(obj, list):
                for i, v in enumerate(obj):
                    if isinstance(v, str):
                        new_v = v
                        for old_disp, new_disp in display_mapping.items():
                            if old_disp in new_v:
                                new_v = new_v.replace(old_disp, new_disp)
                        if new_v != v:
                            obj[i] = new_v
                    else:
                        walk(v)

        walk(data)
        fixed.append(path)
        if not dry_run:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.write("\n")
    return fixed


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    mapping, _stale_headers, _encodings = fix_stale_tale_refs.build_mapping()
    if not mapping:
        print("No stale tale-id headers found (fix_stale_tale_refs.py may have already run and "
              "corrected them) - nothing to do for Gap B. Gap A below is independent of this and "
              "still runs.")
    display_mapping = {old.replace("_", " ").title(): new.replace("_", " ").title() for old, new in mapping.items()}

    chars = load_all_characters()

    parent_fixes = fix_parent_slug_leftovers(chars, args.dry_run)
    print(f"Gap A (raw parent slug in backstory): {len(parent_fixes)} file(s)")
    for path, before, after in parent_fixes:
        print(f"  {path.name}")
        print(f"    before: {before}")
        print(f"    after:  {after}")

    # reload chars fresh in case gap A already rewrote some files, to keep gap B scan accurate
    chars = load_all_characters()
    display_fixes = fix_display_leftovers(chars, display_mapping, args.dry_run)
    print(f"\nGap B (stale Title-Case tale display text): {len(display_fixes)} file(s)")
    for path in display_fixes:
        print(f"  {path.name}")

    if args.dry_run:
        print("\n[dry-run] No files were written.")


if __name__ == "__main__":
    main()

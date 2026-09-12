"""
Run the full mechanical death procedure for a character whose horizon.py just came back
`ending: true` after Step 8's life.lived increment - see .claude/skills/enact/SKILL.md Step 8
point 6. This is everything in that point EXCEPT the one genuine judgement call it contains
(whether a notified circle member's shock resolves as reject/reinterpret/break, per
.claude/skills/character/SKILL.md Step 6) - that stays with whoever is running /enact, same as any
other shock resolution. Everything else here is bookkeeping:

    - sets life.deceased: true on the character's own file
    - writes _lore/tales/<slug>.md recording the death as an objective fact of the world
    - adds the matching row to encodings.json's tales.entries, _lore/tales/_authors.md, and
      _lore/tales/_index.md
    - computes the character's circle and samples 30% of it to notify immediately (reuses
      notify_death.py's own logic, so the two never drift apart)
    - appends a plain "learned of the death" knowledge.experience line to every notified character
    - flags which notified characters are shock candidates (their criterion.anchor references the
      deceased) so the caller knows exactly who still needs a Step 6 judgement call afterward

Usage:
    py scripts/lore/record_death.py <npc_key>
    py scripts/lore/record_death.py <npc_key> --cause "collapsed on the M7 corridor, mid-flight"
    py scripts/lore/record_death.py <npc_key> --seed 42   # reproducible notified-circle sample
"""

import argparse
import json
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import notify_death  # noqa: E402  (sibling module, sys.path adjusted above)

ROOT = Path(__file__).resolve().parent.parent.parent
CHAR_DIR = ROOT / "_lore" / "characters"
ENCODINGS_PATH = ROOT / "_lore" / "encodings.json"
TALES_DIR = ROOT / "_lore" / "tales"
AUTHORS_PATH = TALES_DIR / "_authors.md"
INDEX_PATH = TALES_DIR / "_index.md"


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return "_".join(words)


def git_user_name() -> str:
    import subprocess
    try:
        return subprocess.check_output(["git", "config", "user.name"], cwd=ROOT, text=True).strip() or "unknown"
    except Exception:
        return "unknown"


def write_tale_file(slug: str, name: str, cause: str, told_date: str, responsible: str) -> Path:
    telling = f"{name} has died." if not cause else f"{name} has died - {cause}."
    content = f"""# The Death of {name}

**Responsible:** {responsible} - real-world provenance only, never an in-fiction detail (also recorded in `_lore/tales/_authors.md`)
**Told by:** no one; simply now known
**Told on:** {told_date}
**Encodings id:** `tales.entries[].id = "{slug}"`

## The tale

{telling}

## Where this lands in the record

- Touches: none
- Conflicts raised: none
- Open questions logged: none
"""
    path = TALES_DIR / f"{slug}.md"
    path.write_text(content, encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("npc_key", help="Character key of the character who died")
    parser.add_argument("--cause", default=None, help="Only if the scene actually established one; omit for the ordinary unexplained case")
    parser.add_argument("--seed", type=int, default=None, help="Optional seed, for a reproducible notified-circle sample")
    parser.add_argument("--date", dest="told_date", default=None, help="Defaults to today")
    parser.add_argument("--pass-number", type=int, default=None, help="Provenance (optional, test-suite): the /simulate pass this death was recorded in. Omit for today's exact unchanged output.")
    args = parser.parse_args()

    key = args.npc_key.lower()
    char_path = CHAR_DIR / f"{key}.json"
    if not char_path.exists():
        raise SystemExit(f"No character file for '{key}'.")
    with open(char_path, encoding="utf-8") as f:
        character = json.load(f)
    if character.get("life", {}).get("deceased"):
        raise SystemExit(f"'{key}' is already marked deceased - refusing to run the death procedure twice.")

    name = character["name"]
    told_date = args.told_date or date.today().isoformat()
    responsible = git_user_name()

    # 1. life.deceased
    character.setdefault("life", {})["deceased"] = True
    with open(char_path, "w", encoding="utf-8") as f:
        json.dump(character, f, indent=2, ensure_ascii=False)
        f.write("\n")

    # 2. tale file
    slug = f"death_of_{slugify(name)}"
    base_slug, n = slug, 2
    while (TALES_DIR / f"{slug}.md").exists():
        slug = f"{base_slug}_{n}"
        n += 1
    write_tale_file(slug, name, args.cause, told_date, responsible)

    # 3. encodings.json tales.entries
    with open(ENCODINGS_PATH, encoding="utf-8") as f:
        encodings = json.load(f)
    summary = f"{name} has died." if not args.cause else f"{name} has died - {args.cause}."
    encodings["tales"]["entries"].append({
        "id": slug,
        "source_file": f"_lore/tales/{slug}.md",
        "told_date": told_date,
        "told_by": None,
        "summary": summary,
        "touches": [],
    })
    with open(ENCODINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(encodings, f, indent=2, ensure_ascii=False)
        f.write("\n")
    with open(ENCODINGS_PATH, encoding="utf-8") as f:
        json.load(f)  # round-trip validate

    # 4. _authors.md
    with open(AUTHORS_PATH, "a", encoding="utf-8") as f:
        f.write(f"| `{slug}` | {responsible} | {told_date} |\n")

    # 5. _index.md
    with open(INDEX_PATH, "a", encoding="utf-8") as f:
        f.write(f"| {told_date} | The Death of {name} | no one; simply now known | {responsible} | `{slug}.md` | none |\n")

    # 6-7. circle, notify, boilerplate experience
    characters, enc = notify_death.load()
    entries = enc["hearsay"]["entries"]
    entries_by_id = {e["id"]: e for e in entries}
    name_to_key = notify_death.name_to_key_map(characters)

    relations = notify_death.compute_relations([key], characters)

    extended_keys = set()
    for _scene_id, others in notify_death.scene_participants_of(name, entries):
        for other_name in others:
            k = name_to_key.get(notify_death.normalize(other_name))
            if k and k != key:
                extended_keys.add(k)
    backstory_all = character.get("backstory") or ""
    for other_key, other_char in characters.items():
        if other_key == key:
            continue
        if notify_death.normalize(other_char.get("name", "")) in notify_death.normalize(backstory_all):
            extended_keys.add(other_key)
    extended_keys = notify_death.living_only(extended_keys, characters) - relations

    extended = sorted(extended_keys)
    n_notify = 0 if not extended else max(1, round(0.30 * len(extended)))
    from random import Random
    rng = Random(args.seed)
    sampled = sorted(rng.sample(extended, n_notify)) if n_notify else []
    notified = sorted(relations) + sampled
    circle = sorted(relations | extended_keys)

    shock_candidates = []
    for k in notified:
        notified_char_path = CHAR_DIR / f"{k}.json"
        with open(notified_char_path, encoding="utf-8") as f:
            notified_char = json.load(f)
        notified_char.setdefault("knowledge", {}).setdefault("experience", [])
        entry = f"Learned that {name} has died."
        if args.pass_number is not None:
            entry = {"text": entry, "produced_by": {"scene_id": None, "pass_number": args.pass_number}}
        notified_char["knowledge"]["experience"].append(entry)
        with open(notified_char_path, "w", encoding="utf-8") as f:
            json.dump(notified_char, f, indent=2, ensure_ascii=False)
            f.write("\n")

        anchor = notified_char.get("criterion", {}).get("anchor", "") or ""
        if anchor and notify_death.anchor_references(anchor, name, entries_by_id):
            shock_candidates.append(k)

    print(f"deceased: {key} ({name})")
    print(f"tale written: _lore/tales/{slug}.md  (id: {slug})")
    print(f"relations (guaranteed): {len(relations)}  |  extended circle: {len(extended)} -> sampled {len(sampled)} (30%)  |  total notified: {len(notified)}")
    for k in notified:
        tag = "  [relation]" if k in relations else ""
        flag = "  <-- SHOCK CANDIDATE: resolve per /character Step 6" if k in shock_candidates else ""
        print(f"  notified: {k}{tag}{flag}")
    if not notified:
        print("  (no one notified - empty circle)")
    print()
    print(f"{len(shock_candidates)} notified character(s) still need a Step 6 judgement call:", ", ".join(shock_candidates) or "(none)")


if __name__ == "__main__":
    main()

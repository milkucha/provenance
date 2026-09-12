"""
Record one hearsay entry into both _lore/characters/hearsay.md and _lore/encodings.json's
hearsay.entries array, from structured input - the mechanical half of /enact Step 5.

This script never decides what a claim says or how a character mutated it - that content is
entirely the caller's (the model's) to author, exactly as free-form as it always was. What this
script owns is pure bookkeeping that was previously hand-edited JSON: generating a consistent id,
keeping the two files' shape in sync, and not leaving either one malformed. See
.claude/skills/enact/SKILL.md Step 5 for the full recording rules this mechanizes.

Input is one JSON object, via --json-file or stdin:

    {
      "id": "<optional explicit id - auto-generated from participants+location if omitted>",
      "participants": ["Name1", "Name2"],
      "location": "free text" | {"id": null, "as_named_in_dialog": "free text"},
      "summary": "...",
      "source_file": "<optional; defaults to null - use this for a scene that has no Blabber
                       dialog yet, e.g. an /enact-only or /simulate scene that was never /embody'd>",
      "claims": [
        {
          "text": "...",                        (required)
          "about": "<ref, or null>",             (required key, value may be null)
          "note": "...",                         (optional)
          "inconsistent_with_record": [...],     (optional)
          "inconsistent_with_facts": "...",      (optional)
          "derived_from": "<claim id>",          (optional - only on a traceable lineage_coin roll)
          "oral_lore": true                      (optional - only on an untraceable roll, or growth)
        }
      ]
    }

Usage:
    py scripts/lore/record_hearsay.py --json-file scene.json
    py scripts/lore/record_hearsay.py < scene.json
"""

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
CHAR_DIR = ROOT / "_lore" / "characters"
ENCODINGS_PATH = ROOT / "_lore" / "encodings.json"
HEARSAY_MD_PATH = CHAR_DIR / "hearsay.md"

_SKIP = {"_template", "lifespans"}


def slugify(text: str, max_words: int = 4) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return "_".join(words[:max_words]) if words else "unknown"


def name_to_key_map() -> dict:
    mapping = {}
    for path in CHAR_DIR.glob("*.json"):
        if path.stem in _SKIP:
            continue
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if data.get("name"):
            mapping[data["name"].lower()] = path.stem
    return mapping


def build_id(participants: list, location, existing_ids: set) -> str:
    name_to_key = name_to_key_map()
    keys = [name_to_key.get(p.lower(), slugify(p, max_words=2)) for p in participants]
    loc_text = location if isinstance(location, str) else (location or {}).get("as_named_in_dialog", "")
    loc_slug = slugify(loc_text, max_words=2)
    base = "_".join(keys + ([loc_slug] if loc_slug and loc_slug != "unknown" else []))
    candidate = base
    n = 2
    while candidate in existing_ids:
        candidate = f"{base}_{n}"
        n += 1
    return candidate


def validate_claims(claims: list, existing_claim_ids: set) -> None:
    if not claims:
        raise SystemExit("claims must be a non-empty list.")
    for i, c in enumerate(claims):
        if "text" not in c or not c["text"]:
            raise SystemExit(f"claim[{i}] is missing required 'text'.")
        if "about" not in c:
            raise SystemExit(f"claim[{i}] is missing required key 'about' (use null if there is none).")
        derived_from = c.get("derived_from")
        if derived_from and derived_from not in existing_claim_ids:
            raise SystemExit(
                f"claim[{i}]'s 'derived_from' ('{derived_from}') doesn't resolve to any existing "
                f"hearsay claim id (<hearsay_entry_id>#<claim_index>) in encodings.json - this is the "
                f"retelling-genealogy edge (see TESTING_BRIEF.md §3.2 / measure_drift.py), and a "
                f"dangling one breaks the drift measure silently. Double-check the id against the "
                f"sampled pool item (sample_lore_knowledge.py's own printed format)."
            )


def location_summary(location) -> str:
    if isinstance(location, str):
        return location
    return (location or {}).get("as_named_in_dialog", "") or "(unspecified)"


def render_md_section(entry: dict) -> str:
    lines = [f"\n\n## `{entry['id']}.json`\n"]
    lines.append(f"- **Participants:** {'; '.join(entry['participants'])}")
    lines.append(f"- **Location:** {location_summary(entry['location'])}")
    lines.append(f"- **Summary:** {entry['summary']}")
    lines.append("- **Claims on record:**")
    for c in entry["claims"]:
        lines.append(f"  - {c['text']}")
        if c.get("note"):
            lines.append(f"    - *Note:* {c['note']}")
        if c.get("inconsistent_with_record"):
            lines.append(f"    - *Inconsistent with record:* {c['inconsistent_with_record']}")
        if c.get("inconsistent_with_facts"):
            lines.append(f"    - *Inconsistent with facts:* {c['inconsistent_with_facts']}")
        if c.get("derived_from"):
            lines.append(f"    - *Derived from:* {c['derived_from']}")
        if c.get("oral_lore"):
            lines.append("    - *Oral lore:* true")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--json-file", type=Path, default=None, help="Path to the input JSON. Reads stdin if omitted.")
    args = parser.parse_args()

    raw = args.json_file.read_text(encoding="utf-8") if args.json_file else sys.stdin.read()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise SystemExit(f"Input is not valid JSON: {e}")

    for key in ("participants", "location", "summary", "claims"):
        if key not in data:
            raise SystemExit(f"Input is missing required key '{key}'.")
    if not isinstance(data["participants"], list) or len(data["participants"]) < 1:
        raise SystemExit("'participants' must be a non-empty list.")

    with open(ENCODINGS_PATH, encoding="utf-8") as f:
        encodings = json.load(f)
    entries = encodings["hearsay"]["entries"]
    existing_ids = {e["id"] for e in entries}
    existing_claim_ids = {f"{e['id']}#{i}" for e in entries for i in range(1, len(e["claims"]) + 1)}
    validate_claims(data["claims"], existing_claim_ids)

    entry_id = data.get("id") or build_id(data["participants"], data["location"], existing_ids)
    if entry_id in existing_ids:
        raise SystemExit(f"id '{entry_id}' already exists in encodings.json hearsay.entries - pass an explicit unique 'id'.")

    location = data["location"] if isinstance(data["location"], dict) else {"id": None, "as_named_in_dialog": data["location"]}

    entry = {
        "id": entry_id,
        "source_file": data.get("source_file"),
        "participants": data["participants"],
        "location": location,
        "summary": data["summary"],
        "claims": data["claims"],
    }

    entries.append(entry)
    with open(ENCODINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(encodings, f, indent=2, ensure_ascii=False)
        f.write("\n")

    # Round-trip validate before touching the second file, so a bad write is caught immediately.
    with open(ENCODINGS_PATH, encoding="utf-8") as f:
        json.load(f)

    with open(HEARSAY_MD_PATH, "a", encoding="utf-8") as f:
        f.write(render_md_section(entry))

    print(f"id: {entry_id}")
    print(f"claims recorded: {len(entry['claims'])}")
    print("Wrote to: _lore/encodings.json (hearsay.entries), _lore/characters/hearsay.md")


if __name__ == "__main__":
    main()

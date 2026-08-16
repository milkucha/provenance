"""
Register a freshly-authored arc's own concept tag as a real concepts[] entry in encodings.json - the
permanent-automation half of the 2026-08-11 fix (the one-time catch-up half was
promote_arc_concepts.py, run once by hand; this script is what keeps the gap from reopening).

Call this immediately after any arc gets authored or re-authored in /simulate's extended mode -
Step 3's initial arc-authoring moment (a character's first primacy win as home_frame with no
existing arc) and Step 11's "failed arc gets a fresh one authored" case both qualify. No-ops
cleanly if the concept is already registered (e.g. a transform or death-legacy reuses an existing
concept tag rather than minting a new one) - never overwrites an existing entry.

Deliberately writes `sources: []` - this script only registers that the concept EXISTS; it never
decides which hearsay claims are about it. That linking is build_source_index.py's own job, and
running it is what keeps every new entry's provenance honestly hearsay-tagged
({"category": "hearsay", "origin": "<id>#<n>"}) rather than silently implying material-source
confirmation it doesn't have.

Usage:
    py scripts/lore/register_arc_concept.py <character_key>
      (reads the character's own current arc.about for its "concept: X" tag automatically)
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
ENCODINGS_PATH = ROOT / "_lore" / "encodings.json"
CHAR_DIR = ROOT / "_lore" / "characters"


def humanize(cid: str) -> str:
    return " ".join(w.capitalize() for w in cid.split("_"))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("character_key")
    args = parser.parse_args()

    key = args.character_key.lower()
    char_path = CHAR_DIR / f"{key}.json"
    if not char_path.exists():
        raise SystemExit(f"No character file for '{key}'.")
    with open(char_path, encoding="utf-8") as f:
        character = json.load(f)

    arc = character.get("arc")
    if not arc:
        raise SystemExit(f"'{key}' has no arc on record - nothing to register.")

    cid = None
    for tag in arc.get("about", []):
        if tag.startswith("concept: "):
            cid = tag[len("concept: "):].strip()
            break
    if not cid:
        print(f"'{key}'s arc.about has no 'concept: X' tag - nothing to register (location-only arc, presumably).")
        return

    with open(ENCODINGS_PATH, encoding="utf-8") as f:
        enc = json.load(f)

    existing_ids = {c["id"] for c in enc["concepts"]}
    if cid in existing_ids:
        print(f"concept '{cid}' already registered - no-op (transform/legacy reusing an existing tag).")
        return

    needs = ", ".join(arc.get("needs", [])) or "none on record"
    context = arc.get("context", "unspecified")
    resolution = arc.get("resolution", "unspecified")
    premise = arc.get("premise", "").strip()
    name = character.get("name", key)

    if premise:
        description = f"{premise} (Resolution as of this record: {resolution}.)"
    else:
        # Legacy fallback for an arc written before `premise` existed - the old boilerplate,
        # which never actually described what the project concretely is. See TODO.md.
        description = (
            f"{name}'s /simulate-authored arc project (context: {context}; needs: {needs}). "
            f"Resolution as of this record: {resolution}. Registered from the simulation's own "
            f"arc-tracking tag at authoring time - see the character's own arc.history for the "
            f"full progression."
        )

    entry = {
        "id": cid,
        "names": [humanize(cid), cid],
        "description": description,
        "sources": [],
        "notes": (
            "Auto-registered by register_arc_concept.py at arc-authoring time. Sourced entirely "
            "from hearsay once build_source_index.py links it (see sources[]) - no material-source "
            "confirmation."
        ),
    }
    enc["concepts"].append(entry)

    with open(ENCODINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(enc, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"registered concept: {cid}  (owner: {name})")


if __name__ == "__main__":
    main()

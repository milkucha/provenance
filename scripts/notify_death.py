"""
Compute who learns of a character's death directly, and who among them is due a shock.

Used by /enact when a character's last scene closes them out (horizon.py returns "final" - see
.claude/skills/character/SKILL.md Step 6 and /enact Step 5b point 6). Death itself is handled in two
tiers, and this script only ever computes the first:

    1. GUARANTEED - the character's "circle": everyone they've shared a scene with (co-participants
       across every _lore/analysis/encodings.json hearsay.entries record they appear in) plus
       everyone named in their own registered backstory. 30% of that circle (rounded, minimum 1 if
       the circle is non-empty) is notified immediately - this script picks who. The other 70%
       simply don't hear, not yet.
    2. PROBABILISTIC - everyone else. Handled outside this script entirely: the death is recorded as
       an ordinary _lore/discoveries/ entry (responsible: null, in the normal case), which folds into
       encodings.json and re-enters the same sampling pool as any other fact. Someone outside the
       circle only learns of it the normal way a person learns anything here - drawn into a future
       education sample, or told by someone who was in the circle, subject to the usual lineage_coin
       traceable/untraceable rule.

This script does only the mechanical half. It does NOT decide whether a notified character's
criterion reacts to the news - that judgement (reject / reinterpret / break, per /character Step 6)
stays with whoever is running /enact, same division of labor as Step 5b's shock resolution. What this
script CAN do mechanically is flag which notified characters are even eligible: anyone whose
criterion.anchor is an `experience: <scene_id>` or `hearsay: <entry>#n` that the deceased was a
participant in. That's a pointer check, not a judgement call, so it belongs here.

Usage:
    python scripts/notify_death.py <npc_key>
    python scripts/notify_death.py <npc_key> --seed 42   # reproducible sample
"""

import argparse
import json
from pathlib import Path
from random import Random

ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = ROOT / "_maps" / "npcs" / "registry.json"
ENCODINGS_PATH = ROOT / "_lore" / "analysis" / "encodings.json"


def load():
    with open(REGISTRY_PATH, encoding="utf-8") as f:
        npcs = json.load(f)["npcs"]
    with open(ENCODINGS_PATH, encoding="utf-8") as f:
        enc = json.load(f)
    return npcs, enc


def name_to_key_map(npcs: dict) -> dict:
    return {v["display_name"].lower(): k for k, v in npcs.items() if k != "_template" and v.get("display_name")}


def scene_participants_of(display_name: str, entries: list) -> list:
    """Every hearsay entry this display_name appears in, as (entry_id, other_participants)."""
    hits = []
    for e in entries:
        parts = e.get("participants", [])
        if any(p.lower() == display_name.lower() for p in parts):
            hits.append((e["id"], [p for p in parts if p.lower() != display_name.lower()]))
    return hits


def anchor_references(anchor: str, deceased_name: str, entries_by_id: dict) -> bool:
    """Does this criterion.anchor point at a scene the deceased participated in?"""
    if anchor.startswith("experience: ") or anchor.startswith("hearsay: "):
        scene_id = anchor.split(": ", 1)[1].split("#", 1)[0]
        entry = entries_by_id.get(scene_id)
        if entry:
            return any(p.lower() == deceased_name.lower() for p in entry.get("participants", []))
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("npc_key", help="Registry key of the character who died")
    parser.add_argument("--seed", type=int, default=None, help="Optional seed, for a reproducible sample")
    args = parser.parse_args()

    key = args.npc_key.lower()
    npcs, enc = load()

    if key not in npcs:
        raise SystemExit(f"No registry entry for '{key}'.")

    deceased = npcs[key]
    deceased_name = deceased["display_name"]
    entries = enc["hearsay"]["entries"]
    entries_by_id = {e["id"]: e for e in entries}
    name_to_key = name_to_key_map(npcs)

    circle_keys = set()

    for _scene_id, others in scene_participants_of(deceased_name, entries):
        for name in others:
            k = name_to_key.get(name.lower())
            if k and k != key:
                circle_keys.add(k)

    backstory = (deceased.get("backstory") or "").lower()
    for other_key, other_name in ((k, v["display_name"]) for k, v in npcs.items() if k not in ("_template", key)):
        if other_name.lower() in backstory:
            circle_keys.add(other_key)

    circle = sorted(circle_keys)
    n_notify = 0 if not circle else max(1, round(0.30 * len(circle)))

    rng = Random(args.seed)
    notified = sorted(rng.sample(circle, n_notify)) if n_notify else []
    remainder = sorted(k for k in circle if k not in notified)

    print(f"deceased: {key} ({deceased_name})")
    print(f"circle size: {len(circle)}  ->  notifying {n_notify} (30%)")
    print()
    print("NOTIFIED (write a knowledge.experience entry now):")
    for k in notified:
        anchor = npcs[k].get("criterion", {}).get("anchor", "") or ""
        shock = anchor_references(anchor, deceased_name, entries_by_id) if anchor else False
        flag = "  <-- SHOCK CANDIDATE: anchor references the deceased, resolve per /character Step 6" if shock else ""
        print(f"  {k}{flag}")
    print()
    print("NOT notified this round (may still hear later, via hearsay or the discovery record):")
    for k in remainder:
        print(f"  {k}")
    if not circle:
        print("  (circle is empty - this character shared no recorded scene and appears in no one's backstory)")


if __name__ == "__main__":
    main()

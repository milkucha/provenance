"""
Compute who learns of a character's death directly, and who among them is due a shock.

Used by /enact when a character's last scene closes them out (horizon.py's post-scene "ending" check
comes back true - see .claude/skills/character/SKILL.md Step 6 and /enact Step 8 point 6). Death
itself is handled in two tiers, and this script only ever computes the first:

    1. GUARANTEED - two parts, both always notified in full, no sampling:
       (a) RELATIONS: parents, children (reverse-looked-up via the child's own `parents` field), and
           anyone in the character's own `partners` field - the people who would obviously already
           know, structurally, regardless of how many scenes happen to have been written between them.
           Fixed 2026-08-10 (Run 2, /simulate's seventh extension): previously relations were only
           circle members BY COINCIDENCE, if a scene or backstory mention happened to register them -
           nothing guaranteed a parent or partner ever actually made the circle at all.
       (b) EXTENDED CIRCLE: everyone else who's shared a scene (co-participants across every
           _lore/encodings.json hearsay.entries record) or is named in the character's own backstory,
           minus anyone already counted as a relation. 30% of THIS group (rounded, minimum 1 if
           non-empty) is notified immediately - this script picks who. The other 70% simply don't
           hear, not yet.
    2. PROBABILISTIC - everyone else. Handled outside this script entirely: the death is recorded as
       an ordinary _lore/tales/ entry (told_by: null, in the normal case), which folds into
       encodings.json and re-enters the same sampling pool as any other fact. Someone outside the
       circle only learns of it the normal way a person learns anything here - drawn into a future
       education sample, or told by someone who was in the circle, subject to the usual lineage_coin
       traceable/untraceable rule.

This script does only the mechanical half. It does NOT decide whether a notified character's
criterion reacts to the news - that judgement (reject / reinterpret / break, per /character Step 6)
stays with whoever is running /enact, same division of labor as Step 8's shock resolution. What this
script CAN do mechanically is flag which notified characters are even eligible: anyone whose
criterion.anchor is an `experience: <scene_id>` or `hearsay: <entry>#n` that the deceased was a
participant in. That's a pointer check, not a judgement call, so it belongs here.

**Name matching is accent/diacritic-insensitive, deliberately** (fixed 2026-08-10, same debrief as
above): a character's canonical `name` field may carry accents (e.g. "Ilaría") that a scene
transcript or hearsay `participants` list doesn't always reproduce exactly - dialogue gets typed by
hand, not copy-pasted from the character file, every single time. Before this fix, an unaccented
"Ilaria" written into a scene never matched the accented "Ilaría" on file, so co-participation
matching silently failed for that character across an entire 115-pass run and her circle ended up
built almost entirely from two leftover pre-run lore entries instead of anything from the run itself.
`normalize()` below strips diacritics before comparing, so spelling drift in dialogue no longer
breaks the mechanism it's supposed to feed.

Usage:
    python scripts/lore/notify_death.py <npc_key>
    python scripts/lore/notify_death.py <npc_key> --seed 42   # reproducible sample
"""

import argparse
import json
import sys
import unicodedata
from pathlib import Path
from random import Random

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tuning  # noqa: E402  (sibling module, sys.path adjusted above)

ROOT = Path(__file__).resolve().parent.parent.parent
CHAR_DIR = ROOT / "_lore" / "characters"
ENCODINGS_PATH = ROOT / "_lore" / "encodings.json"

# Character data files only - excludes lifespans.json (not a character shape) and _template.json
# (not a real character). Deliberately reads _lore/characters/, not _npcs/npcs/registry.json: a
# character can die having only ever been enacted, never embodied in-game, so there may be no
# registry.json entry for them at all. name/backstory/criterion/life all live lore-side now.
_SKIP = {"_template", "lifespans"}


def load():
    characters = {}
    for path in CHAR_DIR.glob("*.json"):
        if path.stem in _SKIP:
            continue
        with open(path, encoding="utf-8") as f:
            characters[path.stem] = json.load(f)
    with open(ENCODINGS_PATH, encoding="utf-8") as f:
        enc = json.load(f)
    return characters, enc


def normalize(text: str) -> str:
    """Lowercase and strip diacritics, so name matching survives accent-spelling drift in dialogue."""
    text = unicodedata.normalize("NFKD", text or "")
    return "".join(ch for ch in text if not unicodedata.combining(ch)).lower()


def name_to_key_map(characters: dict) -> dict:
    return {normalize(v["name"]): k for k, v in characters.items() if v.get("name")}


def scene_participants_of(display_name: str, entries: list) -> list:
    """Every hearsay entry this display_name appears in, as (entry_id, other_participants)."""
    hits = []
    target = normalize(display_name)
    for e in entries:
        parts = e.get("participants", [])
        if any(normalize(p) == target for p in parts):
            hits.append((e["id"], [p for p in parts if normalize(p) != target]))
    return hits


def living_only(keys, characters: dict) -> set:
    """Drop any key whose character file is marked deceased - a dead character can't learn anything
    new, so they're never a valid notification target regardless of how close the relation is."""
    return {k for k in keys if not characters.get(k, {}).get("life", {}).get("deceased")}


def compute_relations(subject_keys, characters: dict) -> set:
    """
    Guaranteed-close relations for one or more subject character keys (e.g. both parents at a birth,
    or the one person at a death): each subject's own parents, each subject's other children (found
    by reverse-checking every character's own `parents` field for a subject key), and each subject's
    *frequent* partners - `partners[other] >= tuning.json's partner_threshold` (5 as of this writing),
    the same bar `roll_reproduction.py` already uses to decide two people are more than passing
    acquaintances. Deliberately NOT every recorded partner regardless of count: `partners` tracks
    every shared scene, so an established character's partners dict can list nearly the entire cast
    at 1-2 shared scenes each - including everyone there would make "guaranteed relations" functionally
    equal to "the whole cast," which defeats the purpose of distinguishing a close circle from an
    extended one. Always returns keys, never the subjects themselves. Deceased relations are filtered
    out before returning (via `living_only`) - a dead parent/child/partner is still a real relation,
    just never a valid notification target.
    """
    subject_keys = set(subject_keys)
    threshold = tuning.load()["partner_threshold"]
    relations = set()
    for skey in subject_keys:
        subject = characters.get(skey, {})
        relations |= set(subject.get("parents", []))
        relations |= {p for p, count in subject.get("partners", {}).items() if count >= threshold}
    for other_key, other_char in characters.items():
        if other_key in subject_keys:
            continue
        if subject_keys & set(other_char.get("parents", [])):
            relations.add(other_key)
    relations -= subject_keys
    return living_only(relations, characters)


def anchor_references(anchor: str, deceased_name: str, entries_by_id: dict) -> bool:
    """Does this criterion.anchor point at a scene the deceased participated in?"""
    if anchor.startswith("experience: ") or anchor.startswith("hearsay: "):
        scene_id = anchor.split(": ", 1)[1].split("#", 1)[0]
        entry = entries_by_id.get(scene_id)
        if entry:
            target = normalize(deceased_name)
            return any(normalize(p) == target for p in entry.get("participants", []))
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("npc_key", help="Character key of the character who died")
    parser.add_argument("--seed", type=int, default=None, help="Optional seed, for a reproducible sample")
    args = parser.parse_args()

    key = args.npc_key.lower()
    characters, enc = load()

    if key not in characters:
        raise SystemExit(f"No character file for '{key}'.")

    deceased = characters[key]
    deceased_name = deceased["name"]
    entries = enc["hearsay"]["entries"]
    entries_by_id = {e["id"]: e for e in entries}
    name_to_key = name_to_key_map(characters)

    relations = compute_relations([key], characters)

    extended_keys = set()
    for _scene_id, others in scene_participants_of(deceased_name, entries):
        for name in others:
            k = name_to_key.get(normalize(name))
            if k and k != key:
                extended_keys.add(k)

    backstory = normalize(deceased.get("backstory") or "")
    for other_key, other_name in ((k, v["name"]) for k, v in characters.items() if k != key):
        if normalize(other_name) in backstory:
            extended_keys.add(other_key)

    extended_keys = living_only(extended_keys, characters) - relations
    extended = sorted(extended_keys)
    n_notify = 0 if not extended else max(1, round(0.30 * len(extended)))

    rng = Random(args.seed)
    sampled = sorted(rng.sample(extended, n_notify)) if n_notify else []
    remainder = sorted(k for k in extended if k not in sampled)
    notified = sorted(relations) + sampled

    print(f"deceased: {key} ({deceased_name})")
    print(f"relations (guaranteed): {len(relations)}  |  extended circle: {len(extended)} -> sampling {n_notify} (30%)")
    print()
    print("NOTIFIED (write a knowledge.experience entry now):")
    for k in notified:
        anchor = characters[k].get("criterion", {}).get("anchor", "") or ""
        shock = anchor_references(anchor, deceased_name, entries_by_id) if anchor else False
        tag = "  [relation]" if k in relations else ""
        flag = "  <-- SHOCK CANDIDATE: anchor references the deceased, resolve per /character Step 6" if shock else ""
        print(f"  {k}{tag}{flag}")
    print()
    print("NOT notified this round (may still hear later, via hearsay or the tale record):")
    for k in remainder:
        print(f"  {k}")
    if not relations and not extended:
        print("  (circle is empty - this character shared no recorded scene, has no relations, and appears in no one's backstory)")


if __name__ == "__main__":
    main()

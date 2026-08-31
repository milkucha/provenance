"""
Report one character's whole social circle in one place - family (parents, reverse-looked-up
children, siblings) plus every tracked tie (partners{} strength, partners_quality{} sign), instead
of having to separately read `parents`, grep every other character's own `parents` field for
reverse hits, and eyeball `partners`/`partners_quality` side by side. Read-only - this script never
writes anything, it only ever reports what's already on record across `_lore/characters/*.json`.

Family reuses notify_death.py's own `compute_relations()` for parents/children/frequent-partners
(the same "guaranteed relations" tier death notification uses), then adds siblings on top - anyone
who shares at least one parent with the subject - which compute_relations() doesn't surface on its
own (it's built for "who gets notified," and a sibling with no shared scenes and no partners{} entry
wouldn't otherwise appear there). Unlike notify_death.py, deceased connections are NOT filtered out
here - a died-out rivalry or an ancestor who's passed is still a real, informative part of someone's
circle for a query like this, even though a dead character is never a valid notification target.

Every key in the union of `partners` and `partners_quality` gets listed, tagged "close" once
strength crosses `partner_threshold` (the same bar `roll_reproduction.py`/`compute_relations()`
already use to mean "more than a passing acquaintance"), sorted by strength descending so the
closest ties read first.

Usage:
    py scripts/lore/social_circle.py character_a
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import notify_death as nd  # noqa: E402
import tuning  # noqa: E402


def siblings_of(key: str, characters: dict) -> set:
    subject_parents = set(characters.get(key, {}).get("parents", []))
    if not subject_parents:
        return set()
    return {
        other_key for other_key, other_char in characters.items()
        if other_key != key and subject_parents & set(other_char.get("parents", []))
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("npc_key", help="Character key to report the social circle of")
    args = parser.parse_args()

    key = args.npc_key.lower()
    characters, _enc = nd.load()
    if key not in characters:
        raise SystemExit(f"No character file for '{key}'.")

    subject = characters[key]
    threshold = tuning.load()["partner_threshold"]

    parents = sorted(subject.get("parents", []))
    children = sorted(
        other_key for other_key, other_char in characters.items()
        if key in other_char.get("parents", [])
    )
    siblings = sorted(siblings_of(key, characters))
    frequent_partners = nd.compute_relations([key], characters)  # already excludes deceased

    def tag(other_key: str) -> str:
        return "  [deceased]" if characters.get(other_key, {}).get("life", {}).get("deceased") else ""

    print(f"social circle of {key} ({subject.get('name', key)})")
    print()
    print("FAMILY")
    print(f"  parents:   {', '.join(p + tag(p) for p in parents) or '(none on record)'}")
    print(f"  children:  {', '.join(c + tag(c) for c in children) or '(none on record)'}")
    print(f"  siblings:  {', '.join(s + tag(s) for s in siblings) or '(none on record)'}")
    print()

    strength = subject.get("partners", {})
    quality = subject.get("partners_quality", {})
    all_ties = sorted(set(strength) | set(quality), key=lambda k: strength.get(k, 0), reverse=True)

    print(f"TIES ({len(all_ties)} tracked)")
    if not all_ties:
        print("  (no tracked partners - this character has no recorded shared scenes yet)")
    for other_key in all_ties:
        s = strength.get(other_key, 0)
        q = quality.get(other_key)
        q_text = f"{q:+d}" if q is not None else "  0 (no signal yet)"
        close = "  [close]" if other_key in frequent_partners else ""
        print(f"  {other_key:<24} strength={s:<4} quality={q_text}{close}{tag(other_key)}")

    print()
    print(f"(\"close\" = strength >= partner_threshold, {threshold}, from _lore/tuning.json)")


if __name__ == "__main__":
    main()

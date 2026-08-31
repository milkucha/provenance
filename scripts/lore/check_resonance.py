"""
Find candidate pairs for /enact Step 9 (synthesis) - a character combining something they just
heard/lived this scene with something already in their standing knowledge into a third belief that
isn't reducible to either parent. Like check_anchor_reference.py's reference gate, this is a
mechanical narrowing pass only: it reports which pairs are even eligible, never whether a pairing
actually means anything. See .claude/skills/enact/SKILL.md Step 9 for the full division of labor.

Covers all five subtypes from TODO.md's "Synthesis mechanism" entry in one pass:

    1. causal/narrative       - fresh and standing item share an `about`/entity id, neither is a
                                 conflict or a person reference (see 3, 5 below)
    2. identity/coreference   - fresh and standing item's ids are a NEAR match (not exact - exact
                                 goes to 1/3/5) by name-string similarity; the "distinctive shared
                                 detail" call stays entirely with the model
    3. conflict-explanation   - fresh and standing item share an `about`/entity id, and that id is a
                                 conflict reference (bare CONFLICT-NN, or a `conflict:` category)
    4. pattern/generalization - the fresh item's category already has 2+ standing entries, so this
                                 scene's item would be the 3rd+ - a category-level frequency count,
                                 not true topic clustering (that judgment is the model's)
    5. relational/motive      - same mechanism as 1, but the shared id's category is a person
                                 category (anything under encodings.json's "characters." path -
                                 read from `_categories`, not hardcoded, so a category registered
                                 later is picked up automatically)

Standing knowledge is drawn from `knowledge.education.items` (always ref-shaped) plus any
`knowledge.experience` entry that's grounded - written as `{"text": ..., "about": <ref, or list of
refs>}` (via `update_character.py --add-grounded-experience`) rather than a bare string. An
ungrounded/legacy experience entry (a plain string, or an object with `about: null`) has no id to
match against and is skipped, same as `backstory` - a character's prose can still inform the model's
synthesis text once a script-reported candidate opens the door, but this script can't find it on its
own. See `.claude/skills/enact/SKILL.md` Step 6 for when an experience entry gets grounded (it
usually can be now - both what a character says and what they witness, self-revealed or picked up
from someone else, are all eligible to become a hearsay claim with a real `about` ref; only a fact
nobody ever voiced as a claim stays ungrounded).

Fresh-this-scene items come from the hearsay entry's claims (`--hearsay-id`), or pass `--about`
directly (repeatable) to check specific refs without a recorded entry.

Usage:
    py scripts/lore/check_resonance.py <npc_key> --hearsay-id <entry_id>
    py scripts/lore/check_resonance.py <npc_key> --about "highway: M7" --about "character_legendary: concept_a"
"""

import argparse
import json
import re
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
CHAR_DIR = ROOT / "_lore" / "characters"
ENCODINGS_PATH = ROOT / "_lore" / "encodings.json"

FUZZY_THRESHOLD = 0.77
CONFLICT_ID_RE = re.compile(r"^CONFLICT-\d+$")


def normalize(ref: str) -> str:
    """Accent/case/underscore/spacing-insensitive form, same tolerance check_anchor_reference.py
    and build_source_index.py already use - still a structural comparison, never fuzzy matching a
    genuinely different id."""
    ref = unicodedata.normalize("NFKD", ref).encode("ascii", "ignore").decode("ascii")
    ref = ref.replace("_", " ").strip().lower()
    ref = re.sub(r"\s*:\s*", ": ", ref)
    return re.sub(r"\s+", " ", ref).strip()


def id_part(ref: str) -> str:
    normalized = normalize(ref)
    return normalized.split(": ", 1)[1].strip() if ": " in normalized else normalized


def category_of(ref: str) -> str:
    """'conflict' for a bare CONFLICT-NN id, the prefix before ': ' otherwise, or '' if the ref
    isn't shaped like either (a free-text item this script can't classify). Deliberately does NOT
    go through normalize() - that strips underscores for id-matching tolerance, which would mangle
    a category key like 'character_legendary' into 'character legendary' and break the lookup
    against _categories' actual keys. Only colon-spacing and case are normalized here."""
    s = ref.strip()
    if CONFLICT_ID_RE.match(s):
        return "conflict"
    s = re.sub(r"\s*:\s*", ": ", s.lower())
    return s.split(": ", 1)[0] if ": " in s else ""


def person_categories(categories_schema: dict) -> set:
    """Any category filed under encodings.json's 'characters.' path - read from `_categories`
    itself so a category /integrate registers later is picked up automatically, same principle
    build_source_index.py's load_categories() already follows."""
    return {
        cat_key for cat_key, spec in categories_schema.items()
        if spec.get("path", "").startswith("characters.")
    }


def load_character(key: str) -> dict:
    char_path = CHAR_DIR / f"{key}.json"
    if not char_path.exists():
        raise SystemExit(f"No character file for '{key}'.")
    with open(char_path, encoding="utf-8") as f:
        return json.load(f)


def standing_refs(character: dict) -> list:
    """education.items (always ref-shaped) plus any grounded knowledge.experience entry's `about`
    ref(s) - a plain string or an object with `about: null` has nothing to extract and is skipped.
    Includes synthesis entries (`kind: synthesis`) too - those already carry a real `about` list,
    no different in shape from an ordinary grounded entry for matching purposes."""
    refs = list(character.get("knowledge", {}).get("education", {}).get("items", []) or [])
    for entry in character.get("knowledge", {}).get("experience", []) or []:
        if not isinstance(entry, dict):
            continue  # legacy/ungrounded plain string
        about = entry.get("about")
        if about is None:
            continue
        refs.extend(about if isinstance(about, list) else [about])
    return refs


def load_fresh_refs(args) -> list:
    """Returns [(claim_label, ref), ...] for every `about` ref in play this scene."""
    refs = []
    if args.hearsay_id:
        with open(ENCODINGS_PATH, encoding="utf-8") as f:
            entries = json.load(f)["hearsay"]["entries"]
        entry = next((e for e in entries if e["id"] == args.hearsay_id), None)
        if entry is None:
            raise SystemExit(f"No hearsay entry with id '{args.hearsay_id}'.")
        for i, c in enumerate(entry["claims"]):
            about = c.get("about")
            values = about if isinstance(about, list) else ([about] if about else [])
            for v in values:
                refs.append((f"{entry['id']}#{i}", v))
    for v in args.about:
        refs.append((None, v))
    return refs


def find_exact_matches(fresh_refs: list, standing: list, person_cats: set) -> dict:
    """Subtypes 1/3/5 share one mechanism (shared entity id); this classifies each hit by what
    kind of entity it is."""
    buckets = {"causal/narrative": [], "conflict-explanation": [], "relational/motive": []}
    for claim_label, fresh in fresh_refs:
        fresh_norm, fresh_id = normalize(fresh), id_part(fresh)
        for standing_ref in standing:
            standing_norm, standing_id = normalize(standing_ref), id_part(standing_ref)
            if fresh_norm != standing_norm and fresh_id != standing_id:
                continue
            cat = category_of(fresh) or category_of(standing_ref)
            if cat == "conflict":
                bucket = "conflict-explanation"
            elif cat in person_cats:
                bucket = "relational/motive"
            else:
                bucket = "causal/narrative"
            buckets[bucket].append((claim_label, fresh, standing_ref))
    return buckets


def find_identity_candidates(fresh_refs: list, standing: list) -> list:
    """Subtype 2: near-miss only - an exact match already went to find_exact_matches above.
    Scoped within one category at a time, same false-positive guard build_source_index.py's
    find_fuzzy() already uses ("never a location against a character"). 'conflict' is excluded
    entirely - CONFLICT-NN ids are structurally near-identical by design (sequential numbering),
    so string similarity there is noise, not a naming coincidence; subtype 3 already owns
    conflict-tag matching, exact only."""
    hits = []
    for claim_label, fresh in fresh_refs:
        fresh_cat, fresh_id = category_of(fresh), id_part(fresh)
        if not fresh_cat or fresh_cat == "conflict":
            continue
        for standing_ref in standing:
            standing_cat, standing_id = category_of(standing_ref), id_part(standing_ref)
            if standing_cat != fresh_cat or fresh_id == standing_id:
                continue
            score = SequenceMatcher(None, fresh_id, standing_id).ratio()
            if score >= FUZZY_THRESHOLD:
                hits.append((claim_label, fresh, standing_ref, round(score, 2)))
    return hits


def find_pattern_candidates(fresh_refs: list, standing: list) -> list:
    """Subtype 4: category-level frequency, not true topic clustering - see module docstring."""
    by_category = {}
    for standing_ref in standing:
        cat = category_of(standing_ref)
        if cat:
            by_category.setdefault(cat, []).append(standing_ref)

    hits = []
    for claim_label, fresh in fresh_refs:
        cat = category_of(fresh)
        existing = by_category.get(cat, [])
        if cat and len(existing) >= 2:
            hits.append((claim_label, fresh, cat, existing))
    return hits


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("npc_key", help="Character key, e.g. 'character_a'")
    parser.add_argument("--hearsay-id", default=None, help="A hearsay.entries id - checks all of that entry's claims")
    parser.add_argument("--about", action="append", default=[], help="An 'about' ref to check directly. Repeatable.")
    args = parser.parse_args()

    key = args.npc_key.lower()
    character = load_character(key)
    standing = standing_refs(character)

    if not args.hearsay_id and not args.about:
        raise SystemExit("Nothing to check - pass --hearsay-id or one or more --about.")

    fresh_refs = load_fresh_refs(args)
    if not fresh_refs:
        print(f"character: {key}")
        print("No fresh refs this scene (every claim's `about` was null) - no candidates possible.")
        return

    print(f"character: {key}")
    print(f"fresh refs this scene: {len(fresh_refs)}")
    print(f"standing refs (education + grounded experience): {len(standing)}")
    print()

    if not standing:
        print("No standing knowledge to pair against - no candidates possible.")
        return

    with open(ENCODINGS_PATH, encoding="utf-8") as f:
        categories_schema = json.load(f).get("_categories", {})
    person_cats = person_categories(categories_schema)

    exact = find_exact_matches(fresh_refs, standing, person_cats)
    identity = find_identity_candidates(fresh_refs, standing)
    pattern = find_pattern_candidates(fresh_refs, standing)

    total = 0

    def report(subtype: str, hits: list, render):
        nonlocal total
        print(f"[{subtype}] {len(hits)} candidate(s)")
        for hit in hits:
            print(f"  {render(hit)}")
        total += len(hits)
        print()

    report("1. causal/narrative", exact["causal/narrative"],
           lambda h: f"{h[0] or '(direct)'}: '{h[1]}' <-> standing '{h[2]}'")
    report("2. identity/coreference", identity,
           lambda h: f"{h[0] or '(direct)'}: '{h[1]}' ~ standing '{h[2]}' (similarity {h[3]})")
    report("3. conflict-explanation", exact["conflict-explanation"],
           lambda h: f"{h[0] or '(direct)'}: '{h[1]}' <-> standing '{h[2]}'")
    report("4. pattern/generalization", pattern,
           lambda h: f"{h[0] or '(direct)'}: '{h[1]}' would be occurrence {len(h[3]) + 1} of category "
                     f"'{h[2]}' (existing: {', '.join(h[3])})")
    report("5. relational/motive", exact["relational/motive"],
           lambda h: f"{h[0] or '(direct)'}: '{h[1]}' <-> standing '{h[2]}'")

    if total == 0:
        print("No candidates in any subtype. Default applies: no synthesis this scene.")
    else:
        print(f"{total} total candidate(s) across all subtypes. Judge each per SKILL.md Step 9 "
              "point 3 - most should still produce nothing.")


if __name__ == "__main__":
    main()

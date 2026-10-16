"""
The circle writer: the one place that writes a character's `social_circle` (design session
2026-10-17, TODO.md "Travel as nodes, social circle writer, class through inheritance"). Before this
nothing wrote the field, and the known-supplier tier of destination choice (location_context) and
the death notification (notify_death) had only partners/parents to go on.

SHAPE. `social_circle` is a stored map {character key: kind}, never computed on read:

    "social_circle": {"khaoe": "parent", "farlis": "met", "belken": "inherited", "ilaria": "mentioned"}

Kinds, STRONGEST FIRST (a person who is several things at once keeps the strongest; a tie is only
ever upgraded, never downgraded):
    parent       the character's own parents
    child        their children
    descendant   grandchildren and further down
    met          shared a scene (record_partner.py; backfill: any `partners` key)
    inherited    in a parent's circle when the character was born (the social capital: a seeded draw
                 of `social_circle.inherit_share`, 30%, of EACH parent's circle, logged as the
                 `social_circle_inherit` draw)
    mentioned    referenced in their knowledge - an education item (`character: <key>`, or any item
                 whose text, resolved through encodings.json, names someone) or an experience entry
                 (its text, or an `about` tag)
The author's sources, one for one: parents and 30% of their circles (parent, inherited), characters
they have met (met), characters referenced in their knowledge (mentioned), their children and
descendants (child, descendant). The dead stay in the circle (a dead parent is still a parent); the
readers that mean "alive" filter for it themselves. The old shape was a bare list; `normalize_circle`
reads it as {key: "mentioned"} (a list never said how they knew each other).

WHEN IT RUNS (every call site is in-process, an import of this module):
    birth         generate_offspring.py -> on_birth(): parents (parent), a seeded share of each
                  parent's circle (inherited), the child's own knowledge refs (mentioned); then the
                  child goes into each parent's circle (child) and every ancestor's (descendant)
    a scene       record_partner.py -> add_tie(.., "met")
    knowledge     pass_apply.py, after a scene's experience writes -> `mentions <p1> <p2>` (this CLI);
                  record_death.py / generate_offspring.py / arc_completion.py add the one mention
                  their own notification line creates
    old worlds    backfill_social_circle.py (dry-run by default)

Usage:
    py scripts/lore/update_social_circle.py met khaoe farlis
    py scripts/lore/update_social_circle.py mentions khaoe farlis
    py scripts/lore/update_social_circle.py birth --child khordarel [--seed 7]
"""

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path
from random import Random

SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT = SCRIPTS_DIR.parent.parent
CHAR_DIR = ROOT / "_lore" / "characters"
ENCODINGS_PATH = ROOT / "_lore" / "encodings.json"

sys.path.insert(0, str(SCRIPTS_DIR))
import rng_context  # noqa: E402
import tuning  # noqa: E402

KINDS = ("parent", "child", "descendant", "met", "inherited", "mentioned")  # strongest first
RANK = {k: i for i, k in enumerate(KINDS)}
_SKIP = {"_template", "lifespans"}


# --------------------------------------------------------------------------------------------
# Pure functions on character dicts
# --------------------------------------------------------------------------------------------

def normalize_circle(raw) -> dict:
    """The stored circle as {key: kind}, whatever shape is on disk (None, the old list, the map)."""
    if not raw:
        return {}
    if isinstance(raw, dict):
        return dict(raw)
    return {k: "mentioned" for k in raw}


def add_tie(character: dict, other: str, kind: str) -> bool:
    """Put `other` in the character's circle as `kind`, keeping the stronger kind if they are already
    there (a tie is only ever upgraded). A circle still in the old list shape is converted on the way.
    The caller is responsible for never passing the character's own key. Returns True if the circle
    changed."""
    assert kind in RANK, kind
    circle = normalize_circle(character.get("social_circle"))
    had_old_shape = not isinstance(character.get("social_circle"), dict) and bool(character.get("social_circle"))
    if other not in circle or RANK[kind] < RANK.get(circle[other], len(KINDS)):
        circle[other] = kind
        character["social_circle"] = circle
        return True
    if had_old_shape:
        character["social_circle"] = circle
        return True
    return False


def inherit_draw(parent_circle: dict, exclude: set, rng: Random, share: float) -> list:
    """The social capital a parent hands down: `share` of their circle (minus `exclude`, the child and
    the parents themselves), rounded, at least one if there is anyone to give. Sorted candidates,
    so a seeded draw is the same in every process."""
    cands = sorted(k for k in normalize_circle(parent_circle) if k not in exclude)
    n = 0 if not cands else max(1, round(share * len(cands)))
    return sorted(rng.sample(cands, n)) if n else []


def norm_text(text: str) -> str:
    text = unicodedata.normalize("NFKD", text or "")
    return "".join(ch for ch in text if not unicodedata.combining(ch)).lower()


def build_matcher(characters: dict):
    """(regex, {normalized name: key}) over every character's display name, whole words only so a
    short name inside a longer word does not fire. Accent-insensitive (notify_death.normalize's
    discipline). None if nobody has a usable name."""
    by_name = {}
    for k, c in characters.items():
        n = norm_text(c.get("name") or "").strip()
        if len(n) >= 3:
            by_name[n] = k
    if not by_name:
        return None, {}
    names = sorted(by_name, key=len, reverse=True)
    rx = re.compile(r"(?<![a-z0-9])(" + "|".join(re.escape(n) for n in names) + r")(?![a-z0-9])")
    return rx, by_name


def build_index(enc: dict) -> dict:
    """{ref: text} for the refs a knowledge item can carry that may name a person: tales, concepts,
    conflicts, hearsay claims. (Locations and routes name places, not people.)"""
    out = {}
    for t in (enc.get("tales") or {}).get("entries", []) or []:
        out[f"tale: {t['id']}"] = t.get("summary", "")
    for c in enc.get("concepts", []) or []:
        out[f"concept: {c['id']}"] = " ".join([c.get("description", "")] + (c.get("names") or []))
    for c in enc.get("conflicts", []) or []:
        out[f"conflict: {c['id']}"] = f"{c.get('topic', '')} {c.get('detail', '')}"
    for h in (enc.get("hearsay") or {}).get("entries", []) or []:
        for i, claim in enumerate(h.get("claims", []), 1):
            out[f"hearsay: {h['id']}#{i}"] = claim.get("text", "")
    return out


def mentioned_keys(character: dict, self_key: str, characters: dict, matcher, index: dict) -> set:
    """Everyone this character's knowledge refers to: `character: <key>` education items and `about`
    tags directly; otherwise any other character whose name appears (whole word) in the text of an
    education item (resolved through `index`) or an experience entry."""
    rx, by_name = matcher
    know = character.get("knowledge") or {}
    texts, direct = [], set()
    for ref in (know.get("education") or {}).get("items") or []:
        ref = str(ref)
        if ref.startswith("character: "):
            direct.add(ref.split(": ", 1)[1].strip())
        texts.append(index.get(ref, ""))
    for entry in know.get("experience") or []:
        if isinstance(entry, dict):
            texts.append(entry.get("text", ""))
            about = entry.get("about")
            for tag in (about if isinstance(about, list) else [about] if about else []):
                if isinstance(tag, str) and tag.startswith("character: "):
                    direct.add(tag.split(": ", 1)[1].strip())
        else:
            texts.append(str(entry))
    found = {k for k in direct if k in characters}
    if rx is not None:
        for t in texts:
            for m in rx.finditer(norm_text(t)):
                found.add(by_name[m.group(1)])
    found.discard(self_key)
    return found


def ancestors(key: str, characters: dict) -> set:
    seen, stack = set(), list((characters.get(key) or {}).get("parents") or [])
    while stack:
        p = stack.pop()
        if p in seen or p not in characters:
            continue
        seen.add(p)
        stack.extend((characters[p] or {}).get("parents") or [])
    return seen


# --------------------------------------------------------------------------------------------
# File-level operations
# --------------------------------------------------------------------------------------------

def load_all() -> dict:
    out = {}
    for path in sorted(CHAR_DIR.glob("*.json")):
        if path.stem in _SKIP:
            continue
        with open(path, encoding="utf-8") as f:
            try:
                out[path.stem] = json.load(f)
            except json.JSONDecodeError:
                continue
    return out


def save(key: str, character: dict) -> None:
    with open(CHAR_DIR / f"{key}.json", "w", encoding="utf-8") as f:
        json.dump(character, f, indent=2, ensure_ascii=False)
        f.write("\n")


def load_encodings() -> dict:
    with open(ENCODINGS_PATH, encoding="utf-8") as f:
        return json.load(f)


def refresh_mentions(keys: list, characters: dict | None = None) -> dict:
    """Re-read each character's knowledge and add every referenced person as `mentioned` (a stronger
    existing kind stays). Returns {key: [newly added keys]}. Writes only the files that changed."""
    characters = characters if characters is not None else load_all()
    matcher = build_matcher(characters)
    index = build_index(load_encodings())
    added = {}
    for key in keys:
        c = characters.get(key)
        if c is None:
            continue
        new = []
        for other in sorted(mentioned_keys(c, key, characters, matcher, index)):
            if other not in normalize_circle(c.get("social_circle")) and add_tie(c, other, "mentioned"):
                new.append(other)
        if new:
            save(key, c)
        added[key] = new
    return added


def add_met(a: str, b: str) -> None:
    """Both directions, one file write each. Used by the CLI; record_partner.py (one direction per
    call, like partners{}) calls add_tie itself on the file it already holds."""
    for x, y in ((a, b), (b, a)):
        path = CHAR_DIR / f"{x}.json"
        with open(path, encoding="utf-8") as f:
            c = json.load(f)
        if add_tie(c, y, "met"):
            save(x, c)


def on_birth(child_key: str, share: float | None = None) -> dict:
    """Everything the circle writer does at a birth, after the child's file exists. See the module
    docstring. The inheritance draw goes through rng_context (reserve_seed / log_draw, so a seeded
    run reproduces it and the audit shows it as `social_circle_inherit`). Returns what was written."""
    share = tuning.load()["social_circle"]["inherit_share"] if share is None else share
    characters = load_all()
    child = characters[child_key]
    parents = [p for p in child.get("parents") or [] if p in characters]
    child["social_circle"] = {}
    for p in parents:
        add_tie(child, p, "parent")

    seed, draw_index = rng_context.reserve_seed(ROOT)
    rng = Random(seed)
    inherited = {}
    for p in parents:  # in the order the file lists them
        picked = inherit_draw(characters[p].get("social_circle"), {child_key, *parents}, rng, share)
        inherited[p] = picked
        for other in picked:
            add_tie(child, other, "inherited")
    rng_context.log_draw(ROOT, "social_circle_inherit", [child_key], {"child": child_key, "inherited": inherited}, seed, draw_index)

    matcher = build_matcher(characters)
    index = build_index(load_encodings())
    for other in sorted(mentioned_keys(child, child_key, characters, matcher, index)):
        add_tie(child, other, "mentioned")
    save(child_key, child)

    for anc in sorted(ancestors(child_key, characters)):
        c = characters[anc]
        if add_tie(c, child_key, "child" if anc in parents else "descendant"):
            save(anc, c)
    return {"parents": parents, "inherited": inherited, "circle": child["social_circle"]}


# --------------------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("met")
    m.add_argument("a")
    m.add_argument("b")
    mm = sub.add_parser("mentions")
    mm.add_argument("keys", nargs="+")
    b = sub.add_parser("birth")
    b.add_argument("--child", required=True)
    b.add_argument("--seed", type=int, default=None, help="Accepted so a seeded driver can pass it; the draw takes its own seed from the run state (rng_context)")
    a = ap.parse_args()

    if a.cmd == "met":
        add_met(a.a.lower(), a.b.lower())
        print(f"{a.a} and {a.b}: met")
    elif a.cmd == "mentions":
        for k, new in refresh_mentions([x.lower() for x in a.keys]).items():
            print(f"{k}: mentioned += {new}")
    else:
        r = on_birth(a.child.lower())
        print(f"{a.child}: circle of {len(r['circle'])} ({r['inherited']})")


if __name__ == "__main__":
    main()

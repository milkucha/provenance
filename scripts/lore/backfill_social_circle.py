"""
Backfill `social_circle` for a population that predates the circle writer (update_social_circle.py).
DRY-RUN BY DEFAULT: prints what it would write and touches nothing. `--apply` writes, and refuses to
without an explicit `--root`, so this can never run on a real `_lore` by accident - point it at a
scratch copy or at a world you have decided to migrate.

What it rebuilds, per character, in generation order (parents before children, so a child's
inheritance draw sees the parents' finished circles):
    parent       from `parents`
    child / descendant   from the reverse of everyone's `parents` (direct children, then lower)
    met          every key in `partners`
    inherited    the same seeded draw a newborn gets: `social_circle.inherit_share` of EACH parent's
                 finished circle, excluding the character and the parents (here the draw is this
                 script's own `--seed`, default 0, one stream per character, not the run's rng_context:
                 a backfill is not a pass)
    mentioned    names and `character:` refs in their knowledge (update_social_circle.mentioned_keys)
An existing circle is kept and only upgraded (a stronger kind wins), so running it twice changes
nothing the second time (each character's draw is its own seeded stream, and is skipped for
anyone already holding an `inherited` tie, e.g. from a real birth).

Usage:
    py scripts/lore/backfill_social_circle.py --root ../scratch-copy                  # dry run
    py scripts/lore/backfill_social_circle.py --root ../scratch-copy --apply --seed 3
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from random import Random

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))
import update_social_circle as usc  # noqa: E402
import tuning  # noqa: E402

_SKIP = {"_template", "lifespans"}


def generation_order(characters: dict) -> list:
    """Parents before children (founders first); ties by key so the order is the same everywhere."""
    depth = {}

    def d(k, seen=()):
        if k in depth:
            return depth[k]
        ps = [p for p in (characters[k].get("parents") or []) if p in characters and p not in seen]
        depth[k] = 0 if not ps else 1 + max(d(p, seen + (k,)) for p in ps)
        return depth[k]

    for k in characters:
        d(k)
    return sorted(characters, key=lambda k: (depth[k], k))


def descendants(key: str, kids: dict) -> set:
    out, stack = set(), list(kids.get(key, []))
    while stack:
        c = stack.pop()
        if c not in out:
            out.add(c)
            stack.extend(kids.get(c, []))
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=None, help="World root to read (and, with --apply, write). Required for --apply.")
    ap.add_argument("--apply", action="store_true", help="Write the circles. Without it, a dry run.")
    ap.add_argument("--seed", type=int, default=0, help="Seed for the inheritance draw (default 0)")
    a = ap.parse_args()
    if a.apply and not a.root:
        raise SystemExit("--apply needs an explicit --root: this never writes the repo's own _lore by default.")
    root = Path(a.root).resolve() if a.root else SCRIPTS_DIR.parent.parent
    char_dir = root / "_lore" / "characters"
    if not char_dir.is_dir():
        raise SystemExit(f"{char_dir} does not exist")

    characters = {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in sorted(char_dir.glob("*.json")) if p.stem not in _SKIP}
    enc = json.loads((root / "_lore" / "encodings.json").read_text(encoding="utf-8"))
    share = tuning.load()["social_circle"]["inherit_share"]
    matcher = usc.build_matcher(characters)
    index = usc.build_index(enc)

    kids = {}
    for k, c in characters.items():
        for p in c.get("parents") or []:
            kids.setdefault(p, []).append(k)

    before = {k: usc.normalize_circle(c.get("social_circle")) for k, c in characters.items()}
    for k in generation_order(characters):
        c = characters[k]
        parents = [p for p in (c.get("parents") or []) if p in characters]
        c["social_circle"] = dict(before[k])
        for p in parents:
            usc.add_tie(c, p, "parent")
        for ch in sorted(kids.get(k, [])):
            usc.add_tie(c, ch, "child")
        direct = set(kids.get(k, []))
        for ch in sorted(descendants(k, kids) - direct):
            usc.add_tie(c, ch, "descendant")
        for o in sorted(c.get("partners") or {}):
            if o in characters and o != k:
                usc.add_tie(c, o, "met")
        if parents and "inherited" not in set(usc.normalize_circle(c["social_circle"]).values()):
            rng = Random(f"{a.seed}:{k}")  # one stream per character: the same draw on every run, in any order
            for p in parents:
                for o in usc.inherit_draw(characters[p].get("social_circle"), {k, *parents}, rng, share):
                    usc.add_tie(c, o, "inherited")
        for o in sorted(usc.mentioned_keys(c, k, characters, matcher, index)):
            usc.add_tie(c, o, "mentioned")

    changed = [k for k in characters if usc.normalize_circle(characters[k].get("social_circle")) != before[k]]
    kinds = Counter()
    for k in characters:
        kinds.update(usc.normalize_circle(characters[k].get("social_circle")).values())
    sizes = sorted(len(usc.normalize_circle(characters[k]["social_circle"])) for k in characters)
    print(f"{'APPLY' if a.apply else 'DRY RUN'} - root {root}")
    print(f"characters: {len(characters)}, circles that would change: {len(changed)}")
    print("ties by kind: " + ", ".join(f"{kk} {kinds.get(kk, 0)}" for kk in usc.KINDS))
    if sizes:
        print(f"circle size: min {sizes[0]}, median {sizes[len(sizes) // 2]}, max {sizes[-1]}")
    if a.apply:
        for k in changed:
            (char_dir / f"{k}.json").write_text(json.dumps(characters[k], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"wrote {len(changed)} character files")
    else:
        print("(nothing written; --root <scratch copy> --apply to write)")


if __name__ == "__main__":
    main()

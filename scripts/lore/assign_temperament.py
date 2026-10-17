"""
Give existing characters a temperament (risk, thrift, communality, persistence; each in [-1, 1]), for a
population that was made before the field existed, or to author one character's by hand. See
temperament.py and TODO.md, "Temperament traits and recent trends in the work roll".

Dry run by default: prints what would be drawn and writes nothing. `--apply` writes. `--root` is
REQUIRED and is never a default: this tool writes character files, so it is only ever pointed at a
root on purpose (a scratch copy, a worktree), never at a real `_lore` by accident.

  - Without `--key`: every LIVING character that has no `temperament` field yet gets a seeded uniform
    draw in [-1, 1] per trait. Characters that already have one are left alone (`--force` redraws).
    Each character's draw uses its own Random derived from `--seed` and the character's place in the
    sorted list of keys, so the result does not depend on who else is in the folder being processed first;
    with `--apply` every draw is appended to the root's draw audit (`.simulate_draw_audit.jsonl`).
  - With `--key K --set risk=0.6 thrift=-0.2 ...`: authors that one character's traits by hand (the other
    traits keep their value, or 0). No dice.
  - With `--key K` and no `--set`: draws that one character's traits (seeded, the same uniform draw), the
    way /character gives a new character one when the user has no disposition in mind. Nobody is left
    without a temperament (2026-10-17).

Usage:
    py scripts/lore/assign_temperament.py --root /path/to/root --seed 7            # dry run
    py scripts/lore/assign_temperament.py --root /path/to/root --seed 7 --apply
    py scripts/lore/assign_temperament.py --root /path/to/root --key khaoe --set risk=0.6 persistence=-0.4 --apply
    py scripts/lore/assign_temperament.py --root /path/to/root --key khaoe --seed 7 --apply      # draw one
"""

import argparse
import json
import secrets
import sys
from pathlib import Path
from random import Random

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))
import rng_context  # noqa: E402
import temperament  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", required=True, help="the root whose _lore/characters/ is read (and written with --apply)")
    ap.add_argument("--apply", action="store_true", help="write the files (default: dry run)")
    ap.add_argument("--seed", type=int, default=None, help="seed for the draws (default: a fresh one, printed)")
    ap.add_argument("--force", action="store_true", help="redraw characters that already have a temperament")
    ap.add_argument("--key", default=None, help="author one character's traits instead of drawing")
    ap.add_argument("--set", nargs="*", default=[], help="trait=value for --key, e.g. risk=0.6")
    a = ap.parse_args()

    root = Path(a.root).resolve()
    chars_dir = root / "_lore" / "characters"
    if not chars_dir.is_dir():
        raise SystemExit(f"{chars_dir} does not exist")
    paths = sorted(p for p in chars_dir.glob("*.json") if p.stem not in ("_template", "lifespans"))
    tag = "APPLY" if a.apply else "DRY RUN (nothing written; pass --apply)"
    print(f"{tag}: {root}")

    def write(path: Path, c: dict) -> None:
        if a.apply:
            path.write_text(json.dumps(c, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if a.key:
        path = chars_dir / f"{a.key.lower()}.json"
        if not path.exists():
            raise SystemExit(f"No character file for '{a.key}'.")
        c = json.loads(path.read_text(encoding="utf-8"))
        traits = temperament.traits_of(c)
        seed = a.seed if a.seed is not None else secrets.randbelow(10 ** 9)
        if not a.set:
            traits = temperament.draw_random(Random(rng_context.derive_seed(seed, 0)))
            print(f"seed: {seed}")
        for item in a.set:
            k, _, v = item.partition("=")
            if k not in temperament.TRAITS:
                raise SystemExit(f"'{k}' is not a trait ({', '.join(temperament.TRAITS)})")
            traits[k] = temperament.clamp(float(v))
        c["temperament"] = {k: round(traits[k], 2) for k in temperament.TRAITS}
        write(path, c)
        if a.apply and not a.set:
            rng_context.log_draw(root, "assign_temperament.py", [path.stem, "--seed", str(seed)], {"temperament": temperament.fmt(c["temperament"])}, rng_context.derive_seed(seed, 0), 0)
        print(f"{path.stem}: {temperament.fmt(c['temperament'])}")
        return

    seed = a.seed if a.seed is not None else secrets.randbelow(10 ** 9)
    print(f"seed: {seed}")
    done = skipped = 0
    for i, path in enumerate(paths):
        c = json.loads(path.read_text(encoding="utf-8"))
        if (c.get("life") or {}).get("deceased"):
            continue
        if c.get("temperament") and not a.force:
            skipped += 1
            continue
        s = rng_context.derive_seed(seed, i)
        traits = temperament.draw_random(Random(s))
        c["temperament"] = traits
        write(path, c)
        if a.apply:
            rng_context.log_draw(root, "assign_temperament.py", [path.stem, "--seed", str(seed)], {"temperament": temperament.fmt(traits)}, s, i)
        done += 1
        print(f"{path.stem}: {temperament.fmt(traits)}")
    print(f"{'assigned' if a.apply else 'would assign'}: {done}; left alone (already have one): {skipped}")


if __name__ == "__main__":
    main()

"""
DEPRECATED for its original purpose (2026-08-16): computes a character's knowledge.education.items
category distribution against the rest of the corpus's baseline. This used to back /character Step
4d's tiebreaker for trusts/distrusts ("over-representation against the other characters' baseline",
e.g. "Döran holding 12% chronicle items where everyone else holds 2-7%") - Step 4d now derives
trusts/distrusts from provenance instead (see scripts/lore/anchor_epistemology.py), which resolves
every anchor to a definite answer (or genuinely none) without needing a tiebreaker at all. Left in
place since the underlying distribution-vs-corpus-baseline computation may still be useful for other
purposes; just no longer called by Step 4d.

This script only ever computes the signal, never decides anything - same discipline as
anchor_epistemology.py. Read Step 4d's own reasoning before treating a number here as decisive: raw
distribution mostly measures how the sample was drawn (a `--mode skewed` topic), not who the
character is.

Each item in knowledge.education.items is a string like "era_ensayo: Las Guerras de Gorff" - the
category is everything before the first ": ".

Usage:
    py scripts/lore/baseline_stats.py <npc_key>
    py scripts/lore/baseline_stats.py <npc_key> --category hearsay
"""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
CHAR_DIR = ROOT / "_lore" / "characters"
_SKIP = {"_template", "lifespans"}


def category_of(item: str) -> str:
    return item.split(": ", 1)[0] if ": " in item else item


def counts_for(items: list) -> dict:
    counts: dict = {}
    for it in items:
        cat = category_of(it)
        counts[cat] = counts.get(cat, 0) + 1
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("npc_key", help="Character key, e.g. 'doran'")
    parser.add_argument("--category", default=None, help="Only report this one category (default: all)")
    args = parser.parse_args()

    key = args.npc_key.lower()
    char_path = CHAR_DIR / f"{key}.json"
    if not char_path.exists():
        raise SystemExit(f"No character file for '{key}'.")

    all_chars = {}
    for path in CHAR_DIR.glob("*.json"):
        if path.stem in _SKIP:
            continue
        with open(path, encoding="utf-8") as f:
            all_chars[path.stem] = json.load(f)

    if key not in all_chars:
        raise SystemExit(f"No character file for '{key}'.")

    target_items = all_chars[key].get("knowledge", {}).get("education", {}).get("items", []) or []
    if not target_items:
        raise SystemExit(f"'{key}' has no drawn knowledge.education.items yet - nothing to compare.")
    target_counts = counts_for(target_items)
    target_total = len(target_items)

    others_pct_by_cat: dict = {}
    for other_key, other in all_chars.items():
        if other_key == key:
            continue
        items = other.get("knowledge", {}).get("education", {}).get("items", []) or []
        if not items:
            continue
        counts = counts_for(items)
        total = len(items)
        for cat, n in counts.items():
            others_pct_by_cat.setdefault(cat, []).append(100.0 * n / total)

    categories = [args.category] if args.category else sorted(set(target_counts) | set(others_pct_by_cat))

    print(f"character: {key}  (total items: {target_total})")
    print(f"{'category':<20}{'this char':>12}{'baseline avg':>16}{'baseline range':>18}   flag")
    for cat in categories:
        n = target_counts.get(cat, 0)
        this_pct = 100.0 * n / target_total
        baseline_samples = others_pct_by_cat.get(cat, [])
        if baseline_samples:
            baseline_avg = sum(baseline_samples) / len(baseline_samples)
            baseline_range = f"{min(baseline_samples):.0f}-{max(baseline_samples):.0f}%"
        else:
            baseline_avg = 0.0
            baseline_range = "(no data)"
        flag = "  <-- over-represented" if baseline_samples and this_pct > 1.5 * baseline_avg else ""
        print(f"{cat:<20}{n:>7} ({this_pct:4.1f}%){baseline_avg:>13.1f}%{baseline_range:>18}{flag}")


if __name__ == "__main__":
    main()

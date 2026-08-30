"""
Derivation coverage - instrument (b)-derivation of the Provenance test suite (see TESTING_BRIEF.md,
vault-side `projects/provenance/`). How much of a claim's content traces back to the record vs.
floats free.

Reuses `build_source_index.py`'s own reference-resolution functions directly (`resolve_ref`,
`load_categories`, `build_index`, `build_other_known_ids`) rather than reimplementing resolution
logic - this script never writes `encodings.json`, it only asks the same question that script's
"unresolved" report already answers, then turns it into a per-run, per-category coverage metric:
resolvable references / total, for every hearsay claim's `about` field(s).

Also reports `knowledge.experience` provenance coverage: the fraction of experience entries (across
every character file) that carry a `produced_by` field (see `scripts/lore/update_character.py`/
`generate_offspring.py`/`record_death.py`'s optional `--scene-id`/`--pass-number` flags) - lets
derivation be scored per-generation, not only per-corpus.

Acceptance criterion #3 (TESTING_BRIEF.md §6): this metric should reproduce the documented failure
mode on the pre-2026-08-11 corpus (325/331 unlinked references) - verify against a scratch checkout
of commit `4fe6767` (the last commit with real lore content before it was stripped for this branch;
see the implementation plan's Context section), not against this branch's own (empty) `_lore/`.

Usage:
    py scripts/test/measure_derivation.py [--root <worktree root>] [--json-out report.json]
"""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
LORE_SCRIPTS = ROOT / "scripts" / "lore"
sys.path.insert(0, str(LORE_SCRIPTS))
import build_source_index as bsi  # noqa: E402

_SKIP_CHAR_FILES = {"_template", "lifespans"}


def measure_reference_derivation(root: Path) -> dict:
    encodings_path = root / "_lore" / "encodings.json"
    if not encodings_path.exists():
        return {"total": 0, "resolved": 0, "by_category": {}}
    data = json.loads(encodings_path.read_text(encoding="utf-8"))
    if "_categories" not in data:
        return {"total": 0, "resolved": 0, "by_category": {}}

    categories = bsi.load_categories(data)
    specs = data["_categories"]
    index = bsi.build_index(categories, specs)
    other_known = bsi.build_other_known_ids(data)
    hearsay_ids = {e["id"] for e in data["hearsay"]["entries"]}
    sourced_keys = set(categories.keys())

    grounding_entries, _, _ = bsi.load_grounding()
    if grounding_entries:
        index += bsi.build_index({"grounding": grounding_entries}, specs)
        sourced_keys.add("grounding")

    total = 0
    resolved = 0
    by_category = defaultdict(lambda: {"total": 0, "resolved": 0})
    unresolved = []

    def handle(raw: str, source_label: str, about_category_hint: str):
        nonlocal total, resolved
        if not raw:
            return
        total += 1
        by_category[about_category_hint]["total"] += 1
        status, *_ = bsi.resolve_ref(raw, index, other_known, hearsay_ids, sourced_keys)
        if status == "attach":
            resolved += 1
            by_category[about_category_hint]["resolved"] += 1
        elif status == "unresolved":
            unresolved.append((source_label, raw))
        else:  # out_of_scope - a recognized-but-unsourced reference; don't count against coverage
            total -= 1
            by_category[about_category_hint]["total"] -= 1

    for e in data["hearsay"]["entries"]:
        for i, claim in enumerate(e["claims"], start=1):
            about = claim.get("about")
            values = about if isinstance(about, list) else ([about] if about else [])
            for v in values:
                prefix = v.split(":")[0].strip().lower() if ":" in v else "bare"
                handle(v, f"hearsay:{e['id']}#{i}", prefix)

    return {
        "total": total, "resolved": resolved,
        "coverage": round(resolved / total, 4) if total else None,
        "by_category": {k: {**v, "coverage": round(v["resolved"] / v["total"], 4) if v["total"] else None} for k, v in by_category.items()},
        "unresolved_sample": unresolved[:20],
        "unresolved_count": len(unresolved),
    }


def measure_experience_provenance(root: Path) -> dict:
    char_dir = root / "_lore" / "characters"
    total = 0
    with_provenance = 0
    by_character = {}
    for path in sorted(char_dir.glob("*.json")):
        if path.stem in _SKIP_CHAR_FILES:
            continue
        c = json.loads(path.read_text(encoding="utf-8"))
        entries = c.get("knowledge", {}).get("experience", [])
        if not entries:
            continue
        n = len(entries)
        tagged = sum(1 for e in entries if isinstance(e, dict) and e.get("produced_by"))
        total += n
        with_provenance += tagged
        by_character[path.stem] = {"total": n, "with_provenance": tagged, "coverage": round(tagged / n, 4)}
    return {
        "total": total, "with_provenance": with_provenance,
        "coverage": round(with_provenance / total, 4) if total else None,
        "by_character": by_character,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=ROOT, help="Repo/worktree root to read _lore/ from (default: this repo's own root)")
    parser.add_argument("--json-out", type=Path, default=None)
    args = parser.parse_args()

    ref = measure_reference_derivation(args.root)
    exp = measure_experience_provenance(args.root)
    report = {"reference_derivation": ref, "experience_provenance": exp}

    lines = ["## Derivation coverage", ""]
    if ref["total"]:
        lines.append(f"Hearsay `about` references: {ref['resolved']}/{ref['total']} resolvable ({ref['coverage']:.1%})")
        for cat, v in sorted(ref["by_category"].items()):
            if v["total"]:
                lines.append(f"  - {cat}: {v['resolved']}/{v['total']} ({v['coverage']:.1%})")
        if ref["unresolved_count"]:
            lines.append(f"  Unresolved (sample of {min(20, ref['unresolved_count'])} of {ref['unresolved_count']}):")
            for label, raw in ref["unresolved_sample"]:
                lines.append(f"    - {label}: '{raw}'")
    else:
        lines.append("No hearsay claims with `about` references found (empty corpus, or nothing sampled yet).")
    lines.append("")
    if exp["total"]:
        lines.append(f"knowledge.experience provenance coverage: {exp['with_provenance']}/{exp['total']} entries carry produced_by ({exp['coverage']:.1%})")
    else:
        lines.append("No knowledge.experience entries found.")

    human_readable = "\n".join(lines)
    print(human_readable)

    if args.json_out:
        args.json_out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()

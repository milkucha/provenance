"""
Drift - instrument (b)-drift of the Provenance test suite (see TESTING_BRIEF.md, vault-side
`projects/provenance/`). How far a claim travels across retellings.

Genealogy edge: reuses the existing `derived_from` field on a hearsay claim (format
`<hearsay_entry_id>#<claim_index>`, set by `/enact` Step 7 on a traceable `lineage_coin.py` roll -
see `scripts/lore/record_hearsay.py`'s write-time validation, added alongside this tool) rather than
a new schema field - see the implementation plan's design decision #1 for why.

For every retelling edge (parent claim -> child claim), measures:
- **Lexical distance** - normalized edit distance (`difflib.SequenceMatcher`, already used elsewhere
  in this codebase for exactly this kind of near-match scoring, e.g. `build_source_index.py`'s fuzzy
  matching) and word-bigram Jaccard overlap. Stdlib only - no embeddings by default (see `--semantic`
  below).
- **Reference drift** - did the claim's `about` category (the prefix before `:`, or "bare") change
  from the parent claim's own `about` category.

Aggregates per-lineage (root claim -> every descendant, however many retellings deep) and reports the
overall distance distribution.

`--semantic` is intentionally NOT implemented - stdlib-only/lean-first per TESTING_BRIEF.md §7; a
heavier embeddings-based measure is a deliberately deferred, flagged decision (see the implementation
plan's design decision #6 and TODO.md).

Usage:
    py scripts/test/measure_drift.py [--root <worktree root>] [--semantic] [--json-out report.json]
"""

import argparse
import json
import statistics
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent


def about_category(about) -> str:
    if not about:
        return "none"
    value = about[0] if isinstance(about, list) else about
    return value.split(":", 1)[0].strip().lower() if ":" in value else "bare"


def word_bigrams(text: str) -> set:
    words = text.lower().split()
    return set(zip(words, words[1:])) if len(words) > 1 else set()


def lexical_distance(a: str, b: str) -> dict:
    edit_ratio = SequenceMatcher(None, a, b).ratio()
    bigrams_a, bigrams_b = word_bigrams(a), word_bigrams(b)
    union = bigrams_a | bigrams_b
    jaccard = len(bigrams_a & bigrams_b) / len(union) if union else 1.0
    return {"edit_distance": round(1 - edit_ratio, 4), "bigram_jaccard_distance": round(1 - jaccard, 4)}


def build_claim_index(encodings: dict) -> dict:
    """claim_id ('<entry_id>#<n>') -> {"text", "about", "entry_id"}."""
    index = {}
    for e in encodings["hearsay"]["entries"]:
        for i, claim in enumerate(e["claims"], start=1):
            index[f"{e['id']}#{i}"] = {"text": claim.get("text", ""), "about": claim.get("about"), "derived_from": claim.get("derived_from")}
    return index


def build_edges(claim_index: dict) -> list:
    return [
        {"parent": claim["derived_from"], "child": claim_id}
        for claim_id, claim in claim_index.items()
        if claim.get("derived_from") and claim["derived_from"] in claim_index
    ]


def lineage_depth(root: str, edges_by_parent: dict, cache: dict) -> int:
    if root in cache:
        return cache[root]
    children = edges_by_parent.get(root, [])
    depth = 1 + max((lineage_depth(c, edges_by_parent, cache) for c in children), default=0)
    cache[root] = depth
    return depth


def measure(root: Path, semantic: bool) -> dict:
    if semantic:
        raise NotImplementedError(
            "Semantic drift is deliberately deferred (lean-first per TESTING_BRIEF.md §7) - see the "
            "implementation plan's design decision #6 and TODO.md. Use lexical measures (the default)."
        )

    encodings_path = root / "_lore" / "encodings.json"
    encodings = json.loads(encodings_path.read_text(encoding="utf-8")) if encodings_path.exists() else {"hearsay": {"entries": []}}
    claim_index = build_claim_index(encodings)
    edges = build_edges(claim_index)

    edges_by_parent = {}
    for e in edges:
        edges_by_parent.setdefault(e["parent"], []).append(e["child"])

    roots = sorted({e["parent"] for e in edges} - {e["child"] for e in edges})
    depth_cache = {}
    lineages = [{"root": r, "depth": lineage_depth(r, edges_by_parent, depth_cache)} for r in roots]

    edge_results = []
    for e in edges:
        parent, child = claim_index[e["parent"]], claim_index[e["child"]]
        dist = lexical_distance(parent["text"], child["text"])
        edge_results.append({
            "parent": e["parent"], "child": e["child"],
            **dist,
            "reference_drift": about_category(parent["about"]) != about_category(child["about"]),
            "parent_about_category": about_category(parent["about"]),
            "child_about_category": about_category(child["about"]),
        })

    edit_distances = [r["edit_distance"] for r in edge_results]
    return {
        "edge_count": len(edges),
        "lineage_count": len(lineages),
        "max_depth": max((l["depth"] for l in lineages), default=0),
        "edges": edge_results,
        "lineages": lineages,
        "aggregate": {
            "mean_edit_distance": round(statistics.fmean(edit_distances), 4) if edit_distances else None,
            "median_edit_distance": round(statistics.median(edit_distances), 4) if edit_distances else None,
            "reference_drift_rate": round(sum(1 for r in edge_results if r["reference_drift"]) / len(edge_results), 4) if edge_results else None,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=ROOT, help="Repo/worktree root to read _lore/encodings.json from")
    parser.add_argument("--semantic", action="store_true", help="Not implemented - deliberately deferred, see module docstring")
    parser.add_argument("--json-out", type=Path, default=None)
    args = parser.parse_args()

    report = measure(args.root, args.semantic)

    lines = ["## Drift", ""]
    if report["edge_count"] == 0:
        lines.append("No retelling edges found (no claim's `derived_from` resolves to another claim yet).")
    else:
        lines.append(f"Retelling edges: {report['edge_count']}  |  lineages: {report['lineage_count']}  |  max depth: {report['max_depth']}")
        agg = report["aggregate"]
        lines.append(f"Mean edit distance: {agg['mean_edit_distance']}  |  median: {agg['median_edit_distance']}")
        lines.append(f"Reference-category drift rate: {agg['reference_drift_rate']:.1%}" if agg["reference_drift_rate"] is not None else "")
        lines.append("")
        lines.append("Per-edge detail:")
        for e in report["edges"]:
            ref_note = f" (about drifted: {e['parent_about_category']} -> {e['child_about_category']})" if e["reference_drift"] else ""
            lines.append(f"  - {e['parent']} -> {e['child']}: edit_distance={e['edit_distance']}, bigram_jaccard_distance={e['bigram_jaccard_distance']}{ref_note}")

    human_readable = "\n".join(l for l in lines if l is not None)
    print(human_readable)

    if args.json_out:
        args.json_out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()

"""
Divergence - instrument (b)-divergence of the Provenance test suite (see TESTING_BRIEF.md,
vault-side `projects/provenance/`). Two questions: (i) the same event remembered by different
characters - do their accounts differ consistently with differing criteria (the within-run variant);
(ii) the same world seed grown in multiple runs - how far apart do the resulting worlds drift (the
cross-run variant), including the isolation experiment: a seeded pair's dice are identical, so any
residual difference is the agent layer in isolation.

Takes 1+ run manifest paths. Manifests sharing `world_seed.commit` (see `run_manifest.py` - "same
world seed" = same starting git commit) are compared pairwise:

- **Entity-set overlap** - born/deceased character slugs, Jaccard.
- **Vocabulary overlap** - bag-of-words Jaccard across all hearsay-claim + tale text (lexical, no
  embeddings - see TESTING_BRIEF.md §7).
- **Hearsay-corpus similarity** - mean best lexical match (via `measure_drift.lexical_distance`,
  reused rather than reimplemented) of each claim in one run against its closest counterpart in the
  other - a different lens than bag-of-words overlap: near-duplicate *claims*, not shared vocabulary.
- **Arc-outcome distribution comparison** - proportion differences per outcome, from each run's own
  draw-audit log if present.

A pair sharing both `world_seed.commit` *and* a non-null `rng_seed` is flagged as a **seeded pair**
(the isolation experiment): their draw-audit logs are diffed `result`-by-`result` (should match
exactly - this is acceptance criterion #1) and their non-mechanical divergence is reported as the
agent-layer residual. If a free (unseeded) pair sharing the same commit is also given, the
**freedom-gauge** reading (free-pair divergence minus seeded-pair residual = the dice's own
contribution) is reported too.

The **within-run** variant needs no pairing: for each manifest individually, claims that belong to
the same hearsay entry (the same recorded scene) are compared pairwise via the same lexical-distance
function - a scene with multiple claims on record is exactly "the same event, differently
remembered."

Usage:
    py scripts/test/measure_divergence.py --manifest run_a/.simulate_run_manifest.json run_b/.simulate_run_manifest.json [--json-out report.json]
"""

import argparse
import json
import sys
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from measure_drift import lexical_distance, build_claim_index  # noqa: E402

_SKIP_CHAR_FILES = {"_template", "lifespans"}


def load_run(manifest_path: Path) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    root = manifest_path.parent
    char_dir = root / "_lore" / "characters"
    slugs, deceased = set(), set()
    for path in char_dir.glob("*.json"):
        if path.stem in _SKIP_CHAR_FILES:
            continue
        c = json.loads(path.read_text(encoding="utf-8"))
        slugs.add(path.stem)
        if c.get("life", {}).get("deceased"):
            deceased.add(path.stem)
    born = slugs - set(manifest["world_seed"]["pool"])

    encodings_path = root / "_lore" / "encodings.json"
    encodings = json.loads(encodings_path.read_text(encoding="utf-8")) if encodings_path.exists() else {"hearsay": {"entries": []}, "tales": {"entries": []}}
    claim_texts = [c.get("text", "") for e in encodings["hearsay"]["entries"] for c in e["claims"]]
    tale_texts = [t.get("summary", "") for t in encodings.get("tales", {}).get("entries", [])]

    audit_path = root / ".simulate_draw_audit.jsonl"
    draws = []
    if audit_path.exists():
        draws = [json.loads(line) for line in audit_path.read_text(encoding="utf-8").splitlines() if line.strip()]

    return {
        "manifest_path": str(manifest_path), "manifest": manifest, "root": root,
        "born": born, "deceased": deceased, "claim_texts": claim_texts, "tale_texts": tale_texts,
        "draws": draws, "claim_index": build_claim_index(encodings),
    }


def jaccard(a: set, b: set) -> float:
    union = a | b
    return len(a & b) / len(union) if union else 1.0


def bag_of_words(texts: list) -> set:
    words = set()
    for t in texts:
        words |= set(t.lower().split())
    return words


def hearsay_corpus_similarity(texts_a: list, texts_b: list) -> float:
    if not texts_a or not texts_b:
        return None
    scores = []
    for a in texts_a:
        best = max((1 - lexical_distance(a, b)["edit_distance"] for b in texts_b), default=0.0)
        scores.append(best)
    return round(sum(scores) / len(scores), 4)


def arc_outcome_distribution(draws: list) -> dict:
    counts = {"advance": 0, "stall": 0, "reverse": 0}
    for d in draws:
        if d["script"] == "roll_arc_outcome.py" and d.get("result"):
            outcome = d["result"].get("outcome")
            if outcome in counts:
                counts[outcome] += 1
    total = sum(counts.values())
    return {k: round(v / total, 4) for k, v in counts.items()} if total else {}


def compare_pair(run_a: dict, run_b: dict) -> dict:
    born_j = jaccard(run_a["born"], run_b["born"])
    died_j = jaccard(run_a["deceased"], run_b["deceased"])
    vocab_j = jaccard(bag_of_words(run_a["claim_texts"] + run_a["tale_texts"]), bag_of_words(run_b["claim_texts"] + run_b["tale_texts"]))
    hearsay_sim = hearsay_corpus_similarity(run_a["claim_texts"], run_b["claim_texts"])
    dist_a, dist_b = arc_outcome_distribution(run_a["draws"]), arc_outcome_distribution(run_b["draws"])
    arc_diff = None
    if dist_a and dist_b:
        arc_diff = round(sum(abs(dist_a.get(k, 0) - dist_b.get(k, 0)) for k in ("advance", "stall", "reverse")) / 2, 4)

    same_rng = (
        run_a["manifest"].get("rng_seed") is not None
        and run_a["manifest"].get("rng_seed") == run_b["manifest"].get("rng_seed")
    )
    result = {
        "run_a": run_a["manifest"]["run_id"], "run_b": run_b["manifest"]["run_id"],
        "seeded_pair": same_rng,
        "born_overlap": round(born_j, 4), "deceased_overlap": round(died_j, 4),
        "vocabulary_overlap": round(vocab_j, 4), "hearsay_corpus_similarity": hearsay_sim,
        "arc_outcome_distribution_diff": arc_diff,
        "divergence_score": round(1 - vocab_j, 4),
    }
    if same_rng:
        mismatches = []
        for i, (da, db) in enumerate(zip(run_a["draws"], run_b["draws"])):
            if da.get("result") != db.get("result"):
                mismatches.append({"index": i, "a": da, "b": db})
        result["isolation_check"] = {
            "draws_compared": min(len(run_a["draws"]), len(run_b["draws"])),
            "draw_count_matches": len(run_a["draws"]) == len(run_b["draws"]),
            "mismatches": mismatches[:10],
            "mismatch_count": len(mismatches),
            "mechanically_identical": not mismatches and len(run_a["draws"]) == len(run_b["draws"]),
        }
    return result


def within_run_same_scene(run: dict) -> dict:
    by_entry: dict = {}
    for claim_id, claim in run["claim_index"].items():
        entry_id = claim_id.rsplit("#", 1)[0]
        by_entry.setdefault(entry_id, []).append(claim["text"])
    pair_distances = []
    for entry_id, texts in by_entry.items():
        for a, b in combinations(texts, 2):
            pair_distances.append(lexical_distance(a, b)["edit_distance"])
    return {
        "scenes_with_multiple_claims": sum(1 for texts in by_entry.values() if len(texts) > 1),
        "pairwise_comparisons": len(pair_distances),
        "mean_distance": round(sum(pair_distances) / len(pair_distances), 4) if pair_distances else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--manifest", type=Path, nargs="+", required=True, help="One or more .simulate_run_manifest.json paths")
    parser.add_argument("--json-out", type=Path, default=None)
    args = parser.parse_args()

    runs = [load_run(p) for p in args.manifest]

    by_commit: dict = {}
    for r in runs:
        by_commit.setdefault(r["manifest"]["world_seed"]["commit"], []).append(r)

    pairs = []
    for commit, group in by_commit.items():
        for a, b in combinations(group, 2):
            pairs.append(compare_pair(a, b))

    freedom_gauge = None
    seeded = [p for p in pairs if p["seeded_pair"]]
    free = [p for p in pairs if not p["seeded_pair"]]
    if seeded and free:
        freedom_gauge = round(
            (sum(p["divergence_score"] for p in free) / len(free))
            - (sum(p["divergence_score"] for p in seeded) / len(seeded)), 4
        )

    within_run = {r["manifest"]["run_id"]: within_run_same_scene(r) for r in runs}

    report = {"cross_run_pairs": pairs, "freedom_gauge": freedom_gauge, "within_run_same_scene": within_run}

    lines = ["## Divergence", ""]
    if len(runs) == 1:
        lines.append(f"Only one manifest given ({runs[0]['manifest']['run_id']}) - only the within-run variant applies.")
    for group in by_commit.values():
        if len(group) < 2:
            continue
    if not pairs:
        lines.append("No two manifests share a world_seed.commit - nothing to compare cross-run.")
    for p in pairs:
        lines.append(f"### {p['run_a']} vs {p['run_b']}" + (" [SEEDED PAIR - isolation experiment]" if p["seeded_pair"] else ""))
        lines.append(f"  born overlap: {p['born_overlap']:.1%}  |  deceased overlap: {p['deceased_overlap']:.1%}")
        lines.append(f"  vocabulary overlap: {p['vocabulary_overlap']:.1%}  |  hearsay-corpus similarity: {p['hearsay_corpus_similarity']}")
        if p["arc_outcome_distribution_diff"] is not None:
            lines.append(f"  arc-outcome distribution diff: {p['arc_outcome_distribution_diff']}")
        if p["seeded_pair"]:
            ic = p["isolation_check"]
            verdict = "IDENTICAL (dice confirmed isolated)" if ic["mechanically_identical"] else f"{ic['mismatch_count']} mismatch(es) - NOT mechanically identical"
            lines.append(f"  isolation check: {verdict} ({ic['draws_compared']} draws compared)")
    if freedom_gauge is not None:
        lines.append("")
        lines.append(f"Freedom gauge (free-pair divergence − seeded-pair residual): {freedom_gauge}")
    lines.append("")
    lines.append("### Within-run (same scene, multiple rememberers)")
    for run_id, w in within_run.items():
        if w["pairwise_comparisons"]:
            lines.append(f"  {run_id}: {w['scenes_with_multiple_claims']} scene(s) with >1 claim, mean pairwise distance {w['mean_distance']}")
        else:
            lines.append(f"  {run_id}: no scene has more than one recorded claim yet")

    human_readable = "\n".join(lines)
    print(human_readable)

    if args.json_out:
        args.json_out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()

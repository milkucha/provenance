"""
Machinery conformance report - instrument (a) of the Provenance test suite (see TESTING_BRIEF.md,
vault-side `projects/provenance/`). Reads a run's `.simulate_draw_audit.jsonl` +
`.simulate_run_manifest.json` (both written by `scripts/lore/rng_context.py`/`run_manifest.py`) plus
`_lore/tuning.json` and the current character files, and reports:

1. Observed-vs-expected odds, per fixed-odds stochastic script, with a Wilson score interval (stdlib
   `math` only - no scipy/numpy, per the brief's lean-first constraint) flagging any observed rate
   whose interval excludes the odds actually used.
2. Arc-outcome distribution, bucketed by (inclined, contested) - the only two inputs
   `roll_arc_outcome.py`'s own WEIGHTS table keys off - imported directly from that script rather than
   duplicated here.
3. Invariant checks (deterministic rules that must always hold), pass/fail with detail.
4. A draw-audit summary (counts by script, seeded vs free).

Wired automatically into `/simulate` Step 4 and `/generate` Step 6 - the brief's own "wire into the
run workflow" requirement. Also runnable standalone against any worktree:

Usage:
    py scripts/test/conformance_report.py [--root <worktree root>] [--json-out report.json]
"""

import argparse
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
LORE_SCRIPTS = ROOT / "scripts" / "lore"
sys.path.insert(0, str(LORE_SCRIPTS))
import tuning  # noqa: E402
from roll_arc_outcome import WEIGHTS as ARC_WEIGHTS  # noqa: E402

FIXED_ODDS_CHECKS = {
    # script: (outcome_key, true_value, odds_key_in_result_or_None, tuning path to the fallback odds)
    "roll_contested.py": ("contested", "true", "odds_used", ("odds_percent", "contested")),
    "roll_reproduction.py": ("reproduces", "true", None, ("odds_percent", "reproduction")),
    "roll_lead_followup.py": ("followed", "true", None, ("odds_percent", "lead_followup")),
    "roll_death_legacy.py": ("passes", "true", None, ("odds_percent", "death_legacy")),
}


def _tuning_value(t: dict, path: tuple) -> float:
    node = t
    for p in path:
        node = node[p]
    return float(node)


def wilson_interval(k: int, n: int, z: float = 1.96) -> tuple:
    """95% Wilson score interval for a binomial proportion - stdlib math only, no scipy. Standard
    formula (Wilson 1927); more reliable than a naive normal approximation at small n, which is
    exactly the regime a short test run's draw counts usually fall into."""
    if n == 0:
        return (0.0, 1.0)
    p_hat = k / n
    denom = 1 + z * z / n
    center = p_hat + z * z / (2 * n)
    margin = z * math.sqrt((p_hat * (1 - p_hat) + z * z / (4 * n)) / n)
    return ((center - margin) / denom, (center + margin) / denom)


def load_jsonl(path: Path) -> list:
    if not path.exists():
        return []
    entries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            entries.append(json.loads(line))
    return entries


def load_manifest(path: Path) -> dict | None:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def draw_audit_summary(draws: list) -> dict:
    by_script = defaultdict(lambda: {"total": 0, "seeded": 0, "free": 0})
    for d in draws:
        s = by_script[d["script"]]
        s["total"] += 1
        s["seeded" if d.get("seed_used") is not None else "free"] += 1
    return dict(by_script)


def check_fixed_odds(draws: list, t: dict) -> list:
    results = []
    for script, (outcome_key, true_value, odds_key, tuning_path) in FIXED_ODDS_CHECKS.items():
        entries = [
            d for d in draws
            if d["script"] == script and isinstance(d.get("result"), dict) and outcome_key in d["result"]
        ]
        n = len(entries)
        if n == 0:
            continue
        k = sum(1 for d in entries if d["result"][outcome_key] == true_value)
        observed_rate = k / n
        if odds_key:
            odds_values = [float(d["result"][odds_key]) for d in entries if odds_key in d["result"]]
            expected_rate = (sum(odds_values) / len(odds_values) / 100.0) if odds_values else _tuning_value(t, tuning_path) / 100.0
            expected_note = "mean odds_used across draws (relationship-skewed, so this is the right baseline, not the flat tuning.json default)"
        else:
            expected_rate = _tuning_value(t, tuning_path) / 100.0
            expected_note = "flat tuning.json odds (this script has no per-call skew)"
        lo, hi = wilson_interval(k, n)
        flagged = not (lo <= expected_rate <= hi)
        results.append({
            "script": script, "n": n, "observed_k": k, "observed_rate": round(observed_rate, 4),
            "expected_rate": round(expected_rate, 4), "expected_note": expected_note,
            "wilson_95": (round(lo, 4), round(hi, 4)), "flagged": flagged,
        })
    return results


def check_arc_outcome_distribution(draws: list) -> list:
    buckets = defaultdict(lambda: {"advance": 0, "stall": 0, "reverse": 0})
    for d in draws:
        if d["script"] != "roll_arc_outcome.py" or not d.get("result"):
            continue
        argv = d.get("argv", [])
        inclined = argv[argv.index("--inclined") + 1] if "--inclined" in argv else "unknown"
        contested = "--contested" in argv
        outcome = d["result"].get("outcome")
        if outcome in buckets[(inclined, contested)]:
            buckets[(inclined, contested)][outcome] += 1

    out = []
    for (inclined, contested), counts in buckets.items():
        n = sum(counts.values())
        if n == 0 or inclined not in ARC_WEIGHTS:
            continue
        advance_w, stall_w, reverse_w = ARC_WEIGHTS[inclined]
        if contested:
            shift = min(advance_w, tuning.load()["contested_outcome_shift"])
            advance_w -= shift
            reverse_w += shift
        total_w = advance_w + stall_w + reverse_w
        expected = {k: round(w / total_w, 3) for k, w in zip(("advance", "stall", "reverse"), (advance_w, stall_w, reverse_w))}
        observed = {k: round(v / n, 3) for k, v in counts.items()}
        out.append({"inclined": inclined, "contested": contested, "n": n, "observed": observed, "expected": expected})
    return out


def check_invariants(root: Path) -> list:
    checks = []
    char_dir = root / "_lore" / "characters"
    lifespans_path = char_dir / "lifespans.json"
    lifespans = json.loads(lifespans_path.read_text(encoding="utf-8"))["lifespans"] if lifespans_path.exists() else {}

    # (a) deaths land exactly on rolled span
    detail = []
    for path in sorted(char_dir.glob("*.json")):
        if path.stem in ("_template", "lifespans"):
            continue
        c = json.loads(path.read_text(encoding="utf-8"))
        if c.get("life", {}).get("deceased") and path.stem in lifespans:
            lived = c["life"].get("lived", 0)
            span = lifespans[path.stem].get("span")
            if span is not None and lived != span:
                detail.append(f"{path.stem}: life.lived={lived} != rolled span={span}")
    checks.append({"name": "deaths land exactly on rolled span", "passed": not detail, "detail": detail})

    # (b) no character-name collisions
    names = defaultdict(list)
    for path in sorted(char_dir.glob("*.json")):
        if path.stem in ("_template", "lifespans"):
            continue
        c = json.loads(path.read_text(encoding="utf-8"))
        if c.get("name"):
            names[c["name"].strip().lower()].append(path.stem)
    collisions = [f"{name!r}: {keys}" for name, keys in names.items() if len(keys) > 1]
    checks.append({"name": "no character-name collisions", "passed": not collisions, "detail": collisions})

    # (c) parent/child reproduction exclusion honored
    detail = []
    for path in sorted(char_dir.glob("*.json")):
        if path.stem in ("_template", "lifespans"):
            continue
        c = json.loads(path.read_text(encoding="utf-8"))
        parents = set(c.get("parents", []))
        partners = set(c.get("partners", {}).keys())
        overlap = parents & partners
        if overlap:
            detail.append(f"{path.stem}: parents {overlap} also appear as partners")
    checks.append({"name": "parent/child reproduction exclusion honored", "passed": not detail, "detail": detail})

    # (d) hearsay never upgraded to fact
    facts_path = root / "_lore" / "facts" / "facts.json"
    detail = []
    if facts_path.exists():
        facts = json.loads(facts_path.read_text(encoding="utf-8"))
        blob = json.dumps(facts)
        if "hearsay:" in blob or "derived_from" in blob:
            detail.append("facts.json contains a hearsay-shaped provenance reference - facts must carry none")
    checks.append({"name": "hearsay never upgraded to fact", "passed": not detail, "detail": detail})

    # (e) scene-id uniqueness (best-effort - no next_scene_id.py guard exists on this branch; see
    # TODO.md for that pre-existing gap, out of this brief's scope)
    scenes_dir = root / "_npcs" / "scenes"
    detail = []
    if scenes_dir.exists():
        suffixed = [p.name for p in scenes_dir.glob("*_[0-9].md")]
        if suffixed:
            detail.append(f"{len(suffixed)} scene file(s) carry a numeric collision-recovery suffix (e.g. '_2.md') - a near-miss, not a hard failure: {suffixed}")
    checks.append({"name": "scene-id uniqueness (best-effort - no next_scene_id.py guard exists yet)", "passed": not detail, "detail": detail})

    return checks


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=ROOT, help="Worktree root to read the run's files from (default: this repo's own root)")
    parser.add_argument("--json-out", type=Path, default=None, help="Also write the full machine-readable report here")
    args = parser.parse_args()

    draws = load_jsonl(args.root / ".simulate_draw_audit.jsonl")
    manifest = load_manifest(args.root / ".simulate_run_manifest.json")
    t = tuning.load()

    report = {
        "run_id": manifest["run_id"] if manifest else None,
        "draw_audit_summary": draw_audit_summary(draws),
        "fixed_odds": check_fixed_odds(draws, t),
        "arc_outcome_distribution": check_arc_outcome_distribution(draws),
        "invariants": check_invariants(args.root),
    }

    lines = ["## Machinery conformance report", ""]
    lines.append(f"Run: {report['run_id'] or '(no manifest found)'}")
    lines.append(f"Total stochastic draws logged: {sum(s['total'] for s in report['draw_audit_summary'].values())}")
    lines.append("")
    lines.append("### Observed vs. expected odds")
    if not report["fixed_odds"]:
        lines.append("(no fixed-odds draws logged this run)")
    for r in report["fixed_odds"]:
        flag = " **FLAGGED**" if r["flagged"] else ""
        lines.append(
            f"- `{r['script']}`: {r['observed_k']}/{r['n']} = {r['observed_rate']:.1%} observed, "
            f"expected {r['expected_rate']:.1%} ({r['expected_note']}), "
            f"95% CI [{r['wilson_95'][0]:.1%}, {r['wilson_95'][1]:.1%}]{flag}"
        )
    lines.append("")
    lines.append("### Arc-outcome distribution (by inclined x contested)")
    if not report["arc_outcome_distribution"]:
        lines.append("(no arc-outcome draws logged this run)")
    for r in report["arc_outcome_distribution"]:
        lines.append(f"- inclined={r['inclined']} contested={r['contested']} (n={r['n']}): observed {r['observed']}, expected {r['expected']}")
    lines.append("")
    lines.append("### Invariant checks")
    for c in report["invariants"]:
        status = "PASS" if c["passed"] else "FAIL"
        lines.append(f"- [{status}] {c['name']}")
        for d in c["detail"]:
            lines.append(f"    - {d}")

    human_readable = "\n".join(lines)
    print(human_readable)

    if args.json_out:
        args.json_out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()

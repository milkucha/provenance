"""
Run manifest - the machine-readable record of a /simulate or /generate run's exact starting state,
so "same world seed" and "same run" are well-defined, comparable objects for the trace-measure
tooling in scripts/test/ (see TESTING_BRIEF.md, vault-side `projects/provenance/`).

World seed = the git commit a run's worktree branches from. `simulate_setup_worktree.py` always
branches from `HEAD`, and `/simulate`'s own Step 0 already refuses to proceed with uncommitted
`_lore/` changes - so the starting commit hash is already a well-defined, comparable "same world
seed" object; no separate content-hashing scheme is needed. Two runs share a world seed iff this
commit matches. The pool and a `_lore/tuning.json` snapshot are recorded alongside it for human
readability, not as part of the identity check itself.

Written once at run start (`write()`), updated once at run end (`finalize()`). Lives at the worktree
root, alongside the existing `.simulate_snapshot.json`.

Usage (CLI - for a skill-orchestrated shell context, e.g. /simulate's SKILL.md):
    py scripts/lore/run_manifest.py write --pool khaoe farlis --passes 50 [--seed 7] [--mode simple]
    py scripts/lore/run_manifest.py finalize --passes-run 47 [--simulation-log SIMULATION_LOG.md] ...

Usage (library - for an in-process driver, e.g. simulate_generate_population.py):
    import run_manifest
    run_manifest.write(root, mode="simple", rng_seed=None, pool=[...], passes=50)
    ...
    run_manifest.finalize(root, outputs={...}, passes_actually_run=47)
"""

import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
MANIFEST_FILENAME = ".simulate_run_manifest.json"


def _manifest_path(root: Path) -> Path:
    return root / MANIFEST_FILENAME


def _git_commit(root: Path) -> str:
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"git rev-parse HEAD failed in {root}:\n{result.stderr}")
    return result.stdout.strip()


def _tuning_snapshot(root: Path) -> str:
    tuning_path = root / "_lore" / "tuning.json"
    if not tuning_path.exists():
        return ""
    return hashlib.sha256(tuning_path.read_bytes()).hexdigest()[:16]


def write(root: Path, mode: str, rng_seed, pool: list, passes: int) -> dict:
    manifest = {
        "run_id": root.name,
        "world_seed": {
            "commit": _git_commit(root),
            "pool": list(pool),
            "tuning_snapshot": _tuning_snapshot(root),
        },
        "rng_seed": rng_seed,
        "mode": mode,
        "passes_planned": passes,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "tastings": [],
    }
    with open(_manifest_path(root), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    return manifest


def finalize(root: Path, outputs: dict, passes_actually_run: int) -> dict:
    path = _manifest_path(root)
    if not path.exists():
        raise SystemExit(f"No run manifest at {path} - run `write` first.")
    with open(path, encoding="utf-8") as f:
        manifest = json.load(f)
    manifest["ended_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    manifest["passes_actually_run"] = passes_actually_run
    manifest["outputs"] = outputs
    with open(path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p_write = sub.add_parser("write")
    p_write.add_argument("--pool", nargs="+", required=True)
    p_write.add_argument("--passes", type=int, required=True)
    p_write.add_argument("--seed", type=int, default=None, help="RNG seed - if given, this is a seeded run (the isolation experiment); omit for a free/unseeded run (default, today's exact behavior)")
    p_write.add_argument("--mode", choices=["simple", "divergence"], default="simple")
    p_write.add_argument("--root", type=Path, default=ROOT)

    p_finalize = sub.add_parser("finalize")
    p_finalize.add_argument("--simulation-log", default=None)
    p_finalize.add_argument("--tally-report", default=None)
    p_finalize.add_argument("--draw-audit-log", default=None)
    p_finalize.add_argument("--passes-run", type=int, required=True)
    p_finalize.add_argument("--root", type=Path, default=ROOT)

    args = parser.parse_args()

    if args.command == "write":
        manifest = write(args.root, args.mode, args.seed, [s.lower() for s in args.pool], args.passes)
        if args.seed is not None:
            sys.path.insert(0, str(Path(__file__).resolve().parent))
            import rng_context
            rng_context.start_seeded_run(args.root, args.seed)
        print(f"run_id: {manifest['run_id']}")
        print(f"world_seed.commit: {manifest['world_seed']['commit']}")
        print(f"rng_seed: {manifest['rng_seed']}")
        print(f"mode: {manifest['mode']}")
        print(f"manifest: {_manifest_path(args.root)}")
    else:
        outputs = {
            "simulation_log": args.simulation_log,
            "tally_report": args.tally_report,
            "draw_audit_log": args.draw_audit_log,
        }
        manifest = finalize(args.root, outputs, args.passes_run)
        print(f"finalized: {_manifest_path(args.root)}")
        print(f"passes_actually_run: {manifest['passes_actually_run']}")


if __name__ == "__main__":
    main()

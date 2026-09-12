"""
Shared RNG-seeding and draw-audit plumbing for a `/simulate`/`/generate` run - built for the
Provenance test suite (see TESTING_BRIEF.md, vault-side `projects/provenance/`). Not a standalone
script - import from a sibling driver (`simulate_pass_lib.py`, `simulate_generate_population.py`) or
from a per-pass CLI driver (`simulate_pass_brief.py`, `simulate_resolve_pair.py`,
`simulate_pass_reproduction.py`).

**Off by default.** A run is "free" (today's exact behavior, byte-for-byte) unless a run-state file
exists at the worktree root - `next_seed()` returns `None` the instant that file is absent, and every
caller already falls back to "don't pass --seed" / "use a fresh unseeded Random()" in that case. Only
the isolation experiment (a seeded pair of runs) ever creates that file.

Two files live at the worktree root, alongside the existing `.simulate_snapshot.json`:

- `.simulate_rng_state.json` - mutable: `{"rng_seed": int, "draw_counter": int}`. Present only for a
  seeded run. `next_seed()` reads it, derives this draw's local seed, increments the counter, and
  writes it straight back - safe because orchestration here is always sequential (one pass's process
  exits before the next one starts; `/generate`'s own loop is single-process, single-threaded), never
  concurrent.
- `.simulate_draw_audit.jsonl` - append-only, one JSON object per line, written by every call to
  `next_seed()` regardless of whether seeding is active - this is the "no model guessing" proof, not
  just a seeding side-effect. See `next_seed()`'s docstring for the line shape.

Usage (from a sibling script in this same directory):
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import rng_context

    seed = rng_context.next_seed("pick_pair.py", root=ROOT, result={"participant_1": a, "participant_2": b})
"""

import hashlib
import json
import time
from pathlib import Path
from random import Random

RNG_STATE_FILENAME = ".simulate_rng_state.json"
DRAW_AUDIT_FILENAME = ".simulate_draw_audit.jsonl"

# Every scripts/lore/*.py filename that accepts --seed and performs a genuine stochastic draw -
# simulate_pass_lib.call() consults this to decide whether to auto-inject --seed. Kept here (not in
# simulate_pass_lib.py) so any other caller (a per-pass CLI driver invoking a script directly) can
# check the same registry without importing the full pass-orchestration library.
STOCHASTIC_SCRIPTS = {
    "pick_pair.py", "roll_routine.py", "roll_home_visit.py", "roll_survival.py",
    "roll_arc_primacy.py", "roll_contested.py", "roll_arc_outcome.py", "roll_lead_followup.py",
    "roll_reproduction.py", "roll_death_legacy.py", "lineage_coin.py", "roll_lifespan.py",
    "generate_offspring.py", "notify_death.py", "record_death.py", "sample_lore_knowledge.py",
}

_current_pass: int | None = None


def set_current_pass(pass_number: int | None) -> None:
    """Process-local pass-number context, so audit-log entries carry a best-effort pass number
    without threading a new parameter through every simulate_pass_lib wrapper function. Call once,
    near the top of any driver that already parses its own --pass-number."""
    global _current_pass
    _current_pass = pass_number


def current_pass() -> int | None:
    return _current_pass


def derive_seed(run_seed: int, draw_index: int) -> int:
    """Deterministic, stable across processes/machines/Python versions - NOT Python's own randomized
    hash(), which varies per-interpreter-invocation (PYTHONHASHSEED) and would break reproducibility
    the instant a seeded pass ran in a fresh process, which is the normal case here."""
    digest = hashlib.sha256(f"{run_seed}:{draw_index}".encode("utf-8")).hexdigest()
    return int(digest[:16], 16)


def _state_path(root: Path) -> Path:
    return root / RNG_STATE_FILENAME


def _audit_path(root: Path) -> Path:
    return root / DRAW_AUDIT_FILENAME


def _append_audit(root: Path, entry: dict) -> None:
    with open(_audit_path(root), "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def reserve_seed(root: Path) -> tuple:
    """Reads+increments the run-state file if one exists. Returns (seed, draw_index) - both `None`
    if this run isn't seeded. Split from the audit-log write (see `log_draw()`) because a subprocess
    caller (simulate_pass_lib.call()) needs the seed BEFORE invoking the script, but only knows the
    draw's result AFTER - one audit-log line should cover both, not two half-written ones."""
    state_path = _state_path(root)
    if not state_path.exists():
        return None, None
    with open(state_path, encoding="utf-8") as f:
        state = json.load(f)
    draw_index = state["draw_counter"]
    seed = derive_seed(state["rng_seed"], draw_index)
    state["draw_counter"] = draw_index + 1
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
    return seed, draw_index


def log_draw(root: Path, script_or_context: str, argv: list | None, result, seed: int | None, draw_index: int | None = None) -> None:
    """Appends one line to `.simulate_draw_audit.jsonl` - written for EVERY stochastic decision,
    seeded or not, since the audit log is the "every random decision came from a genuine mechanical
    draw, never a model guess" proof, and that claim needs proving on ordinary free runs too."""
    _append_audit(root, {
        "draw_index": draw_index,
        "script": script_or_context,
        "argv": argv or [],
        "result": result,
        "pass_number": current_pass(),
        "seed_used": seed,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
    })


def next_seed(script_or_context: str, root: Path, argv: list | None = None, result=None) -> int | None:
    """Convenience wrapper for the single-call case (seed and result both available/known at the
    same call site - e.g. an in-process draw via local_random()). Returns the local seed to use, or
    `None` if this run isn't seeded (today's exact unseeded behavior, unchanged)."""
    seed, draw_index = reserve_seed(root)
    log_draw(root, script_or_context, argv, result, seed, draw_index)
    return seed


def local_random(context_label: str, root: Path) -> Random:
    """For a stochastic decision that never leaves the process (no subprocess involved) - e.g.
    simulate_pass_lib.py's own peer_knowledge_items(). Same seeding/audit-log treatment as
    next_seed(), but hands back a ready-to-use Random instance instead of a bare seed int."""
    seed = next_seed(context_label, root)
    return Random(seed)


def start_seeded_run(root: Path, rng_seed: int) -> None:
    """Creates .simulate_rng_state.json - called once, at run start, only for a seeded run (the
    isolation experiment). Never called for an ordinary free run; the run-state file's mere absence
    is what keeps every other function in this module a no-op-equivalent to today's behavior."""
    with open(_state_path(root), "w", encoding="utf-8") as f:
        json.dump({"rng_seed": rng_seed, "draw_counter": 0}, f, indent=2)

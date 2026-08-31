"""
Driver script for /simulate's unattended batch mode - the last, largest mechanical block: /enact
Step 8 points 3-8 and Step 10's experience/grounded-experience writes, for both participants in one
call. See pass_prep.py's docstring for why this collapsing matters and the "simulate-token-efficiency"
memory this driver-script trio follows.

Every judgment call (criterion move, cost ledger, what to write as experience, synthesis text) is
still entirely the model's, decided BEFORE calling this script, from pass_record.py's own output
(anchor-reference and resonance results). This script only sequences the already-decided writes and
the parts of the mechanism that are pure arithmetic/roll with no judgment left in them at all:

  - one update_character.py call per participant (lived-delta + experience + cost-ledger +
    criterion-move, whichever apply - exactly what that script already supports combined)
  - one update_character.py --add-grounded-experience call per grounded entry (repeatable per
    participant - the underlying script takes only one per call)
  - one update_character.py --add-synthesis call per synthesis entry (same reason)
  - the SECOND, energy-based death check (/enact Step 8 point 6b) - read directly from
    .simulate_pass_brief.json's own survival.<slug>.died, never from the input JSON, so this can't
    drift from what simulate_pass_brief.py actually rolled
  - horizon.py again, post-lived-delta (Step 8 point 6) - and record_death.py if `ending` now reads
    true and the energy check hasn't already recorded this character's death this pass
  - reproduction (simulate_pass_reproduction.py, Step 8 point 8) - always run, regardless of whether
    either death check fired
  - death-legacy (roll_death_legacy.py then, on a true roll, apply_death_legacy.py, Step 8 point 7) -
    only attempted for a participant who died this pass with band "established" (not "late") and a
    non-empty notified circle; the roll itself picks the recipient mechanically, so both calls chain
    automatically with no judgment slot left open

Genuinely NOT handled here, because they need a judgment call this script cannot make: composing a
newly-eligible child's name (simulate_pass_reproduction.py reports reproduces:true and stops there -
run generate_offspring.py directly once the model composes the name) and resolving any notified
character's shock-candidate criterion move (record_death.py's own output flags who qualifies - resolve
each with an ordinary update_character.py --criterion-move call, same as any other shock, since deaths
and their notified circles are rare enough that wrapping this too would cost more to build than it
would ever save).

Input: --json-file pointing at a decisions payload:
{
  "participants": {
    "<slug>": {
      "lived_delta": 1,
      "experience": ["...", ...],
      "cost_ledger": ["...", ...],
      "criterion_move": {"move": "reject|reinterpret|break", "dialog": "...", "cause": "...",
                          "note": "...", "trusts": "...", "distrusts": "..."} | null,
      "grounded_experience": [{"about": "..." or ["...", ...], "text": "..."}],
      "synthesis": [{"about": ["A", "B"], "text": "..."}],
      "death_cause": "<text>" | null   # only used if the scene established one AND this character's
                                        # life turns out to have ended this pass (horizon, not energy -
                                        # the energy vector already has its own fixed cause)
    }
  }
}
Every key under a participant is optional except lived_delta (send 0 explicitly if truly nothing -
normally 1, once per scene, same as /enact Step 8 point 5 always requires).

Prints one combined JSON block: per participant {deceased, cause, band_after, ending, notified_circle,
shock_candidates}, plus reproduction's own result, plus any death-legacy application.

Usage:
    py scripts/lore/pass_apply.py --json-file decisions.json --p1 khaoe --p2 farlis --pass-number 12
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT = SCRIPTS_DIR.parent.parent
CHAR_DIR = ROOT / "_lore" / "characters"
BRIEF_PATH = ROOT / ".simulate_pass_brief.json"

sys.path.insert(0, str(SCRIPTS_DIR))
import rng_context  # noqa: E402


def _kv(stdout: str) -> dict:
    """Parses top-level 'key: value' lines into a dict - same convention
    simulate_pass_lib.kv() uses, duplicated here (not imported) for the same reason
    roll_survival.py's own _tally() duplicates rather than pulling in the full lib."""
    out = {}
    for line in stdout.splitlines():
        if not line or line[0] in " \t":
            continue
        key, sep, value = line.partition(":")
        if sep:
            out[key.strip()] = value.strip()
    return out


def run(args: list, allow_fail: bool = False) -> tuple:
    """This driver calls a couple of genuinely stochastic siblings directly (record_death.py's
    circle sample, roll_death_legacy.py's roll) rather than through simulate_pass_lib.call() - so,
    same discipline as that function, auto-inject --seed and log the draw whenever this run is
    seeded (rng_context.STOCHASTIC_SCRIPTS is the single shared registry both places read)."""
    script_name = Path(args[0]).name
    argv = args[1:]
    stochastic = script_name in rng_context.STOCHASTIC_SCRIPTS and "--seed" not in argv
    seed = draw_index = None
    if stochastic:
        seed, draw_index = rng_context.reserve_seed(ROOT)
        if seed is not None:
            argv = [*argv, "--seed", str(seed)]

    result = subprocess.run([sys.executable, args[0], *argv], capture_output=True, text=True)
    if stochastic:
        # conformance_report.py's check_fixed_odds() indexes result[outcome_key] as a dict (it
        # has roll_death_legacy.py registered) - a raw stdout string used to be logged here
        # instead, which crashed that check the first time a real run reached it (TypeError:
        # string indices must be integers). Parse to a dict, same shape simulate_pass_lib.call()
        # already logs for every OTHER stochastic script in the pipeline.
        rng_context.log_draw(ROOT, script_name, argv, _kv(result.stdout) or None, seed, draw_index)
    if result.returncode != 0 and not allow_fail:
        raise SystemExit(f"{' '.join(args)} failed (exit {result.returncode}):\n{result.stderr}")
    return result.returncode, result.stdout, result.stderr


def parse_horizon(output: str) -> dict:
    fields = {}
    for line in output.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fields[k.strip()] = v.strip()
    return {"band": fields.get("band"), "lived": int(fields.get("lived", 0)), "ending": fields.get("ending") == "true"}


def is_deceased(slug: str) -> bool:
    with open(CHAR_DIR / f"{slug}.json", encoding="utf-8") as f:
        return json.load(f).get("life", {}).get("deceased", False)


def parse_record_death(output: str) -> dict:
    notified, shock = [], []
    for line in output.splitlines():
        line = line.strip()
        if line.startswith("notified:"):
            key = line.split("notified:", 1)[1].strip().split()[0]
            notified.append(key)
            if "SHOCK CANDIDATE" in line:
                shock.append(key)
    return {"notified_circle": notified, "shock_candidates": shock}


def apply_participant(slug: str, decisions: dict, scene_id: str | None, pass_number: int) -> dict:
    provenance = ["--scene-id", scene_id, "--pass-number", str(pass_number)] if scene_id else []

    cmd = [str(SCRIPTS_DIR / "update_character.py"), slug, "--lived-delta", str(decisions.get("lived_delta", 0))]
    for entry in decisions.get("experience", []):
        cmd += ["--add-experience", entry]
    for entry in decisions.get("cost_ledger", []):
        cmd += ["--cost-ledger", entry]
    move = decisions.get("criterion_move")
    if move:
        cmd += ["--criterion-move", move["move"], "--dialog", move["dialog"], "--cause", move["cause"]]
        if move.get("note"):
            cmd += ["--note", move["note"]]
        if move.get("trusts"):
            cmd += ["--trusts", move["trusts"]]
        if move.get("distrusts"):
            cmd += ["--distrusts", move["distrusts"]]
    run(cmd + provenance)

    for g in decisions.get("grounded_experience", []):
        gcmd = [str(SCRIPTS_DIR / "update_character.py"), slug, "--add-grounded-experience"]
        about = g["about"] if isinstance(g["about"], list) else [g["about"]]
        for a in about:
            gcmd += ["--about", a]
        gcmd += ["--text", g["text"]]
        run(gcmd + provenance)

    for s in decisions.get("synthesis", []):
        scmd = [
            str(SCRIPTS_DIR / "update_character.py"), slug, "--add-synthesis",
            "--about", s["about"][0], "--about", s["about"][1], "--text", s["text"],
        ] + provenance
        run(scmd)

    result = {"deceased": False, "cause": None, "notified_circle": [], "shock_candidates": []}

    brief = json.loads(BRIEF_PATH.read_text(encoding="utf-8")) if BRIEF_PATH.exists() else {}
    energy_died = brief.get("survival", {}).get(slug, {}).get("died", False)
    if energy_died and not is_deceased(slug):
        _, out, _ = run([str(SCRIPTS_DIR / "record_death.py"), slug, "--cause", "exhaustion/starvation - energy depleted"])
        result.update({"deceased": True, "cause": "energy"})
        result.update(parse_record_death(out))

    horizon_after = parse_horizon(run([str(SCRIPTS_DIR / "horizon.py"), slug])[1])
    result["band_after"] = horizon_after["band"]
    result["ending"] = horizon_after["ending"]

    if horizon_after["ending"] and not is_deceased(slug):
        cause = decisions.get("death_cause")
        cmd = [str(SCRIPTS_DIR / "record_death.py"), slug]
        if cause:
            cmd += ["--cause", cause]
        _, out, _ = run(cmd)
        result.update({"deceased": True, "cause": cause or "unspecified"})
        result.update(parse_record_death(out))

    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--json-file", required=True)
    parser.add_argument("--p1", required=True)
    parser.add_argument("--p2", required=True)
    parser.add_argument("--pass-number", type=int, required=True)
    parser.add_argument("--scene-id", default=None, help="This pass's scene id (pass_record.py's hearsay_id) - threaded into update_character.py's --scene-id/--pass-number so knowledge.experience entries carry produced_by (measure_derivation.py's provenance-coverage instrument reads this). Optional; omitting it reproduces today's exact untagged output.")
    args = parser.parse_args()

    p1, p2 = args.p1.lower(), args.p2.lower()
    payload = json.loads(Path(args.json_file).read_text(encoding="utf-8"))
    participants = payload.get("participants", {})

    report = {"participants": {}}
    for slug in (p1, p2):
        report["participants"][slug] = apply_participant(
            slug, participants.get(slug, {"lived_delta": 1}), args.scene_id, args.pass_number,
        )

    _, repro_out, _ = run([
        str(SCRIPTS_DIR / "simulate_pass_reproduction.py"),
        "--p1", p1, "--p2", p2, "--pass-number", str(args.pass_number),
    ])
    report["reproduction_raw"] = repro_out

    report["death_legacy"] = []
    for slug in (p1, p2):
        r = report["participants"][slug]
        if r["deceased"] and r["band_after"] == "established" and r["notified_circle"]:
            code, roll_out, _ = run(
                [str(SCRIPTS_DIR / "roll_death_legacy.py"), "--candidates", *r["notified_circle"]],
            )
            if "passes: true" in roll_out:
                recipient = next(l.split(":", 1)[1].strip() for l in roll_out.splitlines() if l.startswith("recipient:"))
                _, apply_out, _ = run([
                    str(SCRIPTS_DIR / "apply_death_legacy.py"), "--deceased", slug, "--recipient", recipient,
                ])
                report["death_legacy"].append({"deceased": slug, "recipient": recipient, "applied": True})
            else:
                report["death_legacy"].append({"deceased": slug, "applied": False})

    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

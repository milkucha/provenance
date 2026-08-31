"""
Batch driver for an unattended /simulate run using the Local (Ollama) enacter path - built
2026-08-31, on a token-cost audit of a real run: dispatching each pass as a chain of ~5 separate
Bash round-trips (resolve pair, prep, enact, record, apply) meant every pass re-paid that session's
entire growing context from scratch, the same "simulate-token-efficiency" problem the pass_prep.py/
pass_record.py/pass_apply.py driver trio already solved one level down. This collapses the whole
happy-path pass (resolve pair -> prep -> local-model enact -> record -> apply -> pool/log update)
into one call, and STOPS the batch the instant a judgment slot appears (arc re-authoring or a
reproduction), leaving enough state on disk to resume after the orchestrating session supplies the
content. Confirmed cutting the cost enough that a run using this driver covered 250 passes inside a
budget that previously capped runs around 40.

State files (all at worktree root, alongside the existing .simulate_snapshot.json /
.simulate_run_manifest.json / .simulate_rng_state.json):
  .simulate_driver_state.json  - {"pool": [...], "pending_children": [{"slug","unlock_pass"}],
                                   "next_pass": int, "deaths": [...], "births": [...]}
  .simulate_running_log.txt    - one line per completed pass, append-only

Usage:
    py scripts/lore/simulate_driver.py run --end 1000 [--limit 25]
        Runs passes from state's next_pass up to min(end, next_pass+limit-1). Stops early on:
        arc_authoring_needed, a reproduction, pool < 2 living participants, or a script failure.
        Prints one JSON status block.

    py scripts/lore/simulate_driver.py resolve-arc --arc-json <path>
        Call after composing arc content for a pass that stopped with status "needs_arc". Writes the
        arc (write_arc.py) and updates driver state so the NEXT `run` call continues that same pass
        (uses the already-cached .simulate_pass_brief.json rather than re-running pass_prep, since
        pass_prep already applied that pass's survival mutation and must not run twice for one pass).
        Compose `needs` from `arc_authoring_needed.needs_candidates`' ranked options for the chosen
        context, not free-typed - write_arc.py hard-rejects anything outside that context's own
        _lore/contexts.json provides vocabulary.

    py scripts/lore/simulate_driver.py resolve-birth --child-name <name>
        Call after composing a child's name for a pass that stopped with status "needs_name". Runs
        generate_offspring.py, registers the child's future pool-entry date, and clears the pending
        birth so the NEXT `run` call continues.

Before first use each run: the caller (the orchestrating session) is responsible for run_manifest.py
write, simulate_tally.py snapshot, and reset_reproduction_cooldown.py --pool <...> per /simulate
SKILL.md's own Step 3 setup, and for writing .simulate_driver_state.json with the initial living pool
and next_pass: 1 before the first `run` call - this script does not do any of that itself. Both
judgment slots (arc content, child names) are deliberately never scripted - same discipline
write_arc.py/generate_offspring.py themselves already follow; this driver only collapses the
MECHANICAL steps around those judgment calls, never the calls themselves.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent.parent
sys.path.insert(0, str(SCRIPTS))
import rng_context  # noqa: E402
STATE_PATH = ROOT / ".simulate_driver_state.json"
LOG_PATH = ROOT / ".simulate_running_log.txt"
BRIEF_PATH = ROOT / ".simulate_pass_brief.json"
PENDING_PATH = ROOT / ".simulate_pending.json"  # {"kind": "arc"|"birth", "pass": N, "p1":..,"p2":..,"forced_visit":bool, ...}


def _kv(stdout):
    out = {}
    for line in stdout.splitlines():
        if not line or line[0] in " \t":
            continue
        key, sep, value = line.partition(":")
        if sep:
            out[key.strip()] = value.strip()
    return out


def run(args, allow_fail=False):
    """Same auto-seed-injection discipline as pass_apply.py's own run() - any script this driver
    calls directly (not through another driver script that already does this) gets --seed injected
    and logged when it's in rng_context.STOCHASTIC_SCRIPTS and this is a seeded run."""
    args = [str(a) for a in args]
    script_name = Path(args[0]).name
    argv = args[1:]
    stochastic = script_name in rng_context.STOCHASTIC_SCRIPTS and "--seed" not in argv
    seed = draw_index = None
    if stochastic:
        seed, draw_index = rng_context.reserve_seed(ROOT)
        if seed is not None:
            argv = [*argv, "--seed", str(seed)]
    r = subprocess.run([sys.executable, args[0], *argv], capture_output=True, text=True, cwd=ROOT)
    if stochastic:
        rng_context.log_draw(ROOT, script_name, argv, _kv(r.stdout) or None, seed, draw_index)
    if r.returncode != 0 and not allow_fail:
        raise SystemExit(f"FAILED: {' '.join(args)}\nSTDOUT:\n{r.stdout}\nSTDERR:\n{r.stderr}")
    return r.returncode, r.stdout, r.stderr


def load_state():
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def save_state(s):
    STATE_PATH.write_text(json.dumps(s, indent=2, ensure_ascii=False), encoding="utf-8")


def append_log(line):
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def maybe_admit_children(state, pass_number):
    still_pending = []
    for c in state.get("pending_children", []):
        if pass_number >= c["unlock_pass"]:
            if c["slug"] not in state["pool"]:
                state["pool"].append(c["slug"])
            append_log(f"pass {pass_number}: {c['slug']} admitted to living pool (cooldown cleared)")
        else:
            still_pending.append(c)
    state["pending_children"] = still_pending


def name_from_slug_map(slugs):
    """slug -> display name, from each character file's own 'name' field."""
    out = {}
    for s in slugs:
        f = ROOT / "_lore" / "characters" / f"{s}.json"
        if f.exists():
            out[s] = json.loads(f.read_text(encoding="utf-8")).get("name", s)
    return out


def parse_horizon_text(output):
    fields = {}
    for line in output.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fields[k.strip()] = v.strip()
    return {"band": fields.get("band"), "lived": int(fields.get("lived", 0)), "ending": fields.get("ending") == "true"}


def horizon_pre_block(p1, p2):
    _, o1, _ = run([SCRIPTS / "horizon.py", p1])
    _, o2, _ = run([SCRIPTS / "horizon.py", p2])
    return {p1: parse_horizon_text(o1), p2: parse_horizon_text(o2)}


def characters_block(p1, p2, context):
    """Mirrors pass_prep.py's load_character_brief() - re-read directly here so a resumed pass
    (after write_arc.py just ran) picks up the freshly-authored arc's own premise, same as a fresh
    pass_prep.py call would if it ran after the write instead of before."""
    out = {}
    for slug in (p1, p2):
        f = ROOT / "_lore" / "characters" / f"{slug}.json"
        if not f.exists():
            out[slug] = {}
            continue
        char = json.loads(f.read_text(encoding="utf-8"))
        criterion = char.get("criterion") or {}
        entry = {"criterion": {
            "standard": criterion.get("standard"), "wasted_life": criterion.get("wasted_life"),
            "trusts": criterion.get("trusts"), "distrusts": criterion.get("distrusts"),
            "anchor": criterion.get("anchor"),
        }}
        routine = next((r for r in char.get("routines", []) if r.get("context") == context), None)
        if routine:
            entry["routine"] = {"location": routine.get("location"), "routine_actions": routine.get("routine_actions")}
        arc = char.get("arc")
        if arc and arc.get("resolution") == "ongoing":
            entry["arc_premise"] = {"about": arc.get("about"), "needs": arc.get("needs"), "premise": arc.get("premise")}
        out[slug] = entry
    return out


def do_one_pass(state, pass_number):
    """Runs one pass through to completion (no pending judgment call). Returns a dict describing
    what happened, or raises SystemExit on script failure."""
    pending = json.loads(PENDING_PATH.read_text(encoding="utf-8")) if PENDING_PATH.exists() else None

    if pending and pending["pass"] == pass_number and pending["kind"] == "resume":
        p1, p2, forced_visit = pending["p1"], pending["p2"], pending["forced_visit"]
        raw_brief = json.loads(BRIEF_PATH.read_text(encoding="utf-8"))
        # The arc that triggered this resume is already written (write_arc.py just ran) - strip the
        # now-stale arc_authoring_needed block before handing this to the enacter. Found 2026-09-01:
        # left in place, it still carries the OLD arc's completion_tale_id (e.g. "arc_complete_x"),
        # and the local model reliably latches onto that as a fake `about` tag for its own claims,
        # since it reads as just another id-shaped string sitting in the brief.
        raw_brief.pop("arc_authoring_needed", None)
        brief = {
            "horizon_pre": horizon_pre_block(p1, p2),
            "brief": raw_brief,
            "characters": characters_block(p1, p2, raw_brief.get("context")),
        }
        PENDING_PATH.unlink()
    else:
        _, out, _ = run([SCRIPTS / "simulate_resolve_pair.py", "--pool", *state["pool"], "--pass-number", pass_number])
        resolved = json.loads(out.strip().splitlines()[-1])
        p1, p2, forced_visit = resolved["participant_1"], resolved["participant_2"], resolved["forced_visit"]

        prep_args = [SCRIPTS / "pass_prep.py", "--p1", p1, "--p2", p2, "--pass-number", pass_number]
        if forced_visit:
            prep_args.append("--forced-visit")
        _, out, _ = run(prep_args)
        brief = json.loads(out)

        if brief["brief"].get("arc_authoring_needed"):
            PENDING_PATH.write_text(json.dumps({
                "kind": "arc", "pass": pass_number, "p1": p1, "p2": p2, "forced_visit": forced_visit,
            }), encoding="utf-8")
            return {"status": "needs_arc", "pass": pass_number, "p1": p1, "p2": p2,
                    "arc_authoring_needed": brief["brief"]["arc_authoring_needed"]}

    # Dispatch the local enacter.
    brief_file = ROOT / f".pass_{pass_number}_brief.json"
    brief_file.write_text(json.dumps(brief, ensure_ascii=False), encoding="utf-8")
    reply_file = ROOT / f".pass_{pass_number}_reply.json"
    run([SCRIPTS / "enact_via_ollama.py", "--brief-file", brief_file, "--out", reply_file])
    reply = json.loads(reply_file.read_text(encoding="utf-8"))["reply"]

    names = name_from_slug_map([p1, p2])

    # Write the scene file.
    hearsay = reply["hearsay"]
    hearsay["participants"] = [names.get(p1, p1), names.get(p2, p2)]
    hearsay_file = ROOT / f".pass_{pass_number}_hearsay.json"
    hearsay_file.write_text(json.dumps(hearsay, ensure_ascii=False), encoding="utf-8")

    record_args = [SCRIPTS / "pass_record.py", "--json-file", hearsay_file, "--p1", p1, "--p2", p2, "--pass-number", pass_number]
    _, out, _ = run(record_args)
    record_report = json.loads(out)
    scene_id = record_report["hearsay_id"]

    slug_to_name = {p1: names.get(p1, p1), p2: names.get(p2, p2)}

    def display_speaker(raw):
        return slug_to_name.get(raw.strip().lower(), raw)

    scene_path = ROOT / "_npcs" / "scenes" / f"{scene_id}.md"
    lines = [f"# {scene_id}", "", f"- **Participants:** {names.get(p1, p1)}, {names.get(p2, p2)}",
             "- **Format:** two-npc", f"- **Location:** {hearsay.get('location', brief['brief'].get('location', ''))}",
             "", "## Transcript", ""]
    for turn in reply["scene"]:
        lines.append(f"{display_speaker(turn['speaker'])}: {turn['line']}")
        lines.append("")
    scene_path.write_text("\n".join(lines), encoding="utf-8")

    # Decisions payload for pass_apply.
    decisions = {"participants": {}}
    for slug in (p1, p2):
        pdata = reply["participants"].get(slug, {})
        pdata.setdefault("lived_delta", 1)
        decisions["participants"][slug] = pdata
    decisions_file = ROOT / f".pass_{pass_number}_decisions.json"
    decisions_file.write_text(json.dumps(decisions, ensure_ascii=False), encoding="utf-8")

    apply_args = [SCRIPTS / "pass_apply.py", "--json-file", decisions_file, "--p1", p1, "--p2", p2,
                  "--pass-number", pass_number, "--scene-id", scene_id]
    _, out, _ = run(apply_args)
    apply_report = json.loads(out)

    # Deaths.
    result = {"status": "ok", "pass": pass_number, "p1": p1, "p2": p2, "deaths": [], "births": None}
    for slug in (p1, p2):
        pr = apply_report["participants"][slug]
        if pr["deceased"]:
            result["deaths"].append(slug)
            if slug in state["pool"]:
                state["pool"].remove(slug)

    # Reproduction.
    repro_lines = apply_report["reproduction_raw"].splitlines()
    repro = {ln.split(":", 1)[0].strip(): ln.split(":", 1)[1].strip() for ln in repro_lines if ":" in ln}
    if repro.get("reproduces") == "true":
        PENDING_PATH.write_text(json.dumps({
            "kind": "birth", "pass": pass_number, "p1": p1, "p2": p2,
            "name_lead": repro["name_lead"], "other_parent": repro["other_parent"],
            "deaths": result["deaths"],
        }), encoding="utf-8")
        result["status"] = "needs_name"
        result["name_lead"] = repro["name_lead"]
        result["other_parent"] = repro["other_parent"]

    # Clean up per-pass scratch files.
    for f in (brief_file, reply_file, hearsay_file, decisions_file):
        f.unlink(missing_ok=True)

    return result


def finish_pass(state, n, p1, p2, deaths, birth_slug=None):
    maybe_admit_children(state, n)
    line = f"pass {n}: {p1} x {p2}"
    if deaths:
        line += f" DEATHS:{','.join(deaths)}"
    if birth_slug:
        line += f" BIRTH:{birth_slug}"
    append_log(line)
    state["next_pass"] = n + 1
    save_state(state)


def cmd_run(args):
    state = load_state()
    end = args.end
    limit = args.limit
    done = 0
    while state["next_pass"] <= end and done < limit:
        if len(state["pool"]) < 2:
            save_state(state)
            print(json.dumps({"status": "pool_exhausted", "pool_size": len(state["pool"]), "next_pass": state["next_pass"]}))
            return
        n = state["next_pass"]
        result = do_one_pass(state, n)
        if result["status"] in ("needs_arc", "needs_name"):
            save_state(state)
            print(json.dumps(result, indent=2))
            return
        finish_pass(state, n, result["p1"], result["p2"], result["deaths"])
        done += 1
    print(json.dumps({"status": "batch_done", "passes_run": done, "next_pass": state["next_pass"], "pool_size": len(state["pool"])}))


def cmd_resolve_arc(args):
    a = json.loads(Path(args.arc_json).read_text(encoding="utf-8"))
    cmd = [SCRIPTS / "write_arc.py", a["character_slug"]]
    for tag in a["about"]:
        cmd += ["--about", tag]
    for tag in a["needs"]:
        cmd += ["--needs", tag]
    cmd += ["--context", a["context"], "--premise", a["premise"]]
    _, out, _ = run(cmd)
    pending = json.loads(PENDING_PATH.read_text(encoding="utf-8"))
    PENDING_PATH.write_text(json.dumps({
        "kind": "resume", "pass": pending["pass"], "p1": pending["p1"], "p2": pending["p2"],
        "forced_visit": pending["forced_visit"],
    }), encoding="utf-8")
    print(out)
    print(json.dumps({"status": "arc_written", "resume_pass": pending["pass"]}))


def cmd_resolve_birth(args):
    pending = json.loads(PENDING_PATH.read_text(encoding="utf-8"))
    cmd = [SCRIPTS / "generate_offspring.py", "--parent-a", pending["p1"], "--parent-b", pending["p2"],
           "--name", args.child_name, "--pass-number", pending["pass"]]
    _, out, _ = run(cmd)
    state = load_state()
    # generate_offspring.py prints "(child_cooldown_passes=N, ...)" - parse it.
    cooldown = None
    for line in out.splitlines():
        if "child_cooldown_passes=" in line:
            cooldown = int(line.split("child_cooldown_passes=")[1].split(",")[0].split(")")[0].strip())
    if cooldown is None:
        cooldown = json.loads((ROOT / "_lore" / "tuning.json").read_text(encoding="utf-8"))["child_cooldown_passes"]
    slug = None
    for line in out.splitlines():
        if line.startswith("born:"):
            # "born: <key> (<name>)"
            slug = line.split(":", 1)[1].strip().split(" ", 1)[0]
    unlock_pass = pending["pass"] + cooldown
    state.setdefault("pending_children", []).append({"slug": slug, "unlock_pass": unlock_pass, "birth_pass": pending["pass"]})
    PENDING_PATH.unlink()
    finish_pass(state, pending["pass"], pending["p1"], pending["p2"], pending.get("deaths", []), birth_slug=slug)
    print(out)
    print(json.dumps({"status": "birth_recorded", "slug": slug, "unlock_pass": unlock_pass, "next_pass": state["next_pass"]}))


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run")
    p_run.add_argument("--end", type=int, required=True)
    p_run.add_argument("--limit", type=int, default=25)
    p_run.set_defaults(func=cmd_run)

    p_arc = sub.add_parser("resolve-arc")
    p_arc.add_argument("--arc-json", required=True)
    p_arc.set_defaults(func=cmd_resolve_arc)

    p_birth = sub.add_parser("resolve-birth")
    p_birth.add_argument("--child-name", required=True)
    p_birth.set_defaults(func=cmd_resolve_birth)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

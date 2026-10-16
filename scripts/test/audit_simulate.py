"""
Mechanical half of the /simulate pass audit (see .claude/skills/audit-simulate/SKILL.md). Copies a
corpus worktree's scripts/ and _lore/ into a temp dir, runs N passes of the REAL pass scripts there
with a seeded RNG and no model (a motivated pass gets a stub scene instead of an enacter call), and
prints observed branch counts plus a set of probes, one per audit finding, that say whether each
finding is still present. The real _lore is never written; the copy is deleted afterwards.

Two modes:
  --fixture none    the corpus as it is
  --fixture travel  renames location ids to the display names characters use, chains the locations
                    with routes, makes one need available only at the far end, and seeds half the
                    starting city with provisions >= the arc cost. Generic: picks its own need tag.

`--baseline findings-<date>.json` diffs the probes against a saved snapshot and prints
fixed / new / regressed / unchanged. Probes are True when the finding is still present.

Usage:
    py scripts/test/audit_simulate.py --root <corpus worktree> --passes 40 --seed 7 --fixture none
    py scripts/test/audit_simulate.py --root <corpus worktree> --passes 200 --seed 5 --fixture travel \\
        --baseline diagrams/simulate-audit/findings-2026-10-16.json --json-out run.json
"""

import argparse
import collections
import glob
import importlib
import inspect
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

NOTE_PATTERNS = {
    "local_noop": "pursued their arc's need",
    "no_target": "no reachable target",
    "travel_hop": "is traveling toward",
    "nobody_there": "nobody is around",
    "missed_connection": "missed the connection",
    "p2_mismatch": "doesn't provide",
    "pay_cannot_afford": "cannot_afford",
    "pay_failed": "payment_failed",
    "paid": " paid ",
    "arc_complete": "arc completed",
    "arc_failed": "arc failed",
    "arc_transform": "transformed",
    "arc_no_needs": "has no needs authored",
}


def sh(args, cwd):
    r = subprocess.run([sys.executable, *map(str, args)], capture_output=True, text=True, cwd=cwd)
    if r.returncode:
        raise SystemExit(f"FAILED {args}\n{r.stdout[-600:]}\n{r.stderr[-1200:]}")
    return r.stdout


def living(chars):
    return {k: v for k, v in chars.items() if not v.get("life", {}).get("deceased")}


def load_chars(tmp):
    out = {}
    for p in (tmp / "_lore" / "characters").glob("*.json"):
        if p.stem not in ("lifespans", "_template"):
            out[p.stem] = json.loads(p.read_text(encoding="utf-8"))
    return out


def norm(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def apply_travel_fixture(tmp):
    """Returns a description dict, or {"skipped": reason}."""
    chars = load_chars(tmp)
    live = living(chars)
    contexts = json.loads((tmp / "_lore" / "contexts.json").read_text(encoding="utf-8"))
    by_loc = collections.Counter(c.get("location") for c in live.values() if c.get("location"))
    locs = [l for l, _ in by_loc.most_common()]
    if len(locs) < 2:
        return {"skipped": "needs at least two occupied locations"}
    start, supplier = locs[0], locs[-1]
    start_ctx = {r["context"] for c in live.values() for r in c.get("routines", []) if r["location"] == start}
    start_provides = {t for ctx in start_ctx for t in contexts.get(ctx, {}).get("provides", [])}
    pick = next(((ctx, t) for ctx, d in contexts.items() if isinstance(d, dict) for t in d.get("provides", []) if t not in start_provides), None)
    if not pick:
        return {"skipped": "every provides tag is already available at the start location"}
    ctx, need = pick
    enc_path = tmp / "_lore" / "encodings.json"
    enc = json.loads(enc_path.read_text(encoding="utf-8"))
    ids = {norm(l["id"]): l for l in enc["locations"]}
    for loc in locs:
        if norm(loc) in ids:
            ids[norm(loc)]["id"] = loc
        else:
            enc["locations"].append({"id": loc, "names": [loc], "sources": []})
    enc["routes"] = [{"id": f"audit_{i}", "endpoints": [a, b]} for i, (a, b) in enumerate(zip(locs, locs[1:]))]
    enc_path.write_text(json.dumps(enc, indent=1, ensure_ascii=False), encoding="utf-8")
    n = 0
    for key, c in live.items():
        path = tmp / "_lore" / "characters" / f"{key}.json"
        if c.get("location") == supplier:
            c["routines"] = [{"location": supplier, "context": ctx, "weight": 100, "routine_actions": "audit fixture"}]
        elif c.get("location") == start and c.get("arc"):
            c["arc"].update(needs=[need], about=["concept: audit_fixture"], resolution="ongoing")
            c["partners"] = {}
            c["places_visited"] = list(locs)
            if n % 2 == 0:
                c["provisions"] = 8
            n += 1
        else:
            continue
        path.write_text(json.dumps(c, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"start": start, "supplier": supplier, "need": need, "supplier_context": ctx, "chain": locs, "seeded_provisions": (n + 1) // 2}


def run_passes(tmp, passes, seed, counts):
    S = tmp / "scripts" / "lore"
    (tmp / ".simulate_rng_state.json").write_text(json.dumps({"rng_seed": seed, "draw_counter": 0}))
    sys.path.insert(0, str(S))
    drv = importlib.import_module("simulate_driver")
    start_pool = set(living(load_chars(tmp)))
    for n in range(1, passes + 1):
        pool = sorted(k for k in living(load_chars(tmp)) if k in start_pool)
        if len(pool) < 2:
            counts["pool_exhausted_at"] = n
            break
        p1 = json.loads(sh([S / "simulate_resolve_pair.py", "--pool", *pool, "--pass-number", n], tmp).strip().splitlines()[-1])["participant_1"]
        journey_before = load_chars(tmp)[p1].get("pursuit")
        b = json.loads(sh([S / "pass_prep.py", "--p1", p1, "--pass-number", n], tmp))["brief"]
        counts["passes"] += 1
        pu = b.get("pursuit")
        if pu:
            counts["stage_" + pu["stage"]] += 1
            counts["stagereason_%s/%s" % (pu["stage"], pu["reason"])] += 1
            counts["could_afford_" + str(pu["could_afford"]).lower()] += 1
        if b.get("scene"):
            counts["scene_" + b["scene"]] += 1
        if journey_before and b["survival"].get(p1, {}).get("choice") == "survive":
            counts["survive_midjourney"] += 1
            if not load_chars(tmp)[p1].get("pursuit"):
                counts["journey_reset"] += 1
        counts["choice_" + str(b["survival"].get(p1, {}).get("choice"))] += 1
        notes = " | ".join(b["notes"])
        for k, pat in NOTE_PATTERNS.items():
            if pat in notes:
                counts[k] += 1
        if b["travel"] and b["context"] == "route":
            counts["travel_hop_pass"] += 1
        if b["participant_2"]:
            counts["met_someone"] += 1
        if b["participant_2"] and b.get("scene") == "pair":
            if b["motivated"]:
                counts["motivated"] += 1
                counts["gate_" + b["arc"]["gate"]] += 1
            if b["contested"]:
                counts["contested"] += 1
            if b["arc"]["outcome"]:
                counts["outcome_" + b["arc"]["outcome"]] += 1
            if not b["motivated"] and b["arc"]["outcome"]:
                counts["outcome_without_payment"] += 1  # must stay 0: no arc outcome without a purchase
            p2 = b["participant_2"]
            hs = tmp / f".h{n}.json"
            hs.write_text(json.dumps({"participants": [p1, p2], "location": b["location"], "summary": "stub", "claims": [{"text": "stub", "about": None}]}))
            rec = json.loads(sh([S / "pass_record.py", "--json-file", hs, "--p1", p1, "--p2", p2, "--pass-number", n], tmp))
            dec = tmp / f".d{n}.json"
            dec.write_text(json.dumps({"participants": {p1: {"lived_delta": 1}, p2: {"lived_delta": 1}}}))
            rep = json.loads(sh([S / "pass_apply.py", "--json-file", dec, "--p1", p1, "--p2", p2, "--pass-number", n, "--scene-id", rec["hearsay_id"]], tmp))
            for who, r in rep["participants"].items():
                counts["scene_deaths"] += bool(r["deceased"])
            if "reproduces: true" in rep["reproduction_raw"]:
                counts["reproduces"] += 1
            hs.unlink(); dec.unlink()
        else:
            if drv.apply_solo(p1, n, b)["deceased"]:
                counts["solo_deaths"] += 1
    return drv


def static_probes(tmp, counts, fixture_info):
    """Each probe is True when the finding is still present. None = not scriptable (READ only)."""
    S = tmp / "scripts" / "lore"
    src = lambda name: (S / name).read_text(encoding="utf-8")
    lib = importlib.import_module("simulate_pass_lib")
    lc = importlib.import_module("location_context")
    tuning = json.loads((tmp / "_lore" / "tuning.json").read_text(encoding="utf-8"))
    template = json.loads((tmp / "_lore" / "characters" / "_template.json").read_text(encoding="utf-8"))
    cost = tuning["arc_payment"]["arc_need_cost"]
    default_prov = template.get("provisions", tuning["survival"]["starting_provisions_per_capita"])
    all_py = {p.name: p.read_text(encoding="utf-8") for p in S.glob("*.py")}

    # provisions writers other than the payment gate
    writers = [n for n, t in all_py.items() if re.search(r'\[["\']provisions["\']\]\s*=', t) and n != "simulate_pass_lib.py"]
    chars = load_chars(tmp)
    live = living(chars)
    dead = {k for k, v in chars.items() if v.get("life", {}).get("deceased")}
    biggest = collections.Counter(c.get("location") for c in live.values()).most_common(1)
    dead_cand = total_cand = 0
    if biggest:
        cands = lib.candidates_at(biggest[0][0], chars, exclude="")
        total_cand, dead_cand = len(cands), len([c for c in cands if c in dead])
    counts["candidates_at_biggest_city"] = total_cand
    counts["dead_among_candidates"] = dead_cand
    # F3, second half: a dead character's routine must not make a place "provide" anything
    dead_provide_leak = False
    if biggest:
        contexts_all = json.loads((tmp / "_lore" / "contexts.json").read_text(encoding="utf-8"))
        with_dead = lc.location_provides(biggest[0][0], list(chars.values()), contexts_all)
        living_only = lc.location_provides(biggest[0][0], list(live.values()), contexts_all)
        dead_provide_leak = with_dead != living_only
    counts["dead_routines_change_provides"] = dead_provide_leak

    locs_enc = json.loads((tmp / "_lore" / "encodings.json").read_text(encoding="utf-8")).get("locations", [])
    contexts = json.loads((tmp / "_lore" / "contexts.json").read_text(encoding="utf-8"))
    provides_nonempty = sum(1 for l in locs_enc if lc.location_provides(l["id"], list(chars.values()), contexts))
    counts["encodings_locations"] = len(locs_enc)
    counts["encodings_locations_with_provides"] = provides_nonempty

    tuning_text = json.dumps(tuning)
    keys = {k for k in re.findall(r'"([a-z_]+)":', tuning_text) if not k.startswith("_")} - {"min", "max", "base"}
    code = "".join(all_py.values()) + "".join(p.read_text(encoding="utf-8") for p in (tmp / "scripts" / "test").glob("*.py"))
    unused = sorted(k for k in keys if not re.search(r'["\']%s["\']' % k, code))
    if code.count("LEAD_EXPIRY_PASSES") <= 1:
        unused.append("lead_expiry_passes (loaded, never used)")
    counts["unused_tuning_keys"] = unused

    social_writers = [n for n, t in all_py.items() if re.search(r'social_circle["\']\]?\s*(=|\.append|\.extend)', t) or "setdefault(\"social_circle\"" in t]
    lead_readers = [n for n, t in all_py.items() if "roll_lead_followup(" in t and n not in ("simulate_pass_lib.py",)]
    prep_src = src("pass_prep.py") + src("simulate_pass_brief.py")
    mech_src = inspect.getsource(lib.run_pass_mechanics)
    repo = Path(__file__).resolve().parents[2]
    diagram = repo / "diagrams" / "gen_simulate_pass.py"
    return {
        "F1": default_prov < cost and not writers,
        "F2": "history" not in mech_src.split("if matched_need:")[1].split("# Step 5")[0],
        "F3": dead_cand > 0 or dead_provide_leak,
        "F4": "check_anchor_reference" not in prep_src and "check_anchor_reference" not in mech_src,
        "F5": "derived_from" not in src("enact_via_ollama.py").split("REPLY_SCHEMA")[1].split("def load_preamble")[0],
        "F6": "provides" not in inspect.getsource(lib.candidates_at),
        # RAN since the pursuit redesign: a survive roll taken mid-journey must leave the journey alone.
        # None when this run never rolled one.
        "F7": (counts["journey_reset"] > 0) if counts["survive_midjourney"] else None,
        "F8": 'add_argument("--p2", required=True' in src("pass_apply.py") and "roll_death_legacy" not in inspect.getsource(importlib.import_module("simulate_driver").apply_solo),
        "F9": counts.get("conformance_kin_invariant_failures", 0) > 0,
        "F10": None,
        "F11": bool(unused) or not social_writers or not lead_readers,
        "F12": diagram.exists() and "participant_2" in diagram.read_text(encoding="utf-8") and "lead" in diagram.read_text(encoding="utf-8"),
        "F13": counts["encodings_locations"] > 0 and provides_nonempty == 0 if not fixture_info else None,
        "F14": "max(" not in inspect.getsource(importlib.import_module("provisions_lib").set_provisions),
        "F15": None,
        "F16": "knowledge" not in inspect.getsource(importlib.import_module("pass_prep").load_character_brief),
    }, {"provisions_writers_outside_payment": writers, "social_circle_writers": social_writers, "lead_followup_callers": lead_readers}


def conformance_kin_failures(tmp):
    r = subprocess.run([sys.executable, str(tmp / "scripts" / "test" / "conformance_report.py"), "--root", str(tmp)], capture_output=True, text=True, cwd=tmp)
    return len(re.findall(r"also appear as partners", r.stdout))


def diff(baseline_path, probes):
    base = json.loads(Path(baseline_path).read_text(encoding="utf-8"))
    status = {f["id"]: f["status"] for f in base["findings"]}
    out = {"fixed": [], "new": [], "regressed": [], "still_present": [], "not_scriptable": []}
    for fid, present in probes.items():
        if present is None:
            out["not_scriptable"].append(fid)
        elif fid not in status:
            out["new"].append(fid) if present else None
        elif status[fid] == "open" and not present:
            out["fixed"].append(fid)
        elif status[fid] == "fixed" and present:
            out["regressed"].append(fid)
        elif present:
            out["still_present"].append(fid)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", required=True, help="a corpus worktree (never written)")
    ap.add_argument("--passes", type=int, default=40)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--fixture", choices=["none", "travel"], default="none")
    ap.add_argument("--baseline", default=None)
    ap.add_argument("--json-out", default=None)
    a = ap.parse_args()
    root = Path(a.root).resolve()
    if not (root / "_lore").exists() or not (root / "scripts" / "lore").exists():
        raise SystemExit(f"{root} has no _lore/ and scripts/lore/")

    tmp = Path(tempfile.mkdtemp(prefix="audit_simulate_"))
    try:
        ign = shutil.ignore_patterns("__pycache__", ".git")
        shutil.copytree(root / "_lore", tmp / "_lore", ignore=ign)
        shutil.copytree(root / "scripts", tmp / "scripts", ignore=ign)
        (tmp / "_npcs" / "scenes").mkdir(parents=True)
        fixture = apply_travel_fixture(tmp) if a.fixture == "travel" else None
        counts = collections.Counter()
        if fixture and fixture.get("skipped"):
            print(f"fixture skipped: {fixture['skipped']}")
        run_passes(tmp, a.passes, a.seed, counts)
        counts["conformance_kin_invariant_failures"] = conformance_kin_failures(tmp)
        probes, extra = static_probes(tmp, counts, fixture)
        result = {"root": str(root), "passes": a.passes, "seed": a.seed, "fixture": a.fixture, "fixture_info": fixture,
                  "observed": dict(counts), "static": extra, "probes": probes}
        if a.baseline:
            result["diff"] = diff(a.baseline, probes)
        text = json.dumps(result, indent=2, ensure_ascii=False, default=list)
        print(text)
        if a.json_out:
            Path(a.json_out).write_text(text + "\n", encoding="utf-8")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()

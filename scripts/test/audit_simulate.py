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

`--dump DIR` keeps the run's end state (characters, provisions pools, draw audit) in DIR, for comparing two
seeded runs byte for byte (see scripts/test/test_travel_nodes.py). Roads are nodes now (TODO.md "Travel as
nodes"): the observed counts carry `road_hops`, `stage_met_on_road`, `road_meetings_with_outcome`,
`died_en_route`, `longest_journey_passes`, and probes F17-F20 cover roads. A root with a travel graph but
no lore can be made with scripts/test/make_travel_fixture.py.

`--baseline findings-<date>.json` diffs the probes against a saved snapshot and prints
fixed / new / regressed / unchanged. Probes are True when the finding is still present.

Added with the circle writer / arc completion / estate work (2026-10-17): `--births` makes a pair
that reproduces actually have a child (a stub name, no model), so the birth-time circle writer runs
in the loop; `scenario_probes()` builds a tiny synthetic world in the scratch copy and drives the
three new mechanisms through the REAL code (a completion through run_pass_mechanics, deaths through
record_death.py, a birth through generate_offspring.py) - probes F17 (circle), F18 (completion), F19
(estate). `--digest-out` writes sha256 digests of the draw log (timestamps stripped) and of every
character file and encodings.json, so two runs of one seed - also under different PYTHONHASHSEED -
can be compared byte for byte.

Added with the author's answers of 2026-10-17 (bequest tax, reflection scenes, a need available at home,
completion tales for later children, no births on roads, no neutral temperament): `decision_checks()`
drives each through the REAL code and the probes F2 (a need available at home goes through the arrival
pipeline), F24 (the new scale definitions), F25 (a character alone at an empty place gets a one-person
reflection scene, dispatched through the driver with a stub enacter), F26 (the bequest tax), F27 (a child
born after a completion has its parents' completion tale), F28 (no births on roads) and F29 (everybody has a
temperament) read them. The enacter is always a stub: no model call anywhere in this file.

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
import hashlib
import tempfile
from pathlib import Path

NOTE_PATTERNS = {
    "local_available": "is available at their own place",
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
    "met_on_road": "on the road at",
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


def run_passes(tmp, passes, seed, counts, births=False):
    S = tmp / "scripts" / "lore"
    (tmp / ".simulate_rng_state.json").write_text(json.dumps({"rng_seed": seed, "draw_counter": 0}))
    sys.path.insert(0, str(S))
    drv = importlib.import_module("simulate_driver")
    start_pool = set(living(load_chars(tmp)))
    journey_len: dict = {}
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
            if pu.get("local"):
                counts["pursuit_local"] += 1
                counts["local_outcome_rolled"] += bool(b["arc"]["outcome"])
        if b.get("scene"):
            counts["scene_" + b["scene"]] += 1
        if journey_before and b["survival"].get(p1, {}).get("choice") in ("work", "survive"):  # "survive" is the pre-2026-10-17 name
            counts["work_midjourney"] += 1
            if not load_chars(tmp)[p1].get("pursuit"):
                counts["journey_reset"] += 1
        counts["choice_" + str(b["survival"].get(p1, {}).get("choice"))] += 1
        if b.get("arc_completion"):
            ac = b["arc_completion"]
            counts["arc_completions"] += 1
            counts.setdefault("arc_completion_turns", []).append(ac["turns"])
            counts.setdefault("arc_completion_rewards", []).append(ac["reward"])
        notes = " | ".join(b["notes"])
        for k, pat in NOTE_PATTERNS.items():
            if pat in notes:
                counts[k] += 1
        if b["travel"] and b["context"] == "route":
            counts["travel_hop_pass"] += 1
            if b["location"].startswith("road:"):
                counts["road_hops"] += 1
            else:
                counts["place_hops_mid_journey"] += 1
        if pu and pu["stage"] == "died_en_route":
            counts["died_en_route"] += 1
        if pu and pu["stage"] == "met_on_road":
            counts["met_on_road_with_payment"] += bool(b["motivated"])
            counts["road_meetings_with_outcome"] += bool(b["arc"]["outcome"])  # must stay 0: nothing is bought on a road
        if journey_before:
            journey_len[p1] = journey_len.get(p1, 0) + 1
            counts["longest_journey_passes"] = max(counts["longest_journey_passes"], journey_len[p1])
        else:
            journey_len.pop(p1, None)
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
                if births:
                    counts["births"] += 1
                    drv.run([S / "generate_offspring.py", "--parent-a", p1, "--parent-b", p2, "--name", f"Audit Child {n}", "--pass-number", n])
            # circle writer: two people who shared a scene hold each other as at least `met`
            after = load_chars(tmp)
            for a_, b_ in ((p1, p2), (p2, p1)):
                circle = after[a_].get("social_circle") or {}
                if not isinstance(circle, dict) or b_ not in circle:
                    counts["pair_scenes_without_circle_tie"] += 1
            hs.unlink(); dec.unlink()
        elif b.get("scene") == "solo":
            # a reflection (arrived_empty): one participant, no claims, no partner, no reproduction
            counts["reflections"] += 1
            hs = tmp / f".h{n}.json"
            hs.write_text(json.dumps({"participants": [p1], "location": b["location"], "summary": "stub reflection", "claims": []}))
            rec = json.loads(sh([S / "pass_record.py", "--json-file", hs, "--p1", p1, "--pass-number", n], tmp))
            dec = tmp / f".d{n}.json"
            dec.write_text(json.dumps({"participants": {p1: {"lived_delta": 1}}}))
            rep = json.loads(sh([S / "pass_apply.py", "--json-file", dec, "--p1", p1, "--pass-number", n, "--scene-id", rec["hearsay_id"]], tmp))
            counts["reflection_reproduction_ran"] += bool(rep["reproduction_raw"].strip())  # must stay 0
            counts["reflection_deaths"] += bool(rep["participants"][p1]["deceased"])
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

    pv = json.loads((tmp / "_lore" / "provisions.json").read_text(encoding="utf-8")) if (tmp / "_lore" / "provisions.json").exists() else {}
    counts["road_pools_created"] = sum(1 for sect in pv.values() if isinstance(sect, dict) for k in sect if k.startswith("road:"))
    counts["roads_in_places_visited"] = sum(1 for c in chars.values() for l in c.get("places_visited") or [] if l.startswith("road:"))
    tg = importlib.import_module("travel_graph")
    g = tg.build_graph(json.loads((tmp / "_lore" / "encodings.json").read_text(encoding="utf-8")))
    counts["direct_place_to_place_edges"] = sum(1 for n, nb in g.items() for m in nb if not tg.is_road(n) and not tg.is_road(m))

    social_writers = [n for n, t in all_py.items() if re.search(r'social_circle["\']\]?\s*(=|\.append|\.extend)', t) or "setdefault(\"social_circle\"" in t]
    lead_readers = [n for n, t in all_py.items() if "roll_lead_followup(" in t and n not in ("simulate_pass_lib.py",)]
    prep_src = src("pass_prep.py") + src("simulate_pass_brief.py")
    mech_src = inspect.getsource(lib.run_pass_mechanics)
    repo = Path(__file__).resolve().parents[2]
    diagram = repo / "diagrams" / "gen_simulate_pass.py"
    return {
        "F1": default_prov < cost and not writers,
        "F2": None,  # set from the scenario probes in main(): a need available at home goes through the arrival pipeline
        "F3": dead_cand > 0 or dead_provide_leak,
        "F4": "check_anchor_reference" not in prep_src and "check_anchor_reference" not in mech_src,
        "F5": "derived_from" not in src("enact_via_ollama.py").split("REPLY_SCHEMA")[1].split("def load_preamble")[0],
        "F6": "provides" not in inspect.getsource(lib.candidates_at),
        # RAN since the pursuit redesign: a work roll taken mid-journey must leave the journey alone.
        # None when this run never rolled one.
        "F7": (counts["journey_reset"] > 0) if counts["work_midjourney"] else None,
        # pass_apply/pass_record take a one-participant call now (2026-10-17); what remains is that a solo pass's
        # death (apply_solo) still has no death-legacy and no shock-candidate resolution
        "F8": "roll_death_legacy" not in inspect.getsource(importlib.import_module("simulate_driver").apply_solo),
        "F9": counts.get("conformance_kin_invariant_failures", 0) > 0,
        "F10": None,
        "F11": bool(unused) or not social_writers or not lead_readers,
        "F12": diagram.exists() and "participant_2" in diagram.read_text(encoding="utf-8") and "lead" in diagram.read_text(encoding="utf-8"),
        "F13": counts["encodings_locations"] > 0 and provides_nonempty == 0 if not fixture_info else None,
        "F14": "max(" not in inspect.getsource(importlib.import_module("provisions_lib").set_provisions),
        "F15": None,
        "F16": "knowledge" not in inspect.getsource(importlib.import_module("pass_prep").load_character_brief),
        # Roads as nodes (2026-10-17). Each is True when the problem is present.
        "F17": counts["road_pools_created"] > 0,           # a pool, or an upkeep checkpoint, exists for a road
        "F18": counts["road_meetings_with_outcome"] > 0 or counts["met_on_road_with_payment"] > 0,  # an arc outcome or a purchase on a road scene
        "F19": counts["roads_in_places_visited"] > 0,      # a road recorded as a place visited
        "F20": counts["direct_place_to_place_edges"] > 0,  # a connection without a road node between
    }, {"provisions_writers_outside_payment": writers, "social_circle_writers": social_writers, "lead_followup_callers": lead_readers}


def _write(tmp, key, c):
    (tmp / "_lore" / "characters" / f"{key}.json").write_text(json.dumps(c, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _blank(name, location, **extra):
    c = {"name": name, "origin": location, "location": location, "places_visited": [location], "backstory": "", "knowledge": {"education": {"percent": None, "mode": "", "topic": None, "items": []}, "experience": []},
         "criterion": {"standard": "", "wasted_life": "", "anchor": "", "derivation": "", "trusts": "", "distrusts": "", "tempered": 0, "cost_ledger": [], "history": []},
         "life": {"lived": 0, "deceased": False}, "energy": 20, "provisions": 2, "parents": [], "partners": {}, "partners_quality": {}, "social_circle": {}, "routines": [],
         "arc": {"about": [], "needs": [], "context": "", "premise": "", "resolution": "ongoing", "history": [], "turns": 0}}
    c.update(extra)
    return c


def scenario_probes(tmp):
    """A tiny synthetic world in the scratch copy, driven through the real code. Returns
    {check name: True if it PASSED}, plus a `_detail` dict. Generic names only (no lore)."""
    S = tmp / "scripts" / "lore"
    sys.path.insert(0, str(S))
    for m in [m for m in sys.modules if m in ("simulate_pass_lib", "arc_completion", "estate", "update_social_circle", "notify_death", "tuning", "provisions_lib", "rng_context", "location_context", "travel_graph")]:
        del sys.modules[m]  # fresh import against this scratch root
    lib = importlib.import_module("simulate_pass_lib")
    usc = importlib.import_module("update_social_circle")
    ac = importlib.import_module("arc_completion")
    tuning_mod = importlib.import_module("tuning")
    T = tuning_mod.load()
    contexts = json.loads((tmp / "_lore" / "contexts.json").read_text(encoding="utf-8"))
    ctx_need = next((c, d["provides"][0]) for c, d in contexts.items() if isinstance(d, dict) and d.get("provides"))
    shop_ctx, need = ctx_need
    home_ctx = next(c for c, d in contexts.items() if isinstance(d, dict) and need not in d.get("provides", []))
    chars_before = set(load_chars(tmp))
    ok, detail = {}, {}

    # --- locations and a route between them
    enc_path = tmp / "_lore" / "encodings.json"
    enc = json.loads(enc_path.read_text(encoding="utf-8"))
    for loc in ("ProbeHome", "ProbeShop"):
        enc["locations"].append({"id": loc, "names": [loc], "sources": []})
    enc["routes"].append({"id": "probe_route", "endpoints": ["ProbeHome", "ProbeShop"]})
    enc_path.write_text(json.dumps(enc, indent=1, ensure_ascii=False), encoding="utf-8")

    # --- the cast: completer A (child C, mentioned X, five people met), supplier B, a childless E
    mets = [f"probe_m{i}" for i in range(5)]
    for k in mets:
        _write(tmp, k, _blank(k.title().replace("_", " "), "ProbeHome", routines=[{"location": "ProbeHome", "context": home_ctx, "weight": 100, "routine_actions": "probe"}]))
    a_arc = {"about": ["concept: probe"], "needs": [need], "context": home_ctx, "premise": "Probe wants the thing done.", "resolution": "ongoing",
             "history": [{"pass": 1, "outcome": "advance"}, {"pass": 2, "outcome": "advance"}], "turns": 6}
    _write(tmp, "probe_a", _blank("Probe Alpha", "ProbeHome", provisions=20, arc=a_arc, places_visited=["ProbeHome", "ProbeShop"],
                                  routines=[{"location": "ProbeHome", "context": home_ctx, "weight": 100, "routine_actions": "probe"}],
                                  social_circle={**{m: "met" for m in mets}, "probe_x": "mentioned"}))
    _write(tmp, "probe_x", _blank("Probe Ex", "ProbeHome"))
    _write(tmp, "probe_b", _blank("Probe Bravo", "ProbeShop", routines=[{"location": "ProbeShop", "context": shop_ctx, "weight": 100, "routine_actions": "probe"}]))
    _write(tmp, "probe_c", _blank("Probe Child", "ProbeHome", parents=["probe_a"], provisions=1))
    _write(tmp, "probe_e", _blank("Probe Echo", "ProbeHome", provisions=4))
    lifespans = json.loads((tmp / "_lore" / "characters" / "lifespans.json").read_text(encoding="utf-8"))
    for k in ("probe_a", "probe_b", "probe_c", "probe_e", "probe_x", *mets):
        lifespans["lifespans"][k] = {"span": 99, "range": "30-60"}
    (tmp / "_lore" / "characters" / "lifespans.json").write_text(json.dumps(lifespans, indent=2), encoding="utf-8")

    # --- drive one pass of probe_a through the real run_pass_mechanics. Only the dice are fixed.
    lib.roll_survival = lambda key, home: {"choice": "arc"}
    lib.roll_meetable = lambda candidates, favor=None: {"met": True, "chosen": "probe_b", "odds_used": 100}
    lib.arc_payment_gate = lambda p1, p2, arc: {"motivated": True, "reason": None, "odds_used": 100, "cost": 0}
    lib.roll_contested = lambda strength=0, quality=0: False
    lib.check_arc_alignment = lambda about, needs, peer: {"gate": "hit", "inclined": "help", "matched_about": []}
    lib.roll_arc_outcome = lambda inclined, contested=False: "advance"
    (tmp / ".simulate_rng_state.json").write_text(json.dumps({"rng_seed": 99, "draw_counter": 0}))
    for _ in range(3):  # the first passes may be the walk; keep going until the arc is settled
        r = lib.run_pass_mechanics("probe_a", 500 + _)
        if (r.get("arc") or {}).get("tally_result") == "complete":
            break
    a = load_chars(tmp)["probe_a"]
    done = r.get("arc_completion") or {}
    if not done:
        detail["completion_last_pass"] = {"pursuit": r.get("pursuit"), "arc": r.get("arc"), "notes": r.get("notes")}
    ok["completion_detected"] = bool(done)
    if done:
        expect = ac.reward_for(a["arc"]["turns"], T["arc_completion_reward"])
        ok["reward_in_range"] = T["arc_completion_reward"]["min"] <= done["reward"] <= T["arc_completion_reward"]["max"]
        ok["reward_is_the_formula"] = abs(done["reward"] - expect) < 1e-9 and a["arc"]["completion"]["turns"] == a["arc"]["turns"]
        ok["turns_counted_each_own_pass"] = a["arc"]["turns"] >= 7  # 6 before + this walk, at least one pass
        ok["tale_filed"] = (tmp / "_lore" / "tales" / f"{done['tale_id']}.md").exists() and any(t["id"] == done["tale_id"] for t in json.loads(enc_path.read_text(encoding="utf-8"))["tales"]["entries"])
        c = load_chars(tmp)["probe_c"]
        ok["child_has_tale_in_knowledge"] = f"tale: {done['tale_id']}" in c["knowledge"]["education"]["items"]
        ok["child_told_for_certain"] = "probe_c" in done["notified"] and any("achieved" in (e if isinstance(e, str) else e.get("text", "")) for e in c["knowledge"]["experience"])
        wider = len(mets) + 1  # the five met, plus the supplier A met in this very pass
        ok["wider_circle_share"] = len(done["notified"]) == 1 + max(1, round(T["notification"]["extended_share"] * wider)) and "probe_x" not in done["notified"]
        ok["completer_holds_reward"] = a["provisions"] > 20 and done["provisions"] == a["provisions"]
        detail["completion"] = {"turns": a["arc"]["turns"], "reward": done["reward"], "notified": done["notified"]}

    # --- deaths through record_death.py: the bequest tax (half) to the pool of the place they died in, the rest
    # to the living child; the whole estate to that pool when childless; two heirs split the heirs' half equally
    tax = float((T.get("estate") or {}).get("bequest_tax", 0.0))
    pool_mod = importlib.import_module("provisions_lib")
    pools = lambda: json.loads((tmp / "_lore" / "provisions.json").read_text(encoding="utf-8"))["pools"]
    before_c = load_chars(tmp)["probe_c"]["provisions"]
    a_now = load_chars(tmp)["probe_a"]
    estate_a, loc_a = a_now["provisions"], a_now["location"]
    pool_a_before = pool_mod.get_provisions(loc_a)
    sh([S / "record_death.py", "probe_a", "--seed", "3"], tmp)
    after = load_chars(tmp)
    ok["estate_to_living_child"] = abs(after["probe_c"]["provisions"] - (before_c + estate_a * (1 - tax))) < 1e-9 and after["probe_a"]["provisions"] == 0
    ok["bequest_tax_goes_to_the_pool_where_they_died"] = abs(pools()[loc_a] - (pool_a_before + estate_a * tax)) < 1e-9
    ok["bequest_conserves_the_estate"] = abs((after["probe_c"]["provisions"] - before_c) + (pools()[loc_a] - pool_a_before) - estate_a) < 1e-9
    pool_before = pool_mod.get_provisions("ProbeHome")
    sh([S / "record_death.py", "probe_e", "--seed", "3"], tmp)
    pool_after = pools()["ProbeHome"]
    ok["estate_to_pool_without_children"] = abs(pool_after - (pool_before + 4)) < 1e-9 and load_chars(tmp)["probe_e"]["provisions"] == 0
    # two heirs split equally
    _write(tmp, "probe_p", _blank("Probe Papa", "ProbeHome", provisions=5))
    for k in ("probe_k1", "probe_k2"):
        _write(tmp, k, _blank(k.title().replace("_", " "), "ProbeHome", parents=["probe_p"], provisions=0))
    lifespans["lifespans"].update({"probe_p": {"span": 99, "range": "30-60"}})
    (tmp / "_lore" / "characters" / "lifespans.json").write_text(json.dumps(lifespans, indent=2), encoding="utf-8")
    pool_before = pool_mod.get_provisions("ProbeHome")
    sh([S / "record_death.py", "probe_p", "--seed", "3"], tmp)
    after = load_chars(tmp)
    ok["estate_split_equally"] = after["probe_k1"]["provisions"] == after["probe_k2"]["provisions"] == 5 * (1 - tax) / 2
    ok["bequest_two_heirs_pool_share"] = abs(pools()["ProbeHome"] - (pool_before + 5 * tax)) < 1e-9
    detail["bequest"] = {"tax": tax, "completer_estate": estate_a, "died_at": loc_a}

    # --- a birth through generate_offspring.py: circle inheritance and propagation
    pool_live = [k for k in sorted(chars_before) if not load_chars(tmp)[k]['life'].get('deceased') and load_chars(tmp)[k].get('parents')]
    parents = len(pool_live) >= 14
    if parents:
        # two living characters that have parents of their own are the parents of the test child
        pa, pb = pool_live[0], pool_live[1]
        others = [k for k in pool_live[2:14] if k not in (pa, pb)]
        ca, cb = load_chars(tmp)[pa], load_chars(tmp)[pb]
        ca["social_circle"] = {k: "met" for k in others[:10]}
        cb["social_circle"] = {k: "met" for k in others[4:10]}
        _write(tmp, pa, ca); _write(tmp, pb, cb)
        sh([S / "generate_offspring.py", "--parent-a", pa, "--parent-b", pb, "--name", "Probe Newborn", "--pass-number", 600, "--seed", 11], tmp)
        circ = load_chars(tmp)["probe_newborn"]["social_circle"]
        inh = [k for k, v in circ.items() if v == "inherited"]
        ok["birth_parents_in_circle"] = circ.get(pa) == "parent" and circ.get(pb) == "parent"
        ok["birth_inherits_a_share"] = 3 <= len(inh) <= 5 and set(inh) <= set(others[:10])
        got = load_chars(tmp)
        ok["birth_child_in_parents_circles"] = got[pa]["social_circle"].get("probe_newborn") == "child" and got[pb]["social_circle"].get("probe_newborn") == "child"
        grand = [g for p in (pa, pb) for g in got[p].get("parents", []) if g in got]
        ok["birth_descendant_up_the_line"] = all(got[g]["social_circle"].get("probe_newborn") == "descendant" for g in grand)
        detail["birth"] = {"inherited": inh, "grandparents": grand}
    # --- readers take the new shape
    lc = importlib.import_module("location_context")
    tg = importlib.import_module("travel_graph")
    kid_like = {"social_circle": {"probe_b": "met", "probe_x": "mentioned"}, "partners": {}, "parents": []}
    ok["readers_take_the_map"] = lc._known_keys(kid_like) == {"probe_b", "probe_x"} and tg._known_people_locations(kid_like) is not None
    # --- backfill is a dry run by default and idempotent
    bf = tmp / "scripts" / "lore" / "backfill_social_circle.py"
    dry = sh([bf, "--root", tmp], tmp)
    ok["backfill_dry_run_writes_nothing"] = "DRY RUN" in dry and "nothing written" in dry
    sh([bf, "--root", tmp, "--apply", "--seed", 2], tmp)
    snap = {k: json.dumps(v, sort_keys=True) for k, v in load_chars(tmp).items()}
    sh([bf, "--root", tmp, "--apply", "--seed", 2], tmp)
    again = {k: json.dumps(v, sort_keys=True) for k, v in load_chars(tmp).items()}
    ok["backfill_is_idempotent"] = snap == again
    if snap != again:
        detail["backfill_changed_on_second_run"] = sorted(k for k in snap if snap[k] != again.get(k))[:5]

    # --- temperament and the second participant (2026-10-17): p2 eats, traits move the odds in the
    # stated directions, trends respond, a neutral character is unchanged, and the window is kept.
    ok.update(temperament_checks(tmp, lib, S, home_ctx, shop_ctx, need, detail))
    ok.update(decision_checks(tmp, lib, S, home_ctx, shop_ctx, need, detail))
    ok["_detail"] = detail
    return ok



def temperament_checks(tmp, lib, S, home_ctx, shop_ctx, need, detail):
    """Probes for the second participant eating (p2_*) and for temperament (trait_*, trend_*,
    neutral_*, window_*, retry_*). Names start with their prefix so main() can fold them into findings
    F21 to F24. Everything runs through the REAL code; only the dice that would decide where the pass
    goes are fixed (the same stubs scenario_probes installed)."""
    ok = {}
    rs = importlib.import_module("roll_survival")
    tm = importlib.import_module("temperament")
    er = importlib.import_module("economy_rules")
    pl = importlib.import_module("provisions_lib")
    T = importlib.import_module("tuning").load()
    s_, t_ = T["survival"], T["temperament"]
    eat, rate = s_["eat_amount"], s_["upkeep_rate_per_capita"]

    # ---- the second participant eats ------------------------------------------------------------
    lifespans_path = tmp / "_lore" / "characters" / "lifespans.json"

    def add_lifespans(*keys):
        ls = json.loads(lifespans_path.read_text(encoding="utf-8"))
        for k in keys:
            ls["lifespans"][k] = {"span": 99, "range": "30-60"}
        lifespans_path.write_text(json.dumps(ls, indent=2), encoding="utf-8")

    shop = [{"location": "ProbeShop", "context": shop_ctx, "weight": 100, "routine_actions": "probe"}]
    home = [{"location": "ProbeHome", "context": home_ctx, "weight": 100, "routine_actions": "probe"}]
    arc = {"about": ["concept: probe_q"], "needs": [need], "context": home_ctx, "premise": "Probe wants a thing.", "resolution": "ongoing", "history": [], "turns": 0}
    # q1 stands at the shop but works at home (a visitor), so the shop is its destination at 0 hops
    _write(tmp, "probe_q1", _blank("Probe Q One", "ProbeShop", routines=home, arc=arc, places_visited=["ProbeHome", "ProbeShop"], provisions=2))
    _write(tmp, "probe_s", _blank("Probe Supplier", "ProbeShop", routines=shop, energy=10, provisions=2))
    _write(tmp, "probe_t", _blank("Probe Starver", "ProbeShop", routines=shop, energy=1, provisions=0))
    add_lifespans("probe_q1", "probe_s", "probe_t")
    pop = pl.population_of("ProbeShop")
    pl.set_provisions("ProbeShop", 100)
    lib.roll_survival = lambda key, home: {"choice": "arc"}
    lib.roll_meetable = lambda candidates, favor=None: {"met": True, "chosen": "probe_s", "odds_used": 100}
    lib.arc_payment_gate = lambda p1, p2, arc_: {"motivated": False, "reason": "cannot_afford", "odds_used": None, "cost": 3}
    lib.check_arc_alignment = lambda a_, n_, peer: {"gate": "miss", "inclined": None, "matched_about": []}
    r = lib.run_pass_mechanics("probe_q1", 700)
    after = load_chars(tmp)
    sv = after["probe_s"]
    pool_now = json.loads((tmp / "_lore" / "provisions.json").read_text(encoding="utf-8"))["pools"]["ProbeShop"]
    detail["p2_pass"] = {"pursuit": (r.get("pursuit") or {}).get("stage"), "survival": r["survival"].get("probe_s"), "pool": pool_now}
    ok["p2_eats_base_cost_and_meal"] = r.get("participant_2") == "probe_s" and sv["energy"] == 10 - s_["base_cost"] + eat and r["survival"]["probe_s"]["energy"] == sv["energy"]
    ok["p2_eats_from_own_and_pool"] = sv["provisions"] == 2 - eat // 2
    ok["p2_no_work_pay_no_arc_cost"] = sv["provisions"] <= 2 and sv["energy"] == 10 - s_["base_cost"] + eat  # a worker would hold more, an arc-goer one less energy
    ok["p2_upkeep_once_per_pass"] = abs(pool_now - (100 - pop * rate - eat)) < 1e-9  # p1 and p2 each take one unit from the pool, the drain is taken once
    # failed pursuit leaves the character a memory of where it went (persistence reads it)
    ok["retry_failed_destination_written"] = (after["probe_q1"].get("failed_destination") or {}).get("place") == "ProbeShop"

    # starvation: p2 with 1 energy, nothing in the purse, nothing in the pool
    pl.set_provisions("ProbeShop", 0)
    lib.roll_meetable = lambda candidates, favor=None: {"met": True, "chosen": "probe_t", "odds_used": 100}
    q = load_chars(tmp)["probe_q1"]; q["provisions"] = 2; q["energy"] = 20; _write(tmp, "probe_q1", q)
    r2 = lib.run_pass_mechanics("probe_q1", 701)
    ok["p2_can_starve"] = bool(r2["survival"].get("probe_t", {}).get("died")) and any("probe_t" in n and "hit 0" in n for n in r2["notes"])
    # and it goes through the death path: pass_apply reads the brief and calls record_death.py
    if ok["p2_can_starve"]:
        (tmp / ".simulate_pass_brief.json").write_text(json.dumps(r2), encoding="utf-8")
        hs = tmp / ".hq.json"
        hs.write_text(json.dumps({"participants": ["probe_q1", "probe_t"], "location": "ProbeShop", "summary": "stub", "claims": [{"text": "stub", "about": None}]}))
        rec = json.loads(sh([S / "pass_record.py", "--json-file", hs, "--p1", "probe_q1", "--p2", "probe_t", "--pass-number", 701], tmp))
        dec = tmp / ".dq.json"
        dec.write_text(json.dumps({"participants": {"probe_q1": {"lived_delta": 1}, "probe_t": {"lived_delta": 1}}}))
        rep = json.loads(sh([S / "pass_apply.py", "--json-file", dec, "--p1", "probe_q1", "--p2", "probe_t", "--pass-number", 701, "--scene-id", rec["hearsay_id"]], tmp))
        tdead = load_chars(tmp)["probe_t"]
        ok["p2_starvation_recorded"] = rep["participants"]["probe_t"]["cause"] == "energy" and tdead["life"]["deceased"] and any(t_["id"].startswith("death_of_probe_starver") for t_ in json.loads((tmp / "_lore" / "encodings.json").read_text(encoding="utf-8"))["tales"]["entries"])

    # ---- the window is kept ------------------------------------------------------------------------
    q = load_chars(tmp)["probe_q1"]
    ok["window_recorded_per_own_turn"] = len(q.get("recent", [])) == 2 and set(q["recent"][-1]) == {"pc", "p", "e"}
    for _ in range(t_["recent_window_max"] + 3):
        lib.run_pass_mechanics("probe_q1", 710 + _)
        c_ = load_chars(tmp)["probe_q1"]
        if c_["life"]["deceased"]:
            break
    ok["window_capped_at_max"] = len(load_chars(tmp)["probe_q1"].get("recent", [])) <= t_["recent_window_max"]

    # ---- traits move the odds in the stated directions ------------------------------------------------
    base = (10, 0.5, 0.5, 2, 0.0, 2)  # energy, affinity, pressure, pool per head, checkpoint trend, provisions
    odds = lambda traits=None, recent=None, args=base: rs.arc_odds(s_, *args, traits=traits, recent=recent, t=t_)
    # risk and the cushion: a purse of 8 sits between the bold reserve (3) and the cautious one (13)
    mid = (10, 0.5, 0.5, 2, 0.0, 8)
    ok["trait_risk_bold_pursues_sooner"] = odds({"risk": 1}, args=mid)["pct"] > odds({"risk": 0}, args=mid)["pct"] > odds({"risk": -1}, args=mid)["pct"]
    low = (3, 0.5, 0.5, 2, 0.0, 20)  # a full purse: every cushion at its ceiling, so only the threat terms differ
    e_b, e_c = odds({"risk": 1}, args=low), odds({"risk": -1}, args=low)
    ok["trait_risk_scales_threat_terms"] = e_b["pct"] - odds({"risk": 0}, args=low)["pct"] > 0 and e_c["pct"] < odds({"risk": 0}, args=low)["pct"]
    ok["trait_risk_cushion_is_against_the_reserve"] = odds({"risk": -1}, args=mid)["personal_cushion"] < odds({"risk": 0}, args=mid)["personal_cushion"] < odds({"risk": 1}, args=mid)["personal_cushion"]
    ok["trait_communality_scales_obligation_only"] = (
        odds({"communality": 1})["pct"] < odds({"communality": 0})["pct"] < odds({"communality": -1})["pct"]
        and abs((odds({"communality": 0})["pct"] - odds({"communality": 1})["pct"]) - s_["weights"]["affinity_obligation"] * 0.5 * t_["communality"]["obligation_k"]) < 1e-9
        and odds({"communality": 1})["pool_surplus"] == odds({"communality": -1})["pool_surplus"]
        and abs(odds({"communality": 1}, args=(10, 0.0, 0.5, 2, 0.0, 2))["pct"] - odds({"communality": -1}, args=(10, 0.0, 0.5, 2, 0.0, 2))["pct"]) < 1e-9)  # no bond, no duty to scale
    ok["trait_persistence_adds_pressure"] = odds({"persistence": 1})["pct"] > odds({"persistence": 0})["pct"] > odds({"persistence": -1})["pct"]
    # thrift: the hard gate is unchanged, the hesitation is soft and relative to nobody
    cost = T["arc_payment"]["arc_need_cost"]
    pay = lambda thrift, prov: er.payment_odds(prov, cost, 0.0, thrift, T["arc_payment"], s_, t_)
    ok["trait_thrift_hesitates_below_keep_level"] = pay(1, cost + 1)["pct"] < pay(0, cost + 1)["pct"] < pay(-1, cost + 1)["pct"] and pay(1, cost + 1)["hesitation"] > 0
    ok["trait_thrift_none_when_flush"] = pay(1, cost + 4 * eat)["hesitation"] == 0 and pay(1, cost + 4 * eat)["pct"] == pay(0, cost + 4 * eat)["pct"]
    # the real gate (scenario_probes stubbed the module's), loaded fresh from the scratch copy
    from importlib import util as _iu
    spec = _iu.spec_from_file_location("spl_real", S / "simulate_pass_lib.py")
    real = _iu.module_from_spec(spec); spec.loader.exec_module(real)

    def gate(thrift, prov):
        c_ = load_chars(tmp)["probe_q1"]
        c_.update(provisions=prov, temperament={"risk": 0, "thrift": thrift, "communality": 0, "persistence": 0}); _write(tmp, "probe_q1", c_)
        return real.arc_payment_gate("probe_q1", "probe_s", c_["arc"])
    g1, g0 = gate(1, cost + 1), gate(0, cost + 1)
    ok["trait_thrift_hard_gate_unchanged"] = gate(1, cost - 0.5)["reason"] == "cannot_afford" and gate(-1, cost - 0.5)["reason"] == "cannot_afford"
    gs = gate(-1, cost + 1)
    ok["trait_thrift_shown_in_gate"] = g1["odds_used"] < g0["odds_used"] < gs["odds_used"] and g1["hesitation"] > g0["hesitation"] > 0 and gs["hesitation"] == 0
    detail["gate"] = {"saver": [g1["odds_used"], g1["hesitation"]], "middle": [g0["odds_used"], g0["hesitation"]], "spender": [gs["odds_used"], gs["hesitation"]]}

    # ---- trends respond -----------------------------------------------------------------------------------
    win = lambda pcs, ps=None: [{"pc": pc, "p": (ps[i] if ps else 2), "e": 15} for i, pc in enumerate(pcs)]
    flat, fall, rise = win([3, 3, 3, 3, 3]), win([5, 4, 3, 2, 1]), win([1, 2, 3, 4, 5])
    n_, bold = {}, {"risk": 1}
    ok["trend_decline_pushes_to_work"] = odds(n_, fall)["pct"] < odds(n_, flat)["pct"] and odds(n_, fall)["trend"] < 0
    ok["trend_rise_no_pull_unless_bold"] = abs(odds(n_, rise)["pct"] - odds(n_, flat)["pct"]) < 1e-9 and odds(bold, rise)["pct"] > odds(bold, flat)["pct"]
    mild, calm, mild_args = win([3.5, 3.25, 3, 2.75, 2.5]), win([3] * 5), (10, 0.0, 0.5, 2, 0.0, 3)  # a fall of one unit: rate -0.25, no clamps in play
    drop = lambda r: odds({"risk": r}, calm, mild_args)["pct"] - odds({"risk": r}, mild, mild_args)["pct"]
    ok["trend_cautious_feel_declines_more"] = drop(1) < drop(0) < drop(-1) and drop(1) > 0
    dropping = win([3] * 5, [6, 5, 4, 3, 2])
    ok["trend_thrift_scales_purse_decline"] = (odds({"thrift": 1}, dropping)["pct"] < odds({"thrift": 0}, dropping)["pct"] < odds({"thrift": -1}, dropping)["pct"]) and odds({"thrift": 0}, dropping)["personal_trend"] < 0
    # window length: bold short, cautious long, whole observations; a short history is used as it is
    ok["trend_window_by_trait"] = (tm.pool_window(1, t_), tm.pool_window(0, t_), tm.pool_window(-1, t_)) == (t_["recent_window_min"], round((t_["recent_window_min"] + t_["recent_window_max"]) / 2), t_["recent_window_max"]) and \
        (tm.personal_window(-1, t_), tm.personal_window(1, t_)) == (t_["recent_window_min"], t_["recent_window_max"])
    spike = win([3, 3, 3, 3, 3, 3, 1, 1])
    pr_bold, _ = tm.rates(spike, 4, tm.pool_window(1, t_), 5)
    pr_cautious, _ = tm.rates(spike, 4, tm.pool_window(-1, t_), 5)
    ok["trend_short_window_forgets_long_remembers"] = pr_bold == 0 and pr_cautious < 0
    few = win([3, 1, 1])
    ok["trend_few_observations_use_what_exists"] = tm.rates(few, 4, 8, 8)[0] == tm.rates(few, 4, 3, 3)[0] < 0 and tm.rates(few[:1], 4, 8, 8) == (None, None)
    # no window: the old checkpoint term, untouched
    ok["trend_no_window_is_checkpoint_term"] = abs(odds(n_, None, (10, 0.5, 0.5, 2, -1.0, 2))["pct"] - odds(n_, win([3]), (10, 0.5, 0.5, 2, -1.0, 2))["pct"]) < 1e-9 and odds(n_, None, (10, 0.5, 0.5, 2, -1.0, 2))["trend"] < 0

    # ---- the new scale definitions (2026-10-17, no neutral centre) -----------------------------------------
    # replaces the old guarantee that trait 0 was the pre-temperament roll
    risk_cfg, thrift_cfg = t_["risk"], t_["thrift"]
    mc = risk_cfg["margin_meals_cautious"]  # the cautious end of the margin, whatever the knob says (0 meals is the bold end)
    ok["scale_risk_margin_runs_from_0_to_the_cautious_knob"] = (tm.margin_meals(1, risk_cfg), tm.margin_meals(-1, risk_cfg)) == (risk_cfg["margin_meals_bold"], mc) and risk_cfg["margin_meals_bold"] == 0 and \
        tm.reserve_wanted(1, cost, eat, risk_cfg) == cost and tm.reserve_wanted(-1, cost, eat, risk_cfg) == cost + mc * eat
    thr = s_["provides_provisions_threshold"]
    cush_scale = t_["cushion_scale_meals"] * eat if t_.get("cushion_scale_meals") else thr  # the cushion's own scale (2026-10-17 calibration), else the old threshold
    clamp1 = lambda x: max(-1.0, min(1.0, x))
    ok["scale_cushion_computed_against_that_margin"] = all(
        abs(rs.arc_odds(s_, 10, 0.5, 0.5, 2, 0.0, prov, traits={"risk": r}, t=t_)["personal_cushion"] - clamp1((prov - (cost + tm.margin_meals(r, risk_cfg) * eat)) / cush_scale)) < 1e-9
        for r in (-1, -0.4, 0, 0.7, 1) for prov in (0, 3, 6, 8, 13, 20))
    ok["scale_cushion_not_pinned_for_ordinary_holdings"] = all(  # holdings of 1 to 9 units, the range real characters have: the term is strictly between its limits for most (risk, holdings) pairs
        sum(-1.0 < rs.arc_odds(s_, 10, 0.5, 0.5, 2, 0.0, prov, traits={"risk": r}, t=t_)["personal_cushion"] < 1.0 for prov in range(1, 10)) >= 6 for r in (-1, -0.5, 0, 0.5, 1))
    ok["scale_keep_level_runs_0_to_3_meals"] = (tm.keep_meals(-1, thrift_cfg), tm.keep_meals(1, thrift_cfg)) == (0, 3)
    ok["scale_hesitation_not_relative_to_a_neutral_payer"] = pay(0, cost)["hesitation"] == thrift_cfg["hesitation_per_meal"] * tm.keep_meals(0, thrift_cfg) and \
        pay(-1, cost)["hesitation"] == 0 and pay(1, cost)["hesitation"] == thrift_cfg["hesitation_per_meal"] * 3
    ok["scale_pool_level_is_a_world_constant"] = len({rs.arc_odds(s_, 10, 0.5, 0.5, 3, 0.0, 2, traits={k: v}, t=t_)["pool_surplus"] for k in tm.TRAITS for v in (-1, 0, 1)}) == 1
    ok["scale_old_data_reads_zero_and_works"] = tm.traits_of({}) == tm.traits_of({"temperament": None}) == {k: 0.0 for k in tm.TRAITS} and tm.words({}, .4) == "" and \
        abs(rs.arc_odds(s_, *base, traits=None, recent=None, t=t_)["pct"] - rs.arc_odds(s_, *base, traits={"risk": 0}, recent=None, t=t_)["pct"]) < 1e-9

    # ---- persistence retries the failed destination -----------------------------------------------------
    opts = [{"location": "A", "weight": 2.0}, {"location": "B", "weight": 2.0}]
    r_ = {"need": "n", "place": "A"}; pc_ = t_["persistence"]
    got = {p: tm.retry_adjust(opts, r_, "n", p, pc_)[0]["weight"] for p in (1, 0, -1)}
    ok["retry_persistent_pulled_restless_pushed"] = got[1] > got[0] == 2.0 > got[-1] > 0 and tm.retry_adjust(opts, r_, "other", 1, pc_) == opts
    detail["temperament"] = {"retry_weights_A": got, "windows_pool_by_risk": [tm.pool_window(x, t_) for x in (-1, 0, 1)], "windows_purse_by_thrift": [tm.personal_window(x, t_) for x in (-1, 0, 1)]}
    return ok


def decision_checks(tmp, lib, S, home_ctx, shop_ctx, need, detail):
    """The author's answers of 2026-10-17, through the real code, no model: local_* (a need available at the
    character's own place goes through the arrival pipeline), reflection_* (a one-person scene for
    arrived_empty, dispatched by the driver with a stub enacter, and for nothing else), cultural_* (a child
    born after a completion has its parents' completion tales), roadbirth_* (no births on roads), nodefault_*
    (everybody has a temperament). The bequest tax is in scenario_probes (bequest_*, estate_*); the scales
    are in temperament_checks (scale_*)."""
    ok = {}
    T = importlib.import_module("tuning").load()
    enc_path = tmp / "_lore" / "encodings.json"
    lifespans_path = tmp / "_lore" / "characters" / "lifespans.json"

    def add_lifespans(*keys):
        ls = json.loads(lifespans_path.read_text(encoding="utf-8"))
        for k in keys:
            ls["lifespans"][k] = {"span": 99, "range": "30-60"}
        lifespans_path.write_text(json.dumps(ls, indent=2), encoding="utf-8")

    # ---- a need available at home (audit F2) -------------------------------------------------------------
    shop = [{"location": "ProbeHome", "context": shop_ctx, "weight": 100, "routine_actions": "probe"}]
    home = [{"location": "ProbeHome", "context": home_ctx, "weight": 100, "routine_actions": "probe"}]
    arc = {"about": ["concept: probe_l"], "needs": [need], "context": home_ctx, "premise": "Probe wants a thing at hand.", "resolution": "ongoing", "history": [], "turns": 0}
    _write(tmp, "probe_l1", _blank("Probe L One", "ProbeHome", routines=home, arc=arc, provisions=8))
    _write(tmp, "probe_l2", _blank("Probe L Two", "ProbeHome", routines=shop))
    add_lifespans("probe_l1", "probe_l2")
    lib.roll_survival = lambda key, home_: {"choice": "arc"}
    lib.roll_meetable = lambda candidates, favor=None: {"met": True, "chosen": "probe_l2", "odds_used": 100}
    lib.arc_payment_gate = lambda p1, p2, arc_: {"motivated": True, "reason": None, "odds_used": 100, "cost": 0}
    lib.roll_contested = lambda strength=0, quality=0: False
    lib.check_arc_alignment = lambda about, needs, peer: {"gate": "hit", "inclined": "help", "matched_about": []}
    lib.roll_arc_outcome = lambda inclined, contested=False: "advance"
    (tmp / ".simulate_rng_state.json").write_text(json.dumps({"rng_seed": 123, "draw_counter": 0}))
    r = lib.run_pass_mechanics("probe_l1", 800)
    pu = r.get("pursuit") or {}
    after = load_chars(tmp)["probe_l1"]
    ok["local_runs_the_arrival_pipeline"] = pu.get("stage") == "met_paid" and pu.get("local") is True and r["participant_2"] == "probe_l2" and r["scene"] == "pair" and r["travel"] is None
    ok["local_advances_the_arc"] = r["arc"]["outcome"] == "advance" and len(after["arc"]["history"]) == 1 and after["location"] == "ProbeHome"
    ok["local_stage_name_retired"] = "local_satisfied" not in lib.PURSUIT_STAGES
    detail["local"] = {"stage": pu.get("stage"), "local": pu.get("local"), "outcome": r["arc"]["outcome"]}
    lib.roll_meetable = lambda candidates, favor=None: {"met": False, "chosen": None, "odds_used": 10}
    r2 = lib.run_pass_mechanics("probe_l1", 801)
    ok["local_nobody_useful_is_arrived_nobody"] = (r2["pursuit"] or {}).get("stage") == "arrived_nobody" and r2["pursuit"]["local"] is True and r2["scene"] == "pair" and r2["arc"]["outcome"] is None
    ok["local_failure_leaves_no_retry_memory"] = "failed_destination" not in load_chars(tmp)["probe_l1"]
    # alone: the only supplier is p1's own routine at a place nobody else lives
    olone = [{"location": "ProbeLone", "context": shop_ctx, "weight": 100, "routine_actions": "probe"}]
    enc = json.loads(enc_path.read_text(encoding="utf-8"))
    enc["locations"].append({"id": "ProbeLone", "names": ["ProbeLone"], "description": "A quiet stretch of nothing in particular.", "sources": []})
    enc_path.write_text(json.dumps(enc, indent=1, ensure_ascii=False), encoding="utf-8")
    arc_o = {**arc, "about": ["concept: probe_o"], "premise": "Probe wants to be left alone with a thing."}
    _write(tmp, "probe_o1", _blank("Probe Lone", "ProbeLone", routines=olone, arc=arc_o, provisions=8, temperament={"risk": 0.5, "thrift": -0.5, "communality": 0.1, "persistence": 0.9}))
    add_lifespans("probe_o1")
    r3 = lib.run_pass_mechanics("probe_o1", 802)
    ok["local_nobody_at_all_is_arrived_empty"] = (r3["pursuit"] or {}).get("stage") == "arrived_empty" and r3["pursuit"]["local"] is True and r3["scene"] == "solo" and r3["participant_2"] is None

    # ---- a reflection scene (arrived_empty) --------------------------------------------------------------
    pp = importlib.import_module("pass_prep")
    eo = importlib.import_module("enact_via_ollama")
    drv = importlib.import_module("simulate_driver")
    hz = {"probe_o1": {"band": "early", "lived": 0, "ending": False}}
    prep = pp.enacter_input(r3, hz)
    ok["reflection_brief_has_one_participant"] = list(prep["characters"]) == ["probe_o1"] and list(prep["horizon_pre"]) == ["probe_o1"] and prep["brief"]["participant_2"] is None and prep["brief"]["scene"] == "solo" \
        and prep["place"] is not None and prep["characters"]["probe_o1"].get("knowledge") is not None and "temperament" in prep["characters"]["probe_o1"] and "routine" in prep["characters"]["probe_o1"]
    stub = {"scene": [{"speaker": "Probe Lone", "line": "Quiet, here."}, {"speaker": "Probe Lone", "line": "I came for something and found the wind."}],
            "hearsay": {"location": "ProbeLone", "summary": "Probe Lone alone at ProbeLone.", "claims": []},
            "participants": {"probe_o1": {"experience": ["Stood a while at ProbeLone, thinking of the thing they came for."], "grounded_experience": [], "cost_ledger": [], "criterion_move": None}}}
    ok["reflection_reply_validates"] = eo.validate_reply(eo.clean_reply(json.loads(json.dumps(stub))), ["probe_o1"], prep) == []
    two = json.loads(json.dumps(stub)); two["scene"].append({"speaker": "Somebody Else", "line": "Hello?"})
    extra = json.loads(json.dumps(stub)); extra["participants"]["probe_l2"] = extra["participants"]["probe_o1"]
    ok["reflection_refuses_a_second_speaker_or_participant"] = bool(eo.validate_reply(two, ["probe_o1"], prep)) and bool(eo.validate_reply(extra, ["probe_o1"], prep))
    hs = tmp / ".h_empty.json"
    hs.write_text(json.dumps({"participants": ["Probe A", "Probe B"], "location": "x", "summary": "s", "claims": []}))
    bad = subprocess.run([sys.executable, str(S / "record_hearsay.py"), "--json-file", str(hs)], capture_output=True, text=True, cwd=tmp)
    ok["reflection_empty_claims_only_for_one_participant"] = bad.returncode != 0 and "non-empty" in (bad.stderr + bad.stdout)
    hs.unlink()

    # the driver, end to end, with the model stubbed: p1 and the enacter's reply are fixed, everything else is the real driver
    from pathlib import Path as _P
    orig_run, calls = drv.run, []

    def fake_run(args, allow_fail=False):
        name = _P(str(args[0])).name
        if name == "simulate_resolve_pair.py":
            return 0, json.dumps({"participant_1": fake_run.p1}) + "\n", ""
        if name == "pass_prep.py":
            return 0, json.dumps(fake_run.prep), ""
        if name == "enact_via_ollama.py":
            calls.append(fake_run.p1)
            out = args[args.index("--out") + 1]
            _P(str(out)).write_text(json.dumps({"attempts": 1, "problems": [], "model": "stub", "reply": fake_run.reply}), encoding="utf-8")
            return 0, "", ""
        return orig_run(args, allow_fail)
    drv.run = fake_run
    try:
        fake_run.p1, fake_run.prep, fake_run.reply = "probe_o1", prep, json.loads(json.dumps(stub))
        (tmp / ".simulate_pass_brief.json").write_text(json.dumps(r3), encoding="utf-8")
        lived_before = load_chars(tmp)["probe_o1"]["life"]["lived"]
        state = {"pool": ["probe_o1", "probe_l1", "probe_l2"], "pending_children": [], "next_pass": 803}
        res = drv.do_one_pass(state, 803)
        enc2 = json.loads(enc_path.read_text(encoding="utf-8"))
        entry = next((h for h in enc2["hearsay"]["entries"] if h["participants"] == ["Probe Lone"]), None)
        scene_file = (tmp / "_npcs" / "scenes" / f"{entry['id']}.md") if entry else None
        o1 = load_chars(tmp)["probe_o1"]
        ok["reflection_dispatched_with_one_character"] = calls == ["probe_o1"] and res["status"] == "ok" and res["p2"] is None and entry is not None and entry["claims"] == []
        ok["reflection_scene_file_written"] = bool(scene_file and scene_file.exists() and "reflection" in scene_file.read_text(encoding="utf-8") and "Probe Lone: Quiet, here." in scene_file.read_text(encoding="utf-8"))
        ok["reflection_records_experience_and_life"] = any("Stood a while" in (e if isinstance(e, str) else e.get("text", "")) for e in o1["knowledge"]["experience"]) and o1["life"]["lived"] == lived_before + 1
        ok["reflection_no_partner_no_arc_outcome"] = not o1.get("partners") and prep["brief"]["arc"]["outcome"] is None and not prep["brief"]["motivated"]
        # an ordinary work pass, a no_target pass and an en_route pass are NOT dispatched
        lib.roll_survival = lambda key, home_: {"choice": "work"}
        rw = lib.run_pass_mechanics("probe_l2", 804)
        calls.clear()
        fake_run.p1, fake_run.prep = "probe_l2", pp.enacter_input(rw, {"probe_l2": {"band": "early", "lived": 0, "ending": False}})
        (tmp / ".simulate_pass_brief.json").write_text(json.dumps(rw), encoding="utf-8")
        drv.do_one_pass(state, 804)
        ok["reflection_not_extended_to_work_passes"] = rw.get("scene") is None and calls == []
        detail["reflection"] = {"hearsay_id": entry and entry["id"], "dispatches": 1, "work_pass_dispatches": len(calls)}
    finally:
        drv.run = orig_run

    # ---- children born after a completion (cultural capital) ---------------------------------------------
    ac = importlib.import_module("arc_completion")
    cc_arc = {"about": ["concept: probe_cc"], "needs": [need], "context": home_ctx, "premise": "Probe CC wants the first thing.", "resolution": "complete",
              "history": [{"pass": 1, "outcome": "advance"}] * 3, "turns": 12}
    _write(tmp, "probe_cc", _blank("Probe Cee", "ProbeHome", provisions=2, arc=cc_arc, routines=home))
    _write(tmp, "probe_cd", _blank("Probe Dee", "ProbeHome", routines=home))
    add_lifespans("probe_cc", "probe_cd")
    first = ac.complete("probe_cc", 900)
    c_ = load_chars(tmp)["probe_cc"]
    c_["arc"] = {**cc_arc, "about": ["concept: probe_cc2"], "premise": "Probe CC wants the second thing.", "resolution": "ongoing", "history": [], "turns": 0}  # re-authored: arc.completion is gone
    c_["arc"].pop("completion", None)
    _write(tmp, "probe_cc", c_)
    c_["arc"].update(resolution="complete", history=cc_arc["history"], turns=5)
    _write(tmp, "probe_cc", c_)
    second = ac.complete("probe_cc", 901)
    ok["cultural_completer_keeps_every_completion"] = load_chars(tmp)["probe_cc"].get("completed_tales") == [first["tale_id"], second["tale_id"]]
    sh([S / "generate_offspring.py", "--parent-a", "probe_cc", "--parent-b", "probe_cd", "--name", "Probe Heir", "--pass-number", 905, "--seed", 21], tmp)
    heir = load_chars(tmp)["probe_heir"]
    items = heir["knowledge"]["education"]["items"]
    ok["cultural_child_born_after_gets_both_tales"] = all(f"tale: {t}" in items for t in (first["tale_id"], second["tale_id"])) and len(items) == len(set(items))
    _write(tmp, "probe_ce", _blank("Probe Eee", "ProbeHome", routines=home))
    add_lifespans("probe_ce")
    sh([S / "generate_offspring.py", "--parent-a", "probe_cd", "--parent-b", "probe_ce", "--name", "Probe Other", "--pass-number", 906, "--seed", 22], tmp)
    other = load_chars(tmp)["probe_other"]
    ok["cultural_no_completion_no_guaranteed_tale"] = not any(i.startswith("tale: arc_complete_probe_c") for i in other["knowledge"]["education"]["items"] if i not in set(load_chars(tmp)["probe_cd"]["knowledge"]["education"]["items"]))
    detail["cultural"] = {"tales": [first["tale_id"], second["tale_id"]], "heir_items": len(items)}

    # ---- no births on roads -------------------------------------------------------------------------------
    rp = importlib.import_module("simulate_pass_reproduction")
    road = "road:ProbeHome--ProbeShop"
    for k in ("probe_rr1", "probe_rr2"):
        _write(tmp, k, _blank(k.title().replace("_", " "), "ProbeHome", routines=home))
    add_lifespans("probe_rr1", "probe_rr2")
    for a_, b_ in (("probe_rr1", "probe_rr2"), ("probe_rr2", "probe_rr1")):
        c_ = load_chars(tmp)[a_]; c_["partners"] = {b_: lib.PARTNER_THRESHOLD + 3}; _write(tmp, a_, c_)
    audit_log = tmp / ".simulate_draw_audit.jsonl"
    lines_before = len(audit_log.read_text(encoding="utf-8").splitlines()) if audit_log.exists() else 0
    c_ = load_chars(tmp)["probe_rr1"]; c_["location"] = road; _write(tmp, "probe_rr1", c_)
    on_road = rp.check_and_roll("probe_rr1", "probe_rr2", 910)
    lines_after = len(audit_log.read_text(encoding="utf-8").splitlines()) if audit_log.exists() else 0
    ok["roadbirth_not_rolled_on_a_road"] = on_road["eligible"] is False and on_road["reproduces"] is False and on_road["blocked"] == "road" and lines_after == lines_before
    c_ = load_chars(tmp)["probe_rr1"]; c_["location"] = "ProbeHome"; _write(tmp, "probe_rr1", c_)
    at_place = rp.check_and_roll("probe_rr1", "probe_rr2", 911)
    lines_place = len(audit_log.read_text(encoding="utf-8").splitlines()) if audit_log.exists() else 0
    ok["roadbirth_still_rolls_at_a_place"] = at_place["eligible"] is True and at_place["blocked"] is None and lines_place > lines_after
    out_cli = subprocess.run([sys.executable, str(S / "simulate_pass_reproduction.py"), "--p1", "probe_rr1", "--p2", "probe_rr2", "--pass-number", "912"], capture_output=True, text=True, cwd=tmp).stdout
    ok["roadbirth_cli_runs"] = "eligible:" in out_cli

    # ---- everybody has a temperament ---------------------------------------------------------------------
    template = json.loads((tmp / "_lore" / "characters" / "_template.json").read_text(encoding="utf-8"))
    ok["nodefault_template_ships_null"] = template.get("temperament") is None
    ok["nodefault_child_gets_all_four"] = set(heir.get("temperament") or {}) == {"risk", "thrift", "communality", "persistence"} and set(other.get("temperament") or {}) == {"risk", "thrift", "communality", "persistence"}
    _write(tmp, "probe_g1", _blank("Probe Gee", "ProbeHome", routines=home))
    _write(tmp, "probe_g2", _blank("Probe Gee Two", "ProbeHome", routines=home, temperament={"risk": 0, "thrift": 0, "communality": 0, "persistence": 0}))
    add_lifespans("probe_g1", "probe_g2")
    sh([S / "assign_temperament.py", "--root", tmp, "--key", "probe_g1", "--seed", 4, "--apply"], tmp)
    tg1 = load_chars(tmp)["probe_g1"].get("temperament") or {}
    ok["nodefault_character_skill_can_draw_one"] = set(tg1) == {"risk", "thrift", "communality", "persistence"} and any(tg1.values())
    # /generate always draws for anyone without; --keep-neutral is accepted and changes nothing
    _write(tmp, "probe_g3", _blank("Probe Gee Three", "ProbeHome", routines=home))
    _write(tmp, "probe_g4", _blank("Probe Gee Four", "ProbeHome", routines=home))
    add_lifespans("probe_g3", "probe_g4")
    for g_ in (["init", "-q"], ["-c", "user.name=audit", "-c", "user.email=audit@example.invalid", "commit", "--allow-empty", "-q", "-m", "scratch"]):
        subprocess.run(["git", *g_], cwd=tmp, capture_output=True)  # the run manifest records a commit; the scratch copy has none
    gen = subprocess.run([sys.executable, str(S / "simulate_generate_population.py"), "--pool", "probe_g3", "probe_g4", "--passes", "1", "--seed", "5", "--keep-neutral"], capture_output=True, text=True, cwd=tmp)
    got = load_chars(tmp)
    ok["nodefault_generate_draws_even_with_keep_neutral"] = gen.returncode == 0 and all(set(got[k].get("temperament") or {}) == {"risk", "thrift", "communality", "persistence"} for k in ("probe_g3", "probe_g4")) and "no-op" in gen.stdout
    if gen.returncode != 0:
        detail["generate_error"] = (gen.stderr or gen.stdout)[-600:]

    # ---- road work is rest (the author's decision 2026-10-17, option A) -------------------------------------
    # a traveller standing on a road whose work-or-arc roll comes up "work": no pay, no pool, base cost and a
    # meal from their own provisions, destination kept, still on the node, still findable there
    s_ = T["survival"]
    road = "road:ProbeHome--ProbeShop"
    journey_ = {"need": need, "target": "ProbeShop", "origin": "ProbeHome", "since_pass": 1}
    trav_arc = {"about": ["concept: probe_t"], "needs": [need], "context": home_ctx, "premise": "Probe walks toward a thing.", "resolution": "ongoing", "history": [], "turns": 0}
    _write(tmp, "probe_t1", _blank("Probe Tee", road, routines=home, arc=trav_arc, provisions=6, energy=10, pursuit=dict(journey_)))
    add_lifespans("probe_t1")
    lib.roll_survival = lambda key, home_: {"choice": "work"}
    pools_path = tmp / "_lore" / "provisions.json"
    rr = lib.run_pass_mechanics("probe_t1", 920)
    t1 = load_chars(tmp)["probe_t1"]
    pools_after = json.loads(pools_path.read_text(encoding="utf-8")).get("pools", {}) if pools_path.exists() else {}
    ok["roadrest_choice_is_rest"] = rr["survival"]["probe_t1"]["choice"] == "rest" and rr["scene"] is None and rr["participant_2"] is None
    ok["roadrest_no_pay_only_the_meal"] = t1["provisions"] == 6 - s_["eat_amount"]  # the whole meal from their own provisions (no pool on a road), nothing earned
    ok["roadrest_energy_is_base_cost_plus_meal_no_arc_cost"] = t1["energy"] == 10 - s_["base_cost"] + s_["eat_amount"]
    ok["roadrest_no_pool_exists_or_is_fed"] = road not in pools_after
    ok["roadrest_destination_kept_untouched"] = t1.get("pursuit") == journey_
    ok["roadrest_stays_on_the_node"] = t1["location"] == road and rr["location"] == road
    others = lib.load_all_characters()
    ok["roadrest_findable_by_another_traveller"] = lib.present_on_road(road, others, exclude="someone_else") == ["probe_t1"]
    # at a PLACE mid-journey a work roll is still work in place (pays, journey kept): only a road is rest
    c_ = load_chars(tmp)["probe_t1"]; c_.update(location="ProbeHome", provisions=2, energy=10); _write(tmp, "probe_t1", c_)
    wk = lib.run_pass_mechanics("probe_t1", 921)
    t1b = load_chars(tmp)["probe_t1"]
    ok["roadrest_a_place_mid_journey_is_still_work"] = wk["survival"]["probe_t1"]["choice"] == "work" and t1b["provisions"] > 2 and t1b.get("pursuit") == journey_ and t1b["location"] == "ProbeHome"
    # a character left on a road with NO journey (arc finished, a dead end) is not parked there: their work roll
    # sends them to a routine location as before (logged in OPEN_QUESTIONS.md)
    c_ = load_chars(tmp)["probe_t1"]; c_.update(location=road, provisions=6, energy=10); c_.pop("pursuit", None); _write(tmp, "probe_t1", c_)
    st = lib.run_pass_mechanics("probe_t1", 922)
    t1c = load_chars(tmp)["probe_t1"]
    ok["roadrest_stranded_without_a_journey_goes_to_a_routine_place"] = st["survival"]["probe_t1"]["choice"] == "work" and t1c["location"] == "ProbeHome" and t1c["provisions"] > 6 - s_["eat_amount"]
    detail["roadrest"] = {"choice": rr["survival"]["probe_t1"]["choice"], "provisions_6_to": t1["provisions"], "energy_10_to": t1["energy"], "location": t1["location"]}

    # ---- the Ollama context window (correctness, 2026-10-17) ----------------------------------------------------
    eo = importlib.import_module("enact_via_ollama")
    ecfg = eo.enacter_cfg()
    ok["ctx_knob_in_tuning_and_default_12288"] = (T.get("enacter") or {}).get("num_ctx") == 12288 and ecfg["num_ctx"] == 12288
    sent = {}

    class _Resp:
        def __init__(self, body): self.body = body
        def read(self): return json.dumps(self.body).encode()
        def __enter__(self): return self
        def __exit__(self, *a): return False

    def fake_urlopen_for(body):
        def fake(req, timeout=0):
            sent["payload"] = json.loads(req.data.decode())
            return _Resp(body)
        return fake
    good_body = {"message": {"content": json.dumps({"scene": [], "hearsay": {}, "participants": {}})}, "prompt_eval_count": 7000, "eval_count": 900}
    real_urlopen = eo.urllib.request.urlopen
    try:
        eo.urllib.request.urlopen = fake_urlopen_for(good_body)
        eo.call_ollama("http://x", "m", "sys " * 100, "user " * 100, 0.5)
        ok["ctx_num_ctx_sent_in_options"] = sent["payload"]["options"].get("num_ctx") == ecfg["num_ctx"] and "temperature" in sent["payload"]["options"]
        eo.call_ollama("http://x", "m", "sys", "user", 0.5, num_ctx=16384)
        ok["ctx_flag_overrides_the_knob"] = sent["payload"]["options"]["num_ctx"] == 16384
        sent.clear()
        try:
            eo.call_ollama("http://x", "m", "a" * 40000, "b" * 20000, 0.5)  # ~17k tokens by the estimate
            pre = False
        except SystemExit as e:
            pre = "will not fit" in str(e)
        ok["ctx_preflight_refuses_a_prompt_that_cannot_fit_and_sends_nothing"] = pre and not sent
        for label, body in (("at", {**good_body, "prompt_eval_count": ecfg["num_ctx"]}), ("under_margin", {**good_body, "prompt_eval_count": ecfg["num_ctx"] - ecfg["truncation_margin"]})):
            eo.urllib.request.urlopen = fake_urlopen_for(body)
            try:
                eo.call_ollama("http://x", "m", "sys", "user", 0.5)
                refused = False
            except SystemExit as e:
                refused = "TRUNCATED" in str(e)
            ok[f"ctx_truncated_reply_refused_{label}"] = refused
        eo.urllib.request.urlopen = fake_urlopen_for({**good_body, "prompt_eval_count": 9000, "eval_count": ecfg["num_ctx"] - 9000})
        try:
            eo.call_ollama("http://x", "m", "sys", "user", 0.5)
            refused = False
        except SystemExit as e:
            refused = "ran out" in str(e)
        ok["ctx_reply_that_filled_the_window_refused"] = refused
        eo.urllib.request.urlopen = fake_urlopen_for({**good_body, "prompt_eval_count": ecfg["num_ctx"] - ecfg["truncation_margin"] - 10, "eval_count": 1})
        ok["ctx_just_under_the_margin_is_accepted"] = eo.call_ollama("http://x", "m", "sys", "user", 0.5) is not None
    finally:
        eo.urllib.request.urlopen = real_urlopen
    help_ = subprocess.run([sys.executable, str(S / "enact_via_ollama.py"), "--help"], capture_output=True, text=True, cwd=tmp).stdout
    ok["ctx_cli_has_num_ctx_flag"] = "--num-ctx" in help_
    # a real pair-scene brief and the preamble must fit with room to spare at the default window
    pre_tokens = eo.estimate_tokens(eo.load_preamble(), chars_per_token=ecfg["chars_per_token"])
    ok["ctx_preamble_alone_is_well_under_the_window"] = pre_tokens < ecfg["num_ctx"] // 2
    detail["ollama_ctx"] = {"num_ctx": ecfg["num_ctx"], "preamble_chars": len(eo.load_preamble()), "preamble_tokens_est": pre_tokens}
    return ok


def run_end_stats(tmp, dead_before):
    """What the run left behind: circles by kind, completions, dead characters still holding food."""
    chars = load_chars(tmp)
    kinds = collections.Counter()
    for c in chars.values():
        circle = c.get("social_circle")
        if isinstance(circle, dict):
            kinds.update(circle.values())
    # dead during THIS run and still holding food = an estate that never moved (the corpus's earlier
    # dead predate the rule and are not judged)
    holding = [k for k, c in chars.items() if c.get("life", {}).get("deceased") and k not in dead_before and c.get("provisions", 0) > 0]
    arc_turns = [c["arc"]["turns"] for c in chars.values() if (c.get("arc") or {}).get("turns")]
    return {
        "circle_ties_by_kind": dict(kinds),
        "characters_with_a_circle": sum(1 for c in chars.values() if isinstance(c.get("social_circle"), dict) and c["social_circle"]),
        "dead_holding_provisions": len(holding),
        "ongoing_arc_turns": sorted(arc_turns),
    }


def digest(tmp):
    """sha256 of the draw log with timestamps stripped, of every character file and of encodings.json."""
    out = {}
    log = tmp / ".simulate_draw_audit.jsonl"
    if log.exists():
        lines = []
        for line in log.read_text(encoding="utf-8").splitlines():
            d = json.loads(line)
            d.pop("timestamp", None)
            lines.append(json.dumps(d, sort_keys=True))
        out["draw_log"] = hashlib.sha256("\n".join(lines).encode()).hexdigest()
        out["draw_count"] = len(lines)
    for p in sorted((tmp / "_lore" / "characters").glob("*.json")):
        out["char/" + p.stem] = hashlib.sha256(p.read_bytes()).hexdigest()
    out["encodings"] = hashlib.sha256((tmp / "_lore" / "encodings.json").read_bytes()).hexdigest()
    pj = tmp / "_lore" / "provisions.json"
    if pj.exists():
        out["provisions"] = hashlib.sha256(pj.read_bytes()).hexdigest()
    return out


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
    ap.add_argument("--births", action="store_true", help="a pair that reproduces has a child (stub name), so the birth-time circle writer runs in the loop")
    ap.add_argument("--digest-out", default=None, help="write sha256 digests of the draw log (no timestamps), every character file and encodings.json, for a same-seed identity check")
    ap.add_argument("--json-out", default=None)
    ap.add_argument("--dump", default=None, help="keep the run's end state (characters, pools, draw audit) in this new directory")
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
        dead_before = {k for k, c in load_chars(tmp).items() if c.get('life', {}).get('deceased')}
        run_passes(tmp, a.passes, a.seed, counts, births=a.births)
        counts["conformance_kin_invariant_failures"] = conformance_kin_failures(tmp)
        run_digest = digest(tmp) if a.digest_out else None
        for k_, v_ in run_end_stats(tmp, dead_before).items():
            counts[k_] = v_  # Counter.update would add; these are plain values
        probes, extra = static_probes(tmp, counts, fixture)
        scen = scenario_probes(tmp)
        if a.digest_out:  # the scenario is seeded too, so the world after it is part of the identity check
            Path(a.digest_out).write_text(json.dumps({"after_run": run_digest, "after_scenarios": digest(tmp)}, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        detail = scen.pop("_detail", {})
        extra["scenario"] = {"passed": sorted(k for k, v in scen.items() if v), "failed": sorted(k for k, v in scen.items() if not v), "detail": detail}
        probes["F17"] = counts["pair_scenes_without_circle_tie"] > 0 or any(not scen[k] for k in scen if k.startswith(("birth_", "readers_", "backfill_")))
        probes["F18"] = any(not scen[k] for k in scen if k.startswith(("completion_", "reward_", "turns_", "tale_", "child_", "wider_", "completer_")))
        probes["F19"] = counts["dead_holding_provisions"] > 0 or any(not scen[k] for k in scen if k.startswith("estate_"))
        # 2026-10-17 temperament work: True when the thing is still wrong
        probes["F21"] = any(not scen[k] for k in scen if k.startswith("p2_"))                 # p2 does not eat / cannot starve
        probes["F22"] = any(not scen[k] for k in scen if k.startswith(("trait_", "retry_")))  # a trait does not move the odds as stated
        probes["F23"] = any(not scen[k] for k in scen if k.startswith(("trend_", "window_")))  # trends do not respond
        probes["F24"] = any(not scen[k] for k in scen if k.startswith("scale_"))              # a scale is not the new definition
        # 2026-10-17, the author's answers
        probes["F2"] = any(not scen[k] for k in scen if k.startswith("local_"))
        probes["F25"] = any(not scen[k] for k in scen if k.startswith("reflection_")) or counts["reflection_reproduction_ran"] > 0
        probes["F26"] = any(not scen[k] for k in scen if k.startswith("bequest_"))
        probes["F27"] = any(not scen[k] for k in scen if k.startswith("cultural_"))
        probes["F28"] = any(not scen[k] for k in scen if k.startswith("roadbirth_"))
        probes["F29"] = any(not scen[k] for k in scen if k.startswith("nodefault_"))
        probes["F30"] = any(not scen[k] for k in scen if k.startswith("roadrest_"))   # a work roll on a road is not rest
        probes["F31"] = any(not scen[k] for k in scen if k.startswith("ctx_"))       # the Ollama call can silently truncate its prompt
        result = {"root": str(root), "passes": a.passes, "seed": a.seed, "fixture": a.fixture, "fixture_info": fixture,
                  "observed": dict(counts), "static": extra, "probes": probes}
        if a.baseline:
            result["diff"] = diff(a.baseline, probes)
        text = json.dumps(result, indent=2, ensure_ascii=False, default=list)
        print(text)
        if a.json_out:
            Path(a.json_out).write_text(text + "\n", encoding="utf-8")
        if a.dump:
            d = Path(a.dump)
            shutil.copytree(tmp / "_lore" / "characters", d / "characters")
            for name in (".simulate_draw_audit.jsonl",):
                if (tmp / name).exists():
                    shutil.copy(tmp / name, d / name)
            if (tmp / "_lore" / "provisions.json").exists():
                shutil.copy(tmp / "_lore" / "provisions.json", d / "provisions.json")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()

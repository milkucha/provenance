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
        "F2": "history" not in mech_src.split("if matched_need:")[1].split("# Step 5")[0],
        "F3": dead_cand > 0 or dead_provide_leak,
        "F4": "check_anchor_reference" not in prep_src and "check_anchor_reference" not in mech_src,
        "F5": "derived_from" not in src("enact_via_ollama.py").split("REPLY_SCHEMA")[1].split("def load_preamble")[0],
        "F6": "provides" not in inspect.getsource(lib.candidates_at),
        # RAN since the pursuit redesign: a work roll taken mid-journey must leave the journey alone.
        # None when this run never rolled one.
        "F7": (counts["journey_reset"] > 0) if counts["work_midjourney"] else None,
        "F8": 'add_argument("--p2", required=True' in src("pass_apply.py") and "roll_death_legacy" not in inspect.getsource(importlib.import_module("simulate_driver").apply_solo),
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

    # --- deaths through record_death.py: estate to the living child, and to the pool when childless
    before_c = load_chars(tmp)["probe_c"]["provisions"]
    estate_a = load_chars(tmp)["probe_a"]["provisions"]
    sh([S / "record_death.py", "probe_a", "--seed", "3"], tmp)
    after = load_chars(tmp)
    ok["estate_to_living_child"] = abs(after["probe_c"]["provisions"] - (before_c + estate_a)) < 1e-9 and after["probe_a"]["provisions"] == 0
    pool_mod = importlib.import_module("provisions_lib")
    pool_before = pool_mod.get_provisions("ProbeHome")
    sh([S / "record_death.py", "probe_e", "--seed", "3"], tmp)
    pool_after = json.loads((tmp / "_lore" / "provisions.json").read_text(encoding="utf-8"))["pools"]["ProbeHome"]
    ok["estate_to_pool_without_children"] = abs(pool_after - (pool_before + 4)) < 1e-9 and load_chars(tmp)["probe_e"]["provisions"] == 0
    # two heirs split equally
    _write(tmp, "probe_p", _blank("Probe Papa", "ProbeHome", provisions=5))
    for k in ("probe_k1", "probe_k2"):
        _write(tmp, k, _blank(k.title().replace("_", " "), "ProbeHome", parents=["probe_p"], provisions=0))
    lifespans["lifespans"].update({"probe_p": {"span": 99, "range": "30-60"}})
    (tmp / "_lore" / "characters" / "lifespans.json").write_text(json.dumps(lifespans, indent=2), encoding="utf-8")
    sh([S / "record_death.py", "probe_p", "--seed", "3"], tmp)
    after = load_chars(tmp)
    ok["estate_split_equally"] = after["probe_k1"]["provisions"] == after["probe_k2"]["provisions"] == 2.5

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
    ok["_detail"] = detail
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

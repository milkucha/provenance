"""
Fast-forward many passes of /simulate's extended-mode mechanic with NO scene-writing and NO
subagent per pass - built for `/simulate -generate`, whose whole point is producing a large,
multi-generation starting population quickly rather than a showcase trail of prose. Every
mechanical sub-step of the interactive skill's Step 3 (.claude/skills/simulate/SKILL.md) that's
already backed by a script or plain arithmetic runs here exactly as documented there: pairing,
lead-followup, routine/location rolls, archetype lookup, needs/provides, arc primacy/gate/contested/
outcome, tally+threshold (including transform), partner tracking, reproduction eligibility+roll,
offspring generation, life.lived + death + death-legacy.

Three deliberate scope differences from the interactive skill, all confirmed with the user rather
than assumed:

1. No scene prose, and no /enact Steps 5/5b/6 underneath it (hearsay mutation, criterion shock) -
   this mode's whole reason to exist. Criteria stay exactly as inherited/authored; they get tested
   later in real /enact or interactive /simulate scenes.
2. The two things that genuinely need a model's judgment - a child's blended name, and a freshly
   authored arc's about/needs/archetype/specialization content - are never invented here. Instead
   this script writes a placeholder identity immediately (so the child can exist and participate in
   later passes: reproduce, be visited, die) and queues the real content into `_pending_language.json`
   at the worktree root for a SINGLE batched subagent pass at the very end of the whole run (see
   `.claude/skills/simulate/SKILL.md`'s "-generate" mode, Step 4) - never one dispatch per event.
   The placeholder's SLUG is never renamed later, only the human-facing `name` field and prose that
   quotes it (see `apply_language_layer.py`) - this sidesteps rewriting every cross-file slug
   reference (`parents`, `partners`, `leads`, `lifespans.json`, tale ids) for a cosmetic rename.
3. Step 9's contested-rival mechanic ("a rival only gets named if a character file already exists for
   them") requires inventing a plausible rival identity when none is dictated by the mechanics - that
   is exactly the kind of free content this mode cannot produce without a model. `contested` is still
   rolled and reported for every motivated visit (real bookkeeping, not skipped), but this mode never
   writes the `leads` entry or the attributed rival note that only the "named + hinder" branch
   produces - every contested case here resolves as the ambient/unnamed default instead.

Everything else - pairing, routine/location, needs/provides, the arc gate/outcome/tally machinery,
partner tracking, reproduction, offspring inheritance (including routines, which
`generate_offspring.py` already inherits mechanically from both parents), death, and death-legacy -
runs for real, exactly as it would under a human running the interactive skill by hand.

Every sibling script is invoked by an ABSOLUTE path derived from this script's own `__file__`
(`SCRIPTS_DIR / "<name>.py"`), never a relative one and never dependent on the caller's cwd - this is
what the interactive skill's Step 3 has to defend against by convention (a subagent can mistype or
misresolve a relative path); a single Python process constructing its own sibling paths has no such
failure mode; there is no subagent here to make that mistake, only this file.

Usage:
    py scripts/lore/simulate_generate_population.py --pool khaoe farlis khaasan --passes 60
    py scripts/lore/simulate_generate_population.py --pool khaoe farlis --passes 40 --seed 7
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT = SCRIPTS_DIR.parent.parent
CHAR_DIR = ROOT / "_lore" / "characters"
PENDING_PATH = ROOT / "_pending_language.json"
SNAPSHOT_PATH = ROOT / ".simulate_snapshot.json"
LOG_PATH = ROOT / "GENERATION_LOG.md"

sys.path.insert(0, str(SCRIPTS_DIR))
import tuning  # noqa: E402

T = tuning.load()
PARTNER_THRESHOLD = T["partner_threshold"]
PARENT_COOLDOWN_PASSES = T["parent_cooldown_passes"]
CHILD_COOLDOWN_PASSES = T["child_cooldown_passes"]
LEAD_EXPIRY_PASSES = T["lead_expiry_passes"]
ARC_RESOLUTION_THRESHOLD = T["arc_resolution_threshold"]

ARCHETYPES = json.loads((ROOT / "_lore" / "archetypes.json").read_text(encoding="utf-8"))


# --------------------------------------------------------------------------------------------
# Plumbing: character file I/O, sibling-script invocation, stdout parsing
# --------------------------------------------------------------------------------------------

def load_char(key: str) -> dict:
    path = CHAR_DIR / f"{key}.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_char(key: str, character: dict) -> None:
    path = CHAR_DIR / f"{key}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(character, f, indent=2, ensure_ascii=False)
        f.write("\n")


def call(script_name: str, argv: list) -> str:
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / script_name), *argv],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"{script_name} {argv} failed (exit {result.returncode}):\n{result.stderr}")
    return result.stdout


def kv(stdout: str) -> dict:
    """Parses top-level (non-indented) 'key: value' lines into a dict. Indented lines (e.g. a
    script's per-item '  notified: x' listing) are deliberately excluded - use a dedicated
    line-scraper (see notified_keys()) for those instead."""
    out = {}
    for line in stdout.splitlines():
        if not line or line[0] in " \t":
            continue
        key, sep, value = line.partition(":")
        if sep:
            out[key.strip()] = value.strip()
    return out


def notified_keys(stdout: str) -> list:
    return re.findall(r"^\s+notified:\s+(\S+)", stdout, re.MULTILINE)


# --------------------------------------------------------------------------------------------
# Sibling-script wrappers (one per scripts/lore/*.py this loop calls)
# --------------------------------------------------------------------------------------------

def pick_pair(pool: list) -> tuple:
    d = kv(call("pick_pair.py", pool))
    return d["participant_1"], d["participant_2"]


def roll_lead_followup(leads: list) -> dict:
    return kv(call("roll_lead_followup.py", ["--leads", *leads]))


def roll_routine(routines: list) -> str:
    args = [f"{r['location']}:{r['weight']}" for r in routines]
    return kv(call("roll_routine.py", args))["routine"]


def resolve_location(p1: str, p1_routine: str, p2: str, p2_routine: str) -> dict:
    return kv(call("resolve_location.py", [
        "--p1", p1, "--p1-routine", p1_routine, "--p2", p2, "--p2-routine", p2_routine,
    ]))


def check_needs_provides(needs: list, provides: list) -> dict:
    args = []
    for n in needs:
        args += ["--needs", n]
    for p in provides:
        args += ["--provides", p]
    return kv(call("check_needs_provides.py", args))


def roll_arc_primacy(p1: str, p2: str) -> str:
    return kv(call("roll_arc_primacy.py", ["--p1", p1, "--p2", p2]))["primary"]


def peer_knowledge_items(character: dict, cap: int = 15) -> list:
    items = []
    for entry in character.get("knowledge", {}).get("experience", []):
        if isinstance(entry, dict) and entry.get("about"):
            about = entry["about"]
            tags = about if isinstance(about, list) else [about]
            items.append(f"{entry.get('text', '')}::{','.join(tags)}")
    return items[-cap:]


def check_arc_alignment(arc_about: list, arc_needs: list, peer: dict) -> dict:
    args = []
    for tag in arc_about:
        args += ["--arc-about", tag]
    for tag in arc_needs:
        args += ["--arc-needs", tag]
    criterion = peer.get("criterion", {})
    args += ["--peer-standard", criterion.get("standard", "")]
    args += ["--peer-wasted-life", criterion.get("wasted_life", "")]
    for item in peer_knowledge_items(peer):
        args += ["--peer-knowledge-item", item]
    out = kv(call("check_arc_alignment.py", args))
    out["matched_about"] = [t for t in out.get("matched_about", "").split(",") if t]
    return out


def roll_contested() -> bool:
    return kv(call("roll_contested.py", []))["contested"] == "true"


def roll_arc_outcome(inclined: str) -> str:
    return kv(call("roll_arc_outcome.py", ["--inclined", inclined]))["outcome"]


def record_partner(key: str, other: str) -> None:
    call("record_partner.py", [key, "--with", other])


def roll_reproduction(p1: str, p2: str) -> dict:
    return kv(call("roll_reproduction.py", ["--p1", p1, "--p2", p2]))


def generate_offspring(parent_a: str, parent_b: str, name: str, pass_number: int) -> dict:
    stdout = call("generate_offspring.py", [
        "--parent-a", parent_a, "--parent-b", parent_b, "--name", name, "--pass-number", str(pass_number),
    ])
    born_match = re.search(r"^born: (\S+) \(", stdout, re.MULTILINE)
    eligible_match = re.search(r">=\s*(\d+)", stdout)
    return {
        "slug": born_match.group(1),
        "eligible_pass": int(eligible_match.group(1)),
    }


def horizon(key: str) -> dict:
    return kv(call("horizon.py", [key]))


def record_death(key: str) -> dict:
    stdout = call("record_death.py", [key])
    return {"notified": notified_keys(stdout)}


def roll_death_legacy(candidates: list) -> dict:
    return kv(call("roll_death_legacy.py", ["--candidates", *candidates]))


def update_character_lived(key: str, delta: int = 1) -> None:
    call("update_character.py", [key, "--lived-delta", str(delta)])


# --------------------------------------------------------------------------------------------
# Arc bookkeeping (no script exists for this even in the interactive skill - it's a direct
# character-file edit there too, just done by hand instead of by this function)
# --------------------------------------------------------------------------------------------

def resolve_archetype_for_location(character: dict, location: str) -> str:
    for r in character.get("routines", []):
        if r["location"] == location:
            return r["archetype"]
    raise RuntimeError(f"'{character.get('name')}' has no routine at location '{location}'.")


def tally(history: list) -> int:
    last_transform = -1
    for i, h in enumerate(history):
        if h.get("outcome") == "transform":
            last_transform = i
    relevant = history[last_transform + 1:]
    score = {"advance": 1, "stall": 0, "reverse": -1}
    return sum(score.get(h.get("outcome"), 0) for h in relevant)


# --------------------------------------------------------------------------------------------
# One pass
# --------------------------------------------------------------------------------------------

class State:
    def __init__(self, pool: list):
        self.living = list(dict.fromkeys(pool))
        self.pending_births = []  # (child_slug, eligible_pass)
        self.pending = {"children": [], "arcs": []}
        self.queued_arc_chars = set()
        self.generation = {slug: 0 for slug in pool}
        self.child_counter = 0
        self.log = []


def maybe_admit_children(state: State, pass_number: int) -> None:
    still_pending = []
    for slug, eligible_pass in state.pending_births:
        if pass_number >= eligible_pass:
            state.living.append(slug)
        else:
            still_pending.append((slug, eligible_pass))
    state.pending_births = still_pending


def queue_arc(state: State, key: str, character: dict, reason: str, pass_number: int) -> bool:
    if key in state.queued_arc_chars:
        return False
    state.queued_arc_chars.add(key)
    band = horizon(key)["band"]
    state.pending["arcs"].append({
        "character_slug": key,
        "character_name": character.get("name"),
        "reason": reason,
        "queued_at_pass": pass_number,
        "horizon_band": band,
        "city": character.get("city", ""),
        "backstory": character.get("backstory", ""),
        "criterion": character.get("criterion", {}),
        "routines": character.get("routines", []),
        "prior_arc": character.get("arc") if reason == "reauthor_failed" else None,
    })
    return True


def run_pass(state: State, pass_number: int) -> str:
    notes = []

    p1, p2 = pick_pair(state.living)
    p1_char, p2_char = load_char(p1), load_char(p2)

    # Step 2 - lead override
    forced_visit = False
    leads = p1_char.get("leads", [])
    fresh_leads = [l for l in leads if pass_number - l["created_pass"] < LEAD_EXPIRY_PASSES]
    if len(fresh_leads) != len(leads):
        p1_char["leads"] = fresh_leads
        save_char(p1, p1_char)
    if fresh_leads:
        res = roll_lead_followup([l["target"] for l in fresh_leads])
        if res["followed"] == "true":
            target = res["lead"]
            if target in state.living and target != p1:
                p2 = target
                p2_char = load_char(p2)
                p1_char["leads"] = [l for l in fresh_leads if l["target"] != target]
                save_char(p1, p1_char)
                forced_visit = True
                notes.append(f"{p1} followed a lead to {p2}")

    # Step 3/4 - routine + location
    p2_routine = roll_routine(p2_char["routines"])
    if forced_visit:
        mode, location, home_frame, traveler = "visit", p2_routine, p2, p1
    else:
        p1_routine = roll_routine(p1_char["routines"])
        loc = resolve_location(p1, p1_routine, p2, p2_routine)
        mode, location, home_frame = loc["mode"], loc["location"], loc["home_frame"]
        traveler = loc["traveler"] if loc["traveler"] != "none" else None

    home_frame_char = p1_char if home_frame == p1 else p2_char
    archetype = resolve_archetype_for_location(home_frame_char, location)
    provides = ARCHETYPES[archetype]["provides"]

    # Step 6 - needs/provides (visit only, traveler must have an active arc with needs)
    motivated, contested = False, False
    if mode == "visit" and traveler:
        traveler_char = p1_char if traveler == p1 else p2_char
        t_arc = traveler_char.get("arc")
        if t_arc and t_arc.get("resolution") == "ongoing" and t_arc.get("needs"):
            np_res = check_needs_provides(t_arc["needs"], provides)
            motivated = np_res["match"] == "true"

    # Step 9 - contested (only if motivated). Never names a rival (see module docstring point 3) -
    # rolled and reported, but never writes `leads`/a rival note, since that requires an invented
    # identity no script or dice roll here can supply.
    if motivated:
        contested = roll_contested()

    # Step 7/8 - arc primacy + gate
    primacy = roll_arc_primacy(p1, p2)
    primary_char = p1_char if primacy == p1 else p2_char
    other_char = p2_char if primacy == p1 else p1_char
    arc = primary_char.get("arc")

    if not arc:
        if primacy == home_frame and queue_arc(state, primacy, primary_char, "first", pass_number):
            notes.append(f"{primacy} queued for a first arc")
    elif arc.get("resolution") == "ongoing":
        gate_res = check_arc_alignment(arc.get("about", []), arc.get("needs", []), other_char)
        gate_hit = gate_res["gate"] == "hit"
        if gate_hit:
            inclined = gate_res.get("inclined", "neutral")
            outcome = roll_arc_outcome(inclined)
            arc.setdefault("history", []).append({"pass": pass_number, "outcome": outcome})
            score = tally(arc["history"])
            if score >= ARC_RESOLUTION_THRESHOLD:
                arc["resolution"] = "complete"
                notes.append(f"{primacy}'s arc completed")
            elif score <= -ARC_RESOLUTION_THRESHOLD:
                matched_about = gate_res.get("matched_about") or []
                if matched_about:
                    arc["about"] = matched_about
                    arc["history"][-1]["outcome"] = "transform"
                    notes.append(f"{primacy}'s arc transformed -> {matched_about}")
                else:
                    arc["resolution"] = "failed"
                    notes.append(f"{primacy}'s arc failed")
                    queue_arc(state, primacy, primary_char, "reauthor_failed", pass_number)
            else:
                notes.append(f"{primacy}'s arc: {outcome}")
            save_char(primacy, primary_char)

    # Step 12 - partner tracking, always both directions
    record_partner(p1, p2)
    record_partner(p2, p1)
    p1_char, p2_char = load_char(p1), load_char(p2)

    # Step 13 - reproduction eligibility + roll
    count_ab = p1_char.get("partners", {}).get(p2, 0)
    count_ba = p2_char.get("partners", {}).get(p1, 0)
    eligible = max(count_ab, count_ba) >= PARTNER_THRESHOLD
    cooldown_ok = all(
        c.get("last_reproduced_pass") is None
        or pass_number - c["last_reproduced_pass"] >= PARENT_COOLDOWN_PASSES
        for c in (p1_char, p2_char)
    )
    already_parent_child = p2 in p1_char.get("parents", []) or p1 in p2_char.get("parents", [])

    if eligible and cooldown_ok and not already_parent_child:
        repro = roll_reproduction(p1, p2)
        if repro["reproduces"] == "true":
            name_lead = repro["name_lead"]
            other_parent = p2 if name_lead == p1 else p1
            state.child_counter += 1
            placeholder = f"placeholder_{name_lead}_{other_parent}_{state.child_counter}"
            birth = generate_offspring(p1, p2, placeholder, pass_number)
            child = load_char(birth["slug"])
            state.pending_births.append((birth["slug"], birth["eligible_pass"]))
            state.generation[birth["slug"]] = 1 + max(
                state.generation.get(p1, 0), state.generation.get(p2, 0)
            )
            lead_char, other_char_ = (p1_char, p2_char) if name_lead == p1 else (p2_char, p1_char)
            state.pending["children"].append({
                "placeholder_slug": birth["slug"],
                "placeholder_name": placeholder,
                "name_lead": name_lead,
                "parent_a": {"slug": name_lead, "name": lead_char.get("name"), "city": lead_char.get("city", ""), "backstory": lead_char.get("backstory", "")},
                "parent_b": {"slug": other_parent, "name": other_char_.get("name"), "city": other_char_.get("city", ""), "backstory": other_char_.get("backstory", "")},
                "birth_pass": pass_number,
                "routines": child.get("routines", []),
            })
            notes.append(f"{p1}+{p2} had a child ({birth['slug']}, generation {state.generation[birth['slug']]})")

    # Step 15/16 - life.lived, death, death-legacy
    for participant in (p1, p2):
        update_character_lived(participant, 1)
        h = horizon(participant)
        if h["ending"] == "true":
            death = record_death(participant)
            state.living = [s for s in state.living if s != participant]
            notes.append(f"{participant} died")
            if h["band"] == "established" and death["notified"]:
                legacy = roll_death_legacy(death["notified"])
                if legacy["passes"] == "true":
                    recipient = legacy["recipient"]
                    deceased_char = load_char(participant)
                    deceased_arc = deceased_char.get("arc")
                    if deceased_arc:
                        recipient_char = load_char(recipient)
                        prev_arc = recipient_char.get("arc") or {}
                        archetype_ = prev_arc.get("archetype")
                        if not archetype_:
                            routines = recipient_char.get("routines", [])
                            if routines:
                                archetype_ = max(routines, key=lambda r: r.get("weight", 0))["archetype"]
                        recipient_char["arc"] = {
                            "about": list(deceased_arc.get("about", [])),
                            "needs": list(deceased_arc.get("needs", [])),
                            "archetype": archetype_ or deceased_arc.get("archetype"),
                            "resolution": "ongoing",
                            "history": [],
                        }
                        save_char(recipient, recipient_char)
                        notes.append(f"{participant}'s arc passed to {recipient} (death-legacy)")

    maybe_admit_children(state, pass_number)

    summary = f"pass {pass_number}: {p1} x {p2} ({mode}"
    if motivated:
        summary += f", motivated{' contested' if contested else ''}"
    summary += ")"
    if notes:
        summary += " - " + "; ".join(notes)
    return summary


# --------------------------------------------------------------------------------------------
# Driver
# --------------------------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--pool", nargs="+", required=True, help="Starting living participants (must all have routines)")
    parser.add_argument("--passes", type=int, required=True)
    args = parser.parse_args()

    pool = [s.lower() for s in args.pool]
    for slug in pool:
        path = CHAR_DIR / f"{slug}.json"
        if not path.exists():
            raise SystemExit(f"No character file for '{slug}'.")
        c = json.loads(path.read_text(encoding="utf-8"))
        if c.get("life", {}).get("deceased"):
            raise SystemExit(f"'{slug}' is already deceased - drop them from --pool.")
        if not c.get("routines"):
            raise SystemExit(f"'{slug}' has no routines - generate mode requires every starting participant to have them (a routine-less character can never be paired into the reproduction mechanic).")

    call("simulate_tally.py", ["snapshot", *pool, "--out", str(SNAPSHOT_PATH)])

    state = State(pool)
    ran = 0
    for pass_number in range(1, args.passes + 1):
        if len(state.living) < 2:
            print(f"Stopping early after {ran} pass(es) - fewer than 2 living participants remain.")
            break
        summary = run_pass(state, pass_number)
        state.log.append(summary)
        print(summary)
        ran += 1

    PENDING_PATH.write_text(
        json.dumps({"generated_at_pass": ran, **state.pending}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    LOG_PATH.write_text("# Generation log\n\n" + "\n".join(f"- {line}" for line in state.log) + "\n", encoding="utf-8")

    max_gen = max(state.generation.values(), default=0)
    print()
    print(f"passes run: {ran}")
    print(f"living pool at end: {len(state.living)}  ({', '.join(state.living)})")
    print(f"children born: {len(state.pending['children'])}")
    print(f"arcs queued for the language layer: {len(state.pending['arcs'])}")
    print(f"max generation depth reached: {max_gen}")
    print(f"pending language manifest: {PENDING_PATH}")
    print(f"log: {LOG_PATH}")
    print(f"snapshot (for simulate_tally.py report): {SNAPSHOT_PATH}")


if __name__ == "__main__":
    main()

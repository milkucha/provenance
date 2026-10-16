"""
What happens when a character completes an arc (design session 2026-10-17, TODO.md "class through
inheritance"). Called from simulate_pass_lib.run_pass_mechanics at the one place a completion is
detected (the tally reaches the threshold and `arc.resolution` flips to "complete"), so the
interactive /enact path, the driver and /generate all get the same thing:

  1. THE TALE. The completion is filed as a tale (_lore/tales/arc_complete_<key>.md and
     encodings.json tales.entries), same standing a birth or a death already has. Moved here from
     simulate_pass_brief.py (which keeps `write_arc_completion_tale` as an alias).
  2. THE REWARD. The completer is granted provisions: clamp(base + per_turn x turns, min, max), all
     four from tuning.json `arc_completion_reward`. `turns` is `arc.turns`, the character's own
     turns (passes in which they were the drawn p1) since the arc was authored. The grant goes into
     their own `provisions`, so it is inherited at death with everything else (estate.py); nothing
     is added to the estate separately.
  3. THE TELLING. The tale is TOLD, the way a death is. notify_death.circle_of() gives the two tiers:
     relations are told for certain, and `notification.extended_share` of the wider circle hears at
     once (the knob a death and a birth already use - this notification has none of its own). Each
     one gets a "Learned that ..." line in knowledge.experience and the completer as a `mentioned`
     tie in their circle. Everyone else finds out the way people do: the tale is in encodings.json
     and re-enters the knowledge sampling pool. The draw is logged as `arc_completion_notify`.
  4. THE CULTURAL CAPITAL. Every living child gets the tale as an education item (`tale: <id>`), in
     their knowledge itself, not just a line of hearsay: culture is inherited when a parent completes
     an arc. (Children born after the completion do not receive it - open question.)

Mechanical throughout: no judgment call, the tale's words are the same templated sentence as before.
"""

import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path
from random import Random

SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT = SCRIPTS_DIR.parent.parent
CHAR_DIR = ROOT / "_lore" / "characters"
ENCODINGS_PATH = ROOT / "_lore" / "encodings.json"
TALES_DIR = ROOT / "_lore" / "tales"

sys.path.insert(0, str(SCRIPTS_DIR))
import estate  # noqa: E402
import notify_death  # noqa: E402
import rng_context  # noqa: E402
import tuning  # noqa: E402
import update_social_circle  # noqa: E402


def reward_for(turns: int, cfg: dict | None = None) -> float:
    """clamp(base + per_turn x turns, min, max). Pure, so the balance script can call it."""
    cfg = cfg or tuning.load()["arc_completion_reward"]
    return max(cfg["min"], min(cfg["max"], cfg["base"] + cfg["per_turn"] * turns))


def git_user_name() -> str:
    try:
        return subprocess.check_output(["git", "config", "user.name"], cwd=ROOT, text=True).strip() or "unknown"
    except Exception:
        return "unknown"


def write_arc_completion_tale(key: str, name: str, arc: dict) -> str:
    """Mechanical - files already-decided content, makes no judgment call, same discipline
    write_arc.py itself follows. An arc's premise is already a concrete, resolved fact the moment
    its resolution flips to "complete" - the same standing a birth or death already has
    (generate_offspring.py's write_birth_tale() / record_death.py's write_tale_file()), so it belongs
    in tales.entries too, not left to evaporate as a bare resolution flag on the character's own
    arc field. Returns the tale id."""
    slug = f"arc_complete_{key}"
    base_slug, n = slug, 2
    while (TALES_DIR / f"{slug}.md").exists():
        slug = f"{base_slug}_{n}"
        n += 1

    told_date = date.today().isoformat()
    responsible = git_user_name()
    telling = f"{name} achieved what they'd set out to do: {arc.get('premise', '').rstrip('.')}."

    content = f"""# The Completion of {name}'s Arc

**Responsible:** {responsible} - real-world provenance only, never an in-fiction detail (also recorded in `_lore/tales/_authors.md`)
**Told by:** no one; simply now known
**Told on:** {told_date}
**Encodings id:** `tales.entries[].id = "{slug}"`

## The tale

{telling}

## Where this lands in the record

- Touches: {arc.get('about', [])}
- Conflicts raised: none
- Open questions logged: none
"""
    TALES_DIR.mkdir(parents=True, exist_ok=True)
    (TALES_DIR / f"{slug}.md").write_text(content, encoding="utf-8")

    encodings = json.loads(ENCODINGS_PATH.read_text(encoding="utf-8"))
    encodings["tales"]["entries"].append({
        "id": slug,
        "source_file": f"_lore/tales/{slug}.md",
        "told_date": told_date,
        "told_by": None,
        "summary": telling,
        "touches": [],
    })
    ENCODINGS_PATH.write_text(json.dumps(encodings, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return slug


def _load(key: str) -> dict:
    return json.loads((CHAR_DIR / f"{key}.json").read_text(encoding="utf-8"))


def _save(key: str, character: dict) -> None:
    (CHAR_DIR / f"{key}.json").write_text(json.dumps(character, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def complete(key: str, pass_number: int | None = None) -> dict:
    """Run the four steps above for `key`, whose arc has just been written as complete. Returns
    {tale_id, turns, reward, provisions, notified, children}."""
    character = _load(key)
    name = character.get("name", key)
    arc = character.get("arc") or {}
    turns = int(arc.get("turns", 0))
    reward = reward_for(turns)

    tale_id = write_arc_completion_tale(key, name, arc)

    default = tuning.load()["survival"]["starting_provisions_per_capita"]
    character["provisions"] = character.get("provisions", default) + reward
    arc["completion"] = {"pass": pass_number, "turns": turns, "reward": reward, "tale": tale_id}
    character["arc"] = arc
    _save(key, character)

    # The telling: relations for certain, a share of the wider circle at once (notify_death's own
    # mechanism and knob), the draw logged.
    characters, enc = notify_death.load()
    relations, extended_keys = notify_death.circle_of(key, characters, enc["hearsay"]["entries"])
    extended = sorted(extended_keys)
    n = notify_death.notify_count(len(extended))
    seed, draw_index = rng_context.reserve_seed(ROOT)
    sampled = sorted(Random(seed).sample(extended, n)) if n else []
    notified = sorted(relations) + sampled
    rng_context.log_draw(ROOT, "arc_completion_notify", [key], {"completer": key, "sampled": sampled, "relations": sorted(relations)}, seed, draw_index)

    telling = f"Learned that {name} achieved what they set out to do: {arc.get('premise', '').rstrip('.')}."
    children = estate.living_children(key)
    for k in notified:
        c = _load(k)
        c.setdefault("knowledge", {}).setdefault("experience", []).append(
            {"text": telling, "produced_by": {"scene_id": None, "pass_number": pass_number}}
            if pass_number is not None else telling
        )
        update_social_circle.add_tie(c, key, "mentioned")
        if k in children:
            items = c["knowledge"].setdefault("education", {"percent": None, "mode": "", "topic": None, "items": []}).setdefault("items", [])
            if f"tale: {tale_id}" not in items:
                items.append(f"tale: {tale_id}")
        _save(k, c)
    # Living children are relations (told above); a child somehow outside that set still gets the tale.
    for k in children:
        if k not in notified:
            c = _load(k)
            items = c.setdefault("knowledge", {}).setdefault("education", {"percent": None, "mode": "", "topic": None, "items": []}).setdefault("items", [])
            if f"tale: {tale_id}" not in items:
                items.append(f"tale: {tale_id}")
                _save(k, c)

    return {"tale_id": tale_id, "turns": turns, "reward": reward, "provisions": character["provisions"],
            "notified": notified, "children": children}

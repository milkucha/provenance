"""
Apply a decided set of changes to one character's _lore/characters/<key>.json - the mechanical half
of /enact Step 5b (points 3-5) and Step 6. Every value this script writes is something the caller (the
model running /enact) already decided; this script only owns getting it into the file correctly -
incrementing counters, appending to the right array, clearing the right pair of fields on a break -
instead of that being a hand-edited JSON diff every single pass.

This script makes NO judgement calls. It does not decide whether a shock lands, how a claim mutated,
or what a character's new trust reads as - it only records decisions already made. See
.claude/skills/character/SKILL.md Step 6 for what those three moves mean and how to choose between them.

Typical call, once per character enacted this scene (life.lived always advances; the rest are optional):

    py scripts/lore/update_character.py khaoe --lived-delta 1 \\
        --add-experience "Met Gondarfolas at the Espiral de las Eras." \\
        --add-experience "He owns both the Ensayo and the Libro."

Recording a shock resolution (only when check_anchor_reference.py's gate actually matched):

    py scripts/lore/update_character.py auroboro_iii --lived-delta 1 \\
        --criterion-move reject --dialog gondarfolas_auroboro_iii_espiral \\
        --cause "gondarfolas_auroboro_iii_espiral#4: Gondarfolas's suggestion that the Guerras might be told differently in the Libro" \\
        --note "Gate matched; claim was speculative and low-confidence. Rejected outright." \\
        --distrusts "people who suggest his story could fragment across sources"

A break clears standard/wasted_life to blank and keeps the old values in history's "was" field - do
not pass --new-standard/--new-wasted-life here; the gap is deliberately left open for a future pass
or /character session to fill, per Step 6 move 3.

Drift bookkeeping (Step 5b point 4, only when honoring the criterion cost something this scene):

    py scripts/lore/update_character.py nerkeli --cost-ledger "Turned down Auroboro III's offer, staying with routes instead of stories (nerkeli_auroboro_iii_terfila_plaza)."

Recording a synthesis (Step 5c point 8, one call per synthesis - call again for a second one the
same scene, since --add-synthesis only takes one --about pair and one --text per call):

    py scripts/lore/update_character.py nerkeli \\
        --add-synthesis --about "highway: M7" --about "character_legendary: navalius" \\
        --text "If M7 always ends where Nuvilo's family says they're from, then all these years turning around at the airstrip, I've been skipping past the one place that might matter most to him."

Recording a knowledge.experience entry that has a matching hearsay claim (Step 6 - reuse that
claim's `about` ref rather than writing a plain string, so check_resonance.py can find it later; one
call per grounded entry, --about repeatable for an entry that draws on more than one claim at once):

    py scripts/lore/update_character.py aureobalo --add-grounded-experience \\
        --about "Las Guerras de Gorff" \\
        --text "Told Farlis, for the first time aloud, that his surname resembles the losing side of the Guerras de Gorff."

An experience entry with no matching claim (a narrated action nobody voiced - this happens, and is a
legitimate outcome, not a recording failure) still uses plain --add-experience, unchanged.

Usage:
    py scripts/lore/update_character.py <npc_key> [options]
"""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
CHAR_DIR = ROOT / "_lore" / "characters"

_MOVE_LABELS = {"reject": "rejected", "reinterpret": "reinterpreted", "break": "broke"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("npc_key", help="Character key, e.g. 'khaoe'")
    parser.add_argument("--lived-delta", type=int, default=0, help="Amount to add to life.lived (usually 1, once per scene)")
    parser.add_argument("--add-experience", action="append", default=[], dest="experience", help="Append one knowledge.experience entry. Repeatable.")
    parser.add_argument("--criterion-move", choices=["reject", "reinterpret", "break"], default=None, help="The resolved shock move, if the anchor gate matched")
    parser.add_argument("--dialog", default=None, help="Dialog/scene id this move happened in (required with --criterion-move)")
    parser.add_argument("--cause", default=None, help="The claim id/text that triggered the shock (required with --criterion-move)")
    parser.add_argument("--note", default=None, help="Free-text explanation of the resolution, stored in criterion.history")
    parser.add_argument("--trusts", default=None, help="New criterion.trusts value, if this outcome moved it")
    parser.add_argument("--distrusts", default=None, help="New criterion.distrusts value, if this outcome moved it")
    parser.add_argument("--cost-ledger", action="append", default=[], dest="cost_ledger", help="Append one criterion.cost_ledger entry. Repeatable.")
    parser.add_argument("--deceased", action="store_true", help="Set life.deceased true directly. For a full death (tale, notify, circle), use record_death.py instead - this flag alone does none of that.")
    parser.add_argument("--add-synthesis", action="store_true", help="Append one knowledge.experience synthesis entry (/enact Step 5c). Requires exactly two --about and one --text. Call again for a second synthesis the same scene.")
    parser.add_argument("--add-grounded-experience", action="store_true", help="Append one knowledge.experience entry with a real 'about' ref, reused from a matching hearsay claim (/enact Step 6). Requires one or more --about and one --text. Call again for a second grounded entry the same scene.")
    parser.add_argument("--about", action="append", default=[], help="A parent/source ref for --add-synthesis (pass exactly twice) or --add-grounded-experience (pass one or more).")
    parser.add_argument("--text", default=None, help="The entry text for --add-synthesis or --add-grounded-experience.")
    args = parser.parse_args()

    if args.criterion_move and not (args.dialog and args.cause):
        parser.error("--criterion-move requires both --dialog and --cause")
    if args.add_synthesis and args.add_grounded_experience:
        parser.error("pass one of --add-synthesis or --add-grounded-experience per call, not both")
    if args.add_synthesis and (len(args.about) != 2 or not args.text):
        parser.error("--add-synthesis requires exactly two --about and one --text")
    if args.add_grounded_experience and (not args.about or not args.text):
        parser.error("--add-grounded-experience requires one or more --about and one --text")
    if (args.about or args.text) and not (args.add_synthesis or args.add_grounded_experience):
        parser.error("--about/--text only apply with --add-synthesis or --add-grounded-experience")

    key = args.npc_key.lower()
    char_path = CHAR_DIR / f"{key}.json"
    if not char_path.exists():
        raise SystemExit(f"No character file for '{key}'.")
    with open(char_path, encoding="utf-8") as f:
        character = json.load(f)

    changes = []

    if args.lived_delta:
        character.setdefault("life", {"lived": 0, "deceased": False})
        character["life"]["lived"] = character["life"].get("lived", 0) + args.lived_delta
        changes.append(f"life.lived += {args.lived_delta}  (now {character['life']['lived']})")

    if args.deceased:
        character.setdefault("life", {"lived": 0, "deceased": False})
        character["life"]["deceased"] = True
        changes.append("life.deceased = true")

    if args.experience:
        character.setdefault("knowledge", {}).setdefault("experience", [])
        character["knowledge"]["experience"].extend(args.experience)
        changes.append(f"knowledge.experience += {len(args.experience)} entr{'y' if len(args.experience) == 1 else 'ies'}")

    if args.criterion_move:
        criterion = character.setdefault("criterion", {
            "standard": "", "wasted_life": "", "anchor": "", "origin": "",
            "trusts": "", "distrusts": "", "tempered": 0, "cost_ledger": [], "history": [],
        })
        move_label = _MOVE_LABELS[args.criterion_move]
        history_entry = {"dialog": args.dialog, "move": move_label, "cause": args.cause}
        if args.note:
            history_entry["note"] = args.note

        if args.criterion_move == "reinterpret":
            criterion["tempered"] = criterion.get("tempered", 0) + 1
            changes.append(f"criterion.tempered += 1  (now {criterion['tempered']})")
        elif args.criterion_move == "break":
            history_entry["was"] = {"standard": criterion.get("standard", ""), "wasted_life": criterion.get("wasted_life", "")}
            criterion["standard"] = ""
            criterion["wasted_life"] = ""
            changes.append("criterion.standard/wasted_life cleared (break) - old values kept in history")

        criterion.setdefault("history", []).append(history_entry)
        changes.append(f"criterion.history += 1 entry (move: {move_label})")

        if args.trusts is not None:
            criterion["trusts"] = args.trusts
            changes.append("criterion.trusts updated")
        if args.distrusts is not None:
            criterion["distrusts"] = args.distrusts
            changes.append("criterion.distrusts updated")

    if args.cost_ledger:
        character.setdefault("criterion", {}).setdefault("cost_ledger", [])
        character["criterion"]["cost_ledger"].extend(args.cost_ledger)
        changes.append(f"criterion.cost_ledger += {len(args.cost_ledger)} entr{'y' if len(args.cost_ledger) == 1 else 'ies'}")

    if args.add_synthesis:
        character.setdefault("knowledge", {}).setdefault("experience", [])
        character["knowledge"]["experience"].append({
            "kind": "synthesis",
            "about": list(args.about),
            "derived_from": list(args.about),
            "text": args.text,
        })
        changes.append(f"knowledge.experience += 1 synthesis entry (about: {args.about})")

    if args.add_grounded_experience:
        character.setdefault("knowledge", {}).setdefault("experience", [])
        about_value = args.about[0] if len(args.about) == 1 else list(args.about)
        character["knowledge"]["experience"].append({"text": args.text, "about": about_value})
        changes.append(f"knowledge.experience += 1 grounded entry (about: {about_value})")

    if not changes:
        raise SystemExit("Nothing to do - pass at least one of --lived-delta, --add-experience, --criterion-move, --cost-ledger, --deceased, --add-synthesis, --add-grounded-experience.")

    with open(char_path, "w", encoding="utf-8") as f:
        json.dump(character, f, indent=2, ensure_ascii=False)
        f.write("\n")

    with open(char_path, encoding="utf-8") as f:
        json.load(f)  # round-trip validate

    print(f"{key}:")
    for c in changes:
        print(f"  {c}")


if __name__ == "__main__":
    main()

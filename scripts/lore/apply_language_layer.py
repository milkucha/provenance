"""
Applies the single batched subagent pass's output back onto the character files -
`/generate`'s own Step 5 (see `.claude/skills/generate/SKILL.md`, and
`simulate_generate_population.py`'s own docstring for why this is batched at all rather than
one dispatch per birth/arc).

Reads two files at the worktree root:
- `_pending_language.json` - written by `simulate_generate_population.py`: every placeholder-named
  child and every queued arc, with the supporting data the language-layer subagent needed.
- `_pending_language_resolved.json` - the subagent's own output, same shape keyed by
  `placeholder_slug`/`character_slug`:
    {"children": [{"placeholder_slug": "...", "name": "Real Name",
                   "routines": [{"location": "...", "routine_actions": "..."}]}],
     "arcs":     [{"character_slug": "...", "about": [...], "needs": [...], "context": "...", "premise": "..."}]}

For each resolved child: does a literal text substitution of the placeholder name string first,
scoped to exactly the files `generate_offspring.py` is known to have written it into, THEN (as of
2026-08-31, design debrief - see CHRONICLE.md) renames the character's own SLUG/filename to match
the resolved name too, walking every structural cross-reference (`parents`, `partners`,
`partners_quality`, `lifespans.json`'s key, birth/death tale filenames and their `encodings.json`/
`_index.md`/`_authors.md` entries). This used to be considered purely cosmetic and skipped on
purpose - but once a population needs merging back together from multiple parallel `/generate`
worktrees, the mechanical placeholder counter (`placeholder_child_0001`, reset to 0 per invocation)
guarantees cross-worktree filename collisions between unrelated children, while a name-derived slug
collides far less often. Since this script already has to walk every cross-reference for the NAME
substitution below, doing the SLUG rename in the same pass costs nothing extra. `leads` is not
handled here - `/generate` never writes a `leads` entry to a character file (see its own SKILL.md's
scope-difference #3), so there is nothing to rename there.

The literal text substitution itself is scoped to exactly the files
`generate_offspring.py` is known to have written it into:
  - the child's own `name` field
  - `_lore/tales/birth_of_<slug>.md`'s content
  - that birth's own `tales.entries` row in `_lore/encodings.json` (found by id, not a blanket
    file-wide replace - encodings.json is shared and must not be touched outside that one entry)
  - the matching row in `_lore/tales/_index.md` (found by the tale's `<slug>.md` reference, not a
    blanket replace either - that file is an append-only log of every tale ever recorded)
  - every character file's `knowledge.experience` entries that contain the placeholder substring
    (parents' "Had a child with X, named <placeholder>." and the notified circle's "Heard that X and
    Y now have a child, <placeholder>." - scanned rather than enumerated, since exactly who got
    notified isn't tracked outside those files themselves)
Any routine's `routine_actions` line the subagent rewrote is applied by matching `location` against
the child's own `routines[]`.

For each resolved arc: writes `arc = {about, needs, context, premise, resolution: "ongoing",
history: []}` onto that character's file, then runs `register_arc_concept.py` now that `premise` is
real content (folded into the registered concept's own `description`, not the old boilerplate) -
mirroring the interactive skill's own rule that only a genuinely-authored arc gets registered (a
transform or death-legacy reuses an existing tag and is never routed through this script at all).

Finally runs `build_source_index.py` once (the interactive skill's own Step 17 batch tidy-up) and
archives both pending files under `_generation_archive/` so a later `/generate` run in the same
worktree starts from a clean pending manifest.

Usage:
    py scripts/lore/apply_language_layer.py
"""

import json
import re
import shutil
import subprocess
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT = SCRIPTS_DIR.parent.parent
CHAR_DIR = ROOT / "_lore" / "characters"
TALES_DIR = ROOT / "_lore" / "tales"
ENCODINGS_PATH = ROOT / "_lore" / "encodings.json"
INDEX_PATH = TALES_DIR / "_index.md"
AUTHORS_PATH = TALES_DIR / "_authors.md"
LIFESPANS_PATH = CHAR_DIR / "lifespans.json"
PENDING_PATH = ROOT / "_pending_language.json"
RESOLVED_PATH = ROOT / "_pending_language_resolved.json"
ARCHIVE_DIR = ROOT / "_generation_archive"


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return "_".join(words)


def unique_slug(base: str) -> str:
    if not (CHAR_DIR / f"{base}.json").exists():
        return base
    n = 2
    while (CHAR_DIR / f"{base}_{n}.json").exists():
        n += 1
    return f"{base}_{n}"


def rename_slug(old_slug: str, real_name: str) -> str:
    """Renames the character's own slug/filename to match the resolved name, walking every
    structural cross-reference. Returns the (possibly disambiguated) new slug, or old_slug unchanged
    if the derived slug collides with itself."""
    new_slug = unique_slug(slugify(real_name))
    if new_slug == old_slug:
        return old_slug

    (CHAR_DIR / f"{old_slug}.json").rename(CHAR_DIR / f"{new_slug}.json")

    if LIFESPANS_PATH.exists():
        lifespans = json.loads(LIFESPANS_PATH.read_text(encoding="utf-8"))
        if old_slug in lifespans.get("lifespans", {}):
            lifespans["lifespans"][new_slug] = lifespans["lifespans"].pop(old_slug)
            LIFESPANS_PATH.write_text(json.dumps(lifespans, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    for path in CHAR_DIR.glob("*.json"):
        if path.stem in (new_slug, "_template", "lifespans"):
            continue
        other = json.loads(path.read_text(encoding="utf-8"))
        changed = False
        parents = other.get("parents")
        if parents and old_slug in parents:
            other["parents"] = [new_slug if p == old_slug else p for p in parents]
            changed = True
        for field in ("partners", "partners_quality"):
            d = other.get(field)
            if d and old_slug in d:
                d[new_slug] = d.pop(old_slug)
                changed = True
        if changed:
            path.write_text(json.dumps(other, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    for prefix in ("birth_of_", "death_of_"):
        old_tale = TALES_DIR / f"{prefix}{old_slug}.md"
        if old_tale.exists():
            old_tale.rename(TALES_DIR / f"{prefix}{new_slug}.md")

    with open(ENCODINGS_PATH, encoding="utf-8") as f:
        encodings = json.load(f)
    for entry in encodings["tales"]["entries"]:
        for prefix in ("birth_of_", "death_of_"):
            if entry["id"] == f"{prefix}{old_slug}":
                entry["id"] = f"{prefix}{new_slug}"
                entry["source_file"] = f"_lore/tales/{prefix}{new_slug}.md"
    with open(ENCODINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(encodings, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for prefix in ("birth_of_", "death_of_"):
        old_id, new_id = f"{prefix}{old_slug}", f"{prefix}{new_slug}"
        if INDEX_PATH.exists():
            text = INDEX_PATH.read_text(encoding="utf-8")
            INDEX_PATH.write_text(text.replace(f"`{old_id}.md`", f"`{new_id}.md`"), encoding="utf-8")
        if AUTHORS_PATH.exists():
            text = AUTHORS_PATH.read_text(encoding="utf-8")
            AUTHORS_PATH.write_text(text.replace(f"`{old_id}`", f"`{new_id}`"), encoding="utf-8")

    return new_slug


def call(script_name: str, argv: list) -> str:
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / script_name), *argv],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"{script_name} {argv} failed (exit {result.returncode}):\n{result.stderr}")
    return result.stdout


def load_char(slug: str) -> dict:
    with open(CHAR_DIR / f"{slug}.json", encoding="utf-8") as f:
        return json.load(f)


def save_char(slug: str, character: dict) -> None:
    with open(CHAR_DIR / f"{slug}.json", "w", encoding="utf-8") as f:
        json.dump(character, f, indent=2, ensure_ascii=False)
        f.write("\n")


def safe_replace(text: str, old: str, new: str, protect: list) -> str:
    """Replaces every occurrence of `old` with `new`, except inside any of the `protect` substrings -
    needed because a placeholder name and its own (never-renamed) slug are frequently the same
    string, so a blanket replace would also corrupt an id/filename reference like
    'birth_of_<slug>' that happens to contain the placeholder name as a substring."""
    sentinels = {}
    for i, p in enumerate(protect):
        if p and p in text:
            token = f"\x00PROTECT{i}\x00"
            sentinels[token] = p
            text = text.replace(p, token)
    text = text.replace(old, new)
    for token, original in sentinels.items():
        text = text.replace(token, original)
    return text


def replace_in_experience(character: dict, old: str, new: str, protect: list) -> bool:
    changed = False
    for entry in character.get("knowledge", {}).get("experience", []):
        if isinstance(entry, str) and old in entry:
            idx = character["knowledge"]["experience"].index(entry)
            character["knowledge"]["experience"][idx] = safe_replace(entry, old, new, protect)
            changed = True
        elif isinstance(entry, dict) and isinstance(entry.get("text"), str) and old in entry["text"]:
            entry["text"] = safe_replace(entry["text"], old, new, protect)
            changed = True
    return changed


def rename_child(placeholder_slug: str, placeholder_name: str, real_name: str, routine_updates: list) -> str:
    protect = [f"birth_of_{placeholder_slug}"]

    child = load_char(placeholder_slug)
    child["name"] = real_name
    for update in routine_updates or []:
        for r in child.get("routines", []):
            if r["location"] == update.get("location"):
                r["routine_actions"] = update.get("routine_actions", r.get("routine_actions", ""))
    save_char(placeholder_slug, child)

    tale_path = TALES_DIR / f"birth_of_{placeholder_slug}.md"
    if tale_path.exists():
        text = tale_path.read_text(encoding="utf-8")
        tale_path.write_text(safe_replace(text, placeholder_name, real_name, protect), encoding="utf-8")

    with open(ENCODINGS_PATH, encoding="utf-8") as f:
        encodings = json.load(f)
    tale_id = f"birth_of_{placeholder_slug}"
    for entry in encodings["tales"]["entries"]:
        if entry["id"] == tale_id and placeholder_name in (entry.get("summary") or ""):
            entry["summary"] = safe_replace(entry["summary"], placeholder_name, real_name, protect)
    with open(ENCODINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(encodings, f, indent=2, ensure_ascii=False)
        f.write("\n")

    if INDEX_PATH.exists():
        lines = INDEX_PATH.read_text(encoding="utf-8").splitlines(keepends=True)
        marker = f"`{tale_id}.md`"
        lines = [
            safe_replace(line, placeholder_name, real_name, protect) if marker in line and placeholder_name in line else line
            for line in lines
        ]
        INDEX_PATH.write_text("".join(lines), encoding="utf-8")

    renamed_elsewhere = 0
    for path in CHAR_DIR.glob("*.json"):
        if path.stem == placeholder_slug:
            continue
        other = json.loads(path.read_text(encoding="utf-8"))
        if replace_in_experience(other, placeholder_name, real_name, protect):
            with open(path, "w", encoding="utf-8") as f:
                json.dump(other, f, indent=2, ensure_ascii=False)
                f.write("\n")
            renamed_elsewhere += 1

    new_slug = rename_slug(placeholder_slug, real_name)
    slug_note = f"  [slug: {placeholder_slug} -> {new_slug}]" if new_slug != placeholder_slug else ""
    print(f"renamed: {placeholder_slug}  '{placeholder_name}' -> '{real_name}'  ({renamed_elsewhere} other file(s) updated){slug_note}")
    return new_slug


def apply_arc(character_slug: str, about: list, needs: list, context: str, premise: str) -> None:
    character = load_char(character_slug)
    character["arc"] = {
        "about": about,
        "needs": needs or [],
        "context": context,
        "premise": premise or "",
        "resolution": "ongoing",
        "history": [],
    }
    save_char(character_slug, character)
    print(call("register_arc_concept.py", [character_slug]).strip())


def archive(generated_at_pass) -> None:
    ARCHIVE_DIR.mkdir(exist_ok=True)
    stamp = f"pass_{generated_at_pass}_{datetime.now():%Y%m%d-%H%M%S}"
    dest = ARCHIVE_DIR / stamp
    dest.mkdir()
    shutil.move(str(PENDING_PATH), str(dest / PENDING_PATH.name))
    shutil.move(str(RESOLVED_PATH), str(dest / RESOLVED_PATH.name))
    print(f"archived pending manifests under {dest}")


def main() -> None:
    if not PENDING_PATH.exists():
        raise SystemExit(f"No pending manifest at {PENDING_PATH} - run simulate_generate_population.py first.")
    if not RESOLVED_PATH.exists():
        raise SystemExit(f"No resolved manifest at {RESOLVED_PATH} - the language-layer subagent hasn't written its output yet.")

    pending = json.loads(PENDING_PATH.read_text(encoding="utf-8"))
    resolved = json.loads(RESOLVED_PATH.read_text(encoding="utf-8"))

    pending_children = {c["placeholder_slug"]: c for c in pending.get("children", [])}
    slug_map = {}
    for entry in resolved.get("children", []):
        slug = entry["placeholder_slug"]
        if slug not in pending_children:
            print(f"WARNING: resolved child '{slug}' not found in pending manifest - skipping.")
            continue
        new_slug = rename_child(slug, pending_children[slug]["placeholder_name"], entry["name"], entry.get("routines"))
        slug_map[slug] = new_slug

    for entry in resolved.get("arcs", []):
        character_slug = slug_map.get(entry["character_slug"], entry["character_slug"])
        apply_arc(character_slug, entry.get("about", []), entry.get("needs", []), entry.get("context", ""), entry.get("premise", ""))

    print(call("build_source_index.py", []).strip())

    archive(pending.get("generated_at_pass", "unknown"))

    resolved_children = {c["placeholder_slug"] for c in resolved.get("children", [])}
    resolved_arcs = {a["character_slug"] for a in resolved.get("arcs", [])}
    missing_children = set(pending_children) - resolved_children
    missing_arcs = {a["character_slug"] for a in pending.get("arcs", [])} - resolved_arcs
    if missing_children:
        print(f"NOTE: {len(missing_children)} pending child(ren) had no resolved name and are still placeholder-named: {', '.join(sorted(missing_children))}")
    if missing_arcs:
        print(f"NOTE: {len(missing_arcs)} pending arc(s) were never resolved and remain arc-less: {', '.join(sorted(missing_arcs))}")


if __name__ == "__main__":
    main()

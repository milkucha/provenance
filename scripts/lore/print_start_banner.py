"""
Print the fixed-width welcome banner the /start skill shows a new session: a short pitch, a live
one-line count of what's already in this copy of the world (characters/tales/hearsay/conflicts/
material sources), and the two doors in - growing the record vs. putting it in motion - each pointing
at the skill that owns it.

All alignment/padding is done here in Python (exact string widths), not left to the model composing
the reply - the same "let a script own anything mechanical" discipline as every other scripts/lore/
file. /start's own job is just to run this and print its output verbatim inside a fenced code block.

Usage:
    python scripts/lore/print_start_banner.py
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
LORE = ROOT / "_lore"
INNER_WIDTH = 76


def count_characters() -> int:
    char_dir = LORE / "characters"
    if not char_dir.exists():
        return 0
    skip = {"_template.json", "lifespans.json"}
    return sum(1 for p in char_dir.glob("*.json") if p.name not in skip)


def count_material() -> int:
    material_dir = LORE / "material"
    if not material_dir.exists():
        return 0
    return sum(1 for p in material_dir.iterdir() if p.is_file() and not p.name.startswith("_"))


def load_encodings() -> dict:
    path = LORE / "encodings.json"
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def line(content: str = "") -> str:
    content = content[:INNER_WIDTH].ljust(INNER_WIDTH)
    return f"│{content}│"


def build_banner() -> str:
    encodings = load_encodings()
    n_characters = count_characters()
    n_tales = len(encodings.get("tales", {}).get("entries", []))
    n_hearsay = len(encodings.get("hearsay", {}).get("entries", []))
    conflicts = encodings.get("conflicts", [])
    n_conflicts_open = sum(1 for c in conflicts if not c.get("user_resolution"))
    n_material = count_material()

    rows = [
        "  Provenance",
        "  A storytelling engine — grow a fictional society from a small seed.",
        "",
        "  This world right now:",
        f"    {n_characters} character(s), {n_tales} tale(s), {n_hearsay} hearsay claim(s)",
        f"    {n_conflicts_open} open conflict(s), {n_material} material source(s)",
        "",
        "  Growing the record",
        "    /character      hand-author a person: name, origin, backstory",
        "    /tell           record a myth or legend with no material trace",
        "    material →     drop a file in _lore/material/, then run /integrate",
        "",
        "  Putting it in motion",
        "    /enact                one live scene, played turn by turn",
        "    /simulate             chain many scenes across a population",
        "    /generate             fast-forward a whole starting cast, no prose",
        "",
        "  New here? README.md §0-2 has the full picture.",
    ]

    top = "╭" + ("─" * INNER_WIDTH) + "╮"
    bottom = "╰" + ("─" * INNER_WIDTH) + "╯"
    body = "\n".join(line(row) for row in rows)
    return f"{top}\n{body}\n{bottom}"


if __name__ == "__main__":
    print(build_banner())

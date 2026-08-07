"""
List open sections in _lore/unknowns.md - the "what still needs a user decision" backlog /resolve
Step 1 shows when working through unknowns.md rather than encodings.json's conflicts array.

A heading counts as OPEN unless its own title contains "resolved" or "correction" (case-insensitive) -
the file's own established convention for marking a section closed (see its several existing
"## Resolved by..." and "## Correction (...)" headings). This is judged per-heading, not inherited
from a parent section - e.g. the "### Follow-up flag" subsection nested under a resolved 2026-07-24
section is correctly still OPEN, since that specific follow-up question was never answered.

This script does not decide whether a section is actually worth putting to the user, and never
touches the file - it only lists candidates for a human to pick from. See /resolve
(.claude/skills/resolve/SKILL.md).

Usage:
    py scripts/lore/list_open_unknowns.py
"""

import re
import sys
from pathlib import Path

# See resolve_conflict.py for why: this machine's Python defaults stdout to cp1252, which mangles
# the diacritics throughout this file's Spanish-language section titles once piped through a shell
# expecting UTF-8.
sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent.parent
UNKNOWNS_PATH = ROOT / "_lore" / "unknowns.md"

CLOSED_WORDS = ("resolved", "correction")


def main() -> None:
    lines = UNKNOWNS_PATH.read_text(encoding="utf-8").splitlines()
    open_count = 0
    for i, line in enumerate(lines, start=1):
        m = re.match(r"^(#{2,3})\s+(.*)", line)
        if not m:
            continue
        title = m.group(2)
        if any(word in title.lower() for word in CLOSED_WORDS):
            continue
        open_count += 1
        print(f"line {i} ({m.group(1)}): {title}")

    print()
    print(f"{open_count} open section(s). A heading not saying 'Resolved'/'Correction' is a candidate,")
    print("not a guarantee - some are genuine gaps in the source material rather than decisions the")
    print("user can actually settle (nobody can resolve what a document simply never says). Use")
    print("judgement about which are worth putting to the user versus left as documented gaps.")


if __name__ == "__main__":
    main()

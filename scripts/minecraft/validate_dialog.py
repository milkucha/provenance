#!/usr/bin/env python3
"""
Validate a Blabber dialogue JSON file's structure - the mechanical checks /embody Step 1 currently
asks a model to do by eye ("Validate before moving on — every choices[].next must resolve to a real
state, start_at must be valid, and the top-level layout is present"), plus the two hard formatting
rules from the top of .claude/skills/embody/SKILL.md: no stage-direction cues, no line over 300
characters.

This checks structure only - it has no opinion on writing quality, gesture choice, or whether the
conversion is faithful to the transcript it came from. A clean pass here does not mean the dialog is
good, only that it will not break when Blabber tries to load it.

Usage:
    py scripts/minecraft/validate_dialog.py data/luminacion/blabber/dialogues/<file>.json
"""

import argparse
import json
import re
import sys
from pathlib import Path

CUE_PATTERN = re.compile(r"\*[^*]+\*")
MAX_LINE_LEN = 300


def check(dialog: dict) -> tuple[list, list]:
    errors: list[str] = []
    warnings: list[str] = []

    if dialog.get("layout", {}).get("type") != "blabber:rpg":
        errors.append('Missing or wrong top-level "layout": { "type": "blabber:rpg" }.')
    if "$schema" not in dialog:
        warnings.append('Missing "$schema" field.')

    states = dialog.get("states")
    if not isinstance(states, dict) or not states:
        errors.append('Missing or empty "states" object.')
        return errors, warnings

    start_at = dialog.get("start_at")
    if not start_at:
        errors.append('Missing "start_at".')
    elif start_at not in states:
        errors.append(f'"start_at" ("{start_at}") does not match any state key.')

    referenced = {start_at} if start_at else set()

    for state_id, state in states.items():
        is_end = state.get("type") == "end_dialogue"

        texts_to_check = []
        if "text" in state:
            texts_to_check.append(("text", state["text"]))

        if not is_end and "text" not in state:
            errors.append(f'State "{state_id}": non-end state has no "text".')

        choices = state.get("choices", [])
        if not is_end and not choices:
            warnings.append(f'State "{state_id}": non-end state has no "choices" - dead end?')

        for i, choice in enumerate(choices):
            if "text" in choice:
                texts_to_check.append((f"choices[{i}].text", choice["text"]))
            next_id = choice.get("next")
            if not next_id:
                errors.append(f'State "{state_id}" choices[{i}]: missing "next".')
            elif next_id not in states:
                errors.append(f'State "{state_id}" choices[{i}]: "next" ("{next_id}") does not match any state key.')
            else:
                referenced.add(next_id)

        for label, text in texts_to_check:
            if len(text) > MAX_LINE_LEN:
                errors.append(f'State "{state_id}" {label}: {len(text)} chars, over the {MAX_LINE_LEN} cap.')
            if CUE_PATTERN.search(text):
                errors.append(f'State "{state_id}" {label}: contains a stage-direction cue (*...*) - dialogue only, no action cues.')

    unreachable = set(states) - referenced
    if unreachable:
        warnings.append(f"Unreachable state(s), never targeted by start_at or any choice: {sorted(unreachable)}")

    return errors, warnings


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("path", type=Path, help="Path to the dialogue JSON file")
    args = parser.parse_args()

    if not args.path.exists():
        raise SystemExit(f"No such file: {args.path}")
    try:
        dialog = json.loads(args.path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise SystemExit(f"Not valid JSON: {e}")

    errors, warnings = check(dialog)

    print(f"{args.path}")
    print(f"states: {len(dialog.get('states', {}))}")
    print()

    if errors:
        print(f"ERRORS ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
    if warnings:
        print(f"WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"  - {w}")
    if not errors and not warnings:
        print("Clean - no structural issues found.")

    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()

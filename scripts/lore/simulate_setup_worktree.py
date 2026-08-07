"""
Create the dedicated worktree /simulate runs in, and grant it a scoped permission bypass - the two
mechanical steps that .claude/skills/simulate/SKILL.md Step 2 documents as needing to happen in this
exact order, before EnterWorktree is ever called. Doing both in one script removes the one way this
was confirmed to go wrong: editing the settings file after switching into the worktree leaves every
subagent still prompting for the rest of that session, because a session's config for a directory is
fixed at the point it starts treating that directory as a project root.

What this script does NOT do: call EnterWorktree. That's a tool call only the calling skill can make;
this script only needs the worktree and its settings file to already exist on disk first, per the
ordering /simulate Step 2 depends on.

Usage:
    py scripts/lore/simulate_setup_worktree.py
    py scripts/lore/simulate_setup_worktree.py --name simulate-20260807-153000
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--name", default=None, help="Worktree name. Default: simulate-<YYYYMMDD-HHMMSS>")
    args = parser.parse_args()

    name = args.name or f"simulate-{datetime.now():%Y%m%d-%H%M%S}"
    worktree_path = ROOT / ".claude" / "worktrees" / name
    branch = f"worktree-{name}"

    if worktree_path.exists():
        raise SystemExit(f"{worktree_path} already exists - pick a different --name.")

    result = subprocess.run(
        ["git", "worktree", "add", str(worktree_path), "-b", branch, "HEAD"],
        cwd=ROOT, capture_output=True, text=True,
    )
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        raise SystemExit(f"git worktree add failed (exit {result.returncode}) - see stderr above.")

    settings_path = worktree_path / ".claude" / "settings.json"
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    if settings_path.exists():
        with open(settings_path, encoding="utf-8") as f:
            settings = json.load(f)
    else:
        settings = {}

    settings.setdefault("permissions", {})["defaultMode"] = "bypassPermissions"
    settings["skipDangerousModePermissionPrompt"] = True

    with open(settings_path, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)
        f.write("\n")

    with open(settings_path, encoding="utf-8") as f:
        json.load(f)  # round-trip validate

    print(f"path: {worktree_path}")
    print(f"branch: {branch}")
    print("settings.json: bypass permissions written")
    print("Next: call EnterWorktree with path set to the line above, exactly as printed.")


if __name__ == "__main__":
    main()

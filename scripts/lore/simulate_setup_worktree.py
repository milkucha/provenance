"""
Create the dedicated worktree /simulate runs in, and grant it a scoped permission bypass - the two
mechanical steps that .claude/skills/simulate/SKILL.md Step 2 documents as needing to happen in this
exact order, before EnterWorktree is ever called. Doing both in one script removes the one way this
was confirmed to go wrong: editing the settings file after switching into the worktree leaves every
subagent still prompting for the rest of that session, because a session's config for a directory is
fixed at the point it starts treating that directory as a project root.

`defaultMode: bypassPermissions` + `skipDangerousModePermissionPrompt` alone are NOT sufficient to
guarantee zero prompts for an unattended run - confirmed the hard way on 2026-08-08 mid-run, three
separate gaps beyond what those two cover:
1. Dispatching a subagent (the Agent tool) still prompted despite bypassPermissions being active for
   ordinary Bash/Read/Write calls in the same directory - needs its own explicit `"Agent"` allow entry
   (and `skipWorkflowUsageWarning: true`, in case the harness classifies subagent dispatch as a
   "workflow" internally).
2. A Bash command combining `cd <path> && <command>` is hard-blocked by a security guardrail
   ("Compound command contains cd with path operation") that no permission setting can override, ever
   - this is not fixable via settings.json at all. The only fix is behavioral: never emit that pattern
   in the first place (see SKILL.md Step 3's "never use cd" rule) - every `scripts/lore/*.py` file
   resolves its own root via `Path(__file__).resolve().parent.parent.parent`, so `cd` is never actually
   needed to invoke them correctly regardless of shell cwd.
3. A subagent (especially on a smaller/cheaper model) can mistype the long absolute worktree path when
   re-deriving it from memory across many tool calls - observed once as a lore-salient word ("Lundria")
   silently substituted for the real folder name ("Luminacion") in a Read call, which then prompted for
   a new, unrecognized path outside the worktree. Read is non-destructive (a bad path just errors
   cleanly), so it's safe to blanket-allow; broadening `Write`/`Edit`/`Bash` too closes the same class
   of gap for every other tool a subagent might invoke mid-pass, and `Glob`/`Grep` cost nothing to add.
   This is a one-way trust expansion scoped ONLY to this one disposable worktree's own settings.json -
   it is never written to the main repo's settings.json/settings.local.json, and never to
   settings.local.json even inside the worktree (which the harness silently rewrites on individual
   prompt approvals, clobbering any bypass written there).

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

    permissions = settings.setdefault("permissions", {})
    permissions["defaultMode"] = "bypassPermissions"
    allow = permissions.setdefault("allow", [])
    for entry in ("Agent", "Read", "Write", "Edit", "Bash", "Glob", "Grep"):
        if entry not in allow:
            allow.append(entry)
    settings["skipDangerousModePermissionPrompt"] = True
    settings["skipWorkflowUsageWarning"] = True

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

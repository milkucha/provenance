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
   re-deriving it from memory across many tool calls - observed once as a lore-salient word ("City G")
   silently substituted for the real folder name ("Luminacion") in a Read call, which then prompted for
   a new, unrecognized path outside the worktree. Read is non-destructive (a bad path just errors
   cleanly), so it's safe to blanket-allow; broadening every other tool a subagent could plausibly reach
   for closes the same class of gap regardless of which one it picks.
4. A subagent can reach for the **PowerShell** tool instead of Bash on this Windows environment (not as
   a documented fallback-after-failure - as its first choice for a shell command), which is a wholly
   separate tool with its own permission gate that a `"Bash"` allow entry does not cover. Blanket-allow
   it too rather than assuming Bash is the only shell tool a subagent will ever pick.
5. **`.claude/` gets its own extra protection that a bare `"Write"`/`"Edit"` allow does not cover.**
   Observed: a subagent wrote a scratch JSON file into the worktree's own `.claude/` directory (an odd
   location choice in itself - Step 3 now tells it not to), and that write alone triggered a prompt even
   though ordinary `Write` calls elsewhere in the worktree had been working cleanly for a dozen prior
   passes. `.claude/` is the harness's own config/skills/permissions directory, so it's reasonable this
   gets guarded specially; the fix is the same pattern the harness's own `update-config` skill documents
   (`"Edit(.claude)"` as a distinct rule from a general `Edit` allow) - add explicit path-scoped entries
   for both the directory itself and everything under it.

**Every tool a `/simulate` subagent's actual procedure could plausibly reach for is blanket-allowed
below** - both shells (`Bash`, `PowerShell`), all file I/O (`Read`, `Write`, `Edit`, `Glob`, `Grep`,
plus explicit `.claude/` path entries per point 5), subagent dispatch (`Agent`), skill invocation
(`Skill`, in case it invokes one directly rather than reading the SKILL.md file), and its own task
tracking (`Task*`). Deliberately NOT included: anything
with no role in this skill's lore-only, no-network procedure (`WebFetch`, `WebSearch`, browser/MCP
tools, scheduling, `EnterWorktree`/`ExitWorktree` - a subagent should never be managing worktrees
itself) - broadening those would be an unrelated expansion of trust, not a fix for anything this skill
actually does. This is a one-way trust expansion scoped ONLY to this one disposable worktree's own
settings.json - it is never written to the main repo's settings.json/settings.local.json, and never to
settings.local.json even inside the worktree (which the harness silently rewrites on individual prompt
approvals, clobbering any bypass written there).

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
    for entry in (
        "Agent", "Read", "Write", "Write(.claude)", "Write(.claude/**)",
        "Edit", "Edit(.claude)", "Edit(.claude/**)", "Bash", "PowerShell", "Glob", "Grep", "Skill",
        "TaskCreate", "TaskUpdate", "TaskGet", "TaskList", "TaskOutput", "TaskStop",
    ):
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

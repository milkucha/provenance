---
description: Batch-run many /enact character-vs-character scenes across an existing population, in an isolated git worktree, to see how the lore state (hearsay pool, criteria, lifespans, deaths) evolves over a number of passes without touching the real files. Use for testing the enactment mechanism at scale or for producing a showcase trail of scenes — never for a single one-off scene, that's /enact directly.
disable-model-invocation: true
---

Orchestrator over `/enact`'s existing-character path, run unattended and repeatedly inside a
dedicated worktree. Lore-only, same as `/enact` and `/character` — never touches `data/` or
`_npcs/`. Read `.claude/skills/enact/SKILL.md` before running this if it hasn't been read yet this
session; this skill points back at its rules rather than restating them, and only spells out where
it deviates (no interactive questions inside a pass, existing participants only, absolute paths into
the worktree).

## Step 0 — Preconditions

- **Already in a worktree?** If this conversation is currently sitting inside a worktree from an
  earlier `/simulate` run (or any other reason), don't call `EnterWorktree` again — it errors if
  called from inside an existing worktree session. Ask the user (AskUserQuestion) whether to exit
  and keep that one first. Never call `ExitWorktree` without asking; it's a no-op if there's nothing
  to exit, so it's always safe to ask.
- **Uncommitted lore changes?** Run `git status --short -- _lore/` in the current directory. If it
  reports anything, the simulation is about to branch from the last *commit*, not these edits — tell
  the user plainly and ask (AskUserQuestion: commit first / proceed anyway understanding the gap).
  A worktree's working directory is independent of this one; uncommitted changes here do not carry
  over regardless of how the worktree is created.

## Step 1 — Setup questions

Ask as plain conversation, or AskUserQuestion where multiple-choice fits:

1. **Participants** — which characters take part, by name. For each: slugify the same way `/enact`
   Step 1 does and check `_lore/characters/<slug>.json` exists. **This skill never creates a
   participant** — if a file is missing, say so and stop (point at `/character` to build it first),
   rather than seeding a bare one on the spot. Also check `life.deceased` on each existing file — a
   deceased character can't be enacted, same rule as `/enact` Step 1; drop them or ask for a
   replacement. Need at least 2 living participants to proceed at all.
2. **Passes** — how many scenes to run in total, e.g. 50.
3. **Context** — optional free text: a scenario/situation to feed into every scene (e.g. "these all
   happen during the Feria"). Leave blank for random — each pass then invents its own plausible
   situation, bounded by what both participants in it could actually know.
4. **Model** — which model plays each pass (Haiku / Sonnet / Opus), default Sonnet if not asked.
   Quality matters more here than in a one-off `/enact`, because a pass's Step 5b judgment calls
   (criterion shock resolution, hearsay mutation) become the input the *next* pass reads — errors
   compound across a run in a way they don't in a single scene. This only affects the per-pass
   subagent below; the orchestration in this skill itself (pairing, logging) runs at whatever model
   this conversation is already on.

## Step 2 — Create the worktree

Every pass in Step 3 dispatches a subagent that runs several `py scripts/lore/...` calls, `cd`, and
`git`-adjacent commands — dozens of routine tool calls per pass, times N passes. Without a permission
bypass in place *before* any of that runs, each one prompts the user, which defeats the entire point
of an unattended batch run.

1. Run the setup script — it creates the worktree with `git worktree add ... HEAD` and writes the
   scoped permission bypass into *that worktree's own* `.claude/settings.json`, both in one call, in
   the only order confirmed to work (see below for why):
   ```bash
   py scripts/lore/simulate_setup_worktree.py
   ```
   Keep the printed `path` and `branch` — point 2 below and Step 4 both need the path. The script
   always branches from `HEAD` directly, regardless of the `worktree.baseRef` setting — that setting
   only governs `EnterWorktree`'s own `name`-based creation flow, which point 2 deliberately avoids by
   passing `path` instead.
2. Only now call `EnterWorktree` with `path` set to the printed path (not `name` — the worktree
   already exists, this just switches the session into it). Because the settings file was already on
   disk before this call, this is the point where the bypass actually takes effect for the rest of the
   run.

**Why the order matters:** editing the worktree's settings file *after* switching into it leaves
every subagent still prompting for the rest of that session — confirmed the hard way — because the
session's config for a directory is fixed at the point it starts treating that directory as a project
root, and does not live-reload from later edits to it. The script exists specifically so this can't
happen: the worktree and its settings file are both already on disk before this skill ever calls
`EnterWorktree`.

**The bypass only ever lands in the new worktree's own `settings.json`** — never the main repo's
`settings.json`/`settings.local.json`, and never `settings.local.json` even inside the worktree
(`settings.local.json` gets rewritten by the harness itself whenever a prompt is individually
approved, which would silently clobber this — `settings.json` doesn't). This keeps the bypass scoped
to this one disposable, isolated copy for exactly the duration of this run; it must never leak into
the directory the user actually works in day to day, and every future `/simulate` run gets its own
fresh worktree and this same fresh grant via the same script, not a standing one.

If prompts still fire during Step 3 despite this order, the fix is to end the session and start a new
one that calls `EnterWorktree` with `path` pointed at the already-existing worktree — a fresh
session's config load will pick up the settings file that's already sitting there even if the one
that created it couldn't. Passes already completed are safe either way; they're written straight to
disk in the worktree as each one finishes, per Step 3.

A fresh worktree per run is what makes repeated runs independently comparable against the same
starting lore state — report the path and branch to the user once created. Everything from here
happens inside that worktree's copy of the repo; the original working directory is untouched.

## Step 3 — Run passes

Keep, in this conversation only (nothing written to disk until Step 4):

- The **living pool** — participant slugs, minus anyone whose `life.deceased` turns `true` mid-run.
- A **running log** of one-line-per-pass summaries returned by each pass's subagent.

Before pass 1, snapshot every participant's starting state from inside the worktree — this is what
lets Step 4 report only what changed *this run*, not each character's whole history:

```bash
py scripts/lore/simulate_tally.py snapshot <slug1> <slug2> ... --out .simulate_snapshot.json
```

It writes `.simulate_snapshot.json` at the worktree root; Step 4 reads that same path back.

For pass 1 through N:

1. If fewer than 2 living participants remain, stop early and say so, noting how many passes
   actually ran before the pool ran out.
2. Pick 2 participants from the living pool with
   `py scripts/lore/pick_pair.py <every slug still in the living pool>` — a genuine uniform draw,
   not the model's own guess at "random" (which skews toward whichever names are most salient in
   context rather than drawing evenly). Every pass is an independent draw — pairs can repeat, and
   should be expected to over a long run.
3. Dispatch one subagent (Agent tool, `subagent_type: general-purpose`, the model chosen in Step 1,
   `run_in_background: false` — the next pass needs this one's file writes to have landed first).
   Brief it self-contained, since it starts with no memory of this conversation:
   - The worktree's absolute path — every file read/write and every `py scripts/lore/...` call must
     use it explicitly, never an assumed working directory. This includes the rule-pointer file below:
     give its full absolute path inside the worktree (`<worktree>/.claude/skills/enact/SKILL.md`),
     never a bare relative one, and read it with the `Read` tool, never a shell `cat`/`Get-Content`
     fallback. A subagent's actual working directory is not guaranteed to match the parent
     conversation's; a relative path can silently resolve outside wherever its real cwd turns out to
     be, and the `Read` tool is never gated for paths *inside* the working directory — only for paths
     it resolves as outside it, which is what a permission prompt on a plain file read means when it
     happens.
   - Both participants' names, and that **both already have character files** — Step 1/2's
     interactive questions and the name-uniqueness check are for new characters only and don't apply
     here. It should still: check `life.deceased` before starting, run `horizon.py` for each per
     Step 1's "Criterion and lifespan" rules, and run Step 3b in full (character vs. character, one
     message, alternating turns, natural stopping point — no player is present).
   - The scenario context from Step 1, if one was given; otherwise instruct it to invent a situation
     grounded in what both characters could plausibly know.
   - **Never call `AskUserQuestion` or wait on a live user** — there isn't one. Make the same calls
     `/enact` would normally ask about (whether the scene has reached a natural stopping point, how a
     shock resolves) autonomously, and note any non-obvious judgment call in its final report.
   - **If any tool call fails for any reason — a `py scripts/lore/...` call, a file read, anything —
     report the exact error and stop that pass. Never retry it via a different shell, tool, or method
     (PowerShell instead of Bash, `cat`/`Get-Content` instead of `Read`, bare `python` instead of
     `py`, etc.).** Confirmed the hard way: a `py` script failure that fell back to the PowerShell tool
     is what surfaced a live permission prompt mid-run, even with `bypassPermissions` set — the exact
     mechanism isn't fully pinned down, but switching tools/methods after a failure is the one thing
     observed to break the "no prompts, ever" guarantee, so it's banned outright rather than trusted a
     second time. Bare `python` is confirmed not on PATH in this environment — always use `py`.
   - Run Steps 5, 5b, and 6 **in full** — hearsay mutation, shock resolution, drift, the record
     update. This is the actual mechanism being exercised; nothing here gets shortened for speed.
   - Report back *only* a short summary, not the transcript: both participants, a one-line gist of
     the scene, whether either's criterion changed (and how), whether either died this pass.
4. Append that one-line summary to the running log — this is what keeps a long run affordable: the
   main thread accumulates summaries, never the 50 full transcripts and record-keeping writeups.
5. If either participant died this pass, drop them from the living pool before the next draw.

## Step 4 — Summarize

Once all passes are done (or the pool ran out early):

- Run the tally script against the snapshot Step 3 wrote, rather than hand-counting deaths and
  criterion moves from the running log's one-liners:
  ```bash
  py scripts/lore/simulate_tally.py report .simulate_snapshot.json
  ```
  It diffs every participant's current `_lore/characters/<key>.json` against where they stood before
  pass 1, so the deaths, criterion-move counts, and final `life.lived` come straight from the record
  rather than being reconstructed from memory of up to N pass summaries.
- Write `SIMULATION_LOG.md` at the worktree root: the Step 1 setup (participants, pass count,
  context, model), the pass-by-pass one-liners in order, and the tally script's output as the closing
  section.
- Tell the user: how many passes ran, headline events, the worktree's path and branch name, and that
  it stays on disk untouched by anything here — nothing in the original working directory changed.
  They can `/enact` a character from inside this worktree, read any file directly, ask questions
  about what changed, or run `/simulate` again (after exiting this worktree, or from a different
  session) for an independent second trial off the same starting state, to compare against this one.
- Don't call `ExitWorktree` — only on explicit request, same as Step 0.

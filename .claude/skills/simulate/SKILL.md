---
description: Batch-run many /enact character-vs-character scenes across an existing population, in an isolated git worktree, to see how the lore state (hearsay pool, criteria, lifespans, deaths, arcs, population) evolves over a number of passes without touching the real files. Use for testing the enactment mechanism at scale or for producing a showcase trail of scenes — never for a single one-off scene, that's /enact directly. This skill is nothing but orchestration around /enact — pairing, worktree isolation, batching — it owns none of the scene mechanics itself any more. For mechanically pregenerating a large starting population instead of a showcase trail of prose, that's /generate, a separate command.
disable-model-invocation: true
---

Pure orchestrator over `/enact`, run unattended and repeatedly inside a dedicated worktree — every
pass is one full `/enact` run between two already-existing characters, nothing more. Lore-only, same
as `/enact` and `/character` — never touches `data/` or `_npcs/`. Read
`.claude/skills/enact/SKILL.md` before running this if it hasn't been read yet this session; this
skill points back at its rules rather than restating them, and only spells out where it deviates (no
interactive questions inside a pass, existing participants only, absolute paths into the worktree).

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
   replacement. **Also check `routines`+`arc` completeness on each** — every pass now runs through
   `/enact`'s own Step 2 eligibility gate, which requires both non-negotiably (no more freeform
   fallback for a participant missing them). Point at `/character` to complete a participant who's
   missing either (it can be re-run on an existing character for exactly this — see its Step 2a) or
   drop them from this run, same as the deceased-check rule just above. Need at least 2 living,
   eligible participants to proceed at all.
2. **Passes** — how many scenes to run in total, e.g. 50.
3. **Context** — optional free text: a scenario/situation to feed into every scene (e.g. "these all
   happen during the Feria"). Leave blank for random — each pass then invents its own plausible
   situation, bounded by what both participants in it could actually know.
4. **Model** — which model plays each pass (Haiku / Sonnet / Opus), default Sonnet if not asked.
   Quality matters more here than in a one-off `/enact`, because a pass's Step 8 judgment calls
   (criterion shock resolution, hearsay mutation) become the input the *next* pass reads — errors
   compound across a run in a way they don't in a single scene. This only affects the per-pass
   subagent below; the orchestration in this skill itself (pairing, logging) runs at whatever model
   this conversation is already on.
5. **Pregenerate first? (optional, `--pregenerate`)** — only ask if the user's request suggests
   wanting a bigger starting cast before the showcase trail begins (e.g. "grow the population a bit
   first", "I want more characters in the mix"). Default: no, skip straight to Step 2. If yes: which
   pool to grow from (can differ from this step's own Participants — that pool only needs
   `routines`, per `/generate`'s own Step 1 check) and how many mechanical passes to pregenerate.
   This folds `/generate`'s own mechanism in as an optional first phase of an ordinary run (Step 2h
   below) instead of requiring a separate `/generate` invocation and a second session to use its
   output — same mechanism, same scope differences (no scene prose, deferred name/arc-content
   authoring batched into one subagent pass), just run inline before Step 3 begins rather than as
   its own standalone command.

## Step 2 — Create the worktree

Every pass in Step 3 dispatches a subagent that runs several `py scripts/lore/...` calls (each by full
absolute path — see Step 3's "never use `cd`" rule) plus file reads/writes — dozens of routine tool
calls per pass, times N passes. Without a permission bypass in place *before* any of that runs, each
one prompts the user, which defeats the entire point of an unattended batch run.

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

**`defaultMode: bypassPermissions` alone is not sufficient — four more gaps, all now closed by the
script, are worth knowing about if a run still stalls:**
1. Dispatching a subagent (the `Agent` tool) can still prompt on its own even with the bypass active
   for ordinary Bash/Read/Write in the same directory — the script adds an explicit `"Agent"` allow
   entry (and `skipWorkflowUsageWarning: true`) to close this.
2. A Bash command combining `cd <path> && <command>` is hard-blocked by a security guardrail
   ("Compound command contains cd with path operation") that **no permission setting can ever
   override**. This is not a settings problem — it's a behavioral one. See Step 3's "never use `cd`"
   rule below; every `scripts/lore/*.py` file resolves its own root via
   `Path(__file__).resolve().parent.parent.parent`, so `cd` is never actually needed to invoke them
   correctly, regardless of the shell's cwd.
3. A subagent can mistype the long absolute worktree path when re-deriving it from memory across many
   tool calls (observed: a lore-salient word silently substituted for the real folder name in a Read
   call), which then prompts for a new, unrecognized path.
4. A subagent can reach for the **PowerShell tool instead of Bash** on this Windows environment as its
   *first* choice, not merely as a fallback after a Bash failure — a wholly separate tool with its own
   permission gate that a `"Bash"` allow entry does not cover.
5. **`.claude/` gets its own extra protection that a bare `"Write"`/`"Edit"` allow does not cover**,
   even under `bypassPermissions`. Observed: a subagent wrote a scratch JSON file into the worktree's
   own `.claude/` directory (see Step 3's "never write scratch files there" rule — that choice was the
   subagent's own mistake), and that single write triggered a prompt despite a dozen prior passes'
   worth of ordinary `Write` calls elsewhere in the same worktree working cleanly. This is by design —
   `.claude/` is the harness's own config/skills/permissions directory — and matches what the harness's
   own `update-config` skill documents as the correct pattern (`"Edit(.claude)"` as a distinct rule from
   a general `Edit` allow), not a bug to route around some other way.

The script closes all five the same way: blanket-allow **every tool this skill's subagents could
plausibly reach for**, plus explicit `.claude`-scoped entries per point 5 —
`Read`/`Write`/`Write(.claude)`/`Write(.claude/**)`/`Edit`/`Edit(.claude)`/`Edit(.claude/**)`/`Bash`/
`PowerShell`/`Glob`/`Grep`/`Agent`/`Skill`/`Task*` — rather than adding one entry at a time as each gap
surfaces. `bypassPermissions` is already the harness's most permissive mode; there is no single broader
toggle that also covers the handful of actions (subagent spawn, `.claude/` writes) it deliberately still
gates by design — enumerating every tool comprehensively, as done here, **is** the correct "no prompts,
ever" fix for those. A typo'd path or an unexpected tool choice now fails cleanly with an ordinary tool
error instead of blocking on a prompt — safe here specifically because this is a disposable, isolated
worktree, never the directory the user actually works in. Deliberately NOT included: anything with no
role in this lore-only, no-network procedure (`WebFetch`, `WebSearch`, browser/MCP tools, scheduling,
`EnterWorktree`/`ExitWorktree`) — broadening those would be an unrelated expansion of trust, not a fix
for anything this skill actually does.

If prompts still fire during Step 3 despite all of the above, the fix is to end the session and start a
new one that calls `EnterWorktree` with `path` pointed at the already-existing worktree — a fresh
session's config load will pick up the settings file that's already sitting there even if the one
that created it couldn't. Passes already completed are safe either way; they're written straight to
disk in the worktree as each one finishes, per Step 3.

**Worktree naming and Windows' 260-char path limit:** this repo has hit this before (see
`f3e4fbd`'s `.venv` untracking) and the setup script's own worktree path can push some of the repo's
already-deeply-nested files over the limit purely from the *name* being a few characters longer — 
confirmed the hard way: `--name simulate-permtest2` (one character longer than a name that had just
worked) made `git worktree add` fail outright with dozens of "Filename too long" errors, while the
shorter name succeeded cleanly. Prefer the script's own default name (`simulate-<YYYYMMDD-HHMMSS>`,
already about as short as a collision-safe name can be) over a custom `--name` unless there's a real
reason to pick one, and if `git worktree add` fails this way, that's the first thing to suspect — not
a settings or permissions problem.

A fresh worktree per run is what makes repeated runs independently comparable against the same
starting lore state — report the path and branch to the user once created. Everything from here
happens inside that worktree's copy of the repo; the original working directory is untouched.

## Step 2h — Optional pregeneration (only if Step 1 point 5 asked for `--pregenerate`)

Runs the exact mechanism `.claude/skills/generate/SKILL.md` documents (its Steps 1/3/4/5), inline,
inside the SAME worktree Step 2 just created — never a second worktree, never a second session.
Skip this step entirely if Step 1 didn't ask for it.

1. Confirm every character in the pregeneration pool has a non-empty `routines` array (`/generate`
   Step 1's own check) before running anything.
2. Run `/generate` Step 3's mechanical loop exactly as documented, with one addition — pass
   `--living-pool-out` so the resulting pool doesn't have to be retyped from stdout:
   ```bash
   py "<worktree>/scripts/lore/simulate_generate_population.py" --pool <slug1> <slug2> ... \
       --passes <N> --living-pool-out "<worktree>/.living_pool.json"
   ```
3. Run `/generate` Step 4 exactly as documented (the one batched language-layer subagent) and Step 5
   exactly as documented (`apply_language_layer.py`).
4. Read `<worktree>/.living_pool.json` back (the slugs Step 3's loop still had alive at the end,
   after any deaths and any now-eligible births during that mechanical run). **Union this into Step
   1's own participant list** for the showcase-trail passes about to start in Step 3 below — the
   user doesn't have to re-name everyone who's now part of the cast; Step 1's originally-named
   participants are guaranteed included in this union even if the pregeneration pool was a different
   (or overlapping) set of names.
5. Tell the user, briefly, what pregeneration produced (passes run, births, population size) before
   moving on to Step 3 — the same summary `/generate` Step 6 would give if this had been a standalone
   `/generate` run, just folded into this run's own narration rather than a separate report.

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
2. Resolve this pass's pair, one call, absolute path:
   ```bash
   py "<worktree>/scripts/lore/simulate_resolve_pair.py" --pool <every slug still in the living pool> --pass-number <N>
   ```
   A genuine uniform draw over the pool (not the model's own guess at "random," which skews toward
   whichever names are most salient in context), plus the lead-override check (an unexpired `leads`
   entry on the drawn participant_1, younger than `lead_expiry_passes` — 8, from `_lore/tuning.json`
   — forces this pass to `participant_1` visiting that lead's target instead, consuming the lead).
   Prints `participant_1`, `participant_2`, and `forced_visit` — keep all three for point 3 below.
   Every pass is an independent draw; pairs can repeat, and should be expected to over a long run.
3. Dispatch one subagent (Agent tool, `subagent_type: general-purpose`, the model chosen in Step 1,
   `run_in_background: false` — the next pass needs this one's file writes to have landed first) to
   run one full `/enact` scene between the two participants point 2 resolved. Brief it self-contained,
   since it starts with no memory of this conversation:
   - The worktree's absolute path — every file read/write and every `py scripts/lore/...` call must
     use it explicitly, never an assumed working directory. This includes the rule-pointer file below:
     give its full absolute path inside the worktree (`<worktree>/.claude/skills/enact/SKILL.md`),
     never a bare relative one, and read it with the `Read` tool, never a shell `cat`/`Get-Content`
     fallback. A subagent's actual working directory is not guaranteed to match the parent
     conversation's; a relative path can silently resolve outside wherever its real cwd turns out to
     be, and the `Read` tool is never gated for paths *inside* the working directory — only for paths
     it resolves as outside it, which is what a permission prompt on a plain file read means when it
     happens. Tell it explicitly to copy the worktree path string literally rather than re-deriving it
     from memory on each call — a smaller model can silently substitute a lore-salient word for part of
     the real path (observed once: "Lundria" for "Luminacion") when the path is long and the model's
     context is full of in-world names; Step 2's broadened `Read`/`Write`/`Edit`/`Bash` allow entries
     mean a typo like that now fails cleanly instead of blocking on a prompt, but it still wastes the
     pass, so ask for care regardless.
   - **Any scratch/temp file it needs (e.g. the JSON payload for `record_hearsay.py --json-file`)
     goes at the worktree root, never inside `<worktree>/.claude/`.** `.claude/` is the harness's own
     config/skills/permissions directory, not a data workspace — a stray write there can trigger its
     own permission prompt even when ordinary `Write` calls elsewhere are working cleanly (observed
     once). The worktree root already holds `.simulate_snapshot.json` for the same reason; scratch
     files belong alongside it.
   - **Use the Bash tool for every shell command — never the PowerShell tool, not even as a first
     choice on this Windows environment.** Both tools are available, but this skill's whole discipline
     (`py`, never `python`; absolute paths, never `cd`) is written and tested against Bash only, and
     switching tools mid-run is separately banned below for good reason. Say this explicitly, since a
     model can otherwise reach for PowerShell by default on Windows without ever having failed at
     anything first.
   - **Never use `cd`, under any circumstances — not even as its own standalone command.** A Bash
     command combining `cd <path> && <command>` is hard-blocked by a security guardrail no permission
     setting can override; it is never worth the risk of the model reaching for it.
   - **`py scripts/lore/<name>.py` — call it ONLY by the full absolute worktree path, never a bare
     relative one, not even once.** This is not just a style preference: a subagent's Bash cwd is not
     guaranteed to be inside the worktree at all (it may default to the main repo checkout instead), and
     `Path(__file__).resolve().parent.parent.parent` — the trick every `scripts/lore/*.py` file uses to
     find its own project root — is exactly what makes a relative call dangerous rather than safe: if
     the relative path resolves against the *main checkout's own copy* of the script (because that's
     where cwd happened to be), that copy's `__file__` correctly-but-wrongly points at the *main
     checkout's* `_lore/`, and the write lands there instead — silently, with no error, since the script
     ran successfully by every measure it can see. **Confirmed the hard way:** one pass's
     `record_hearsay.py`/`update_character.py` calls did exactly this, writing real scene content into
     the user's actual `_lore/characters/*.json`, `hearsay.md`, and `encodings.json` — discovered only
     because the pass's own after-the-fact verification checked the *worktree's* copy, found the entry
     missing there, and reported a false "silent script failure" instead of the true cause. Always give
     the full absolute path: `py "<worktree>\scripts\lore\record_hearsay.py" --json-file "<worktree>\...\file.json"`
     — never `py scripts/lore/record_hearsay.py ...`.
   - **Run `/enact` Step 2 onward for these two, exactly as that skill defines it** — both already
     have character files, so skip Step 1's brand-new-character branch (the name-uniqueness check
     and the creation questions), but still run its "Criterion and lifespan" checks. Pass point 2's
     `forced_visit` through as `--forced-visit` on `/enact` Step 4's `simulate_pass_brief.py` call if
     it read `true`; omit the flag otherwise. Follow every rule in `/enact`'s own file as written — the
     mechanical block, the eligibility gate (already guaranteed to pass, since this skill's own Step 1
     already filtered the pool to eligible participants, but the subagent should still trust
     `/enact`'s own check rather than skip it), the judgment slots, hearsay, shock/drift, the record
     update. This is the actual mechanism being exercised; nothing here gets shortened for speed.
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
   - **After `record_hearsay.py` reports success, verify it actually landed** — read the tail of
     `<worktree>/_lore/characters/hearsay.md` (or check the entry count) and confirm the new entry is
     really there before trusting the script's own stdout. **If it's missing from the worktree's copy,
     do not assume the write silently failed** — check whether it landed in the *main repo's* copy
     instead (the relative-path leak explained above is exactly this symptom: the script succeeds, the
     entry exists, just in the wrong repository). Either way, report the exact finding and stop the
     pass per the rule below rather than retrying or guessing.
   - Report back *only* a short summary, not the transcript: both participants, a one-line gist of
     the scene, whether either's criterion changed (and how), whether an arc advanced/resolved,
     whether a birth or death happened this pass.
4. **Safety net — before trusting the pass's report, check it didn't leak into the real repo:** run
   `git -C "<main repo root, NOT the worktree>" status --short -- _lore/ _npcs/` (no `cd` — `git -C`
   targets a foreign path directly in one command and is not subject to the compound-cd block, and this
   works from inside the worktree). Any output at all means this pass wrote into the user's real files
   — confirmed possible via the relative-path leak explained in point 3 above, seen three times in one
   run at roughly a 1-in-10 pass rate despite maximal prompt hardening: twice as a partial leak (only
   some of the pass's script calls went to the wrong repo) and once as a total leak (the *entire* pass —
   reads included — ran against the main checkout, leaving the worktree's own copy of both characters
   completely untouched).
   - **Revert automatically, every time, without asking — this is a standing rule, decided 2026-08-09
     after the third occurrence.** `git checkout -- <the exact leaked paths only>` in the main repo
     (list them explicitly; never a bare `git checkout .`), plus `rm` any newly-untracked leaked file
     under `_npcs/scenes/`. Never touch any other file in that diff — a separate, unrelated concurrent
     session may be editing the same shared checkout at the same time (confirmed happening during the
     incident that established this rule). Log the revert in the running log for Step 4's summary, but
     do not stop the run or ask the user — the fix is fully mechanical at this point.
   - **Check whether the worktree itself actually received this pass's writes** (e.g. `life.lived` on
     both participants' files under the worktree, or the scene transcript under
     `<worktree>/_npcs/scenes/`) — a *partial* leak still leaves real progress in the worktree and this
     pass counts as done; a *total* leak (worktree completely untouched, as in the incident above) means
     this pass never actually happened from the simulation's point of view and must be run again with a
     fresh subagent dispatch (same participants and context are fine to reuse) before moving on, rather
     than being counted toward the pass total.
5. Append that one-line summary to the running log — this is what keeps a long run affordable: the
   main thread accumulates summaries, never the 50 full transcripts and record-keeping writeups.
6. If either participant died this pass, drop them from the living pool before the next draw. If a
   birth happened this pass, add the child to the pool once the current pass number reaches
   `birth_pass + child_cooldown_passes` (`generate_offspring.py` prints the exact threshold).

At the natural end of a batch (the run's requested pass count is reached, or the session is otherwise
wrapping up) — not after every single pass — run `py scripts/lore/build_source_index.py` once, so
every concept registered this batch gets its accumulated hearsay claims folded into its own
`sources[]`, the same absorption a separate `/integrate` pass would eventually do anyway.

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
- **Append a "Narrative report" section** (standing requirement, added 2026-08-10 on request) —
  prose, not another mechanical recap: for each participant's arc, how it actually developed across
  the run (the shape of it - steady, volatile, stalled, resolved), what changed in their
  relationships to each other, any criterion moves and what prompted them, and an honest account of
  what didn't happen (deaths, reproductions, resolutions) alongside what did. This is the section a
  person would actually want to read to know what this slice of the world's history was about: write
  it that way, grounded in the specific pass-by-pass facts already on record above it, not invented
  beyond them. Required every time this step runs, not only when a run happens to feel eventful.
- Tell the user: how many passes ran, headline events, the worktree's path and branch name, and that
  it stays on disk untouched by anything here — nothing in the original working directory changed.
  They can `/enact` a character from inside this worktree, read any file directly, ask questions
  about what changed, or run `/simulate` again (after exiting this worktree, or from a different
  session) for an independent second trial off the same starting state, to compare against this one.
- **If this run was testing or extending the system's design** (not a casual one-off), append a dated
  entry to `LAB_REPORT.md` at the **main repo root** — read that file's own header for the expected
  entry shape first. **Do this only from the orchestrating session, using the file's absolute main-repo
  path** (the same pattern as the Step 3 safety net's `git -C "<main repo root>"`), **never by writing
  it from inside the active worktree.** This is a deliberate, single, explicit write to a known
  meta-file at the very end of a run — unlike the accidental relative-path leaks Step 3's safety net
  exists to catch and revert, this one is intentional, so it's fine for it to land in the main repo. If
  the run surfaced a design gap or an open question rather than a settled answer, log it under that
  file's "Open design questions" section rather than only leaving it in chat history.
- Don't call `ExitWorktree` — only on explicit request, same as Step 0.

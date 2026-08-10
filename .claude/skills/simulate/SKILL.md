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

## Step 3 (extended mode) — Routines, arcs, and material consequence

**Applies automatically whenever any participant's character file has a non-empty `routines`
array** — no separate setup question needed, since the mechanic can't run without that data
existing. If none of this pass's participants have `routines` populated, skip straight to the base
"Step 3 — Run passes" below instead.

**Governing principle (design debrief, 2026-08-10): keep the subagent's judgment to a minimum.**
Every decision in the sequence below that can be made mechanically already is - by a script, a
dice roll, or plain arithmetic over numbers already on record. The subagent's job is narrower than
in a base-mode pass: it writes the words that dramatize a sequence of facts that are **already all
decided before it starts writing**, the same way it already can't decide whether a criterion breaks
mid-scene. There are exactly two places a model's judgment is the right tool instead of a script,
called out explicitly where they occur below - composing a plausible name-blend for a newborn
character, and picking the actual words of the scene itself. Nothing else in this sequence should
be left to the subagent to decide.

Run this sequence in full, in order, for every pass in extended mode - it replaces the base Step
3's pairing-through-dispatch logic; Step 3's "Never call `AskUserQuestion`", "never use `cd`",
absolute-path, and safety-net rules below all still apply unchanged.

**Every number below (odds, thresholds, cooldowns) lives in `_lore/tuning.json`, read via
`scripts/lore/tuning.py` - the numbers stated here are what's in that file as of this writing, not
a second copy to keep in sync by hand. If the file has been retuned, its values win; re-read it
rather than trusting this prose.**

1. **Pairing** (unchanged): `pick_pair.py` draws participant_1/participant_2 from the living pool,
   exactly as base mode does.
2. **Lead override check** (mechanical - only relevant if participant_1 has a `leads` array with
   any entry younger than `lead_expiry_passes` (8) passes; prune anything older first, plain
   arithmetic, no roll needed).
   If any unexpired leads remain: `roll_lead_followup.py --leads <target1> [<target2> ...]`. If
   `followed: true`, override participant_2 to the rolled lead's target, remove that lead from
   participant_1's `leads`, and force `mode: visit` (skip step 4's location resolution - it's
   already decided: participant_1 is seeking participant_2 out). Otherwise proceed with
   participant_2 exactly as `pick_pair.py` drew it.
3. **Routine rolls** (mechanical): `roll_routine.py` for participant_2 always. `roll_routine.py`
   for participant_1 too, unless step 2 already forced a visit (then skip - participant_1's
   routine is irrelevant this pass, they deliberately left it).
4. **Location resolution** (mechanical, skip if step 2 already forced a visit): `resolve_location.py`
   with both rolled routines -> `mode`/`location`/`home_frame`/`traveler`.
5. **Archetype lookup** (mechanical, plain read - no script): read `_lore/archetypes.json` for the
   archetype tagged on whichever participant's routine entry matches the resolved `location`, for
   its `texture` (context to hand the subagent) and `provides` tags.
6. **Needs/provides check** (mechanical, only for `mode: visit`, and only if the traveler currently
   has an arc): `check_needs_provides.py --needs <traveler's arc.needs...> --provides <step 5's
   provides tags...>`. A match means this visit gets framed as motivated - tell the subagent why,
   using the matched tags directly, not an invented reason. No match: ordinary, unmotivated visit.
7. **Arc primacy roll** (mechanical): `roll_arc_primacy.py --p1 <participant_1> --p2
   <participant_2>` decides whose arc, if either, is even in play this scene. Replaces the old
   host-only rule outright.
8. **Knowledge/criteria gate** (mechanical, only if the primacy winner has an active arc):
   `check_arc_alignment.py --arc-about <primary's arc.about...> --arc-needs <primary's
   arc.needs...> --peer-standard "<other participant's criterion.standard>" --peer-wasted-life
   "<other participant's criterion.wasted_life>" --peer-knowledge-item "<text>::<about tags>" ...`
   (one `--peer-knowledge-item` per entry in the other participant's `knowledge.experience` that
   carries an `about`/tag reference; cap at the ~15 most recent if that list is long, to keep the
   call reasonable). Output: `gate: hit/miss`, `inclined: help/hinder/mixed/neutral`, and (if hit)
   `matched_about` - the specific tags a transform would need later.
9. **Contested check** (mechanical, only if step 6 matched): `roll_contested.py` (odds from
   `_lore/tuning.json`'s `odds_percent.contested`, 15 as of this writing). If
   `contested: true`, the resolution is a **fixed lookup over step 8's `inclined` value, not a new
   judgment call**: `help` -> the visitor's claim wins despite the contest; `hinder` -> the prior
   claim holds, the visitor doesn't get it this pass; `mixed`/`neutral` -> split or deferred (a
   partial or delayed version). A rival only gets **named** in the scene if
   `_lore/characters/<slug>.json` already exists for them (plain file-existence check) - otherwise
   keep it ambient/unnamed, same as the default case. If named and the lookup resolved `hinder`:
   append a `leads` entry (`{target: <rival slug>, created_pass: <N>}`) to the traveler's own file,
   and write one attributed note to the *rival's own* `knowledge.experience` (never invented prose -
   use exactly: `"According to <supplier>, <rival> already claimed <matched_provide> before
   <traveler> arrived."`), so whoever plays the rival later has this on record instead of
   improvising it fresh.
10. **Arc outcome roll - MUST run and be known before the scene is written** (mechanical, only if
    step 8's gate hit): `roll_arc_outcome.py --inclined <step 8's value, or step 9's lookup result
    if contested overrode it>` -> `advance`/`stall`/`reverse`. Hand this to the subagent as an
    already-decided fact to dramatize. Writing the scene first and rolling after is not an
    acceptable substitute ordering - see the script's own docstring for why.
11. **Tally and threshold** (mechanical arithmetic, no script - sum `arc.history` outcomes,
    advance=+1/stall=0/reverse=−1, from the most recent `"transform"` entry onward, or from the
    start if none, including this pass's new outcome; threshold is `_lore/tuning.json`'s
    `arc_resolution_threshold`, 3 as of this writing):
    - Sum >= +threshold -> `resolution: "complete"`.
    - Sum <= −threshold **and** step 8 gate-hit on this exact pass -> **transform**: set
      `arc.about` to step 8's `matched_about` tags, append a `{"outcome": "transform", ...}`
      history entry, `resolution` stays `"ongoing"`. The new topic is copied mechanically from what
      already matched - nothing here is composed freely.
    - Sum <= −threshold and no gate hit this pass -> `resolution: "failed"`. A fresh arc gets
      authored (archetype + personal specialization + criterion, scoped against `horizon.py`'s
      band - see `.claude/skills/character/SKILL.md`) the next time this character wins a primacy
      roll as home_frame.
12. **Partner tracking** (mechanical, always, both directions): `record_partner.py <p1> --with
    <p2>` and `record_partner.py <p2> --with <p1>`.
13. **Reproduction eligibility + roll** (arithmetic, then one roll - only if step 12 just crossed
    either direction's count to `>= partner_threshold` (5) **and** neither participant's
    `last_reproduced_pass` is within the last `parent_cooldown_passes` (10) passes -- both from
    `_lore/tuning.json`): `roll_reproduction.py --p1 <p1> --p2 <p2>` (odds from
    `odds_percent.reproduction`, 40 as of this writing). If `reproduces: true`, this is the **first
    of the two places a model's judgment belongs**: the roll's own `name_lead` output already
    decided mechanically which parent's name leads the blend - the subagent's only job is composing
    a name that reads as a plausible blend starting from that parent's name (not a script's job -
    see `generate_offspring.py`'s own docstring for why), then run `generate_offspring.py
    --parent-a <p1> --parent-b <p2> --name "<composed name>" --pass-number <N>` (the slug is
    derived from the name automatically, not a second thing to decide). This also writes a direct
    `knowledge.experience` line to both parents and notifies 30% of their combined circle, the same
    shape as `record_death.py`'s own notification - the child only enters `pick_pair.py`'s eligible
    pool once the current pass number reaches `birth_pass + child_cooldown_passes` (5, **distinct
    from** the parent cooldown above - the script prints the exact threshold, so this never needs
    computing by hand) - track this the same way the living pool itself is tracked in Step 3 base
    mode.
14. **Write the scene - the subagent's other legitimate judgment call.** Every fact above is
    already fixed: who, where, whether motivated and why, whether contested and how it resolves,
    whether the arc advances/stalls/reverses/transforms, whether a birth is happening and what name
    it needs. The subagent's job is picking the actual words that dramatize all of it - nothing
    more. `/enact` Steps 5, 5b, and 6 still run underneath this in full (hearsay mutation, criterion
    shock, drift) exactly as base mode requires - this sequence sits on top of that, not instead of
    it.
15. **Death check** (existing mechanism, unchanged): `horizon.py` per participant after `life.lived`
    increments; `ending: true` -> `record_death.py` (already computes the circle, notifies 30%,
    flags shock candidates whose `criterion.anchor` references the deceased for the existing
    `/character` Step 6 judgment call - this already covers "criterion checked against close ones").
    Note the `band` `horizon.py` reported at this exact call - needed by step 16.
16. **Death-legacy check** (mechanical, only if step 15 fired): "died early" = step 15's noted band
    read `"established"` rather than `"late"` (a rolled span can never sit below the world-normal
    range's floor, so `"early"` is structurally impossible at the exact pass death fires - this
    comparison is the correct proxy, not a new threshold). If early: `roll_death_legacy.py
    --candidates <record_death.py's notified list>` (odds from `odds_percent.death_legacy`, 40 as
    of this writing). If `passes: true`, apply the same
    mechanical copy a transform uses to the recipient's own arc (about/needs copied from the
    deceased's arc, `resolution` reset to `"ongoing"`, tally reset) - archetype/routine stays the
    recipient's own.
17. Append the pass's one-line summary to the running log, same as base mode. If either participant
    died this pass, drop them from the living pool before the next draw (base mode's existing rule,
    unchanged).

## Step 3 — Run passes

**If extended mode (above) applies to this pass's participants, use that sequence instead of the
one below.**

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
   - **After `record_hearsay.py` reports success, verify it actually landed** — read the tail of
     `<worktree>/_lore/characters/hearsay.md` (or check the entry count) and confirm the new entry is
     really there before trusting the script's own stdout. **If it's missing from the worktree's copy,
     do not assume the write silently failed** — check whether it landed in the *main repo's* copy
     instead (the relative-path leak explained above is exactly this symptom: the script succeeds, the
     entry exists, just in the wrong repository). Either way, report the exact finding and stop the
     pass per the rule below rather than retrying or guessing.
   - Report back *only* a short summary, not the transcript: both participants, a one-line gist of
     the scene, whether either's criterion changed (and how), whether either died this pass.
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
6. If either participant died this pass, drop them from the living pool before the next draw.

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

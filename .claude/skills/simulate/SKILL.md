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
4. **Model** — which model plays each pass: **Haiku / Sonnet / Opus** (all via the Agent tool, a
   Claude subagent), or **Local (Ollama, `qwen2.5:14b`)** — a plain script call instead of a
   subagent, see Step 3 point 4. Default Sonnet if not asked. Quality matters more here than in a
   one-off `/enact`, because a pass's Step 8 judgment calls (criterion shock resolution, hearsay
   mutation) become the input the *next* pass reads — errors compound across a run in a way they
   don't in a single scene. **The Local path is newer and less proven** — validated so far only on
   two hand-built test passes outside a real run (see `CHRONICLE.md`'s 2026-08-30 entry): dialogue
   quality and exact `about`-tag copying held up both times, but its harder judgment calls (which
   claims are kernels worth recording, when a `criterion_move` is a genuine test of an anchor versus
   just an affirmation of it) haven't been exercised at scale the way the Claude path has across
   hundreds of prior passes. Worth reading the running log more closely than usual for the first
   several passes of any run that picks it. This only affects the per-pass dispatch below; the
   orchestration in this skill itself (pairing, logging) runs at whatever model this conversation is
   already on.
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
6. **RNG seed (optional, test suite)** — only ask if the user's request suggests they want a
   reproducible/comparable run (e.g. "run the isolation experiment," "seed this the same as last
   time," building a divergence comparison). Default: none (a free/unseeded run — today's exact
   behavior, unchanged). If given, this is the isolation experiment's seeded pair: identical world
   seed (this same starting commit) + identical RNG seed reproduces identical mechanical records,
   isolating whatever differs to the agent layer — see `TESTING_BRIEF.md` (vault-side
   `projects/provenance/`) for why this matters and `scripts/test/measure_divergence.py` for how it
   gets measured. Also ask for a **mode** label (`simple`/`divergence`, default `simple`) — recorded
   on the manifest only, not a different code path here.

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

**Note the current UTC timestamp right now, before anything else in this step** (e.g. `date -u
+%Y-%m-%dT%H:%M:%S.000Z`) and keep it in this conversation only — Step 4's token-usage bullet needs it
as the window's start. Cheap to note, easy to forget once passes start.

Before pass 1, snapshot every participant's starting state from inside the worktree — this is what
lets Step 4 report only what changed *this run*, not each character's whole history:

```bash
py scripts/lore/simulate_tally.py snapshot <slug1> <slug2> ... --out .simulate_snapshot.json
```

It writes `.simulate_snapshot.json` at the worktree root; Step 4 reads that same path back.

Right alongside it, write the run manifest (test suite — see `TESTING_BRIEF.md`, vault-side
`projects/provenance/`): the machine-readable record of this run's exact starting state, so "same
world seed" is a well-defined, comparable object later. Pass `--seed` only if Step 1 point 6 asked
for one — omitting it is a free/unseeded run, today's exact behavior:

```bash
py "<worktree>/scripts/lore/run_manifest.py" write --pool <slug1> <slug2> ... --passes <N> --mode <simple|divergence> [--seed <N>]
```

Also clear the reproduction cooldown's two absolute-pass-number scalars (`last_reproduced_pass`,
`birth_pass`) for every participant, right here, before pass 1 — a fresh run's own pass counter always
starts at 1 regardless of the branched-from commit's own history, so a stale value from whatever
earlier run wrote it reads as "had a child hundreds of passes in the future," wrongly blocking
reproduction until this run's own count coincidentally exceeds that old absolute number:

```bash
py "<worktree>/scripts/lore/reset_reproduction_cooldown.py" --pool <slug1> <slug2> ...
```

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
3. **Run the mechanical prep yourself, in the orchestrating session, absolute paths, Bash only, never
   `cd`:** `py "<worktree>/scripts/lore/pass_prep.py" --p1 <slug> --p2 <slug> --pass-number <N>
   [--forced-visit]` — wraps `horizon.py` (both participants), the whole `simulate_pass_brief.py`
   mechanical block (survival roll/apply, arc gate, criterion-move gate check, everything /enact Step
   4 decides), AND (added 2026-08-29, round-3 debrief) each participant's own `criterion` and, if they
   have one, their arc's `premise`/`about`/`needs` — into one call. Prints the pre-scene horizon, the
   full brief, and this `characters` block as one JSON object. This is now the *complete* input the
   enacter needs; nothing else has to be separately fetched, composed, or looked up. If the brief's
   `arc_authoring_needed` is non-null, author that arc yourself (`premise`/`context`/`about` are a
   name-blend-shaped judgment call, not a dice roll — same reasoning `generate_offspring.py`'s own
   docstring gives for why it can't script a child's name) and call `write_arc.py` directly before
   continuing this pass. **`needs` is different — mechanized 2026-08-31, on user correction after six
   consecutive arc re-authorings in one run all converged on `needs: ["news"]` regardless of topic:
   pick `needs` from `arc_authoring_needed.needs_candidates`, ranked by actual textual overlap with
   this character's own `routine_actions` — the highest-scoring tag for the routine matching your
   chosen `context`, not whichever tag was easiest to reach for.** `write_arc.py` also now hard-rejects
   any `--needs` value outside that context's own `_lore/contexts.json` `provides` list, so this isn't
   optional — but read the ranked list and actually use it, don't just satisfy the gate with the first
   valid-but-ungrounded option. If `reason` is `"reauthor_complete"`, `write_arc_completion_tale()`
   already ran inside `simulate_pass_brief.py` before this brief was even printed — the completed
   arc's `completion_tale_id` is right there in the payload; nothing further to do for it (it's
   mechanical, not a judgment call — the arc's own already-authored `premise` is what got filed).
4. **Dispatch the enacter.** How depends on Step 1's model choice — either way this is the ONE dispatch
   per pass, it does no tool-calling of its own, and it never sees anything beyond point 3's JSON plus,
   when relevant, a short director's note (below).

   **Haiku/Sonnet/Opus** (Agent tool, `subagent_type: general-purpose`, the model chosen in Step 1,
   `run_in_background: false`). Redesigned 2026-08-29 (round-2 debrief) after auditing an actual run's
   token cost: the old design had a single subagent both write the scene AND drive every mechanical
   script call itself, which meant every pass re-sent a long, rule-heavy prompt from scratch and the
   subagent regularly burned 3-6x the intended tool calls fumbling JSON schemas and retrying. Splitting
   content from mechanism fixes both at once, and keeps the enacter's own prompt short and stable
   enough to run on a genuinely small/local model too — see the Local path below, which is exactly
   that: it never needs script rules, path discipline, or worktree-leak precautions, because it never
   touches a tool.
   - **Paste point 3's JSON output directly into the dispatch prompt. Never hand-paraphrase it into
     prose first.** Caught in the round-3 debrief: an earlier session was retyping the brief as
     sentences ("Pass 20. Location: the road between City C and the harvest fields...") before every
     single dispatch — pure overhead, spent in the *orchestrator's own* tokens, restating facts the
     JSON already stated. `.claude/PRINCIPLES.md`'s "script everything that can be scripted" principle
     governs this directly: if it's already data, hand it over as data. Trim only genuinely
     irrelevant bulk (e.g. `character_files`'s absolute paths, which the enacter has no use for since
     it never touches a file) — don't rewrite what's left.
   - Prepend the fixed instruction preamble (same text every pass, never composed fresh): the standing
     writing rules (dialogue-only, no invented named people, criterion shows through behavior not
     recitation, finitude is pressure never topic, natural stop) and the required reply structure.
   - Ask for ONE structured text reply, nothing else: the scene transcript; a short list of hearsay
     claims (text + `about` tag, `category: value` shaped — never a bare word or a character's own name
     as the tag) grounded in what was actually said; each participant's `experience` (plain strings)
     and any `grounded_experience` (text + `about` tag(s)) worth keeping; and, only if the brief's own
     anchor-reference check flagged it as live this pass, a `criterion_move` verdict
     (`reject`/`reinterpret`/`break`, with the dialogue line, cause, and any new trusts/distrusts text)
     — see `.claude/skills/enact/SKILL.md` Step 6 for the authoring discipline behind that judgment;
     reserve it for a genuine test of the anchor, not just a scene that happens to reference it (a gate
     hit alone is not a move — confirmed empirically: 20 passes into round 3, most gate hits were the
     character exercising or affirming their existing trust/distrust, not having it challenged, and the
     correct call was "none" every time). Tell it explicitly it has no tools to use and should never
     attempt one — just answer in its final message.

   **Local (Ollama, `qwen2.5:14b`)** — no Agent tool at all, a plain script call in the orchestrating
   session, absolute path, Bash only. Write point 3's JSON to a file first (there's no subagent
   context to paste it into this time), then:
   ```bash
   py "<worktree>/scripts/lore/enact_via_ollama.py" --brief-file "<worktree>/.pass_<N>_brief.json" \
       [--director-note "<1-2 sentences, same rule as the Claude path above>"] \
       --out "<worktree>/.pass_<N>_reply.json"
   ```
   The script owns the fixed preamble itself (`scripts/lore/enact_preamble.md`, read fresh from disk
   every call — the same standing writing rules as the Claude path, never edited here), forces the
   model's output into strict JSON via Ollama's structured-output mode, and already runs its own
   cleanup/validation/retry loop (empty-placeholder stripping, exact `about`-tag matching against the
   brief) before ever printing a final reply — see its own docstring for the full contract. **If it
   still exits non-zero after its own retries, that's a script failure like any other**: report the
   exact error and stop this pass rather than switching model or method mid-run (same discipline as
   point 5 below, just reached one step earlier here). On success, its `reply` field is already shaped
   to drop into point 5's hearsay/decisions JSON almost as-is — see that point's Local note.

   **For a many-pass run on the Local path, `scripts/lore/simulate_driver.py` collapses this whole
   per-pass sequence (points 2-5 below, resolve pair through pass_apply) into one call** instead of
   the ~5 separate round-trips a subagent-per-pass design costs — built 2026-08-31 on a token-cost
   audit that found this cut real usage enough to run 250 passes where ~40 was the prior ceiling on
   the same budget. It stops the batch automatically at either judgment slot (`needs_arc`/
   `needs_name`) and resumes cleanly once the orchestrating session supplies the content via its own
   `resolve-arc`/`resolve-birth` subcommands — read its own docstring before using it. Optional: the
   manual per-pass sequence below still works and is the reference implementation this script wraps.

   The **director's note** rule is the same for both paths, and it's the one legitimate addition to
   either dispatch: 1-2 sentences, only when the gate hit and an outcome needs a concrete "what
   satisfies this" nudge the mechanical JSON can't supply on its own (e.g. "'mixed' means the other
   participant's angle partially fits but doesn't resolve anything — your call what"). This is real
   judgment, not restated fact, so prose is the right tool for exactly this part and no more of it.
5. **Do everything mechanical yourself, in the orchestrating session, from the enacter's reply:**
   - Write the scene file under `<worktree>/_npcs/scenes/` per `_npcs/scenes/_template.md`'s shape.
   - Build the hearsay JSON from its claims and run `pass_record.py` (absolute path, Bash only) —
     wraps `record_hearsay.py` plus anchor-reference/resonance checks for both participants.
   - Build the decisions JSON from its experience/grounded_experience/criterion_move fields and run
     `pass_apply.py` (absolute path, Bash only) — wraps every remaining mechanical write: `update_character.py`
     calls, the energy-death check, post-lived-delta `horizon.py`, reproduction, death-legacy. **Pass
     `--scene-id <this pass's scene id>`** (found 2026-08-30, local-model integration test) — without
     it, every `knowledge.experience` entry this pass writes goes untagged, and
     `measure_derivation.py`'s provenance-coverage instrument (Step 4) reads 0% for the whole run
     regardless of how the pass was actually dispatched.
   - **Local path shortcut:** `enact_via_ollama.py`'s `reply.hearsay` and `reply.participants` are
     already shaped to match `pass_record.py`/`pass_apply.py`'s own input contracts field-for-field
     (`text`/`about`/`note`/`oral_lore` for claims; `experience`/`grounded_experience`/`cost_ledger`/
     `criterion_move` per participant, `move`/`dialog`/`cause`/`note`/`trusts`/`distrusts` inside a
     move) — this isn't composed from prose the way the Claude path's reply is, it's assembled
     directly. All that's left to add: `participants` (the two characters' real `name` values, not
     slugs) and this pass's scene id to `reply.hearsay` before it becomes the hearsay JSON, and
     `lived_delta: 1` to each participant's block before it becomes the decisions JSON — `synthesis`
     and `death_cause` stay absent/null, same as the Claude path (neither is the enacter's job).
   - Since you're the one making both calls with a schema you already know is correct, there's no
     retry loop to design around — a failure here means something is genuinely wrong (a malformed
     brief, a missing file), not a JSON-shape guess to fix and resubmit.
   - **If any script call fails for any reason, report the exact error and stop that pass rather than
     switching tool/method** — same discipline as always, just now applied to your own calls instead
     of a subagent's.
   - **After `pass_record.py` reports success, verify it actually landed** — read the tail of
     `<worktree>/_lore/characters/hearsay.md` and confirm the new entry is really there.
   - If `pass_apply.py`'s output says `reproduces: true`, compose the child's name yourself (the one
     other judgment call this whole pipeline can't script) and call `generate_offspring.py` directly.
6. Append a one-line summary (both participants, gist, criterion change, birth/death) to the running
   log — this is what keeps a long run affordable in the *orchestrator's own* context, same reasoning
   as before, just no longer needing a subagent's self-report to summarize from.
7. If either participant died this pass, drop them from the living pool before the next draw. If a
   birth happened this pass, add the child to the pool once the current pass number reaches
   `birth_pass + child_cooldown_passes` (`generate_offspring.py` prints the exact threshold) — and
   treat them as an ordinary adult participant from that pass on, no special handling: the cooldown
   period itself already *is* their portrayed childhood (they exist, may be known of or talked about,
   but never appear in a scene until the pool admits them) — see TODO.md's "childhood/age" open note.

The relative-path-leak risk this section used to warn a subagent about (a bare `scripts/lore/...` call
resolving against the main checkout's own copy instead of the worktree's, silently writing real files)
still applies to the orchestrator's own calls in points 3 and 5 — the discipline (full absolute path,
every single call, never a bare relative one) carries over unchanged; only the "who has to be told
this" part of the old design goes away.

At the natural end of a batch (the run's requested pass count is reached, or the session is otherwise
wrapping up) — not after every single pass — run `py scripts/lore/build_source_index.py` once, so
every concept registered this batch gets its accumulated hearsay claims folded into its own
`sources[]`, the same absorption a separate `/integrate` pass would eventually do anyway.

## Step 4 — Summarize

Once all passes are done (or the pool ran out early):

- **Decide, once, right now: was this run testing or extending the system's design, or a casual
  one-off/showcase trail?** This single judgment call (unchanged from its original, narrower use —
  see the last bullet below) now also gates the test suite and the immersion tasting a few bullets
  down, not only the `LAB_REPORT.md` entry. Two things always happen regardless of this call — the
  tally and the Narrative report — everything else in this step is conditional on it. When in doubt,
  ask the user (AskUserQuestion) rather than guess; this decides real, skippable compute below, so
  it's worth a genuine check rather than a default.
- Run the tally script against the snapshot Step 3 wrote, rather than hand-counting deaths and
  criterion moves from the running log's one-liners — **always, regardless of the call above**, since
  the Narrative report below draws on it:
  ```bash
  py scripts/lore/simulate_tally.py report .simulate_snapshot.json
  ```
  It diffs every participant's current `_lore/characters/<key>.json` against where they stood before
  pass 1, so the deaths, criterion-move counts, and final `life.lived` come straight from the record
  rather than being reconstructed from memory of up to N pass summaries.
- **Only on a design-testing/extending run — run the test suite's closing instruments and the
  immersion tasting.** Skip this whole bullet on a casual/showcase run; nothing below it depends on
  it having run. (Reworked 2026-08-30 from "always, seeded or not" — these instruments are cheap,
  read-only scripts, but the point stands on principle: not every run needs the full apparatus, and
  running it unconditionally on every showcase trail was never actually a deliberate choice, just an
  unexamined default.)
  ```bash
  py "<worktree>/scripts/test/conformance_report.py" --root "<worktree>"
  py "<worktree>/scripts/test/measure_derivation.py" --root "<worktree>"
  ```
  Both print a human-readable section — include them verbatim in `SIMULATION_LOG.md` below, under
  their own "Test suite" heading. Immediately after, **ask the four immersion-tasting questions
  inline** — this is `/taste`'s own Step 2/3 (read `.claude/skills/taste/SKILL.md` if it hasn't been
  read yet this session), folded into this step rather than left for a separate later invocation:
  read the run's own pass-by-pass log and the Narrative report you're about to write (draft that
  section first if it makes the tasting more informed — order between the two is your call), then ask
  a rater name (default: the current git `user.name`) and walk **legibility** / **aliveness** (incl.
  felt contingency) / **curiosity** / **specificity**, 0–10 each, plus an optional per-dimension note,
  exactly as `/taste` Step 3 documents. Record it the same way that skill does:
  ```bash
  py "<worktree>/scripts/test/record_tasting.py" --manifest "<worktree>/.simulate_run_manifest.json" --rater "<name>" \
      --legibility <N> --aliveness <N> --curiosity <N> --specificity <N> --note "<note>" [--note "..."]
  ```
  Include the recorded scores (and any notes) in `SIMULATION_LOG.md` too, under a "Tasting" heading
  next to the Test suite section. `/taste` still exists as a standalone command for scoring a run
  later, or for a second rater's independent tasting on this same run — this inline ask is the first
  tasting, not a replacement for the command.
- **Also only on a design-testing/extending run — log the orchestrator's own token usage for this
  run** (added 2026-08-30, so a run's real cost is comparable across dispatch models rather than only
  guessed at). This reads Claude Code's own session transcript; it changes nothing and needs no
  network access:
  1. Find this session's own transcript: the session id is the folder-name segment of this session's
     scratchpad path (given in the system prompt, right before `/scratchpad`) — Glob for
     `~/.claude/projects/**/<session-id>.jsonl`; there is exactly one match, this session's own file.
  2. Note the current UTC timestamp now, the same way Step 3 noted its own start timestamp.
  3. Run the script with both timestamps:
     ```bash
     py "<worktree>/scripts/test/simulate_token_usage.py" --transcript "<path from step 1>" \
         --since "<Step 3's start timestamp>" --until "<the timestamp just noted>" \
         --label "<pass count> passes + Step 4, <Model from Step 1>"
     ```
  Include its output verbatim in `SIMULATION_LOG.md`, under a "Token usage" heading next to Test
  suite/Tasting. Read `scripts/test/simulate_token_usage.py`'s own docstring before quoting its
  numbers at face value — `cache_read` dominates the raw total and is not the same cost per token as
  `output`/`cache_creation`; say so rather than reporting one bare "total tokens" figure.
- Write `SIMULATION_LOG.md` at the worktree root: the Step 1 setup (participants, pass count,
  context, model), the pass-by-pass one-liners in order, and the tally script's output — always.
  **Only if the design-testing bullet above ran**, also include the test suite's two reports (under
  "Test suite"), the tasting scores/notes (under "Tasting"), and the token-usage output (under "Token
  usage") as further sections. The Narrative report (below) closes the file either way.
- Finalize the run manifest:
  ```bash
  py "<worktree>/scripts/lore/run_manifest.py" finalize --passes-run <actual N> --simulation-log SIMULATION_LOG.md
  ```
- **Append a "Narrative report" section** (standing requirement, added 2026-08-10 on request) —
  prose, not another mechanical recap: for each participant's arc, how it actually developed across
  the run (the shape of it - steady, volatile, stalled, resolved), what changed in their
  relationships to each other, any criterion moves and what prompted them, and an honest account of
  what didn't happen (deaths, reproductions, resolutions) alongside what did. This is the section a
  person would actually want to read to know what this slice of the world's history was about: write
  it that way, grounded in the specific pass-by-pass facts already on record above it, not invented
  beyond them. **Required every time this step runs, unconditionally** — this is the one section that
  never depends on the design-testing call above; a casual/showcase run still gets a real narrative
  report, it just skips the test suite and tasting around it.
- Tell the user: how many passes ran, headline events, the worktree's path and branch name, and that
  it stays on disk untouched by anything here — nothing in the original working directory changed.
  They can `/enact` a character from inside this worktree, read any file directly, ask questions
  about what changed, or run `/simulate` again (after exiting this worktree, or from a different
  session) for an independent second trial off the same starting state, to compare against this one.
- **If this run was testing or extending the system's design** (the same call from the top of this
  step — don't re-ask it), append a dated entry to `LAB_REPORT.md` so no run's result is ever only in
  chat history. **`LAB_REPORT.md` is deliberately absent from `provenance-bare`** (this branch ships
  the bare engine with no run history). A persistent, branch-independent copy is optional and lives
  outside this repo entirely (e.g. a personal notes vault) — resolving where that is works the same
  way any other project-specific external path does: check `CLAUDE.md`/project settings for a
  configured location first; if none is set, ask the user for the absolute path once and treat it as
  standing for the rest of the session; if the user says there isn't one, skip the external copy and
  only append to the main repo's own `LAB_REPORT.md` (next bullet) if that exists. Once resolved, read
  that file's own header for the expected entry shape before appending. **If the main repo root this
  session is actually checked out on also has its own `LAB_REPORT.md`**, **append the identical entry
  there too**, so the two stay in sync rather than drifting apart by writing to only one. **Do this
  only from the orchestrating session, using each file's absolute path** (the same pattern as the
  Step 3 safety net's `git -C "<main repo root>"`), **never by writing it from inside the active
  worktree.** This is
  a deliberate, single, explicit write to a known meta-file at the very end of a run — unlike the
  accidental relative-path leaks Step 3's safety net exists to catch and revert, this one is
  intentional, so it's fine for it to land outside the worktree. If the run surfaced a design gap or
  an open question rather than a settled answer, log it under that file's "Open design questions"
  section rather than only leaving it in chat history.
- Don't call `ExitWorktree` — only on explicit request, same as Step 0.

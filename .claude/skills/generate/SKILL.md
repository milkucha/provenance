---
description: Mechanically pregenerate a large, multi-generation starting population (offspring, inherited knowledge, arcs) in one script-driven run — fast-forwarding many passes with NO scene-writing at all. Use when the goal is a big starting cast, not a showcase trail of prose — that's /simulate, a different mechanism entirely. In an isolated git worktree, same as /simulate.
disable-model-invocation: true
---

`/generate` reuses `/simulate`'s worktree isolation and preconditions, but replaces its
interactive showcase-trail loop with a mechanical one: the entire pass loop runs as ONE Python
process with no subagent dispatched per pass, and the only subagent this skill ever spawns is a
single batched "language layer" pass at the very end (Step 4 below) — never one dispatch per birth
or per arc. See `scripts/lore/simulate_generate_population.py`'s own docstring for the full
mechanical rationale and the three deliberate scope differences from an interactive
`/simulate` extended-mode run (no scene prose or criterion shocks; the child-naming/arc-authoring
judgment calls are deferred and batched rather than invented per-event; a contested visit never
invents a named rival, since that requires content no script or dice roll can supply).

Lore-only, same as `/simulate`, `/enact`, and `/character` — never touches `data/` or `_npcs/`.
Read `.claude/skills/simulate/SKILL.md` before running this if it hasn't been read yet this
session; this skill points back at its Step 0 and Step 2 rather than restating them.

## Step 0 — Preconditions

Identical to `.claude/skills/simulate/SKILL.md`'s own Step 0 — same worktree/uncommitted-changes
checks, unchanged.

## Step 1 — Setup questions

Same as `/simulate` Step 1's participant checks (must exist, must be living), plus one requirement
unique to this skill: every participant in `--pool` must already have a non-empty `routines` array
(checked by `simulate_generate_population.py` itself, but confirm before running it - a
routine-less character can never be paired into the reproduction mechanic, so including one just
wastes a run). Ask only: participants, and how many passes to run. No context/model questions -
there is no scene, so nothing for either to shape.

## Step 2 — Create the worktree

Identical to `.claude/skills/simulate/SKILL.md`'s own Step 2, unchanged. Still worth doing even
though this skill dispatches only one subagent total (not per pass) - that Step's bypassPermissions
setup is what lets that one dispatch, plus every `py scripts/lore/...` call in Steps 3/5 below, run
without prompting.

## Step 3 — Run the mechanical loop

One call, absolute path, same non-negotiable rule as every other script invocation this skill's
sibling skills use:
```bash
py "<worktree>/scripts/lore/simulate_generate_population.py" --pool <slug1> <slug2> ... --passes <N>
```
Report its printed summary (passes run, living pool, births, arcs queued, max generation depth). It
writes `.simulate_snapshot.json` (for Step 6) and `_pending_language.json` (for Step 4) at the
worktree root, and `GENERATION_LOG.md` with a one-line-per-pass log.

## Step 4 — Language layer (the one subagent)

Dispatch exactly one subagent (Agent tool, `subagent_type: general-purpose`, the model chosen for
this run if the user specified one, else Sonnet, `run_in_background: false`). Brief it
self-contained, same absolute-path/Bash-only/no-`cd` discipline as every other subagent
`/simulate` dispatches (see its Step 3's rules, restated in full to it):
- Read `<worktree>/_pending_language.json` (absolute path).
- For each entry in `children`: compose a name that reads as a plausible blend of `parent_a`'s and
  `parent_b`'s names, leading from `name_lead`'s side (per `generate_offspring.py`'s own docstring -
  this is the one thing in the whole mechanism that can't be scripted). Also rewrite each of that
  child's `routines[]` entries' `routine_actions` line so it reads as the CHILD's own progression of
  actions, not a verbatim restatement of whichever parent it was inherited from - keeping the same
  `location`/`context`, only rewording `routine_actions` (a short action sequence, not a trait/
  description, same discipline as `character/SKILL.md` Step 8's own examples, e.g. "minds the stall
  while his mother haggles, learning the regulars' faces one by one").
- For each entry in `arcs`: author `about` (topic tags, at least one `"concept: <id>"` tag for a
  genuinely new project - see `register_arc_concept.py`), `needs` (what it currently requires, in
  the same vocabulary `check_needs_provides.py` matches against a context's `provides` tags),
  `context` (must be a key already in `_lore/contexts.json`, ordinarily matching one of that
  character's own `routines[].context`), and `premise` (the arc's actual concrete content -
  `character/SKILL.md` Step 8's full authoring discipline applies here too: the resolution-moment
  test, grounding the target in the character's own known corpus when possible, and the
  texture-vs-claim-shaped-content attribution rule). Scope the ambition against the entry's own
  `horizon_band` exactly as `character/SKILL.md` Step 8 prescribes: `early` can be ambitious;
  `established`/`late` should read as realistically closer to finishable. For `reason:
  "reauthor_failed"` or `"reauthor_complete"`, read `prior_arc` for continuity/contrast rather than
  starting from nothing.
- Write `<worktree>/_pending_language_resolved.json` (absolute path) in exactly this shape:
  ```json
  {"children": [{"placeholder_slug": "...", "name": "...",
                 "routines": [{"location": "...", "routine_actions": "..."}]}],
   "arcs":     [{"character_slug": "...", "about": ["..."], "needs": ["..."], "context": "...",
                 "premise": "..."}]}
  ```
- No scene-writing, no `AskUserQuestion`, no touching any other file. Report back only a short
  summary: how many children named, how many arcs authored.

## Step 5 — Apply

One call, absolute path:
```bash
py "<worktree>/scripts/lore/apply_language_layer.py"
```
It renames every resolved child (text-substituting the placeholder name across the child's own
file, its birth tale, `encodings.json`'s matching tale entry, `_lore/tales/_index.md`'s row, and any
other character file's `knowledge.experience` mentioning it - never the slug/filename, see the
script's own docstring for why), writes each resolved arc and registers its concept, runs
`build_source_index.py` once, and archives both pending JSON files under `_generation_archive/`.
Report its printed summary, including any `NOTE:` lines about children or arcs the subagent left
unresolved (they simply stay placeholder-named/arc-less - not an error, just something to revisit).

## Step 6 — Summarize

Reuse `simulate_tally.py report` against Step 3's snapshot, same as `/simulate`'s own Step 4:
```bash
py "<worktree>/scripts/lore/simulate_tally.py" report "<worktree>/.simulate_snapshot.json"
```
Tell the user: passes run, population before/after (living pool size, births, deaths), max
generation depth reached, and the worktree's path/branch - same "stays on disk, nothing merged
automatically" framing as every other `/simulate`-family run. This worktree's population is now
ready to serve as the starting cast for an ordinary `/simulate` run - either from inside this
worktree in a later session, or by hand-copying `_lore/characters/` over
once satisfied with it. Don't call `ExitWorktree` - only on explicit request, same as Step 0. If
this run was testing or extending the mechanism itself, append a dated entry to `LAB_REPORT.md` at
the main repo root, same discipline as `/simulate` Step 4's closing bullet.

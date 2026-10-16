---
description: Re-run the audit of one /simulate pass (what each step reads, rolls and writes, whether step N's output is really read by step N+1, and how the code measures up against README Part I), diff the findings against the saved baseline, and republish the Pass Map artifact. Use to measure progress after engine changes, or before a design session on how character state should skew the dice. Never changes engine code; it only reads, runs the mechanical scripts on a scratch copy, and writes findings.
disable-model-invocation: true
---

An audit, not a fix. It looks at the engine as it stands, says what it found and how sure it is, and leaves the changing to a separate session. Same rule as the rest of this project: nothing decided silently, gaps go to [OPEN_QUESTIONS.md](../../../OPEN_QUESTIONS.md), bugs to [TODO.md](../../../TODO.md). The baseline is `diagrams/simulate-audit/findings-2026-10-16.json` (and `artifact.html` next to it); every later run is judged against it.

## Step 1 - Scope

One pass, in order: draw p1, work-or-arc, routine, local check, pathfind/travel, meet, p2 routine, payment, contest/align/outcome/tally, scene and record, apply (aging, deaths, birth, legacy), solo bookkeeping. For each step write down: the script, the state it reads, the dice with their odds (from `_lore/tuning.json`, never from memory), the state it writes, and what lands in the lore (hearsay, tale, character file). Then check the seams: is what step N writes actually read by step N+1? Look for dead fields (written, never read), dangling reads (read, never written), and docs that say something the code does not (SKILL.md, README, docstrings, `diagrams/`). Start from `scripts/lore/simulate_pass_lib.py:run_pass_mechanics`; it is the spine.

## Step 2 - Intent against README Part I

Evaluate the code against Part I as it stands now, not against SKILL.md. Mark each item met / partly / not met / unknown with file:function evidence:
- **Objectives:** structural organic (produces its own components, mutates, exchanges with the environment) and perceived organic/immersive (responsive, unpredictable, legibly caused); model-agnostic; token-lean.
- **Design principles:** negative space and provenance; all knowledge self-contained (look for anything entering from outside the record); imperfection kept (look for contradiction being smoothed away).
- **Testability:** do the instruments' inputs exist in a real run (manifest, draw audit, hearsay lineage, `produced_by`)? Which Objectives have no instrument at all?

## Step 3 - Run it (RAN)

Mechanical scripts only, a seeded RNG, no model, no Ollama. Make a corpus worktree outside the repo, run the script, remove the worktree:

```bash
git worktree add <scratchpad>/corpus corpus-three-cities
py scripts/test/audit_simulate.py --root <scratchpad>/corpus --passes 40  --seed 7 --fixture none
py scripts/test/audit_simulate.py --root <scratchpad>/corpus --passes 200 --seed 5 --fixture travel \
    --baseline diagrams/simulate-audit/findings-2026-10-16.json --json-out <scratchpad>/run.json
git worktree remove --force <scratchpad>/corpus
```

`audit_simulate.py` copies `_lore/` and `scripts/` to a temp dir, so the real files are never written. `--fixture travel` renames location ids to the display names, chains the places with routes, makes one need available only at the far end and seeds some provisions; it picks its own need tag, so it runs on any corpus. It prints branch counts (`local_noop`, `paid`, `dead_among_candidates`, ...) and one probe per finding (True = still present, null = only readable). A motivated pass gets a stub scene, so nothing about the scene text is tested here. Anything you cannot run (the model, reproduction in a real birth, multi-need arcs) stays READ and says so.

## Step 4 - Findings format

One entry each, same shape as the baseline JSON: `id` (keep the old id if it is the same finding, next free `F<n>` otherwise), `title`, `severity` (high/medium/low), `kind` (bug / doc / dead-field / gap), `verification` (RAN / READ / DOC-ONLY), `status` (open / fixed), `evidence` (with the observed counts), `where` (file:function), `steps` (indexes into the flow), `probe`. A design disagreement is not a bug: it goes to OPEN_QUESTIONS.md in a short entry in the author's voice, hedged, and ends with a question.

## Step 5 - Diff against the baseline

`audit_simulate.py --baseline` reports **fixed** (open before, probe false now), **new** (probe true, not in the baseline), **regressed** (fixed before, true now), **still_present**, and **not_scriptable** (READ-only findings; re-read those by hand and say which changed). Run both fixtures: F13 can only be judged on `--fixture none`. Write the new snapshot as `diagrams/simulate-audit/findings-<today>.json` with `status` updated, keep the old file, and say in one line what moved.

## Step 6 - Rebuild and republish the artifact

The page is `diagrams/simulate-audit/artifact.html` (self-contained, tokens at the top, data in `STEPS`, `FN`/`FE` (flowchart nodes and edges with the observed counts per run), `ROWS`, `CONS`, `FINDS`, `INTENT`; the flowchart is laid out by dagre 0.8.5 from cdnjs, then the main route is straightened in `drawChart`). Edit the data, not the layout: update the counts from the run (the `FE` rows hold run A and run B counts, `FUN` the strip above the chart), flip finding statuses, move the cited lines. Save it back to the same path, then republish to the **same artifact URL** (Artifact tool, `url` set, `file_path` the saved html) so the link stays stable. Keep generic characters only; no lore names.

## Rules

- No engine edits, no pushing, no named lore in this branch.
- Say honestly what was RAN and what was READ. A finding without a verification mark does not go in.
- Commit the new snapshot, the html and any TODO/OPEN_QUESTIONS entries in one commit, in the author's voice ([.claude/VOICE.md](../../VOICE.md)).

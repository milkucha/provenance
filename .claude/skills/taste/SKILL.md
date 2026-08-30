---
description: Score one immersion "tasting" against a /simulate or /generate run - the subjective instrument of the Provenance test suite (see TESTING_BRIEF.md, vault-side projects/provenance/). Asks 0-10 for legibility, aliveness (incl. felt contingency), curiosity, and specificity, then records the scores against that run's manifest via scripts/test/record_tasting.py. Multiple tastings (different raters, or the same rater on different runs) accumulate rather than overwrite. Use after reading a run's harvest (SIMULATION_LOG.md / GENERATION_LOG.md), when the user wants to score how the run actually read, not just whether it ran correctly.
disable-model-invocation: true
---

Read `TESTING_BRIEF.md` (vault-side `projects/provenance/`) first if it hasn't been read yet this
session — §2(c) and §4.3 are this skill's own design contract, not restated here. This skill owns
only the mechanical recording; `scripts/test/conformance_report.py`/`measure_derivation.py` (the
objective instruments) are separate and already run automatically at the end of `/simulate`/
`/generate` — this skill is the subjective one, always user-invoked.

## Step 1 — Locate the run

Ask which run, unless it's obvious from context (the conversation just finished a `/simulate` or
`/generate` run in this session). A run is identified by its `.simulate_run_manifest.json`, at that
run's worktree root — if the user names a worktree instead of a path, resolve it to
`.claude/worktrees/<name>/.simulate_run_manifest.json`. If no manifest exists at that path, say so
plainly and stop — a run started before this test suite existed has nothing to score against yet.

## Step 2 — Read the harvest

Before asking for scores, actually read what the run produced — `SIMULATION_LOG.md` or
`GENERATION_LOG.md` at the run's worktree root (whichever exists), including its narrative section.
Scoring from the pass-by-pass mechanical log alone, without reading the narrative, isn't a real
tasting.

## Step 3 — Ask for the four scores

Ask as **plain conversation, not `AskUserQuestion`** — a 0–10 integer isn't a clean small discrete
set, and `.claude/PRINCIPLES.md`'s own convention reserves `AskUserQuestion` for genuinely discrete
choices. Ask for a rater name first (default: the current git `user.name`), then walk the four
dimensions one at a time, per `TESTING_BRIEF.md` §2(c):

1. **Legibility** — is the seed's fingerprint visible in the growth? If the output could have come
   from any seed, the wire is broken.
2. **Aliveness** — transformation beyond what the seed could script, including *felt contingency*:
   does the world read as if it could have gone otherwise.
3. **Curiosity** — does the harvest make you want to keep reading it.
4. **Specificity** — the anti-equalization check: evident bias, imperfection, unevenness (towns that
   grew and towns that didn't) vs. everything mixing into brown.

Take a 0–10 score for each, plus an optional short note on why (per-dimension notes are more useful
than one general comment — encourage one line each, but don't force it if the user just wants to give
numbers).

## Step 4 — Record it

```bash
py scripts/test/record_tasting.py --manifest <path to .simulate_run_manifest.json> --rater <name> \
    --legibility <N> --aliveness <N> --curiosity <N> --specificity <N> \
    --note "<per-dimension note>" [--note "<another note>" ...]
```

This appends to the manifest's `tastings: []` array — it never overwrites an earlier tasting, on this
run or any other rater's. Report back the recorded scores and the running tasting count for this run.

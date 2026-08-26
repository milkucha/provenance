# /simulate Lab Report

**Purpose.** `/simulate` batch-runs `/enact` scenes to test whether this system's design actually
produces what it's meant to: emergent, materially-grounded lore-drift, not just mechanically-correct
but dramatically repetitive record-keeping. This file is the persistent, core-repo record of that
test across runs — deliberately *not* inside any worktree, so it survives past any single run, any
single conversation's context window, and any single agent. A fresh session or a different agent
should be able to read this file alone and pick up the thread: the standing hypothesis, what's been
tried, what worked, what didn't, and what's still genuinely undecided — without re-deriving any of it
from chat history.

**How to use this file.**
- Before starting a `/simulate` run intended to test or extend the system's design (not a casual
  one-off), read this whole file first.
- After a run's Step 4 tally completes, append a new dated entry under **Run log** — from the
  orchestrating session, using this file's absolute main-repo path. Never write it from inside the
  active worktree itself; see the note in `.claude/skills/simulate/SKILL.md` Step 4 for why.
- Keep entries factual and specific: cite the worktree name, pass counts, concrete outcomes (deaths,
  arc resolutions, emergent structures), not just impressions.
- When a run surfaces a design gap or an open question, log it under **Open design questions** so it
  doesn't live only in chat history and get lost at the next compaction.
- Update **Open design questions** in place as questions get resolved — move a resolved question's
  answer into the relevant run-log entry or into the design itself (`TODO.md`), and remove it from the
  open list rather than leaving stale unresolved-looking questions that were actually settled later.

## Standing objective

Does `/simulate`'s design render its own stated intent — characters whose criteria, knowledge, and
relationships drift over many interactions in a way that's genuinely emergent (organically branched out
of initial conditions) rather than a repeated pattern regurgitated by the model, or a smooth convergence
produced by the model's own bias toward agreement? The mechanism should produce real material
consequence (things that can fail, end, or run out) alongside the language-level consequence (hearsay,
criterion drift) it already reliably produces.

A second, standing methodological concern runs alongside the first: anywhere the system needs a
"random" or "which one matters" decision, that decision must come from a genuine mechanical draw
(`pick_pair.py`'s `random.sample()`, `roll_routine.py`'s `random.choices()`, etc.), never from a model
guessing at what feels salient — the same reasoning that motivated building `pick_pair.py` in the first
place applies to every subsequent mechanic layered on top.

## Methodology

After each run that's testing the design (as opposed to a routine content-generation run):
1. Compare what actually happened against the standing objective above — not against whether the
   *mechanism* ran correctly (that's `simulate_tally.py`'s job and is usually fine), but against
   whether the *content* it produced reflects real emergence and material stakes.
2. Distinguish a mechanism working as designed but producing the wrong content, from a mechanism that
   itself didn't work — these need different fixes.
3. Log concrete evidence for both — what if anything broke narrative-content symmetry (deaths, failed
   arcs, contradictory secondhand accounts, structural collapse), and what stayed suspiciously
   convergent or safe.
4. Carry forward anything left genuinely undecided into **Open design questions** rather than silently
   assuming an answer the next time the system gets extended.

## Run log

(No runs logged yet.)

## Open design questions (carried forward)

(None yet.)

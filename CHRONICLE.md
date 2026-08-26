# Chronicle

**Purpose.** This is the project's own memory of itself — the landmarks in the conversation that's
been building Luminacion, session to session, kept somewhere durable instead of only living in chat
history that eventually ages out, gets compacted, or simply isn't retrievable across machines. Not a
transcript, not a diff log (`git log` already does that) — the *why* behind the *what*: decisions
made and the reasoning behind them, arguments that shifted the design, things learned the hard way,
and open questions that were live at a given point, even ones later settled elsewhere.

**How to use this file.**
- Not every session needs an entry. Add one when something landmark happened: a design decision, a
  changed mind, a real disagreement and how it resolved, a surprising result, a new open question. A
  session that was pure execution of an already-settled plan doesn't need one.
- Keep entries short — a few lines to a short paragraph, not a full recap. This is a spine of
  landmarks, not thorough documentation; that's what the rest of the repo is for.
- An open question logged here that's actionable also belongs in `TODO.md` or, if it's a
  `/simulate`-design question, `LAB_REPORT.md`'s **Open design questions** — this file just notes
  *when and why* it came up, those files track it to resolution. Don't duplicate the tracking, just
  point to it.
- Newest entry at the top.

---

### 2026-08-27 — Grounding, and why it alone won't fix epistemology dominance

Long dialogic session about the standing "everything reads as verification/epistemology" complaint.
Pushed past the corpus/backstory explanation to a mechanism point: arcs and shocks both still route
through `criterion`, so new content alone can't change the throughline unless it also feeds criterion
derivation itself — genuinely undecided, not resolved this session.

Built grounding anyway (`_lore/grounding/`) as a worthwhile axis on its own: objective, access-gated-
by-routine content, distinct from facts (universal) and material (a claim that may not be true — the
Troy distinction). `mechanics.json` got an exhaustive vanilla-1.20.1 pass (63 entries, wiki-verified);
`world_state.json` waits on an external region-file/vision pipeline the user is building in parallel.
Committed.

Also scoped, not yet built: reflection (three forced triggers — shock, death-notification, a
passes-since-last-one cooldown — plus its own arc-outcome roll, not just solo narration) and a
missing object/possession layer (characters exchange things in scenes with zero persistent trace,
which is what the "dice feels meaningless" complaint actually turned out to be about).

---

### 2026-08-27 — Author's voice, and this file

Started from a question about whether I retain any sense of how the user actually talks, for
writing README/docs prose in their register rather than default assistant prose. Answer at the
time: no — nothing existed to capture that. Built `.claude/VOICE.md` for it: a project-wide, dated,
accumulating list of the user's actual verbal patterns (not a generic "casual tone" description),
wired into `.claude/PRINCIPLES.md` and a new root `CLAUDE.md` so it applies to every agent/session
in this repo, not just one conversation's personal memory.

That led to the same question one level up: is the *conversation itself* — the argument-by-argument
journey of the project, not just the docs voice — retrievable across sessions? Checked: session
transcripts exist locally (`~/.claude/projects/.../*.jsonl`) but aren't a real answer — local-only,
not git-tracked, not something to rely on as the project's record. This file is the fix, modeled on
`LAB_REPORT.md`'s existing pattern (a durable, append-only run log that survives any single
conversation's context) but for the project's decisions/arguments generally rather than `/simulate`
runs specifically.

That open question — how to make appending to this file actually happen reliably, given plain
written instructions can't force it — got resolved same-session: a `Stop` hook
(`.claude/hooks/chronicle-nudge.sh`) now nudges once per session, only when the transcript looks
substantive and `CHRONICLE.md` doesn't already have uncommitted changes, blocking-with-reason so I
get the chance to actually check and append rather than just showing the user a message. Known gap:
the "already touched" check is `git diff`-based, which can't see edits to `CHRONICLE.md` until after
its first commit (it's currently untracked).

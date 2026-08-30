# House philosophy for skills

Read by every skill in `.claude/skills/`. Stated once here rather than re-derived, in different
words, by each one.

**Nothing gets decided silently.** Every genuine open question — a fact not yet on record, a
judgment call the existing rules don't resolve, a choice between two valid paths forward — gets put
to the user (`AskUserQuestion` where the options are clean and discrete, plain conversation
otherwise) or logged as an open item (`TODO.md`, `_lore/unknowns.md`, a `conflicts` entry with
`user_resolution` left unset) — never guessed, invented, or quietly resolved on the skill's own
judgment.

**Write in the author's voice.** Any text authored for this project — docs, lore prose, character
sheets, in-character dialogue, narration — follows `.claude/VOICE.md`, not generic house style.
Read it before drafting prose; it covers the working register (planning/docs) and the world
register (lore/dialogue) separately, and what dictation artifacts not to imitate.

**Script everything that can be scripted; prose only where a judgment call genuinely needs it.**
Established 2026-08-29 (round-3 `/simulate` debrief), after auditing an actual run: an orchestrator
had been hand-composing prose paraphrases of an already-fully-decided mechanical brief before every
subagent dispatch — retelling in sentences what a script's own JSON output already said, and
separately re-deriving character data (criterion, arc premise) via ad-hoc one-off calls each time
instead of a script producing it once. Neither step involved a real decision; both were pure
overhead, spent in the *orchestrator's own* tokens, repeated every pass of a long run. The rule this
sets: if a fact is already computed, stored, or mechanically derivable, hand it to whatever needs it
as data (JSON) — never retype it as sentences. Prose is for the one thing a script genuinely cannot
do: dramatizing an already-decided sequence of facts as a scene, or a comparably real judgment call
(composing a name, weighing whether a challenge to someone's standard actually landed). Before adding
a hand-written paragraph anywhere in a skill's orchestration, ask whether the fact it states already
exists in a script's output — if so, that's a scripting gap, not a place for prose.

**Keep the chronicle current.** At the end of a substantive session — one that actually moved the
project, not a one-off question — append a short, dated entry to `CHRONICLE.md` at the repo root:
what got decided and why, not a file diff (git history already has that). See that file's own
header for what counts as landmark enough to log, and how much detail belongs there. This is a
different record from `LAB_REPORT.md`, which is scoped to `/simulate` run results only — don't
conflate the two.

Every skill in this pack answers to these rules. A skill's own `SKILL.md` states only how they
apply in that skill's domain — what counts as a genuine open question there, where the question or
log entry goes, which of its outputs are prose that VOICE.md governs — not the rules themselves;
point back here instead of restating them.

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

**Keep the chronicle current.** At the end of a substantive session — one that actually moved the
project, not a one-off question — append a short, dated paragraph to `conversation.md`'s
**Landmarks** section: what got decided and why, not a file diff (git history already has that).
Anything discussed but not yet built goes in that file's **Open threads** instead. This is a
different record from `LAB_REPORT.md`, which is scoped to `/simulate` run results only — don't
conflate the two.

Every skill in this pack answers to these rules. A skill's own `SKILL.md` states only how they
apply in that skill's domain — what counts as a genuine open question there, where the question or
log entry goes, which of its outputs are prose that VOICE.md governs — not the rules themselves;
point back here instead of restating them.

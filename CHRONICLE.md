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

### 2026-08-28 — Architecture reframed to 3 tiers; found this checkout mid-merge with lore staged for deletion

Talked through the README §0 diagram out loud: the old "Foundation/Supporting/Datapack/Resource pack"
4-layer split conflated inert content with the process that acts on it, and split shipping across two
layers that are really one export. Reframed as three tiers — **Content** (`_lore/`), **Handlers**
(skills + scripts + the templates/registries they share), **Shipping** (datapack + resource pack) —
and rewrote §0's prose/diagram plus `graphifyish.py`'s concept-graph layer defs to match. Also started
a `Luminacion` → `Provenance` branding sweep (the project's old name), scoped to human-facing text —
`pack.mcmeta` descriptions, script/skill docstrings, in-game chat prefixes, release zip names — while
deliberately leaving the lowercase `luminacion` Minecraft namespace (`data/luminacion/`, `luminacion:`
function calls, `resourcepacks/luminacion/` junction) untouched, since that's load-bearing for the live
world and this repo's own folder name.

Mid-sweep, discovered the checkout wasn't the clean `provenance-bare` state the session opened on: it's
actually on `provenance-standalone-merge-bare`, mid an unresolved merge of `provenance-bare` into it,
with 5 real conflicts (`PRINCIPLES.md`, `VOICE.md`, `TODO.md`, both `graphifyish` outputs) and — far
more alarming — 172 `_lore/characters/*.json` files staged as deletions. Unclear whether that's
intentional (building a lore-stripped template branch) or a merge gone wrong; also explains why several
edits this session weren't persisting to disk. Paused all further changes and asked the user to
confirm — **open question, unresolved as of this entry.**

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

---

**Backfilled below: `provenance-bare`'s `conversation.md` Landmarks, folded in here during the
2026-08-28 `provenance-bare` → `provenance-standalone` merge** (see the 2026-08-28 entry above) —
`conversation.md` covered the same "project's own memory of itself" role as this file, independently,
on that branch; rather than keep two competing chronicles going forward, its history moves here and
the file itself is retired. Reordered newest-first to match this file's convention; original entries
otherwise unedited.

### 2026-08-26 to 27 — Provenance, `/start`, and folding extended mode into `/enact`

The project renamed itself from Luminacion to Provenance in the README, leading with the engine rather
than Minecraft. `/start` shipped as a live welcome banner for a fresh checkout. `/simulate`'s extended
mode — until now an optional branch — became the only mode: `/enact` against another character now
always requires routines+arc and always runs the mechanical layer first, with no more freeform
fallback for an incomplete pair. This is also when voice dictation + TTS got wired up for this
project, and when `.claude/VOICE.md` (this branch's own, now superseded above) got built — a direct
response to noticing the README and docs didn't sound like the person building them.

### 2026-08-16 to 17 — Provenance rework, genealogy bugs

Criterion's trust/distrust derivation moved from a hardcoded per-category flag to resolving
mechanically off an anchor's actual source provenance. A 2000-pass `-generate` run then surfaced real
bugs in the reproduction mechanism itself (criterion copied verbatim instead of re-derived, arcs
converging onto ~25 signatures, an unbounded placeholder-slug growth that crashed a deep lineage) —
each one fixed and logged rather than the run just quietly discarded.

### 2026-08-10 to 13 — Extended mode, Runs 2 and 3

The redesign added routines tied to a real place-type archetype, arcs with progressive state
(primacy, gate, outcome, transform), reproduction, and death legacy — the governing rule for the whole
build: minimize the subagent's judgment, so almost every per-pass decision became a script, a dice
roll, or arithmetic, leaving only scene-prose and a newborn's name-blend as genuine model calls. Run 2
piloted it on 6 characters, then got extended in place seven more times up to 305 passes on direct
request rather than as separate runs — and it delivered exactly the material stakes Run 1 was missing:
arcs that stalled, reversed, transformed, and resolved on real dice rather than smooth convergence;
four generations of births; deaths that triggered genuine criterion shocks; one arc that stayed open
for 148 passes before resolving. It also surfaced a real string of bugs worth remembering because of
what they say about the system's own blind spots: an accent mismatch ("Ilaría" vs. "Ilaria") silently
broke an entire character's death-notification circle for 115 passes before anyone noticed; hearsay
was never actually folding back into the concepts it referenced, because `/simulate`'s own recurring
arc topics had never been registered as real `encodings.json` entries — the corpus looked like it was
accreting when 325 of 331 references were silently going nowhere; a scene-transcript filename
collision quietly overwrote earlier dialogue four separate times before a collision guard existed.
Each was root-caused and fixed. Run 3 then validated `/generate` (300 mechanical passes, zero scenes)
as a genuinely faster path to a starting population, at the cost of not testing drift itself — why
`/generate` and `/simulate` stayed two separate commands.

### 2026-08-05 to 09 — `/simulate`, Run 1, and the unattended-run problem

`/simulate` was born to batch `/enact` across a population, run inside a disposable worktree so a
stress-test run couldn't touch real files. Run 1 (97 passes on 5 characters) delivered real, unchosen
material consequence — 4 natural deaths, a keeper network that structurally collapsed as the
population shrank — but also the diagnosis that mattered most: nearly every scene still orbited the
same one conflict (multiplicity vs. singular truth), because routines at that point were bare
`{location: weight}` pairs with no authored practice behind them, and arcs were auto-derived from a
character's existing criterion anchor instead of from what they actually did somewhere. Content
converging like that was structural, not a prompting problem — it's what led straight into the
extended-mode redesign above. Separately, what actually ate the most *time* in this stretch wasn't the
simulation design at all — it was getting a run to survive unattended, overnight, with no permission
prompts: worktree settings written before `EnterWorktree` instead of after, a relative-path leak that
silently wrote real scene content into the main checkout, `cd`-in-Bash hard-blocked with no override.
Each got documented as its own fix rather than papered over, since the failure mode kept recurring in
slightly different shape until it was actually root-caused.

### 2026-07-30 to 31 — Tale, fact, and criterion

`/tell` and `/discover` (later merged into `/tell`) split off a third and fourth source of truth
alongside material and hearsay. The criterion mechanism got designed in real time across one long
session — negative derivation, anchors, the will to live, shocks vs. drift — settling most of the
shape it still has today. Also the first fully bilingual enactments (Khan Icé, la Feria del Milenio,
Gok, Bardaglis, Auroboro III) — the in-character register `.claude/VOICE.md`'s original "world voice"
section was built from.

### 2026-07-24 to 25 — Cold start

First commits: hearsay, the gesture rig, `/character` as a lighter sibling of a full enacted scene.
The gesture work in particular ran through a lot of in-game trial and error (an elbow joint that
wouldn't compose with its parent bone, a shared timer that broke once more than one NPC could gesture
at once) before landing on what's in `GESTURES.md` now.

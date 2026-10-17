# Hand-off

For a cold agent picking this up. Read `CLAUDE.md` first, then this, then the sections of `TODO.md` and
`OPEN_QUESTIONS.md` named below. Written 2026-10-17 at the end of a two-day session; the numbers and states
below were true then, check `git log` before trusting them.

## What this session was for (keep pursuing this)

The author's brief, at the start: review the status of the project, audit the logic, test the testing
suite, and integrate new functionality, over two or three days. **The objective is to advance the project
one more step so the machinery works from end to end as an MVP that can be published and shared while it
keeps being developed.** The parallel objective is to polish the author's own understanding of the project
and its explanation, in the README and in spoken form. Go step by step, one part at a time; the author
reviews each part. Context is a budget: the orchestrator delegates work to agents and keeps its own
context light. The author also works with other agents through the Open Code harness; their roles aren't
fixed yet.

What that meant in practice: audit `/simulate` against the intent in README Part I (the author's most
distilled statement of what the project is for), fix what the audit found, design the missing connections
so that character state causes consequences the way it would in reality (the dice give randomness,
parameters skew them), and get an MVP loop that runs without a person in it. Still to do for the MVP:
audit the testing suite once the simulation architecture settles, run the engine on real corpora (the
three-city one and the author's Milkantis lore), finish README Part I, and the website.

## How to work with the author

- Short, executive answers. Depth only when asked. Don't explain procedures or concepts unprompted.
- Dispatch agents for implementation, one job per agent with a numbered spec and a final report under
  ~300 words. Parallel agents each get their own worktree and branch; merge them yourself. A sole agent
  works in the main folder. The author dislikes stray worktrees: remove them when done.
- **Nothing gets decided silently.** Where a spec leaves room the agent picks, logs the choice in
  `OPEN_QUESTIONS.md` (numbered), and the author confirms by number. Propose, don't decide, on design.
- The author's voice for repo prose (`.claude/VOICE.md`); commit messages plain and short, ending with
  the Co-Authored-By trailer given in the harness. README Part I is the author's own text: never rewrite
  it without being asked (spelling and stale facts only, and say so).
- **Never push without being told.** Commit when asked or at a natural stop. Keep `SESSION_LOG.md` and
  `CHRONICLE.md` current at the end of every session (the author asked for this explicitly).
- Provenance is an engine and ships empty. `provenance-standalone` never carries lore. The author's lore
  and test casts live on corpus branches. Don't ask the author to restate this.
- The decision to defer: Jev (TypeSafe's decision model) stays out until agent decisions that are
  closed choices; see the 2026-10-17 CHRONICLE entry. The testing-suite audit is deferred until the
  simulation architecture settles.

## Where things are

- Branches: `provenance-standalone` (engine, current, default on GitHub), `corpus-three-cities` (cut from
  standalone on 2026-10-16 plus the three-city cast, schema-migrated; behind the engine by ~60 commits),
  `provenance-milkantis` (a clean cut of standalone at `8cab914` for the author's lore, worktree at
  `~/Provenance-milkantis`, behind by ~55 commits). **Nothing after `cd523b9` is pushed; standalone is
  ~61 commits ahead of origin.** Corpus branches are not to be pushed unless the author says so.
- Environment: WSL2 on Windows 11, RTX 4070 SUPER 12 GB. Ollama runs on Windows (`ollama serve`, started
  by hand if the app isn't open); WSL reaches it at `http://localhost:11434` because `.wslconfig` has
  mirrored networking. The enacter is always Ollama, model `qwen2.5:14b` (also installed:
  `qwen2.5-coder:14b`, `qwen3-coder:30b`, too big for 12 GB). A 10.8k-token prompt reads in about 13 s.
- Audit and balance tooling: `/audit-simulate` skill + `scripts/test/audit_simulate.py` (probes, `--baseline`
  diff, snapshots in `diagrams/simulate-audit/`), `scripts/test/balance_economy.py` (toy town with the
  real rules: `--traits`, `--gens`, `--scan`, `--journey`, `--calibrate`), `scripts/test/make_travel_fixture.py`.
  The flow dashboard (sequence view + flowchart + parameter matrix + findings): private artifact
  https://claude.ai/artifact/S7WFikJZZ2u23JfbboB8hD (built on the 2026-10-16 engine; stale on the
  pursuit/economy changes, refresh it by re-running the audit skill).
- Memory notes (`~/.claude/projects/-home-milkucha-Provenance/memory/`): session log at session end;
  engine ships empty.

## What was built this session (all on standalone)

1. Branch cleanup: stale branches and the stashed three-cities dump removed, named lore taken out of
   standalone, the corpus branch cut and migrated.
2. README rewritten in two parts: Part I (concept, the author's own text, banner and four blueprints in
   `assets/blueprints/`) and Part II (technical). Three blueprints still pending from the author
   (characters, simulation, testing).
3. `/simulate` audit and the redesign it led to: weighted destination dice (known suppliers weigh more,
   nearer places weigh more, a kept journey), failed pursuits as scenes (nobody there, can't pay, met on
   the road), an empty place as a reflection scene, a need available at home running the full pipeline,
   named `pursuit` stages, dead characters never met.
4. What the enacter is given: the whole knowledge sample of each participant, the place, a legend of
   every field in the preamble, `ending` and `lived` stripped, temperament as a few words,
   an explicit Ollama context window with truncation checks.
5. Economy: `survive` became `work` (+personal, +pool), one substance at two scopes, eating takes from
   both with half meals, flat per-capita upkeep, numbers adopted 2026-10-17 (`work_pool` 4,
   `work_personal` 3, upkeep 0.05, "review later"), a balance script that tunes by running.
6. Travel as nodes: one automatic road node per connection, roads have no pool, a journey costs food,
   road work is rest.
7. Social circle writer (`{key: kind}`), circle inherited at birth (a seeded 30% of the parents'), the
   `mentioned` kind excluded from the known-supplier tier.
8. Class as three capitals handed down at their own moment: economic at death (split among living
   children, half to the town as a bequeathal tax), social at birth, cultural when a parent completes an
   arc (told like a death, children get the tale, later children too). Arc completion pays a
   provisions reward by how many turns it took.
9. Temperament traits (risk, thrift, communality, persistence) as per-character multipliers on the
   work roll, the payment odds and the destination retry; trend windows scaled by trait; everyone has a
   temperament (no neutrals); the second participant of a scene eats too.

## Where the author's calls live

`TODO.md`: "Pursuit redesign", "What the enacter is given", "Economy rewrite", "Travel as nodes, social
circle writer, class through inheritance", "Temperament traits and recent trends". `OPEN_QUESTIONS.md`:
every default an agent chose, numbered, each awaiting confirmation. `CHRONICLE.md`: the reasoning
behind the landmark decisions (mundaneity is lore; class is three capitals; the roll gets a character).

## Left to do

Waiting on the author:
- Confirm or change the agents' defaults in `OPEN_QUESTIONS.md` (reward formula `clamp(6 + 0.2 x turns, 9,
  15)`, the estate fallback, trend windows, margins, thresholds).
- Whether travel reachability should also exclude `mentioned` people (only the supplier tier was changed).
- Push standalone; merge standalone into `corpus-three-cities` and `provenance-milkantis` (the author
  says when; Milkantis is where they pour their lore and run from the beginning).
- Reflection scenes for ordinary work passes were refused (cost); revisit only if asked.

Queued, not started (the dashboard first, the author wants it as the project's progress view):
- **Make the artifact a real dashboard and keep it current.** Today the private artifact `Pass Map`
  (https://claude.ai/artifact/S7WFikJZZ2u23JfbboB8hD, last published 2026-10-16) is a static snapshot of the
  2026-10-16 engine: it shows findings F1 to F8 and knows nothing of the pursuit redesign, the economy, roads,
  the circle, class or traits. Its source is `diagrams/simulate-audit/artifact.html`. Plan (the author agreed
  to put it here, not yet dispatched): (1) a build script, e.g. `scripts/test/build_dashboard.py`, that reads
  the findings snapshots in `diagrams/simulate-audit/` (seven so far), the audit's stage distributions, the
  balance script's tables, `_lore/tuning.json`, the counts in `OPEN_QUESTIONS.md`/`TODO.md` and the git head,
  and writes the page with the data embedded and a visible 'built from commit X on date Y'; (2) republish to
  the SAME URL with the Artifact tool (update, don't create a new one), and make that the last step of the
  `/audit-simulate` skill; (3) a progress timeline (open vs fixed findings across snapshots), tabs for
  progress and open decisions, flow (sequence + flowchart, updated to the current stages), economy and traits
  balance, the parameter matrix, branch status; (4) optionally a post-commit warning when the dashboard is
  older than the engine code, and pinning it in the sidebar. An alternative (artifact database written
  through `ArtifactData`) only works from inside a Claude session, so start with the build script.
- A real short `/simulate` run on the new engine with `qwen2.5:14b` (everything so far was tested
  mechanically with the model stubbed; whether the 14B model handles the bigger brief well is unknown).
- Audit the testing suite (conformance has a known false positive: kin-as-partner reads `partners`);
  deferred until the simulation settles.
- README Part I: sections still missing (seed, arcs and routines as their own), the voice pass on the
  parts, the three pending blueprints.
- Genericize the real names still in docs and code comments, and decide the `luminacion` datapack
  namespace (it names the author's old world inside the Minecraft layer).
- Remove the Claude-subagent enacter path from `/simulate` if the enacter is always Ollama (flagged,
  not removed).
- Known gaps: `leads`/rivalry follow-up has no call site, reflection mechanism for ordinary passes,
  persistence holding a stalled arc, solo-pass shock and legacy resolution.
- Website: static explainer first (TypeScript, React, Astro for the static part; serif type), then a
  local web app; see `TODO.md` "Website and front-end platform".

## State at hand-off

The calibration agent was halted by the author mid-run (tokens). What it left is committed as `e4ac408`
("... halted mid-run: compiled, not audited"): road work is rest (a work roll on a road node pays and
feeds nothing, keeps the destination, character stays on the node; `apply_survival.py --choice rest`);
an explicit Ollama context window (`tuning.json` `enacter.num_ctx` 12288 plus a pre-flight size check and a
truncation check on Ollama's reported prompt tokens, unit-testable with stubbed bodies); and a
first-guess trait calibration for variation (risk margin 0 to 2 meals, thrift keep 0 to 2, cushion scale 4,
persistence pressure 1.5; old values in the comments). **None of this was audited or measured**: the
agent only compiled it, and the balance script was mid-edit (it had planned to reorder `--gens`
before `--traits` and add death-correlation columns). The author said to take best guesses and tune later.

How far the halted agent had got (rough, read off the diffs, not from its plan):

| Job | Done | What was left |
|---|---|---|
| 1. Calibrate for variation | ~40% | Values applied as first guesses; no before/after tables; the balance script was mid-edit (option reorder, death-correlation columns); the full search was cut on purpose. |
| 2. Road work is rest | ~85% | Code, `--choice rest`, docs and an audit probe are in; the probe was never run. |
| 3. Ollama context window | ~80% | Knob, pre-flight and truncation checks are in; the stubbed-body unit test wasn't confirmed run; the docs note is partial. |
| Verification | ~10% | One audit run, seeded-pair identity, snapshot. |

About 60 to 65% of the original spec, about 80% of the trimmed scope the author gave it (best guesses,
minimal checks, commit). What remains of the trimmed scope is step 2 below.

First things to do cold:
1. `git log --oneline -15` and `git status`; the tree should be clean.
2. One quick `scripts/test/audit_simulate.py` run against `diagrams/simulate-audit/findings-2026-10-17-decisions.json`
   to confirm nothing regressed from `e4ac408` (road rest, num_ctx, the traits values), and fix what fails.
3. Then tune the trait and economy numbers cheaply with `balance_economy.py` (targets the author set:
   work-share spread sd about 0.12 or more, roughly 5 to 15% starvation deaths concentrated among bold and
   free-spending characters, nobody pinned at the cushion floor, wealth not running away across
   generations; some deaths and some error are wanted: variation, not perfection). Don't over-test: the
   author is token-constrained, one table per question.
4. Then the dashboard, a real short `/simulate` run on the new engine with `qwen2.5:14b`, and merging
   standalone into `corpus-three-cities` and `provenance-milkantis` when the author says.

Nothing after `cd523b9` is pushed (about 64 commits ahead). Push only when the author asks.

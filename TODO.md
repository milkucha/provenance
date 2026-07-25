# TODO

Open implementation decisions and work, deferred for later. This is a build/production backlog —
open questions about the lore itself live in `_lore/analysis/unknown.md`, not here.

---

## Sonoros (Balehm)

- [ ] Decide skin (mineskin URL) — `_maps/npcs/registry.json` entry has it blank.
- [ ] Decide movement mode (`NONE` vs. roaming) — determines whether `resume_routine.mcfunction` /
      `check_proximity.mcfunction` are needed at all (README §4).
- [ ] Set `spawn_position` in the registry, or stand at the spot manually before spawning.
- [ ] Build `functions/npcs/sonoros/spawn.mcfunction` from the template.
- [ ] Wire the right-click action to actually start `luminacion:sonoros_lost_traveler`.
- [ ] Spawn in-game and capture `taterzen_uuid` (README §5).

## Nawom & Morkulo (Nvhi — first meeting scene)

- [ ] Neither is registered in `_maps/npcs/registry.json` yet at all — no skin, city, or spawn
      position decided for either.
- [ ] Decide who "hosts" `nawom_morkulo_first_meeting.json` — which of the two is the Blabber
      `interlocutor` when the dialog starts, or whether this needs a different trigger entirely
      (e.g. a proximity/scene trigger rather than a right-click on one specific NPC).
- [ ] Decide the dialog's `end` state action: resume routines for both NPCs, just the triggering
      one, or none at all (relying on the §4 proximity safety net)? Currently left with no `action`
      on purpose, pending this.
- [ ] Register the dialog in `_maps/dialogs/registry.json` once the above is settled — the registry
      format assumes one dialog belongs to one NPC key, which doesn't cleanly fit a two-NPC scene.
- [ ] Decide movement modes for both and build their spawn functions.

## Gondarfolas (Görff)

- [x] Movement mode decided: `PATH` (chosen 2026-07-24 for in-game testing). Built
      `functions/npcs/gondarfolas/spawn.mcfunction`, `resume_routine.mcfunction`, and
      `check_proximity.mcfunction`, and registered the latter in
      `data/luminacion/tags/functions/npc_routine_tick.json`. The actual path waypoints still need
      to be recorded in-game via Taterzens' own `/npc path` commands — until then he'll stand still
      even in `PATH` mode.
- [x] Right-click action wired to start `luminacion:gondarfolas_darnis_and_bracco`.
- [ ] `skin` is filled in from `Luminacion Register [Code].xlsx` (Mineskin column) at the user's
      request — `taterzen_uuid` and `spawn_position` are still blank, per the normal `/enact` flow.
- [ ] Material docs also give an "Easy NPC Preset" (`gondarfolas_gorff`) and Mocap Recording
      reference (`gondarfolas_test2`) and list his role as "Sailing to Terfila" — none of that was
      used here (out of scope for `/enact`); worth checking if a spawn.mcfunction author wants it.
- [ ] Set `spawn_position` in the registry, or stand at the spot manually before spawning (current
      plan: manual, since `spawn_position` is still null).
- [ ] Spawn in-game and capture `taterzen_uuid` (README §5).

## Nuvilo & Nerkeli (Feria del Milenio — hangar eavesdrop scene)

- [ ] Neither is registered in `_maps/npcs/registry.json` with a `spawn_position`, skin, or
      movement mode yet — decide these for both.
- [ ] Decide movement modes for both (they're standing together by the hangar for this scene —
      likely `NONE` for at least the duration of the conversation, but confirm).
- [ ] This dialog is an eavesdrop scene, not a right-click trigger on either NPC — decide how the
      player actually starts/overhears it (proximity trigger? walking near the hangar? a
      `blabber:command` fired from a pressure plate or region check?) rather than the usual
      `enter_dialog` right-click wiring.
- [ ] Decide who (if either) "hosts" `nuvilo_nerkeli_feria_del_milenio.json` for registry purposes,
      or whether it needs a different registration shape entirely — same open question as the
      Nawom & Morkulo entry above, and for the same reason: `_maps/dialogs/registry.json` assumes
      one dialog belongs to one NPC key, which doesn't cleanly fit a two-NPC eavesdrop scene.
- [ ] Decide the dialog's `end` state action — currently left with no `action` at all (matching the
      Nawom & Morkulo precedent), pending the movement-mode and trigger decisions above.
- [ ] Build spawn functions for both once the above is settled.

## Nuvilo (Feria del Milenio — scholar dialog vs. the player)

- [ ] Movement mode not decided yet. The dialog's `end` state already wires a `resume_routine` call
      (`luminacion:npcs/nuvilo/resume_routine`), matching the Sonoros/Gondarfolas precedent of
      filling it in ahead of the movement-mode decision — if Nuvilo ends up `NONE`, remove that
      action and drop `resume_routine.mcfunction`/`check_proximity.mcfunction` per §4.
- [ ] Decide skin (mineskin URL) and `spawn_position` — both blank in the registry.
- [ ] Build `functions/npcs/nuvilo/spawn.mcfunction` from the template.
- [ ] Wire the right-click action to actually start `luminacion:nuvilo_scholar_at_the_feria`.
- [ ] Spawn in-game and capture `taterzen_uuid` (README §5).

## Nerkeli (Feria del Milenio — hangar dialog vs. the player)

- [ ] Movement mode not decided yet — same open question as the Nuvilo & Nerkeli eavesdrop scene
      above, but note that dialog left `end` with no action while *this* one (`nerkeli_hangar_talk`)
      already wires `resume_routine` on both endings (`end_showcase`/`end_feria`), matching the
      Sonoros/Nuvilo/Gondarfolas precedent — if Nerkeli ends up `NONE`, remove those actions and drop
      `resume_routine.mcfunction`/`check_proximity.mcfunction` per §4. Whatever gets decided should
      apply consistently across both of his dialogs.
- [ ] Decide skin (mineskin URL) and `spawn_position` — both blank in the registry.
- [ ] Build `functions/npcs/nerkeli/spawn.mcfunction` from the template.
- [ ] Wire the right-click action to actually start `luminacion:nerkeli_hangar_talk`.
- [ ] Spawn in-game and capture `taterzen_uuid` (README §5) — shared with the eavesdrop-scene entry
      above; only needs doing once.

## Döran (Salthos Cruzados — Plaza de las Culturas, Feria del Milenio)

- [x] Movement mode decided: `PATH` (chosen 2026-07-25, via the new `/spawn` skill — a plaza host who
      patrols a loop around the four castle replicas). Built `functions/npcs/doran/spawn.mcfunction`,
      `resume_routine.mcfunction`, `check_proximity.mcfunction`, `heal_skin.mcfunction`, and
      `heal_path.mcfunction`, and registered `check_proximity` in
      `data/luminacion/tags/functions/npc_routine_tick.json`. Actual path waypoints still need to be
      decided and recorded via `functions/npcs/doran/paths/<path_name>.mcfunction` (see
      `_templates/npcs/paths/select_path.mcfunction`) — until then he'll stand still even in `PATH`
      mode, same as Gondarfolas.
- [x] **Random dialog selection mechanism resolved — took two rounds of real in-game debugging.**
      Round 1: the roll added directly as `npc edit commands add minecraft execute store result
      score doran_dialog_roll luminacion.int run random value 1..3` failed to load at all
      (`logs/latest.log`: Brigadier parse error at the start of `random`). Suspected at the time this
      was specific to nesting inside Taterzens' `npc edit commands add` argument, so round 1's fix
      moved the roll into its own `functions/npcs/doran/roll_dialog.mcfunction`, called via a plain
      `function` command — but kept `random value 1..3` inside that function.
      Round 2: `roll_dialog.mcfunction` *also* failed to load with the exact same error, even as a
      plain top-level `.mcfunction` line with no Taterzens argument involved at all — disproving the
      nesting theory. `/random` is simply unavailable in this pack's actual server environment (root
      cause undetermined; nothing else in the logs uses it successfully either). Also explains why
      right-clicking Döran (once deselected, past the separate NPC-edit-UI-on-selected-NPC quirk) did
      nothing at all: `doran_dialog_roll` was never set, so all three `matches` gates were always
      false. Fixed by rewriting `roll_dialog.mcfunction` to use `time query gametime` reduced mod 3
      via a scoreboard operation instead — no special command needed. The three
      `execute if score ... run blabber dialogue start ...` dispatch commands stay directly-added
      (per `_maps/actions/registry.json` → `_action_templates.random_dialog`, so `--clicker--`
      substitution keeps working); these are still the one piece of this mechanism not yet confirmed
      working end-to-end in-game.
      Also fixed in round 1, still holds: `@e[name=Döran,...]` (unquoted) failed to parse because `ö`
      isn't in Brigadier's unquoted-string charset — fixed by quoting (`name="Döran"`) in
      `check_proximity.mcfunction`, `heal_skin.mcfunction`, `heal_path.mcfunction` (comment), and the
      selectors in `spawn.mcfunction`.
      Round 3 (2026-07-25, caught by the user in-game, not the log): round 1 over-applied that same
      quoting fix to `npc create "Döran"` too, which is a DIFFERENT argument (Taterzens' own, not a
      vanilla selector) that doesn't strip quote characters — the NPC's actual name ended up
      literally containing the quote marks (`"Döran"`), unselectable normally and mismatching every
      `@e[name="Döran",...]` selector in his other functions (looking for the name without quotes).
      Reverted to unquoted `npc create Döran` — this argument takes `ö` raw with no complaint and was
      never the source of any parse error, only the selectors were. Both the correct rule and the
      wrong turn are documented in `_action_templates.random_dialog` and
      `.claude/skills/spawn/SKILL.md` for reuse — never use `/random` anywhere in this pack; quote
      diacritic-bearing names in every vanilla `@e[...]` selector referencing them; do NOT quote
      `npc create <name>` itself. **Confirmed working after this fix** — dialog opened correctly.
      Round 4 (2026-07-25, same session): dialog opened, but the user reported Döran started
      wandering mid-conversation and no nodding was visible. Root cause: `check_proximity.mcfunction`'s
      resume safety-net used the same 2-block radius as its pause trigger. Taterzens has no
      interact-range override (`config/Taterzens/config.json` confirmed no such setting — plain
      vanilla reach, 6 blocks in creative), so a click from beyond 2 blocks read as "nobody nearby" on
      the very next tick, undoing the pause (reverting to PATH) while the dialog was still open — the
      wandering, and its movement/rotation writes fighting and swallowing the nod animation, are both
      symptoms of the same bug. Fixed pack-wide (not just Döran): resume radius widened from 2 to 6
      blocks in `_templates/npcs/check_proximity.mcfunction` and all four existing per-NPC copies
      (`gondarfolas`, `nerkeli`, `nuvilo`, `doran`), plus README §4 and
      `_action_templates.routine_pause_resume` corrected to explain why the two radii must differ.
      **Not yet independently ruled out**: repeated `/function .../spawn` re-runs during rounds 1-4
      (5 "spawned successfully" messages logged) may have left stray duplicate "Döran" entities behind
      if older ones weren't killed each time — `@e[name="Döran",...,sort=nearest]` would then silently
      target whichever copy is nearest, which could look identical to this bug. Worth an `/npc list`
      check before trusting the fix is complete. **Still needs one more `/reload` + a real
      right-click-and-wait test** to confirm he now stays still/facing the player and nods correctly
      for a full conversation — check `logs/latest.log` for `doran` before assuming it's clean, same
      as every previous round.
- [x] Skin decided: `https://minesk.in/c336e48215fb4759908960d4a2748b2a`, filled into
      `_maps/npcs/registry.json` and `spawn.mcfunction`/`heal_skin.mcfunction`. `spawn_position` stays
      `null` — positioning him at the Plaza in-game will be manual, per user preference (same as
      Gondarfolas).
- [x] Built `functions/npcs/doran/spawn.mcfunction` from the template, right-click action wired (see
      random-dialog point above).
- [ ] Spawn in-game, position him at the Plaza de las Culturas, decide and record path waypoints, and
      capture `taterzen_uuid` (README §5).

## Khaoe & Farlis (Feria del Milenio — Castillo de Görff replica, Plaza de las Culturas)

- [ ] A fourth dialog, `khaoe_calendario_mecanografico.json` (Khaoe vs. the player, at the Feria's new
      Calendario Mecanográfico — a different spot from the castle replica scenes below), and a fifth,
      `khaoe_banco_colectivo.json` (Khaoe vs. the player, sitting on a bench elsewhere at the Feria),
      are already registered normally in `_maps/dialogs/registry.json` under her key, per the
      single-NPC-vs-player flow — unlike the three ambient ones below, these don't have an open
      registration question. Both still need actual right-click wiring once
      `functions/npcs/khaoe/spawn.mcfunction` exists (`npc edit commands add ... blabber dialogue
      start luminacion:<dialog_id> --clicker-- ...`, one command per dialog, since Khaoe now has more
      than one vs.-player dialog — decide then whether they need Döran's `random_dialog` treatment too,
      or whether each is meant to trigger only in its own specific spot, which would need a
      location/proximity condition rather than a plain right-click gate).

Three short ambient dialogs (`khaoe_farlis_el_castillo_que_fue.json`,
`khaoe_farlis_lo_que_cambia_el_tiempo.json`, `khaoe_farlis_esperando_a_khaasan.json`), written in
Latin American Spanish, meant to connect as fragments of one ongoing conversation but fire
independently — the player should overhear whichever one comes up, not all three in sequence. Per
`/enact` §8's Step 6 rule for two-NPC dialogs ("do not guess how to register a dialog that belongs to
two NPCs"), the following is deliberately left open rather than decided silently:

- [ ] **Random-pick wiring.** The existing mechanism for "N independent dialogs, picked at random on
      right-click" is Döran's `_action_templates.random_dialog` (see `_maps/actions/registry.json` and
      `functions/npcs/doran/roll_dialog.mcfunction`/`spawn.mcfunction`) — gametime-mod-N via
      scoreboard, since `/random` doesn't work in this environment at all (see the Döran section
      above). That pattern was built for one NPC picking among its own solo dialogs; here there are
      *two* NPCs sharing *one* shared set of three dialogs. Decide: does right-clicking either Khaoe or
      Farlis trigger the same roll into the same three files (two independent roll scores,
      `khaoe_dialog_roll`/`farlis_dialog_roll`, both gated 1..3 against the same three
      `khaoe_farlis_*` dialog ids), or does only one of them act as the "trigger" NPC while the other
      just stands there silently animated? Either way, `--clicker--` still needs to resolve to
      whichever NPC the player actually clicked, per the dispatch-commands-stay-directly-added rule.
- [ ] **`_maps/dialogs/registry.json` registration.** Same open question as Nawom & Morkulo and
      Nuvilo & Nerkeli above — the registry format assumes one dialog belongs to one NPC key, which
      doesn't cleanly fit three dialogs shared by two NPCs. Decide once the wiring question above is
      settled.
- [ ] **Movement mode** not decided for either — they're standing still together at the Castillo de
      Görff replica for this scene, which suggests `NONE`, but confirm. Each dialog's `end` state is
      currently plain `end_dialogue` with no `resume_routine` action (matching the Nawom & Morkulo /
      Nuvilo & Nerkeli precedent for undecided-movement two-NPC scenes) — add the action only if
      either ends up roaming.
- [ ] `spawn_position` and `taterzen_uuid` are still blank/null for both in the registry (skins were
      already on file from before this `/enact` run and were left as-is). Decide placement — likely
      standing at/near the Castillo de Görff replica in the Plaza de las Culturas, alongside Döran's
      pavilion — and build `functions/npcs/khaoe/spawn.mcfunction` and
      `functions/npcs/farlis/spawn.mcfunction` from the template once the wiring question above is
      resolved (spawn.mcfunction is where the right-click random-dialog commands actually get added).
- [ ] Khaoe and Farlis both had pre-existing one-line registry stubs before this run (`"Member of the
      Collective."` / `"Member of the Collective. Travels the Khol Moshin-Görff route on
      horseback."`) with no `knowledge.education` sample drawn yet — this `/enact` run was their first
      real pass, so both got a full backstory merge (new detail layered onto what was already there,
      not replacing it) and a fresh 27% composite knowledge sample each. Nothing left open on that
      front, noted here only for context if a future run wonders why their samples look freshly drawn
      despite the stub predating this session.
- [ ] Khaasan (mentioned in all three dialogs, expected to arrive by griffon, not yet seen) was not
      enacted this run and his registry entry was left untouched — his one-word backstory tag is
      "Teletraveller," which the hearsay record for `khaoe_farlis_esperando_a_khaasan.json` already
      flags as a divergence from the "arrives by griffon" expectation voiced in-scene (see
      `_lore/analysis/hearsay.md`). Left unresolved on purpose — see that entry's note before deciding
      whether Khaasan's own eventual `/enact` pass should reconcile it or lean into the contradiction.

## Gesture animation system (resource pack)

Built 2026-07-25/26: a custom EMF/Iris `player.jem`/`player_slim.jem` override giving Taterzens NPCs
(and real players) 7 animated gestures — wave, point, bow, shrug, palms-up (originally prototyped as
"cross-arms", renamed once it visually read as the former instead), scratch-head, and laugh — each
triggered by an invisible `minecraft:stick{CustomModelData:<101-107>}` in the main hand, smoothly eased
via a self-referencing `var.*` low-pass filter pattern (proven more reliable than self-referencing the
bone key directly, which jittered). Coexists with the already-installed Fresh Animations + FA+Player by
forking only `player.jem`/`player_slim.jem` (the two files that needed the gesture hook) rather than the
whole pack — every other file (movement/idle/equipment math, textures, cape) still falls through to
FA+Player underneath, since Minecraft resolves each asset path independently across the active pack
stack. Full technical writeup lives in this conversation's history (2026-07-25/26 session), not yet
copied into README/registry docs.

Wired into Döran's three dialogs (`doran_plaza_orientation`, `doran_four_castles`,
`doran_eras_of_culture`) via 7 new `functions/npcs/_shared/gesture_<name>.mcfunction` files (already
git-tracked, datapack-side) + a shared `gesture_clear.mcfunction`, following the same
tag+`schedule ... replace` pattern as `nod_up_down.mcfunction`. Each wired dialogue state's action
*replaces* its `nod_up_down` call rather than adding to it, so gesture and nod are mutually exclusive by
construction — every other line keeps its ordinary nod untouched.

- [ ] **Multi-NPC gesture/nod scheduling collision** (found 2026-07-25 building the jump gesture, not
      yet fixed): `gesture_clear.mcfunction`, and the `nod_up_down_2/_3/_4` / `nod_left_right_2/_3/_4`
      continuation chains, all advance via `schedule function <id> <ticks>t replace` — but
      `schedule function` is a single global timer *per function ID* in vanilla Minecraft, not
      per-entity. Every `gesture_<name>.mcfunction` schedules the same `gesture_clear`, so if NPC A
      starts a gesture and NPC B starts any gesture a few ticks later, B's `replace` call overwrites
      A's pending timer — A's hold then gets cut short or stretched to whenever B's schedule actually
      fires, and when it fires, `gesture_clear` clears *every* entity currently tagged
      `luminacion.gesture_active` at once, not just the one whose hold time actually expired. Harmless
      so far (all testing has been one NPC gesturing at a time), but jump's much shorter `12t` hold vs.
      everyone else's `50t` (see `gesture_jump.mcfunction`'s own docstring, where this was first
      flagged) makes the collision far more likely to actually manifest once enough NPCs exist that two
      might gesture within a few ticks of each other. The identical flaw exists independently in
      `nod_up_down`/`nod_left_right`: confirmed by reading `nod_up_down_4.mcfunction` — beat 4 applies
      to *every* `@e[tag=luminacion.gesture_nod_ud]` at once, so a second NPC nodding mid-way through a
      first NPC's nod compresses/desyncs both nods' beat timing (`nod_left_right` mirrors this exactly,
      via `luminacion.gesture_nod_lr`). System-wide fix needed, not a jump-specific patch.

      **Planned fix — per-entity scoreboard countdown instead of global `schedule`.** 1.20.1 has no
      `mcfunction` macros (`$(arg)`, added 1.20.2+), which is what would otherwise let a scheduled
      callback carry per-entity context — so the fix has to route around `schedule` entirely for
      anything needing true per-entity independence:
        1. Add a new `dummy` scoreboard objective (e.g. `luminacion.gest_timer`) in `load.mcfunction`,
           alongside the existing `luminacion.bool`/`luminacion.int`.
        2. Every `gesture_<name>.mcfunction` sets `scoreboard players set @s luminacion.gest_timer
           <duration>` (its own per-gesture hold — 12 for jump, 50 for the rest) instead of calling
           `schedule function .../gesture_clear ... replace`.
        3. `tick.mcfunction` gets one new line calling a shared function that, every tick: decrements
           `luminacion.gest_timer` for every `@e[tag=luminacion.gesture_active]`, then runs a
           "clear self" step (item off, tag off) only `as`/`at` whichever entities' timer has just hit
           0 — each NPC's gesture then ends exactly `<duration>` ticks after *it* started, independent
           of what any other NPC is doing.
        4. Same treatment for the nod families, though scope this as its own decision once the
           gesture-side fix is proven: replace the `nod_up_down_2/_3/_4` (and `_left_right` equivalent)
           schedule chain with per-entity beat state on the same countdown pattern — nods are a fixed
           ~9-tick, 4-beat sequence rather than "hold then clear", so this is more naturally a per-tick
           state machine keyed off one countdown value (current beat = f(ticks remaining)) than four
           separately-scheduled function hops.
        5. Update every `gesture_*.mcfunction`/`nod_*.mcfunction` docstring that currently describes
           the `schedule ... replace` caveat (worded near-identically in several files) once the
           mechanism underneath them actually changes.
        6. `gesture_clear.mcfunction` itself gets simplified/renamed once it's driven from the tick
           loop with an already-narrowed selector, rather than unconditionally clearing every tagged
           entity on a global timer.
- [ ] **Not yet version-controlled**: the resource pack itself (`pack.mcmeta` +
      `assets/minecraft/emf/cem/player.jem`/`player_slim.jem` + the invisible item model/texture under
      `assets/minecraft/models/item/stick.json` + `assets/luminacion/...`) still lives only at
      `resourcepacks/luminacion-gesture-test/` in the PrismLauncher instance — outside this git repo,
      named as a throwaway test folder. User wants it moved into the production/version-controlled
      folder; deferred to decide **where** exactly (2026-07-26 session ran out of day before deciding).
      Two options were on the table, both with real tradeoffs:
        1. New standalone git repo initialized directly at `resourcepacks/<name>/` — mirrors exactly how
           *this* datapack repo already works (the repo IS the live folder Minecraft loads from, no
           symlink/copy step ever needed) — but is a second repo to manage.
        2. Move it into *this* repo as a subfolder (e.g. `assets/` alongside `data/`, matching the
           Localization section's existing plan below — see `scripts/build_resourcepack.py`), then
           symlink `resourcepacks/<name>/` to it — one repo, but needs a working Windows symlink
           (Developer Mode or admin rights) and silently breaks if that link is ever lost/not recreated
           on a new machine.
      **Relevant precedent already on record** (see Localization section immediately below): this
      project already planned for `assets/luminacion/lang/en_us.json` to live alongside `data/` in this
      same repo, plus a future `scripts/build_resourcepack.py` that zips `assets/` + its own
      `pack.mcmeta` into a resource pack — i.e. the project's own established intended pattern already
      leans toward option 2 (single repo). Worth weighing against symlink reliability before deciding.
      Also applies here regardless of which option is picked: the Localization section's "need a second
      `pack.mcmeta` for the resource pack" point is the same constraint the gesture pack already has
      (it already ships its own separate `pack.mcmeta`, currently sitting outside this repo).
- [ ] Once the location is settled: move/copy the pack's contents there, rename away from
      `-gesture-test`/`-test` naming now that it's graduating from prototype, and update this repo's own
      `resourcepacks/` reference (the live folder Minecraft actually loads) to match — either by having
      the new repo live there directly (option 1) or via the symlink (option 2).
- [ ] Still main-hand only (off-hand path never built — would need the trickier
      `Inventory`/slot-`-106` NBT path discovered for real players, unconfirmed for Taterzens).
- [ ] Elbow joint (separate forearm bone) — attempted 2026-07-25 for the new cross-arms gesture as a
      nested `submodels` child bone of `right_arm`/`left_arm`, reverted same day: this CEM/EMF build
      does **not** compose a nested submodel's rotation with its parent's — the child renders at its
      raw `translate` position, unrotated by the arm, so it visually detached from the elbow (and broke
      the base player model, not just the gesture, since the split was unconditional). Real elbow
      articulation would need explicit forward-kinematics math (rotate the elbow pivot by the shoulder's
      current rotation) baked into the expression language, not simple nesting — bigger scope than
      previously estimated, not started.
- [ ] Only Döran has gestures wired so far — Gondarfolas, Nuvilo, Nerkeli, and any future NPCs' dialogs
      don't use them yet.

## Localization (per-player dialog language)

- [ ] Add a top-level `assets/luminacion/lang/en_us.json` (and other language files as they're
      written) alongside `data/` in this same repo. The datapack loader only ever reads `data/`, so
      `assets/` living here during dev is inert to it — no folder split needed for authoring.
- [ ] Write `scripts/extract_dialogue_lang.py`: sweeps `data/luminacion/blabber/dialogues/*.json`
      (templates excluded), derives a deterministic key per line as
      `luminacion.dialogue.<file_stem>.<state_id>` (and `.choice.<n>` for choices), writes/updates
      the key → text entry in `assets/luminacion/lang/en_us.json`, and rewrites the dialogue file's
      `text` field to `{"translate": key}`. Mechanical and re-runnable — authoring stays plain literal
      text (no change to `/enact` Step 4/5 or to how `hearsay.md` gets written), and this only runs
      as a deliberate "finalize for localization" pass over already-written dialogues.
- [ ] Document, in `hearsay.md`'s own preamble and README §8, that once a dialogue has been through
      extraction, `assets/luminacion/lang/en_us.json` (not the dialogue file) is the resolved source
      of truth for what a line actually says — the same role `_lore/material/` plays for `context.md`.
      Only matters for *revisiting* an already-extracted dialogue (e.g. a later `/enact` run
      referencing an existing NPC's old lines); doesn't affect authoring a new dialogue, since the
      English text is still written and read literally before extraction ever runs.
- [ ] Write `scripts/build_resourcepack.py`: zips `assets/` + a resource-pack `pack.mcmeta` into
      `saves/Miniatures/resources.zip` for local per-world testing (Minecraft's per-world resource
      pack mechanism), and separately emits `dist/Luminacion/` (datapack: `data/` + its `pack.mcmeta`)
      and `dist/Luminacion-resourcepack.zip` (resource pack) for release — built only from `data/` and
      `assets/`, leaving `_lore/`, `_maps/`, `_templates/`, `scripts/`, and the docs out of both.
- [ ] Need a second `pack.mcmeta` for the resource pack (own `pack_format`) — the datapack's existing
      root `pack.mcmeta` can't serve both.
- [ ] Convert existing dialogue files to translation keys via the extractor once it exists (currently
      all six non-template dialogues use literal `text`).

## Lore integration skill (`/integrate`)

- [x] Built 2026-07-25: `.claude/skills/integrate/SKILL.md`, documented in README §0 (Layer 1).
      Three passes — analyse new `_lore/material/` into `context.md`/`encodings.json`/`unknown.md`;
      audit `data/luminacion/blabber/dialogues/` for missing `hearsay.entries` coverage; check for
      drift between what's referenced elsewhere (registries, sampled knowledge) and what's actually
      recorded in `encodings.json`.
- [ ] Not yet run end-to-end against real material or a real drift case — worth a first live pass
      next time material is added or a periodic audit is due, to confirm the three passes hold up in
      practice rather than just on paper.

## General

- [ ] Once one of the above ships, consider adding it as a second worked example in README §8
      (currently only references the Sonoros dialog).
- [ ] Trading with NPCs: vanilla's trade UI only opens via right-click on an actual
      `villager`/`wandering_trader` entity (custom `Offers` NBT), which doesn't integrate with
      Taterzens' `npc edit commands` action pipeline — would need a paired, disguised villager
      entity kept in sync with the Taterzens NPC. Alternative: a small Fabric mod exposing a command
      (e.g. `luminacion:trade open <trade_table> <player>`) that opens `MerchantScreenHandler`
      directly against a custom `Merchant` implementation, no entity required — see
      [VillagerConfig](https://modrinth.com/mod/villagerconfig)'s `/vc test villager` for a working
      precedent of this pattern. Decide which approach before any NPC needs trading.

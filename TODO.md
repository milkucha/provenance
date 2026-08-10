# TODO

Open implementation decisions and work, deferred for later. This is a build/production backlog —
open questions about the lore itself live in `_lore/unknowns.md`, not here.

## Knowledge mutation system (2026-08-01)

Implemented: Step 5 of `/enact` now records hearsay with mutations applied. Each character's
understanding is filtered through their criterion/trusts/distrusts/wasted_life. Original unmutated
versions are not recorded (unless they had separate hearsay entries). The lineage_coin mechanism
already decides traceable vs untraceable origins.

- [ ] **Retroactive mutation.** All existing hearsay entries (Nawom/Morkulo, Feria scenes, Khaoe/Farlis entries) should be reviewed and updated to reflect mutations. Priority: entries that spawned into major characters' education (Bardaglis's song from Khaoe/Farlis; Farlis/Aureobalo bar scene). Lower priority: one-off encounters (Gok/Nerkeli).
- [ ] **Material mutation.** When characters cite objective material (eras, locations), record how they reframed it. Current scenes may have missed this — not retroactive work needed, but forward pattern to apply from now on.
- [ ] **Auroboro III & Farlis hearsay:** Entry rewritten with mutations applied (2026-08-01). Both perspectives recorded; claims reflect each character's interpretation, not objective fact.

## Auroboro III & Farlis, Alcoba de las Guerras (2026-08-01)

Dialog written: `auroboro_iii_farlis_alcoba.json`. Hearsay entry recorded (27 total).
Auroboro III: lived 0→1, tempered 0→1 (first shock — rejected Farlis's radical reframing of the Guerras as hierarchy-oppression).
Farlis: lived 8→9. No shock (anchor not referenced).

- [ ] **Dialog registration ambiguous.** Auroboro III is a new NPC with no existing dialog registry entry. Farlis already has one (`khaoe_farlis_*`). Should Auroboro III's key point to this new dialog, or should both be listed somehow? Same multi-NPC registration question as Nawom & Morkulo.
- [ ] **Auroboro III spawn work** — skin, movement mode, `spawn_position`, UUID. Placeholder logged here pending those decisions.
- [x] **Gestures baked** (2026-08-05) — 3 of 9 states now carry a gesture (`gesture_wave`,
      `gesture_no`, `gesture_face_palm`) instead of uniform `nod_up_down`. Run as a one-time backlog
      cleanup when `/bake_dialog` was retired in favor of `/embody` baking inline (see `/embody`
      Step 3) — this file predates that change and was never touched by it directly.

## Khaoe & Milkucha, Jardín de los Parajes (2026-08-01)

Dialog written: `khaoe_milkucha_jardin_de_los_parajes.json`. Hearsay entry recorded (24 total).
Khaoe lived: 9 → 10. No shocks (anchor not referenced).

- [ ] **Dialog registration ambiguous.** Khaoe already has an entry in `_npcs/dialogs/registry.json`
      pointing to `khaoe_banco_colectivo.json`. This new dialog is a second conversation she has,
      this time with Milkucha (the player). Should it overwrite that entry, or should Khaoe's key
      point to a list, or should it stay separate in TODO until the registry format decision is made?
      Same question as the three Feria scenes (Nawom & Morkulo precedent).
- [ ] **Milkucha is a new NPC, introduced only through this scene.** They're the player, so they're
      not being added to the NPC roster (same as Sonoros), but if you want to track them for
      reference, note it in TODO or create a light entry tagged "player-character" and leave it
      untracked.
- [x] **Gestures baked** (2026-08-05) — 10 of 34 states now carry a gesture (`gesture_wave` bookending
      the scene's open/close, `gesture_flex_arm` on Milkucha's mod-powered brag, `gesture_point_left`
      on the literal "a tu izquierda" line, and others) instead of uniform `nod_up_down`. Run as a
      one-time backlog cleanup when `/bake_dialog` was retired in favor of `/embody` baking inline.

---

## Sonoros (Balehm)

- [ ] Decide skin (mineskin URL) — `_npcs/npcs/registry.json` entry has it blank.
- [ ] Decide movement mode (`NONE` vs. roaming) — determines whether `resume_routine.mcfunction` /
      `check_proximity.mcfunction` are needed at all (README §4).
- [ ] Set `spawn_position` in the registry, or stand at the spot manually before spawning.
- [ ] Build `functions/npcs/sonoros/spawn.mcfunction` from the template.
- [ ] Wire the right-click action to actually start `luminacion:sonoros_lost_traveler`.
- [ ] Spawn in-game and capture `taterzen_uuid` (README §5).

## Nawom & Morkulo (Nvhi — first meeting scene)

- [x] Trigger/hosting decided (2026-07-30): proximity-based, same mechanism as the khaoe_farlis_*
      fragments — hosted under Nawom's key (his spawn.mcfunction will own the proximity check),
      rather than a plain right-click on either NPC.
- [ ] Neither is registered in `_npcs/npcs/registry.json` yet at all — no skin, city, backstory, or
      spawn position decided for either. Run `/character` for both before building spawn functions.
- [ ] Decide the dialog's `end` state action: resume routines for both NPCs, just the triggering
      one, or none at all (relying on the §4 proximity safety net)? Currently left with no `action`
      on purpose, pending this.
- [ ] Register the dialog in `_npcs/dialogs/registry.json` under Nawom's key once he's registered and
      the proximity check exists — same shape as Nerkeli's `_comment` for
      `nuvilo_nerkeli_feria_del_milenio`.
- [ ] Decide movement modes for both and build their spawn functions — Nawom's also needs the
      proximity roll/check logic once his movement mode is decided.

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

- [x] Trigger/hosting decided (2026-07-30): proximity-based, same mechanism as the khaoe_farlis_*
      fragments — hosted under Nerkeli's key (his hangar, his spawn.mcfunction will own the proximity
      check against Nuvilo). Registered in `_npcs/dialogs/registry.json`.
- [ ] Neither is registered in `_npcs/npcs/registry.json` with a `spawn_position` or skin yet —
      decide these for both.
- [ ] Movement modes for both — likely `NONE` for at least the duration of the conversation (they're
      standing together by the hangar), but confirm.
- [ ] Decide the dialog's `end` state action — currently left with no `action` at all, pending the
      movement-mode decision above.
- [ ] Build spawn functions for both — Nerkeli's needs the proximity roll/check logic against Nuvilo
      added, matching Khaoe's `roll_dialog.mcfunction` pattern.

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

## Iläria (Feria del Milenio — Espiral de la Historia)

- [x] Movement mode decided: `NONE` (stationary) — matches her backstory of being permanently
      stationed at the center of the Espiral's labyrinth. `resume_routine.mcfunction`,
      `check_proximity.mcfunction`, `heal_skin.mcfunction`, `heal_path.mcfunction` all built per the
      current house rule (every NPC gets this machinery regardless of movement mode), and
      `ilaria_espiral_de_la_historia.json`'s `end` state now calls `resume_routine`.
- [x] Skin decided: `https://minesk.in/016a5789bc0145a19b63db9a2ae65ed1` (in the registry and wired
      into `spawn.mcfunction`/`heal_skin.mcfunction`).
- [ ] `spawn_position` left `null` on purpose (user's choice) — position her manually in-game at the
      entrance to the Espiral de la Historia, once that structure exists.
- [x] `functions/npcs/ilaria/spawn.mcfunction` built from the template.
- [x] Right-click wired to `luminacion:ilaria_espiral_de_la_historia` (single dialog, no side effects).
- [x] `luminacion:npcs/ilaria/check_proximity` registered in
      `data/luminacion/tags/functions/npc_routine_tick.json`.
- [ ] No path needed (`NONE`, no waypoints) — `heal_path.mcfunction` is a header-only stub, matching
      Khaoe's precedent.
- [ ] Spawn in-game and capture `taterzen_uuid` (README §5).

## Döran (Salthos Cruzados — Plaza de las Culturas, Feria del Milenio)

- [x] Movement mode decided: `PATH` (chosen 2026-07-25, via the new `/spawn` skill — a plaza host who
      patrols a loop around the four castle replicas). Built `functions/npcs/doran/spawn.mcfunction`,
      `resume_routine.mcfunction`, `check_proximity.mcfunction`, `heal_skin.mcfunction`, and
      `heal_path.mcfunction`, and registered `check_proximity` in
      `data/luminacion/tags/functions/npc_routine_tick.json`. Actual path waypoints still need to be
      decided and recorded via `functions/npcs/doran/paths/<path_name>.mcfunction` (see
      `_npcs/templates/paths/select_path.mcfunction`) — until then he'll stand still even in `PATH`
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
      (per `_npcs/actions/registry.json` → `_action_templates.random_dialog`, so `--clicker--`
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
      blocks in `_npcs/templates/check_proximity.mcfunction` and all four existing per-NPC copies
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
      `_npcs/npcs/registry.json` and `spawn.mcfunction`/`heal_skin.mcfunction`. `spawn_position` stays
      `null` — positioning him at the Plaza in-game will be manual, per user preference (same as
      Gondarfolas).
- [x] Built `functions/npcs/doran/spawn.mcfunction` from the template, right-click action wired (see
      random-dialog point above).
- [ ] Spawn in-game, position him at the Plaza de las Culturas, decide and record path waypoints, and
      capture `taterzen_uuid` (README §5).

## Khaoe & Farlis (Feria del Milenio — Castillo de Görff replica, Plaza de las Culturas)

- [x] **Khaoe fully wired, 2026-07-25 (`/spawn` skill).** Movement mode: `NONE` (stationary, user's
      explicit preference — "maybe it doesn't make sense" by their own admission, kept anyway).
      Built `functions/npcs/khaoe/spawn.mcfunction` and `functions/npcs/khaoe/roll_dialog.mcfunction`.
      `spawn_position` stays `null` (manual placement, per user preference, same as
      Gondarfolas/Döran) — `taterzen_uuid` still needs the normal capture pass (README §5).
- [x] **Pack-wide policy correction, same session: the routine pause/resume + self-heal machinery is
      now built for EVERY NPC regardless of movement mode, not just roaming ones.** Khaoe originally
      shipped with only `spawn.mcfunction`/`roll_dialog.mcfunction` under the old "skip for `NONE`"
      rule (README §4, the `/spawn` skill, and `_action_templates.routine_pause_resume` all said this)
      — the user caught that her skin had broken (Taterzens' async mineskin fetch lost the race) with
      no `heal_skin.mcfunction` around to fix it, and pointed out the async-fetch race has nothing to
      do with movement mode. Retrofitted: built `functions/npcs/khaoe/resume_routine.mcfunction`
      (`<MODE>` = `NONE`, a behavioral no-op but still clears the pause/dialog tags),
      `check_proximity.mcfunction`, `heal_skin.mcfunction`, and a header-only `heal_path.mcfunction`
      stub (no path defined); registered `luminacion:npcs/khaoe/check_proximity` in
      `data/luminacion/tags/functions/npc_routine_tick.json`; added the
      `execute as @interlocutor run function luminacion:npcs/khaoe/resume_routine` action to the `end`
      state of all five of her dialogs (previously plain `end_dialogue` with no action). Updated the
      scoping language pack-wide to match: README §4 (now "every NPC", not "roaming NPCs only"),
      `.claude/skills/spawn/SKILL.md` (Steps 2/5/6), and `_npcs/actions/registry.json` →
      `_action_templates.routine_pause_resume`. Also fixed, while touching `heal_skin.mcfunction`'s
      template: a stale `scoreboard players set <npc_key>_skin_cd luminacion.int 0` line that was
      never actually part of the real pattern (Gondarfolas's built file already omitted it — the two
      heal functions share `check_proximity.mcfunction`'s own `<npc_key>_heal_cd` counter, reset
      there) — the template just hadn't been corrected to match. Net effect: a stationary NPC now
      still briefly turns to face a player who gets close or talks to it (via `pause_routine`'s
      `FORCED_LOOK`), then reverts to `NONE` once they leave/the dialog ends, same tagging as any
      roaming NPC — this is a side effect of the fix, not something separately requested.
- [x] **Right-click wiring resolved for all five dialogs, condition-gated rather than a plain
      always-fire trigger:**
      - `khaoe_calendario_mecanografico` fires when Khaoe's own live Taterzens pose is `STANDING` and
        Farlis isn't nearby (see next point) — checked directly via
        `execute if data entity @e[name=Khaoe,...] {TaterzenNPCTag:{Pose:"STANDING"}} run ...`.
      - `khaoe_banco_colectivo` fires the same way for pose `SITTING`.
      - **Taterzens has a real, previously-undocumented `/npc edit pose <name>` command** (confirmed
        via the mod's own `PoseCommand.class`, disassembled with `javap` since it wasn't mentioned
        anywhere in this pack's docs before now), backed by vanilla's `EntityPose` enum and persisted
        as `TaterzenNPCTag.Pose` — same NBT nesting convention `heal_skin.mcfunction` already relies on
        for `TaterzenNPCTag.skin.value`. `STANDING` and `SITTING` are both real, valid values; defaults
        to `STANDING` if never set. Not added to README's command cheat-sheet yet — worth doing next
        time that section is touched.
      - The three `khaoe_farlis_*` ambient fragments use Döran's `random_dialog` pattern (equal odds,
        `functions/npcs/khaoe/roll_dialog.mcfunction`, gametime-mod-3 — same reasoning as Döran, see
        that section above) but ONLY fire when the NPC named Farlis is within 5 blocks of Khaoe
        (`if entity @e[name=Farlis,distance=..5]`), checked as the first (highest-priority) branch —
        this only makes sense when both Khaoe and Farlis are actually placed in-world together for the
        scene. This priority (companion-scene overrides the pose-based solo pair when both conditions
        could apply, e.g. she's STANDING AND Farlis is nearby) was picked as the only reasonable
        default given the two conditions can overlap — flag if it should be inverted instead.
      - Wired only on Khaoe's own `spawn.mcfunction` for now — whether right-clicking **Farlis**
        himself should also trigger this same roll (mirroring it with a second `farlis_dialog_roll`
        score) is still open, deferred to whenever `functions/npcs/farlis/spawn.mcfunction` gets built.
- [x] **`_npcs/dialogs/registry.json` registration resolved** — all five dialogs now registered under
      Khaoe's key (she's the one whose `spawn.mcfunction` actually wires the trigger), each with a
      `condition` field describing its actual gate (pose / Farlis-proximity) instead of `null`. See the
      registry's own `_comment` on the `khaoe` entry for the full mechanism summary.
- [ ] Farlis himself still has no `spawn.mcfunction`, `spawn_position`, or `taterzen_uuid` — needs its
      own `/spawn Farlis` pass, which should also settle the open question above (does clicking Farlis
      also roll the ambient scene, or is Khaoe the sole trigger).
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
      `_lore/characters/hearsay.md`). Left unresolved on purpose — see that entry's note before deciding
      whether Khaasan's own eventual `/enact` pass should reconcile it or lean into the contradiction.

## Farlis, Aureobalo, Khaoe, Khaasan & Bardaglis (bar in Salthos Cruzados — Feria del Milenio, opening night)

Five two-NPC scenes from the same evening, enacted via `/enact` 2026-07-30 in Latin American Spanish,
each written short (per the user's explicit "keep it shorter" feedback) rather than exhaustively
covering everything each character's sample would allow.

- [ ] All five scenes below are enacted and recorded (hearsay.md/encodings.json, registry experience
      for every participant) 2026-07-30, but **none are yet converted to a Blabber dialog file**
      (§8 Step 4) — deferred at the user's explicit request this run. Transcripts live in this
      conversation's history until converted: `farlis_aureobalo_bar_salthos_cruzados`,
      `aureobalo_khaasan_bar_salthos_cruzados`, `farlis_khaoe_bar_salthos_cruzados`,
      `khaoe_khaasan_bar_salthos_cruzados`, `farlis_bardaglis_bar_salthos_cruzados`.
- [ ] Two-NPC dialog registration is an open question for all five scenes in this section, same as the
      Nawom & Morkulo precedent: `_npcs/dialogs/registry.json` assumes one dialog per NPC key. Ask the
      user how these should be registered once converted.
- [ ] Khaasan resolved this run (2026-07-30): drew his first `knowledge.education` sample (26%,
      composite — see registry) and the user confirmed he always travels by griffon ("Teletraveller"
      describes the distance he covers, not the means) — folds into the correction now made to
      `hearsay.md`/`encodings.json`'s `khaoe_farlis_esperando_a_khaasan` entry and resolves the open
      question the Khaoe & Farlis section above had left on this exact point.
- [ ] Aureobalo, Khaasan, and Bardaglis all still need `spawn_position`, `taterzen_uuid`, and a
      `spawn.mcfunction` of their own — skins are already set for all three (see registry). Farlis's
      and Khaoe's builds are tracked separately in the Khaoe & Farlis section above.

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

- [x] **Multi-NPC gesture/nod scheduling collision** (found 2026-07-25 building the jump gesture,
      fixed same day): `schedule function <id> <ticks>t replace` is a single global timer *per
      function ID*, not per-entity — every gesture shared one `gesture_clear` timer and every nod
      direction shared one `_2/_3/_4` continuation-beat timer, so a second NPC gesturing/nodding a few
      ticks after a first one would silently overwrite the first one's pending timing. Replaced with a
      per-entity scoreboard countdown for both systems:
        - `luminacion.gest_timer` / `luminacion.nod_timer` (new `dummy` objectives, `load.mcfunction`).
        - Every `gesture_<name>.mcfunction` now does `scoreboard players set @s luminacion.gest_timer
          <duration>` instead of scheduling `gesture_clear`. `tick.mcfunction` calls the new
          `gesture_tick.mcfunction` every tick, which decrements the score for every
          `@e[tag=luminacion.gesture_active]` and runs `gesture_clear.mcfunction` (now simplified to
          act on `@s` alone) only for entities whose score has reached 0.
        - `nod_up_down.mcfunction`/`nod_left_right.mcfunction` now set `luminacion.nod_timer` to `9`
          instead of scheduling `_2`. The new `nod_tick.mcfunction` (also called from `tick.mcfunction`)
          decrements it per-entity and fires each beat at the score matching 3/6/9 ticks elapsed,
          landing beat 4 in the new `nod_up_down_clear.mcfunction`/`nod_left_right_clear.mcfunction`.
          The old `nod_up_down_2/_3/_4.mcfunction` and `nod_left_right_2/_3/_4.mcfunction` files are
          deleted — superseded by this tick+score design, one shared `nod_timer` objective for both
          directions since an NPC is never tagged mid-nod in both at once.
      Each NPC's hold/beat timing is now fully independent of every other NPC's, regardless of how
      many NPCs gesture/nod concurrently or how staggered their start times are. Docstrings across every
      touched `gesture_*`/`nod_*.mcfunction`, the README (Layer 2 gesture dispatch, the "to call a
      gesture" walkthrough, the Jump reference-table row), and `.claude/skills/spawn/SKILL.md` (which
      named the now-deleted nod continuation files) were updated to match.
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
- [x] **Elbow joint (separate forearm bone) — working, landed 2026-07-25.** `right_arm`/`left_arm` are
      each split at the vertical midpoint into a shortened shoulder segment and a nested `submodels`
      child bone (`right_forearm`/`left_forearm`), pivoted at the elbow. First attempt (same day) used
      absolute-frame-style `translate`/`coordinates` numbers for the nested bone and got the rotation
      approach backwards, causing it to render fully detached — see the README "Elbow joint" writeup for
      what was actually wrong and how it was diagnosed (a real Fresh Animations `wolf.jem` — the same
      author this rig already credits — was pulled from GitHub to reverse-engineer the correct nested
      `translate`/`coordinates` scale). Position tracking through the parent's rotation turned out to be
      automatic; only the pivot's local-frame numbers needed calibrating, which took extensive in-game
      trial and error (see README for final values). A small elbow seam remains and is considered
      acceptable — the blocky character style camouflages it. `cross_arms` (CustomModelData 111) is the
      first gesture using it, bending `right_forearm.rx`/`left_forearm.rx` by `torad(-90)`. Not yet wired
      into any other gesture (scratch-head/palms-up could plausibly use it too, unexplored).
- [ ] Forearm sleeve overlay (`right_forearm_sleeve`/`left_forearm_sleeve`) isn't positionally
      calibrated to match the tuned forearm bone — nesting it under `right_sleeve`/`left_sleeve` the
      same way `right_forearm` nests under `right_arm` was tried and reverted, since that bone only
      inherits the shoulder's rotation (not the forearm's own local elbow bend), breaking `cross_arms`'s
      bend for the sleeve layer specifically. Needs either its own copy of `var.gest_rforearmrx` or
      nesting under `right_forearm` instead of `right_sleeve` (untried). See README "Elbow joint".
- [x] Packaged the manual gesture-selection pass as its own skill, `.claude/skills/bake_dialog/SKILL.md`
      (2026-07-25) — callable standalone on any dialog file, or automatically as `/enact`'s new Step 8.
- [x] Ran `bake_dialog` over every remaining non-template dialog (2026-07-25): `nerkeli_hangar_talk`,
      `nuvilo_scholar_at_the_feria`, `gondarfolas_darnis_and_bracco`, all five `khaoe_*` dialogs,
      `sonoros_lost_traveler`, `nawom_morkulo_first_meeting`. Every dialog in the pack now has at
      least one gesture beyond the uniform default nod. The three `khaoe_farlis_*` states that were
      missing an `action` entirely (see the entry above this one, and the "always a nod" question
      that surfaced it) got filled in as part of this same pass rather than left as a separate gap.
      One pre-existing `nod_left_right` in `khaoe_farlis_el_castillo_que_fue.json` (state `f1`) was
      swapped to `gesture_laugh` — the line ("me da risa") was amusement, not disagreement, and the
      user confirmed the swap before it was made. Any *new* dialog from `/enact` still needs this
      pass — it isn't a one-time fix, `/enact` Step 8 runs it going forward.
- [ ] **`gesture_demo_step.mcfunction`'s self-reschedule doesn't work — cause unconfirmed.** Built
      2026-07-25 as a QA tool (`data/luminacion/functions/admin/gesture_demo_all.mcfunction` +
      `gesture_demo_step.mcfunction`) to auto-play every gesture in sequence on the nearest Taterzen,
      3s apart, via each step scheduling the next with `schedule function
      luminacion:admin/gesture_demo_step 60t replace`. In-game testing (real-time watching, confirmed
      not a window-focus-pause artifact) showed only the *first* gesture ever plays automatically —
      diagnosed via `logs/latest.log` and manual isolation: both the per-index `execute if score ...`
      gesture-selection branches AND the `scoreboard players add` counter increment work correctly
      (calling `function luminacion:admin/gesture_demo_step` by hand repeatedly plays the correct next
      gesture each time), but even `/schedule function luminacion:admin/gesture_demo_step 60t replace`
      run standalone in chat — no `execute if score` wrapper at all — silently does nothing. So the bug
      is specifically in `schedule function` not re-firing this function, not in anything upstream of
      it; root cause (self-referential scheduling from within the function it's scheduling? some
      mod interaction — this is a heavily modded Fabric/Forge pack? a `schedule`-specific quirk in this
      environment?) wasn't pinned down before the user chose to stop debugging and use the tool as a
      manual step-by-step trigger instead (`function luminacion:admin/gesture_demo_step`, called
      repeatedly). The two files' own comments still describe the *intended* auto-advancing behavior,
      not this known-broken state — worth fixing those comments if picked back up.

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
      `assets/`, leaving `_lore/`, `_npcs/`, `scripts/`, and the docs out of both.
- [ ] Need a second `pack.mcmeta` for the resource pack (own `pack_format`) — the datapack's existing
      root `pack.mcmeta` can't serve both.
- [ ] Convert existing dialogue files to translation keys via the extractor once it exists (currently
      all six non-template dialogues use literal `text`).

## Lore integration skill (`/integrate`)

- [x] Built 2026-07-25: `.claude/skills/integrate/SKILL.md`, documented in README §0 (Layer 1).
      Three passes — analyse new `_lore/material/` into `context.md`/`encodings.json`/`unknowns.md`;
      audit `data/luminacion/blabber/dialogues/` for missing `hearsay.entries` coverage; check for
      drift between what's referenced elsewhere (registries, sampled knowledge) and what's actually
      recorded in `encodings.json`.
- [ ] Not yet run end-to-end against real material or a real drift case — worth a first live pass
      next time material is added or a periodic audit is due, to confirm the three passes hold up in
      practice rather than just on paper.
- [x] **Stale reference fixed, 2026-08-07.** Pass 2 cited "README §8 Step 5" as the shape a hearsay
      entry should match — that step never existed in README; §8 only ever documented Steps 1–4, and
      the hearsay-recording step lives solely in `/enact`'s own Step 5 (added after the `/enact`/
      `/embody` split, never backported into README's numbering). Fixed to point at `/enact` Step 5
      directly. Same pass, every README.md reference was removed from `integrate/SKILL.md` (and every
      other skill — see the dedicated section near the end of this file) — skills are agent-facing and
      now self-contained; README stays the human-facing doc. Doesn't touch the still-open item above,
      or the schema-evolution issue in the next section — neither was in scope.
- [x] **Two-layer `sources` provenance, built 2026-08-07.** New `scripts/lore/build_source_index.py`
      (mechanical, no model judgment): migrates every `locations`/`concepts`/
      `characters.in_world_or_legendary`/`characters.real_world_authors_and_players` entry's `sources`
      from flat strings to `{"category": "material"/"hearsay"/"tale", "origin": "..."}`, and links every
      `hearsay.entries[].claims[].about`/`tales.entries[].touches` reference that resolves — exactly, or
      via `difflib` fuzzy match (ratio ≥ 0.77, same-category comparisons only) — into the target node's
      `sources` list. A fuzzy link auto-groups (adds the new spelling to `names[]` so it resolves
      directly next time) but is never treated as settled: it also appends an unconfirmed `CONFLICT-NN`
      ("possible same-entity spelling, auto-grouped"), same as every other conflict — `user_resolution`
      stays the user's call. Wired into Pass 3 step 2 above. Applied once to the live `encodings.json`:
      164 sources migrated, 70 new hearsay/tale links, one real spelling-drift bug caught
      (`balahm`→`balham`, `CONFLICT-18`), 7 references honestly left unresolved rather than guessed
      (one missing `locations` entry — `jardin_de_los_parajes` — and four `concept:` references to
      concepts that don't exist yet: `hotel_kholi`, `preservation`, `memory`, `transformation`). Script
      is idempotent (verified via a second dry run). **Does not touch or resolve any part of the
      "Schema evolution" CRITICAL section below** — that's about the top-level category schema itself
      being able to grow; this works entirely inside the four categories that already exist.

## Schema evolution in `encodings.json` and criterion epistemology (CRITICAL, 2026-08-05)

**IMPORTANT ARCHITECTURAL ISSUE:** The current `/integrate` skill and sampling system assume a fixed
schema (`time_systems`, `locations`, `routes`, `characters`, `concepts`, `conflicts`, `hearsay`,
`tales`) that was established on first material analysis. However, the original design intent was for
the lore structure itself to *emerge organically* from material analysis — categories should not be
frozen in place.

This matters because:

1. **Lore extensibility:** If new material introduces genuinely novel organizational structure (e.g.,
   "alien cultures" that don't fit cleanly into existing categories), the current `/integrate` skill
   has no mechanism to recognize this and propose new categories — it just force-fits into the old
   schema.

2. **Criterion epistemology:** Categories in `encodings.json` drive the sampling categories
   (`era_libro`, `era_ensayo`, `hearsay`, etc.) used by `scripts/lore/sample_lore_knowledge.py`, which in
   turn determine the epistemology anchors (`criterion.trusts`/`distrusts`) that characters derive at
   creation. If the schema evolves, the sampling categories would need to evolve alongside it,
   automatically giving new criteria new epistemologies as new source types emerge.

3. **Current limitation:** The sampling script hardcodes paths into `encodings.json` to extract
   categories (e.g., line 83: `for e in data["time_systems"]["ensayo_i_eras"]`). This is rigid —
   it can't discover categories dynamically.

**What needs to change:**

- [x] **`/integrate` Pass 1 detects novel structure, built 2026-08-07.** New Pass 1 step 2: before
      folding anything in, check whether the material's own structure fits an existing category; if
      not, ask (AskUserQuestion) whether to create a new one, and never continue past that point on the
      skill's own judgment. On approval, also propose an `epistemology_group` for `/character` Step
      4d's trusts/distrusts table (join an existing group, or draft a new row) — confirmed by the user,
      never inferred from category size (Step 4d already documents why that approach failed once).
- [x] **`encodings.json` schema can evolve, built 2026-08-07.** New self-describing `_categories` block
      (added by `scripts/lore/add_categories_schema.py`, a one-time migration) lists every category's
      sampling shape: `path` into the JSON, `shape` (`"list"` for the common flat-list-of-entities case,
      plus two special-cased existing shapes — `"grouped_list"` for `characters.named_inhabitants`,
      `"claims"` for `hearsay.entries`), and `epistemology_group`. A new category registers here
      alongside its own top-level data key — no code change needed if it follows the `"list"` shape.
- [x] **Sampling script discovers categories dynamically, built 2026-08-07.** `sample_lore_knowledge.py`'s
      `flatten_pool()` now iterates `encodings.json`'s own `_categories` block and dispatches by
      `shape` via a small `SHAPE_HANDLERS` registry, instead of 15 hardcoded per-path `for` loops.
      Verified byte-for-byte against a pre-migration baseline: identical 367-item pool, same
      `(category, id)` pairs; the only diffs were internal `text` field formatting for list-valued
      fields (`names`, `places`) — from a stringified Python list to a clean joined string, a disclosed
      cleanup, not a behavior change (`text` is never shown to a user, only substring-matched for
      `--mode skewed`).
      **Honest residual limit, not solved and not claimed to be:** this covers the common case (a flat
      list of `{id, ...}` dicts), which is what every category added via material analysis has looked
      like so far. A genuinely novel structural shape (another nested grouping, another claims-like
      pattern) still needs one new function added to `SHAPE_HANDLERS` by hand — the script refuses to
      sample a category whose shape it doesn't recognize rather than silently skipping it, but "zero
      code for any conceivable shape" was never actually achievable without forcing every future
      category into one canonical shape, which would cut against "let structure emerge organically."

This is a prerequisite for the lore system to grow without architectural friction as new materials
accumulate over time.

- [x] **Cold-start bootstrap, built 2026-08-07.** `scripts/lore/bootstrap_lore.py` creates whichever
      of five structural files don't exist yet (`_lore/encodings.json`, `_lore/material/_context.md`,
      `_lore/unknowns.md`, `_lore/characters/hearsay.md`, `_lore/tales/_index.md` +
      `_lore/tales/_authors.md`), each with an empty/generic header and no content pre-filled in —
      `/integrate` Pass 1 proposes every content category the first time real material calls for it,
      the same way the original schema was built by hand before any of this tooling existed.
      `/integrate`, `/enact`, and `/tell` each got a one-line cold-start pointer at this script.
      Surfaced and fixed a real bug while testing it: `build_source_index.py` hardcoded its own
      4-category list via direct dict access and crashed (`KeyError`) on a fresh/partial project
      instead of no-op'ing — fixed by deriving the list from a new `has_sources` flag on each
      `_categories` entry instead. Verified: bootstrap in an isolated scratch dir (creates correctly,
      idempotent), `sample_lore_knowledge.py` and `build_source_index.py` both run cleanly against the
      fresh file with zero crashes, and both re-verified byte-identical against the live repo
      (zero behavior change there).

## `/embody` can't run cold — no scene transcript is ever persisted (landed 2026-08-07)

**Problem:** `/embody`'s own SKILL.md says it "reads the transcript still sitting in context, not a
file" — confirmed by reading it directly, not assumed. Once an `/enact`-only conversation ends, the
actual turn-by-turn dialogue is gone. What survives on disk (`hearsay.entries[].claims`,
`knowledge.experience`) is not a substitute: both are independently-authored, already-mutated
*summaries* of the same scene from two different angles (the world's sampling pool vs. a character's
own bounded memory) — genuinely different consumers, not redundant with each other, but neither one
is, or was ever meant to be, a verbatim record. Step 5 says so outright: "the original unmutated
version is not recorded." This gap is already visible in this file — see the Feria del Milenio bar
scenes entry above ("Transcripts live in this conversation's history until converted").

**Correction from the first pass at this proposal:** scenes must NOT live under `_lore/` — that
directory is for lore (analysis, sampleable knowledge, the character record), and a raw transcript is
none of those; it only exists to feed `/embody`, which is purely Minecraft-facing. It belongs under
`_npcs/`, alongside `templates/`, `npcs/`, `dialogs/`, `actions/`.

**Boundary check (verified, not assumed):** `/enact`'s own frontmatter says it "touches nothing under
`data/luminacion/` or `_npcs/npcs/registry.json`" — specific to those two, not a blanket ban on
anything under `_npcs/`. A new `_npcs/scenes/` staging directory doesn't violate that. README §0's
higher-level architecture blurb is worded more broadly, though ("`/character` and `/enact` only ever
touch `_lore/` and know nothing of Minecraft") — that line will need a one-line carve-out once this is
built, or the boundary language should be tightened to match what the frontmatters actually say.
Bonus effect of moving it out of `_lore/`: the "must wall this off from `sample_lore_knowledge.py`'s
pool" problem (same isolation `_lore/facts/` and `_authors.md` files need) disappears for free — that
script only ever reads `encodings.json`, so a file under `_npcs/` was never at risk of being sampled
to begin with.

**Shipped shape** (built 2026-08-07):

- [x] New `_npcs/scenes/<scene_id>.md` — one file per enacted scene (same id the hearsay entry gets, so
      the two cross-reference trivially — `/enact` Step 4 now passes this id explicitly into
      `record_hearsay.py` rather than letting it auto-generate one, closing that loop by construction),
      holding the raw turn-by-turn transcript verbatim (dialogue only, no action cues — same rule
      `/enact` already followed), plus participants/format/location metadata. Shape documented in
      `_npcs/scenes/_template.md`.
- [x] New `/enact` Step 4, immediately after the scene is played and *before* Step 5's mutation ever
      throws the original away — saves the transcript first. Same "record immediately, don't batch"
      discipline already in place for hearsay/experience, just started one step earlier. Slots into the
      numbering gap left at "Step 4" when dialog-writing moved out to `/embody`.
- [x] `/embody` Step 1 now reads `_npcs/scenes/<scene_id>.md` instead of "the transcript still sitting
      in context" — the actual unlock. `/embody` is now uniformly file-driven, cold or hot, same
      conversation or months later; if invoked cold without a scene already identified, it asks the user
      which one (character name or scene id).
- [x] README §0 got the carve-out this section flagged as needed: the `/character`/`/enact`
      lore-vs-Minecraft boundary line, plus the `/enact`/`/embody` bullets and the §1 folder tree, now
      all describe `_npcs/scenes/` accurately instead of the old "never touches `_npcs/`" claim.
- [ ] **Limitation, can't be fixed retroactively:** any `/enact`-only scene that predates this change
      still has no recoverable transcript — those would need to be re-enacted from scratch to ever be
      embodied. Applies to every dialog-linked hearsay entry already on record as of 2026-08-07 (see the
      `hearsay.entries` list) and to the two not-yet-embodied `#1`-suffixed entries
      (`gok_milkucha_alcove#1`, `farlis_gok_alcove#1`).
- [x] **Open question resolved (user's call, 2026-08-07): keep permanently.** `/embody` never
      deletes/archives a scene file after conversion — cheap to keep, and it's the only recoverable
      source if a dialogue ever needs re-converting after an editing mistake.

## Conflict-resolution skill (landed 2026-08-07)

No skill existed to help work through `encodings.json`'s `conflicts` array. As of 2026-08-05, 14 of
17 entries (all but `CONFLICT-01`/`03`/`05`) had no `user_resolution` — every disagreement `/tell`
and `/integrate` have ever logged is append-only by design: neither is allowed to set
`user_resolution` themselves, that's the one thing only the user can do (see each skill's own docs).
Previously the only way to resolve one was to notice it while reading the file directly.

- [x] **`/resolve`** (`.claude/skills/resolve/SKILL.md`) surfaces one open item at a time — topic, full
      `detail`, and every place elsewhere in the record that mentions it (a plain substring scan of
      every string field in `encodings.json` plus every matching line in `_lore/unknowns.md`, since no
      structured `conflict_ref` field actually exists — the real convention already in use is a
      free-text `"see CONFLICT-NN"` note, e.g. `isla_de_la_amistad`'s `notes` field) — and, only on the
      user's own explicit call, writes `user_resolution` (dated, "per user, <date>", matching the
      existing convention exactly). Never suggests a resolution, never infers one from
      majority-source-agreement or recency, never resolves more than the one item the user is actively
      looking at. Skipping is a first-class, no-op-safe choice — Step 3 stops cleanly and changes
      nothing if the user isn't ready.
- [x] **Two mechanical scripts, same "mechanize the lookup, keep judgement in prose" pattern as
      `check_anchor_reference.py`.** `scripts/lore/resolve_conflict.py` (`--list` / `<id>` /
      `<id> --set-resolution "..."` [`--force`]) — refuses to silently overwrite an existing
      `user_resolution`. `scripts/lore/list_open_unknowns.py` — lists every `_lore/unknowns.md` heading
      whose own title doesn't say "Resolved"/"Correction" (judged per-heading, not inherited from a
      parent section, so the "Follow-up flag" sub-question nested under the resolved 2026-07-24 section
      correctly still shows as open). Both tested against real data (read-only) and, for the write path,
      a scratch copy — refusal-without-`--force`, success-with-`--force`, and unknown-id refusal all
      confirmed before touching the real file.
- [x] **Real bug found and fixed while testing, not part of the original ask:** this machine's Python
      defaults stdout to `cp1252`, which silently mangled every diacritic this pack's lore is full of
      (Milkäan, Iläria, Aerörea...) once piped through a shell expecting UTF-8 — confirmed by round-
      tripping a redirected script's output back through a UTF-8 decode, which raised
      `UnicodeDecodeError` on byte `0xf6`. Both new scripts now call `sys.stdout.reconfigure(encoding=
      "utf-8")` up front. Pre-existing scripts that print accented text (e.g. `check_anchor_reference.py`
      printing a claim's `about` field) likely have the same latent bug — not fixed here, out of scope
      for this pass, but worth the same one-line fix next time one of them is touched.
- [x] **`_lore/unknowns.md` handled too**, per the open question this section originally raised — same
      "only the user decides, never inferred" rule, via `list_open_unknowns.py` plus `/resolve` Step 4's
      prose procedure (append to a dated `## Resolved by the user (<date>)` section matching the file's
      own established convention, plus a one-line pointer left in the original section — never deleted,
      the underlying documentary content stays on record). Unlike conflicts, there's no script that
      writes the resolution here: the file is free-form markdown, and matching its existing prose style
      is a judgement call each time, not a mechanical transform.

## Random character location selection in `/enact` (pinned 2026-08-01)

When setting a scene location in `/enact` Step 1 (or any step that needs to pick a place), if the character's `city` field lists multiple locations or is blank, use weighted location selection rather than the user specifying it outright or picking at random:

1. **Primary locus:** the character's registered `city` (split on commas if multiple are listed) — each listed location gets equal weight within this group.
2. **Secondary locus:** locations where people the character has shared scenes with are based (drawn from `hearsay.entries` — count unique co-participants and look up their `city` fields) — these are offered at lower weight than primary, and only if the user hasn't overridden the location in the scene prompt.
3. **Rationale:** makes the world feel organically connected — characters naturally gravitate toward places they know or toward people they've already met, rather than appearing randomly across the map. Also prevents unnatural isolation: a character who's been to a place twice already and knows someone there has more reason to return than to go somewhere fresh.
4. **Implementation:** proposed as a heuristic for the human running `/enact` rather than a code-level feature. Decision should come up naturally when the user specifies only characters, not a location (e.g., `Farlis and Gok at his station in the Espiral` over-specifies and doesn't need this logic; `Gok runs into Nuvilo` does).
5. **Open:** should the weight favor the character's *most-visited* city over others in their list? And should repeated co-participants (met in multiple scenes) carry more weight than meeting someone once? Current leaning: keep it simple and equal, let narrative preference override via explicit scene prompts.

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

## Feria del Milenio, second day — three scenes enacted 2026-07-31

Dialogs written and fully recorded (hearsay entry, `hearsay.md`, registry experience, Step 5b
resolution, `life.lived`): `khaoe_khaasan_partida_a_khan_ice.json`,
`aureobalo_farlis_castillo_en_miniatura.json`, `bardaglis_ilaria_khaoe_segunda_noche.json`.

- [ ] **None of the three is registered in `_npcs/dialogs/registry.json`** — all are multi-NPC, and
      the registry format assumes one dialog per NPC key. Same unresolved question as the Nawom &
      Morkulo precedent; not guessed. Decide the shape (host under one participant's key? a new
      multi-NPC section?) and apply it to all four at once.
- [ ] **`bardaglis_ilaria_khaoe_segunda_noche` has three speakers**, which `/enact` Step 4 doesn't
      cover — it only specifies the two-NPC case. The `"Name: "` prefix plus single `"..."` choice
      generalises without any change, and the file validates, but the skill should say so explicitly
      rather than leave the next run to infer it.
- [ ] **Spawn work for the six participants** — Khaoe, Khaasan, Farlis, Aureobalo, Bardaglis, Iläria
      all still need movement mode, `spawn_position`, `spawn.mcfunction`, and UUID capture. Iläria
      and Aureobalo also have no `skin`. Because no movement mode is decided, all three new dialogs
      use the bare `{"type": "end_dialogue"}` terminal state with **no `resume_routine` call**,
      matching the `nawom_morkulo_first_meeting` / `nuvilo_nerkeli_feria_del_milenio` precedent. Add
      the resume action to each when the modes are settled.
- [x] **Gestures baked on all three** (2026-08-05) — `khaoe_khaasan_partida_a_khan_ice.json` (6/19
      states), `aureobalo_farlis_castillo_en_miniatura.json` (7/20), and
      `bardaglis_ilaria_khaoe_segunda_noche.json` (7/22). Run as a one-time backlog cleanup when
      `/bake_dialog` was retired in favor of `/embody` baking inline — these three predate that change
      and were originally left uniform on purpose (see the entry below), so nothing skipped them
      silently; they were just never revisited until now.
- [x] **`-nobake` flag added to `/enact`** (2026-07-31, author's request): skips Step 8 only.
      Everything through Step 7 still runs in full — the hearsay record, criterion resolution, and
      `life.lived` are the point of an enactment and aren't Minecraft-facing. Documented in a new
      Flags section at the top of `enact/SKILL.md`, which also states explicitly that it does *not*
      skip Step 4 or Step 5/5b.
- [x] **`bake_dialog` couldn't be invoked from `/enact`'s old Step 8 — resolved, but differently than
      either option this item originally proposed, and then superseded again the same day** (2026-08-05).
      By the time this was revisited, the lore/Minecraft split (`/enact` vs `/embody`) had already moved
      dialog-writing and gesture-baking out of `/enact` entirely — the blocker actually lived in
      `/embody`'s Step 4 (its own handoff to `/bake_dialog`, same `disable-model-invocation: true`
      refusal). First fix: `/embody` Step 3 (formerly Step 4) started inlining the full
      gesture-selection procedure instead of invoking `bake_dialog` via the Skill tool. Then, the same
      day, `.claude/skills/bake_dialog/SKILL.md` was deleted outright — every real dialog in the pack was
      produced by tooling (`/enact`/`/embody` or their pre-split ancestor), none hand-written, so there
      was no longer any dialog-creation path outside `/embody`/`/enact-embody` for a standalone baking
      skill to serve. The 5 pre-existing dialogs still uniform at that point (Auroboro III, Milkucha's
      Jardín de los Parajes, and the three Feria del Milenio second-day scenes — see entries above and
      below) were baked by hand as a one-time backlog cleanup before the skill was removed, so nothing
      was left stranded. Every dialog `/embody`/`/enact-embody` produces now gets baked automatically as
      part of that same run — there is no separate baking step or skill left to invoke.
- [ ] **Khaasan is off-map until further notice** — he left the Feria for Khan Ice to see his uncle,
      carrying an errand for Khaoe (check whether a house near the water still stands). Two threads
      to pay off whenever he next appears: what he found, and Döran's Khan Ice claim, which he went
      to check with his own eyes and which Döran made without ever having been.

## Criterion model — gaps found by using it (2026-07-31)

Surfaced by running the three scenes above; all three are places `/character` Step 6 is
underspecified, not bugs in the data.

- [ ] **The "hardening" rule only fits the *reject* move.** Step 6 says surviving a refutation hardens
      `distrusts` against that kind of source. That's right when a character survives by *dismissing*
      the claim — but when they survive by *accepting and reinterpreting*, hardening against the
      source that just corrected them is backwards. Farlis accepted Khaoe's rebuttal via Aureobalo;
      hardening him against named firsthand testimony would have been wrong, so his trust fields were
      left untouched. Make the rule conditional on the move.
- [ ] **Reaffirmation has no defined outcome.** The gate matched three times this run where the claim
      *confirmed* rather than challenged the anchor (Iläria asked which chronicle is right and
      declined to say; Khaoe's own castle line came up in her presence). The three moves are all
      responses to a refutation, so these were recorded as "no change," which feels right but isn't
      written down anywhere. Decide whether a reaffirmation ever tempers, and say so.
- [ ] **No guidance on how often tempering should fire.** It fired in two of three scenes here, which
      may be too eager for a mechanic meant to make characters gradually rigid. Worth a sentence on
      what does *not* count as a challenge (banter, a friendly restatement) versus what does.

## Pre-existing dialog issues (found 2026-07-31 while validating)

- [ ] **Two shipped dialogs break the 300-character hard cap** that `/enact` Step 4 states as a rule:
      `gondarfolas_darnis_and_bracco.json` (`farewell`, 332) and `nuvilo_scholar_at_the_feria.json`
      (`writes_about_2`, 308). Both predate the rule being enforced. Fix by splitting at a clause
      boundary with a `"..."` connector state, per the same Step 4.

## Criterion / will-to-live system (landed 2026-07-31)

Shipped this round: `_lore/facts/` (the fifth, never-sampled source of truth),
`scripts/lore/roll_lifespan.py`, `criterion`/`life` on the registry `_template`, `/character` Steps 4–7
(derivation, lifespan, and the reference model for how a criterion changes), and `/enact`'s facts
loading, in-scene modulation, and Step 5b shock/drift resolution. Still open:

- [ ] **`/temperament` skill.** The disposition that governs move 2 vs. move 3 when a character
      accepts a refuting claim — rebuild the meaning, or let the criterion go. Deferred by the user
      on 2026-07-31; until it exists, `/character` Step 6 says to decide on provenance, proximity,
      and susceptibility alone and bias toward reinterpretation. Should be set at creation from the
      backstory and drift slowly with `knowledge.experience` (the working split: knowledge changes
      your criterion, experience changes your temperament).
- [ ] **Inherited criteria (city/trade fallback).** `/character` Step 4e currently leaves
      `criterion` blank with `"origin": "uncollided"` when nothing in the sample touches the
      backstory or city, because the fallback implies giving every city (and trade) its own ambient
      criterion. Pinned by the user on 2026-07-31. Worth building — it's what produces shared
      culture rather than a hundred idiosyncratic philosophies, and it's the common case for
      ordinary people, who inherit their town's answer rather than authoring one.
- [ ] **No `/fact` skill.** Adding a fact means hand-editing `_lore/facts/facts.json`, a new `.md`,
      and the `_index.md` table. Fine for now given how rarely facts should be added, but the other
      sources of truth all have skills (`/integrate` for material/analysis, `/tell` for tale).
- [x] **Backfilled 2026-07-31:** Bardaglis, Farlis, Khaoe, Khaasan, Aureobalo, Döran, and Iläria all
      have a derived criterion (with anchor, `trusts`/`distrusts`, and a seeded `cost_ledger` drawn
      from what their recorded history already cost them) and a rolled lifespan. `life.lived` was
      backfilled from the hearsay record — one `hearsay.entries[]` record is one scene — per the new
      rule in `/character` Step 5.
- [ ] **Still without a criterion or lifespan:** Gondarfolas, Nuvilo, Nerkeli, Nawom, and Morkulo
      (drawn samples, so derivable now), plus the ~50 entries whose `knowledge.education.percent` is
      still `null` — those can't be derived at all until they have both a backstory and a sample.
      Let it happen lazily as each next comes up in an `/enact` run, or batch them like the seven
      above.
- [ ] **Lifespan range set to 30–60** (author decision, 2026-07-31, replacing the initial 4–14) and
      written into `scripts/lore/roll_lifespan.py`'s defaults. Nobody is anywhere near their span yet —
      the most-lived character, Khaoe, is 7 scenes into 51 — so the endgame path in `/enact` Step 5b
      is written but has never actually fired. Worth testing deliberately with a throwaway character
      on `--min 2 --max 4` rather than waiting for it.
- [x] **Death notification, landed 2026-08-01.** `scripts/lore/notify_death.py` computes a dying
      character's "circle" (scene co-participants + everyone named in their own backstory) and
      mechanically samples 30% of it (min 1) to notify immediately via a forced
      `knowledge.experience` entry; it also flags which notified characters have a `criterion.anchor`
      referencing the deceased, so `/enact` Step 5b point 6 can resolve that as a shock through the
      existing reject/reinterpret/break machinery. Everyone else only learns later, the ordinary way
      — the death is recorded as a `_lore/tales/` entry (same shape `/tell` produces,
      `told_by: null` unless a cause was established in the closing scene) and re-enters the
      normal sampling pool. `life.deceased` (plain, non-secret bool) added to the registry `life`
      object and to every already-touched character (`false`); Step 1 now refuses to re-enact anyone
      with `deceased: true`. Tested against real data: `notify_death.py khaoe`/`bardaglis` correctly
      compute their circles, and the shock flag was confirmed to fire (seed 9 on `khaoe` selects
      Khaasan, whose anchor is `experience: khaoe_khaasan_bar_salthos_cruzados` — Khaoe is a
      participant in that scene, so it flags).
- [ ] **Still open: what a dead character's *NPC* does in-game.** Nothing yet stops a *spawned*
      Taterzen from standing in the world with a working right-click dialog after `life.deceased`
      flips true — this is the Minecraft-facing half the notification mechanism deliberately doesn't
      touch. Decide: despawn, stay as a silent fixture, or get replaced by someone retelling them.
- [ ] **Not yet exercised on a real death.** No character is anywhere near their span (see the
      lifespan entry below), so `notify_death.py` has only been tested by hypothetically running it
      against living characters, never through an actual `/enact` Step 5b point 6 closing-out. Worth
      running the short-lifespan test suggested below specifically to watch the full death procedure
      fire end to end, including the tale-record write and a real shock resolution.
- [ ] **`python` on PATH is the Microsoft Store stub** on this machine, and the repo's `.venv/` is a
      dead Codespace artifact (`.venv/bin/python` points at `/home/codespace/...`). `py -3` works.
      Either fix the venv, or update the `python scripts/...` invocations in README §5 and the
      skills to `py -3`.

## Skills decoupled from README + shared house philosophy + `/simulate` scripting (2026-08-07)

Skills are agent-facing; README is human-facing. Every skill previously cited README.md for rules or
procedure it either already restated (redundant) or, in one case, misquoted (see the `/integrate`
entry above). Cleaned up in one pass:

- [x] **Every README.md reference removed from every skill** (`enact`, `embody`, `spawn`, `package`,
      `integrate`, `tell`; `character`/`simulate`/`enact-embody` had none to begin with). Skills no
      longer read or cite README at all. The one line left (`package/SKILL.md` listing `README.md` as
      a filename excluded from the release zip) isn't a documentation dependency, so it stayed.
- [x] **`.claude/PRINCIPLES.md` created** — the "nothing gets decided silently" rule, previously
      restated in slightly different words in six places (`enact`, `embody`, `spawn`, `integrate`,
      `tell`, `character`), now stated once. Each of those six skills points at it with one line and
      keeps only its own domain-specific application (what counts as an open question there, and
      where it gets logged). README §0 Layer 1 now points at it too, for a human reader.
- [x] **Three new scripts wired into `/simulate`**, replacing prose-only steps with the same
      "mechanize the mechanical part, keep the judgment calls in prose" pattern already used for
      `update_character.py`/`record_hearsay.py`/etc.:
      - `scripts/lore/simulate_setup_worktree.py` — collapses Step 2's worktree-create +
        settings-bypass-write into one call, in the exact order previously spelled out (and easy to
        get wrong) across three separate prose steps.
      - `scripts/lore/pick_pair.py` — a genuine `random.sample()` draw for Step 3's pass pairing,
        replacing the model's own "pick randomly" (LLMs are demonstrably non-uniform at this).
      - `scripts/lore/simulate_tally.py` (`snapshot` + `report`) — Step 4's closing tally (deaths,
        criterion moves, final `life.lived`) computed from a before/after diff of the character
        files, instead of hand-counted from up to N pass summaries.
      Tested: `pick_pair.py`'s draw and its too-small-pool error path; `simulate_tally.py`'s
      snapshot→report round trip against real (unmodified) character files, confirmed zero false
      positives. `simulate_setup_worktree.py` is compile-checked only, not run live, since it creates
      a real git worktree + branch — first actual `/simulate` run will exercise it for real.

**Not in scope, still open:** the `/integrate` end-to-end test and the schema-evolution architectural
issue, both under "Lore integration skill (`/integrate`)" above, are unrelated to this pass — neither
was touched.

## Model-agnosticism plan (drafted 2026-08-07, paused — resume when the user is back)

Goal: use this pack with Claude, but also other model providers — commercial and open-source/local.
Researched rather than assumed (web search, not memory) before drafting. Two separate axes, easy to
conflate:

- **Axis A — same harness (Claude Code), different model underneath.** Free: Claude Code always
  offers the same tools (Bash, Read, AskUserQuestion, EnterWorktree, Agent, ...) to whatever model
  answers the API calls; swapping the model doesn't change what tools exist, only whether that model
  calls them well. Ollama v0.14+ ships a *native* Anthropic Messages API endpoint — point Claude Code
  at it via `ANTHROPIC_BASE_URL`, no proxy, no skill changes. Other commercial providers (OpenAI,
  Gemini, ...) aren't Anthropic-API-native, but a LiteLLM proxy translates, same env-var trick pointed
  at the proxy instead.
- **Axis B — leave Claude Code for a different harness** (Cursor, Gemini CLI, Codex CLI, OpenHands,
  Aider, ...). Real work, but less than expected: the `SKILL.md` format itself (folder + frontmatter +
  markdown body) is now an **open standard** (agentskills.io, donated to the Linux Foundation's
  Agentic AI Foundation, Dec 2025), natively supported by 30+ tools including Cursor, Gemini CLI,
  Codex, VS Code, GitHub Copilot, OpenHands, Goose, Roo Code. Our `.claude/skills/*/SKILL.md` files
  already sit in the right shape — no structural migration needed. What's *not* standardized: the
  Claude Code-specific tool names our skill prose calls out directly (`AskUserQuestion`,
  `EnterWorktree`, the `Agent` subagent dispatcher, `TaskCreate`) and the `.claude/settings.json`
  permission-bypass mechanism `/simulate` depends on — no equivalent on most other harnesses.

**User decision (2026-08-07): pursue Axis A first**, see how far it gets before committing to Axis B.

- [x] **Environment prepped for Axis A, 2026-08-07.** Ollama server confirmed running (v0.17.1, past
      the 0.14 threshold). `qwen2.5-coder:14b` pulled (~9 GB) — the top-rated local coding model for a
      12 GB VRAM card (RTX 4070 Super), chosen for tool-calling/agentic reliability over the two
      models already present (`mistral:latest`, `llama3.2:1b` — neither well-suited to this use case).
- [x] **Phase 0 smoke test run, 2026-08-08 — negative result, three distinct failure modes.** Not a
      config problem; a real result. Tested two models across two proxy paths, low-stakes prompts only
      (`.claude/PRINCIPLES.md` read, "what is an apple", no full skill run):
      1. `qwen2.5-coder:14b` via Ollama's native Anthropic-compat endpoint (`ANTHROPIC_BASE_URL` →
         `http://localhost:11434`) — hallucinated fake tool calls on *every* message, including ones
         needing no tool at all (`{"name": "GetModel", "arguments": {}}`,
         `{"name": "Read", "arguments": {"file_path": "/path/to/..."}}` on placeholder paths).
         Confirmed as a known, documented issue: this model's tool calls come back as raw JSON text in
         the response content instead of a structured `tool_calls` block, so Claude Code just prints
         the JSON as if it were the answer rather than executing anything.
      2. `qwen3:8b` via the same Ollama endpoint — stopped hallucinating fake tools, but *under*-triggers
         real ones (asked "what does PRINCIPLES.md say" → claimed it can't access local files at all,
         rather than calling `Read`). When explicitly told to use `Read`, it did — then hit a genuine,
         currently-open Ollama bug (`API Error: Content block not found`, a multi-turn tool-result
         serialization issue, confirmed against a live `ollama/ollama` GitHub issue), and in response to
         *that* error, fabricated an unrelated file as a guessed "fix" and falsely reported the original
         task complete. (Correction: it did ask permission before writing that file — not a silent
         bypass, just an irrelevant, hallucinated action it then lied about the purpose of.)
      3. `qwen3:8b` again, this time via a local LiteLLM proxy (`litellm[proxy]`, config mapping
         `qwen3-8b` → `ollama_chat/qwen3:8b` on port 4000) instead of Ollama's native endpoint — fixed
         the protocol bug (`Read` succeeded cleanly this time) but surfaced two more problems: an
         unprompted, unrelated file write (`example.json`, `{"key": "value"}`) with *no* error to react
         to this time (ruling out "error-driven confabulation" as the explanation — it's a standing
         habit, not error recovery), and then, worse, within the *same conversation*, right after
         successfully using `Read`, it lost all awareness of having file tools at all — denied having
         read the file, asked for an absolute path as if `Read` didn't exist, then flatly claimed it
         "cannot access local files," in three consecutive turns.
      Setup notes for reproducing: `py -m pip install "litellm[proxy]"`; the `litellm` console script
      isn't `python -m`-invokable (no `__main__.py`) — call the installed `.exe` directly, or add
      Python's `Scripts/` dir to PATH. Hit two unrelated environment snags getting it running at all:
      an `ImportError: cannot import name 'get_flat_dependant'` from a too-new `fastapi` (fixed by
      pinning `fastapi==0.115.6`, which in turn downgrades `starlette` below what the locally-installed
      `mcp`/`sse-starlette` packages want — a real, currently-unresolved conflict, just not one that
      broke anything used this session) and a `UnicodeEncodeError` on litellm's own startup banner
      under Windows' default `cp1252` console encoding (fixed with `PYTHONUTF8=1`).
      **Conclusion:** not "wrong model, try another" — three qualitatively different failure modes
      across two models and two proxy paths point at the same root cause: Claude Code's harness (system
      prompt, exact tool schemas, Anthropic Messages API conventions) is shaped around Claude
      specifically, and an 8–14B local model doesn't reliably hold together inside a harness built for a
      different model, even once the API plumbing technically works. Bigger local models (32B+) or an
      agentic-tool-calling-specific fine-tune might fare better, but that's a deliberate hardware/time
      investment, not a quick next swap.
- [ ] **Pivot (2026-08-08, user's own reframe): stop trying to make local models impersonate Claude
      inside Claude Code, and instead pursue Axis B properly** — a harness that's model-agnostic *by
      design* rather than via an Anthropic-API emulation shim. This was always going to be needed for
      other commercial harnesses too, so it isn't wasted work either way. Two concrete candidates,
      researched but not yet tried:
      - **Goose** (Block, open source) — natively lists every installed Ollama model in its own model
        picker (`GOOSE_PROVIDER=ollama`, `OLLAMA_HOST`), no translation shim needed for the local case;
        confirmed Agent Skills support; built on MCP for tools specifically (an open standard, not a
        bespoke harness-specific tool set) — architecturally the closer fit to "generic skills, no
        vendor-specific API." Windows-supported.
      - **OpenHands** — explicitly branded "model-agnostic," routes through LiteLLM for provider choice
        (OpenAI, Anthropic, Ollama, vLLM, ...), confirmed Agent Skills support
        (`docs.openhands.dev/overview/skills`). More established specifically for local-model agentic
        coding; docs recommend a much larger local model (Qwen3.6-35B-A3B) as the first one to try,
        likely too big for 12 GB VRAM comfortably — would need a smaller Qwen3 variant instead.
      Why either should sidestep this session's specific bugs: neither asks the model to speak
      Anthropic's Messages API tool-use format at all — they talk to Ollama via its OpenAI-compatible
      tool-calling path, which has existed since mid-2024 and is far more battle-tested than Ollama's
      ~7-month-old Anthropic-compat endpoint that produced failure modes 1 and 3 above.
      **Decided (2026-08-09): OpenHands.** Chosen over Goose specifically on scalability — Goose
      hard-caps concurrent subagents at 10 with no recursive spawning and a 5-minute/25-turn default
      ceiling per subagent, while OpenHands isolates each task in its own Docker/Kubernetes container
      with no equivalent hard cap, has a headless REST-API mode built for CI/batch use, and an optional
      managed-cloud path if local scale ever isn't enough — the better long-term fit for something
      shaped like `/simulate` (many isolated, potentially parallel passes) even though Goose would have
      been the faster thing to stand up tonight.

### Repo restructuring plan (2026-08-09, planned — NOT YET IMPLEMENTED, do next session)

**The problem with the first draft of this plan:** it pointed OpenHands at `.claude/skills/` (via a
junction) and left `.claude/PRINCIPLES.md` as the canonical philosophy file — which still made the
*project* depend on a `.claude/`-shaped structure, just with another harness bolted on. Correctly
called out by the user: model-agnosticism means the reverse — `.claude/` should hold only what Claude
Code itself hard-pins to that exact path, nothing else, and the project's real content should live
somewhere no single vendor's product name is attached to.

**Corrected target structure:**

```
AGENTS.md              canonical, harness-neutral orientation doc — replaces .claude/PRINCIPLES.md's
                        role (the "nothing decided silently" rule) plus README §0's architecture
                        overview, rewritten for an agent audience. The real cross-tool standard for
                        this role (natively read by Codex/Cursor/Gemini CLI/Windsurf/Aider/15+ others,
                        60,000+ repos on it already).
CLAUDE.md               thin — just imports AGENTS.md (Claude Code doesn't read AGENTS.md natively as
                        of mid-2026, per its own docs).
.agents/
  skills/                canonical home for all 10 skill folders (moved from .claude/skills/ via
                          `git mv`, preserving history) — the actual Agent Skills open-standard
                          location, and OpenHands' own default lookup path, so it needs zero
                          skills-related config on OpenHands' side once files live here for real.
  harness/
    openhands/
      launch.ps1          sets LLM_MODEL/LLM_BASE_URL/LLM_API_KEY env vars + `--override-with-envs`
                          (required — OpenHands silently ignores those env vars without this flag and
                          falls back to the user's global `~/.openhands/settings.json`, which isn't
                          repo-portable), then runs `openhands serve --mount-cwd`. Action-approval
                          stays interactive by default (matching how the main repo's own
                          `.claude/settings.json` behaves today — no bypass); a bypass
                          (`--always-approve`, or `--headless --exit-without-confirmation` for full
                          unattended automation) is an opt-in flag on the script, not the default —
                          same split `/simulate`'s worktree already draws between normal sessions and
                          batch runs, deliberately kept consistent rather than inventing a new rule.
.claude/
  settings.json           stays — genuinely Claude-only, no cross-tool equivalent exists, and it's
                          already repo-committable so Claude Code needs nothing else.
  settings.local.json     stays, same reason.
  skills/                  → directory junction to ../.agents/skills (same proven pattern as this
                          repo's existing `resourcepack/` ↔ `resourcepacks/luminacion/` junction, see
                          README Layer 4) — exists only because Claude Code hardcodes this exact path
                          and can't be told to look elsewhere. Zero real content stored under `.claude/`
                          once this is done.
README.md                unchanged — still the human tutorial, untouched by any of this.
```

**Steps, in order:**
1. `git mv` all 10 skill folders from `.claude/skills/` → `.agents/skills/`.
2. Write `AGENTS.md` at repo root (content sourced from `.claude/PRINCIPLES.md` + README §0).
3. Delete `.claude/PRINCIPLES.md`; update the 6 skills that currently point at it (`enact`, `embody`,
   `spawn`, `integrate`, `tell`, `character`) to point at `AGENTS.md` instead.
4. Write thin `CLAUDE.md` that imports `AGENTS.md`.
5. Create the `.claude\skills` → `..\.agents\skills` junction (`mklink /J`, no admin/Developer Mode
   needed for a directory junction on Windows, unlike a symlink).
6. Fix any other live references to `.claude/skills/` across the repo (README, scripts) —
   `TODO.md`'s own historical entries stay untouched; they're a changelog of what was true when
   written, not living documentation.
7. Write `.agents/harness/openhands/launch.ps1` per the spec above.
8. Install OpenHands (`py -3.12 -m pip install openhands-ai`, sidestepping the machine's default
   Python 3.14 that caused the fastapi/litellm conflict earlier this session) and run the launch
   script from inside the repo.
9. Smoke test: start a fresh OpenHands conversation (required so it rebuilds its skills catalog),
   confirm it lists the skills correctly, then repeat the same low-stakes checks from the Ollama/Claude
   Code round — read `.claude/PRINCIPLES.md` → `AGENTS.md` once moved, then `/tell` — watching
   specifically for whether OpenHands' harness avoids the three failure modes logged above (fake tool
   calls, unprompted irrelevant writes, mid-conversation tool amnesia), since the whole premise of
   switching harnesses is that those were Claude-shaped-harness problems, not Qwen problems.
- [ ] **Cosmetic, low priority:** every skill's `disable-model-invocation: true` frontmatter field is
      a Claude Code extension, not part of the core Agent Skills spec (confirmed against
      agentskills.io/specification — core fields are `name`, `description`, `license`, `compatibility`,
      `metadata`, `allowed-tools`). Likely harmless (unrecognized YAML keys are typically just ignored)
      but a strict validator on another client could flag it. Not worth fixing unless it actually
      breaks something on a real Axis B test.

## Synthesis mechanism — characters forming their own theories (proposed, pinned 2026-08-07)

**Built 2026-08-08.** Design pass, decision pass, spec (`.claude/skills/enact/SKILL.md` Step 5c),
`scripts/lore/check_resonance.py`, and `update_character.py --add-synthesis` are all done — see Step 5c
in `SKILL.md` for the calling convention. Not yet exercised on a real `/enact` run; the mechanical
pre-filter only matches against `knowledge.education.items` (structured `about`-style refs), not
`knowledge.experience`/`backstory` prose, so its candidate recall on a character-heavy scene is
untested until it's actually used. Answers a real gap identified while discussing the "Knowledge
mutation system" section near the
top of this file and the "Schema evolution in `encodings.json`" work done this session: everything
currently in `/enact` — mutation at record time, the criterion shock/reject/reinterpret/break
machinery — reinterprets or resolves *one* input at a time. Nothing currently lets a character combine two things they know into a third belief that isn't
reducible to either parent. The goal: a character can form their own theory about the world (or about
themselves, or about someone else) from what they already knew plus what they just heard, gated so that
this stays rare and meaningful rather than firing on every scene.

**Where it runs:** a new `/enact` step, proposed as Step 5c, immediately after Step 5b's shock
resolution (same "reflect on what this scene did" position, same "default is no change and that will be
the answer almost every time" discipline the shock gate already uses).

**Core shape, agreed so far:** synthesis only considers pairs where one side is something the character
heard/lived *this scene* and the other is already in their standing knowledge (education sample or
prior experience) — never a full sweep of a character's whole life, never two things both freshly heard
in the same breath. A cheap mechanical pre-filter narrows candidates (varies by subtype, see below);
the model then judges, per candidate, whether the pairing actually raises something neither claim states
alone (a gap or tension, not agreement/restatement) — most candidates should produce nothing. Whatever
does synthesize gets written to `knowledge.experience` as `{"kind": "synthesis", "about": [A, B],
"derived_from": [A, B], "text": "..."}` (extending the existing "about can be a list" convention, not a
new field shape) — private knowledge unless the character actually voices it in a later scene, at which
point it becomes an ordinary hearsay claim through the existing recording path, no new sampling-pool
machinery needed. **Credibility inheritance rule:** the synthesized claim inherits the *weaker* of its
two parents' credibility — a synthesis built on a shaky/uncorroborated parent comes out hedged ("maybe,"
"it makes me think"), not asserted, reusing the existing `oral_lore`/traceable ledger rather than
inventing a new certainty scale.

**Subtypes identified so far, each with a different resonance signal — not an exhaustive taxonomy, more
should surface once this is actually tried:**

1. **Causal/narrative.** Two things that already share an `about`/entity reference combine into a new
   claim about meaning, motive, or cause. Worked example discussed: Nerkeli has flown M7 (→ Nvhi) for
   years without ever really seeing the place (his own established backstory); Nuvilo's family claims
   descent from Navalius, Nvhi's founder (freshly heard, uncorroborated). Synthesis: "If M7 always ends
   where Nuvilo's family says they're from, then all these years turning around at the airstrip, I've
   been skipping past the one place that might matter most to him." Mechanical pre-filter: shared
   `about` id (reuse `check_anchor_reference.py`'s matching logic).

2. **Identity/coreference.** Two *differently-named* things share a distinctive (not generic) detail,
   suggesting they might be the same referent. Worked example discussed: a character knows "Sit Nalta"
   has a hot-air-balloon port; a traveler mentions "Sit:Nalta" and its hot-air balloons. Synthesis:
   these may be the same place. Notably, this exact ambiguity is *already* logged as `CONFLICT-07` in
   the objective record — a character reaching this independently, from inside their own bounded
   sample, would be rediscovering a real structural ambiguity without ever having read `conflicts`.
   Proposed check: when an identity-type synthesis fires, look it up against `conflicts` — a match is a
   good, coherent "the character caught something real" outcome worth noting as such; no match is a
   riskier, unbacked guess, held more tentatively (possibly worth its own `unknowns.md` entry if it
   resonates with the corpus, per the same "not every claim produces one" discipline `/enact` Step 5
   already uses). Mechanical pre-filter: name-string similarity (the same `difflib` fuzzy-match already
   built for `build_source_index.py`) plus shared distinctive descriptive content — the distinctiveness
   call (hot-air balloons vs. "has a market") stays a model judgment, not scriptable.

3. **Conflict-explanation** (brainstormed, not yet discussed with the user in depth). A character
   encounters two items that are *already* flagged as disagreeing in the objective record (share a
   `CONFLICT-NN` tag) and invents a personal reconciling story for *why* the disagreement exists —
   without ever officially resolving it; `user_resolution` stays the user's call alone, same as every
   other conflict. Sketch: a character who's sampled both chronicles' conflicting start-years for Era
   del Daax might theorize "maybe one book counts from when the códigos were invented, the other from
   when the government fell — two starting lines for the same age" (Döran's own claim #8 already
   brushes right up against this without taking the last step). Mechanical pre-filter: shared
   `CONFLICT-NN` tag between two known items.

4. **Pattern/generalization.** Not a pairwise collision at all — noticing the *same* thing recurring
   three or more times across a character's own sample and abstracting it into a general belief or
   proverb, not a claim about one specific referent. Sketch: a character who's sampled several
   highway/train segments that all terminate at Nvhi might conclude "seems like every road in this
   world eventually leads to Nvhi." Mechanical pre-filter: frequency (an entity/theme appearing 3+
   times across the sample), not a pairwise `about` match — structurally different from the other four.
   **Decided 2026-08-08: the occurrence that crosses the 3+ threshold must be fresh from the scene that
   just concluded** — the prior N-1 occurrences are already standing knowledge, and generalization only
   fires because *this* scene supplied the tipping instance. Keeps it consistent with every other
   subtype's "something new happened" gating rather than letting a character generalize from pure
   reflection with nothing new. (Like all of Step 5c, this check runs once, post-scene, at record time —
   not live during the scene itself.)

5. **Relational/motive.** Same causal mechanic as (1), but pointed at a *person's*
   motive or history — including the character's own backstory — rather than a place's meaning. Sketch:
   Khaoe's registered backstory already says her family came from Khan Ice before Khol Moshin; if she
   later samples Döran's claim that Khan Icé served as a wartime refuge, she could theorize "maybe
   that's why my family left — the war, not just wanting somewhere new." Mechanical pre-filter: both
   items concern the same person (self or a named third party), not a place.

**Open questions:**

- ~~Should the criterion (`trusts`/`distrusts`) color the *flavor* of a synthesis when one exists (skeptic
  vs. connective framing), or only gate whether it fires at all?~~ **Decided 2026-08-08: both.** Criterion
  affects whether synthesis fires at all (e.g. skeptics synthesize less readily) *and* colors the
  tone/framing of the resulting claim when it does fire. A character with no derived criterion yet
  (several still don't, see the "Criterion / will-to-live system" section above) can presumably still
  synthesize plainly, same as the trust table's ambiguous bottom row.
- ~~Is one synthesis per scene the right cap, or should it scale with how many genuine candidates survive
  the resonance gate?~~ **Decided 2026-08-08: no cap.** Every candidate that survives the mechanical
  pre-filter *and* the model's gap/tension judgment gets written, however many that is in a given scene.
  No tie-break needed since nothing competes for a single slot.
- ~~Subtypes 3–5 are brainstormed, not yet worked through with a concrete example the way 1–2 were.~~
  **Resolved 2026-08-08:** subtypes 3 and 5 already had worked examples and mechanical pre-filters at the
  same depth as 1–2 on inspection — no further pass needed. Subtype 4 was the actual gap (see its own
  entry above for the resolution: this-scene trigger required, evaluated post-scene at record time).
- ~~Whether this needs its own mechanical script (a `check_resonance.py` mirroring
  `check_anchor_reference.py`'s shape) per subtype, or one script with a subtype parameter.~~ **Decided
  2026-08-08: one script, subtype parameter.** The five detection mechanisms differ enough to need
  separate internal logic branches, but share one entry point rather than duplicating I/O/CLI scaffolding
  across five files.
- [ ] **Does a synthesis ever reach `encodings.json`, and by what mechanism?** The spec above says a
  synthesis is "private knowledge unless the character actually voices it in a later scene, at which
  point it becomes an ordinary hearsay claim through the existing recording path, no new sampling-pool
  machinery needed" — but that claim hasn't been checked against how a hearsay claim actually gets folded
  into `encodings.json` (vs. just `hearsay.md`/the character's own `knowledge.experience`). Worth
  confirming, once Step 5c has actually fired at least once and been voiced in a follow-up scene: does
  `record_hearsay.py`/`/enact` Step 5's existing path really carry a `"kind": "synthesis"` claim all the
  way into the world's sampleable pool the same way any other hearsay claim does, or does something
  synthesis-specific (the `derived_from`/`about`-list shape, the inherited-credibility hedging) get lost
  or need special-casing along the way? Unverified either direction — flagged here so it isn't assumed
  either way before a real run tests it.

### /simulate debrief and next-phase design: materiality, arcs, and emergence (2026-08-10, planned — design only, NOT YET IMPLEMENTED)

**See `LAB_REPORT.md` (repo root) for the persistent, cross-run assessment log this debrief seeded** —
run-by-run findings against the standing objective, plus open design questions carried forward across
sessions. This section is the original design writeup; that file is where it gets tested and revised.

**Debrief context.** The 50-pass `/simulate` run (2026-08-08/09/10, worktree `simulate-20260808-181023`,
full record in that worktree's `SIMULATION_LOG.md`) worked exactly as designed mechanically — 25
criterion moves, 20 syntheses, hearsay mutation and record-keeping all correct, several real machinery
bugs found and permanently fixed in the skill itself — but the *content* converged heavily on
epistemological discussion (whose account to trust, contradiction-preservation) instead of producing
dramatic emergence. Diagnosed three independent, compounding, structural sources — none a bug in what
was built, all properties of what the tool currently *is*:

1. 3 of the 5 participants (Auroboro III, Ilária, Khaoe) walked in with epistemically-anchored criteria
   from *before* this run — traceable to backstory (Ilária's backstory literally is "wrote one of the
   two contradictory chronicles"), not to anything this run did.
2. `/enact` Step 3's `trusts`/`distrusts` field is explicitly named as the skill's privileged dramatic
   payoff ("nearly invisible until two sources actually disagree in the scene — that's the moment it
   shows"), which structurally channels *every* scene toward epistemic conflict regardless of what a
   character's `standard` is actually about (even Nerkeli's action-flavored standard — "reach places,
   don't just study maps" — got phrased as a *verification*, i.e. epistemic, distrust once run through
   this mechanism).
3. Any future "shared knowledge between two characters" topic-selector would *also* skew epistemic, for
   a third, unrelated reason: checked directly against `encodings.json`, `concepts` (19 entries) and
   `conflicts` (18) are roughly a third the size of `locations` (58) and `named_inhabitants` (69) — so
   two independently-sampled characters are mechanically far more likely to coincidentally share a
   concept or conflict than a specific person or place, purely from smaller-pool collision odds.

**Conclusion:** the tool renders its designed objective correctly — lore evolves, criteria shift, hearsay
mutates, exactly as specified. The underwhelming *drama* isn't a flaw in that design; it's that
everything so far runs on one substrate only (language), with no material consequence, no scarcity, no
clock outside `life.span` (which never fired once in 50 passes), and a content-generation step
(`trusts`/`distrusts`) that was only ever meant to modulate a reaction, not generate a topic.

**Proposed next phase**, worked out collaboratively in the debrief conversation following the run:

1. **Routines as authored archetypes.** Each character gets a small, handcrafted set of home routines —
   a location tied to a role ("works the market," "keeps the workshop in Khan Icé"). The routine *is*
   the archetype: "market" already implies buying, selling, price disputes, scarcity, trust in a trading
   partner — texture for free, without authoring a project per character. Author-placed, not generated,
   same discipline as everything else in this system that's a premise rather than painted detail.
2. **Cycling.** Each pass, a simple mechanical rule (fixed rotation, or an authored skew toward one
   routine) decides which of a character's routines they're currently in. Deliberately not meaningful on
   its own — just needs to run.
3. **Pairing stays exactly as-is** — `pick_pair.py`, unchanged, still a uniform random draw across the
   living pool. No new selection layer; letting a model choose who to visit would just reintroduce the
   same salience bias `pick_pair.py` already exists to prevent.
4. **Location resolves mechanically after the draw:** compare both participants' current routine. Same →
   coincidence (scene happens there, whichever one's "home" it narratively is decided by a coin flip —
   unplanned, ordinary, no criterion or motive required). Different → visit (scene happens at
   participant_2's home; participant_1 traveled). Verified `pick_pair.py`'s `random.sample()` carries no
   positional bias, so the traveler/host role averages out fairly over a long run — no extra fairness
   logic needed.
5. **Group scenes fall out of coincidence for free.** When 2+ participants share a location, check every
   *other* living character's current routine against that spot; each match gets an independent
   dice-roll chance to join. Keeps group scenes rare by construction; the roll probability should get
   tuned down as population grows (see reproduction below), or group scenes stop being rare as the cast
   grows.
6. **Arcs, derived from the routine's archetype, not a separate collision-derivation step.** Authored
   once per place-type (the market archetype, the workshop archetype), not per character. An arc carries
   real progressive state — a "last thing done" that every scene touching that routine advances. This is
   genuinely material: an evolving fact, not a corpus-drawn category (so it doesn't inherit the
   small-pool bias in point 3) and not free model invention (so it doesn't inherit the salience bias
   `pick_pair.py` was built to avoid).
7. **Scene content candidate — proposed, not decided:** anchor each scene on the host's (or shared, in a
   coincidence) "last thing done." The visitor walks into a concrete, already-determined material fact,
   and brings their own last-thing-done into it. `trusts`/`distrusts` still applies, but only to *how*
   each character reacts to what's actually there — it stops being asked to generate the topic too.
   **Unresolved:** how a reaction is supposed to fold back into becoming the arc's *next* "last thing
   done" — flagged in the debrief, not solved.
8. **Reproduction (autopoiesis — self-*re*production).** Rare, selected event, not automatic once a
   threshold (e.g. a minimum shared-conversation count, cheap to check since hearsay entries already
   record participants) is crossed — mirrors how death is gated by `horizon.py`'s own logic, not
   automatic either. **Open: what triggers the birth *check* itself** (every pass? probability-gated?).
   Once selected: mirror `record_death.py`'s existing circle-notification pattern — the parents' circles
   get told immediately ("others know them before they know them"), while the child doesn't enter
   `pick_pair.py`'s eligible pool until a cooldown clears (decided at creation, hand-authored, like
   routine counts). The child's traits should be a genuine mutation/blend of both parents — knowledge
   crossed and mutated, not a fresh `sample_lore_knowledge.py` draw; criterion inherited-then-mutated
   rather than freshly derived; possibly `life.span` itself as a heritable trait — not just "a new NPC,"
   an actual drift of the population's own composition across generations.
9. **Emergent routine acquisition (later idea, not decided):** a location a character keeps ending up at
   via repeated visits could become a de facto additional routine over time, without being authored at
   creation — emergent geography layered on top of the handcrafted starting set.

**Explicitly still open — per this project's own "nothing decided silently" rule, do not resolve these
silently when implementing:**
- Birth-check trigger condition (point 8).
- How a scene's outcome becomes the arc's next "last thing done" (point 7).
- Group scenes need `/enact` Step 3b extended beyond its current strictly-two-participant design —
  multiple `trusts`/`distrusts` pairs interacting at once, and whether an anchor-touching shock is
  visible to everyone present or just whoever it's aimed at.
- Whether `/enact` Step 3 should be rewritten to give material/action friction an equally-weighted
  "moment it shows" alongside epistemic disagreement now that arcs are meant to carry most of that
  weight — or left as-is, since it may end up doing less work once arcs exist regardless.

**Suggested implementation order** — this is a substantial redesign; build and test the smaller piece
before the larger one, not all at once:
1. Add authored `routines` + per-archetype texture to character files (or a shared lookup keyed by
   archetype name), plus the cycling rule.
2. Extend `/simulate` Step 3 to compute each participant's current routine post-pairing and resolve
   coincidence vs. visit into a scene location.
3. Add arc state (a `last_done`-shaped field) and seed scene content from it instead of free invention,
   per point 7.
4. Run a smaller `/simulate` batch on the existing 5-character population against just steps 1–3,
   specifically to test whether this actually breaks the epistemology-convergence pattern, before
   building anything further on top of it.
5. Only after that: reproduction (point 8) and group scenes (point 5), which both depend on the above
   already working and both need `/enact` itself extended — dyadic → variable participant count for
   group scenes; a new record-keeping script mirroring `record_death.py` for births.

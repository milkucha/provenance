# TODO

Open implementation decisions and work, deferred for later. This is a build/production backlog —
open questions about the lore itself live in `_lore/unknown.md`, not here.

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
- [ ] **Gestures not baked** — passed `-nobake`, uniform `nod_up_down` on all states. Pending `/bake_dialog` pass when wanted in-game.

## Khaoe & Milkucha, Jardín de los Parajes (2026-08-01)

Dialog written: `khaoe_milkucha_jardin_de_los_parajes.json`. Hearsay entry recorded (24 total).
Khaoe lived: 9 → 10. No shocks (anchor not referenced).

- [ ] **Dialog registration ambiguous.** Khaoe already has an entry in `_maps/dialogs/registry.json`
      pointing to `khaoe_banco_colectivo.json`. This new dialog is a second conversation she has,
      this time with Milkucha (the player). Should it overwrite that entry, or should Khaoe's key
      point to a list, or should it stay separate in TODO until the registry format decision is made?
      Same question as the three Feria scenes (Nawom & Morkulo precedent).
- [ ] **Milkucha is a new NPC, introduced only through this scene.** They're the player, so they're
      not being added to the NPC roster (same as Sonoros), but if you want to track them for
      reference, note it in TODO or create a light entry tagged "player-character" and leave it
      untracked.
- [ ] **Gestures not baked** — passed `-nobake`, so every non-`end` state carries uniform
      `nod_up_down`. Pending `/bake_dialog` pass when/if the dialog is wanted in-game.

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

- [x] Trigger/hosting decided (2026-07-30): proximity-based, same mechanism as the khaoe_farlis_*
      fragments — hosted under Nawom's key (his spawn.mcfunction will own the proximity check),
      rather than a plain right-click on either NPC.
- [ ] Neither is registered in `_maps/npcs/registry.json` yet at all — no skin, city, backstory, or
      spawn position decided for either. Run `/character` for both before building spawn functions.
- [ ] Decide the dialog's `end` state action: resume routines for both NPCs, just the triggering
      one, or none at all (relying on the §4 proximity safety net)? Currently left with no `action`
      on purpose, pending this.
- [ ] Register the dialog in `_maps/dialogs/registry.json` under Nawom's key once he's registered and
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
      check against Nuvilo). Registered in `_maps/dialogs/registry.json`.
- [ ] Neither is registered in `_maps/npcs/registry.json` with a `spawn_position` or skin yet —
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
      `.claude/skills/spawn/SKILL.md` (Steps 2/5/6), and `_maps/actions/registry.json` →
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
- [x] **`_maps/dialogs/registry.json` registration resolved** — all five dialogs now registered under
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
      `_lore/hearsay/hearsay.md`). Left unresolved on purpose — see that entry's note before deciding
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
      Nawom & Morkulo precedent: `_maps/dialogs/registry.json` assumes one dialog per NPC key. Ask the
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

## Conflict-resolution skill (proposed, pinned 2026-08-05)

No skill exists yet to help work through `encodings.json`'s `conflicts` array. As of 2026-08-05, 14 of
17 entries (all but `CONFLICT-01`/`03`/`05`) have no `user_resolution` — every disagreement `/tell`
and `/integrate` have ever logged is append-only by design: neither is allowed to set
`user_resolution` themselves, that's the one thing only the user can do (see each skill's own docs).
Right now the only way to resolve one is to notice it while reading the file directly.

- [ ] A proposed `/resolve` (name not fixed) skill would surface open conflicts one at a time — topic,
      full `detail`, and every entry elsewhere in `encodings.json` that carries a matching
      `conflict_ref`/`"see CONFLICT-NN"` note, so the user has the full picture without hunting for
      it — and, only on the user's own explicit call, write `user_resolution` (dated, "per user,
      <date>", matching the existing convention). It must never suggest a resolution, never infer one
      from majority-source-agreement or recency, and never resolve more than the one conflict the user
      is actively looking at. Skipping a conflict (not ready to decide) must be a first-class,
      no-op-safe choice, not just leaving the skill mid-run.
- [ ] Worth deciding whether it should also handle the analogous case in `_lore/unknown.md`
      (a gap the user is now ready to close) — same "only the user decides, never inferred" rule, but
      currently no skill touches `unknown.md` at all except to add to it.

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

- [ ] **None of the three is registered in `_maps/dialogs/registry.json`** — all are multi-NPC, and
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
- [ ] **Gestures deliberately not baked on any of the three** — the author called these three
      lore-only runs (2026-07-31) and asked for Minecraft-facing work to be skipped, so every
      non-`end` state still carries the uniform `nod_up_down` it was written with. Run
      `/bake_dialog <path>` on each of the three if and when they're wanted in-game.
- [x] **`-nobake` flag added to `/enact`** (2026-07-31, author's request): skips Step 8 only.
      Everything through Step 7 still runs in full — the hearsay record, criterion resolution, and
      `life.lived` are the point of an enactment and aren't Minecraft-facing. Documented in a new
      Flags section at the top of `enact/SKILL.md`, which also states explicitly that it does *not*
      skip Step 4 or Step 5/5b.
- [ ] **`bake_dialog` still can't be invoked from `/enact`.** `bake_dialog/SKILL.md` sets
      `disable-model-invocation: true`, so Step 8's Skill-tool call is refused outright — the
      instruction was never executable. Step 8 now documents the blocker and routes to the user
      instead, but the underlying contradiction stands: either drop that flag from `bake_dialog`, or
      accept that baking is permanently user-initiated and simplify Step 8 to say so.
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
`scripts/roll_lifespan.py`, `criterion`/`life` on the registry `_template`, `/character` Steps 4–7
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
      written into `scripts/roll_lifespan.py`'s defaults. Nobody is anywhere near their span yet —
      the most-lived character, Khaoe, is 7 scenes into 51 — so the endgame path in `/enact` Step 5b
      is written but has never actually fired. Worth testing deliberately with a throwaway character
      on `--min 2 --max 4` rather than waiting for it.
- [x] **Death notification, landed 2026-08-01.** `scripts/notify_death.py` computes a dying
      character's "circle" (scene co-participants + everyone named in their own backstory) and
      mechanically samples 30% of it (min 1) to notify immediately via a forced
      `knowledge.experience` entry; it also flags which notified characters have a `criterion.anchor`
      referencing the deceased, so `/enact` Step 5b point 6 can resolve that as a shock through the
      existing reject/reinterpret/break machinery. Everyone else only learns later, the ordinary way
      — the death is recorded as a `_lore/tale/` entry (same shape `/tell` produces,
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

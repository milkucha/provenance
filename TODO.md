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

- [ ] Movement mode not decided yet — material docs list his `Type` as "Hybrid" in
      `Luminacion Register [Code].xlsx` (NPC sheet), which doesn't map cleanly onto Taterzens'
      NONE/FORCED_LOOK/PATH/FORCED_PATH/FOLLOW/FREE modes (README §6). Needs a real decision. The
      dialog's `end` state already wires a `resume_routine` call (matching the Sonoros precedent,
      where the same thing was done ahead of a movement-mode decision) — if Görff ends up `NONE`,
      remove that action and drop `resume_routine.mcfunction`/`check_proximity.mcfunction` per §4.
- [ ] `skin` is filled in from `Luminacion Register [Code].xlsx` (Mineskin column) at the user's
      request — `taterzen_uuid` and `spawn_position` are still blank, per the normal `/enact` flow.
- [ ] Material docs also give an "Easy NPC Preset" (`gondarfolas_gorff`) and Mocap Recording
      reference (`gondarfolas_test2`) and list his role as "Sailing to Terfila" — none of that was
      used here (out of scope for `/enact`); worth checking if a spawn.mcfunction author wants it.
- [ ] Set `spawn_position` in the registry, or stand at the spot manually before spawning.
- [ ] Build `functions/npcs/gondarfolas/spawn.mcfunction` from the template.
- [ ] Wire the right-click action to actually start `luminacion:gondarfolas_darnis_and_bracco`.
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

## General

- [ ] Once one of the above ships, consider adding it as a second worked example in README §8
      (currently only references the Sonoros dialog).

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

## General

- [ ] Once one of the above ships, consider adding it as a second worked example in README §8
      (currently only references the Sonoros dialog).

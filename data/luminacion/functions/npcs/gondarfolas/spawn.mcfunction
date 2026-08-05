# =============================================================================
# Luminacion — Gondarfolas Spawn
# =============================================================================
# Built from _npcs/templates/spawn.mcfunction — see that file for the
# full workflow notes. spawn_position is null in the registry, so stand at the
# desired spot (his boat, Görff) before running this.
#
# WHO CAN RUN THIS: Any operator, once, at setup time.
# WHO CAN TRIGGER THE NPC: Any player (no restrictions after creation).
# =============================================================================


# --- IDENTITY -----------------------------------------------------------------

npc create Gondarfolas

npc edit skin https://minesk.in/8e4356a7612f4b97ac864836457b274e


# --- MOVEMENT -----------------------------------------------------------------

# PATH: follows a set path with rests/look-arounds. Requires resume_routine.mcfunction,
# check_proximity.mcfunction and heal_skin.mcfunction (all built alongside this file),
# and this NPC's check_proximity registered in
# data/luminacion/tags/functions/npc_routine_tick.json.
# Waypoints are NOT recorded via Taterzens' in-game "/npc path" left-click editor —
# that's what causes the stale-restriction bug (see
# _npcs/templates/paths/select_path.mcfunction). Instead, after running this spawn
# function, run one of functions/npcs/gondarfolas/paths/<path_name>.mcfunction to
# give him a route. Until you do, he just stands still in PATH mode.
npc edit movement PATH


# --- PERMISSION LEVEL ---------------------------------------------------------

npc edit commands setPermissionLevel 2


# --- RIGHT-CLICK ACTIONS ------------------------------------------------------

npc edit commands add minecraft function luminacion:npcs/_shared/enter_dialog
npc edit commands add minecraft blabber dialogue start luminacion:gondarfolas_darnis_and_bracco --clicker-- @e[name=Gondarfolas,limit=1,sort=nearest]


# --- REGISTRATION REMINDER ----------------------------------------------------
# UUID capture is automated — do not copy it by hand. Once this NPC (and any
# others) are created and registered in _npcs/npcs/registry.json, run:
#   1. python scripts/minecraft/update_uuids.py generate
#   2. /reload
#   3. /function luminacion:admin/export_npc_uuids
#   4. python scripts/minecraft/update_uuids.py update --log "<path/to/logs/latest.log>"

tellraw @s [{"text":"[Luminacion] ","color":"gold","bold":true},{"text":"Gondarfolas created. Run the UUID export pipeline (scripts/minecraft/update_uuids.py) to register its UUID — see workflow docs."}]

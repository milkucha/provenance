# =============================================================================
# Luminacion — Iläria Spawn
# =============================================================================
# Built from _templates/npcs/spawn.mcfunction — see that file for the full
# workflow notes. spawn_position is null in the registry (manual placement),
# so stand at the desired spot (entrance to the Espiral de la Historia, Feria
# del Milenio) before running this.
#
# WHO CAN RUN THIS: Any operator, once, at setup time.
# WHO CAN TRIGGER THE NPC: Any player (no restrictions after creation).
# =============================================================================


# --- IDENTITY -----------------------------------------------------------------

npc create Iläria

npc edit skin https://minesk.in/016a5789bc0145a19b63db9a2ae65ed1


# --- MOVEMENT -----------------------------------------------------------------

# NONE: stationary, no face-tracking — matches her backstory (permanently
# stationed at the center of the Espiral de la Historia's labyrinth). Requires
# resume_routine.mcfunction, check_proximity.mcfunction, heal_skin.mcfunction
# and heal_path.mcfunction (all built alongside this file) and this NPC's
# check_proximity registered in data/luminacion/tags/functions/
# npc_routine_tick.json — same as every other movement mode (see Khaoe's
# spawn.mcfunction for the precedent on why NONE is not exempt from this
# machinery). enter_dialog's pause_routine still temporarily sets FORCED_LOOK
# while a player is close or she's mid-conversation; resume_routine.mcfunction
# sets her back to NONE afterward.
npc edit movement NONE


# --- PERMISSION LEVEL ---------------------------------------------------------

npc edit commands setPermissionLevel 2


# --- RIGHT-CLICK ACTIONS ------------------------------------------------------
# Single dialog, no side effects beyond it.

npc edit commands add minecraft function luminacion:npcs/_shared/enter_dialog
npc edit commands add minecraft blabber dialogue start luminacion:ilaria_espiral_de_la_historia --clicker-- @e[name="Iläria",limit=1,sort=nearest]


# --- REGISTRATION REMINDER ----------------------------------------------------
# UUID capture is automated — do not copy it by hand. Once this NPC (and any
# others) are created and registered in _npcs/npcs/registry.json, run:
#   1. python scripts/update_uuids.py generate
#   2. /reload
#   3. /function luminacion:admin/export_npc_uuids
#   4. python scripts/update_uuids.py update --log "<path/to/logs/latest.log>"

tellraw @s [{"text":"[Luminacion] ","color":"gold","bold":true},{"text":"Iläria created. Run the UUID export pipeline (scripts/update_uuids.py) to register its UUID — see workflow docs."}]

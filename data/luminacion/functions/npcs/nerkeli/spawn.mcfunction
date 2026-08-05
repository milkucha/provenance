# =============================================================================
# Luminacion — Nerkeli Spawn
# =============================================================================
# Built from _templates/npcs/spawn.mcfunction — see that file for the full
# workflow notes. spawn_position is null in the registry, and his default
# state (hangar) doesn't teleport him anywhere, so stand him at the hangar
# (next to Nuvilo) manually before or after running this.
#
# WHO CAN RUN THIS: Any operator, once, at setup time.
# WHO CAN TRIGGER THE NPC: Any player (no restrictions after creation).
# =============================================================================


# --- IDENTITY -----------------------------------------------------------------

npc create Nerkeli

npc edit skin https://minesk.in/7338c1b2f7b540e0b831728ddd0792bf


# --- PERMISSION LEVEL ---------------------------------------------------------

npc edit commands setPermissionLevel 2


# --- MOVEMENT & RIGHT-CLICK ACTIONS --------------------------------------------
# Nerkeli has two states (see _npcs/actions/registry.json → _action_templates.
# multi_state_npc, and functions/npcs/nerkeli/states/): "hangar" (stationary,
# standing with Nuvilo, triggers his solo hangar-talk dialog — his default
# below) and "roaming" (PATH, no dialog wired yet). Switch at any time with
# /function luminacion:npcs/nerkeli/states/<hangar|roaming>.

function luminacion:npcs/nerkeli/states/hangar


# --- REGISTRATION REMINDER ----------------------------------------------------
# UUID capture is automated — do not copy it by hand. Once this NPC (and any
# others) are created and registered in _npcs/npcs/registry.json, run:
#   1. python scripts/update_uuids.py generate
#   2. /reload
#   3. /function luminacion:admin/export_npc_uuids
#   4. python scripts/update_uuids.py update --log "<path/to/logs/latest.log>"

tellraw @s [{"text":"[Luminacion] ","color":"gold","bold":true},{"text":"Nerkeli created. Run the UUID export pipeline (scripts/update_uuids.py) to register its UUID — see workflow docs."}]

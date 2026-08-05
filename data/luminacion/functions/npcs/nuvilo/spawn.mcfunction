# =============================================================================
# Luminacion — Nuvilo Spawn
# =============================================================================
# Built from _npcs/templates/spawn.mcfunction — see that file for the full
# workflow notes. spawn_position is null in the registry, and his default
# state (hangar) doesn't teleport him anywhere, so stand him next to Nerkeli
# manually before or after running this.
#
# WHO CAN RUN THIS: Any operator, once, at setup time.
# WHO CAN TRIGGER THE NPC: Any player (no restrictions after creation).
# =============================================================================


# --- IDENTITY -----------------------------------------------------------------

npc create Nuvilo

# TODO: skin not decided yet (blank in _npcs/npcs/registry.json). Uncomment
# and fill in once chosen, then also fill in heal_skin.mcfunction to match:
# npc edit skin <https://www.mineskin.org/ID>


# --- PERMISSION LEVEL ---------------------------------------------------------

npc edit commands setPermissionLevel 2


# --- MOVEMENT & RIGHT-CLICK ACTIONS --------------------------------------------
# Nuvilo has two states (see _npcs/actions/registry.json → _action_templates.
# multi_state_npc, and functions/npcs/nuvilo/states/): "hangar" (stationary,
# standing with Nerkeli, triggers the eavesdrop dialog — his default below)
# and "roaming" (PATH, triggers his solo scholar dialog). Switch at any time
# with /function luminacion:npcs/nuvilo/states/<hangar|roaming>.

function luminacion:npcs/nuvilo/states/hangar


# --- REGISTRATION REMINDER ----------------------------------------------------
# UUID capture is automated — do not copy it by hand. Once this NPC (and any
# others) are created and registered in _npcs/npcs/registry.json, run:
#   1. python scripts/minecraft/update_uuids.py generate
#   2. /reload
#   3. /function luminacion:admin/export_npc_uuids
#   4. python scripts/minecraft/update_uuids.py update --log "<path/to/logs/latest.log>"

tellraw @s [{"text":"[Luminacion] ","color":"gold","bold":true},{"text":"Nuvilo created. Run the UUID export pipeline (scripts/minecraft/update_uuids.py) to register its UUID — see workflow docs."}]

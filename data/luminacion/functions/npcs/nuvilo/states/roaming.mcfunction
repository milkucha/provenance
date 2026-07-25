# =============================================================================
# Luminacion — Nuvilo State: roaming
# =============================================================================
# Built from _templates/npcs/states/roaming_state.mcfunction. Switches Nuvilo
# out of the hangar scene and into his solo wandering routine: clears
# right-click actions and rewires them to his scholar dialog, sets movement
# to PATH, and records this as the active state.
#
# No waypoints are set yet. Once some are decided, add here (see
# _templates/npcs/paths/select_path.mcfunction for the exact pattern):
#   execute as @e[type=taterzens:npc,name=Nuvilo,limit=1] at @s run tp @s <x0> <y0> <z0>
#   data merge entity @e[type=taterzens:npc,name=Nuvilo,limit=1] {TaterzenNPCTag:{PathTargets:[...],CurrentMoveTarget:0}}
# — and a matching line in heal_path.mcfunction. Until then he just stands
# still in PATH mode, same as an NPC that's never had a path recorded.
# =============================================================================

execute as @e[type=taterzens:npc,name=Nuvilo,limit=1] at @s run npc edit commands clear
execute as @e[type=taterzens:npc,name=Nuvilo,limit=1] at @s run npc edit commands add minecraft function luminacion:npcs/_shared/enter_dialog
execute as @e[type=taterzens:npc,name=Nuvilo,limit=1] at @s run npc edit commands add minecraft blabber dialogue start luminacion:nuvilo_scholar_at_the_feria --clicker-- @e[name=Nuvilo,limit=1,sort=nearest]

execute as @e[type=taterzens:npc,name=Nuvilo,limit=1] at @s run npc edit movement PATH

data modify storage luminacion:npcs nuvilo.active_state set value "roaming"

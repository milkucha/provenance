# =============================================================================
# Luminacion — Nerkeli State: roaming
# =============================================================================
# Built from _templates/npcs/states/roaming_state.mcfunction. Switches
# Nerkeli out of the hangar scene into a roaming routine: sets movement to
# PATH and records this as the active state.
#
# No roaming dialog decided yet, so right-click actions are just cleared (no
# interaction while roaming, for now) — once one exists, add here:
#   execute as @e[type=taterzens:npc,name=Nerkeli,limit=1] at @s run npc edit commands add minecraft function luminacion:npcs/_shared/enter_dialog
#   execute as @e[type=taterzens:npc,name=Nerkeli,limit=1] at @s run npc edit commands add minecraft blabber dialogue start luminacion:<dialog_id> --clicker-- @e[name=Nerkeli,limit=1,sort=nearest]
# (that dialog's end_dialogue action should call resume_routine, same as any
# single-state roaming NPC).
#
# No waypoints set yet either — once decided, add here (see
# _templates/npcs/paths/select_path.mcfunction for the exact pattern):
#   execute as @e[type=taterzens:npc,name=Nerkeli,limit=1] at @s run tp @s <x0> <y0> <z0>
#   data merge entity @e[type=taterzens:npc,name=Nerkeli,limit=1] {TaterzenNPCTag:{PathTargets:[...],CurrentMoveTarget:0}}
# — and a matching line in heal_path.mcfunction. Until then he just stands
# still in PATH mode.
# =============================================================================

execute as @e[type=taterzens:npc,name=Nerkeli,limit=1] at @s run npc edit commands clear

execute as @e[type=taterzens:npc,name=Nerkeli,limit=1] at @s run npc edit movement PATH

data modify storage luminacion:npcs nerkeli.active_state set value "roaming"

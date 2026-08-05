# =============================================================================
# Luminacion — NPC Roaming State Template
# =============================================================================
# For NPCs that switch between multiple named "states" at runtime — see
# _npcs/actions/registry.json → _action_templates.multi_state_npc for the full
# convention. Skip this whole states/ pattern if this NPC only ever roams —
# use _templates/npcs/paths/select_path.mcfunction directly instead.
#
# This variant: movement PATH, with waypoints set the same way
# _templates/npcs/paths/select_path.mcfunction does (confirmed in-game:
# "/data merge entity" retroactively triggers Taterzens' own NBT-load logic,
# including its restrictTo() call, so this sets the movement restriction
# correctly with no left-click editor involved).
#
# Does wire enter_dialog/pause_routine into the right-click action (if this
# state has a dialog) — unlike a stationary state, there IS a routine here
# that needs pausing while talking. That dialog's end_dialogue action should
# call resume_routine, same as any single-state roaming NPC.
#
# WORKFLOW:
#   1. Duplicate as: functions/npcs/<npc_key>/states/<state_name>.mcfunction
#   2. Fill <display_name>, <npc_key>, <state_name>, <dialog_id> and the
#      waypoint list below. Remove the two blabber/enter_dialog lines
#      entirely if this state has no right-click dialog yet.
#   3. If no waypoints are decided yet, delete the "tp" and "data merge
#      entity" lines below — the NPC will just stand still in PATH mode
#      until you come back and add them (see paths/select_path.mcfunction).
#   4. Add a matching line to functions/npcs/<npc_key>/heal_path.mcfunction
#      once waypoints exist, same as a plain roaming NPC.
#   5. Run as an operator: /function luminacion:npcs/<npc_key>/states/<state_name>
# =============================================================================

execute as @e[type=taterzens:npc,name=<display_name>,limit=1] at @s run npc edit commands clear
execute as @e[type=taterzens:npc,name=<display_name>,limit=1] at @s run npc edit commands add minecraft function luminacion:npcs/_shared/enter_dialog
execute as @e[type=taterzens:npc,name=<display_name>,limit=1] at @s run npc edit commands add minecraft blabber dialogue start luminacion:<dialog_id> --clicker-- @e[name=<display_name>,limit=1,sort=nearest]

execute as @e[type=taterzens:npc,name=<display_name>,limit=1] at @s run tp @s <x0> <y0> <z0>
data merge entity @e[type=taterzens:npc,name=<display_name>,limit=1] {TaterzenNPCTag:{PathTargets:[{x:<x0>,y:<y0>,z:<z0>},{x:<x1>,y:<y1>,z:<z1>}],CurrentMoveTarget:0}}
execute as @e[type=taterzens:npc,name=<display_name>,limit=1] at @s run npc edit movement PATH

data modify storage luminacion:npcs <npc_key>.active_state set value "<state_name>"

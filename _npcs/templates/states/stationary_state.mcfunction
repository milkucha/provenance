# =============================================================================
# Luminacion — NPC Stationary State Template
# =============================================================================
# For NPCs that switch between multiple named "states" at runtime (e.g.
# standing still for one scene, roaming for another) — see
# _npcs/actions/registry.json → _action_templates.multi_state_npc for the full
# convention. Skip this whole states/ pattern if this NPC only ever has one
# movement mode for its entire lifetime — use plain spawn.mcfunction instead.
#
# This variant: movement NONE. No teleport — "stationary" just means "stay
# wherever it currently is." Position the NPC manually (stand there and
# /npc tp, or walk it there) before or after running this.
#
# Does NOT wire enter_dialog/pause_routine into the right-click action, and
# any dialog triggered from this state should NOT call resume_routine on its
# end_dialogue action — there's no routine to pause while movement is NONE.
# check_proximity.mcfunction only runs the pause/resume dance while this
# NPC's active_state is its roaming one (see roaming_state.mcfunction).
#
# WORKFLOW:
#   1. Duplicate as: functions/npcs/<npc_key>/states/<state_name>.mcfunction
#   2. Fill <display_name>, <npc_key>, <state_name> and <dialog_id> below.
#      Remove the blabber line entirely if this state has no right-click dialog.
#   3. Run as an operator: /function luminacion:npcs/<npc_key>/states/<state_name>
# =============================================================================

execute as @e[type=taterzens:npc,name=<display_name>,limit=1] at @s run npc edit commands clear
execute as @e[type=taterzens:npc,name=<display_name>,limit=1] at @s run npc edit commands add minecraft blabber dialogue start luminacion:<dialog_id> --clicker-- @e[name=<display_name>,limit=1,sort=nearest]

execute as @e[type=taterzens:npc,name=<display_name>,limit=1] at @s run npc edit movement NONE

data modify storage luminacion:npcs <npc_key>.active_state set value "<state_name>"

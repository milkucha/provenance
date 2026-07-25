# =============================================================================
# Luminacion — Nuvilo State: hangar
# =============================================================================
# Built from _templates/npcs/states/stationary_state.mcfunction. Switches
# Nuvilo into the stationary hangar scene alongside Nerkeli: clears
# right-click actions and rewires them to the two-NPC eavesdrop dialog, sets
# movement to NONE, and records this as the active state.
#
# No teleport — position him next to Nerkeli manually (stand there and
# /npc tp, or walk him there). This is the default state spawn.mcfunction
# puts him in.
#
# Stationary (NONE) doesn't need enter_dialog/pause_routine wiring — there's
# no routine to pause. check_proximity.mcfunction only runs the pause/resume
# dance while active_state is "roaming" (see states/roaming.mcfunction).
#
# Faces him toward Nerkeli continuously — see hangar_look_tick.mcfunction
# (registered in npc_routine_tick.json), which re-applies this every tick
# while both NPCs are marked "hangar", so no one-time facing command is
# needed here at all; the tick check picks it up within a fraction of a
# second regardless of spawn order.
# =============================================================================

execute as @e[type=taterzens:npc,name=Nuvilo,limit=1] at @s run npc edit commands clear
execute as @e[type=taterzens:npc,name=Nuvilo,limit=1] at @s run npc edit commands add minecraft blabber dialogue start luminacion:nuvilo_nerkeli_feria_del_milenio --clicker-- @e[name=Nuvilo,limit=1,sort=nearest]

execute as @e[type=taterzens:npc,name=Nuvilo,limit=1] at @s run npc edit movement NONE

data modify storage luminacion:npcs nuvilo.active_state set value "hangar"

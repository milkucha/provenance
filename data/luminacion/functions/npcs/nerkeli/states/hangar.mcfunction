# =============================================================================
# Luminacion — Nerkeli State: hangar
# =============================================================================
# Built from _npcs/templates/states/stationary_state.mcfunction. Switches
# Nerkeli into the stationary hangar scene: clears right-click actions and
# rewires them to his solo hangar-talk dialog, sets movement to NONE, and
# records this as the active state.
#
# No teleport — position him at the hangar (next to Nuvilo) manually. This is
# the default state spawn.mcfunction puts him in.
#
# Stationary (NONE) doesn't need enter_dialog/pause_routine wiring — there's
# no routine to pause. check_proximity.mcfunction only runs the pause/resume
# dance while active_state is "roaming" (see states/roaming.mcfunction).
#
# Note: the two-NPC eavesdrop dialog (nuvilo_nerkeli_feria_del_milenio) is
# proximity-triggered (2026-07-26 change), not right-click, by a player
# getting within 2 blocks of EITHER Nuvilo or Nerkeli — see
# functions/npcs/nuvilo/hangar_dialog_tick.mcfunction, which lives under
# nuvilo/ but reads and checks both NPCs. This solo dialog's right-click
# wiring below is unrelated and unaffected.
#
# Faces him toward Nuvilo continuously — see
# functions/npcs/nuvilo/hangar_look_tick.mcfunction (registered in
# npc_routine_tick.json), which re-applies this every tick while both NPCs
# are marked "hangar", so no one-time facing command is needed here at all.
# =============================================================================

execute as @e[type=taterzens:npc,name=Nerkeli,limit=1] at @s run npc edit commands clear
execute as @e[type=taterzens:npc,name=Nerkeli,limit=1] at @s run npc edit commands add minecraft blabber dialogue start luminacion:nerkeli_hangar_talk --clicker-- @e[name=Nerkeli,limit=1,sort=nearest]

execute as @e[type=taterzens:npc,name=Nerkeli,limit=1] at @s run npc edit movement NONE

data modify storage luminacion:npcs nerkeli.active_state set value "hangar"

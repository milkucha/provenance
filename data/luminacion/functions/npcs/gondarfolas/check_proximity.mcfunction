# =============================================================================
# Luminacion — Gondarfolas Proximity Check
# =============================================================================
# Built from _templates/npcs/check_proximity.mcfunction. Runs once per
# tick via #luminacion:npc_routine_tick (see functions/tick.mcfunction).
# =============================================================================

# A player got within 2 blocks: stop the routine and become interactable.
execute as @e[type=taterzens:npc,name=Gondarfolas,limit=1,tag=!luminacion.paused] at @s if entity @a[distance=..2] run function luminacion:npcs/_shared/pause_routine

# No player nearby anymore, and not mid-dialog: resume the routine.
execute as @e[type=taterzens:npc,name=Gondarfolas,limit=1,tag=luminacion.paused,tag=!luminacion.in_dialog] at @s unless entity @a[distance=..2] run function luminacion:npcs/gondarfolas/resume_routine

# =============================================================================
# Luminacion — Döran Proximity Check
# =============================================================================
# Built from _templates/npcs/check_proximity.mcfunction. Runs once per
# tick via #luminacion:npc_routine_tick (see functions/tick.mcfunction).
# =============================================================================

# A player got within 2 blocks: stop the routine and become interactable.
execute as @e[type=taterzens:npc,name="Döran",limit=1,tag=!luminacion.paused] at @s if entity @a[distance=..2] run function luminacion:npcs/_shared/pause_routine

# No player within 6 blocks anymore: resume the routine. Widened from 2 to 6 —
# confirmed in-game (2026-07-25) that 2 blocks let a click from beyond that (trivial
# in creative, where reach is 6 blocks) undo the pause on the very next tick while
# the dialog was still open, since Taterzens has no interact-range override on top
# of plain vanilla reach. That's what made him visibly wander off mid-conversation
# and swallowed his nod animations (movement fighting the nod's rotation writes).
# See _maps/actions/registry.json → _action_templates.routine_pause_resume for the
# full writeup. Keep this wider than the 2-block pause trigger above.
execute as @e[type=taterzens:npc,name="Döran",limit=1,tag=luminacion.paused] at @s unless entity @a[distance=..6] run function luminacion:npcs/doran/resume_routine

# Self-heal (skin + path): check every 100 ticks (5s), not every tick, so
# drift gets fixed without hammering mineskin.org or constantly re-teleporting
# mid-route on every tick.
scoreboard players add doran_heal_cd luminacion.int 1
execute if score doran_heal_cd luminacion.int matches 100.. run function luminacion:npcs/doran/heal_skin
execute if score doran_heal_cd luminacion.int matches 100.. run function luminacion:npcs/doran/heal_path
execute if score doran_heal_cd luminacion.int matches 100.. run scoreboard players set doran_heal_cd luminacion.int 0

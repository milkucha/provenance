# =============================================================================
# Luminacion — Gondarfolas Proximity Check
# =============================================================================
# Built from _templates/npcs/check_proximity.mcfunction. Runs once per
# tick via #luminacion:npc_routine_tick (see functions/tick.mcfunction).
# =============================================================================

# A player got within 2 blocks: stop the routine and become interactable.
execute as @e[type=taterzens:npc,name=Gondarfolas,limit=1,tag=!luminacion.paused] at @s if entity @a[distance=..2] run function luminacion:npcs/_shared/pause_routine

# No player within 6 blocks anymore: resume the routine. Widened from 2 to 6 — a
# click from beyond 2 blocks (trivial in creative, 6-block reach) would otherwise
# undo the pause on the very next tick while the dialog is still open, since
# Taterzens has no interact-range override on top of plain vanilla reach. Confirmed
# in-game via Döran, 2026-07-25 — see _maps/actions/registry.json →
# _action_templates.routine_pause_resume for the full writeup. Keep this wider than
# the 2-block pause trigger above.
execute as @e[type=taterzens:npc,name=Gondarfolas,limit=1,tag=luminacion.paused] at @s unless entity @a[distance=..6] run function luminacion:npcs/gondarfolas/resume_routine

# Self-heal (skin + path): check every 100 ticks (5s), not every tick, so
# drift gets fixed without hammering mineskin.org or constantly re-teleporting
# mid-route on every tick.
scoreboard players add gondarfolas_heal_cd luminacion.int 1
execute if score gondarfolas_heal_cd luminacion.int matches 100.. run function luminacion:npcs/gondarfolas/heal_skin
execute if score gondarfolas_heal_cd luminacion.int matches 100.. run function luminacion:npcs/gondarfolas/heal_path
execute if score gondarfolas_heal_cd luminacion.int matches 100.. run scoreboard players set gondarfolas_heal_cd luminacion.int 0

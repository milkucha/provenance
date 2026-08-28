# =============================================================================
# Provenance — NPC Proximity Check Template
# =============================================================================
# Needed for every NPC, regardless of movement mode — including NONE. This used
# to be scoped to roaming modes only, which was wrong: the skin self-heal race
# (see heal_skin.mcfunction) and the pause/resume tagging apply to a stationary
# NPC exactly the same as a roaming one.
#
# WORKFLOW:
#   1. Duplicate as: functions/npcs/<npc_key>/check_proximity.mcfunction
#   2. Fill <display_name> and <npc_key> below.
#   3. Add this function's path to the "values" array in:
#      data/luminacion/tags/functions/npc_routine_tick.json
#   4. Make sure functions/npcs/<npc_key>/resume_routine.mcfunction exists too.
#   5. Make sure functions/npcs/<npc_key>/heal_skin.mcfunction exists too
#      (see _npcs/templates/heal_skin.mcfunction).
#   6. Make sure functions/npcs/<npc_key>/heal_path.mcfunction exists too
#      (see _npcs/templates/heal_path.mcfunction and _npcs/templates/paths/select_path.mcfunction).
#
# Runs once per tick via #luminacion:npc_routine_tick (see tick.mcfunction).
# =============================================================================

# A player got within 2 blocks: stop the routine and become interactable.
execute as @e[type=taterzens:npc,name=<display_name>,limit=1,tag=!luminacion.paused] at @s if entity @a[distance=..2] run function luminacion:npcs/_shared/pause_routine

# No player within 6 blocks anymore: resume the routine. This is the safety net for
# dialogs abandoned early (Escape / disconnect) — Blabber does not run end_dialogue
# actions in that case, so the dialog-end resume call (see resume_routine.mcfunction)
# never fires on its own. Blabber's screen freezes player movement while open, so
# distance can only exceed THIS radius after the dialog has actually closed — but
# that only holds if the radius is at least as wide as the game's actual click/reach
# range. Taterzens has no interact-range override (plain vanilla reach: 3 blocks
# survival, 6 creative), so this MUST be wider than the 2-block pause trigger above,
# or a click from beyond 2 blocks (easy in creative) undoes the pause on the very
# next tick while the dialog is still open — confirmed in-game (Döran, 2026-07-25:
# he visibly wandered off mid-conversation, and the nod animation got swallowed by
# the resulting movement fighting its own rotation writes). 6 blocks covers creative
# reach with no margin to spare; don't shrink it back toward the pause trigger's 2.
execute as @e[type=taterzens:npc,name=<display_name>,limit=1,tag=luminacion.paused] at @s unless entity @a[distance=..6] run function luminacion:npcs/<npc_key>/resume_routine

# Self-heal (skin + path): check every 100 ticks (5s), not every tick, so
# drift gets fixed without hammering mineskin.org or constantly re-teleporting
# mid-route on every tick.
scoreboard players add <npc_key>_heal_cd luminacion.int 1
execute if score <npc_key>_heal_cd luminacion.int matches 100.. run function luminacion:npcs/<npc_key>/heal_skin
execute if score <npc_key>_heal_cd luminacion.int matches 100.. run function luminacion:npcs/<npc_key>/heal_path
execute if score <npc_key>_heal_cd luminacion.int matches 100.. run scoreboard players set <npc_key>_heal_cd luminacion.int 0

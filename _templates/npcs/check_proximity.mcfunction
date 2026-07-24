# =============================================================================
# Luminacion — NPC Proximity Check Template
# =============================================================================
# Only needed for NPCs with a roaming movement mode (PATH / FORCED_PATH / FREE /
# FOLLOW). Stationary (NONE) NPCs don't need this.
#
# WORKFLOW:
#   1. Duplicate as: functions/npcs/<npc_key>/check_proximity.mcfunction
#   2. Fill <display_name> and <npc_key> below.
#   3. Add this function's path to the "values" array in:
#      data/luminacion/tags/functions/npc_routine_tick.json
#   4. Make sure functions/npcs/<npc_key>/resume_routine.mcfunction exists too.
#
# Runs once per tick via #luminacion:npc_routine_tick (see tick.mcfunction).
# =============================================================================

# A player got within 2 blocks: stop the routine and become interactable.
execute as @e[type=taterzens:npc,name=<display_name>,limit=1,tag=!luminacion.paused] at @s if entity @a[distance=..2] run function luminacion:npcs/_shared/pause_routine

# No player nearby anymore, and not mid-dialog: resume the routine.
# This is the safety net for dialogs abandoned early (Escape / disconnect) — Blabber
# does not run end_dialogue actions in that case, so the dialog-end resume call
# (see resume_routine.mcfunction) never fires on its own.
execute as @e[type=taterzens:npc,name=<display_name>,limit=1,tag=luminacion.paused,tag=!luminacion.in_dialog] at @s unless entity @a[distance=..2] run function luminacion:npcs/<npc_key>/resume_routine

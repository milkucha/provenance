# =============================================================================
# Luminacion — Döran Resume Routine
# =============================================================================
# Built from _templates/npcs/resume_routine.mcfunction. See that file
# for the two call contexts this must work under (@s = the NPC in both cases).
# =============================================================================

npc edit movement PATH
tag @s remove luminacion.paused
tag @s remove luminacion.in_dialog

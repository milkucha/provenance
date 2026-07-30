# =============================================================================
# Luminacion — Iläria Resume Routine
# =============================================================================
# Built from _templates/npcs/resume_routine.mcfunction. See that file
# for the two call contexts this must work under (@s = the NPC in both cases).
#
# Iläria's resting movement mode is NONE, so this doesn't restore any actual
# movement behavior — it exists for the tag cleanup (below) and because this
# machinery is now built for every NPC regardless of movement mode (see
# _maps/actions/registry.json -> _action_templates.routine_pause_resume).
# "npc edit movement NONE" here just re-asserts her resting mode after
# pause_routine's temporary FORCED_LOOK.
# =============================================================================

npc edit movement NONE
tag @s remove luminacion.paused
tag @s remove luminacion.in_dialog

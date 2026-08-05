# =============================================================================
# Luminacion — Nuvilo Resume Routine
# =============================================================================
# Built from _npcs/templates/resume_routine.mcfunction. Hardcodes PATH since
# check_proximity.mcfunction only ever calls this while Nuvilo's active_state
# is "roaming" — see _npcs/actions/registry.json → _action_templates.multi_state_npc.
# =============================================================================

npc edit movement PATH
tag @s remove luminacion.paused
tag @s remove luminacion.in_dialog

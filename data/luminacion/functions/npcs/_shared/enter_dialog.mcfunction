# =============================================================================
# Luminacion — Shared: Enter Dialog
# =============================================================================
# Called as the FIRST right-click command action, before "blabber dialogue start".
# Pauses the NPC's routine and flags it as mid-conversation.
#
# CALL CONTEXT: must be called with @s = the NPC itself (true for right-click
# command actions — see functions/npcs/_shared/pause_routine.mcfunction).
# =============================================================================

function luminacion:npcs/_shared/pause_routine
tag @s add luminacion.in_dialog

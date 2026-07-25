# =============================================================================
# Luminacion — Shared: Pause Routine
# =============================================================================
# Stops the NPC's roaming and turns it to face the nearby player (FORCED_LOOK),
# and flags it as paused, so the proximity/dialog resume logic knows to leave it
# alone until resumed.
#
# CALL CONTEXT: must be called with @s = the NPC itself. This is already true when
# called from a Taterzens right-click command action (Taterzens executes those with
# the NPC as the command source), or from a tick check via "execute as <npc> run ...".
# =============================================================================

npc edit movement FORCED_LOOK
tag @s add luminacion.paused

# =============================================================================
# Luminacion — Shared: Pause Routine
# =============================================================================
# Stops whatever movement behaviour the NPC currently has and flags it as paused,
# so the proximity/dialog resume logic knows to leave it alone until resumed.
#
# CALL CONTEXT: must be called with @s = the NPC itself. This is already true when
# called from a Taterzens right-click command action (Taterzens executes those with
# the NPC as the command source), or from a tick check via "execute as <npc> run ...".
# =============================================================================

npc edit movement NONE
tag @s add luminacion.paused

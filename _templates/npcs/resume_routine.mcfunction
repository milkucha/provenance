# =============================================================================
# Luminacion — NPC Resume Routine Template
# =============================================================================
# WORKFLOW:
#   1. Duplicate as: functions/npcs/<npc_key>/resume_routine.mcfunction
#   2. Fill <MODE> below to match this NPC's routine movement mode
#      (see _maps/actions/registry.json -> movement action for this NPC).
#      For FOLLOW mode, replace the line with:
#        npc edit movement FOLLOW <name>
#        npc edit movement FOLLOW UUID <uuid>
#   3. Needed for every NPC, including NONE — in that case <MODE> is just NONE
#      again, which doesn't change any actual behavior; the tag cleanup below
#      (and the check_proximity/heal_skin machinery this unlocks) is the part
#      that still matters for a stationary NPC.
#
# CALLED FROM TWO PLACES — both must reach this with @s = the NPC itself:
#   1. functions/npcs/<npc_key>/check_proximity.mcfunction (tick loop), already
#      executed "as" the NPC — calls this function directly.
#   2. This NPC's Blabber dialog end_dialogue action(s), via:
#        execute as @interlocutor run function luminacion:npcs/<npc_key>/resume_routine
#      Must use "execute as @interlocutor" there (not call this function directly),
#      since Blabber dialog actions run with @s = the player, not the NPC.
# =============================================================================

npc edit movement <MODE>
tag @s remove luminacion.paused
tag @s remove luminacion.in_dialog

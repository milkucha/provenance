# =============================================================================
# Provenance — Dialog Ending Template: Give Item + Resume Routine
# =============================================================================
# Use this pattern whenever a dialog ending needs to combine a side effect
# (give / scoreboard / etc.) with resuming the NPC's routine — a Blabber
# end_dialogue action can only run ONE command, so combined effects go through
# a function like this one instead of two separate actions.
#
# WORKFLOW:
#   1. Duplicate/rename as needed under functions/npcs/<npc_key>/ (e.g.
#      end_with_gift.mcfunction), one per dialog ending that needs this.
#   2. Fill <item_id> / <count> (and add/remove other side-effect lines).
#   3. Reference it from the dialog's end_dialogue action:
#        "value": "function luminacion:npcs/<npc_key>/end_with_gift"
#
# CALL CONTEXT: runs with @s = the player (called directly from the dialog's
# end_dialogue action — do NOT wrap this call in "execute as ...", or
# @interlocutor below will fail to resolve).
# =============================================================================

give @s minecraft:<item_id> <count>
execute as @interlocutor run function luminacion:npcs/<npc_key>/resume_routine

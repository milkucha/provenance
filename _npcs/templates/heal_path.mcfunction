# =============================================================================
# Luminacion — NPC Path Self-Heal Template
# =============================================================================
# Called every 100 ticks from check_proximity.mcfunction, alongside
# heal_skin.mcfunction. Re-applies the currently active path only if
# PathTargets has actually gone empty (not merely changed) — this avoids
# rubber-banding the NPC mid-route on a false positive.
#
# WORKFLOW:
#   1. Duplicate as: functions/npcs/<npc_key>/heal_path.mcfunction
#   2. Leave it as just this header until this NPC has at least one path —
#      see _npcs/templates/paths/select_path.mcfunction.
#   3. Add one line below per path defined for this NPC — copy this pattern
#      for every functions/npcs/<npc_key>/paths/<path_name>.mcfunction:
#
#   execute if data storage luminacion:npcs {<npc_key>:{active_path:"<path_name>"}} unless data entity @e[type=taterzens:npc,name=<display_name>,limit=1] TaterzenNPCTag.PathTargets[0] run function luminacion:npcs/<npc_key>/paths/<path_name>
# =============================================================================

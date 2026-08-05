# =============================================================================
# Luminacion — Nerkeli Path Self-Heal
# =============================================================================
# Built from _npcs/templates/heal_path.mcfunction. Called every 100 ticks (5s)
# from check_proximity.mcfunction, only while active_state is "roaming".
#
# No waypoints defined for the "roaming" state yet, so this file has nothing
# to do. Once functions/npcs/nerkeli/states/roaming.mcfunction has waypoints,
# add a line here to match — see _npcs/templates/heal_path.mcfunction for the
# pattern (using active_state instead of active_path):
#
# execute if data storage luminacion:npcs {nerkeli:{active_state:"roaming"}} unless data entity @e[type=taterzens:npc,name=Nerkeli,limit=1] TaterzenNPCTag.PathTargets[0] run function luminacion:npcs/nerkeli/states/roaming
# =============================================================================

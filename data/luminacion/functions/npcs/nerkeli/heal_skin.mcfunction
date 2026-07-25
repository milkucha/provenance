# =============================================================================
# Luminacion — Nerkeli Skin Self-Heal
# =============================================================================
# Built from _templates/npcs/heal_skin.mcfunction. Called every 100 ticks (5s)
# from check_proximity.mcfunction.
#
# No skin decided yet (blank in _maps/npcs/registry.json), so this file has
# nothing to do. Once one is chosen, fill in spawn.mcfunction's "npc edit
# skin" line AND uncomment/fill in the line below:
#
# execute as @e[type=taterzens:npc,name=Nerkeli,limit=1] at @s unless data entity @s TaterzenNPCTag.skin.value run npc edit skin <https://www.mineskin.org/ID>
# =============================================================================

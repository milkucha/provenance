# =============================================================================
# Luminacion — Iläria Skin Self-Heal
# =============================================================================
# Built from _templates/npcs/heal_skin.mcfunction. Called every 100 ticks (5s)
# from check_proximity.mcfunction, alongside heal_path.mcfunction — both share
# the same cooldown counter, reset there rather than here.
#
# Works around a Taterzens bug: skins are fetched asynchronously from
# mineskin.org on a background thread, decoupled from anything else touching
# the NPC. This applies regardless of movement mode — a NONE npc is just as
# exposed to the race as a roaming one — which is why this file (and
# check_proximity.mcfunction calling it) is built for every NPC, not only
# roaming ones.
# =============================================================================

execute as @e[type=taterzens:npc,name="Iläria",limit=1] at @s unless data entity @s TaterzenNPCTag.skin.value run npc edit skin https://minesk.in/016a5789bc0145a19b63db9a2ae65ed1

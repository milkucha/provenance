# =============================================================================
# Luminacion — Nerkeli Skin Self-Heal
# =============================================================================
# Built from _npcs/templates/heal_skin.mcfunction. Called every 100 ticks (5s)
# from check_proximity.mcfunction.
#
# Works around a Taterzens bug: skins are fetched asynchronously from
# mineskin.org on a background thread, decoupled from anything else happening
# to the NPC (e.g. deselecting it). If something touches the NPC's profile
# before that fetch lands, the skin can end up permanently unset. Re-running
# "npc edit skin" is harmless when the skin is already set — Taterzens just
# re-fetches and overwrites it with the same result.
# =============================================================================

execute as @e[type=taterzens:npc,name=Nerkeli,limit=1] at @s unless data entity @s TaterzenNPCTag.skin.value run npc edit skin https://minesk.in/7338c1b2f7b540e0b831728ddd0792bf

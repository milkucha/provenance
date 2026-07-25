# =============================================================================
# Luminacion — Khaoe Skin Self-Heal
# =============================================================================
# Built from _templates/npcs/heal_skin.mcfunction. Called every 100 ticks (5s)
# from check_proximity.mcfunction, alongside heal_path.mcfunction — both share
# the same cooldown counter, reset there rather than here.
#
# Works around a Taterzens bug: skins are fetched asynchronously from
# mineskin.org on a background thread, decoupled from anything else touching
# the NPC. This applies regardless of movement mode — a NONE npc is just as
# exposed to the race as a roaming one — which is why this file (and
# check_proximity.mcfunction calling it) is now built for every NPC, not only
# roaming ones as originally documented. Confirmed the hard way: Khaoe shipped
# without it first, and her skin never healed after a failed fetch.
# =============================================================================

execute as @e[type=taterzens:npc,name=Khaoe,limit=1] at @s unless data entity @s TaterzenNPCTag.skin.value run npc edit skin https://minesk.in/36106afb45f343e4adba20d4454a573a

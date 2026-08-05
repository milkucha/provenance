# =============================================================================
# Luminacion — NPC Skin Self-Heal Template
# =============================================================================
# Works around a Taterzens bug: skins are fetched asynchronously from
# mineskin.org (or a player name) on a background thread, decoupled from
# anything else happening to the NPC (e.g. deselecting it). If something
# touches the NPC's profile before that fetch lands, the skin can end up
# permanently unset. Re-running "npc edit skin" is harmless when the skin is
# already set — Taterzens just re-fetches and overwrites it with the same
# result.
#
# WORKFLOW:
#   1. Duplicate as: functions/npcs/<npc_key>/heal_skin.mcfunction
#   2. Fill <display_name>, <npc_key> and <skin_url_or_player> below — use the
#      exact same value as the "npc edit skin" line in this NPC's
#      spawn.mcfunction.
#   3. Called automatically from check_proximity.mcfunction every 100 ticks.
#      No separate registration needed — just make sure check_proximity.mcfunction
#      has the matching call block (see _npcs/templates/check_proximity.mcfunction).
#      Both share the same <npc_key>_heal_cd cooldown counter, reset in
#      check_proximity.mcfunction — don't reset it again here.
#
# Needed for every NPC, regardless of movement mode — the async fetch race
# applies just as much to a stationary (NONE) NPC as a roaming one.
# =============================================================================

execute as @e[type=taterzens:npc,name=<display_name>,limit=1] at @s unless data entity @s TaterzenNPCTag.skin.value run npc edit skin <skin_url_or_player>

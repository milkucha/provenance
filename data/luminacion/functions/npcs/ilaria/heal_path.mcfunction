# =============================================================================
# Luminacion — Iläria Path Self-Heal
# =============================================================================
# Built from _templates/npcs/heal_path.mcfunction. Called every 100 ticks (5s)
# from check_proximity.mcfunction, alongside heal_skin.mcfunction.
#
# Works around the same class of problem as heal_skin.mcfunction, but for
# paths: Taterzens' in-game path editor (/npc edit path) lets a stray
# left-click silently add or clear waypoints, and clearing them leaves a
# stale internal movement restriction behind. functions/npcs/ilaria/
# paths/<path_name>.mcfunction (if one is ever needed) would avoid that
# editor entirely (see _templates/npcs/paths/select_path.mcfunction).
#
# Iläria's movement mode is NONE and she has no path defined, so this file has
# nothing to do — built anyway, since this machinery is now built for every
# NPC regardless of movement mode (see check_proximity.mcfunction's header).
# If she's ever given a path, add a line here for it — one line per path:
#
#   execute if data storage luminacion:npcs {ilaria:{active_path:"<path_name>"}} unless data entity @e[type=taterzens:npc,name="Iläria",limit=1] TaterzenNPCTag.PathTargets[0] run function luminacion:npcs/ilaria/paths/<path_name>
# =============================================================================

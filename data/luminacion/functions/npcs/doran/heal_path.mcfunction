# =============================================================================
# Luminacion — Döran Path Self-Heal
# =============================================================================
# Built from _npcs/templates/heal_path.mcfunction. Called every 100 ticks (5s)
# from check_proximity.mcfunction, alongside heal_skin.mcfunction.
#
# Works around the same class of problem as heal_skin.mcfunction, but for
# paths: Taterzens' in-game path editor (/npc edit path) lets a stray
# left-click silently add or clear waypoints, and clearing them leaves a
# stale internal movement restriction behind. functions/npcs/doran/
# paths/<path_name>.mcfunction avoids that editor entirely (see
# _npcs/templates/paths/select_path.mcfunction). This only re-applies the
# active path if PathTargets has actually gone empty — it doesn't try to
# detect a merely-modified path, to avoid rubber-banding the NPC mid-route
# on a false positive.
#
# No path has been defined for Döran yet, so this file has nothing to
# do. Once functions/npcs/doran/paths/<path_name>.mcfunction exists,
# add a line here for it — one line per path defined for this NPC:
#
#   execute if data storage luminacion:npcs {doran:{active_path:"<path_name>"}} unless data entity @e[type=taterzens:npc,name="Döran",limit=1] TaterzenNPCTag.PathTargets[0] run function luminacion:npcs/doran/paths/<path_name>
# =============================================================================

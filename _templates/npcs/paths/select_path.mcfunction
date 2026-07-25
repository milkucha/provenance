# =============================================================================
# Luminacion — NPC Path Template
# =============================================================================
# Defines ONE named path and makes it this NPC's active route. Replaces the
# in-game "/npc edit path" left-click editor entirely — that editor is what
# causes accidental waypoint changes and Taterzens' stale-restriction bug in
# the first place (a stray left-click adds/removes a node, and clearing nodes
# afterward doesn't clear the internal movement restriction Taterzens pins to
# them). Confirmed instead: "/data merge entity" re-triggers Taterzens' own
# NBT-load logic on a live entity, including its internal restrictTo() call,
# exactly as if the entity had just been freshly loaded — so writing
# PathTargets this way sets the restriction correctly with no editor needed.
#
# WORKFLOW:
#   1. Duplicate as: functions/npcs/<npc_key>/paths/<path_name>.mcfunction
#   2. Fill <display_name>, <path_name> and the waypoint list below (add or
#      remove {x,y,z} entries as needed — two shown here is just an example).
#   3. Add a matching line to functions/npcs/<npc_key>/heal_path.mcfunction
#      (see _templates/npcs/heal_path.mcfunction) so this path self-heals if
#      its waypoints ever get cleared.
#   4. Run as an operator: /function luminacion:npcs/<npc_key>/paths/<path_name>
#      — teleports the NPC to the first waypoint and starts the route.
#
# Switching between multiple paths for the same NPC: just run a different
# paths/<other_name>.mcfunction. The teleport to its first waypoint means
# switching is always clean, regardless of where the NPC currently is.
# =============================================================================

execute as @e[type=taterzens:npc,name=<display_name>,limit=1] at @s run tp @s <x0> <y0> <z0>
data merge entity @e[type=taterzens:npc,name=<display_name>,limit=1] {TaterzenNPCTag:{PathTargets:[{x:<x0>,y:<y0>,z:<z0>},{x:<x1>,y:<y1>,z:<z1>}],CurrentMoveTarget:0}}
execute as @e[type=taterzens:npc,name=<display_name>,limit=1] at @s run npc edit movement PATH

data modify storage luminacion:npcs <npc_key>.active_path set value "<path_name>"

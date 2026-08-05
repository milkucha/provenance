# Luminacion — tick
# Runs every game tick (20/s).

# Roaming NPCs: stop when a player gets within 2 blocks, resume when they leave.
# See _npcs/templates/check_proximity.mcfunction for the per-NPC setup.
function #luminacion:npc_routine_tick

# Gestures and nods: per-entity countdowns, replacing the old global
# "schedule function ... replace" mechanism (see TODO.md "Multi-NPC
# gesture/nod scheduling collision").
function luminacion:npcs/_shared/gesture_tick
function luminacion:npcs/_shared/nod_tick

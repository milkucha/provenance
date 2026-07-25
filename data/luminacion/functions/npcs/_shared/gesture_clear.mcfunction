# =============================================================================
# Luminacion — Shared: Gesture — Clear
# =============================================================================
# Ends whichever gesture is currently active on any NPC: empties the main
# hand (dropping the invisible CustomModelData marker item that the gesture
# resource pack reads) and clears the tracking tag. Selects by tag, not @s —
# "schedule function" loses the calling entity's context by the time this
# fires, same reasoning as nod_up_down_4.mcfunction.
#
# Internal — called only via "schedule function ... <ticks>t replace" from
# the individual gesture_<name>.mcfunction files below. Don't call directly.
#
# Same multi-NPC caveat as the nod system: "replace" scheduling is keyed to
# this function's id globally, not per-entity, so if two NPCs' gestures
# happen to overlap, the later one's schedule call can push out the earlier
# one's clear time by a beat. Harmless here (worst case a gesture holds very
# slightly longer/shorter than its own intended duration) — see
# nod_up_down.mcfunction's docstring for the same tradeoff explained in full.
# =============================================================================

execute as @e[tag=luminacion.gesture_active] run item replace entity @s weapon.mainhand with minecraft:air
tag @e[tag=luminacion.gesture_active] remove luminacion.gesture_active

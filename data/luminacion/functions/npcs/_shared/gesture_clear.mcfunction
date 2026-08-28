# =============================================================================
# Provenance — Shared: Gesture — Clear (internal)
# =============================================================================
# Ends the current NPC's gesture: empties the main hand (dropping the
# invisible CustomModelData marker item that the gesture resource pack
# reads) and clears the tracking tag. Called as
# "execute as <npc> run function ..." from gesture_tick.mcfunction, once per
# tick, only for whichever entity's own luminacion.gest_timer has just
# reached 0 — @s is already scoped to that one NPC, not every currently-
# gesturing NPC (that was the old behavior when this fired off a single
# global "schedule function ... replace" timer shared by every gesture —
# see TODO.md "Multi-NPC gesture/nod scheduling collision").
#
# Internal — called only from gesture_tick.mcfunction. Don't call directly.
# =============================================================================

item replace entity @s weapon.mainhand with minecraft:air
tag @s remove luminacion.gesture_active

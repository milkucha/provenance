# =============================================================================
# Provenance — Shared: Gesture — Wave
# =============================================================================
# Gives the NPC's own main hand an invisible marker item (CustomModelData
# 101), which the gesture resource pack (player.jem/player_slim.jem override
# in the Iris/EMF pipeline) reads to raise and swing the right arm side to
# side. Clears itself automatically after 2.5s (50 ticks): sets
# luminacion.gest_timer to 50, and gesture_tick.mcfunction (called every
# tick from tick.mcfunction) counts it down per-entity, running
# gesture_clear.mcfunction on this NPC alone once it reaches 0. Each NPC's
# hold time is independent of every other NPC's — this replaced an earlier
# "schedule function ... replace" design that used one datapack-wide timer
# for every gesture, which broke as soon as two NPCs gestured within a few
# ticks of each other (see TODO.md "Multi-NPC gesture/nod scheduling
# collision" for the full history).
#
# CALL CONTEXT: must be called with @s = the NPC itself, same as the nod_*
# functions (e.g. "execute as @interlocutor run function ...").
#
# Don't call this (or any other gesture_*.mcfunction) on an NPC that's
# already mid-gesture — same caveat nod_up_down has for re-nodding. Never
# pair a gesture action on the same dialogue state as a nod_up_down action —
# gestures fully own the arm/body pose while active, so a simultaneous nod's
# head rotation writes would fight the gesture's own smoothing (worst case
# for the "laugh" gesture, which also overrides head pitch).
# =============================================================================

tag @s add luminacion.gesture_active
item replace entity @s weapon.mainhand with minecraft:stick{CustomModelData:101}

scoreboard players set @s luminacion.gest_timer 50

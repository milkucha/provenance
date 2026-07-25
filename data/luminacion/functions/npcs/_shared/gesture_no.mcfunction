# =============================================================================
# Luminacion — Shared: Gesture — No
# =============================================================================
# Gives the NPC's own main hand an invisible marker item (CustomModelData
# 108), which the gesture resource pack reads to shake the head side to side
# (`head.ry` oscillates via a new `var.gest_headry` low-pass filter, the
# yaw counterpart to Laugh's existing `var.gest_headrx` pitch override) while
# both arms raise in front of the chest and sweep side to side in sync
# (`ry` oscillates, mirrored between arms) — a "no, no" rejection gesture.
# Clears itself automatically after 2.5s (50t) via the per-entity
# luminacion.gest_timer countdown in gesture_tick.mcfunction — see
# gesture_wave.mcfunction for the full mechanism writeup.
#
# CALL CONTEXT: must be called with @s = the NPC itself, same as the nod_*
# functions (e.g. "execute as @interlocutor run function ...").
#
# Overrides head yaw as well as both arms, so — same as Laugh, which
# overrides head pitch — never pair this action with a `nod_left_right`
# action on the same dialogue state; the head rotation writes would fight.
#
# Don't call this (or any other gesture_*.mcfunction) on an NPC that's
# already mid-gesture.
# =============================================================================

tag @s add luminacion.gesture_active
item replace entity @s weapon.mainhand with minecraft:stick{CustomModelData:108}

scoreboard players set @s luminacion.gest_timer 50

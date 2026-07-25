# =============================================================================
# Luminacion — Shared: Nod Left And Right (beat 4 of 4, internal)
# =============================================================================
# Final continuation of nod_left_right.mcfunction, fired 9 ticks after the
# initial call — do not call directly.
#
# Beat 4: undo beat 3's turn, settle back to baseline yaw, restore
# FORCED_LOOK if it was suspended (see nod_left_right.mcfunction's
# FORCED_LOOK GUARD note) and still applies, and clear the in-progress tag.
# Uses "tp" with a relative yaw delta, not raw NBT — see nod_left_right.mcfunction.
# =============================================================================

execute as @e[tag=luminacion.gesture_nod_lr] at @s run tp @s ~ ~ ~ ~-8 ~
execute as @e[tag=luminacion.gesture_nod_lr,tag=luminacion.paused] run npc edit movement FORCED_LOOK
tag @e[tag=luminacion.gesture_nod_lr] remove luminacion.gesture_nod_lr

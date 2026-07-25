# =============================================================================
# Luminacion — Shared: Nod Left And Right (beat 3 of 4, internal)
# =============================================================================
# Continuation of nod_left_right.mcfunction, fired 6 ticks after the initial
# call — do not call directly.
#
# Beat 3: smaller 8 degree turn, opposite side from beat 1. Uses "tp" with a
# relative yaw delta, not raw NBT — see nod_left_right.mcfunction.
# =============================================================================

execute as @e[tag=luminacion.gesture_nod_lr] at @s run tp @s ~ ~ ~ ~8 ~

schedule function luminacion:npcs/_shared/nod_left_right_4 3t replace

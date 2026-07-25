# =============================================================================
# Luminacion — Shared: Nod Left And Right (beat 2 of 4, internal)
# =============================================================================
# Continuation of nod_left_right.mcfunction, fired 3 ticks later via
# "schedule function" — do not call directly. Runs with no @s context, so it
# re-selects every NPC still tagged mid-shake instead of relying on @s.
#
# Beat 2: undo beat 1's turn, back to baseline yaw. Uses "tp" with a
# relative yaw delta, not raw NBT — see nod_left_right.mcfunction.
# =============================================================================

execute as @e[tag=luminacion.gesture_nod_lr] at @s run tp @s ~ ~ ~ ~15 ~

schedule function luminacion:npcs/_shared/nod_left_right_3 3t replace

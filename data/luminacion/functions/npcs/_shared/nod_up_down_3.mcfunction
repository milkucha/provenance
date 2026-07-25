# =============================================================================
# Luminacion — Shared: Nod Up And Down (beat 3 of 4, internal)
# =============================================================================
# Continuation of nod_up_down.mcfunction, fired 6 ticks after the initial
# call — do not call directly.
#
# Beat 3: smaller 6 degree dip, same direction as beat 1. Uses "tp" with a
# relative pitch delta, not raw NBT — see nod_up_down.mcfunction.
# =============================================================================

execute as @e[tag=luminacion.gesture_nod_ud] at @s run tp @s ~ ~ ~ ~ ~6

schedule function luminacion:npcs/_shared/nod_up_down_4 3t replace

# =============================================================================
# Luminacion — Shared: Nod Up And Down (beat 4 of 4, internal)
# =============================================================================
# Final continuation of nod_up_down.mcfunction, fired 9 ticks after the
# initial call — do not call directly.
#
# Beat 4: undo beat 3's dip, settle back to baseline pitch, restore
# FORCED_LOOK if it was suspended (see nod_up_down.mcfunction's FORCED_LOOK
# GUARD note) and still applies, and clear the in-progress tag. Uses "tp"
# with a relative pitch delta, not raw NBT — see nod_up_down.mcfunction.
# =============================================================================

execute as @e[tag=luminacion.gesture_nod_ud] at @s run tp @s ~ ~ ~ ~ ~-6
execute as @e[tag=luminacion.gesture_nod_ud,tag=luminacion.paused] run npc edit movement FORCED_LOOK
tag @e[tag=luminacion.gesture_nod_ud] remove luminacion.gesture_nod_ud

# =============================================================================
# Luminacion — Shared: Nod Up And Down (beat 2 of 4, internal)
# =============================================================================
# Continuation of nod_up_down.mcfunction, fired 3 ticks later via
# "schedule function" — do not call directly. Runs with no @s context, so it
# re-selects every NPC still tagged mid-nod instead of relying on @s.
#
# Beat 2: undo beat 1's dip, back to baseline pitch. Uses "tp" with a
# relative pitch delta, not raw NBT — see nod_up_down.mcfunction.
# =============================================================================

execute as @e[tag=luminacion.gesture_nod_ud] at @s run tp @s ~ ~ ~ ~ ~-12

schedule function luminacion:npcs/_shared/nod_up_down_3 3t replace

# =============================================================================
# Provenance — Shared: Nod Tick (internal)
# =============================================================================
# Called every tick from tick.mcfunction. Advances every currently-nodding
# NPC's 4-beat sequence (nod_up_down.mcfunction / nod_left_right.mcfunction)
# off its own per-entity luminacion.nod_timer score, rather than the old
# "schedule function ... replace" chain (nod_up_down_2/_3/_4,
# nod_left_right_2/_3/_4 — removed) which shared a single timer datapack-
# wide: a second NPC starting a nod while a first NPC's nod was still in
# progress would silently overwrite the first one's pending beat timing,
# compressing/desyncing both nods. Per-entity scores fix that regardless of
# how many NPCs nod concurrently or how staggered their start times are.
# See TODO.md ("Multi-NPC gesture/nod scheduling collision") for the full
# writeup.
#
# luminacion.nod_timer starts at 9 (set by nod_up_down.mcfunction /
# nod_left_right.mcfunction alongside that function's own beat-1 pose) and
# counts down once per tick; beats 2/3/4 fire at exactly the score values
# that correspond to 3/6/9 ticks having elapsed since the entity's own
# start. Shared between both nod directions since no NPC is ever tagged
# with both luminacion.gesture_nod_ud and luminacion.gesture_nod_lr at
# once (both are gated by the same "don't retrigger a nod already in
# progress" convention).
#
# Internal — called only from tick.mcfunction. Don't call directly.
# =============================================================================

scoreboard players remove @e[tag=luminacion.gesture_nod_ud] luminacion.nod_timer 1
scoreboard players remove @e[tag=luminacion.gesture_nod_lr] luminacion.nod_timer 1

# nod_up_down beats (see nod_up_down.mcfunction for beat 1, applied at trigger time)
execute as @e[tag=luminacion.gesture_nod_ud,scores={luminacion.nod_timer=6}] at @s run tp @s ~ ~ ~ ~ ~-12
execute as @e[tag=luminacion.gesture_nod_ud,scores={luminacion.nod_timer=3}] at @s run tp @s ~ ~ ~ ~ ~6
execute as @e[tag=luminacion.gesture_nod_ud,scores={luminacion.nod_timer=..0}] at @s run function luminacion:npcs/_shared/nod_up_down_clear

# nod_left_right beats (see nod_left_right.mcfunction for beat 1, applied at trigger time)
execute as @e[tag=luminacion.gesture_nod_lr,scores={luminacion.nod_timer=6}] at @s run tp @s ~ ~ ~ ~15 ~
execute as @e[tag=luminacion.gesture_nod_lr,scores={luminacion.nod_timer=3}] at @s run tp @s ~ ~ ~ ~8 ~
execute as @e[tag=luminacion.gesture_nod_lr,scores={luminacion.nod_timer=..0}] at @s run function luminacion:npcs/_shared/nod_left_right_clear

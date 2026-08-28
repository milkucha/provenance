# =============================================================================
# Provenance — Shared: Gesture Tick (internal)
# =============================================================================
# Called every tick from tick.mcfunction. Counts down every currently-active
# gesture's own per-entity luminacion.gest_timer score (set by whichever
# gesture_<name>.mcfunction started it, to that gesture's own hold duration)
# and clears just the entity whose timer has reached 0 — replaces the old
# "schedule function .../gesture_clear <ticks>t replace" call every gesture
# used to make. That was a single timer shared datapack-wide: a second NPC
# starting any gesture would silently overwrite the first NPC's pending
# clear time, and firing it cleared every gesture-tagged NPC at once, not
# just the one actually due. Per-entity scores fix both problems regardless
# of how many NPCs gesture concurrently. See TODO.md ("Multi-NPC
# gesture/nod scheduling collision") for the full writeup.
#
# Internal — called only from tick.mcfunction. Don't call directly.
# =============================================================================

scoreboard players remove @e[tag=luminacion.gesture_active] luminacion.gest_timer 1
execute as @e[tag=luminacion.gesture_active,scores={luminacion.gest_timer=..0}] run function luminacion:npcs/_shared/gesture_clear

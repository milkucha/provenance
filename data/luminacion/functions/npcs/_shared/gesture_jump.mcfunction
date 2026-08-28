# =============================================================================
# Provenance — Shared: Gesture — Jump
# =============================================================================
# Gives the NPC's own main hand an invisible marker item (CustomModelData
# 110), which the gesture resource pack (player.jem/player_slim.jem override
# in the Iris/EMF pipeline) reads to raise the right arm straight overhead
# (victory fist-pump) and bounce the whole body up and down — a Mario
# level-clear-style victory jump. Clears itself after 12t (0.6s) via the
# per-entity luminacion.gest_timer countdown in gesture_tick.mcfunction —
# deliberately much shorter than every other gesture's 50t (2.5s): the
# jump's own one-shot hop (var.gest_jumpclock in the .jem) finishes in ~7
# ticks, and the arm is meant to drop the instant landing happens rather
# than stay pumped for a held victory pose, so the marker item (and with it
# the arm pose) is pulled well before 2.5s would elapse. Because the timer
# is per-entity (see gesture_wave.mcfunction for the full mechanism
# writeup), this shorter hold no longer risks colliding with any other
# NPC's differently-timed gesture the way it did under the old shared
# "schedule ... replace" design — that was the original motivation for this
# whole per-entity-timer system (see TODO.md "Multi-NPC gesture/nod
# scheduling collision" for the history).
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
item replace entity @s weapon.mainhand with minecraft:stick{CustomModelData:110}

scoreboard players set @s luminacion.gest_timer 12

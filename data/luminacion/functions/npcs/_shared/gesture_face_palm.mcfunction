# =============================================================================
# Provenance — Shared: Gesture — Face-palm
# =============================================================================
# Gives the NPC's own main hand an invisible marker item (CustomModelData
# 109), which the gesture resource pack reads to raise the right arm to
# head height and swing it inward across the face — `ry` at -20°, pulled
# back from an initial -40° after in-game testing showed the hand clipping
# into the head mesh; this is a shallower inward swing than Scratch-head's
# outward one, since this one still has to reach the face rather than the
# side of the head, just not so deep that the hand overlaps it — while the
# head pitches down and stays there, statically
# (`var.gest_headrx`, same variable Laugh already overrides for its own
# pitch) — with a slow, subtle side-to-side shake layered on top instead
# (`var.gest_headry`, the yaw variable "No" introduced), `sin(age*0.6)`,
# read as a quiet disapproving head-shake rather than a nod. Own slower
# `var.gest_rate` of 3 (vs. the default 6) so the whole pose eases in more
# smoothly instead of snapping into place. Right hand only for now; a
# left-hand mirror (CustomModelData 209, following the established +100
# convention) is planned but not yet built. Clears itself automatically
# after 2.5s (50t) via the per-entity luminacion.gest_timer countdown in
# gesture_tick.mcfunction — see gesture_wave.mcfunction for the full
# mechanism writeup.
#
# CALL CONTEXT: must be called with @s = the NPC itself, same as the nod_*
# functions (e.g. "execute as @interlocutor run function ...").
#
# Overrides head pitch, so — same as Laugh — never pair this action with a
# `nod_up_down` action on the same dialogue state; the head rotation writes
# would fight.
#
# Don't call this (or any other gesture_*.mcfunction) on an NPC that's
# already mid-gesture.
# =============================================================================

tag @s add luminacion.gesture_active
item replace entity @s weapon.mainhand with minecraft:stick{CustomModelData:109}

scoreboard players set @s luminacion.gest_timer 50

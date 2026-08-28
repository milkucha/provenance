# =============================================================================
# Provenance — Shared: Gesture — Wave (Left)
# =============================================================================
# Gives the NPC's own main hand an invisible marker item (CustomModelData
# 201 — mirror-variant numbering is 100 + the base gesture's number, so
# wave's 101 becomes 201), which the gesture resource pack
# (player.jem/player_slim.jem override in the Iris/EMF pipeline) reads to
# raise and swing the left arm side to side — a mirror of
# gesture_wave.mcfunction's right-arm pose. Clears itself automatically
# after 2.5s (50t) via the per-entity luminacion.gest_timer countdown in
# gesture_tick.mcfunction — see gesture_wave.mcfunction for the full
# mechanism writeup.
#
# CALL CONTEXT / caveats: see gesture_wave.mcfunction — identical pattern.
# =============================================================================

tag @s add luminacion.gesture_active
item replace entity @s weapon.mainhand with minecraft:stick{CustomModelData:201}

scoreboard players set @s luminacion.gest_timer 50

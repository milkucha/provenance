# =============================================================================
# Provenance — Shared: Gesture — Scratch Head (Left)
# =============================================================================
# Gives the NPC's own main hand an invisible marker item (CustomModelData
# 206 — mirror-variant numbering is 100 + the base gesture's number, so
# scratch-head's 106 becomes 206), which the gesture resource pack reads to
# raise the left arm toward the head with the same slow, bursty scratching
# wiggle as gesture_scratch_head.mcfunction, mirrored. Clears itself
# automatically after 3s (60t) via the per-entity luminacion.gest_timer
# countdown in gesture_tick.mcfunction — long enough to show at least one
# full scratch-burst-then-pause cycle. See gesture_wave.mcfunction for the
# full mechanism writeup.
#
# CALL CONTEXT / caveats: see gesture_wave.mcfunction — identical pattern.
# =============================================================================

tag @s add luminacion.gesture_active
item replace entity @s weapon.mainhand with minecraft:stick{CustomModelData:206}

scoreboard players set @s luminacion.gest_timer 60

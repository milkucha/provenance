# =============================================================================
# Luminacion — Shared: Gesture — Scratch Head (Left)
# =============================================================================
# Gives the NPC's own main hand an invisible marker item (CustomModelData
# 206 — mirror-variant numbering is 100 + the base gesture's number, so
# scratch-head's 106 becomes 206), which the gesture resource pack reads to
# raise the left arm toward the head with the same slow, bursty scratching
# wiggle as gesture_scratch_head.mcfunction, mirrored. Clears itself
# automatically after 3s via gesture_clear.mcfunction — long enough to show
# at least one full scratch-burst-then-pause cycle.
#
# CALL CONTEXT / caveats: see gesture_wave.mcfunction — identical pattern.
# =============================================================================

tag @s add luminacion.gesture_active
item replace entity @s weapon.mainhand with minecraft:stick{CustomModelData:206}

schedule function luminacion:npcs/_shared/gesture_clear 60t replace

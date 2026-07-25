# =============================================================================
# Luminacion — Shared: Gesture — Point (Left)
# =============================================================================
# Gives the NPC's own main hand an invisible marker item (CustomModelData
# 202 — mirror-variant numbering is 100 + the base gesture's number, so
# point's 102 becomes 202), which the gesture resource pack reads to extend
# the left arm forward, rigid — a mirror of gesture_point.mcfunction's
# right-arm pose. Clears itself automatically after 1.5s via
# gesture_clear.mcfunction.
#
# CALL CONTEXT / caveats: see gesture_wave.mcfunction — identical pattern.
# =============================================================================

tag @s add luminacion.gesture_active
item replace entity @s weapon.mainhand with minecraft:stick{CustomModelData:202}

schedule function luminacion:npcs/_shared/gesture_clear 30t replace

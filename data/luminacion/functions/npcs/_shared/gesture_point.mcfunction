# =============================================================================
# Luminacion — Shared: Gesture — Point
# =============================================================================
# Gives the NPC's own main hand an invisible marker item (CustomModelData
# 102), which the gesture resource pack reads to extend the right arm
# forward, rigid. Clears itself automatically after 1.5s via
# gesture_clear.mcfunction.
#
# CALL CONTEXT / caveats: see gesture_wave.mcfunction — identical pattern.
# =============================================================================

tag @s add luminacion.gesture_active
item replace entity @s weapon.mainhand with minecraft:stick{CustomModelData:102}

schedule function luminacion:npcs/_shared/gesture_clear 30t replace

# =============================================================================
# Luminacion — Shared: Gesture — Palms Up
# =============================================================================
# Gives the NPC's own main hand an invisible marker item (CustomModelData
# 105), which the gesture resource pack reads to bring both arms in and open
# (openness / reassurance — originally prototyped as "cross-arms" but reads
# visually as palms-up instead, hence the name). Clears itself automatically
# after 1.5s via gesture_clear.mcfunction.
#
# CALL CONTEXT / caveats: see gesture_wave.mcfunction — identical pattern.
# =============================================================================

tag @s add luminacion.gesture_active
item replace entity @s weapon.mainhand with minecraft:stick{CustomModelData:105}

schedule function luminacion:npcs/_shared/gesture_clear 30t replace

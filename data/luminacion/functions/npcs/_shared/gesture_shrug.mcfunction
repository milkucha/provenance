# =============================================================================
# Luminacion — Shared: Gesture — Shrug
# =============================================================================
# Gives the NPC's own main hand an invisible marker item (CustomModelData
# 104), which the gesture resource pack reads to cycle both arms up to
# shoulder height and back down (uncertainty). Clears itself automatically
# after 2.5s via gesture_clear.mcfunction.
#
# CALL CONTEXT / caveats: see gesture_wave.mcfunction — identical pattern.
# =============================================================================

tag @s add luminacion.gesture_active
item replace entity @s weapon.mainhand with minecraft:stick{CustomModelData:104}

schedule function luminacion:npcs/_shared/gesture_clear 50t replace

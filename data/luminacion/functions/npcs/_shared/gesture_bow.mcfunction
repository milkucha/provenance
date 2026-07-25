# =============================================================================
# Luminacion — Shared: Gesture — Bow
# =============================================================================
# Gives the NPC's own main hand an invisible marker item (CustomModelData
# 103), which the gesture resource pack reads to lean the torso forward.
# Clears itself automatically after 2s via gesture_clear.mcfunction.
#
# CALL CONTEXT / caveats: see gesture_wave.mcfunction — identical pattern.
# =============================================================================

tag @s add luminacion.gesture_active
item replace entity @s weapon.mainhand with minecraft:stick{CustomModelData:103}

schedule function luminacion:npcs/_shared/gesture_clear 40t replace

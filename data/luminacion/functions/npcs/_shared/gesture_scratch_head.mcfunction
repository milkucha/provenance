# =============================================================================
# Luminacion — Shared: Gesture — Scratch Head
# =============================================================================
# Gives the NPC's own main hand an invisible marker item (CustomModelData
# 106), which the gesture resource pack reads to raise the right arm toward
# the head with a slow, bursty scratching wiggle (pondering / mild
# confusion). Clears itself automatically after 3s via
# gesture_clear.mcfunction — long enough to show at least one full
# scratch-burst-then-pause cycle.
#
# CALL CONTEXT / caveats: see gesture_wave.mcfunction — identical pattern.
# =============================================================================

tag @s add luminacion.gesture_active
item replace entity @s weapon.mainhand with minecraft:stick{CustomModelData:106}

schedule function luminacion:npcs/_shared/gesture_clear 60t replace

# =============================================================================
# Luminacion — Shared: Gesture — Bow
# =============================================================================
# Gives the NPC's own main hand an invisible marker item (CustomModelData
# 103), which the gesture resource pack reads to lean the torso forward.
# Clears itself automatically after 2s (40t) via the per-entity
# luminacion.gest_timer countdown in gesture_tick.mcfunction — see
# gesture_wave.mcfunction for the full mechanism writeup.
#
# CALL CONTEXT / caveats: see gesture_wave.mcfunction — identical pattern.
# =============================================================================

tag @s add luminacion.gesture_active
item replace entity @s weapon.mainhand with minecraft:stick{CustomModelData:103}

scoreboard players set @s luminacion.gest_timer 40

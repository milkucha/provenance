# =============================================================================
# Luminacion — Shared: Gesture — Laugh
# =============================================================================
# Gives the NPC's own main hand an invisible marker item (CustomModelData
# 107), which the gesture resource pack reads to lean the torso back, tip
# the head down, raise the right arm and rest the left hand on the belly —
# all bouncing on a shared slow rhythm. Overrides head pitch directly, so
# the NPC briefly stops tracking the player's look direction while this
# plays (reads as natural for a laugh — looking away/down mid-laugh).
# Clears itself automatically after 3s (60t) via the per-entity
# luminacion.gest_timer countdown in gesture_tick.mcfunction — see
# gesture_wave.mcfunction for the full mechanism writeup.
#
# CALL CONTEXT / caveats: see gesture_wave.mcfunction — identical pattern.
# =============================================================================

tag @s add luminacion.gesture_active
item replace entity @s weapon.mainhand with minecraft:stick{CustomModelData:107}

scoreboard players set @s luminacion.gest_timer 60

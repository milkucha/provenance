# =============================================================================
# Luminacion — Shared: Gesture — Shrug
# =============================================================================
# Gives the NPC's own main hand an invisible marker item (CustomModelData
# 104), which the gesture resource pack reads to cycle both arms up to
# shoulder height and back down (uncertainty). Clears itself automatically
# after 2.5s (50t) via the per-entity luminacion.gest_timer countdown in
# gesture_tick.mcfunction — see gesture_wave.mcfunction for the full
# mechanism writeup.
#
# CALL CONTEXT / caveats: see gesture_wave.mcfunction — identical pattern.
# =============================================================================

tag @s add luminacion.gesture_active
item replace entity @s weapon.mainhand with minecraft:stick{CustomModelData:104}

scoreboard players set @s luminacion.gest_timer 50

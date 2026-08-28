# =============================================================================
# Provenance — Shared: Gesture — Palms Up
# =============================================================================
# Gives the NPC's own main hand an invisible marker item (CustomModelData
# 105), which the gesture resource pack reads to bring both arms in and open
# (openness / reassurance — originally prototyped as "cross-arms" but reads
# visually as palms-up instead, hence the name). Clears itself automatically
# after 1.5s (30t) via the per-entity luminacion.gest_timer countdown in
# gesture_tick.mcfunction — see gesture_wave.mcfunction for the full
# mechanism writeup.
#
# CALL CONTEXT / caveats: see gesture_wave.mcfunction — identical pattern.
# =============================================================================

tag @s add luminacion.gesture_active
item replace entity @s weapon.mainhand with minecraft:stick{CustomModelData:105}

scoreboard players set @s luminacion.gest_timer 30

# =============================================================================
# Provenance — Shared: Gesture — Point
# =============================================================================
# Gives the NPC's own main hand an invisible marker item (CustomModelData
# 102), which the gesture resource pack reads to extend the right arm
# forward, rigid. Clears itself automatically after 1.5s (30t) via the
# per-entity luminacion.gest_timer countdown in gesture_tick.mcfunction —
# see gesture_wave.mcfunction for the full mechanism writeup.
#
# CALL CONTEXT / caveats: see gesture_wave.mcfunction — identical pattern.
# =============================================================================

tag @s add luminacion.gesture_active
item replace entity @s weapon.mainhand with minecraft:stick{CustomModelData:102}

scoreboard players set @s luminacion.gest_timer 30

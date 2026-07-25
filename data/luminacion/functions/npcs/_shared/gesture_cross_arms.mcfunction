# =============================================================================
# Luminacion — Shared: Gesture — Cross Arms
# =============================================================================
# Gives the NPC's own main hand an invisible marker item (CustomModelData
# 111), which the gesture resource pack (player.jem/player_slim.jem override
# in the Iris/EMF pipeline) reads to raise both arms, swing them in across the
# chest, and bend both elbows via the right_forearm/left_forearm bones
# (defensiveness / stubbornness) — the first gesture to use the elbow joint,
# see the README "Elbow joint" writeup for how it works. Clears itself
# automatically after 2.5s (50t) via the per-entity luminacion.gest_timer
# countdown in gesture_tick.mcfunction — see gesture_wave.mcfunction for the
# full mechanism writeup.
#
# CALL CONTEXT / caveats: see gesture_wave.mcfunction — identical pattern.
# =============================================================================

tag @s add luminacion.gesture_active
item replace entity @s weapon.mainhand with minecraft:stick{CustomModelData:111}

scoreboard players set @s luminacion.gest_timer 50

# =============================================================================
# Provenance — Shared: Gesture — Flex Arm
# =============================================================================
# Gives the NPC's own main hand an invisible marker item (CustomModelData
# 112), which the gesture resource pack (player.jem/player_slim.jem override
# in the Iris/EMF pipeline) reads to raise the right arm out to the side and
# then, once var.gest_flexclock (a per-entity stopwatch, same pattern as
# gesture_jump's var.gest_jumpclock) passes 0.9s, bend the elbow via the
# right_forearm bone (a modest 70°, pulled back from a stronger initial 90°
# after in-game testing) to bring the fist up near the shoulder — a playful
# bicep-flex / showing-off pose, sequenced (raise, then flex) rather than
# simultaneous. Own slower var.gest_rate of 3 (vs. the default 6). Right arm
# only, no mirror variant. Uses the elbow joint — see the README "Elbow
# joint" writeup. Clears itself automatically
# after 2.5s (50t) via the per-entity luminacion.gest_timer countdown in
# gesture_tick.mcfunction — see gesture_wave.mcfunction for the full
# mechanism writeup.
#
# CALL CONTEXT / caveats: see gesture_wave.mcfunction — identical pattern.
# =============================================================================

tag @s add luminacion.gesture_active
item replace entity @s weapon.mainhand with minecraft:stick{CustomModelData:112}

scoreboard players set @s luminacion.gest_timer 50

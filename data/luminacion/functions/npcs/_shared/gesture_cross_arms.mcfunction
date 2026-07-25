# =============================================================================
# Luminacion — Shared: Gesture — Cross Arms
# =============================================================================
# Gives the NPC's own main hand an invisible marker item (CustomModelData
# 111), which the gesture resource pack (player.jem/player_slim.jem override
# in the Iris/EMF pipeline) reads to raise both arms and swing them in across
# the chest (defensiveness / stubbornness) — shoulder-only, straight arms;
# see TODO.md for why the elbow-bend version was reverted. Clears itself
# automatically after 2.5s via gesture_clear.mcfunction.
#
# CALL CONTEXT / caveats: see gesture_wave.mcfunction — identical pattern.
# =============================================================================

tag @s add luminacion.gesture_active
item replace entity @s weapon.mainhand with minecraft:stick{CustomModelData:111}

schedule function luminacion:npcs/_shared/gesture_clear 50t replace

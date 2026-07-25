# =============================================================================
# Luminacion — Shared: Nod Left And Right — Clear (internal)
# =============================================================================
# Final beat of nod_left_right.mcfunction's 4-beat sequence, run once per
# entity by nod_tick.mcfunction when that entity's own luminacion.nod_timer
# counts down to 0 — called as "execute as <npc> at <npc> run function ...",
# so @s is already scoped to the one NPC whose nod just finished, not every
# currently-nodding NPC (that was the old behavior when this fired off a
# single global "schedule function ... replace" timer — see TODO.md
# "Multi-NPC gesture/nod scheduling collision").
#
# Beat 4: undo beat 3's turn, settle back to baseline yaw, restore
# FORCED_LOOK if it was suspended (see nod_left_right.mcfunction's
# FORCED_LOOK GUARD note) and still applies, and clear the in-progress tag.
# Uses "tp" with a relative yaw delta, not raw NBT — see
# nod_left_right.mcfunction.
#
# Internal — called only from nod_tick.mcfunction. Don't call directly.
# =============================================================================

tp @s ~ ~ ~ ~-8 ~
execute if entity @s[tag=luminacion.paused] run npc edit movement FORCED_LOOK
tag @s remove luminacion.gesture_nod_lr

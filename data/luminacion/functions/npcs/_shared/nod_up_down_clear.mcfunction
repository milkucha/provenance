# =============================================================================
# Provenance — Shared: Nod Up And Down — Clear (internal)
# =============================================================================
# Final beat of nod_up_down.mcfunction's 4-beat sequence, run once per
# entity by nod_tick.mcfunction when that entity's own luminacion.nod_timer
# counts down to 0 — called as "execute as <npc> at <npc> run function ...",
# so @s is already scoped to the one NPC whose nod just finished, not every
# currently-nodding NPC (that was the old behavior when this fired off a
# single global "schedule function ... replace" timer — see TODO.md
# "Multi-NPC gesture/nod scheduling collision").
#
# Beat 4: undo beat 3's dip, settle back to baseline pitch, restore
# FORCED_LOOK if it was suspended (see nod_up_down.mcfunction's FORCED_LOOK
# GUARD note) and still applies, and clear the in-progress tag. Uses "tp"
# with a relative pitch delta, not raw NBT — see nod_up_down.mcfunction.
#
# Internal — called only from nod_tick.mcfunction. Don't call directly.
# =============================================================================

tp @s ~ ~ ~ ~ ~-6
execute if entity @s[tag=luminacion.paused] run npc edit movement FORCED_LOOK
tag @s remove luminacion.gesture_nod_ud

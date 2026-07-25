# =============================================================================
# Luminacion — Shared: Nod Up And Down ("yes" gesture)
# =============================================================================
# Plays a short two-beat downward nod (dip, return, smaller dip, return) that
# decays back to whatever pitch the NPC already had — a prior look_up/
# look_down pose is preserved, not reset to level. Takes ~9 ticks (0.45s),
# advanced via "schedule function". The continuation beats live in
# nod_up_down_2/_3/_4.mcfunction — internal, don't call those directly.
#
# CALL CONTEXT: must be called with @s = the NPC itself (from a Taterzens
# right-click/blabber command action, or "execute as <npc> run function ...").
# Safe to trigger on multiple NPCs at once: the baseline pitch is stored in
# the "@s" scoreboard slot, i.e. keyed to each entity's own UUID, and the
# continuation beats re-select every NPC currently mid-nod via a tag rather
# than a hardcoded name — no cross-NPC interference.
#
# Don't retrigger this on an NPC that's already mid-nod (or mid look_up/
# look_down change) — the queued continuation beats will stomp on it.
#
# FORCED_LOOK GUARD: if the NPC is paused (tagged luminacion.paused, set by
# pause_routine.mcfunction), Taterzens' FORCED_LOOK movement mode rewrites
# this same rotation every tick to keep facing the player. Left alone, that
# fights our scheduled writes tick-for-tick. So movement is forced to NONE
# for the gesture's ~9-tick duration and restored by nod_up_down_4.mcfunction
# once it's done.
#
# WHY "tp" AND NOT "data modify entity ... Rotation": this NPC isn't a real
# player — it's a Mob that spoofs a player-join packet so clients render it
# with the player-skin pipeline (confirmed by decompiling TaterzenNPC.class).
# Writing straight to the Rotation NBT array bypasses Minecraft's normal
# rotation packet pipeline, so the fake-player render never gets a proper
# incremental update — it snaps the whole model instead of turning just the
# head. "tp <npc> ~ ~ ~ <yaw> <pitch>" (as used in hangar_look_tick.mcfunction,
# confirmed working head-only there) goes through the real pipeline, so beats
# below use relative tp rotation deltas instead. No baseline capture needed
# either — relative deltas that sum to zero across all four beats naturally
# return to whatever rotation the NPC started at.
# =============================================================================

tag @s add luminacion.gesture_nod_ud

# Suspend FORCED_LOOK for the duration of the gesture so it can't fight these writes.
execute if entity @s[tag=luminacion.paused] run npc edit movement NONE

# Beat 1: dip down 12 degrees from current pitch.
execute at @s run tp @s ~ ~ ~ ~ ~12

schedule function luminacion:npcs/_shared/nod_up_down_2 3t replace

# =============================================================================
# Luminacion — Shared: Look Down
# =============================================================================
# Tilts the NPC's head down and holds it there (a pose, not an animation)
# until something else changes Rotation[1] — another gesture, or Taterzens'
# own FORCED_LOOK movement mode re-aiming the head at the nearest player.
#
# CALL CONTEXT: must be called with @s = the NPC itself (from a Taterzens
# right-click/blabber command action, or "execute as <npc> run function ...").
# Only holds while movement mode is NONE — FORCED_LOOK overrides head
# rotation every tick and will fight this.
#
# Uses "tp" with an absolute pitch, not "data modify entity ... Rotation" —
# this NPC is a Mob spoofing a player-join packet for its render (confirmed
# by decompiling TaterzenNPC.class), and writing straight to the Rotation
# NBT array skips Minecraft's normal rotation packet pipeline, causing the
# fake-player render to visibly snap instead of turning just the head. "tp
# <npc> ~ ~ ~ <yaw> <pitch>" (as used in hangar_look_tick.mcfunction,
# confirmed working head-only there) goes through the real pipeline.
# =============================================================================

execute at @s run tp @s ~ ~ ~ ~ 30

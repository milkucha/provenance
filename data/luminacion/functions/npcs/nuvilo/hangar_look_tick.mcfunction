# =============================================================================
# Luminacion — Nuvilo/Nerkeli Hangar Mutual Look
# =============================================================================
# Keeps Nuvilo and Nerkeli facing each other continuously while both are in
# their "hangar" state — runs every tick via #luminacion:npc_routine_tick,
# but the two "if data storage" checks make it a cheap no-op unless both are
# actually marked "hangar", so this only does anything during that scene.
#
# Uses /execute's own "facing entity ... eyes" (not /teleport's — that form
# doesn't take a trailing anchor argument, confirmed in-game) to compute the
# rotation, then copies it onto each NPC via "tp <npc> ~ ~ ~ ~ ~". A second
# tp per NPC forcibly re-levels the pitch afterward — Taterzens' NPC entity
# doesn't report eye height correctly to vanilla's facing calculation, which
# otherwise pitches them both sharply upward. No "as"/"@s" anywhere — that
# combination failed to parse when chained with "facing ... run tp"; naming
# each NPC explicitly via selector instead is what actually works.
#
# IMPORTANT: every "tp ... ~ ~ ~ ..." below needs its own "at <that NPC>"
# immediately before it. "~ ~ ~" is relative to the execution position
# context, which does NOT carry over between separate top-level lines in a
# .mcfunction file — without "at" re-establishing it, it defaults to wherever
# this tick-tag invocation is anchored (effectively world origin), not the
# NPC's actual position. Got this wrong on the pitch-reset lines the first
# time and it teleported both NPCs toward world spawn every tick. Don't drop
# "at" from any of these four lines.
#
# GESTURE GUARD: each selector below excludes NPCs tagged luminacion.gesture_
# nod_ud/nod_lr (see functions/npcs/_shared/nod_up_down.mcfunction and
# nod_left_right.mcfunction). Hangar NPCs never get FORCED_LOOK/paused (see
# states/hangar.mcfunction — "no routine to pause"), so nod_up_down's own
# FORCED_LOOK guard never triggers for them; without this guard here too,
# this function's own per-tick re-facing would immediately overwrite a nod
# gesture's rotation on the very next tick, making it invisible.
# =============================================================================

execute if data storage luminacion:npcs {nuvilo:{active_state:"hangar"}} if data storage luminacion:npcs {nerkeli:{active_state:"hangar"}} at @e[type=taterzens:npc,name=Nuvilo,limit=1,tag=!luminacion.gesture_nod_ud,tag=!luminacion.gesture_nod_lr] facing entity @e[type=taterzens:npc,name=Nerkeli,limit=1] eyes run tp @e[type=taterzens:npc,name=Nuvilo,limit=1,tag=!luminacion.gesture_nod_ud,tag=!luminacion.gesture_nod_lr] ~ ~ ~ ~ ~
execute if data storage luminacion:npcs {nuvilo:{active_state:"hangar"}} if data storage luminacion:npcs {nerkeli:{active_state:"hangar"}} at @e[type=taterzens:npc,name=Nuvilo,limit=1,tag=!luminacion.gesture_nod_ud,tag=!luminacion.gesture_nod_lr] run tp @e[type=taterzens:npc,name=Nuvilo,limit=1,tag=!luminacion.gesture_nod_ud,tag=!luminacion.gesture_nod_lr] ~ ~ ~ ~ 0

execute if data storage luminacion:npcs {nuvilo:{active_state:"hangar"}} if data storage luminacion:npcs {nerkeli:{active_state:"hangar"}} at @e[type=taterzens:npc,name=Nerkeli,limit=1,tag=!luminacion.gesture_nod_ud,tag=!luminacion.gesture_nod_lr] facing entity @e[type=taterzens:npc,name=Nuvilo,limit=1] eyes run tp @e[type=taterzens:npc,name=Nerkeli,limit=1,tag=!luminacion.gesture_nod_ud,tag=!luminacion.gesture_nod_lr] ~ ~ ~ ~ ~
execute if data storage luminacion:npcs {nuvilo:{active_state:"hangar"}} if data storage luminacion:npcs {nerkeli:{active_state:"hangar"}} at @e[type=taterzens:npc,name=Nerkeli,limit=1,tag=!luminacion.gesture_nod_ud,tag=!luminacion.gesture_nod_lr] run tp @e[type=taterzens:npc,name=Nerkeli,limit=1,tag=!luminacion.gesture_nod_ud,tag=!luminacion.gesture_nod_lr] ~ ~ ~ ~ 0

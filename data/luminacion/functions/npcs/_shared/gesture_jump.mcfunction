# =============================================================================
# Luminacion — Shared: Gesture — Jump
# =============================================================================
# Gives the NPC's own main hand an invisible marker item (CustomModelData
# 110), which the gesture resource pack (player.jem/player_slim.jem override
# in the Iris/EMF pipeline) reads to raise the right arm straight overhead
# (victory fist-pump) and bounce the whole body up and down — a Mario
# level-clear-style victory jump. Clears itself after 12t (0.6s) via
# gesture_clear.mcfunction — deliberately much shorter than every other
# gesture's 50t (2.5s): the jump's own one-shot hop (var.gest_jumpclock in
# the .jem) finishes in ~7 ticks, and the arm is meant to drop the instant
# landing happens rather than stay pumped for a held victory pose, so the
# marker item (and with it the arm pose) is pulled well before 2.5s would
# elapse. Since gesture_clear's "schedule ... replace" is a single global
# timer shared across every gesture/NPC (see gesture_clear.mcfunction's own
# docstring), if this gesture's call happens to overlap another NPC's
# longer-held gesture in the same tick window, the later schedule call wins
# and can cut the earlier gesture's hold short (or stretch this one out) by
# a beat — acceptable here given how rarely two NPCs gesture in the same
# instant, but worth knowing if a gesture is ever seen holding oddly long or
# cutting off early.
#
# CALL CONTEXT: must be called with @s = the NPC itself, same as the nod_*
# functions (e.g. "execute as @interlocutor run function ...").
#
# Don't call this (or any other gesture_*.mcfunction) on an NPC that's
# already mid-gesture — same caveat nod_up_down has for re-nodding. Never
# pair a gesture action on the same dialogue state as a nod_up_down action —
# gestures fully own the arm/body pose while active, so a simultaneous nod's
# head rotation writes would fight the gesture's own smoothing (worst case
# for the "laugh" gesture, which also overrides head pitch).
# =============================================================================

tag @s add luminacion.gesture_active
item replace entity @s weapon.mainhand with minecraft:stick{CustomModelData:110}

schedule function luminacion:npcs/_shared/gesture_clear 12t replace

# =============================================================================
# Provenance — Admin: Gesture Demo (step)
# =============================================================================
# Fires whichever gesture corresponds to the current gesture_demo/
# luminacion.int counter value on the nearest Taterzen, then advances the
# counter. The tail end also tries to reschedule itself 60 ticks later via
# `schedule function`, so the whole sequence was meant to auto-play from a
# single call to gesture_demo_all.mcfunction — but that self-reschedule is
# known broken (2026-07-25, see TODO.md), silently doing nothing even when
# tested standalone with no execute/score wrapper at all; root cause
# unconfirmed. The gesture-selection branches and counter increment above
# it both work correctly on their own, though, so until the reschedule is
# fixed, call this function directly and repeatedly (once per gesture you
# want to see) rather than expecting it to play through automatically.
# =============================================================================

execute if score gesture_demo luminacion.int matches 0 run execute as @e[type=taterzens:npc,sort=nearest,limit=1] run function luminacion:npcs/_shared/gesture_wave
execute if score gesture_demo luminacion.int matches 1 run execute as @e[type=taterzens:npc,sort=nearest,limit=1] run function luminacion:npcs/_shared/gesture_wave_left
execute if score gesture_demo luminacion.int matches 2 run execute as @e[type=taterzens:npc,sort=nearest,limit=1] run function luminacion:npcs/_shared/gesture_point
execute if score gesture_demo luminacion.int matches 3 run execute as @e[type=taterzens:npc,sort=nearest,limit=1] run function luminacion:npcs/_shared/gesture_point_left
execute if score gesture_demo luminacion.int matches 4 run execute as @e[type=taterzens:npc,sort=nearest,limit=1] run function luminacion:npcs/_shared/gesture_bow
execute if score gesture_demo luminacion.int matches 5 run execute as @e[type=taterzens:npc,sort=nearest,limit=1] run function luminacion:npcs/_shared/gesture_shrug
execute if score gesture_demo luminacion.int matches 6 run execute as @e[type=taterzens:npc,sort=nearest,limit=1] run function luminacion:npcs/_shared/gesture_palms_up
execute if score gesture_demo luminacion.int matches 7 run execute as @e[type=taterzens:npc,sort=nearest,limit=1] run function luminacion:npcs/_shared/gesture_scratch_head
execute if score gesture_demo luminacion.int matches 8 run execute as @e[type=taterzens:npc,sort=nearest,limit=1] run function luminacion:npcs/_shared/gesture_scratch_head_left
execute if score gesture_demo luminacion.int matches 9 run execute as @e[type=taterzens:npc,sort=nearest,limit=1] run function luminacion:npcs/_shared/gesture_laugh
execute if score gesture_demo luminacion.int matches 10 run execute as @e[type=taterzens:npc,sort=nearest,limit=1] run function luminacion:npcs/_shared/gesture_no
execute if score gesture_demo luminacion.int matches 11 run execute as @e[type=taterzens:npc,sort=nearest,limit=1] run function luminacion:npcs/_shared/gesture_face_palm
execute if score gesture_demo luminacion.int matches 12 run execute as @e[type=taterzens:npc,sort=nearest,limit=1] run function luminacion:npcs/_shared/gesture_cross_arms
execute if score gesture_demo luminacion.int matches 13 run execute as @e[type=taterzens:npc,sort=nearest,limit=1] run function luminacion:npcs/_shared/gesture_jump
execute if score gesture_demo luminacion.int matches 14 run execute as @e[type=taterzens:npc,sort=nearest,limit=1] run function luminacion:npcs/_shared/gesture_flex_arm

scoreboard players add gesture_demo luminacion.int 1
execute if score gesture_demo luminacion.int matches ..14 run schedule function luminacion:admin/gesture_demo_step 60t replace

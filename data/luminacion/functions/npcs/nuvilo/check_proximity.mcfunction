# =============================================================================
# Luminacion — Nuvilo Proximity Check
# =============================================================================
# Built from the multi_state_npc pattern (see _npcs/actions/registry.json →
# _action_templates.multi_state_npc). Runs once per tick via
# #luminacion:npc_routine_tick (see functions/tick.mcfunction).
#
# Nuvilo has two states (see functions/npcs/nuvilo/states/): only "roaming"
# has an actual routine to pause/resume around a conversation, so the
# pause/resume dance and the path self-heal only run while his active_state
# is "roaming". In "hangar" state (movement NONE) there's nothing to pause.
# =============================================================================

# A player got within 2 blocks while roaming: stop the routine and become interactable.
execute if data storage luminacion:npcs {nuvilo:{active_state:"roaming"}} as @e[type=taterzens:npc,name=Nuvilo,limit=1,tag=!luminacion.paused] at @s if entity @a[distance=..2] run function luminacion:npcs/_shared/pause_routine

# No player within 6 blocks anymore: resume the routine. Widened from 2 to 6 — a
# click from beyond 2 blocks (trivial in creative, 6-block reach) would otherwise
# undo the pause on the very next tick while the dialog is still open, since
# Taterzens has no interact-range override on top of plain vanilla reach. Confirmed
# in-game via Döran, 2026-07-25 — see _npcs/actions/registry.json →
# _action_templates.routine_pause_resume for the full writeup. Keep this wider than
# the 2-block pause trigger above.
execute if data storage luminacion:npcs {nuvilo:{active_state:"roaming"}} as @e[type=taterzens:npc,name=Nuvilo,limit=1,tag=luminacion.paused] at @s unless entity @a[distance=..6] run function luminacion:npcs/nuvilo/resume_routine

# Self-heal: skin regardless of state (correctness doesn't depend on movement
# mode); path only while roaming (nothing to heal in hangar state).
scoreboard players add nuvilo_heal_cd luminacion.int 1
execute if score nuvilo_heal_cd luminacion.int matches 100.. run function luminacion:npcs/nuvilo/heal_skin
execute if data storage luminacion:npcs {nuvilo:{active_state:"roaming"}} if score nuvilo_heal_cd luminacion.int matches 100.. run function luminacion:npcs/nuvilo/heal_path
execute if score nuvilo_heal_cd luminacion.int matches 100.. run scoreboard players set nuvilo_heal_cd luminacion.int 0

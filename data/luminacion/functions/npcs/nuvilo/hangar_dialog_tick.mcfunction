# =============================================================================
# Luminacion — Nuvilo/Nerkeli Hangar Dialog Trigger
# =============================================================================
# Starts the two-NPC eavesdrop dialog (nuvilo_nerkeli_feria_del_milenio) the
# moment a player gets within 2 blocks of EITHER Nuvilo or Nerkeli — not
# right-click (2026-07-26 change; see states/hangar.mcfunction, which now
# clears right-click actions and adds none back for this scene).
#
# Runs once per tick via #luminacion:npc_routine_tick (see functions/tick.mcfunction).
#
# GATING: only fires while both are actually in their "hangar" active_state
# AND within 3 blocks of each other. The state flags alone aren't proof
# they're standing together — states/hangar.mcfunction never teleports
# either NPC (positioned manually, see its own note), so without the
# distance check a misplaced NPC could still trigger the scene alone.
#
# GUARD: luminacion:npcs storage's nuvilo.hangar_dialog_active (a storage
# flag, not an entity tag — the trigger can come from either NPC, so the
# guard has to be readable from both entities' execution contexts; a tag
# would only live on whichever one set it) prevents re-triggering every tick
# while a player stays inside the radius for the whole (frozen) dialog.
# Cleared only once no player is within 6 blocks of BOTH Nuvilo and Nerkeli —
# same asymmetric enter/exit radius (2 in, 6 out) the pause/resume dance
# already uses elsewhere, checked against both NPCs since either one's
# proximity could have opened the dialog. Clearing lets a later approach
# replay the scene.
# =============================================================================

execute if data storage luminacion:npcs {nuvilo:{active_state:"hangar"}} if data storage luminacion:npcs {nerkeli:{active_state:"hangar"}} unless data storage luminacion:npcs {nuvilo:{hangar_dialog_active:1b}} as @e[type=taterzens:npc,name=Nuvilo,limit=1] at @s if entity @e[type=taterzens:npc,name=Nerkeli,limit=1,distance=..3] if entity @a[distance=..2] run function luminacion:npcs/nuvilo/start_hangar_dialog

execute if data storage luminacion:npcs {nuvilo:{active_state:"hangar"}} if data storage luminacion:npcs {nerkeli:{active_state:"hangar"}} unless data storage luminacion:npcs {nuvilo:{hangar_dialog_active:1b}} as @e[type=taterzens:npc,name=Nerkeli,limit=1] at @s if entity @e[type=taterzens:npc,name=Nuvilo,limit=1,distance=..3] if entity @a[distance=..2] run function luminacion:npcs/nuvilo/start_hangar_dialog

execute if data storage luminacion:npcs {nuvilo:{hangar_dialog_active:1b}} as @e[type=taterzens:npc,name=Nuvilo,limit=1] at @s unless entity @a[distance=..6] as @e[type=taterzens:npc,name=Nerkeli,limit=1] at @s unless entity @a[distance=..6] run data remove storage luminacion:npcs nuvilo.hangar_dialog_active

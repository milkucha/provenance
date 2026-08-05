# =============================================================================
# Luminacion — Nuvilo/Nerkeli Hangar Dialog Starter
# =============================================================================
# Called by hangar_dialog_tick.mcfunction once a player is confirmed within 2
# blocks of either Nuvilo or Nerkeli during the hangar scene. Runs with the
# triggering NPC's position carried over as its "at" context (whichever of
# the two fired it), so the nearest-player selector below resolves relative
# to that NPC, not necessarily Nuvilo.
#
# Sets the guard on the "nuvilo" branch of the luminacion:npcs storage
# regardless of which NPC triggered it — one shared guard is enough, read
# from both entities' contexts in hangar_dialog_tick.mcfunction (see
# _npcs/actions/registry.json → _action_templates.proximity_dialog for why a
# storage flag is used here instead of an entity tag).
# =============================================================================

data modify storage luminacion:npcs nuvilo.hangar_dialog_active set value 1b
execute as @a[distance=..2,sort=nearest,limit=1] at @s run blabber dialogue start luminacion:nuvilo_nerkeli_feria_del_milenio @s @e[name=Nuvilo,limit=1,sort=nearest]

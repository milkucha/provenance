# =============================================================================
# Luminacion — Khaoe Spawn
# =============================================================================
# Built from _npcs/templates/spawn.mcfunction — see that file for the full
# workflow notes. spawn_position is null in the registry (manual placement),
# so stand at the desired spot (Plaza de las Culturas / Feria del Milenio,
# near the Castillo de Görff replica) before running this.
#
# WHO CAN RUN THIS: Any operator, once, at setup time.
# WHO CAN TRIGGER THE NPC: Any player (no restrictions after creation).
# =============================================================================


# --- IDENTITY -----------------------------------------------------------------

npc create Khaoe

npc edit skin https://minesk.in/36106afb45f343e4adba20d4454a573a


# --- MOVEMENT -----------------------------------------------------------------

# NONE: stationary, no face-tracking. Requires resume_routine.mcfunction,
# check_proximity.mcfunction, heal_skin.mcfunction and heal_path.mcfunction
# (all built alongside this file) and this NPC's check_proximity registered
# in data/luminacion/tags/functions/npc_routine_tick.json — same as every
# other movement mode. This used to be skipped for NONE (README §4 originally
# read "roaming NPCs only"), which was wrong: the skin self-heal race
# (Taterzens' async mineskin fetch) and the mid-dialog pause/resume tagging
# apply to any NPC, not just ones that roam — confirmed the hard way when
# Khaoe shipped without this machinery first and her skin never healed after
# a failed fetch. So even though her resting mode is NONE, enter_dialog's
# pause_routine still temporarily sets FORCED_LOOK while a player is close or
# she's mid-conversation, and resume_routine.mcfunction sets her back to
# NONE afterward — she'll face you briefly up close, then go back to static.
npc edit movement NONE


# --- POSE ------------------------------------------------------------------

# Taterzens NPCs support a "/npc edit pose <name>" command (confirmed via the
# mod's own PoseCommand class — not documented in this pack's README before
# now) backed by vanilla's EntityPose enum, persisted as TaterzenNPCTag.Pose
# on the entity (same NBT nesting convention as TaterzenNPCTag.skin.value,
# used by heal_skin.mcfunction elsewhere in this pack). STANDING and SITTING
# are both real, valid EntityPose values. Defaults to STANDING if never set.
#
# Right-click dialog selection below reads this pose live — set it to match
# wherever you've placed her for a given scene:
#   /npc select name Khaoe
#   /npc edit pose STANDING   (Calendario Mecanográfico scene)
#   /npc edit pose SITTING    (bench / Banco Colectivo scene)
# Not set here in spawn.mcfunction on purpose, since it depends on which
# scene she's being placed into at the time — a manual step alongside
# positioning her (spawn_position is also manual, see header above).


# --- PERMISSION LEVEL ---------------------------------------------------------

npc edit commands setPermissionLevel 2


# --- RIGHT-CLICK ACTIONS ------------------------------------------------------
# Two independent trigger conditions, checked in this priority order:
#
#   1. Farlis-proximity (highest priority): if the NPC named Farlis is within
#      5 blocks of Khaoe, right-clicking her picks one of the three ambient
#      khaoe_farlis_* scene fragments at random (equal odds, via roll_dialog
#      — see _npcs/actions/registry.json -> _action_templates.random_dialog).
#      This assumes the two of them are standing together for the scene;
#      Farlis's own spawn.mcfunction (not yet built) still needs to decide
#      separately whether right-clicking HIM also triggers this same roll —
#      left open in TODO.md, not guessed here.
#   2. Pose-gated solo dialogs (fallback, only checked when Farlis is NOT
#      within 5 blocks): STANDING -> khaoe_calendario_mecanografico,
#      SITTING -> khaoe_banco_colectivo. Reads TaterzenNPCTag.Pose directly
#      (see POSE section above) rather than any separate flag.
#
# This priority (companion-scene over solo idle lines) was the sole
# reasonable default given the two conditions can overlap (e.g. she could be
# STANDING with Farlis also nearby) — flag if this should be inverted or
# made mutually exclusive some other way.
#
# @e[name=Khaoe,...] / @e[name=Farlis,...] are left unquoted: both names are
# plain ASCII, no characters outside Brigadier's unquoted-string charset
# (unlike Döran/Dägna elsewhere in this pack — see
# _npcs/actions/registry.json -> _action_templates.random_dialog for why
# that distinction matters when it DOES apply).

npc edit commands add minecraft function luminacion:npcs/_shared/enter_dialog
npc edit commands add minecraft function luminacion:npcs/khaoe/roll_dialog
npc edit commands add minecraft execute if entity @e[name=Farlis,distance=..5] if score khaoe_dialog_roll luminacion.int matches 1 run blabber dialogue start luminacion:khaoe_farlis_el_castillo_que_fue --clicker-- @e[name=Khaoe,limit=1,sort=nearest]
npc edit commands add minecraft execute if entity @e[name=Farlis,distance=..5] if score khaoe_dialog_roll luminacion.int matches 2 run blabber dialogue start luminacion:khaoe_farlis_lo_que_cambia_el_tiempo --clicker-- @e[name=Khaoe,limit=1,sort=nearest]
npc edit commands add minecraft execute if entity @e[name=Farlis,distance=..5] if score khaoe_dialog_roll luminacion.int matches 3 run blabber dialogue start luminacion:khaoe_farlis_esperando_a_khaasan --clicker-- @e[name=Khaoe,limit=1,sort=nearest]
npc edit commands add minecraft execute unless entity @e[name=Farlis,distance=..5] if data entity @e[name=Khaoe,limit=1,sort=nearest] {TaterzenNPCTag:{Pose:"STANDING"}} run blabber dialogue start luminacion:khaoe_calendario_mecanografico --clicker-- @e[name=Khaoe,limit=1,sort=nearest]
npc edit commands add minecraft execute unless entity @e[name=Farlis,distance=..5] if data entity @e[name=Khaoe,limit=1,sort=nearest] {TaterzenNPCTag:{Pose:"SITTING"}} run blabber dialogue start luminacion:khaoe_banco_colectivo --clicker-- @e[name=Khaoe,limit=1,sort=nearest]


# --- REGISTRATION REMINDER ----------------------------------------------------
# UUID capture is automated — do not copy it by hand. Once this NPC (and any
# others) are created and registered in _npcs/npcs/registry.json, run:
#   1. python scripts/minecraft/update_uuids.py generate
#   2. /reload
#   3. /function luminacion:admin/export_npc_uuids
#   4. python scripts/minecraft/update_uuids.py update --log "<path/to/logs/latest.log>"

tellraw @s [{"text":"[Luminacion] ","color":"gold","bold":true},{"text":"Khaoe created. Run the UUID export pipeline (scripts/minecraft/update_uuids.py) to register its UUID — see workflow docs."}]

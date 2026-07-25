# =============================================================================
# Luminacion — Döran Spawn
# =============================================================================
# Built from _templates/npcs/spawn.mcfunction — see that file for the full
# workflow notes. spawn_position is null in the registry (manual placement),
# so stand at the Plaza de las Culturas (Salthos Cruzados, Feria del Milenio)
# before running this.
#
# WHO CAN RUN THIS: Any operator, once, at setup time.
# WHO CAN TRIGGER THE NPC: Any player (no restrictions after creation).
# =============================================================================


# --- IDENTITY -----------------------------------------------------------------

# Deliberately UNQUOTED, unlike the @e[name="Döran",...] selectors below — this
# argument is Taterzens' own "npc create <name>" parser, not a vanilla entity
# selector, and it does not strip quote characters the way vanilla selectors
# do. Confirmed in-game: quoting it ("npc create \"Döran\"") created an NPC
# whose actual name included the literal quote marks ("\"Döran\""), which then
# silently mismatched every @e[name="Döran",...] selector elsewhere in this
# NPC's functions (they were all looking for the unquoted name). This
# argument accepts the raw "ö" unquoted with no complaint either way — it was
# never the source of any parse error, only the selectors were.
npc create Döran

npc edit skin https://minesk.in/c336e48215fb4759908960d4a2748b2a


# --- MOVEMENT -----------------------------------------------------------------

# PATH: follows a set path with rests/look-arounds, same as Gondarfolas. Requires
# resume_routine.mcfunction, check_proximity.mcfunction and heal_skin.mcfunction
# (all built alongside this file), and this NPC's check_proximity registered in
# data/luminacion/tags/functions/npc_routine_tick.json.
# Waypoints are NOT recorded via Taterzens' in-game "/npc edit path" left-click editor —
# that's what causes the stale-restriction bug (see
# _templates/npcs/paths/select_path.mcfunction). Instead, after running this spawn
# function, run functions/npcs/doran/paths/<path_name>.mcfunction (not yet written)
# to give him a route around the Plaza. Until you do, he just stands still in PATH mode.
npc edit movement PATH


# --- PERMISSION LEVEL ---------------------------------------------------------

npc edit commands setPermissionLevel 2


# --- RIGHT-CLICK ACTIONS ------------------------------------------------------
# Random dialog pick on every click — see _maps/actions/registry.json →
# _action_templates.random_dialog for the full rationale. Equal odds (1..3) across
# his three independent Plaza dialogs.
#
# The roll itself is NOT added directly here as an "execute ... run random
# value ..." command — confirmed in-game that /random doesn't resolve in this
# environment at all (fails identically nested here or as a plain top-level
# line elsewhere; see roll_dialog.mcfunction for the gametime-based fallback
# actually used). Isolated in its own function regardless, called as a plain
# "function" command like any other right-click action.
#
# @e[name="Döran",...] is quoted below — also confirmed in-game: an unquoted
# selector "name=" value can't contain "ö" (not in Brigadier's allowed
# unquoted-string charset), and fails to parse without the quotes.

npc edit commands add minecraft function luminacion:npcs/_shared/enter_dialog
npc edit commands add minecraft function luminacion:npcs/doran/roll_dialog
npc edit commands add minecraft execute if score doran_dialog_roll luminacion.int matches 1 run blabber dialogue start luminacion:doran_plaza_orientation --clicker-- @e[name="Döran",limit=1,sort=nearest]
npc edit commands add minecraft execute if score doran_dialog_roll luminacion.int matches 2 run blabber dialogue start luminacion:doran_four_castles --clicker-- @e[name="Döran",limit=1,sort=nearest]
npc edit commands add minecraft execute if score doran_dialog_roll luminacion.int matches 3 run blabber dialogue start luminacion:doran_eras_of_culture --clicker-- @e[name="Döran",limit=1,sort=nearest]


# --- REGISTRATION REMINDER ----------------------------------------------------
# UUID capture is automated — do not copy it by hand. Once this NPC (and any
# others) are created and registered in _maps/npcs/registry.json, run:
#   1. python scripts/update_uuids.py generate
#   2. /reload
#   3. /function luminacion:admin/export_npc_uuids
#   4. python scripts/update_uuids.py update --log "<path/to/logs/latest.log>"

tellraw @s [{"text":"[Luminacion] ","color":"gold","bold":true},{"text":"Döran created. Run the UUID export pipeline (scripts/update_uuids.py) to register its UUID — see workflow docs."}]

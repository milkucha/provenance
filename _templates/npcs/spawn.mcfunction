# =============================================================================
# Luminacion — NPC Spawn Template
# =============================================================================
# WORKFLOW:
#   1. Fill in _maps/npcs/registry.json for this NPC (all fields except UUID)
#   2. Duplicate this folder as:  functions/npcs/<npc_key>/spawn.mcfunction
#   3. Fill in all <placeholders> below using that registry entry
#   4. If spawn_position is set in the registry, uncomment the npc tp line below
#      Otherwise, stand at the desired location before running the function
#   5. Run as an operator: /function luminacion:npcs/<npc_key>/spawn
#   6. Run /npc list, find this NPC, copy its UUID into the registry
#
# WHO CAN RUN THIS: Any operator, once, at setup time.
# WHO CAN TRIGGER THE NPC: Any player (no restrictions after creation).
# =============================================================================


# --- IDENTITY -----------------------------------------------------------------

# Creates the NPC and immediately selects it for the executing player.
# All /npc edit commands below apply to this newly created NPC.
npc create <display_name>

# OPTIONAL — Teleport to fixed spawn position from _maps/npcs/registry.json → spawn_position.
# If spawn_position is null, remove this line and stand at the location before running.
# If spawn_position is set, uncomment and fill: npc tp <x> <y> <z>
# npc tp <x> <y> <z>

# Set skin from mineskin URL (stored in _maps/npcs/registry.json → "skin")
npc edit skin <https://www.mineskin.org/ID>


# --- MOVEMENT -----------------------------------------------------------------

# Options: NONE | FORCED_LOOK | PATH | FORCED_PATH | FOLLOW | FREE
# See _maps/actions/registry.json → _action_templates.movement for details
npc edit movement NONE

# Regardless of movement mode (including NONE):
#   1. Duplicate _templates/npcs/resume_routine.mcfunction,
#      _templates/npcs/check_proximity.mcfunction, _templates/npcs/heal_skin.mcfunction
#      (skip only if skin is still blank) and _templates/npcs/heal_path.mcfunction
#      (leave as a header-only stub if this NPC has no path) into this folder,
#      filling in the placeholders.
#   2. Add this NPC's check_proximity.mcfunction path to
#      data/luminacion/tags/functions/npc_routine_tick.json.
# This makes the NPC stop within 2 blocks of a player (and become interactable),
# then resume its routine once the player leaves or the dialog ends, and
# self-heals its skin/path periodically. See _action_templates.routine_pause_resume
# in _maps/actions/registry.json — this used to be skipped for NONE-movement NPCs,
# which was wrong: the skin self-heal race (Taterzens' async mineskin fetch) and
# the pause/resume tagging apply to every NPC, not just roaming ones. For a NONE
# npc, resume_routine.mcfunction's "npc edit movement NONE" doesn't change any
# actual behavior — it's the tag cleanup and periodic heal calls that matter.
#
# Every dialog's end_dialogue action must also call resume_routine now, e.g.:
#   "action": {
#     "type": "blabber:command",
#     "value": "execute as @interlocutor run function luminacion:npcs/<npc_key>/resume_routine"
#   }
#
# If this NPC's movement mode is PATH or FORCED_PATH (it follows waypoints):
# do NOT record them with Taterzens' in-game "/npc edit path" left-click editor —
# a stray click silently adds/removes nodes, and clearing them afterward leaves
# a stale internal movement restriction behind, so the NPC keeps walking toward
# an old point even with an empty path. Instead, after running this spawn
# function, duplicate _templates/npcs/paths/select_path.mcfunction as
# functions/npcs/<npc_key>/paths/<path_name>.mcfunction and run it as an
# operator. Until you do, the NPC just stands still in PATH mode.


# --- PERMISSION LEVEL ---------------------------------------------------------

# Sets the authority level of the NPC's executed commands (NOT a player restriction).
# Level 2 covers: give, blabber dialogue start, scoreboard, and most gameplay commands.
# Any player can still right-click this NPC regardless of this setting.
npc edit commands setPermissionLevel 2


# --- RIGHT-CLICK ACTIONS ------------------------------------------------------
# All lines below run simultaneously when any player right-clicks this NPC.
# --clicker-- is replaced at runtime with the interacting player's name.
# Remove or add lines depending on what this NPC does.
#
# The first line is mandatory whenever a dialog is involved: it pauses this NPC's
# routine and marks it as mid-conversation (functions/npcs/_shared/enter_dialog.mcfunction),
# so a roaming NPC stops and stays put for the length of the conversation. The
# matching resume happens from the dialog's end_dialogue action(s) — see
# _templates/npcs/resume_routine.mcfunction.
#
# EXAMPLE — an innkeeper NPC named "Maren" who:
#   - pauses her routine and opens a greeting dialog
#   - gives the clicker a bread loaf
#   - sets a scoreboard flag recording that this NPC has been met
#
#   npc edit commands add minecraft function luminacion:npcs/_shared/enter_dialog
#   npc edit commands add minecraft blabber dialogue start luminacion:maren_greeting --clicker-- @e[name=Maren,limit=1,sort=nearest]
#   npc edit commands add minecraft give --clicker-- minecraft:bread 1
#   npc edit commands add minecraft scoreboard players set met_maren luminacion.bool 1
#
# Replace the example lines below with this NPC's actual actions:

npc edit commands add minecraft function luminacion:npcs/_shared/enter_dialog
npc edit commands add minecraft blabber dialogue start luminacion:<dialog_id> --clicker-- @e[name=<display_name>,limit=1,sort=nearest]
npc edit commands add minecraft give --clicker-- minecraft:<item_id> <count>
npc edit commands add minecraft scoreboard players set <variable> luminacion.bool <value>


# --- REGISTRATION REMINDER ----------------------------------------------------
# UUID capture is automated — do not copy it by hand. Once this NPC (and any
# others) are created and registered in _maps/npcs/registry.json, run:
#   1. python scripts/update_uuids.py generate
#   2. /reload
#   3. /function luminacion:admin/export_npc_uuids
#   4. python scripts/update_uuids.py update --log "<path/to/logs/latest.log>"
# This message appears in your chat when the function finishes.

tellraw @s [{"text":"[Luminacion] ","color":"gold","bold":true},{"text":"<display_name> created. Run the UUID export pipeline (scripts/update_uuids.py) to register its UUID — see workflow docs."}]

# =============================================================================
# Luminacion — Khaoe Dialog Roll
# =============================================================================
# Rolls a fresh 1..3 into khaoe_dialog_roll (luminacion.int), read immediately
# afterward by the three Farlis-proximity-gated "blabber dialogue start"
# commands added in spawn.mcfunction (the khaoe_farlis_* ambient scene
# fragments). Same mechanism as functions/npcs/doran/roll_dialog.mcfunction —
# see that file and _npcs/actions/registry.json -> _action_templates.random_dialog
# for the full rationale on why this doesn't use the vanilla /random command
# (confirmed unavailable in this pack's server environment).
#
# Rolled unconditionally on every click, even when Farlis isn't nearby — the
# gated dispatch commands in spawn.mcfunction simply won't read this score in
# that case. Harmless to roll and discard.
#
# CALL CONTEXT: no @s dependency — this only touches scoreboard scores, safe
# to call from anywhere (right-click action or otherwise).
# =============================================================================

execute store result score khaoe_dialog_roll luminacion.int run time query gametime
scoreboard players set khaoe_roll_mod luminacion.int 3
scoreboard players operation khaoe_dialog_roll luminacion.int %= khaoe_roll_mod luminacion.int
scoreboard players add khaoe_dialog_roll luminacion.int 1

# =============================================================================
# Luminacion — Döran Dialog Roll
# =============================================================================
# Rolls a fresh 1..3 into doran_dialog_roll (luminacion.int), read immediately
# afterward by the three gated "blabber dialogue start" commands added in
# spawn.mcfunction.
#
# Does NOT use the vanilla /random command. First attempt
# ("execute store result score doran_dialog_roll luminacion.int run random
# value 1..3") failed to load in THIS environment — and not for the reason
# originally suspected: it fails identically whether added directly via "npc
# edit commands add" (nested inside Taterzens' custom argument) OR as a plain
# top-level line in this very function (confirmed in-game both ways, same
# exact Brigadier error landing at the start of "random" either time). Nothing
# else in this heavily-modded pack's logs successfully uses /random either.
# Whatever the cause, /random itself is unavailable here — not a nesting
# problem — so this uses gametime instead, which every vanilla-compatible
# server has:
#
#   1. Read the world's total elapsed ticks (always increasing, never resets).
#   2. Reduce it mod 3 via a scoreboard operation (needs a score to divide by,
#      not a literal — doran_roll_mod is set fresh each call, just a scratch
#      constant, not meant to be read anywhere else).
#   3. Shift the 0..2 result to 1..3 to match the "matches 1/2/3" gates in
#      spawn.mcfunction.
#
# Not cryptographically random (a player could in principle time a click to
# land on a chosen tick), but plenty for picking which of three greeting
# lines to show — same bar every other "random" cosmetic pick in this pack
# needs to clear.
#
# CALL CONTEXT: no @s dependency — this only touches scoreboard scores, safe
# to call from anywhere (right-click action or otherwise).
# =============================================================================

execute store result score doran_dialog_roll luminacion.int run time query gametime
scoreboard players set doran_roll_mod luminacion.int 3
scoreboard players operation doran_dialog_roll luminacion.int %= doran_roll_mod luminacion.int
scoreboard players add doran_dialog_roll luminacion.int 1

# Provenance — load
# Runs once on world load / datapack reload.

# Register scoreboard objectives.
# Safe to run multiple times: Minecraft logs an error if the objective already
# exists but does not crash and does not overwrite existing scores.
scoreboard objectives add luminacion.bool dummy
scoreboard objectives add luminacion.int dummy
scoreboard objectives add luminacion.gest_timer dummy
scoreboard objectives add luminacion.nod_timer dummy

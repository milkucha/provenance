# =============================================================================
# Luminacion — Admin: Gesture Demo (all)
# =============================================================================
# Dev/QA tool, not part of any NPC's actual dialogue flow. Meant to play
# every gesture in sequence, one at a time, on whichever Taterzen is
# currently nearest, via gesture_demo_step.mcfunction self-scheduling 60
# ticks (3s) apart — but as of 2026-07-25 that self-reschedule is known
# broken (see TODO.md "gesture_demo_step.mcfunction's self-reschedule
# doesn't work"): only the first gesture (index 0) actually plays when this
# is called. Until that's fixed, this still resets the counter to 0 and
# fires the first gesture — for anything past that, call
# "function luminacion:admin/gesture_demo_step" by hand, once per gesture
# you want to see (each call correctly plays the next one in sequence and
# advances the counter — that part works fine, it's only the automatic
# timer-based re-trigger that doesn't).
#
# Uses the existing luminacion.int scoreboard (see load.mcfunction) on a
# fixed fake-player holder, "gesture_demo" — not tied to any real entity, so
# don't reuse that holder name for anything else.
# =============================================================================

scoreboard players set gesture_demo luminacion.int 0
function luminacion:admin/gesture_demo_step

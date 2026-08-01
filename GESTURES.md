# Gestures — resource pack reference

The client-side gesture system in full: how the poses are implemented in
`player.jem`/`player_slim.jem`, how to modify, call, and test them, the elbow-joint rig and its
hard-won lessons, and the per-gesture `CustomModelData` table. This file is deliberately **not**
part of session orientation — read it when working on gestures or the resource pack, skip it
otherwise (README §0 Layer 4 has the summary). The datapack-side dispatch
(`gesture_<name>.mcfunction`, per-entity timers, the tick loop) is documented in README §0 Layer 2
"Gesture dispatch", not here.

## Overview

A forked `player.jem`/`player_slim.jem` EMF/Iris override giving Taterzens NPCs (and real players)
13 animated poses (plus left-arm mirror variants), each triggered by a `CustomModelData`-tagged
invisible stick in the main hand. Coexists with the installed Fresh Animations + FA+Player pack by
forking only the two files that need the gesture hook — every other file (movement math, textures,
cape) still falls through to FA+Player underneath.

**Wiring: repo ↔ live pack.** `resourcepack/` in this repo *is* the pack — there's no build/copy/zip
step for local dev. The live folder Minecraft/PrismLauncher actually reads from,
`resourcepacks/luminacion/`, is a Windows directory **junction** pointing back at `resourcepack/` here
(created with `New-Item -ItemType Junction`; unlike a symbolic link this needs no admin rights or
Developer Mode, since both paths are on the same local drive). Editing a file under `resourcepack/`
edits the live pack instantly — reload with `F3+T`, or a full restart if that doesn't pick it up. A
zip-based `scripts/build_resourcepack.py` (see `TODO.md`) is a separate, not-yet-built concern for
*distributing* a finished pack — irrelevant to day-to-day gesture editing.

**Gestures: how they're built, modified, and called.** Each gesture is a held **pose**, not a
keyframed animation: giving the NPC (or a real player) an invisible
`minecraft:stick{CustomModelData:<N>}` in `weapon.mainhand` makes `player.jem`/`player_slim.jem`
override that limb's rotation to a fixed (or, for wave/shrug/scratch-head/laugh, `sin()`-oscillating)
angle for as long as the item is held. Both `.jem` files are a single minified JSON line each — the
whole rig (head, body, both arms, both legs, all 13 gestures) lives in one blob of nested
`if(nbt(SelectedItem.tag.CustomModelData,<N>), <pose>, <next gesture's case>)` expressions per axis
(`right_arm.rx`/`.ry`/`.rz`, `var.body_rx`, `var.gest_headrx`, ...), eased in over a few frames by a
self-referencing `var.*` low-pass filter (proven more reliable than easing the bone key directly,
which jittered). See the table at the end of this file for each gesture's `CustomModelData` value.

- *To modify a pose* (e.g. the wave's arm-height/outward-swing adjustment made 2026-07-25): find the
  gesture's `CustomModelData` number in the table at the end of this file, then in **both** `player.jem` and
  `player_slim.jem` locate every `if(nbt(...,<N>), torad(<deg>), ...)` branch for the axis you want to
  change (`rx` = raise/lower, `ry` = swing in/out sideways, `rz` = twist, or the oscillation term for
  gestures that move) and edit the `torad(<deg>)` value. The two `.jem` files aren't generated from one
  another — keep them in sync by hand. Because each file is one line with every gesture's branches
  nested together, edit by exact substring match (e.g. `CustomModelData,101),torad(-130)`) rather than
  by line/offset, and re-parse the file as JSON afterward — a stray bracket silently breaks a
  *different* gesture's branch instead of erroring.
- *To call a gesture* on an NPC mid-dialogue: `execute as @interlocutor run function
  luminacion:npcs/_shared/gesture_<name>` (see "Gesture dispatch" in README §0 Layer 2) — tags the NPC
  `luminacion.gesture_active`, gives it the marker stick, and sets that NPC's own
  `luminacion.gest_timer` score to the gesture's hold duration (2.5s/50 ticks for most); every tick,
  `gesture_tick.mcfunction` counts it down and runs `gesture_clear.mcfunction` on that NPC alone once
  it reaches 0. Never call a gesture on an NPC already mid-gesture, and never pair a gesture
  action with a `nod_up_down`/`nod_left_right` action on the same dialogue state — gestures fully own
  the pose while active (worst case for laugh, which also overrides head pitch).
- *To test a gesture* without going through a dialog, either target the nearest Taterzen directly:

  ```
  execute as @e[type=taterzens:npc,sort=nearest,limit=1] run function luminacion:npcs/_shared/gesture_wave
  ```

  or give yourself the marker item to preview the pose on your own model — a faster loop when you're
  just iterating on numbers, since the `.jem` logic keys off whoever's holding the item, NPC or player:

  ```
  item replace entity @s weapon.mainhand with minecraft:stick{CustomModelData:101}
  ```

- *Elbow joint* (working, landed 2026-07-25 — first used by the `cross_arms` gesture): `right_arm`/
  `left_arm` are each split at the vertical midpoint into a shortened shoulder segment (unchanged
  pivot) and a nested `submodels` child bone, `right_forearm`/`left_forearm`, added to that part's own
  `"submodels"` array (alongside `right_item`/`left_item`, left untouched — vanilla's held-item
  attachment is keyed to those exact names, so don't move them onto the forearm). A gesture bends the
  elbow by setting `right_forearm.rx`/`left_forearm.rx` (currently only `rx` is used — a real elbow is
  a one-axis hinge, unlike the shoulder's three); see `var.gest_rforearmrx`/`var.gest_lforearmrx` for
  the pattern (gated on a `CustomModelData` check, eased via `var.gest_rate`, identical structure to
  every other gesture var).
  - *The one true lesson*: for a nested `submodels` bone, both `translate` **and** `boxes.coordinates`
    must be small numbers in the *parent's own local frame* — not the large absolute/skin-space numbers
    top-level parts like `right_arm` itself use (e.g. `[4,12,-2,4,12,4]`). The first attempt reused
    those large numbers directly for the forearm and it rendered fully detached, because a small
    parent-relative `translate` combined with a huge box shape doesn't mean what it looks like it
    means. This was confirmed by pulling a real, shipped `wolf.jem` from Fresh Animations' own GitHub
    repo (the same author this rig already credits) and inspecting its `tail`/`tail2` nested-bone
    pair — its child bone's `translate` and `boxes.coordinates` are both small numbers in the same
    handful-of-units range, nothing like the parent's own absolute-frame box.
  - *Position and rotation both compose automatically* once nested correctly — a plain reattachment
    (forearm `rx` always 0, no gesture) needs zero extra formula work; the child just rides along with
    whatever the parent's current rotation is. Don't manually add `right_arm.rx` into the forearm's own
    rotation formula — that double-applies the parent's rotation on top of the automatic composition
    and makes things worse, not better (confirmed the hard way).
  - *Getting the exact pivot right had no shortcut* — the local-frame scale/sign/axis isn't derivable
    from the file alone; it took extensive in-game trial and error (probe values, screenshots, bisecting
    magnitude and each axis independently) to land on the final numbers: `right_forearm` translate
    `[7,17.5,0]`, `left_forearm` translate `[-4,17.5,0]`, both with `boxes.coordinates`
    `[-4,-6,-2,4,6,4]` (classic) / `[-3,-6,-2,3,6,4]` (slim) — i.e. extending from the pivot in
    *negative* local Y. A small seam remains at the elbow; accepted as fine given the blocky art style.
  - *Texture*: both segments reuse the arm's existing UV block (no skin edits). The auto-net's "cap"
    faces read top-to-bottom in **screen space** matching shoulder-to-wrist on the body — the first
    attempt had the shoulder and wrist segments' `textureOffset`s backwards (a real, visible bug, not
    just positional) and needed swapping; see the current `[40,16]`/`[40,22]`-style offset pairs on
    `right_arm`/`right_forearm` for the corrected assignment.
  - *Known imperfection*: the second-layer sleeve overlay (`right_forearm_sleeve`/`left_forearm_sleeve`)
    is **not** positionally calibrated to match the forearm — it's a flat sibling part (like
    `right_sleeve`) using its own separate, never-tuned `translate`, left over from an earlier attempt.
    Nesting it under `right_sleeve`/`left_sleeve` the same way `right_forearm` nests under `right_arm`
    was tried and reverted: it broke `cross_arms`'s elbow bend, because a bone nested under `right_sleeve`
    only inherits `right_sleeve`'s rotation (a copy of the *shoulder's* rotation only — see
    `"right_sleeve.rx":"right_arm.rx"` — never the forearm's own local bend), so the sleeve stayed
    straight while the real arm folded. Fixing this properly means either giving the sleeve's forearm
    bone its own copy of `var.gest_rforearmrx`, or nesting it under `right_forearm` instead of
    `right_sleeve` (untried) — deferred, see TODO.md.

## Gesture `CustomModelData` table

| Gesture | `CustomModelData` | `mcfunction` | Pose |
|---|---|---|---|
| Wave | 101 | `gesture_wave` | Right arm raised + swung outward; `rz` oscillates (`sin(age*0.65)`) for the side-to-side wave motion |
| Point | 102 | `gesture_point` | Right arm extended forward, static |
| Bow | 103 | `gesture_bow` | Body pitches forward 25°; arms untouched, hang naturally |
| Shrug | 104 | `gesture_shrug` | Both arms raised symmetrically, with a small idle bounce (`sin(age*0.4)`) |
| Palms-up | 105 | `gesture_palms_up` | Both arms raised + rotated, static — originally prototyped as "cross-arms", renamed once it visually read as palms-up instead |
| Scratch-head | 106 | `gesture_scratch_head` | Right arm to head height, with an intermittent scratching wobble |
| Laugh | 107 | `gesture_laugh` | Both arms + body + head all animated — overrides head pitch too, so never pair with a `nod_*` action on the same dialogue state |
| No | 108 | `gesture_no` | Both arms raised in front of the chest and swept side to side in sync (`ry` oscillates, `sin(age*1)`, mirrored between arms) while the head shakes side to side (`sin(age*1.3)`) via a new `var.gest_headry` low-pass filter — the yaw counterpart to Laugh's `var.gest_headrx` pitch override, since no earlier gesture touched head yaw. A "no, no" rejection gesture. Rates started much higher (`age*3`/`age*4`) and were slowed down after in-game testing read as a tremor/panic shake rather than a deliberate "no". Overrides head yaw as well as both arms, so never pair with a `nod_left_right` action on the same dialogue state, same caveat as Laugh/`nod_up_down` |
| Face-palm | 109 | `gesture_face_palm` | Right arm raised to head height and swung inward across the face (`ry` at -20°, shallower than Scratch-head's outward +55° — pulled back from an initial -40° after in-game testing showed the hand clipping into the head mesh), while the head pitches down statically via `var.gest_headrx` (the same variable Laugh already overrides) and shakes slowly side to side instead of nodding, via `var.gest_headry` (`sin(age*0.6)`) — the yaw variable "No" introduced. Own slower `var.gest_rate` of 3 (vs. the default 6) for a smoother ease-in. Reads as quiet disapproval/disappointment. Right hand only for now; a left-hand mirror (209, following the established +100 convention) is planned but not yet built |
| Jump | 110 | `gesture_jump` | Right arm raised straight overhead (fist-pump; own faster `var.gest_rate` of 10 so the arm snaps up quickly), `body.ty`/`right_leg.ty`/`left_leg.ty` all share a new `var.gest_bodyty` term — a Mario level-clear-style victory jump. Unlike the other 7 gestures, this one moves body **translation**, not just limb rotation, and it's a genuine one-shot: `var.gest_jumpclock` is a self-resetting per-gesture stopwatch (`if(CMD110, var.gest_jumpclock+frame_time, 0)`, in real seconds via `frame_time`, not the entity's global `age`) driving a single `sin()` hump clamped at its peak (`min(var.gest_jumpclock,pi/9)*9`) so the bounce fires exactly once, in sync with the arm raising, instead of repeating or drifting out of phase with an arbitrary `age` offset the way a naive `sin(age*rate)` would. Also the only gesture with a non-standard hold: `gesture_jump.mcfunction` sets `luminacion.gest_timer` to `12` (0.6s) instead of the usual `50` (2.5s), so the arm drops the instant the ~7-tick hop lands instead of staying pumped for a held pose — safe to vary per-gesture like this since the timer is per-entity (see "Gesture dispatch" in README §0 Layer 2) |
| Wave (left) | 201 | `gesture_wave_left` | Left-arm mirror of Wave: `left_arm.rx` shares Wave's `rx` (unmirrored — raise/lower reads the same on either arm), `ry`/`rz` are sign-flipped from Wave's values, including the `sin(age*0.65)` oscillation term. Mirror-variant `CustomModelData` numbering convention: base gesture's number + 100 |
| Point (left) | 202 | `gesture_point_left` | Left-arm mirror of Point, same convention as Wave (left) |
| Scratch-head (left) | 206 | `gesture_scratch_head_left` | Left-arm mirror of Scratch-head, same convention as Wave (left) |
| Cross-arms | 111 | `gesture_cross_arms` | Both arms raised and swung in across the chest, **and** both elbows bend via the `right_forearm`/`left_forearm` bones (the first gesture to use them — see "Elbow joint" above) |
| Flex-arm | 112 | `gesture_flex_arm` | Right arm only, raised out to the side (`ry` 90°, wider than a first-pass 60° which read as a salute); once `var.gest_flexclock` passes 0.9s the elbow bends via `right_forearm` (70°, pulled back from an initial 90°) to bring the fist up near the shoulder — sequenced raise-then-flex rather than simultaneous, own slower `var.gest_rate` of 3 |

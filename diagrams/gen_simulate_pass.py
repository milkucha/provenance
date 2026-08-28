import html
import json

EM_DASH = chr(0x2014)
RSQUO = chr(0x2019)

def esc(s):
    s = html.escape(s)
    s = s.replace(EM_DASH, '&mdash;').replace(RSQUO, '&rsquo;')
    return s

W = 780
LEFT = 150
RIGHT = 610
BOXW = RIGHT - LEFT
CX = (LEFT + RIGHT) // 2  # 380
CORRIDOR_X = LEFT - 66    # 84 -- gated-slot bypass line
LOOP_X = RIGHT + 80       # 690

BOX_H = 30
VGAP = 44

buf = []
def emit(s): buf.append(s)

DETAILS = {}

def arrow(x1, y1, x2, y2, cls="flow-line", marker=True):
    m = ' marker-end="url(#arrow)"' if marker else ''
    emit(f'<path class="{cls}" d="M{x1},{y1} L{x2},{y2}"{m}/>')

def register(node_id, phase, title, script, returns, note=None, substeps=None):
    DETAILS[node_id] = {"phase": phase, "title": title, "script": script, "returns": returns, "note": note, "substeps": substeps}

def node_open(node_id, hover):
    emit(f'<g class="clickable" tabindex="0" role="button" data-node-id="{node_id}" onclick="showDetail(\'{node_id}\', event)">')
    emit(f'  <title>{esc(hover)}</title>')

def node_close():
    emit('</g>')

def chain_node(top, n, node_id, title, desc, roll=False, has_script=True, hover=None, left=LEFT):
    node_open(node_id, hover or f"{title} — {desc}. Click for the exact command.")
    emit(f'  <rect class="nbox" x="{left}" y="{top}" width="{BOXW}" height="{BOX_H}" rx="5"/>')
    if roll:
        emit(f'  <rect class="stripe" x="{left+1}" y="{top+1}" width="4" height="{BOX_H-2}"/>')
    cy = top + BOX_H/2
    bcx = left + 22
    emit(f'  <circle class="badge-circle" cx="{bcx}" cy="{cy}" r="9"/>')
    emit(f'  <text class="badge-text" x="{bcx}" y="{cy}">{n}</text>')
    title_span = f'<tspan font-weight="600">{esc(title)}</tspan> &mdash; {esc(desc)}'
    if not has_script:
        title_span += ' <tspan class="no-script-tag">&middot; no separate script</tspan>'
    emit(f'  <text class="ntitle" x="{left+42}" y="{cy}">{title_span}</text>')
    node_close()

def chain(items, start_y, left=LEFT, start_n=1):
    y = start_y
    cx = left + BOXW/2
    for i, (node_id, title, desc, roll, has_script) in enumerate(items, start_n):
        chain_node(y, i, node_id, title, desc, roll, has_script, left=left)
        bottom = y + BOX_H
        if i < start_n + len(items) - 1:
            arrow(cx, bottom, cx, bottom + VGAP)
        y = bottom + VGAP
    return start_y + len(items) * BOX_H + (len(items)-1) * VGAP

FRAME_PAD_TOP = 26
FRAME_PAD_BOT = 22
LABEL_H = 26
FRAME_RIGHT = RIGHT + 60
FRAME_LEFT = CORRIDOR_X - 20

# ============================================================================
# SIMULATE'S OWN LOOP -- pre-dispatch half
# ============================================================================
y = 30
emit(f'<text class="phase-label roll" x="{LEFT}" y="{y+LABEL_H-8}">/SIMULATE &middot; LOOP GATE AND PAIRING</text>')

gate_top = y + LABEL_H + 10
gate_bottom = gate_top + BOX_H
node_open("gate0", "Living pool has at least 2 members? If not, stop the run early. Click for detail.")
emit(f'<rect class="nbox" x="{LEFT}" y="{gate_top}" width="{BOXW}" height="{BOX_H}" rx="5"/>')
emit(f'<text class="ntitle" x="{CX}" y="{gate_top+BOX_H/2}" text-anchor="middle">living pool &ge; 2? <tspan class="no-script-tag">&middot; stop early otherwise</tspan></text>')
node_close()
register("gate0", "Simulate", "Living pool size check", None,
    "stop the run early if fewer than 2 living participants remain",
    "Checked before every pass (SKILL.md Step 3 point 1) — not a script call, a plain length check "
    "against the in-conversation living-pool list. Only relevant to a /simulate batch; a standalone "
    "/enact call has no pool to exhaust.")

arrow(CX, gate_bottom, CX, gate_bottom + VGAP)
pair_top = gate_bottom + VGAP
pair_bottom = pair_top + BOX_H
node_open("pair0", "simulate_resolve_pair.py — draws the pair and resolves any lead-override. Click for the exact command.")
emit(f'<rect class="nbox" x="{LEFT}" y="{pair_top}" width="{BOXW}" height="{BOX_H}" rx="5"/>')
emit(f'<rect class="stripe" x="{LEFT+1}" y="{pair_top+1}" width="4" height="{BOX_H-2}"/>')
emit(f'<text class="ntitle" x="{LEFT+42}" y="{pair_top+BOX_H/2}"><tspan font-weight="600">simulate_resolve_pair.py</tspan> &mdash; draws the pair, resolves lead-override</text>')
node_close()
register("pair0", "Simulate", "simulate_resolve_pair.py",
    "py scripts/lore/simulate_resolve_pair.py --pool <every slug still in the living pool> --pass-number <N>",
    "participant_1, participant_2, forced_visit",
    "A genuine uniform draw over the pool (pick_pair.py's own logic) — not the model's own guess at "
    "“random,” which skews toward whichever names are most salient in context. Then checks "
    "participant_1's file for an unexpired leads entry (younger than lead_expiry_passes — 8, from "
    "_lore/tuning.json); if one's followed (roll_lead_followup.py), overrides participant_2 to the "
    "lead's target and consumes that lead. This is /simulate's own concern — deciding WHO is in the "
    "scene — entirely separate from /enact's own mechanics below, which only ever run once the pair "
    "is already fixed.")

arrow(CX, pair_bottom, CX, pair_bottom + VGAP)
dispatch_top = pair_bottom + VGAP
dispatch_bottom = dispatch_top + BOX_H
emit(f'<rect class="nbox hub" x="{LEFT}" y="{dispatch_top}" width="{BOXW}" height="{BOX_H}" rx="5"/>')
emit(f'<text class="ntitle" x="{CX}" y="{dispatch_top+BOX_H/2}" text-anchor="middle">dispatch one subagent to run /enact between these two, end to end</text>')

frameSimA_top = y
frameSimA_bottom = dispatch_bottom + FRAME_PAD_BOT
emit(f'<rect class="section-frame roll" x="{FRAME_LEFT}" y="{frameSimA_top-4}" width="{FRAME_RIGHT-FRAME_LEFT}" height="{frameSimA_bottom-frameSimA_top+4}" rx="10"/>')

conn0_top = frameSimA_bottom + 16
conn0_bottom = conn0_top + 40
arrow(CX, frameSimA_bottom, CX, conn0_bottom)
emit(f'<text class="conn-label" x="{CX}" y="{(conn0_top+conn0_bottom)/2 + 4}" text-anchor="middle">everything below is /enact&rsquo;s own mechanism, unchanged whether called directly or from here</text>')

# ============================================================================
# /ENACT'S OWN FLOW
# ============================================================================
labelEnact_top = conn0_bottom + 20
emit(f'<text class="phase-label judge" x="{LEFT}" y="{labelEnact_top+LABEL_H-8}">/ENACT &middot; STEP 2 &middot; second interlocutor</text>')

fork_top = labelEnact_top + LABEL_H + 10
fork_bottom = fork_top + BOX_H
node_open("fork0", "Player, or another character? Click for detail.")
emit(f'<rect class="nbox hub" x="{LEFT}" y="{fork_top}" width="{BOXW}" height="{BOX_H}" rx="5"/>')
emit(f'<text class="ntitle" x="{CX}" y="{fork_top+BOX_H/2}" text-anchor="middle">the player, or another character?</text>')
node_close()
register("fork0", "Enact", "Second interlocutor", None,
    "decides whether any of what follows applies at all",
    "Against the player, none of Step 4's mechanical block or the eligibility gate below ever "
    "applies — straight to Step 5a, freeform, exactly as /enact has always played a player scene. "
    "Everything on this diagram past this point is the “against another character” branch only.")

diag_top = fork_bottom
diag_bottom = diag_top + 60
player_x = LEFT + 90
node_open("player0", "Step 5a — freeform scene against the player, unchanged, no mechanical layer. Click for detail.")
emit(f'<rect class="nbox" x="{LEFT}" y="{diag_bottom}" width="220" height="{BOX_H}" rx="5"/>')
emit(f'<text class="ntitle" x="{LEFT+14}" y="{diag_bottom+BOX_H/2}">Step 5a &mdash; freeform, vs. player</text>')
node_close()
register("player0", "Enact", "Step 5a — against the player", None,
    "the scene, played turn by turn against live input",
    "Unaffected by anything on this page — no eligibility gate, no mechanical block. Same as it's "
    "always been: play interlocutor 1 in character, waiting for the player's actual input each time.")
arrow(CX, diag_top, player_x, diag_bottom)
emit(f'<text class="cond-label" x="{(CX+player_x)/2 - 10}" y="{(diag_top+diag_bottom)/2 - 6}" text-anchor="middle">player</text>')

another_x = CX
arrow(CX, diag_top, another_x, diag_bottom + BOX_H + 20)
emit(f'<text class="cond-label" x="{CX+10}" y="{(diag_top+diag_bottom)/2 - 6}" text-anchor="middle">another character</text>')

gateE_top = diag_bottom + BOX_H + 20
gateE_bottom = gateE_top + BOX_H
node_open("gateE", "Both participants need routines+arc on file. Click for detail.")
emit(f'<rect class="nbox" x="{LEFT}" y="{gateE_top}" width="{BOXW}" height="{BOX_H}" rx="5"/>')
emit(f'<text class="ntitle" x="{CX}" y="{gateE_top+BOX_H/2}" text-anchor="middle">both have `routines`+`arc` on file?</text>')
node_close()
register("gateE", "Enact", "Eligibility gate", None,
    "stop, name the character and the missing field, point at /character to complete it",
    "No freeform fallback any more — this used to silently drop to an ungrounded scene, and that "
    "path no longer exists. /character Step 2a can re-run Step 8 on an existing character to backfill "
    "just what's missing. A /simulate run filters its whole pool against this same check up front "
    "(its own Step 1), so this should already read “yes” whenever /simulate is the caller — "
    "but /enact never skips its own check just because the caller claims it already passed.")

stop_x = LEFT - 140
stop_top = gateE_bottom + 50
node_open("stopE", "Stop this run — no mechanism to fall back to. Click for detail.")
emit(f'<rect class="nbox gated" x="{stop_x}" y="{stop_top}" width="130" height="{BOX_H}" rx="6"/>')
emit(f'<text class="ntitle" x="{stop_x+12}" y="{stop_top+BOX_H/2}">stop &amp; flag</text>')
node_close()
register("stopE", "Enact", "Stop & flag", None,
    "tell the user plainly which character and field is missing",
    "Point at /character to complete it (Step 2a can re-run Step 8 on an existing character) or drop "
    "this participant from the run. No auto-backfill script — a human decision, flagged, not guessed.")
arrow(CX - 20, gateE_bottom, stop_x + 65, stop_top, marker=True)
emit(f'<text class="skip-label" x="{stop_x+65}" y="{(gateE_bottom+stop_top)/2 - 4}" text-anchor="middle">no</text>')

arrow(CX, gateE_bottom, CX, gateE_bottom + VGAP)
emit(f'<text class="cond-label" x="{CX+10}" y="{gateE_bottom+12}">yes</text>')

frameFork_top = labelEnact_top - 4
frameFork_bottom = stop_top + BOX_H + FRAME_PAD_BOT
emit(f'<rect class="section-frame judge" x="{FRAME_LEFT}" y="{frameFork_top}" width="{FRAME_RIGHT-FRAME_LEFT}" height="{frameFork_bottom-frameFork_top}" rx="10"/>')

# ---------- STEP 4 mechanical block (causal order rewritten 2026-08-28 — see CHRONICLE.md) ----------
step4_items = [
    ("a1", "partner tracking", "records who's paired this pass", False, True),
    ("a2", "home/visit roll", "who's home, who's visiting", True, True),
    ("a3", "routine roll (home only)", "which routine fires for the home participant", True, True),
    ("a4", "location/context assembly", "where the scene lands, texture, provides", False, False),
    ("a5", "arc primacy roll", "whose arc leads the scene", True, True),
    ("a6", "needs/provides check", "does the scene satisfy the primacy winner's arc", False, True),
    ("a7", "contested roll", "does a rival try to hinder", True, True),
    ("a8", "knowledge/criteria gate", "is this pair even eligible", False, True),
    ("a9", "arc-outcome roll", "advances or resolves the lead arc", True, True),
    ("a10", "arc tally vs. threshold", "complete / transform / failed / ongoing", False, False),
]
register("a1", "4", "partner tracking",
    "py scripts/lore/record_partner.py <slug> --with <other slug>",
    "(no return value — pure bookkeeping)",
    "Called twice, once per direction, moved to the very front 2026-08-28 — unconditional the "
    "moment the pair is fixed, with nothing to do with anything decided below. The post-scene "
    "reproduction check (Step 8 point 8) reads the counts this call already wrote.")
register("a2", "4", "home/visit roll",
    "py scripts/lore/roll_home_visit.py --p1 <slug> --p2 <slug>",
    "home: whichever slug is home this pass; visiting: the other",
    "Added 2026-08-28, replacing the old resolve_location.py. A flat coin flip for now — not yet "
    "weighted by anything. Decided BEFORE any routine is rolled, not derived afterward by comparing "
    "two independently-rolled routines. Skipped when the pair was fixed by a lead-override instead "
    "(home is forced to the lead's target). A not-yet-built survival-pressure mechanism is meant to "
    "eventually weight this roll one way or another — see TODO.md's \"survival mechanism\" entry.")
register("a3", "4", "routine roll (home only)",
    "py scripts/lore/roll_routine.py <location:weight> [<location:weight> ...]",
    "the routine that fires",
    "Called once, only for the home participant, against their own routines[] weights. The visiting "
    "participant simply enters whatever context this produces — they don't roll their own routine "
    "this pass any more.")
register("a4", "4", "location/context assembly",
    None, "location, home_frame, traveler, context, texture, provides",
    "Not a script call — a plain assembly (simulate_pass_lib.assemble_location()), same discipline "
    "as the old context/texture lookup this always folded in. With only the home participant's "
    "routine ever rolled, location IS that routine's own location — nothing left to resolve by "
    "comparison. This also retires the old \"coincidence\" mode outright: it depended on two "
    "independently-rolled routines, and only one is ever rolled per pass now.")
register("a5", "4", "arc primacy roll",
    "py scripts/lore/roll_arc_primacy.py --p1 <slug> --p2 <slug>",
    "primary: whichever slug leads this scene's arc",
    "Decides whose arc gets to advance/resolve this pass — the loser's own arc sits out. Moved "
    "2026-08-28 to run AFTER home/visit is decided and independently of it: the visiting "
    "participant's arc can still be the one that leads the scene.")
register("a6", "4", "needs/provides check",
    "py scripts/lore/check_needs_provides.py --needs <tag> [...] --provides <tag> [...]",
    "match: true/false, matched_need, matched_provide",
    "Only runs when the arc-PRIMACY WINNER has an ongoing arc with needs — keyed to whichever "
    "participant that is (2026-08-28: no longer \"the traveler's\" arc as a fixed role; the primacy "
    "winner can just as easily be the home participant).")
register("a7", "4", "contested roll",
    "py scripts/lore/roll_contested.py", "contested: true/false",
    "Only rolled when the scene was motivated. Odds: 15% (_lore/tuning.json odds_percent.contested).")
register("a8", "4", "knowledge/criteria gate",
    "py scripts/lore/check_arc_alignment.py --arc-about <tag> [...] --arc-needs <tag> [...] "
    "--peer-standard \"<text>\" --peer-wasted-life \"<text>\" --peer-knowledge-item <item> [...]",
    "gate: hit/miss, inclined: advance/hinder/neutral, matched_about",
    "Only runs when the primacy winner already has an ongoing arc.")
register("a9", "4", "arc-outcome roll",
    "py scripts/lore/roll_arc_outcome.py --inclined <advance|hinder|neutral> [--contested]",
    "outcome: advance/stall/reverse",
    "Only rolled when the gate hit. Resolved before the scene is written on purpose. Contested-aware "
    "as of 2026-08-28: a contested scene shifts the weights toward reverse by "
    "contested_outcome_shift points (_lore/tuning.json) — it skews the odds, same as inclined "
    "itself, never decides the outcome outright by itself.")
register("a10", "4", "arc tally vs. threshold",
    None, "tally_result: complete/transform/failed/ongoing",
    "Not a script call — plain arithmetic against arc_resolution_threshold: 3 from _lore/tuning.json.")

frameA_top = frameFork_bottom + 30
emit(f'<text class="phase-label roll" x="{LEFT}" y="{frameA_top+LABEL_H-8}">/ENACT &middot; STEP 4 &middot; grounding the scene mechanically</text>')
emit(f'<text class="conn-label" x="{LEFT}" y="{frameA_top+LABEL_H+10}">py scripts/lore/simulate_pass_brief.py --pair &lt;p1&gt; &lt;p2&gt; --pass-number &lt;N&gt; &mdash; one call, everything below</text>')
chainA_start = frameA_top + LABEL_H + 26
chainA_bottom = chain(step4_items, chainA_start, left=LEFT)
frameA_bottom = chainA_bottom + FRAME_PAD_BOT
emit(f'<rect class="section-frame roll" x="{FRAME_LEFT}" y="{frameA_top-4}" width="{FRAME_RIGHT-FRAME_LEFT}" height="{frameA_bottom-frameA_top+4}" rx="10"/>')

conn1_top = frameA_bottom + 16
conn1_bottom = conn1_top + 60
arrow(CX, frameA_bottom, CX, conn1_bottom)
emit(f'<text class="conn-label" x="{CX}" y="{(conn1_top+conn1_bottom)/2 - 6}" text-anchor="middle">writes <tspan class="mono">.simulate_pass_brief.json</tspan></text>')
emit(f'<text class="conn-label" x="{CX}" y="{(conn1_top+conn1_bottom)/2 + 13}" text-anchor="middle">flags which of the three slots below are open</text>')

# ---------- STEP 5b: judgment slots + scene ----------
labelB_top = conn1_bottom + 20
emit(f'<text class="phase-label judge" x="{LEFT}" y="{labelB_top+LABEL_H-8}">/ENACT &middot; STEP 5b &middot; enact both characters</text>')
hub_top = labelB_top + LABEL_H + 10
hub_bottom = hub_top + BOX_H
emit(f'<rect class="nbox hub" x="{LEFT}" y="{hub_top}" width="{BOXW}" height="{BOX_H}" rx="5"/>')
emit(f'<text class="ntitle" x="{CX}" y="{hub_top+BOX_H/2}" text-anchor="middle">reads <tspan class="mono" font-weight="600">.simulate_pass_brief.json</tspan></text>')

j0 = hub_bottom + 40
arrow(CX, hub_bottom, CX, j0)
emit(f'<circle class="junction" cx="{CX}" cy="{j0}" r="3"/>')

gated = [
    ("barc", "Author the arc (fallback)",
        "write_arc.py — scoped to the character’s own horizon band",
        "arc_authoring_needed open"),
    ("brival", "Maybe name a rival",
        "apply_contested_lead.py — only if the scene points at someone who already has a file",
        "contested_hinder_slot open (optional even then)"),
]
register("barc", "5b", "Author the arc",
    "py scripts/lore/write_arc.py <slug> --about \"<tag>\" [...] --needs \"<tag>\" [...] "
    "--context <name> --premise \"<text>\"",
    "writes the arc AND registers its concept: <id> tag, in one call",
    "The FALLBACK path — /character Step 8 authors a character's arc at creation by default. "
    "premise is always agent-composed prose; no script generates it, only writes it to disk.")
register("brival", "5b", "Maybe name a rival",
    "py scripts/lore/apply_contested_lead.py --traveler <slug> --rival <slug> --supplier <slug> "
    "--matched-provide \"<tag>\" --pass-number <N>",
    "writes a leads entry and a fixed attributed note",
    "Genuinely optional even when the slot is open — the default is to leave it ambient/unnamed.")

GBOX_H = 46
GATE_PRE_GAP = 32
GATE_POST_GAP = 54
STAGE_H = GATE_PRE_GAP + GBOX_H + GATE_POST_GAP

j = j0
for node_id, title, desc, cond in gated:
    box_top = j + GATE_PRE_GAP
    box_bottom = box_top + GBOX_H
    j_next = j + STAGE_H
    arrow(CX, j, CX, box_top)
    emit(f'<text class="cond-label" x="{CX+14}" y="{j+12}">{esc(cond)}</text>')
    node_open(node_id, f"{title}. Click for the exact command.")
    emit(f'<rect class="nbox gated" x="{LEFT}" y="{box_top}" width="{BOXW}" height="{GBOX_H}" rx="6"/>')
    emit(f'<text class="ntitle" x="{LEFT+18}" y="{box_top+18}"><tspan font-weight="600">{esc(title)}</tspan></text>')
    emit(f'<text class="nsub" x="{LEFT+18}" y="{box_top+35}">{esc(desc)}</text>')
    node_close()
    arrow(CX, box_bottom, CX, j_next)
    emit(f'<circle class="junction" cx="{CX}" cy="{j_next}" r="3"/>')
    corridor_mid_top = j + 22
    corridor_mid_bottom = j_next - 22
    emit(f'<path class="corridor-line" d="M{CX},{j} Q{CORRIDOR_X+40},{j+8} {CORRIDOR_X},{corridor_mid_top} L{CORRIDOR_X},{corridor_mid_bottom} Q{CORRIDOR_X+40},{j_next-8} {CX},{j_next}" marker-end="url(#arrow)"/>')
    emit(f'<text class="skip-label" x="{CORRIDOR_X-8}" y="{(corridor_mid_top+corridor_mid_bottom)/2}" text-anchor="end">not open</text>')
    j = j_next

always_top = j + 32
always_h = 50
always_bottom = always_top + always_h
arrow(CX, j, CX, always_top)
emit(f'<text class="cond-label always" x="{CX+14}" y="{j+12}">always</text>')
node_open("bscene", "Write the scene — /enact Steps 5b, 7, 8, 10. Click to see each sub-step.")
emit(f'<rect class="nbox always" x="{LEFT}" y="{always_top}" width="{BOXW}" height="{always_h}" rx="6"/>')
emit(f'<text class="ntitle" x="{LEFT+18}" y="{always_top+18}"><tspan font-weight="600">Write the scene</tspan></text>')
emit(f'<text class="nsub" x="{LEFT+18}" y="{always_top+35}">alternating turns, dramatizing Step 4&rsquo;s already-fixed facts</text>')
node_close()
register("bscene", "5b", "Write the scene", None,
    "the scene transcript, a hearsay entry, and any criterion/life update",
    "One message, alternating clearly labeled turns, each character honoring their own bounded "
    "knowledge sample independently — dramatizing Step 4's facts, never re-deciding them. Never "
    "skipped; this is the actual mechanism being exercised.",
    substeps=[
        {"step": "6", "label": "Save the scene transcript",
         "detail": "Choose the scene id now, write _npcs/scenes/<scene_id>.md — the only file under "
                    "_npcs/ this skill ever writes."},
        {"step": "7", "label": "Update the hearsay record",
         "detail": "Record each character's mutated interpretation, not what was objectively said — "
                    "framing, emphasis, and moral judgment filtered through their criterion/trusts/"
                    "distrusts. Written via py scripts/lore/record_hearsay.py --json-file <path>."},
        {"step": "8", "label": "Resolve shocks, drift, and the scene count",
         "detail": "check_anchor_reference.py gates whether any claim touches a participant's "
                    "criterion.anchor; if so, resolve reject/reinterpret/break and record it (plus "
                    "the life.lived+1 every participant gets) via update_character.py. Runs "
                    "horizon.py again afterward, record_death.py and roll_death_legacy.py if so — "
                    "see the closing chain below."},
        {"step": "10", "label": "Update the character record",
         "detail": "Append knowledge.experience for anything the scene established beyond the "
                    "original sample, via update_character.py --add-experience / "
                    "--add-grounded-experience."},
    ])

ret_top = always_bottom + 40
ret_bottom = ret_top + BOX_H
arrow(CX, always_bottom, CX, ret_top)
emit(f'<rect class="nbox hub" x="{LEFT}" y="{ret_top}" width="{BOXW}" height="{BOX_H}" rx="5"/>')
emit(f'<text class="ntitle" x="{CX}" y="{ret_top+BOX_H/2}" text-anchor="middle">returns a short summary</text>')

frameB_top = labelB_top - 4
frameB_bottom = ret_bottom + FRAME_PAD_BOT
emit(f'<rect class="section-frame judge" x="{FRAME_LEFT}" y="{frameB_top}" width="{FRAME_RIGHT-FRAME_LEFT}" height="{frameB_bottom-frameB_top}" rx="10"/>')

# ---------- STEP 8 closing: horizon / death / death-legacy ----------
conn2_top = frameB_bottom + 16
conn2_bottom = conn2_top + 40
arrow(CX, frameB_bottom, CX, conn2_bottom)
emit(f'<text class="conn-label" x="{CX}" y="{(conn2_top+conn2_bottom)/2 + 4}" text-anchor="middle">Step 8, continued &mdash; the closing checks inside the same subagent run</text>')

step8_items = [
    ("c1", "horizon.py", "per participant", False, True),
    ("c2", "record_death.py", "if either participant ended", False, True),
    ("c3", "death-legacy roll", "if either died early", True, True),
    ("c4", "apply_death_legacy.py", "only if c3 passed", False, True),
    ("c5", "reproduction check", "eligibility, then the roll", True, True),
    ("c6", "generate_offspring.py", "only if c5 reproduces", False, True),
]
labelC_top = conn2_bottom + 20
emit(f'<text class="phase-label roll" x="{LEFT}" y="{labelC_top+LABEL_H-8}">/ENACT &middot; STEP 8 &middot; points 6&ndash;8</text>')
chainC_start = labelC_top + LABEL_H + 10
chainC_bottom = chain(step8_items, chainC_start, left=LEFT)
frameC_top = labelC_top - 4
frameC_bottom = chainC_bottom + FRAME_PAD_BOT
emit(f'<rect class="section-frame roll" x="{FRAME_LEFT}" y="{frameC_top}" width="{FRAME_RIGHT-FRAME_LEFT}" height="{frameC_bottom-frameC_top}" rx="10"/>')

register("c1", "8", "horizon.py",
    "py scripts/lore/horizon.py <slug>",
    "band: early/established/late, lived, ending: true/false",
    "Run for both participants. life.lived was already incremented inside Step 8 point 5 by now — "
    "this call only reads what's already on record.")
register("c2", "8", "record_death.py",
    "py scripts/lore/record_death.py <slug> [--cause \"<text>\"]",
    "sets life.deceased: true, writes a _lore/tales/ entry, notifies 30% of the deceased's circle",
    "Only runs for a participant whose horizon.py just read ending: true.")
register("c3", "8", "death-legacy roll",
    "py scripts/lore/roll_death_legacy.py --candidates <notified slug> [...]",
    "passes: true/false, recipient",
    "Only rolled if the death was “early” (band read “established,” not "
    "“late”) AND the notified circle isn't empty. Odds: 40% (odds_percent.death_legacy). "
    "Added 2026-08-27 — the one piece of the old /simulate Phase C that /enact didn't already have.")
register("c4", "8", "apply_death_legacy.py",
    "py scripts/lore/apply_death_legacy.py --deceased <slug> --recipient <slug>",
    "copies the deceased's arc onto the recipient",
    "The roll itself (c3) deliberately leaves the actual transfer undone — about/needs/premise "
    "carried over, resolution reset to “ongoing,” tally reset; the recipient's own context/"
    "routine stay theirs.")
register("c5", "8", "reproduction check",
    "py scripts/lore/simulate_pass_reproduction.py --p1 <slug> --p2 <slug> --pass-number <N>",
    "eligible: true/false, reproduces: true/false, name_lead, other_parent",
    "Moved here 2026-08-28 — point 8, new. Used to run pre-scene inside Step 4's own "
    "simulate_pass_brief.py call, so a birth could be dramatized inside the scene itself; now runs "
    "strictly after the scene, hearsay, and shock resolution, so a birth becomes a short coda "
    "instead. Eligibility (partner_threshold, parent_cooldown_passes, not already related) is plain "
    "arithmetic; only then does the roll itself run, at 40% odds (odds_percent.reproduction).")
register("c6", "8", "generate_offspring.py",
    "py scripts/lore/generate_offspring.py --parent-a <slug> --parent-b <slug> "
    "--name \"<composed name>\" --pass-number <N>",
    "writes a tales.entries birth tale; handles knowledge inheritance in the same call",
    "The name blend (leading from c5's name_lead) is the one thing about a birth that can't be "
    "scripted. Also rewrite the inherited routine's routine_actions line so it reads as this "
    "child's own progression of actions, not a verbatim copy of the parent's, then write a short "
    "coda after the scene announcing the birth.")

# ---------- STEP 9 / STEP 10 closing (brief) ----------
conn3_top = frameC_bottom + 16
conn3_bottom = conn3_top + 40
arrow(CX, frameC_bottom, CX, conn3_bottom)
emit(f'<text class="conn-label" x="{CX}" y="{(conn3_top+conn3_bottom)/2 + 4}" text-anchor="middle">Steps 9&ndash;10, same subagent run</text>')

step910_items = [
    ("s9", "Step 9 — synthesis", "check_resonance.py narrows, the model judges", False, True),
    ("s10", "Step 10 — record update", "knowledge.experience, criterion/life already written", False, True),
]
label910_top = conn3_bottom + 6
chain910_bottom = chain(step910_items, label910_top, left=LEFT)
frame910_top = label910_top - 12
frame910_bottom = chain910_bottom + FRAME_PAD_BOT
emit(f'<rect class="section-frame judge" x="{FRAME_LEFT}" y="{frame910_top}" width="{FRAME_RIGHT-FRAME_LEFT}" height="{frame910_bottom-frame910_top}" rx="10"/>')

register("s9", "9", "Synthesis", "py scripts/lore/check_resonance.py <slug> --hearsay-id <entry_id>",
    "candidate pairs across five subtypes, for the model to judge",
    "Most candidates should produce nothing — the default is silence. See /enact Step 9 for the "
    "full mechanical-narrowing-then-model-judges division of labor.")
register("s10", "10", "Update the character record", None,
    "name/city/backstory/knowledge.education (first time only), knowledge.experience appended",
    "criterion/life are typically already written by Step 8's own calls — this step doesn't "
    "re-touch them.")

# ============================================================================
# SIMULATE'S OWN LOOP -- post-dispatch half, then loop back
# ============================================================================
conn4_top = frame910_bottom + 16
conn4_bottom = conn4_top + 40
arrow(CX, frame910_bottom, CX, conn4_bottom)
emit(f'<text class="conn-label" x="{CX}" y="{(conn4_top+conn4_bottom)/2 + 4}" text-anchor="middle">subagent returns its short summary to /simulate</text>')

simB_items = [
    ("simsafety", "safety net", "reverts any leaked mid-pass state", False, False),
    ("simlog", "log the pass", "advances the pool; drop anyone who died", False, False),
]
labelSimB_top = conn4_bottom + 20
emit(f'<text class="phase-label roll" x="{LEFT}" y="{labelSimB_top+LABEL_H-8}">/SIMULATE &middot; BOOKKEEPING</text>')
chainSimB_start = labelSimB_top + LABEL_H + 10
chainSimB_bottom = chain(simB_items, chainSimB_start, left=LEFT)
frameSimB_top = labelSimB_top - 4
frameSimB_bottom = chainSimB_bottom + FRAME_PAD_BOT
emit(f'<rect class="section-frame roll" x="{FRAME_LEFT}" y="{frameSimB_top}" width="{FRAME_RIGHT-FRAME_LEFT}" height="{frameSimB_bottom-frameSimB_top}" rx="10"/>')

register("simsafety", "Simulate", "Safety net", None,
    "auto-reverts any pass content that leaked into the main repo instead of the worktree",
    "git -C \"<main repo root>\" status --short -- _lore/ _npcs/ directly, revert any leaked path "
    "found, without asking, before moving to the next pass.")
register("simlog", "Simulate", "Log the pass", None,
    "the running in-conversation log gains one more line; anyone who died drops from the pool",
    "Pure bookkeeping — nothing written to disk here beyond what /enact's own calls already wrote. "
    "At the natural end of a batch (not every pass), also runs build_source_index.py once.")

loop_start_y = frameSimB_bottom + 30
loop_end_y = gate_top - 4
arrow(CX, frameSimB_bottom, CX, loop_start_y)
emit(f'<path class="loop-line" d="M{FRAME_RIGHT+8},{loop_start_y} Q{LOOP_X},{loop_start_y} {LOOP_X},{loop_start_y-40} L{LOOP_X},{loop_end_y+40} Q{LOOP_X},{loop_end_y} {FRAME_RIGHT+8},{loop_end_y}" marker-end="url(#arrow-loop)"/>')
mid_loop_y = (loop_start_y + loop_end_y) / 2
emit(f'<text class="loop-label" x="{LOOP_X+14}" y="{mid_loop_y}" transform="rotate(90 {LOOP_X+14} {mid_loop_y})" text-anchor="middle">&#8635; next pass &mdash; while the living pool holds &ge; 2</text>')

total_h = int(loop_start_y + 20)

body = "\n".join(buf)

defs = '''<defs>
  <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
    <path d="M0,0 L10,5 L0,10 z" fill="var(--ink-soft)"/>
  </marker>
  <marker id="arrow-loop" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
    <path d="M0,0 L10,5 L0,10 z" fill="var(--roll)"/>
  </marker>
</defs>'''

aria_label = ("Flowchart of the simulate/enact mechanism, single linear path, no fork. Simulate's own "
    "loop gate checks the living pool, then simulate_resolve_pair.py draws a pair and resolves any "
    "lead-override, then dispatches one subagent to run enact end to end. Enact's own flow: a fork on "
    "player versus another character, where the player path exits immediately to freeform Step 5a; "
    "the other-character path passes an eligibility gate requiring routines and arc on both files, "
    "stopping and flagging if either is missing. Once eligible, Step 4 runs one script call handling "
    "ten mechanical sub-decisions in order, rewritten 2026-08-28: partner tracking first, then a "
    "coin-flip roll for who's home versus visiting, then a routine roll for the home participant "
    "only, then location and context assembly, then arc primacy decided independently of who "
    "traveled, then needs/provides keyed to the primacy winner, then contested, the alignment gate, "
    "and a now contested-aware outcome roll, then the arc tally. Reproduction is no longer part of "
    "this call. Step 5b reads the resulting brief, fills or skips two optional judgment slots, then "
    "always writes the scene, itself covering the transcript save, hearsay update, and character "
    "record steps. Step 8 continued runs horizon, death, the death-legacy roll and its apply step, "
    "and now a post-scene reproduction check and its own offspring-generation step. Steps 9 and 10 "
    "close the pass. Control returns to simulate for a safety-net check and pass logging, then loops "
    "back to the top for as long as two or more characters remain alive. Every step can be clicked "
    "for its exact command and what it reads or writes.")
svg = (f'<svg viewBox="0 0 {W} {total_h}" width="{W}" height="{total_h}" '
    f'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{html.escape(aria_label)}">\n'
    f'{defs}\n{body}\n</svg>')

import pathlib
HTML_PATH = pathlib.Path(__file__).resolve().parent / "simulate-pass.html"
doc = HTML_PATH.read_text(encoding="utf-8")

svg_start = doc.index("<svg")
svg_end = doc.index("</svg>") + len("</svg>")
doc = doc[:svg_start] + svg + doc[svg_end:]

data_marker = 'id="diagram-details-data"'
data_tag_start = doc.index("<script " + data_marker)
data_open_end = doc.index(">", data_tag_start) + 1
data_close = doc.index("</script>", data_open_end)
details_js = "\nwindow.DIAGRAM_DETAILS = " + json.dumps(DETAILS, indent=2, ensure_ascii=False) + ";\n"
doc = doc[:data_open_end] + details_js + doc[data_close:]

HTML_PATH.write_text(doc, encoding="utf-8")

print("total_h=", total_h)
print(f"{len(DETAILS)} node details registered")
print(f"spliced into {HTML_PATH}")

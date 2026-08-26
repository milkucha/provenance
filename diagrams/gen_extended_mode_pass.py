import html
import json

EM_DASH = chr(0x2014)
RSQUO = chr(0x2019)

def esc(s):
    s = html.escape(s)
    s = s.replace(EM_DASH, '&mdash;').replace(RSQUO, '&rsquo;')
    return s

W = 780
LEFT = 170
RIGHT = 630
BOXW = RIGHT - LEFT
CX = (LEFT + RIGHT) // 2  # 400
CORRIDOR_X = 104
LOOP_X = 710

BOX_H = 30
VGAP = 44   # gap between chain boxes (arrow length) -- wide flow-diagram spacing

buf = []
def emit(s): buf.append(s)

DETAILS = {}  # node id -> detail payload, spliced into the HTML as a JS data block

def arrow(x1, y1, x2, y2, cls="flow-line", marker=True):
    m = ' marker-end="url(#arrow)"' if marker else ''
    emit(f'<path class="{cls}" d="M{x1},{y1} L{x2},{y2}"{m}/>')

def register(node_id, phase, title, script, returns, note=None, substeps=None):
    DETAILS[node_id] = {
        "phase": phase, "title": title, "script": script, "returns": returns,
        "note": note, "substeps": substeps,
    }

def node_open(node_id, hover):
    emit(f'<g class="clickable" tabindex="0" role="button" data-node-id="{node_id}" onclick="showDetail(\'{node_id}\', event)">')
    emit(f'  <title>{esc(hover)}</title>')

def node_close():
    emit('</g>')

def chain_node(top, n, node_id, title, desc, roll=False, has_script=True, hover=None):
    node_open(node_id, hover or f"{title} — {desc}. Click for the exact command.")
    emit(f'  <rect class="nbox" x="{LEFT}" y="{top}" width="{BOXW}" height="{BOX_H}" rx="5"/>')
    if roll:
        emit(f'  <rect class="stripe" x="{LEFT+1}" y="{top+1}" width="4" height="{BOX_H-2}"/>')
    cy = top + BOX_H/2
    emit(f'  <circle class="badge-circle" cx="192" cy="{cy}" r="9"/>')
    emit(f'  <text class="badge-text" x="192" y="{cy}">{n}</text>')
    title_span = f'<tspan font-weight="600">{esc(title)}</tspan> &mdash; {esc(desc)}'
    if not has_script:
        title_span += ' <tspan class="no-script-tag">&middot; no separate script</tspan>'
    emit(f'  <text class="ntitle" x="212" y="{cy}">{title_span}</text>')
    node_close()

def chain(items, start_y, start_n=1):
    """items: list of (node_id, title, desc, roll_bool, has_script_bool). Returns bottom y of last node."""
    y = start_y
    for i, (node_id, title, desc, roll, has_script) in enumerate(items, start_n):
        chain_node(y, i, node_id, title, desc, roll, has_script)
        bottom = y + BOX_H
        if i < start_n + len(items) - 1:
            arrow(CX, bottom, CX, bottom + VGAP)
        y = bottom + VGAP
    return start_y + len(items) * BOX_H + (len(items)-1) * VGAP

# ---------- PHASE A ----------
phaseA_items = [
    ("a1",  "pick_pair.py", "draws the pair", True, True),
    ("a2",  "lead-override check", "does an expiring lead still apply", True, True),
    ("a3",  "routine rolls", "which routines actually fire this pass", True, True),
    ("a4",  "location resolution", "where the scene lands", False, True),
    ("a5",  "context / texture lookup", "flavor for the scene brief", False, False),
    ("a6",  "needs/provides check", "motivation match between the pair", False, True),
    ("a7",  "contested roll", "does a rival try to hinder", True, True),
    ("a8",  "arc primacy roll", "whose arc leads the scene", True, True),
    ("a9",  "knowledge/criteria gate", "is this pair even eligible", False, True),
    ("a10", "arc-outcome roll", "advances or resolves the lead arc", True, True),
    ("a11", "arc tally vs. threshold", "complete / transform / failed / ongoing", False, False),
    ("a12", "partner tracking", "records who's paired this pass", False, True),
    ("a13", "reproduction eligibility + roll", "does this pass produce a birth", True, True),
]

register("a1", "A", "pick_pair.py",
    "py scripts/lore/pick_pair.py <every slug in the living pool>",
    "participant_1, participant_2",
    "A genuine uniform draw over the pool — not the model's own guess at “random”, which "
    "skews toward whichever names are most salient in context.")
register("a2", "A", "lead-override check",
    "py scripts/lore/roll_lead_followup.py --leads <target1> [<target2> ...]",
    "followed: true/false, plus which lead",
    "Only runs at all if participant_1 is carrying an unexpired leads entry (younger than "
    "lead_expiry_passes — 8, from _lore/tuning.json). A true result forces mode: visit toward that "
    "target and consumes the lead — participant_2 for this pass is overridden to the lead's target.")
register("a3", "A", "routine rolls",
    "py scripts/lore/roll_routine.py <location:weight> [<location:weight> ...]",
    "the routine that fires",
    "Called once (forced-visit pass) or twice (an ordinary pairing, one roll per participant) against "
    "each character's own routines[] weights.")
register("a4", "A", "location resolution",
    "py scripts/lore/resolve_location.py --p1 <slug> --p1-routine <loc> --p2 <slug> --p2-routine <loc>",
    "mode, location, home_frame, traveler",
    "Decides whether this pass is a home-turf pairing or a visit, and who's travelling to whom.")
register("a5", "A", "context / texture lookup",
    None,
    "context, texture, provides",
    "Not a script call — a plain dict lookup in _lore/contexts.json, done inline inside "
    "resolve_location() itself: it already has the resolved location and the home-frame character's "
    "own routines by construction, so a caller never needed a step of its own.")
register("a6", "A", "needs/provides check",
    "py scripts/lore/check_needs_provides.py --needs <tag> [...] --provides <tag> [...]",
    "match: true/false, matched_need, matched_provide",
    "Only runs on a visit whose traveler has an ongoing arc with needs — checked against this "
    "location's provides tags.")
register("a7", "A", "contested roll",
    "py scripts/lore/roll_contested.py",
    "contested: true/false",
    "Only rolled when the visit was motivated (a6 matched). Odds: 15% (_lore/tuning.json "
    "odds_percent.contested).")
register("a8", "A", "arc primacy roll",
    "py scripts/lore/roll_arc_primacy.py --p1 <slug> --p2 <slug>",
    "primary: whichever slug leads this scene's arc",
    "Decides whose arc gets to advance/resolve this pass — the loser's own arc sits out.")
register("a9", "A", "knowledge/criteria gate",
    "py scripts/lore/check_arc_alignment.py --arc-about <tag> [...] --arc-needs <tag> [...] "
    "--peer-standard \"<text>\" --peer-wasted-life \"<text>\" --peer-knowledge-item <item> [...]",
    "gate: hit/miss, inclined: advance/hinder/neutral, matched_about",
    "Only runs when the primacy winner already has an ongoing arc — checks whether the OTHER "
    "participant's own knowledge/criterion actually touches it at all.")
register("a10", "A", "arc-outcome roll",
    "py scripts/lore/roll_arc_outcome.py --inclined <advance|hinder|neutral>",
    "outcome: advance/stall/reverse",
    "Only rolled when the gate hit (a9). Resolved before the scene is written on purpose — writing "
    "dialogue first and rolling after risks the roll contradicting what was already dramatized.")
register("a11", "A", "arc tally vs. threshold",
    None,
    "tally_result: complete/transform/failed/ongoing",
    "Not a script call — plain arithmetic (score the outcome history since the last transform, "
    "compare against arc_resolution_threshold: 3 from _lore/tuning.json). A transform additionally "
    "needs a matched_about from the gate check (a9); without one a failing tally resolves the arc "
    "“failed” outright.")
register("a12", "A", "partner tracking",
    "py scripts/lore/record_partner.py <slug> --with <other slug>",
    "(no return value — pure bookkeeping)",
    "Called twice, once per direction (p1→p2 and p2→p1) — this is what a13's eligibility "
    "check reads back.")
register("a13", "A", "reproduction eligibility + roll",
    "py scripts/lore/roll_reproduction.py --p1 <slug> --p2 <slug>",
    "reproduces: true/false, name_lead",
    "Eligibility itself is inline arithmetic, not a script: either direction's partner count "
    ">= partner_threshold (5), neither parent within parent_cooldown_passes (10) of their last birth, "
    "neither already lists the other as a parent. Only if all three hold does the roll above actually "
    "run. Odds when it does: 40% (odds_percent.reproduction).")

FRAME_PAD_TOP = 26
FRAME_PAD_BOT = 22
LABEL_H = 26

y = 30
frameA_top = y
emit(f'<text class="phase-label roll" x="{LEFT}" y="{y+LABEL_H-8}">PHASE A &middot; simulate_pass_brief.py &mdash; one call, before the scene</text>')
chainA_start = y + LABEL_H + 10
chainA_bottom = chain(phaseA_items, chainA_start)
frameA_bottom = chainA_bottom + FRAME_PAD_BOT
FRAME_RIGHT = LOOP_X - 20
emit(f'<rect class="section-frame roll" x="44" y="{frameA_top-4}" width="{FRAME_RIGHT-44}" height="{frameA_bottom-frameA_top+4}" rx="10"/>')

# connector A -> B
conn1_top = frameA_bottom + 16
conn1_bottom = conn1_top + 74
arrow(CX, frameA_bottom, CX, conn1_bottom)
emit(f'<text class="conn-label" x="{CX}" y="{(conn1_top+conn1_bottom)/2 - 6}" text-anchor="middle">writes <tspan class="mono">.simulate_pass_brief.json</tspan></text>')
emit(f'<text class="conn-label" x="{CX}" y="{(conn1_top+conn1_bottom)/2 + 13}" text-anchor="middle">flags which of the four slots below are open</text>')

# ---------- PHASE B ----------
labelB_top = conn1_bottom + 20
emit(f'<text class="phase-label judge" x="{LEFT}" y="{labelB_top+LABEL_H-8}">PHASE B &middot; one subagent dispatch</text>')
hub_top = labelB_top + LABEL_H + 10
hub_bottom = hub_top + BOX_H
emit(f'<rect class="nbox hub" x="{LEFT}" y="{hub_top}" width="{BOXW}" height="{BOX_H}" rx="5"/>')
emit(f'<text class="ntitle" x="{CX}" y="{hub_top+BOX_H/2}" text-anchor="middle">reads <tspan class="mono" font-weight="600">.simulate_pass_brief.json</tspan></text>')

j0 = hub_bottom + 40
arrow(CX, hub_bottom, CX, j0)
emit(f'<circle class="junction" cx="{CX}" cy="{j0}" r="3"/>')

gated = [
    ("brepro", "Name the newborn",
        "generate_offspring.py — blends both parents’ names, led by the dice-chosen side",
        "reproduction_slot open"),
    ("barc", "Author the arc (fallback)",
        "write_arc.py — scoped to the character’s own horizon band",
        "arc_authoring_needed open"),
    ("brival", "Maybe name a rival",
        "apply_contested_lead.py — only if the scene points at someone who already has a file",
        "contested_hinder_slot open (optional even then)"),
]

register("brepro", "B", "Name the newborn",
    "py scripts/lore/generate_offspring.py --parent-a <slug> --parent-b <slug> "
    "--name \"<composed name>\" --pass-number <N>",
    "writes a tales.entries birth tale (id: birth_of_<key>); handles knowledge inheritance in the "
    "same call",
    "The name blend itself is the one thing about a birth that can't be scripted — the subagent "
    "composes it, leading from name_lead's side, before making this call. Tag the birth-announcement "
    "hearsay claim about: \"tale: birth_of_<key>\", never a made-up concept tag.")
register("barc", "B", "Author the arc",
    "py scripts/lore/write_arc.py <slug> --about \"<tag>\" [...] --needs \"<tag>\" [...] "
    "--context <name> --premise \"<text>\"",
    "writes the arc AND registers its concept: <id> tag in encodings.json, in one call",
    "As of 2026-08-16 this is the FALLBACK path, not the normal way arcs come to exist — "
    "/character Step 8 now authors a character's arc at creation time by default. This slot only "
    "still fires for a newborn from generate_offspring.py (which never assigns one) or a re-author "
    "after the prior arc resolved “failed” or “complete”. The subagent composes "
    "about/needs/context/premise per /character Step 8's own authoring discipline before calling this.")
register("brival", "B", "Maybe name a rival",
    "py scripts/lore/apply_contested_lead.py --traveler <slug> --rival <slug> --supplier <slug> "
    "--matched-provide \"<tag>\" --pass-number <N>",
    "writes a leads entry on the traveler's file and a fixed attributed note on the rival's file",
    "Genuinely optional even when the slot is open: a rival is only named if the scene plausibly "
    "points at a SPECIFIC character who already has a file. The default and common case is to leave "
    "it ambient/unnamed — this script is then never called at all. The note text is fixed, never "
    "invented prose: “According to <supplier>, <rival> already claimed <matched_provide> before "
    "<traveler> arrived.”")

GBOX_H = 46
GATE_PRE_GAP = 32     # junction -> box top
GATE_POST_GAP = 54    # box bottom -> next junction
STAGE_H = GATE_PRE_GAP + GBOX_H + GATE_POST_GAP

j = j0
for node_id, title, desc, cond in gated:
    box_top = j + GATE_PRE_GAP
    box_bottom = box_top + GBOX_H
    j_next = j + STAGE_H
    # main path
    arrow(CX, j, CX, box_top)
    emit(f'<text class="cond-label" x="{CX+14}" y="{j+12}">{esc(cond)}</text>')
    node_open(node_id, f"{title}. Click for the exact command.")
    emit(f'<rect class="nbox gated" x="{LEFT}" y="{box_top}" width="{BOXW}" height="{GBOX_H}" rx="6"/>')
    emit(f'<text class="ntitle" x="{LEFT+18}" y="{box_top+18}"><tspan font-weight="600">{esc(title)}</tspan></text>')
    emit(f'<text class="nsub" x="{LEFT+18}" y="{box_top+35}">{esc(desc)}</text>')
    node_close()
    arrow(CX, box_bottom, CX, j_next)
    emit(f'<circle class="junction" cx="{CX}" cy="{j_next}" r="3"/>')
    # corridor bypass
    corridor_mid_top = j + 22
    corridor_mid_bottom = j_next - 22
    emit(f'<path class="corridor-line" d="M{CX},{j} Q{CORRIDOR_X+40},{j+8} {CORRIDOR_X},{corridor_mid_top} L{CORRIDOR_X},{corridor_mid_bottom} Q{CORRIDOR_X+40},{j_next-8} {CX},{j_next}" marker-end="url(#arrow)"/>')
    emit(f'<text class="skip-label" x="{CORRIDOR_X-8}" y="{(corridor_mid_top+corridor_mid_bottom)/2}" text-anchor="end">not open</text>')
    j = j_next

# always node
always_top = j + 32
always_h = 50
always_bottom = always_top + always_h
arrow(CX, j, CX, always_top)
emit(f'<text class="cond-label always" x="{CX+14}" y="{j+12}">always</text>')
scene_hover = "Write the scene — /enact Steps 3b, 5, 5b, 6. Click to see each sub-step."
node_open("bscene", scene_hover)
emit(f'<rect class="nbox always" x="{LEFT}" y="{always_top}" width="{BOXW}" height="{always_h}" rx="6"/>')
emit(f'<text class="ntitle" x="{LEFT+18}" y="{always_top+18}"><tspan font-weight="600">Write the scene</tspan></text>')
emit(f'<text class="nsub" x="{LEFT+18}" y="{always_top+35}">/enact Steps 3b, 5, 5b, 6 &mdash; dialogue, hearsay mutation, shock, drift</text>')
node_close()

register("bscene", "B", "Write the scene",
    None,
    "the scene transcript, a hearsay entry, and any criterion/life update — all on the "
    "participants' own character files",
    "The only one of the four judgment slots that's never skipped — this is the actual mechanism "
    "being exercised, run in full, never shortened for speed.",
    substeps=[
        {"step": "3b", "label": "Enact both characters",
         "detail": "Write the full scene as one message, alternating clearly labeled turns, each "
                    "character honoring their own bounded knowledge sample independently. Bring it to "
                    "a natural stopping point rather than running indefinitely."},
        {"step": "5", "label": "Update the hearsay record",
         "detail": "Record each character's mutated interpretation, not what was objectively said — "
                    "framing, emphasis, and moral judgment all filtered through their criterion/trusts/"
                    "distrusts. Written via py scripts/lore/record_hearsay.py --json-file <path>."},
        {"step": "5b", "label": "Resolve shocks, drift, and the scene count",
         "detail": "py scripts/lore/check_anchor_reference.py gates whether any claim actually touches "
                    "a participant's criterion.anchor; if so, resolve reject/reinterpret/break and "
                    "record it (plus the life.lived+1 every participant gets regardless) via "
                    "py scripts/lore/update_character.py. Runs py scripts/lore/horizon.py again "
                    "afterward to check for an ending, and py scripts/lore/record_death.py if so."},
        {"step": "6", "label": "Update the character record",
         "detail": "Append knowledge.experience for anything the scene established beyond the original "
                    "sample, via py scripts/lore/update_character.py --add-experience / "
                    "--add-grounded-experience. criterion/life are typically already written by Step "
                    "5b's own calls by this point."},
    ])

ret_top = always_bottom + 40
ret_bottom = ret_top + BOX_H
arrow(CX, always_bottom, CX, ret_top)
emit(f'<rect class="nbox hub" x="{LEFT}" y="{ret_top}" width="{BOXW}" height="{BOX_H}" rx="5"/>')
emit(f'<text class="ntitle" x="{CX}" y="{ret_top+BOX_H/2}" text-anchor="middle">returns a short summary to the orchestrator</text>')

frameB_top = labelB_top - 4
frameB_bottom = ret_bottom + FRAME_PAD_BOT
emit(f'<rect class="section-frame judge" x="44" y="{frameB_top}" width="{FRAME_RIGHT-44}" height="{frameB_bottom-frameB_top}" rx="10"/>')

# connector B -> C
conn2_top = frameB_bottom + 16
conn2_bottom = conn2_top + 44
arrow(CX, frameB_bottom, CX, conn2_bottom)
emit(f'<text class="conn-label" x="{CX}" y="{(conn2_top+conn2_bottom)/2 + 4}" text-anchor="middle">reads the brief back for who was in the scene &mdash; nothing to retype</text>')

# ---------- PHASE C ----------
phaseC_items_script = [
    ("c1", "horizon.py", "per participant", False, True),
    ("c2", "record_death.py", "if either participant ended", False, True),
    ("c3", "death-legacy roll", "if either died early", True, True),
]
phaseC_items_orch = [
    ("c4", "safety net", "reverts any leaked mid-pass state", False, False),
    ("c5", "log the pass", "advances the pool", False, False),
    ("c6", "build_source_index.py", "batch end only", False, True),
]
labelC_top = conn2_bottom + 20
emit(f'<text class="phase-label roll" x="{LEFT}" y="{labelC_top+LABEL_H-8}">PHASE C &middot; simulate_pass_resolve.py &mdash; one call, after the scene</text>')
chainC_start = labelC_top + LABEL_H + 10
chainC1_bottom = chain(phaseC_items_script, chainC_start, start_n=1)

sub_gap = 60
sub_label_y = chainC1_bottom + 30
chainC2_start = chainC1_bottom + sub_gap
arrow(CX, chainC1_bottom, CX, chainC2_start)
emit(f'<text class="conn-label" x="{CX}" y="{sub_label_y}" text-anchor="middle">orchestrator, after the script above returns &mdash; not part of that one call</text>')

chainC2_bottom = chain(phaseC_items_orch, chainC2_start, start_n=4)
chainC_bottom = chainC2_bottom
frameC_top = labelC_top - 4
frameC_bottom = chainC_bottom + FRAME_PAD_BOT
emit(f'<rect class="section-frame roll" x="44" y="{frameC_top}" width="{FRAME_RIGHT-44}" height="{frameC_bottom-frameC_top}" rx="10"/>')

register("c1", "C", "horizon.py",
    "py scripts/lore/horizon.py <slug>",
    "band: early/established/late, lived, ending: true/false",
    "Run for both participants. life.lived was already incremented inside the subagent's own Step 5b "
    "work — this call only reads what's already on record.")
register("c2", "C", "record_death.py",
    "py scripts/lore/record_death.py <slug> [--cause \"<text>\"]",
    "sets life.deceased: true, writes a _lore/tales/ entry, notifies 30% of the deceased's circle",
    "Only runs for a participant whose horizon.py just read ending: true. Prints which notified "
    "characters are shock candidates, for a future pass's own Step 5b judgment.")
register("c3", "C", "death-legacy roll",
    "py scripts/lore/roll_death_legacy.py --candidates <notified slug> [...]",
    "passes: true/false, recipient",
    "Only rolled if the death was “early” in the structural sense horizon.py can report at this "
    "point (band read “established”, not “late”) AND the notified circle isn't empty. "
    "Odds: 40% (odds_percent.death_legacy). A true result copies the deceased's arc onto the recipient "
    "— about/needs/premise carried over, resolution reset to “ongoing”, tally reset; "
    "context/routine stay the recipient's own. Done inline in Python, not a further script call.")
register("c4", "C", "safety net",
    None,
    "auto-reverts any pass content that leaked into the main repo instead of the worktree",
    "Not part of simulate_pass_resolve.py — the orchestrator runs "
    "git -C \"<main repo root>\" status --short -- _lore/ _npcs/ directly and reverts any leaked path "
    "it finds, without asking, before moving to the next pass.")
register("c5", "C", "log the pass",
    None,
    "the running in-conversation log gains one more line",
    "Pure bookkeeping by the orchestrator — nothing written to disk here; SIMULATION_LOG.md itself "
    "is only written once, at the end of the whole batch (Step 4).")
register("c6", "C", "build_source_index.py",
    "py scripts/lore/build_source_index.py",
    "folds this batch's accumulated hearsay claims into each concept's own sources[]",
    "A separate script call the orchestrator makes only at the natural end of a batch — not after "
    "every single pass.")

# loop back
loop_start_y = frameC_bottom + 6
loop_end_y = frameA_top - 4
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

aria_label = ("Flowchart of one extended-mode pass. Phase A: simulate_pass_brief.py runs thirteen "
    "steps in order, seven of them dice rolls and two of them plain arithmetic or a lookup rather "
    "than a separate script, and writes a brief flagging which judgment slots are open. Phase B: a "
    "single subagent reads the brief, then for each of three optional slots either fills it or skips "
    "it via a bypass line, before always writing the scene, itself made of four /enact sub-steps. "
    "Phase C: simulate_pass_resolve.py runs three closing steps (one a death-legacy roll), then the "
    "orchestrator itself runs three more (a safety-net check, logging the pass, and an end-of-batch "
    "index rebuild) that are not part of that script call. A loop line on the right returns from the "
    "end of Phase C to the start of Phase A for as long as two or more characters remain alive. Every "
    "step can be clicked for its exact command and what it reads or writes.")
svg = (f'<svg viewBox="0 0 {W} {total_h}" width="{W}" height="{total_h}" '
    f'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{html.escape(aria_label)}">\n'
    f'{defs}\n{body}\n</svg>')

# Splice the freshly generated <svg>...</svg>, plus the DETAILS data block, into
# extended-mode-pass.html, which lives next to this script. Everything else in that file (header
# prose, legend, panel scaffold, interaction script, figcaption, closing notes) is hand-authored
# and left alone.
import pathlib
HTML_PATH = pathlib.Path(__file__).resolve().parent / "extended-mode-pass.html"
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
print("frameA", frameA_top, frameA_bottom)
print("frameB", frameB_top, frameB_bottom)
print("frameC", frameC_top, frameC_bottom)
print(f"{len(DETAILS)} node details registered")
print(f"spliced into {HTML_PATH}")

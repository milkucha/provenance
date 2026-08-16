import html

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
VGAP = 22   # gap between chain boxes (arrow length)

buf = []
def emit(s): buf.append(s)

def arrow(x1, y1, x2, y2, cls="flow-line", marker=True):
    m = ' marker-end="url(#arrow)"' if marker else ''
    emit(f'<path class="{cls}" d="M{x1},{y1} L{x2},{y2}"{m}/>')

def chain_node(top, n, title, desc, roll=False):
    emit(f'<g>')
    emit(f'  <rect class="nbox" x="{LEFT}" y="{top}" width="{BOXW}" height="{BOX_H}" rx="5"/>')
    if roll:
        emit(f'  <rect class="stripe" x="{LEFT+1}" y="{top+1}" width="4" height="{BOX_H-2}"/>')
    cy = top + BOX_H/2
    emit(f'  <circle class="badge-circle" cx="192" cy="{cy}" r="9"/>')
    emit(f'  <text class="badge-text" x="192" y="{cy}">{n}</text>')
    emit(f'  <text class="ntitle" x="212" y="{cy}"><tspan font-weight="600">{esc(title)}</tspan> &mdash; {esc(desc)}</text>')
    emit(f'</g>')

def chain(items, start_y):
    """items: list of (title, desc, roll_bool). Returns bottom y of last node."""
    y = start_y
    for i, (title, desc, roll) in enumerate(items, 1):
        chain_node(y, i, title, desc, roll)
        top = y
        bottom = y + BOX_H
        if i < len(items):
            arrow(CX, bottom, CX, bottom + VGAP)
        y = bottom + VGAP
    return start_y + len(items) * BOX_H + (len(items)-1) * VGAP

# ---------- PHASE A ----------
phaseA_items = [
    ("pick_pair.py", "draws the pair", True),
    ("lead-override check", "does an expiring lead still apply", True),
    ("routine rolls", "which routines actually fire this pass", True),
    ("location resolution", "where the scene lands", False),
    ("context / texture lookup", "flavor for the scene brief", False),
    ("needs/provides check", "motivation match between the pair", False),
    ("contested roll", "does a rival try to hinder", True),
    ("arc primacy roll", "whose arc leads the scene", True),
    ("knowledge/criteria gate", "is this pair even eligible", False),
    ("arc-outcome roll", "advances or resolves the lead arc", True),
    ("tally vs. threshold", "reproduction-scene count check", False),
    ("partner tracking", "records who's paired this pass", False),
    ("reproduction eligibility + roll", "does this pass produce a birth", True),
]

FRAME_PAD_TOP = 26
FRAME_PAD_BOT = 16
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
conn1_top = frameA_bottom + 10
conn1_bottom = conn1_top + 46
arrow(CX, frameA_bottom, CX, conn1_bottom)
emit(f'<text class="conn-label" x="{CX}" y="{(conn1_top+conn1_bottom)/2 - 4}" text-anchor="middle">writes <tspan class="mono">.simulate_pass_brief.json</tspan></text>')
emit(f'<text class="conn-label" x="{CX}" y="{(conn1_top+conn1_bottom)/2 + 11}" text-anchor="middle">flags which of the four slots below are open</text>')

# ---------- PHASE B ----------
labelB_top = conn1_bottom + 14
emit(f'<text class="phase-label judge" x="{LEFT}" y="{labelB_top+LABEL_H-8}">PHASE B &middot; one subagent dispatch</text>')
hub_top = labelB_top + LABEL_H + 10
hub_bottom = hub_top + BOX_H
emit(f'<rect class="nbox hub" x="{LEFT}" y="{hub_top}" width="{BOXW}" height="{BOX_H}" rx="5"/>')
emit(f'<text class="ntitle" x="{CX}" y="{hub_top+BOX_H/2}" text-anchor="middle">reads <tspan class="mono" font-weight="600">.simulate_pass_brief.json</tspan></text>')

j0 = hub_bottom + 24
arrow(CX, hub_bottom, CX, j0)
emit(f'<circle class="junction" cx="{CX}" cy="{j0}" r="3"/>')

gated = [
    ("Name the newborn", "generate_offspring.py — blends both parents’ names, led by the dice-chosen side", "reproduction_slot open"),
    ("Author the arc", "write_arc.py — scoped to the character’s own horizon band", "arc_authoring_needed open"),
    ("Maybe name a rival", "apply_contested_lead.py \u2014 only if the scene points at someone who already has a file", "contested_hinder_slot open (optional even then)"),
]

GBOX_H = 46
STAGE_H = 110  # junction to junction

j = j0
for title, desc, cond in gated:
    box_top = j + 20
    box_bottom = box_top + GBOX_H
    j_next = j + STAGE_H
    # main path
    arrow(CX, j, CX, box_top)
    emit(f'<text class="cond-label" x="{CX+14}" y="{j+12}">{esc(cond)}</text>')
    emit(f'<rect class="nbox gated" x="{LEFT}" y="{box_top}" width="{BOXW}" height="{GBOX_H}" rx="6"/>')
    emit(f'<text class="ntitle" x="{LEFT+18}" y="{box_top+18}"><tspan font-weight="600">{esc(title)}</tspan></text>')
    emit(f'<text class="nsub" x="{LEFT+18}" y="{box_top+35}">{esc(desc)}</text>')
    arrow(CX, box_bottom, CX, j_next)
    emit(f'<circle class="junction" cx="{CX}" cy="{j_next}" r="3"/>')
    # corridor bypass
    corridor_mid_top = j + 16
    corridor_mid_bottom = j_next - 16
    emit(f'<path class="corridor-line" d="M{CX},{j} Q{CORRIDOR_X+40},{j+8} {CORRIDOR_X},{corridor_mid_top} L{CORRIDOR_X},{corridor_mid_bottom} Q{CORRIDOR_X+40},{j_next-8} {CX},{j_next}" marker-end="url(#arrow)"/>')
    emit(f'<text class="skip-label" x="{CORRIDOR_X-8}" y="{(corridor_mid_top+corridor_mid_bottom)/2}" text-anchor="end">not open</text>')
    j = j_next

# always node
always_top = j + 20
always_h = 50
always_bottom = always_top + always_h
arrow(CX, j, CX, always_top)
emit(f'<text class="cond-label always" x="{CX+14}" y="{j+12}">always</text>')
emit(f'<rect class="nbox always" x="{LEFT}" y="{always_top}" width="{BOXW}" height="{always_h}" rx="6"/>')
emit(f'<text class="ntitle" x="{LEFT+18}" y="{always_top+18}"><tspan font-weight="600">Write the scene</tspan></text>')
emit(f'<text class="nsub" x="{LEFT+18}" y="{always_top+35}">/enact Steps 3b, 5, 5b, 6 &mdash; dialogue, hearsay mutation, shock, drift</text>')

ret_top = always_bottom + 24
ret_bottom = ret_top + BOX_H
arrow(CX, always_bottom, CX, ret_top)
emit(f'<rect class="nbox hub" x="{LEFT}" y="{ret_top}" width="{BOXW}" height="{BOX_H}" rx="5"/>')
emit(f'<text class="ntitle" x="{CX}" y="{ret_top+BOX_H/2}" text-anchor="middle">returns a short summary to the orchestrator</text>')

frameB_top = labelB_top - 4
frameB_bottom = ret_bottom + FRAME_PAD_BOT
emit(f'<rect class="section-frame judge" x="44" y="{frameB_top}" width="{FRAME_RIGHT-44}" height="{frameB_bottom-frameB_top}" rx="10"/>')

# connector B -> C
conn2_top = frameB_bottom + 10
conn2_bottom = conn2_top + 30
arrow(CX, frameB_bottom, CX, conn2_bottom)
emit(f'<text class="conn-label" x="{CX}" y="{(conn2_top+conn2_bottom)/2 + 4}" text-anchor="middle">reads the brief back for who was in the scene &mdash; nothing to retype</text>')

# ---------- PHASE C ----------
phaseC_items = [
    ("horizon.py", "per participant", False),
    ("record_death.py", "if either participant ended", False),
    ("death-legacy roll", "if either died early", True),
    ("safety net", "reverts any leaked mid-pass state", False),
    ("log the pass", "advances the pool", False),
    ("build_source_index.py", "batch end only", False),
]
labelC_top = conn2_bottom + 14
emit(f'<text class="phase-label roll" x="{LEFT}" y="{labelC_top+LABEL_H-8}">PHASE C &middot; simulate_pass_resolve.py &mdash; one call, after the scene</text>')
chainC_start = labelC_top + LABEL_H + 10
chainC_bottom = chain(phaseC_items, chainC_start)
frameC_top = labelC_top - 4
frameC_bottom = chainC_bottom + FRAME_PAD_BOT
emit(f'<rect class="section-frame roll" x="44" y="{frameC_top}" width="{FRAME_RIGHT-44}" height="{frameC_bottom-frameC_top}" rx="10"/>')

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
    "steps in order, seven of them dice rolls, and writes a brief flagging which judgment slots "
    "are open. Phase B: a single subagent reads the brief, then for each of three optional slots "
    "either fills it or skips it via a bypass line, before always writing the scene. Phase C: "
    "simulate_pass_resolve.py runs six closing steps, one a death-legacy roll. A loop line on the "
    "right returns from the end of Phase C to the start of Phase A for as long as two or more "
    "characters remain alive.")
svg = (f'<svg viewBox="0 0 {W} {total_h}" width="{W}" height="{total_h}" '
    f'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{html.escape(aria_label)}">\n'
    f'{defs}\n{body}\n</svg>')

# Splice the freshly generated <svg>...</svg> into extended-mode-pass.html,
# which lives next to this script. Everything else in that file (header
# prose, legend, figcaption, closing notes) is hand-authored and left alone.
import pathlib
HTML_PATH = pathlib.Path(__file__).resolve().parent / "extended-mode-pass.html"
doc = HTML_PATH.read_text(encoding="utf-8")
svg_start = doc.index("<svg")
svg_end = doc.index("</svg>") + len("</svg>")
doc = doc[:svg_start] + svg + doc[svg_end:]
HTML_PATH.write_text(doc, encoding="utf-8")

print("total_h=", total_h)
print("frameA", frameA_top, frameA_bottom)
print("frameB", frameB_top, frameB_bottom)
print("frameC", frameC_top, frameC_bottom)
print(f"spliced into {HTML_PATH}")

"""
Two-layer mechanical check feeding an arc scene, from the /simulate design debrief (2026-08-10).
Both layers are cheap word-overlap filters on purpose - coarse, not real NLP - the same discipline
as check_anchor_reference.py's pre-filter shape: mechanical gate first, model narrates what the
gate already decided, never the reverse.

Layer 1 - KNOWLEDGE GATES RELEVANCE. Does the peer actually know/possess anything relevant to this
arc at all? Checked against each of the peer's individual knowledge/experience items separately
(not one flattened blob), because a real match needs to point back at a SPECIFIC item and that
item's own `about` tags - this is what lets a transform (see roll_arc_outcome.py's docstring) copy
a new arc topic mechanically from something the peer actually said, instead of a model inventing
one. Most peers, most of the time, won't gate-match at all - that's deliberate, it's what keeps
"inclined" rare rather than constant, mirroring how the anchor-shock gate stays rare.

Layer 2 - CRITERIA DECIDES DIRECTION. Only runs if layer 1 already gate-matched. Checks the peer's
own wasted_life/standard text against the same tag pool: a wasted-life-only hit reads as "hinder",
a standard-only hit reads as "help", both is "mixed", a gate-hit-but-criteria-silent case still
counts as a real collision (useful to a transform) but has no help/hinder valence - "neutral".

Usage:
    py scripts/lore/check_arc_alignment.py \
        --arc-about "era_ensayo: Las Guerras de Gorff" --arc-about "concept: historiography" \
        --arc-needs "rare ore" \
        --peer-standard "text" --peer-wasted-life "text" \
        --peer-knowledge-item "Met a trader in Görff who deals in rare ore.::location: gorff,concept: trade" \
        --peer-knowledge-item "Heard the calendar in Lundria has two versions.::location: lundria"
"""

import argparse
import re

STOPWORDS = {
    "a", "an", "the", "of", "to", "in", "on", "at", "by", "for", "with", "without", "and", "or",
    "but", "not", "is", "are", "was", "were", "be", "been", "being", "this", "that", "their",
    "someone", "who", "what", "than", "as", "it", "its", "one", "spent", "life", "still", "has",
}


def significant_words(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z']+", text.lower())
    return {w for w in words if w not in STOPWORDS and len(w) > 2}


def parse_knowledge_item(entry: str) -> tuple[str, list[str]]:
    text, _, tags = entry.partition("::")
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    return text, tag_list


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--arc-about", action="append", default=[], help="Host/traveler arc's about tag(s), repeatable")
    parser.add_argument("--arc-needs", action="append", default=[], help="Arc's needs tag(s), repeatable")
    parser.add_argument("--peer-standard", default="", help="Peer's criterion.standard text")
    parser.add_argument("--peer-wasted-life", default="", help="Peer's criterion.wasted_life text")
    parser.add_argument(
        "--peer-knowledge-item", action="append", default=[],
        help='One peer knowledge/experience item as "TEXT::tag1,tag2", repeatable',
    )
    args = parser.parse_args()

    arc_words: set[str] = set()
    for tag in args.arc_about + args.arc_needs:
        arc_words |= significant_words(tag)

    # Layer 1: does any single knowledge item actually gate-match?
    matched_about: list[str] = []
    for entry in args.peer_knowledge_item:
        text, tags = parse_knowledge_item(entry)
        if significant_words(text) & arc_words:
            for tag in tags:
                if tag not in matched_about:
                    matched_about.append(tag)

    gate_hit = bool(matched_about)
    print(f"gate: {'hit' if gate_hit else 'miss'}")

    if not gate_hit:
        print("inclined: neutral")
        return

    # Layer 2: only evaluated because layer 1 already found something real to react to.
    wasted_hit = bool(significant_words(args.peer_wasted_life) & arc_words) if args.peer_wasted_life else False
    standard_hit = bool(significant_words(args.peer_standard) & arc_words) if args.peer_standard else False

    if wasted_hit and not standard_hit:
        print("inclined: hinder")
    elif standard_hit and not wasted_hit:
        print("inclined: help")
    elif wasted_hit and standard_hit:
        print("inclined: mixed")
    else:
        print("inclined: neutral")

    print(f"matched_about: {','.join(matched_about)}")


if __name__ == "__main__":
    main()

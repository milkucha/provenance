"""
Roll whether a retold hearsay claim keeps a traceable origin, or becomes untraceable oral lore.

Used by the /enact skill (SKILL.md Step 5) at the moment a character voices something drawn from a
sampled `hearsay` pool item (see README.md §8 Step 1 and scripts/sample_lore_knowledge.py). A flat
50/50 chance, independent of how many retellings deep the claim already is:

    traceable   - the new hearsay entry's claim sets "derived_from" to the sampled item's id, and
                  the dialog line may cite the source by name ("I heard Morkulo say...").
    untraceable - "derived_from" stays unset, "oral_lore" is set true, and the dialog line uses
                  vague in-character framing instead ("they say...", "it's told that...") - no named
                  source, on purpose.

Usage:
    python scripts/lineage_coin.py
    python scripts/lineage_coin.py --seed 42   # reproducible roll
"""

import argparse
from random import Random


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--seed", type=int, default=None, help="Optional seed, for a reproducible roll")
    args = parser.parse_args()

    rng = Random(args.seed)
    result = "traceable" if rng.random() < 0.5 else "untraceable"
    print(result)


if __name__ == "__main__":
    main()

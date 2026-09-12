# Facts — The Floor Everyone Stands On

The fourth source of truth for Milkantis, and the only one that is **never sampled**. Material,
hearsay, and tales are all sampled at random odds by `scripts/lore/sample_lore_knowledge.py`; grounding
is access-gated (by routine, by places visited) but still computed conditionally, never randomly. A
fact skips both mechanisms entirely: every character knows every fact here in full, from creation,
regardless of their education percent/mode/topic. There is no roll, no gate, no condition — a fact is
simply universal.

## The two facts on record

- **`life_is_finite`** — a life comes to an end, for the character and for everyone they meet. What's
  known and withheld is deliberately asymmetric: the fact of the end is known unconditionally, but the
  number itself lives in `_lore/characters/lifespans.json`, never in the character file `/enact` loads,
  and is only ever answered in coarse horizon bands (see `scripts/lore/horizon.py`).
- **`a_worthwhile_life`** — everyone wants their life to have been worth living, universally and
  without needing to be persuaded of it. What's withheld is the criterion itself: *what* worthwhile
  means is never universal, it's derived per character from the collision of their knowledge and
  backstory (see `criterion` in `_lore/characters/<key>.json` and `.claude/skills/character/SKILL.md`).

Together, per `README.md`'s §2 Core Concepts, these two are **the will to live**: time is short, and it
matters what the time was spent on.

## Facts are the checker, not the checked

Unlike every other category, a fact has no provenance, cannot be attributed, and cannot be dismissed —
it's the floor a character's contestable criterion stands on, not part of the argument. A hearsay claim
can be flagged `inconsistent_with_facts` (see `encodings.json`'s `hearsay._method_note`) by checking it
directly against the two entries in `facts.json`; no `fact_ref` id system is needed for that, since
there are only ever a couple of facts on record and checking just means reading the file. Facts
themselves are never flagged for consistency against anything else.

## Never sampled, never folded in

`facts.json` lives deliberately outside `_lore/encodings.json` and must never be folded into it.
`scripts/lore/sample_lore_knowledge.py` must never draw a fact into its random pool — a fact that could
be drawn at 5% odds would be a bug, per `facts.json`'s own `_comment`. Facts are loaded unconditionally
instead: by `/character` during criterion derivation, and by `/enact` for every character in every
scene.

## Recordkeeping

See `_authors.md` for real-world recordkeeping — which user added each fact, and when. That file is
not lore and is never read by any skill that plays a character.

# Grounding — What's Actually True, Whether or Not Anyone Knows It

The fifth source of truth for Milkantis, and the second one (after `_lore/facts/`) that isn't drawn
from `sample_lore_knowledge.py`'s random pool — but for a different reason than facts are exempt.

**Facts** are true of being a person in this world at all, embodiment-independent, and known by
*everyone, always* — no character could coherently be ignorant of them. **Grounding** is true of the
world *itself*, independent of anyone's knowledge of it, and access is *conditional* — a character
knows a piece of grounding only if they'd plausibly have encountered it, not automatically. That's a
genuinely different epistemic shape from both facts and ordinary sampled lore, which is why it gets
its own folder rather than folding into either.

## The Troy distinction — why this is separate from `_lore/material/`

`_lore/material/` is the *claim* about a place — excavated documents, maps, spreadsheets, hearsay,
told stories. Like the ancient texts describing Troy, material may or may not be true, and different
sources can disagree with each other (see `encodings.json`'s `conflicts`). **Grounding is the actual
ruins** — the world's real current state, independent of what anyone ever wrote or said about it.
Material and grounding are allowed to disagree, and that disagreement doesn't need reconciling: a
character can believe what the old maps say about a place and be wrong once they actually see it, or
vice versa. Neither corrects the other.

## Two files, two different "orders of reality" describing the same world

- **`mechanics.json`** — the rules of the current embodiment (Minecraft): what's dangerous, what a
  person needs to survive, how a thing is actually made. Hand-curated, tagged `embodiment: "minecraft"`
  so a future embodiment backend only has to swap this file's content, never the mechanism around it.
- **`world_state.json`** — the world's physical/material state: what's actually built where, a
  settlement's approximate extent, what's changed. Derived from an external region-file/machine-vision
  pipeline (outside this repo), which does its own description-generation before handing over JSON —
  nothing in this repo processes it further. Starts empty; see the file's own `_comment` for the
  intended entry shape once that pipeline delivers.

## Access is gated by routine, not randomly sampled and not universal

`scripts/lore/sample_grounding.py` computes this **live, every call, never cached** into a character
file — routines can be edited after creation (unlike `knowledge.education`, which is frozen for
life), so a creation-time snapshot would go stale the first time someone's routines change, and the
lookup is cheap enough that recomputing it costs nothing worth caching against.

- A `mechanics.json` entry marked `distribution: "universal"` is known by every character, same as a
  fact — but embodiment-scoped rather than personhood-scoped.
- A `distribution: "contextual"` entry is known only if it's tagged with something the character's
  own routine contexts provide, read from `_lore/contexts.json`'s `grounding_provides` field
  (parallel to that file's existing `provides` field, which drives arc-need matching via
  `check_needs_provides.py` — a different concern; don't conflate the two).
- A `world_state.json` entry is known if its `location` matches one of the character's own routine
  locations. (Once travel exists as a mechanic, this should extend to anywhere a character has
  actually traveled — not built yet.)

This is deliberately **not** `sample_lore_knowledge.py`'s random-percentage draw. That sparseness
exists on purpose, to create real gaps in social/historical knowledge. Grounding is the opposite
instinct: if it's yours — your trade, your home turf — you obviously know it, no dice roll involved.

## Attribution — the one way grounding differs from facts

Facts have no provenance and can't be cited. Grounding *can* be attributed, because a character's
access to it is first-hand: they know the church in Terfila is beautiful because they've seen it, not
because someone told them. That's a third kind of source, distinct from both a document (`material`)
and testimony (`hearsay`) — "I know this because I've experienced it myself." `build_source_index.py`
indexes both grounding files as their own sourced category (`grounding`), so a claim's `about` field
can resolve to `grounding: <id>` the same way it resolves to a location or concept — see that
script's own docstring for how the two-file load works, since it can't reuse the ordinary
`_categories`/`encodings.json` path (grounding deliberately lives outside encodings.json).

## The settlement-radius idea (not yet built)

A `world_state.json` entry can carry an approximate `center`/`radius` for a settlement. Two things
mentioned separately in `_lore/material/` that both fall inside the same radius *might* be the same
real place — but the system should only ever flag that as a mechanical possibility, never merge them
automatically. A character still has to notice and say so, in a scene or in reflection (see
`TODO.md`'s reflection entry) — same discipline `/resolve` already holds everywhere else in this
system: nothing gets decided silently.

`_authors.md`, matching `_lore/tales/_authors.md` and `_lore/facts/_authors.md`'s shape, tracks which
real user (or process) added each grounding entry, and when — real-world recordkeeping only, no
in-fiction meaning.

## Grounding on record

See `_authors.md` for the full list. As of this writing: 63 `mechanics.json` entries (an
exhaustive-but-lean pass over vanilla Minecraft 1.20.1, added 2026-08-26/27 — expand by hand as new
routine contexts need mechanics content they don't have yet, and see `TODO.md` for the deferred
mod-content question), 0 `world_state.json` entries (waiting on the external pipeline's first
delivery).

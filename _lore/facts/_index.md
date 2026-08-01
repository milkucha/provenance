# Facts — What Everyone Knows

The fifth source of truth for Milkantis, and the only one that is **not sampled**.

`material/`, `tale/`, and `discoveries/` all feed `_lore/analysis/encodings.json`, and everything in
`encodings.json` goes into the pool that `scripts/sample_lore_knowledge.py` draws from — which means
any given character knows it only at the odds of their education percentage. That is exactly right
for lore. It is exactly wrong for the handful of things that are true of *being a person in this
world at all*, which nobody learns and nobody can fail to know.

So facts live here instead, in `facts.json`, and:

- **Every character knows every fact, in full, from creation** — regardless of their education
  percentage, mode, or topic skew.
- **Facts are never folded into `encodings.json`.** Not into `locations`, `concepts`, `hearsay`, or
  anything else. `/integrate` must not absorb them, and `sample_lore_knowledge.py` must never see
  them. A fact that ends up in the pool is a bug, not a fact.
- **Facts are never hearsay and never contestable.** Unlike a tale, a discovery, or a claim, a fact
  has no provenance to attack and no `consistent_with_context` flag. A character cannot dismiss one,
  cannot have heard it wrong, and cannot cite who told them. Nobody told them.
- **Facts are exempt from a character's epistemology.** A criterion gives its holder a lean about
  which kinds of knowing carry weight — the record, testimony, what they saw themselves
  (`criterion.trusts`/`distrusts`, `/character` Step 4d). That lean governs claims. It never touches
  a fact. A character who distrusts everything written and everything said still knows their life
  will end.

That last rule is what makes facts load-bearing for the will to live. A criterion (what a character
counts as a life well spent) is built on an *anchor* that can be refuted; the facts underneath it
cannot be. They are the floor, not part of the argument.

Facts are read by `/character` (when deriving a criterion) and by `/enact` (as part of every
character's standing knowledge in every scene). One `.md` file per fact for the human-readable
version, plus the machine-readable entry in `facts.json` that the skills actually load.

## Facts on record

| Added | Title | File | Id |
|---|---|---|---|
| 2026-07-31 | Life is finite | `life_is_finite.md` | `life_is_finite` |
| 2026-07-31 | A life should be full and worthwhile | `a_worthwhile_life.md` | `a_worthwhile_life` |

## Adding a fact

There is no `/fact` skill yet (see `TODO.md`). For now, adding one by hand means: a new `.md` file
here, a new entry in `facts.json`, a new row in the table above — and a hard look at whether it
really belongs. The bar is high on purpose. A fact is not a widely-held belief, a cultural norm, or
something everyone in one city happens to know; all three of those are lore, and lore gets sampled.
A fact is something no character could coherently be ignorant of.

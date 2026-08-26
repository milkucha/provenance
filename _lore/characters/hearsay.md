# Hearsay — What Has Been Said

This is the second of two sources of truth in the Luminacion lore, and it is deliberately not the
same kind of source as the first.

`context.md` (and the associative index built from it, `encodings.json`) is the **objective
record**. It was built the way an archaeologist reconstructs a civilization: read every primary
document in `_lore/material/`, transcribe only what is actually there, flag contradictions instead
of resolving them, never invent.

`hearsay.md` is the **subjective record** — a running log of what individual characters have
actually said, in played-out Blabber dialogues, to each other or to a player. An NPC's knowledge is
bounded, personal, sometimes secondhand, and never guaranteed complete or correct, exactly like a
real person's (see README §8 for how that bound is set). The two records will often agree, because
the NPCs so far were built by sampling directly from the objective record. **They are not the same
thing, and should not be read as the same thing.** Nothing in this file is evidence for what
actually happened in Milkantis — it is evidence only for what a specific character, at a specific
moment, said they believed. When a claim here ever contradicts `context.md`, that is not an error to
reconcile — it's the interesting part, and it should be logged as a divergence, not silently fixed.

As of 2026-07-24, individual claims here are also part of the knowledge pool a new character can
sample from (`scripts/lore/sample_lore_knowledge.py`), at the same odds as any objective-record fact — so
a claim can now be repeated by a character who never touched the objective record at all, only heard
it from someone who'd heard it. Every time that happens, a coin flip (`scripts/lore/lineage_coin.py`,
flat 50/50) decides whether the retelling stays traceable or loses its origin: on a traceable roll,
the claim here is noted inline ("derived from `<claim id>`") and the dialog line may name the
source; on an untraceable roll, no origin is recorded at all, the dialog line uses vague framing
("they say...," "it's told that..."), and the claim is marked **oral lore** — folklore now, whether
or not the underlying content has drifted from where it started.

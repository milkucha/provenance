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

Each entry below covers one dialog file in `data/luminacion/blabber/dialogues/` (templates
excluded). "Claims on record" are phrased as reported assertions, not restated as fact, on purpose.

---

## `sonoros_lost_traveler.json`

- **Participants:** Sonoros; an unnamed traveler (the player)
- **Location:** Balhâm ("Balehm," in the traveler's own phrasing)
- **Summary:** A traveler arriving in Balhâm, lost, meets Sonoros waiting by the town's rail depot.
  Sonoros orients them (what the town is, where the trains go), briefly comes under suspicion of
  being a robber, and explains what he's doing there before the two part ways.
- **Claims on record:**
  - Sonoros identifies the town as Balhâm, calls it a "ciudad sagrada" (sacred city), and says it's
    still mostly unfinished ("half of it's still scaffolding").
  - He says it's "been going up since 354" — and explicitly admits he doesn't know what that number
    is counted from.
  - He names a monument, "El Dragón de Balham," as worth seeing.
  - He describes two rail lines out of Balhâm: west to Sälthos Cruzados (which he estimates at "near
    four thousand blocks," and about which he has heard — but does not confirm — that it's the
    biggest town on the continent), and east to Khan Ice.
  - He identifies himself as Sonoros, says he's "out of Görff way," and says his work is walking
    rail crossings and marking damage, naming "Cruce de Trobal, out past Khol Moshin way" as one he
    does regularly.
  - He denies being a robber when directly asked.

## `nawom_morkulo_first_meeting.json`

- **Participants:** Nawom; Morkulo
- **Location:** Nvhi (by the fountain outside the main hall)
- **Summary:** Nawom, arriving at Nvhi in search of the road to Puerto Tortuga, meets Morkulo at the
  fountain. Neither turns out to know the way. They introduce themselves, trade what little they do
  know about each other's home regions, and agree to go inside and look for a map.
- **Claims on record:**
  - Neither Nawom nor Morkulo claims to know the route to Puerto Tortuga.
  - Nawom identifies his home as Terfila, and says explaining how he came to be there ("that's a
    longer story than it sounds") is more than he wants to get into on the spot.
  - Morkulo says he doesn't know Terfila firsthand, but knows it "by reputation" — specifically, a
    banker named Aureobalo who travels the road to Khol Moshin, and "a pilot or two" flying in from
    Sid Nalta.
  - Morkulo identifies himself as originally from Tyrnea, says he studied there "long enough ago I
    barely know the person who did," and says he is at Nvhi "on curiosity alone."
  - Morkulo claims Nvhi is "the place they say Därnis heard whatever it was that sent him off to
    find that new continent" — note the hedge ("they say") built into his own claim.
  - Morkulo complains that recorded coordinates for Khol Moshin and Khan Ice "argue with themselves"
    — a personal, informal echo of the same coordinate disagreements `context.md`/`encodings.json`
    document formally as `CONFLICT-02`, though Morkulo doesn't cite it as such — he's speaking from
    professional frustration, not from having read the analysis.

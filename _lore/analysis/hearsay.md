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
sample from (`scripts/sample_lore_knowledge.py`), at the same odds as any objective-record fact — so
a claim can now be repeated by a character who never touched the objective record at all, only heard
it from someone who'd heard it. Every time that happens, a coin flip (`scripts/lineage_coin.py`,
flat 50/50) decides whether the retelling stays traceable or loses its origin: on a traceable roll,
the claim here is noted inline ("derived from `<claim id>`") and the dialog line may name the
source; on an untraceable roll, no origin is recorded at all, the dialog line uses vague framing
("they say...," "it's told that..."), and the claim is marked **oral lore** — folklore now, whether
or not the underlying content has drifted from where it started.

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

## `gondarfolas_darnis_and_bracco.json`

- **Participants:** Gondarfolas; an unnamed traveler (the player)
- **Location:** Görff ("Gorff," in the dialog's own phrasing)
- **Summary:** A traveler looking for passage meets Gondarfolas, a sailor at his boat in Görff, and
  trades a secondhand story — a man who sailed south and never returned, with a search expedition
  now being organized — for the ride. Gondarfolas recognizes the story as Därnis's, walks through
  what he's read of it, and traces where his own history books came from.
- **Claims on record:**
  - Gondarfolas is based in Görff, sails a small ship ferrying travelers along the coast, and is an
    avid reader of history.
  - Därnis sailed south out of Sindäara and discovered a new ocean, a burning island, and floating
    land, taken by historians as a sign of a new continent — and, per Gondarfolas's reading, "came
    back long enough to tell of it," though what happened to him afterward goes unrecorded.
  - The traveler reports hearing in Khol Moshin that Därnis's siblings are organizing an expedition
    to search for him, departing from where a highway ends at the continent's southern tip —
    Gondarfolas explicitly does not confirm this part; it's new to him.
  - Khol Moshin has no coastline, by Gondarfolas's account — as a sailor, he's never had reason to
    go there himself.
  - Gondarfolas owns two chronicles, the Ensayo and the Libro, and describes them accurately as two
    histories of the same span of years that never reconcile with each other — a personal, informal
    echo of the same divergence `context.md`/`encodings.json` document formally as `CONFLICT-01`.
  - Gondarfolas bought his copies years ago from a trader in Görff he recalls as "Bracco, or
    Braggo," who sold them off cheaply and without explanation — and has no idea where the man came
    from or went afterward.

## `nuvilo_nerkeli_feria_del_milenio.json`

- **Participants:** Nuvilo; Nerkeli
- **Location:** the Feria del Milenio, by the airplane hangar (a millennium-fair venue, not itself
  in the objective record)
- **Summary:** Overheard mid-conversation by the player (no player lines — pure eavesdropping),
  childhood friends Nuvilo and Nerkeli catch up by the hangar Nerkeli is minding for the fair's
  airplane showcase. They cover códigos and the Dääx symbol, Nerkeli's running joke that ducks
  descend from the Daax, and the highways M9/M7, both of which happen to end at Nvhi — the place
  Nuvilo's family claims to have founded.
- **Claims on record:**
  - Nuvilo ties códigos to Era del Daax, begun under Görff's new government, and says the Dääx
    symbol was carved into old ruins "right around those same years" — matches the objective record
    (symbol carved c. 372+ d.V., within Era del Daax's 360–504 d.V. span).
  - Nerkeli jokingly theorizes that ducks are the last living descendants of the Daax — offered
    explicitly as his own unfounded pet theory, not as history.
  - Nuvilo claims descent from "Navalius," said to have founded Nvhi generations back — a family
    claim with no corroborating source, and Nuvilo himself admits he knows little else about Nvhi's
    own history.
  - Nuvilo cites highway M9 (Nvhi → Khan Ice); Nerkeli cites M7 (Puente Intercontinental → Nvhi),
    which he flies regularly without having connected it to Nuvilo's family before this
    conversation.

## `nuvilo_scholar_at_the_feria.json`

- **Participants:** Nuvilo; an unnamed traveler (the player)
- **Location:** the Feria del Milenio (a millennium-fair venue, not itself in the objective record)
- **Summary:** A traveler arriving at the fair meets Nuvilo, who orients them on what the Feria is
  celebrating, explains he has no official role there (just a visiting scholar), and describes what
  he writes about — historical inventors and travelers, and an unresolved puzzle about two
  chronicles of the same centuries that never agree.
- **Claims on record:**
  - The Feria del Milenio celebrates "a thousand years of Milkantis," with exhibits honoring the
    world's cultures and building styles, its landscapes, its artifacts (códigos and redstone work
    among them), and its historical eras.
  - Nuvilo holds no official role at the fair — unlike some others there (e.g. Nerkeli, running the
    airplane showcase), he's simply a visiting scholar, "following the path of knowledge."
  - Nuvilo says he writes about historical inventors and travelers, naming Daaxagoras and
    Pitaglorias (credited with the first atlas) and Därnis (who sailed south and found unmapped
    land).
  - Nuvilo describes an unsolved puzzle he keeps returning to: two histories of the same centuries,
    written by different hands, that never reconcile — an informal, personal echo of the same
    divergence `context.md`/`encodings.json` document formally as `CONFLICT-01`.

## `nerkeli_hangar_talk.json`

- **Participants:** Nerkeli; an unnamed traveler (the player)
- **Location:** the Feria del Milenio, by the airplane hangar
- **Summary:** A traveler stops by Nerkeli's hangar at the fair. A genuine branch: they can ask
  about the plane and Nerkeli's flying (the M7 route, his freight work), or steer the talk toward
  the Feria itself, where Nerkeli turns out skeptical of the "thousand years" framing — and, pressed
  on why, ends up explaining his duck/Daax theory.
- **Claims on record (showcase branch):**
  - Nerkeli flies the M7 corridor (Puente Intercontinental → Nvhi) as his regular assigned run, not
    for any business of his own — freight and the occasional passenger.
  - Despite flying that route for years, Nerkeli says he couldn't tell much about Nvhi itself — he
    turns around at the airstrip each time without properly seeing the place.
  - His freight is mixed: tools, building supplies, mail, and occasionally fragile merchant goods
    too delicate for boat or horse transport.
- **Claims on record (Feria branch):**
  - Nerkeli doubts the fair's "thousand years of Milkantis" framing — he says he's heard the world's
    starting point told three incompatible ways across his travels, none of which line up — a
    personal, informal echo of the same unreconciled origin-point problem `context.md`/`encodings.json`
    document formally as `CONFLICT-12`, though Nerkeli doesn't cite it as such.
  - Nerkeli restates his running joke theory (also given in `nuvilo_nerkeli_feria_del_milenio.json`)
    that ducks are the last living descendants of the Daax — offered explicitly as his own unfounded
    pet theory, not as history.

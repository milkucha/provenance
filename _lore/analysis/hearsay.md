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

Every dialog gets an entry here, full stop - not only the ones where a character explicitly retells
something they heard from someone else. A character's own fresh invention (a venue's description, a
personal theory, an on-the-spot guess) belongs in the record exactly as much as an attributed
retelling does. Oral tradition isn't only fantasy layered on top of a fixed truth - plenty of what
gets said aloud, invented in the moment or not, turns out to be true, or half true, or true with the
names filed off. The record doesn't presume otherwise: an unverified claim sits at `null` until
something confirms or contradicts it, not at "assumed false." This is also the actual mechanism by
which an idea becomes folklore - not a special flag, just repetition. A kernel that gets said once
stays a single claim with a small chance of resurfacing; a kernel repeated across several dialogs (by
the same character or several) accumulates more copies of itself in the sampling pool, which raises
the odds it gets drawn again by some future character, and each retelling is another chance for it to
mutate a little further from wherever it started.

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

## `doran_plaza_orientation.json`

- **Participants:** Döran; an unnamed traveler (the player)
- **Location:** la Plaza de las Culturas, Feria del Milenio (a pavilion, not itself in the objective
  record)
- **Summary:** A visitor at the Plaza de las Culturas asks Döran what the pavilion is about. He
  orients them on the four castle replicas on display and the pavilion's AI-powered architectural
  holograms, then branches on the unfamiliar cities, the holograms' cost, or what "minor wonder"
  means.
- **Claims on record:**
  - The Plaza de las Culturas is one of the Feria del Milenio's pavilions, honoring the diversity of
    architectural styles and urbanity across Milkantis, from small villages to great cities.
  - The Plaza displays castle replicas of Görff, Ciudad Dragón, and Salthos Cruzados, and the palace
    of Khan Icé — the fortresses of the largest cities.
  - The Plaza's pedestals sometimes display miniature AI-powered holograms of five other
    architectural marvels of Milkantis, built on a separate datapack — costly in energy, and if left
    running too long, the fabric of time itself grows tense and starts to crackle.
  - Döran calls Görff the oldest of the four represented castles, "curtida en más de una guerra"
    (weathered by more than one war).
  - Döran says he knows Khan Icé's palace only through what train travelers tell him passing through,
    not firsthand.

## `doran_four_castles.json`

- **Participants:** Döran; an unnamed traveler (the player)
- **Location:** la Plaza de las Culturas, Feria del Milenio
- **Summary:** Döran invites a visitor to ask about any of the four castles in the Plaza, branching
  per city: Salthos Cruzados (his own hometown, and its tie to the legendary prince Döran and the
  discovery of Plathinëa), Ciudad Dragón (its growth and his wariness over the destroyed map of
  Salthos Cruzados), Görff (its wars and its many travelers), and Khan Icé (where he speaks with more
  confidence than his firsthand knowledge supports).
- **Claims on record:**
  - Prince Döran built the castle at Salthos Cruzados after the discovery of Plathinëa, and world
    cartography began there — matches the objective record closely.
  - This Döran shares his name with the legendary prince, and wonders whether that shaped his own
    path into maps and miniatures, or the other way around — a personal descent/namesake claim, not
    corroborated by (nor contradicted by) the objective record.
  - Plathinëa is described as "the other half of the world" — the region discovered after Milkäan.
  - Ciudad Dragón grew from Península Dragón, absorbed a neighboring village, and became the largest
    city in all of Milkantis.
  - Ciudad Dragón's mages are blamed for destroying the great map of Salthos Cruzados — matches the
    `codigos` concept entry.
  - Görff's castle carries so many scars that an entire era was named for its wars, "Las Guerras de
    Görff."
  - Döran says more familiar faces pass through the fair from Görff than from anywhere else — a
    personal impression, not verifiable.
  - Khan Icé is connected by rail to both Görff and Balhâm.
  - Döran speculates, from the palace's defensive architecture, that Khan Icé served as a wartime
    refuge and possibly a capital "when the world closed in on itself" — delivered as unconfirmed
    speculation, not sourced from his own knowledge sample, but it happens to match the objective
    record (Khan Icé: "refuge built end of era 1; world capital in Era del Confinamiento"). A
    confident bluff that landed on the truth, not a knowing lie.

## `doran_eras_of_culture.json`

- **Participants:** Döran; an unnamed traveler (the player)
- **Location:** la Plaza de las Culturas, Feria del Milenio
- **Summary:** Döran muses that cultural differences are temporal as well as spatial, then branches
  on the oldest culture he knows well (Görff, leading into the Era del Daax), a rundown of the ages
  he can name, what era they're currently living in (the Era de la Magia), and a light tease about
  how poetic he sounds.
- **Claims on record:**
  - Döran considers Görff, tied to "Las Guerras de Görff," the oldest culture among the four he can
    speak to with confidence — and admits a gap in what he knows between that era and the Era del
    Daax.
  - Döran describes the Era del Daax as the first age of the códigos and the era when architecture
    itself expanded most, noting the two chronicles disagree on when it began (360 d.V. vs. 294 d.V.)
    though both close it at 504 d.V. — matches the objective record's own boundary mismatch exactly.
  - Döran names the Era de las Maravillas, starting around 804 d.V. with no end he knows of, among
    the ages he can speak to.
  - Döran says the present era is the Era de la Magia — when the tools that shape the world began
    transforming themselves, when people learned to "mod the game" and bend the rules of the universe
    within this plane. The era's existence and dates are in the objective record; this specific
    framing is a session-given elaboration, plausible as written but not independently verifiable.

## `khaoe_farlis_el_castillo_que_fue.json`

- **Participants:** Khaoe; Farlis
- **Location:** la Plaza de las Culturas, frente a la réplica del Castillo de Görff, Feria del Milenio
- **Summary:** Standing in front of the miniature replica of the Castillo de Görff, Khaoe and Farlis —
  both members of the Collective that now lives there — reflect on what the castle used to be versus
  what it is now.
- **Claims on record:**
  - Before the Collective, and before the citadel was left abandoned, a tyrant ruled from the castle
    at Görff — his name no longer remembered.
  - Farlis calls it poetic justice that he and Khaoe now live in the same castle that once belonged to
    that tyrant.
  - Khaoe pushes back on the "poetic justice" framing — to her it's not symbolism, just that someone
    had to take up the stones.

## `khaoe_farlis_lo_que_cambia_el_tiempo.json`

- **Participants:** Khaoe; Farlis
- **Location:** la Plaza de las Culturas, frente a la réplica del Castillo de Görff, Feria del Milenio
- **Summary:** Still by the castle replica, Farlis wonders what the Feria del Milenio's "mil años" is
  actually counted from; Khaoe, just back from Lundria, says every temple there kept its own calendar;
  both conclude meaning shifts given enough time, or enough deliberate effort.
- **Claims on record:**
  - Farlis says he was never told exactly what event the Feria's "thousand years" framing counts from
    — echoes the same unreconciled origin-point problem documented as `CONFLICT-12` (also independently
    echoed by Nerkeli in `nerkeli_hangar_talk.json`), though Farlis doesn't cite it as such.
  - Khaoe says every temple in Lundria kept its own calendar, as if the world began again at each door
    — the objective `lundria` entry records temple-building and the "culto del cubo flotante de
    Lundria" (era 7) but says nothing about calendars specifically; plausible given the temple culture
    on record, not confirmed. Khaoe's own sampled knowledge of Lundria was bounded to the location's
    name/region/type, not this detail, so this is a personal impression from her actual visit, not
    drawn from her sample.
  - Both agree a thing can end up meaning something else entirely, if enough time passes, or if
    someone puts in the work to change it.

## `khaoe_farlis_esperando_a_khaasan.json`

- **Participants:** Khaoe; Farlis
- **Location:** la Plaza de las Culturas, frente a la réplica del Castillo de Görff, Feria del Milenio
- **Summary:** Still waiting by the castle replica, Khaoe and Farlis look out for their comrade
  Khaasan, who said he was coming straight to the fair but hasn't been sighted yet.
- **Claims on record:**
  - Khaasan told Khaoe and Farlis he was coming straight to the Feria del Milenio — a social claim
    about a third party, nothing in the objective record to check it against.
  - Khaoe and Farlis expect Khaasan to arrive by griffon, and are watching the sky for it. Resolved
    2026-07-30 (Khaasan's own `/enact` pass, per the user): he always travels by griffon, full stop —
    "Teletraveller" describes the distance he covers, not a contradiction with the mount. Previously
    logged here as a genuine, unresolved divergence; no longer open.

## `khaoe_calendario_mecanografico.json`

- **Participants:** Khaoe; an unnamed traveler (the player)
- **Location:** the Feria del Milenio, in front of the Calendario Mecanográfico
- **Summary:** A traveler asks Khaoe about the large new machine she's standing in front of. She
  explains what it is and what it's for, then, pressed to clarify her own aside about Lundria, admits
  she came back from her temple trip more confused about timekeeping than she left — and can't
  actually teach what she only half-remembers.
- **Claims on record:**
  - The Calendario Mecanográfico is a new machine, inaugurated for the Feria del Milenio, that marks
    the current year on a moving timeline.
  - Khaoe says every temple in Lundria disagreed on what year it was, each counting from something
    different, with nobody troubled by the mismatch — restates, in more detail, the same impression
    already on record from `khaoe_farlis_lo_que_cambia_el_tiempo.json`.
  - Khaoe says she went to Lundria hoping to learn "the" calendar there and came back without knowing
    which of the many was the real one.
  - Khaoe recalls, vaguely and without confidence, one temple that counted by moons and another that
    counted from the last time the whole town gathered — offered explicitly as a half-remembered,
    unreliable impression, not asserted as fact; she declines to "teach" it and redirects to "someone
    from Lundria" instead.
  - Consistency note: none of these specific temple-counting details (moons; counting from a town
    gathering) appear in the objective `lundria` location entry, which records only temple-building
    and the "culto del cubo flotante de Lundria" (era 7) — plausible given that record, not confirmed
    or contradicted by it; Khaoe's own sampled knowledge of Lundria was bounded to the location's
    name/region/type, so this is personal impression from her actual visit, not drawn from her sample,
    consistent with how the same caveat was already logged for
    `khaoe_farlis_lo_que_cambia_el_tiempo.json`.

## `khaoe_banco_colectivo.json`

- **Participants:** Khaoe; an unnamed traveler (the player)
- **Location:** the Feria del Milenio, a bench
- **Summary:** Sitting on a bench watching people go by, Khaoe is approached by a traveler who's heard
  she's from the Collective. She confirms it, explains the horizontal organization when pressed,
  clarifies that Farlis isn't actually a prince, and names a few fellow Görff residents plus her
  closer comrades Farlis and Khaasan when asked who else is part of it.
- **Claims on record:**
  - Khaoe confirms she's a member of the Collective, and jokes that either it shows or someone's been
    talking about her.
  - Khaoe says the Collective has spent years rebuilding Görff "their own way," and that people talk
    about it, for better or worse — a personal impression, not independently verifiable.
  - Khaoe clarifies that Farlis isn't literally a prince — his family has had money in Terfila for
    generations, but she admits she's never been clear on the exact title, and he doesn't press the
    point either. Consistent with Farlis's own registered backstory (aristocratic Terfila family, old
    money).
  - Khaoe describes the Collective as horizontal in a specific sense: nobody leads just for arriving
    first, or for their surname.
  - Khaoe says, when asked how many are in the Collective, that she doesn't know an exact number —
    more or less everyone living in Görff counts, given how the horizontal structure works. Consistent
    with her own registered backstory, which frames the Collective as made up of "the diversity of
    peoples that inhabit the Gorff farms and citadel."
  - Khaoe names Bardaglis (a musician), Kristok Jakur (works the forge), and Dägna (runs the tavern)
    as fellow Görff residents, then Farlis and Khaasan as the comrades she sees most often. All five
    names match items in Khaoe's own sampled knowledge (`inhabitant: Bardaglis (Gorff)`,
    `inhabitant: Kristok Jakur (Gorff)`, `inhabitant: Dägna (Gorff)`) and their registered roles.

## `ilaria_espiral_de_la_historia.json`

- **Participants:** Iläria; an unnamed traveler (the player)
- **Location:** the Espiral de la Historia, entrance to the Feria del Milenio (the Feria itself is now
  in the objective record — see `feria_del_milenio` — but the Espiral's own internal structure is not)
- **Summary:** A visitor arrives at the entrance to the Espiral de la Historia, the Feria del Milenio's
  first pavilion. Iläria welcomes them and branches on where they are, what the Espiral is, and who she
  is, before converging on an invitation to start the tour.
- **Claims on record:**
  - Iläria says the Espiral de la Historia is, in her own opinion, the most important of the Feria's
    five pavilions — a personal, self-interested claim from its own curator, not independently
    checkable.
  - The Espiral de la Historia is a labyrinth of nine chambers, one per era of the world, holding
    artifacts, documents, art, and figures representing each; Iläria stations herself at the center,
    which represents the current era, la Era de la Magia. This structural detail is Iläria's own
    established backstory (see `_maps/npcs/registry.json`), not stated in `ensayo_i_final`'s brief
    passage on the Feria, which gives only the pavilion count and inauguration date.
  - Iläria identifies herself as the author of the Ensayo documenting the world's history, and as the
    one in charge of this pavilion — consistent with the objective record's `ilaria` character entry
    (credited author of ENSAYO I); her charge over this specific pavilion is backstory-level detail,
    not contradicted by anything in the objective record.

## `farlis_aureobalo_bar_salthos_cruzados.json`

- **Participants:** Farlis; Aureobalo
- **Location:** a bar in Salthos Cruzados, the first evening after the Feria del Milenio's inauguration
- **Summary:** Farlis and Aureobalo, already acquainted from their overlapping travel routes, run into
  each other for the first time at this particular bar on the Feria's opening night. Aureobalo brings
  up a vague story he's heard about Farlis and a castle; Farlis confirms it and fills in his own side.
- **Claims on record:**
  - Aureobalo has heard, vaguely, that someone corrected Farlis over something he'd said about a
    castle and "the stones someone had to hold up" — voiced with deliberately vague framing (an
    untraceable `lineage_coin.py` roll), though it traces back to Khaoe's rebuttal in
    `khaoe_farlis_el_castillo_que_fue.json`.
  - Farlis confirms it was about him: he'd called it poetic justice, living in the tyrant's own former
    castle; he was told flatly that it isn't poetry, someone just has to do it — consistent with his
    own registered stance and Khaoe's on-record rebuttal.

## `aureobalo_khaasan_bar_salthos_cruzados.json`

- **Participants:** Aureobalo; Khaasan
- **Location:** a bar in Salthos Cruzados, the first evening after the Feria del Milenio's inauguration
  (same bar, same evening as `farlis_aureobalo_bar_salthos_cruzados.json`)
- **Summary:** Aureobalo and Khaasan cross paths. Khaasan says he's only passing through, on his way
  from Khan Ice; Aureobalo buys him a drink for it.
- **Claims on record:**
  - Khaasan says he was just passing through Salthos Cruzados, coming from Khan Ice — not there for
    the Feria itself. Consistent with his own registered knowledge sample, skewed toward Khan Ice.
  - Aureobalo toasts him for the long road; Khaasan accepts but says he prefers short drinks —
    personal texture, invented in-scene.

## `farlis_khaoe_bar_salthos_cruzados.json`

- **Participants:** Farlis; Khaoe
- **Location:** a bar in Salthos Cruzados, the first evening after the Feria del Milenio's inauguration
  (same bar, same evening)
- **Summary:** Khaoe notes she saw Farlis talking with Aureobalo earlier; the conversation turns to her
  own recent trip to Lundria.
- **Claims on record:**
  - Khaoe noticed Farlis had been talking with Aureobalo earlier that same evening — same-evening
    continuity with `farlis_aureobalo_bar_salthos_cruzados.json`, not a lore claim.
  - Khaoe says Lundria was different from how she remembered it, and that she came back with more
    questions than she left with — restates, in general terms, the same impression already on her own
    registered experience (see `khaoe_calendario_mecanografico.json`).

## `khaoe_khaasan_bar_salthos_cruzados.json`

- **Participants:** Khaoe; Khaasan
- **Location:** a bar in Salthos Cruzados, the first evening after the Feria del Milenio's inauguration
  (same bar, same evening)
- **Summary:** Khaasan finally reaches Khaoe, griffon and all; light banter about whether she ever
  doubted he'd make it.
- **Claims on record:**
  - Khaasan arrives by griffon, as always, and leaves it outside eating something it shouldn't —
    firsthand, not hearsay, since both participants were actually there. Matches the griffon-travel
    resolution recorded this same run in the `khaoe_farlis_esperando_a_khaasan` entry above.
  - Khaoe teases that she never doubted he'd arrive on time; Khaasan calls it a lie, and she admits it,
    a little — banter/personal texture, invented in-scene.

## `farlis_bardaglis_bar_salthos_cruzados.json`

- **Participants:** Farlis; Bardaglis
- **Location:** a bar in Salthos Cruzados, the first evening after the Feria del Milenio's inauguration
  (same bar, same evening)
- **Summary:** Farlis and Bardaglis meet; Bardaglis reveals he's already turned the castle story into a
  song that's catching on, and Farlis learns his own line to Khaoe outlived the moment it was said in.
- **Claims on record:**
  - Bardaglis has turned the castle story into a song — specifically Khaoe's line about the stones
    someone had to hold up — and it's on its way to becoming popular. Traceable `lineage_coin.py` roll;
    matches Bardaglis's own registered backstory (a song "on the verge of becoming popular") and his
    sampled knowledge, which includes all three `khaoe_farlis_el_castillo_que_fue` claims. Notable
    irony, not asserted in-dialog: the line that stuck was Khaoe's rebuttal, not Farlis's original
    poetic-justice framing.
  - Farlis confirms he was the one who said the poetic-justice line the song answers, and that he said
    it to Khaoe, in front of the castle — matches Farlis's own established stance.

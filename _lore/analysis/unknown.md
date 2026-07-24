# Unknown — Open Questions and Gaps

This file collects everything the material set does not answer: places named once and never again,
questions the source documents pose to themselves and leave blank, sections that are headers with no
content, and identity questions that no source resolves. Cross-references to `encodings.json`'s
`conflicts` array (disagreements *between* sources) are given as `CONFLICT-##`; everything else here is
a gap or an unposed/unanswered question rather than a contradiction.

## Resolved by the user (2026-07-24)
These were raised as open questions in an earlier pass and have since been settled directly by the
user. The underlying documentary facts (the disagreements themselves) are kept in `context.md` and
`encodings.json` for the record; only the *design decision* lives here and in each conflict's
`user_resolution` field.
- **Timeline:** both `ensayo_i`'s a.V./d.V. system and `libro`'s Venidas system coexist in-world as
  separate, non-overriding reckonings. Neither is canonical over the other. (`CONFLICT-01`)
- **World naming:** Milkantis, Milkantida, and "Mundo de Milka" are the same world-name, with spelling
  drift over time. **Not yet extended to Milkäan** — see follow-up flag below. (`CONFLICT-03`)
- **Author identity:** the credited in-world authors (Pitaglorias/Fitaglorias, Daaxagoras, Storfilias,
  Iläria) are a *mix* of real players' in-world personas and purely legendary/fictional figures. Which
  specific name is which was not yet specified — still needed before this can be applied per-character.
  (`CONFLICT-04`, `CONFLICT-05`)

### Follow-up flag: does "Milkäan" belong in the same-name-as-the-world group?
The world-naming resolution above was given for Milkantis/Milkantida/"Mundo de Milka." I did not fold
"Milkäan" into it, because every source that uses "Milkäan" also uses it as one of exactly two named
regions (paired against Platinhëa/Plathinëa) — e.g. every row in the Catastro is tagged
`Zona=Milkäan` or `Zona=Platinhëa`, and `ensayo_i` places "Puerto Pastizal, en la región de Milkäan"
opposite the later-discovered "región de Plathinëa." Treating Milkäan as just another spelling of the
whole world's name would contradict that consistent regional split. **Worth a direct check when
convenient: is Milkäan (a) a region distinct from the world-name entirely, (b) the region that later
lent its name to the whole world (or vice versa), or (c) actually meant to collapse into the same
name after all?**

## Still open: Catastro's "Continente: Antiguo" — but there's a new lead
Asked the user directly; the answer was "not sure yet." This stays a genuine open question rather than
a design decision — see the original description below. However, a third material drop (2026-07-24)
added `El Antiguo Continente de Milkan - Mapa del Milenio.png`, whose title is the first source anywhere
to use "Antiguo" as part of a named continent — "El Antiguo Continente de Milkan," whose rendered
landmass shape matches the continent traced by the yellow outline in `Milka Oceans Plan and Continent
Outline (18.11.2020).png`. This makes it more plausible that Catastro's "Antiguo" tags every row as
belonging to *this specific, currently-mapped* continent — implicitly contrasted with an unmapped "new"
continent (plausibly the one Därnis reaches south of Sindäara in `ensayo_i` era 9). Still an inference
from a title, not a confirmed fact, since the map itself carries no other text.

## Correction (2026-07-24): the "Milka Oceans Plan" caption was misattributed
An earlier pass in this material assigned the caption "Milka Oceans Plan and Continents Outline
(18.10.2020 AD)" (found in `Libro de los Tiempos...`, next to an `[IMAGE]` marker) to `image6.png` (the
aerial parchment-style map), based on reading-order proximity in the extracted text. The third material
drop added a standalone file, `Milka Oceans Plan and Continent Outline (18.11.2020).png` — one month
later, near-identical title — whose *content* is a high-resolution version of `image7.png` (the labeled
grid map), not `image6.png`. The caption almost certainly belongs to the grid map. `image6.png` (the
parchment aerial map) is uncaptioned and unidentified again — this was a case of correcting course, not
a new gap.

## New unlabeled elements on the high-resolution grid map
The high-resolution `Milka Oceans Plan and Continent Outline (18.11.2020).png` reveals overlay detail
invisible in the compressed copy embedded in `Libro`: a thick yellow outline around the whole landmass
(plausibly "the Continent Outline" of the title, and the same shape rendered in the Mapa del Milenio);
two separate, smaller orange-outlined regions (north around grid -3,-4, and center around grid -1,1 to
0,1); roughly ten white triangle markers; and two small red dot markers (near grid 9,1 and grid 4,6).
**None of these are labeled anywhere.** The same white-triangle/orange-outline/yellow-outline visual
vocabulary reappears in `Ruta Lundria-Salthos Cruzados.png`, suggesting these are working web-map
(Dynmap/BlueMap-style) screenshots used as source material for plotting — but what the orange regions
specifically denote, and what the white/red markers mark, is not stated anywhere.

## What does "WP" mean?
Two newly-added screenshots are titled `Khan Ice (WP 17.11.2020).png` and `Sid Nalta (WP 17.11.2020).png`
— "WP" is not expanded anywhere in the material. Possibly "waypoint," possibly a map-export/plugin label.
Not resolved.

## A route named but not plotted: "Ruta Lundria-Salthos Cruzados"
`Ruta Lundria-Salthos Cruzados.png` names a route (Lundria to Sälthos Cruzados) that doesn't match any
of the highway codes (M7/M9/A33/P-33) or train segments already catalogued from `Cartography...xlsx`.
The image shows a purple traced line, but no coordinate table accompanies it, so the route's actual
waypoints aren't recorded anywhere in the material.

## Questions the source documents ask themselves, left unanswered
Transcribed verbatim from `libro`, which poses these as its own open outline points:
- "Milkhantida (is there another name?)" — under Continentes.
- "Sit:Nalta, Saari, otras" — under Islas. **"Saari" and "otras" (other islands) are never named or
  described anywhere else in the material.**
- "Quiénes son les autores?" — under Sobre los Lugares, with no answer given (and unclear whether it asks
  who authored the routes, the atlas books, or the book itself).
- "Cómo se calcula el SBW (Since the Beginning of the World) - minecraft ticks" — listed as a topic to
  explain, never explained.
- "Otras mediciones (ET?)" — a bare stub, "ET" undefined.
- "En qué año del tiempo real (AD) se comenzó el mundo." — posed as a question to be answered later; the
  material never gives a single agreed real-world start date (ensayo_i's players/eras imply Oct 2011;
  catastro's earliest "Inicio" value is 2011 for Isla De La Amistad).

## Entire sections that are only headers, with no content anywhere in the material
From `libro`'s outline: Descubrimiento, Mapas generales, Montañas, Lagos y ríos, Océanos, Registros,
Rutas (only two route *names* — Camino de Forlán, Sistema Intercontinental de trenes — are listed, with
no description of either), Otros sitios. These are confirmed gaps, not omissions on our part — the
source document itself never filled them in.

## Resolved by a later material drop (2026-07-24, second batch)
- **`libro`'s 5 unidentified screenshots are now identified.** A second batch of material added
  `Gorff 1/2 (17.07.2020).png` and `Khan Ice 1/2/3 (26.08.2020).png` — the same screenshots, now with
  place names and dates in the filename. `image1.png`→Khan Ice, `image2.png`→Khan Ice, `image3.png`→Gorff,
  `image4.png`→Khan Ice, `image5.png`→Gorff. Only `image6.png` (the parchment-style "Milka Oceans Plan"
  map) remains without a confirming duplicate. Full mapping in `context.md` §5's addendum.
- **A visual source for Térfila now exists** (`Terfila Old 1/2/3.png`), previously undocumented visually.
  The "Old" qualifier in the filename is itself new and unexplained — see below.

## New open questions from the second material drop (2026-07-24)
- **Aerörea vs. Milkäan** (`CONFLICT-13`) — `ESQUEMA.pdf` names Milkäntis's two main continents as
  Aerörea and Platinhëa, where every other source uses Milkäan in Aerörea's place. This directly bears
  on the still-open Milkäan follow-up flag above; worth resolving together.
- **A third era-timeline** (`CONFLICT-14`) — `ESQUEMA.pdf`'s poster gives era names and boundaries that
  match neither `ensayo_i` nor `libro`'s Venidas cleanly (same names/different ranges in some cases,
  same ranges/different names in others). The user's 2026-07-24 "both timelines coexist" resolution was
  given before this poster surfaced and only mentioned two systems — does it extend to a third?
- **"The Seasons" / "Eras After the Seasons"** (`CONFLICT-12`) — `timelines.py` introduces a threshold
  (Ox = 2025-12-31) after which in-world days run 3x slower, tied to neither the Vórtex nor the Venidas
  system, plus yet another candidate "start of the world" date (2012-07-01) that matches nothing else.
- **`Terfila Old` — old relative to what?** The three screenshots are labeled "Old" but undated, unlike
  every other dated screenshot pair. Is there a "new" Térfila elsewhere in someone's screenshot
  collection, or does "Old" just mean "this screenshot itself is old"?
- **`Osmory` (-2505, 53, 168)** — named once, in `Book of Inventions`, as the site of three deactivated
  "explosive artefact" command-block machines. No other source mentions it at all.
- **The trailing number `1426575558`** at the very end of `Book of Inventions`, with no label — could be
  a world seed, a tick count, or something else entirely.
- **`Cruce de Trobal` and `Monte Pastizal`** — named train-route waypoints from the Cartography
  spreadsheet, appearing nowhere else. "Monte Pastizal" ("Mount Pastizal") suggests a relationship to
  Puerto Pastizal, but nothing states one.
- **`Eurasori`** — `ESQUEMA.pdf`'s 2020 foundations list includes "Eurasori" alongside settlements like
  Lundria and Kurista. `ensayo_i` only mentions a "Cordillera de Eurasori" (a mountain range) receiving
  "the first expedition" in 534 d.V. — a range being explored is not the same as a place being founded;
  unclear if these are the same Eurasori or if the poster is using the name loosely.
- **`Tercera Aldea Survival`** — a plausible but unconfirmed name for `ensayo_i`'s previously-unnamed 3rd
  subsistence settlement (see "The missing 4th subsistence settlement" below, which is really about a
  gap one number higher).
- **`Holistick` vs `Jölystick`** — same 2023 date in both `esquema` and `ensayo_i`; treated as a likely
  spelling variant of the same place, not confirmed.

## Correction (2026-07-24): `Luminacion Register` and `Terraforming Purge Register` ARE lore — split, not excluded
An earlier pass in this file wrongly treated these two spreadsheets as misplaced production files. The
user corrected this directly: they belong here, but as a **blend of two different kinds of material**,
the same split that already applies to `timelines.py` and `Book of Inventions`' command-block recipes —
- **Technical/mysterious elements** — "relative to the very conditions of existence of that which they
  talk about, kind of like a mysterious formula that defines the bounds of reality and the way it
  behaves, which is only understandable by some." In these two files: the `Code` sheet's `Clock
  worldTime`-triggered mocap formulas, the `Taterzen` sheet's distance-based movement-mode switching,
  and the `Terraforming` register's region-file pass/fail grid. These may stay a mystery, or be
  deciphered later — they are not being discarded as noise, just flagged as not-yet-interpreted.
- **Narrative elements** — characters, locations, and actions that are directly usable lore. In
  particular, `Luminacion Register`'s `NPC` sheet is a genuine, if informal, **census of named
  inhabitants**: ~40 named characters with a home locality, a role (musician, barkeeper, blacksmith,
  pilot, market keeper, poet, painter, member of "the Collective," etc.), and in several cases a
  described route or errand (e.g. Gondarfolas "Sailing to Terfila," Aureobalo a "Banker en route" between
  Terfila and Khol Moshin). See the new `characters.named_inhabitants` list in `encodings.json` for the
  full roster with localities.
- Per the user: **"Not everything is useful for this quest of knowledge, but not everything is trash
  either"** — so nothing from either file has been discarded; the technical portions are held as an
  open, possibly-permanent mystery rather than excluded.

## Places named in only one source, with minimal or no further data
Fuerte Fabián, Puerto del Este, Aldea De Selenne, Isla Tortuga (`image7`/grid map only); Reznik, Gas Stop
(`catastro` only); Zotti, Villa Naranja, Friendly Village (`ensayo_i` only); Thrul Mahotta (`atlax_i`
only); Osmory (`book_of_inventions` only); Cruce de Trobal, Monte Pastizal (`cartography_trains` only).
Nothing beyond a name (and sometimes a coordinate or a single date) is known about any of these.

## The missing "4th subsistence settlement"
`ensayo_i` explicitly numbers subsistence settlements: 1st Puerto Pastizal, 2nd Okâsia, 3rd an unnamed
site enabled by the Vías de Hielo (era 6), and 5th Nueva Góndola (era 8, explicitly labeled "quinta").
**No source names a 4th.**

## "Continente: Antiguo" in the Catastro
Every one of the 38 populated rows in `Catastro Milkaan y Platinhëa.xlsx` has "Antiguo" in the
"Continente" column — no other value ever appears, and the column exists as if other values were
expected. **Open: does "Antiguo" mean this spreadsheet only catalogs one continent (with others,
perhaps the "new continent" Därnis reaches in `ensayo_i` era 9, simply not yet entered into this
cadastre), or does "Antiguo" mean something else entirely (a build-status category rather than a
place)?**

## Coordinate system conventions
No source ever labels its coordinate pairs/triples with axis names. `Atlax I` gives two numbers per
place; `Atlax II` gives three for its one entry (Sälthos Cruzados); `libro`'s mausoleos list gives three;
`libro`'s grid map (`image7`) gives an X, a Y, and a separate "Grid" cell reference whose relationship to
X/Y is inferred (grid cell number ≈ coordinate ÷ 1000), not stated. Whether "Y" in any of these tables
means Minecraft's Z-axis (north/south) or true altitude is never specified.

## Undefined concepts
- **örikal** — named once as a theoretical mineral tied to "an ancient power of manifestation"
  discovered ~900 d.V.; never defined further, and never explicitly tied to "Era de la Magia" (952+
  d.V.) despite the adjacency.
- **El hechizo que fuerza a vivir en subsistencia** (the spell discovered by aldea Camilo Ricarda,
  era 9) — described in one sentence, no mechanic, origin, or connection to the Muro Norte/Wasteland
  given.
- **Predicciones para el año 1000 d.V.** (Arkän, Prismätika, Mirage Citadel, Zafiria) — `ensayo_i` itself
  labels these as proposals/predictions, explicitly not established history. They should not be treated
  as canon places unless the user confirms otherwise.

## Identity questions
- Is **Iläria desde Lündria** (credited author of `ENSAYO I`) an in-world narrator persona, a real
  player's pen name, or a name for someone not otherwise listed anywhere? She does not appear in
  `libro`'s player roster. Per the user, the credited authors as a group are a *mix* of real-player
  personas and purely legendary figures — but which one Iläria is specifically is still unspecified.
  (`CONFLICT-05`, see "Resolved by the user" above)
- Are **Pitaglorias/Fitaglorias**, **Daaxagoras**, and **Storfilias** (the credited figures/authors of
  the two Atlax books) in-world legendary/mythic figures, real players' in-world personas, or something
  else? Same partial answer as above — confirmed to be a mix, individual assignments still open.
- The `libro` player roster (Milkucha, Termixdelosandes, Nicolas Alba, Nikkostratos, Gaboleos, Seleniau,
  Frvnco, Marcopolo, Sacrown12, Piroma91, Tommy, Koala, Hermanafranco) is a bare name list — no join
  dates, roles, or in-world characters are attached to any entry besides Milkucha and Nikkostratos (who
  are identified only as the book's two co-authors).

## All source-vs-source conflicts (see `encodings.json` for full detail)
`CONFLICT-01` era systems coexist (resolved) · `CONFLICT-02` coordinate mismatches (Khan Ice, Khol
Moshin, Sit:Nalta, Sälthos Cruzados, Dragon City) · `CONFLICT-03` world/landmass naming (partially
resolved; Milkäan still open) · `CONFLICT-04` Pitaglorias vs Fitaglorias spelling (mix, unassigned) ·
`CONFLICT-05` Iläria's identity (mix, unassigned) · `CONFLICT-06` founding-year mismatches (Isla de la
Amistad, Nalhuë) · `CONFLICT-07` Sid Nalta vs Sit:Nalta · `CONFLICT-08` Villa Naranja vs Orange Manor ·
`CONFLICT-09` Puerto Tortuga vs Isla Tortuga · `CONFLICT-10` Casa De Esteban vs the legend of Esteban ·
`CONFLICT-11` Bahia Pelicanos vs Bahía de las Estatuas · `CONFLICT-12` timelines.py's origin dates and
"the Seasons" threshold vs. every other epoch · `CONFLICT-13` Aerörea vs Milkäan · `CONFLICT-14` a third,
poster-based era-naming scheme (`ESQUEMA.pdf`) that doesn't cleanly match `ensayo_i` or `libro`.

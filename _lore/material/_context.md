# Context — Excavation Log of `_lore/material/`

Method note: this document treats each source file as an artifact recovered independently, with no
assumption that different artifacts agree with each other or with any outside knowledge. Only what is
written or drawn in the source is recorded here. Where a source poses its own open question or leaves
a blank, that is preserved as a gap, not filled in. Contradictions between sources are noted but not
resolved — resolution is left to the associations in `encodings.json` (flagged) and to `unknowns.md`.

Two spelling variants recur across sources for the same evident concepts (e.g. Milkäan/Milkantida/
Milkantis, Platinhëa/Plathinëa/Plathinea, Pitaglorias/Fitaglorias). Each entry below transcribes the
spelling exactly as it appears in that specific source.

---

## 1. `Atlax I-1.png` … `Atlax I-5.png`
**Type:** in-game book, 5 pages, screenshotted.
**Title (page 1):** "ATLAS DE LAS VIEJAS CIUDADES y otras aldeas" — "DAAXAGORAS[symbol]" (credited name, trailing glyph unreadable).
**Dedication (page 2):** "en recuerdo de PITAGLORIAS — inventor y gran explorador."
**Content (pages 3–5):** an index ("INDICE") of place names with paired numeric coordinates:

| Place (as written) | Coordinates |
|---|---|
| Sid Nalta | -130 \| 1250 |
| Citadela de Gorf | 1000 \| 1000 |
| Terfila | 750 \| 1650 |
| Tyrnea | 440 \| 1250 (trailing glyphs unreadable) |
| Khol Moshin | 1275 \| 225 |
| Thrul Mahotta | 2175 \| -115 |
| Khan Ice | 2630 \| -25 |
| Khan ae Mogulaq (name partly unreadable glyphs precede it) | 2470 \| -530 |
| Catraniz | 2800 \| -1600 |

No further text. No explanation of what the coordinate pair axes represent (not labeled X/Z/Y).

---

## 2. `Atlax II-1.png` … `Atlax II-5.png`
**Type:** in-game book, 5 pages, screenshotted, presented as a sequel/companion to Atlax I.
**Title (page 1):** "ATLAX II — LA ERA DEL DAX" — "STORFILIAS" (credited name).
**Body text (pages 2–4, transcribed in full):**
> "Durante la era del Dax se realizaron importantes desarrollos en el Mundo Conocido. Mayor conocimiento vino a auxiliar en la construccion de nuevas estructuras que permitirian el avance hacia una epoca de esplendor virtuoso.
> La Nueva Cartografia impulso el desarrollo urbanistico de las distintas urbes principales, abriendose rutas que conectarian los centros sociales, dando paso a su vez a nuevos asentamientos. Este ATLAX recoge la informacion de aquellos lugares y a su vez de aquellos anteriores que, por una u otra razon, no entraron en los registros dejados por Fitaglorias en su ATLAX original."

Note the spelling shift: the dedicatee of Atlax I is written "PITAGLORIAS"; this second book calls the same original-atlas author "Fitaglorias." Treated here as the same referenced figure, but the discrepancy is preserved (see `unknowns.md`).

**Index (page 5):**

| Place | Coordinates |
|---|---|
| Salthos Cruzados | -539 \| 70 \| 3163 (three numbers, format differs from Atlax I's two-number pairs) |

---

## 3. `Catastro Milkaan y Platinhëa.xlsx`
**Type:** spreadsheet, single populated sheet, header row + 38 data rows (rows 3–40; rows 41–1000 are empty formatting rows).
**Columns:** Nombre, Continente, Zona, Tipo, Condicion, Tamaño, Inicio, Aeropuerto, Observaciones, Prioridad, Dificultad, Coordenadas. The last four columns (Observaciones, Prioridad, Dificultad, Coordenadas) are empty for nearly every row — only one row (Lündria) has an Observaciones note, and no row has Prioridad, Dificultad, or Coordenadas filled in despite the columns existing.
**"Continente" is literally "Antiguo" for all 38 rows** — no other continent value appears anywhere in the sheet (see `unknowns.md`).
**"Zona" only takes two values:** "Platinhëa" or "Milkäan."
**"Inicio" is a real-world calendar year** (2011–2025), not an in-world date.

Full transcription:

| Nombre | Zona | Tipo | Condicion | Tamaño | Inicio | Aeropuerto | Observaciones |
|---|---|---|---|---|---|---|---|
| Serenity Village | Platinhëa | Investigacion | Completo | 90000 | 2023 | Pendiente | |
| Sindäara | Platinhëa | Hospitality | Incompleta | 240000 | 2024 | Pendiente | |
| Bosques De Sindäara | Platinhëa | Biome | Completo | 1210000 | 2024 | No | |
| Bahia Pelicanos | Platinhëa | Hospitality | Primera Piedra | 250000 | 2024 | No | |
| Grösslor | Platinhëa | Hospitality | Incompleto | 1440000 | 2024 | Pendiente | |
| Gas Stop | Platinhëa | Hospitality | Incompleta | 40000 | 2024 | No | |
| Kurïtsa | Platinhëa | Pueblo | Completo | 250000 | 2020 | Pendiente | |
| Dragon City | Platinhëa | Ciudad | Completo | 1700000 | 2020 | Si | |
| Sälthos Cruzados | Platinhëa | Ciudad | Completo | 500000 | 2013 | Si | |
| Soti | Platinhëa | Aldea | Completo | 400000 | ¿2015? | Si | |
| Castillo Del Sol | Platinhëa | Castilllo | Primera Piedra | 10000 | 2023 | No | |
| Lundria | Platinhëa | Pueblo | Incompleto | 300000 | 2020 | Si | "Mejorar éntradas, terminar plaza, terminar puerto" |
| Nueva Gondola | Platinhëa | Pueblo | Incompleto | 60000 | 2024 | Si | |
| Orange Manor | Platinhëa | Residencia | Completo | 150000 | 2024 | Si | |
| Nalhuë (ministerio Del Tiempo) | Platinhëa | Estatal | Incompleto | 135000 | 2024 | Si | |
| Nvhi | Milkäan | Estatal | Incompleto | 150000 | 2018 | Si | |
| Balhëm | Milkäan | Templo | Incompleto | 3000000 | 2017 | Pendiente | |
| Têrfyla | Milkäan | Ciudadela | Incompleto | 120000 | 2012 | Si | |
| Tÿrnea | Milkäan | Ciudadela | Incompleto | 200000 | 2012 | En Evaluacion | |
| Sit:nälta | Milkäan | Ciudad | Incompleto | 1500000 | 2012 | Si | |
| Görff | Milkäan | Reino | Incompleto | 400000 | 2012 | Si | |
| Khôl Moshin | Milkäan | Pueblo | Incompleto | 120000 | 2012 | En Evaluacion | |
| Puerto Pastizal | Milkäan | Puerto | Incompleto | 300000 | 2012 | Si | |
| Isla De La Amistad | Milkäan | Aldea | Completo | 10000 | 2011 | No | |
| Khân Ice | Milkäan | Ciudad | Completo | 1320000 | 2012 | En Construccion | |
| Kanae Mogulac | Milkäan | Recidencia | Completo | 2500 | 2012 | No | |
| Reznik | Milkäan | Castilllo | Primera Piedra | 10000 | 2013 | No | |
| Catraniz | Milkäan | Ciudadela | Incompleto | 120000 | 2013 | En Evaluacion | |
| Puerto Del Norte | Milkäan | Puerto | Primera Piedra | 250000 | 2020 | No | |
| Pueblo Camilo Ricarda | Milkäan | Aldea | Incompleto | 90000 | 2025 | No | |
| Wasteland | Milkäan | Biome | Primera Piedra | 6000000 | 2023 | No | |
| Muro Norte | Milkäan | Estatal | Primera Piedra | (empty) | 2023 | No | |
| Puerto Tortuga | Milkäan | Puerto | Primera Piedra | 10000 | 2019 | No | |
| Puerto Varilla | Milkäan | Puerto | Primera Piedra | 60000 | 2020 | Si | |
| Casa De Esteban | Milkäan | Investigacion | Completo | (empty) | ¿2012? | No | |
| Ciudad Del Viento | Milkäan | Templo | Incompleto | 160000 | 2024 | No | |
| Templo Del Gato | Milkäan | Templo | Completo | (empty) | 2024 | No | |
| Aurora | Milkäan | (empty) | (empty) | (empty) | (empty) | No | |

---

## 4. `ENSAYO I.pdf`
**Title:** "ENSAYO I — ACERCA DE LAS HISTORIAS DE MILKÄAN Y PLATHINËA"
**Credited author:** "Iläria desde Lündria"
**Stated update date:** noviembre 2025

**Time-metric key, transcribed verbatim:**
- 20 min real = 1 día y una noche en Minecraft
- 1 mes real = 6 años en Tiempo de Minecraft
- 1 año real = 72 años en Tiempo de Minecraft
- 0 = 1 de enero 2013
- a.V. = Antes del Vórtex
- d.V. = Después del Vórtex

This is a full, dated era-by-era history, the most complete single timeline in the material set. Ten numbered sections, transcribed with dates, player counts, and named events/places/persons exactly as given:

1. **La Isla de la Amistad y la Primera Etapa de Subsistencia** — -96 a.V. a 0 a.V. (oct 2011 – dic 2012), 3 jugadores. First players ("herederos de las tierras de Milkantis") base at Puerto Pastizal, region Milkäan. First architectural styles, first routes east "en busca del sol y su energía." Four bedrock corner-monuments and the first mausoleum built. Era ends with the shelter of Khân-Icê and discovery of quartz-device ruins; interacting with it opens "el Vortex," transporting players to another world where the lost city of Góndola was founded.
2. **Las Guerras de Görff** — 18 d.V. a 114 d.V. (abr 2013 – jul 2014), 3 jugadores. Definitive return from the Vortex to a changed world. Castle of Görff, fortress of Sït:Nâlta, citadels of Têrfyla and Tÿrnea built; thin political balance over resources; no routes yet, only magic-users traveled and mixed cultures. End of 72 d.V.: Puente de Todas las Naciones built, maritime exploration begins, inspired by "la leyenda de Esteban y el Reloj de Sol," leading to discovery of Plathinëa by Têrfyla navigators. Castle Sâlthos Cruzados built by prince Döran (son of a "terfilës," member of the Academia de Sït:Nâlta); world cartography begins there. 84 d.V.: first Juegos de Milkäan; princes Forlän and Forlîas of Têrfyla (Academia students) attend; Görff's champion loses to Forlän, sparking enmity with the young kingdom of Khân-Ice that eventually becomes an invasion plan. 90 d.V.: Tÿrnea attacked and destroyed by Görff forces, who seize university artifacts and spells to reactivate the Vórtex; Forlîas's sacrifice lets Têrfyla's people flee, leaving the citadel abandoned "hasta el día de hoy"; Sït:Nâlta shelters the refugees and magically destroys the bridge to the continent. Forlän's subsequent journey and the Battle of Joglöria give victory to Khân-Icê, marking the era's end around 100 d.V. 114 d.V.: founding of Khôl-Moshin and the second mausoleum begin an era of calm.
3. **Okasia y la Segunda Etapa de Subsistencia** — 120 d.V. a 144 d.V. (finales 2014), 3 jugadores. Okâsia founded as a precarious village far from the world's origin point; first Ender Pearl obtained. Vläar the explorer travels to the mythic island of Sit:Nâlta seeking riches, succeeds in 144 d.V., but — having grown greedy and looted the ancient magical fortress's walls — dies falling into lava on the way back to Okâsia. The bosque del Dääx is discovered during this expedition. His visit lets the old kingdoms be repopulated by new cultures.
4. **Era del Mosaico** — 150 d.V. a 360 d.V. (ene 2015 – dic 2017), 3 jugadores. Begins with the rise of Sâlthos Cruzados, then the world's largest city and pioneer of mosaic art inherited from Sit:Nâlta's relics. After Görff's restoration with industrial ideals, a group led by charismatic Auroboro undertakes voluntary exile, founding Catraniz north of Milkäan, seeking Görff's lost glory and becoming a major mosaic-art center. 354 d.V.: the sacred city of Balhâm founded south of the region.
5. **Era del Daax** ("Primera época de los códigos") — 360 d.V. a 504 d.V. (ene 2018 – dic 2019), 4 jugadores. 372 d.V.: construction of the library of Nvhi begins. Görff's new government first uses "códigos"; the Dääx is carved into the ruins of Tÿrneas and into other cities as a symbol of peace and contemporary technology. The Puente Ondulante is built, joining both continents. Ends with the arrival of a new player after many years and settlement at Puerto Tortuga; the bank of Têrfyla is founded.
6. **Era del Confinamiento** — 510 d.V. a 648 d.V. (ene 2020 – dic 2021), 9 jugadores. Begins with a ship's arrival at Puerto de Norte and the founding of Lûndria. Second great era of códigos, via command blocks; great rise of Khân-Ice, which becomes the world's largest city. 534 d.V.: first expedition to the Cordillera de Eurasori. 540 d.V.: new players arrive, road construction begins; in Platinhëa the town of Küritsa is founded with the world's first museum. 552 d.V.: Península Dragon and Aldea Fina founded. First train lines begin, connecting Küritsa and Sâlthos Cruzados. 564 d.V.: the historic Sit:Nâlta coliseum is destroyed and rebuilt by the Sâlthos Cruzados government. The Juegos de Milkäan are reestablished in honor of Forlän and Forlîas, held in Khân-Ice, which becomes the new world capital for its unprecedented size. Puerto Varillas and the Sit:Nâlta "globopuerto" are built. From 582 d.V., ocean design begins and the "Vías de Hielo" are built, enabling the third subsistence settlement (after Puerto Pastizal and Okâsia).
7. **Era de los Continentes** — 664 d.V. a 808 d.V. (ene 2022 – feb 2024), 11 jugadores. More players arrive. Mass automation begins in Platinhëa; Banco de Platinhëa founded; Salón Divino created in the Sit:Nâlta ruins, hub of the teleportation network. Spawn point changed a third time, to Bahía de las Estatuas. Rise of Península Dragon. Abril 2022 (684 d.V.): Palacio del Dragón and Universidad de Sâlthos Cruzados built; the "culto del cubo flotante de Lûndria" expands, and temples begin to be built. Julio (702 d.V.): new survival village Friendly Village built, where the dragon armor is forged. 714 d.V.: Villa Naranja founded at "85.000 al este," starting the Camino del Dragón. Finales de 2022 (736 d.V.): bridge at "80,000" built. Marzo 2023 (754 d.V.): village at "50k" built; later, the monument to "Vito" near Khol Moshin. Mayo 2023: first blocks of the future Ministerio del Tiempo built on the Nalhuë mountain. Julio 2023 (778 d.V.): Rivolta Stage built in the Sindära forests, north end of Platinhëa, future home of the Sindära festival. Octubre 2023 (796 d.V.): Península Dragón absorbs Aldea Fina, becoming Dragon City; villagers begin settling parts of Platinhëa; a 3-life express train connects Sälthos Cruzados and Dragon City. Noviembre 2023 (802 d.V.): Zotti repopulated, Jölystick built, Salón Divino renovated. Diciembre (808 d.V.): the Gran Mapa begins at Castillo del Sol; 10th anniversary of Sâlthos Cruzados celebrated; Gran Render Distance arrives; Torre Espacial built; new corner monuments mark the "5K." 814 d.V.: Serenity Village founded as a mineral-research center; Wasteland discovered north of Milkäan and the great north wall built; the Sâlthos Cruzados map is finished, deliberately leaving the far north undescribed "para que las futuras generaciones encuentren nuevos biomas." 820 d.V.: the server changes (leaving Realms behind), ending this era.
8. **Era de la Imaginación** — 826 d.V. a 946 d.V. (marzo 2024 – octubre 2025). Mass mod-based technology integration (cars to aircraft). Ciudad del Viento and Orange Manor built; Nueva Góndola founded as the fifth subsistence village. Mayo 2024 (840 d.V.): Montañita Lodge built; paved roads begin in Platinhëa; Sälthos Cruzados port construction begins; highway P-33 to Sindäara built, discovering Grösslor along the way; waystones introduced; airports built at Sälthos Cruzados and Dragon City (by then the largest city in Milkantis); first Gran Prix held at Sälthos Cruzados; Gran Museo del Desierto built to house every structure ever built in the world. 850 d.V.: the great map of Sälthos Cruzados destroyed by misuse of códigos by Dragon City's mages. 856 d.V.: Templo del Gato built on Milkäan's east end. 880 d.V.: Nvhi renovation begins. 882 d.V.: world "luminación" project begins in Görff, but provokes a curse in Têrfya and the ambitious project is temporarily cancelled. By 900 d.V., zones destroyed in the Görff wars undergo a renaissance: artists and architects inspired by the legends of Forlän and Forlîas rebuild the city with a focus on creativity; the old crossroads and Khol Moshin are refurbished. Archaeologists discover forgotten artifacts and documents revealing an ancient power of manifestation that could yield new theoretical minerals, "como el örikal y la magia."
9. **Era de la Magia** — 952 d.V. a la actualidad (noviembre 2025 – actualidad). Aldea Camilo Ricarda founded; its people discover a spell in Milkantis that forces subsistence-mode living from the north frontier into the unknown lands beyond the wall. Separately, inspired by information heard in Nvhi about arcane monuments, new ecosystems, and continents larger than Platinhëa and Milkäan combined, the traveler Därnis sails south from Sindäara, finds an ocean "más allá de su imaginación" (almost losing his sanity), and after a tortuous voyage reaches the volcanic island described in Nvhi's writings, discovering the world's first floating lands — taken as a sign of having reached the new continent.
10. **Predicciones para el año 1000 d.V.** (agosto 2026) — explicitly labeled as proposals/predictions, not established fact. Proposed new cities: Arkän, Prismätika, Mirage Citadel, Zafiria.

---

## 5. `Libro de los Tiempos, los Espacios y los Lugares.docx`
**Type:** Word document, an explicit work-in-progress outline/index for a larger planned book. Much of the body is a table of contents and section headers with only partial content filled in; several lines are literally open questions the authors posed to themselves. These are preserved as such, not treated as answered.

**Title:** "LIBRO DE LOS TIEMPOS, LOS ESPACIOS Y LOS LUGARES"

**Prefacio (verbatim, condensed):**
> "Este libro fue comenzado en la coalescencia de las iniciativas de Nikkostratos y Milkucha por cristalizar un hilo común para recordar y comprender la geografía y cronología del Mundo de Milka. Muchos intentos de recopilación de los distintos materiales cartográficos e históricos del mundo se han emprendido en el pasado... Comenzamos a trabajar en este documento el año 94 SBW, 2022 AD... El objeto es hacer de esto un trabajo orgánico que crezca conforme lo hace nuestro conocimiento y experiencia."
> Signed: "Milkucha (a.k.a. Camilo) — Berlín, Febrero 2022 AD"

This identifies two real-world co-authors of this specific document: **Milkucha (a.k.a. Camilo)** and **Nikkostratos**. It also introduces a metric not present in ENSAYO I: **SBW ("Since the Beginning of the World")**, said to be calculated from Minecraft ticks — but the document itself leaves "Cómo se calcula el SBW" as an unanswered outline point.

**Section I — Sobre los Tiempos.** Contains an *alternate* era scheme, given only as a bare outline (no narrative detail like ENSAYO I's), naming eras differently and periodizing them differently:
- Primera Venida — 2012 (Sep–Dic) — "Creación de la cultura."
- Segunda Venida — 2013 (Ene–Mar)
- Tercera Venida — 2013 ago – 2014 jul — "Se fundan las primeras ciudades."
- Era del Mosaico — 2016–2017 — "Se fundan nuevas ciudades."
- Era del Daax o de las Máquinas — 2018–2020 — "Expansión de las estructuras y edificios."
- Era de los Reinos Naturales — 2020–actualidad — "Llegada de más jugadores al mundo. Creación de Océanos, Montañas y Rutas."

This does not match ENSAYO I's era names, boundaries, or count (see `unknowns.md`). The section also lists an open, unelaborated roster under "Qué jugadores existen y han existido": **Milkucha, Termixdelosandes, Nicolas Alba, Nikkostratos, Gaboleos, Seleniau, Frvnco, Marcopolo, Sacrown12, Piroma91, Tommy, Koala, Hermanafranco.** No roles, dates, or descriptions are given for any of them.

**Section II — Sobre los Espacios.** Mostly bare headers ("Descubrimiento," "Terraformación," "Mapas generales," etc.) with almost no prose. Two content items:
- A captioned image: **"Milka Oceans Plan and Continents Outline (18.10.2020 AD)"**. **Correction (2026-07-24):** this was originally assigned here to `image6.png` (the aerial/parchment-style map) based on paragraph-proximity in the extracted text. A later material drop added a standalone file, `Milka Oceans Plan and Continent Outline (18.11.2020).png`, whose *content* is a higher-resolution version of `image7.png` (the labeled grid map), not `image6.png` — and it carries essentially this same title (one month later: 18.11 vs 18.10.2020). The caption almost certainly belongs to the grid map, not the parchment map. `image6.png` reverts to uncaptioned/unidentified. See entry 19 below and `unknowns.md`.
- Under "CONTINENTES," two names are listed with no further text: **Plathinea** and **"Milkhantida (is there another name?)"** — the parenthetical is the document's own unresolved question, transcribed verbatim.
- Under "ISLAS": **"Sit:Nalta, Saari, otras"** — "Saari" and "otras" (others) are not identified further anywhere in the material set.

**Section III — Sobre los Lugares.** Also mostly headers, with two populated lists:
- **Ciudades A.V. (antes del vórtice):** Isla de la Amistad (2012), Puerto Pastizal (2012), Khan Ice (2012).
- **Ciudades D.V. (después del vórtice):** Khol Moshin (2013), Citadela de Gorff (2013), Sit:Nalta (2013), Puerto de Terfyla (2013), Universidad de Tyrnea (2013), Salthos Cruzados (2013), Catraniz (2015?) — with coordinates "2800, -1600" attached directly in the text, matching Atlax I and the grid map exactly — Balhâm (2017), Nvhi (no year given), Kuritsa (2020), Peninsula del Dragon (2020), Aldea Fina (2020).
- **Mausoleos**, with raw X/Y/Z-style coordinates:
  - Mausoleo 1: -80, 65, -33
  - Mausoleo 1.1: -108, 69, -316
  - Mausoleo 2 (noted as "3 venida"): 1358, 87, -382
- **Monumentos** (bare list, no detail): Bahía de las Estatuas, Guardián de Görff, Dragón de Balham.
- **Rutas** section header lists "Camino de Forlán" and "Sistema Intercontinental de trenes" as topics to cover, but no content follows.
- The line "Quiénes son les autores?" appears as an unanswered open question in the document itself.

**Embedded images (7 total, `image1.png`–`image7.png`):**
- **`image7.png`** is a labeled world grid map (columns -11 to 11, rows -11 to 11) with a coordinate/grid reference table for many named places. Transcribed exactly:

  | Place | X | Y | Grid |
  |---|---|---|---|
  | Khan Ice | 3,200 | 500 | 4,1 |
  | Khol Moshin | 1,300 | -200 | 2,-1 |
  | Khan Ae Mogulac | 2,500 | -500 | 2,-1 |
  | Catraniz | 2,800 | -1,600 | 3,-2 |
  | Puerto del Norte | 3,500 | 1,300 | 3,1 |
  | Puerto del Este | 6,100 | 1,100 | 6,1 |
  | Puerto Pastizal | -100 | -100 | -1,-1 |
  | Fuerte Fabian | 1,000 | -3,300 | 1,-3 |
  | Tyrnea | 300 | 1,200 | 1,2 |
  | Terfila | 800 | 1,600 | 1,2 |
  | Gorff | 1,000 | 1,000 | 1,2 |
  | Sid Nalta | (none listed) | (none listed) | 2,-1 |
  | Milkantida | (none listed) | (none listed) | 1,-1 |
  | Salthos Cruzados | (none listed) | (none listed) | 4,-1 |
  | Balem | (none listed) | (none listed) | 4,3 |
  | Nvhi | (none listed) | (none listed) | 6,3 |
  | Isla Tortuga | (none listed) | (none listed) | 7,3 |
  | Peninsula Dragon | (none listed) | (none listed) | 4,-3 |
  | Aldea De Selenne | (none listed) | (none listed) | 4,-4 |

  Note: "Milkantida" appears here as a place with its own grid cell, listed alongside cities — distinct from its use elsewhere as a name for the world/landmass as a whole (see `unknowns.md`). "Aldea De Selenne" does not appear in any other source file.

- **`image1.png`, `image2.png`, `image3.png`, `image4.png`, `image5.png`** — in-game screenshots (a snowy settlement with a colosseum-like structure and a fire-ringed monument; a snowy area with a torii-style gate and steaming vents; a daylight stone castle with towers; a snowy riverside building at dusk; an aerial view of a garden/farm plaza). None carry captions in this document. Three of them sit in the document immediately after the "Ciudades A.V." list (Isla de la Amistad / Puerto Pastizal / Khan Ice) and one immediately after "Khol Moshin / Citadela de Gorff," suggesting proximity to those sections. **Update:** a later drop of material included the same five screenshots as standalone files with explicit place+date captions — see entries 9–10 below. They are pixel-identical (or same-scene) matches: `image1.png` = `Khan Ice 2 (26.08.2020).png`, `image2.png` = `Khan Ice 1 (26.08.2020).png`, `image3.png` = `Gorff 1 (17.07.2020).png`, `image4.png` = `Khan Ice 3 (26.08.2020).png`, `image5.png` = `Gorff 2 (17.07.2020).png`. Only `image6.png` (the parchment-style aerial map, captioned "Milka Oceans Plan...") and `image7.png` (the labeled grid map) remain accounted for as before; none of the newly-dropped files matches `image6.png`.

---

## 6. `timelines.py`
**Type:** Python script, no narrative content — a working calculator for converting the world's Minecraft tick-count into calendar time. Comments in the file (transcribed) describe two competing internal models:
- **"Synchronized Timeline"** — driven directly by `/time query gametime` tick counts. Variables: `wt` (total ticks in the world), `wt_atbs` ("total ticks... at the beginning of the seasons"), `wt_as` (ticks "in the Eras After the Seasons"). Hardcoded values in the script: `wt_atbs = 1930880897`, `wt = 1962121156`. Conversion constants: `dw = 24000` ticks/day, `mw = 30` days/month, `yw = 360` days/year (all in ticks).
- **"Parallelized Timeline"** — driven by real-world calendar dates instead of raw ticks. Variables: `O` (origin) `= date(2012, 7, 1)`; `Ox` (origin of "the Eras After the Seasons") `= date(2025, 12, 31)`; `P = date.today()`. Real-time-to-game-time ratio is **not constant**: before "the Seasons," each in-world day = `hr/3` real hours (i.e. 20 real minutes/day — matching `ENSAYO I`'s stated ratio); after "the Seasons," each in-world day = `hr` full real hour (a 3x slowdown). The script prints the world's computed age in years/months/days, the current year "EAS" (Eras After the Seasons), and a countdown to "the millenium" (year 1000).

This introduces a concept not named anywhere else in the material: **"the Seasons"** and **"the Eras After the Seasons" (EAS)**, a before/after threshold distinct from both the Vórtex (a.V./d.V.) and the Venidas system. Its origin date (`O = 2012-07-01`) also does not match any epoch given elsewhere (`ENSAYO I`'s epoch 0 is 1 January 2013; `Libro`'s work began "el año 94 SBW, 2022 AD"). The script is commented such that only the Parallelized Timeline's print statements are active; the Synchronized Timeline's output lines are commented out, though the calculation itself (`st_calculate`) still runs.

---

## 7. `ESQUEMA.pdf`
**Type:** a landscape infographic ("poster") PDF, one page of legend text plus one page of graphic timeline content. Titled **"LINEA DE TIEMPO"**, subtitled **"MILKÄNTIS — 'EL RIO DEL TIEMPO'"** (yet another spelling of the world's name: **Milkäntis**). Because this is a text layer extracted from a graphically laid-out poster (rotated axis labels, a horizontal timeline with vertically-set era names), the *reading order* of the extracted text is not reliable even though the *characters* are — spatial layout does not survive extraction. This is flagged explicitly below wherever it affects a transcription.

**Method note printed on the poster itself:** "La documentación para la construcción de este esquema temporal consiste en libros del mundo, diarios de los jugadores, placas conmemorativas y la memoria colectiva" (world books, player diaries, commemorative plaques, and collective memory) — i.e. the poster is itself a secondary compilation, not a primary source, and says so.

**New continent name.** The legend states: "...las tierras de Milkäntis y sus dos continentes más importantes, **Aerörea** y **Platinhëa**..." This names *Aerörea* as one of Milkäntis's two main continents — paired with Platinhëa exactly where every other source pairs "Milkäan" with Platinhëa/Plathinëa. No source anywhere states how "Aerörea" and "Milkäan" relate (see `unknowns.md`).

**Two named time-axes.** The poster's vertical axis is called "El Vertice del Tiempo," explicitly carrying two parallel scales: **"Tiempo Divino"** (measured in years) and **"Tiempo Interno"** (measured in ticks).

**Era row (bottom of the graphic).** A horizontal sequence of color-coded era markers, each with a name and a d.V. date range, transcribed in the order extracted:

| Era name (as extracted) | Range | Note |
|---|---|---|
| Isla de la Amistad | -96 a.V. – 0 V | matches `ensayo_i` era 1 exactly |
| Guerras de Görff | 18 d.V. – 114 d.V. | matches `ensayo_i` era 2 exactly |
| Guerras de Görff *(same name repeated)* | 120 d.V. – 144 d.V. | this date range is identical to `ensayo_i`'s **Okasia** era (era 3); the repeated name is very likely a rotated-text extraction artifact, not a genuine second "Guerras de Görff" — transcribed as-extracted, not corrected |
| Era del Mosaico | 150 d.V. – 288 d.V. | `ensayo_i`'s Era del Mosaico runs 150–360 d.V. — different end boundary |
| Era del Dääx | 294 d.V. – 504 d.V. | `ensayo_i`'s Era del Daax runs 360–504 d.V. — different start boundary, same end |
| Era de los Continentes | 504 d.V. – 648 d.V. | this range matches `ensayo_i`'s **Era del Confinamiento** (510–648 d.V.), not `ensayo_i`'s own "Era de los Continentes" (664–808 d.V.) — same name, different range than its `ensayo_i` namesake |
| Era de la Expansión | 664 d.V. – 804 d.V. | nearly identical range to `ensayo_i`'s "Era de los Continentes" (664–808 d.V.), under a different name |
| Era de las Maravillas | (no range extracted) | continues past 804 d.V.; no end boundary was recovered from the text layer |

**Year-by-year foundation list (left column of the graphic).** A separate, cleaner list pairing each real calendar year with places founded and a d.V./a.V. range, transcribed as extracted (including apparent typos, not corrected):

| Year | Places founded | Range (as extracted) |
|---|---|---|
| 2011 | Isla de la Amistad | 108 a.V. – 18 a.V. |
| 2012 | Puerto Pastizal, Khân-Icê | 72 a.V. – 18 a.V. |
| 2013 | Sit:Nälta, Görff, Tyrnea, Tërfila, Salthos Cruzados | 18 d.V. – 72 d.V. |
| 2014 | Okasia | 72 d.V. – 144 a.V. *(sic — "a.V." on a d.V.-range row)* |
| 2015 | Catraniz | 144 d.V. – 216 a.V. *(sic)* |
| 2016 | **Sin Registros** ("no records") | 216 d.V. – 288 a.V. *(sic)* |
| 2017 | Balhäm | 288 d.V. – 360 a.V. *(sic)* |
| 2018 | Nvhi | 360 d.V. – 432 a.V. *(sic)* |
| 2019 | Puerto Tortuga, Banco de Terfila | 432 d.V. – 504 a.V. *(sic, printed "504a.V.")* |
| 2020 | Lundria, Puerto del Norte, Eurasori, Kurista, Peninsula Dragon | 504 d.V. – 576 d.V. |
| 2021 | Puerto Varillas, **Tercera Aldea Survival** | 576 d.V. – 648 d.V. |
| 2022 | Friendly Village, Villa Naranja, Camino del Dragon | 648 d.V. – 720 d.V. |
| 2023 | Dragon City, Zotti, **Holistick**, Serenity Village | 720 d.V. – 792 d.V. |

Notable new data points: **2016 is explicitly marked "Sin Registros"** — the poster itself acknowledges a records gap, it isn't a gap on our end. **"Eurasori"** appears listed as if founded/settled in 2020, alongside places like Lundria and Kurista — elsewhere (`ensayo_i`) "Cordillera de Eurasori" is a mountain range that received its "first expedition" in 534 d.V., not a founded settlement; whether this is the same Eurasori is unclear. **"Tercera Aldea Survival"** (2021) reads as a descriptive label ("Third Survival Village") rather than a proper name, and its date/position lines up with `ensayo_i`'s unnamed "tercer emplazamiento de subsistencia" (era 6, ~582 d.V.) — a plausible but unconfirmed match for a place `unknowns.md` had flagged as missing a name. **"Holistick"** (2023) is spelled differently from `ensayo_i`'s "Jölystick" (also dated 2023/802 d.V.) — very likely the same place, alias added.

---

## 8. `Book of Inventions.docx`
**Type:** Word document, companion volume to "Libro de los Tiempos..." — same real-world authorship context. Title page: "BOOK OF INVENTIONS — To be found and taken from the Realm of Milka" (this document is written in English, unlike the other lore texts).

**Preface (transcribed):**
> "In the year 94 SBW, 2022 AD, I began compiling this collection of guidelines to document the implementation of all past knowledge on commands that have been used in the Realm of Milka. The goal pursued was to have this book serve as both a historic archive, and as a handy reference for all present and future endeavours in the world. This will be an ongoing journey that will take, hopefully, an infinite time to complete."
> Signed: "**Milkcha** (a.k.a. Camilo) — Berlin, February 2022" *(note the spelling "Milkcha," one letter short of "Milkucha" as spelled everywhere else — transcribed as written)*

The "94 SBW, 2022 AD" date is identical to `Libro de los Tiempos...`'s own prefacio date — both documents were evidently written in the same sitting/week.

Like `Libro`, this document is explicitly unfinished: its own index promises "Overview of Useful Commands," "Inventions" (with sub-sections "Explosive Artifacts" and "Working Clock"), but only "Explosive Artifacts" has any content; "Working Clock" never appears in the body, and "Overview of Useful Commands" is four bare command names (`/attribute`, `/data`, `/execute`, `/forceload`) with no explanation.

**Explosive Artefacts (full content):** three command-block machines, each described in-world-flavor plus literal Minecraft commands: **Explosive Arrows** (arrows detonate on impact via a repeating command block summoning a creeper with a settable `ExplosionRadius`, max 127 — "this affects all arrows in the game, so Skeletons will become very dangerous. Beware."); **Fire Arrows** (spectral arrows ignite their surroundings via `/fill ... fire`); **Snow Grenade** (snowballs become TNT-equivalent grenades via an area-effect-cloud trick). The text states: "A collection of these three machines exists in **Osmory (-2505, 53, 168)**. They were deactivated on 94 SBW, but can always be turned on again." — **Osmory** is a place name that appears nowhere else in the material.

The document ends with an unrelated, unlabeled scoreboard snippet (a `TownLAND` objective that detects players within 200 blocks of a point and displays a "TOWN" title) and a single bare number, `1426575558`, with no explanation for either.

---

## 9. `Gorff 1 (17.07.2020).png`, `Gorff 2 (17.07.2020).png`
**Type:** in-game screenshots, explicitly labeled and dated in the filename (17 July 2020). `Gorff 1` shows a daylight stone castle with towers, red banners, a checkered wall pattern, and a drawbridge — confirmed identical to the uncaptioned `image3.png` embedded in `Libro de los Tiempos...`. `Gorff 2` shows an aerial view of a garden/farm plaza (greenhouse dome, crop rows, a red boat-like structure, a fountain) — confirmed identical to `Libro`'s uncaptioned `image5.png`. Together these confirm both of those previously-unidentified `Libro` images depict **Görff**.

## 10. `Khan Ice 1 (26.08.2020).png`, `Khan Ice 2 (26.08.2020).png`, `Khan Ice 3 (26.08.2020).png`
**Type:** in-game screenshots, labeled and dated (26 August 2020). `Khan Ice 1` (a snowy area with a torii-style gate, watchtower, and steaming double-vent structure) matches `Libro`'s `image2.png`. `Khan Ice 2` (a snowy settlement with a colosseum-like structure and a fire-ringed monument) matches `Libro`'s `image1.png`. `Khan Ice 3` (a snowy riverside colonnaded building at dusk, red-lit) matches `Libro`'s `image4.png`. Confirms all three previously-unidentified `Libro` images depict **Khân Ice**.

## 11. `Terfila Old 1.png`, `Terfila Old 2.png`, `Terfila Old 3.png`
**Type:** in-game screenshots, labeled ("Terfila Old") but **not dated**, unlike the Gorff/Khan Ice sets. They show a formal white/grey stone plaza with tall spired towers, a domed building, ceremonial arches, and manicured gardens — a distinctly different, more monumental architectural style than anything else visually documented so far. This is the first visual material for **Térfila** in the whole set. The "Old" qualifier is not explained (old relative to what — a rebuild? the "old" pre-Görff-war citadel versus a modern one?).

## 12. `Cartography (Map Markers) [Code].xlsx`
**Type:** spreadsheet, three sheets (`Highways`, `Trains`, `Airports`) — a working technical register of exact in-world waypoint coordinates for routes and transit infrastructure, evidently maintained for build/pathing purposes rather than as a narrative source. Hundreds of individual waypoints are not transcribed here; only named routes, named waypoints, endpoints, and totals are.

**Highways sheet** — five labeled route segments, each a chain of X/Z waypoints with per-segment distances:
- **"Ruta Puente Intercontinental - Nvhi" (code M7):** (2091, 5669) → (589, 2906). Total ≈ 3987.6 blocks.
- **"Ruta Nvhi - Khan Ice" (code M9):** (1810, 4392) → (3818, 489). Total ≈ 6630.9 blocks. A 3-point spur labeled **"Anexo"** ("Annex") branches from (1718, 4210) area, ≈ 187.1 blocks.
- **"Ruta A33":** (-2934, 9764) → (-3387, 4450). Total ≈ 7334.8 blocks.
- **"Ruta P-33 (Extension)":** continues from A33's endpoint (-3387, 4450) → (-5114, 1708). Total ≈ 4188.4 blocks. This confirms `ensayo_i`'s mention of highway "P-33 hasta Sindäara" (Era de la Imaginación) is a real, plotted route, and that it is a continuation of "Ruta A33."

**Trains sheet** — a chain of connected named-endpoint segments forming one continuous line, plus named intermediate waypoints not previously documented: **Gorff → Khan Ice** (ending at (3219, 317), total ≈ 3769.4); **Khan Ice → Puerto del Norte** (passing an unnamed junction, ending at (3473, -1278), total ≈ 2057.8); a segment labeled **"Khol Moshin"** passing a waypoint named **"Cruce de Trobal"** (2333, 85) and ending at a waypoint named **"Monte Pastizal"** (-35, -248, total ≈ 1718.2) — "Monte Pastizal" ("Mount Pastizal") is new, not documented elsewhere, and its name suggests proximity to Puerto Pastizal; **Khan Ice → Balhâm** (ending (2468, 3262), total ≈ 3713.0); **Balhâm → Salthos Cruzados** (ending (-516, 3100), total ≈ 3992.2).

**Airports sheet** — a clean lookup table, transcribed in full:

| Location | Code | X | Z |
|---|---|---|---|
| Catraniz | CTZ | 2923 | -1757 |
| Gorff | GRF | 1239 | 1017 |
| Terfila | TFL | 699 | 1794 |
| Sit:Nalta | SIT | -1004 | 1123 |
| Lundria | LDR | -4883 | 1576 |
| Dragon | DRG | -3078 | 4161 |
| Sälthos Cruzados | SCR | -25 | 3249 |
| Soti | SOT | -3157 | 3065 |
| Nalhuë | NLH | -11374 | 1940 |
| Nvhi | NVH | 2200 | 6243 |

These are airport-specific coordinates (not necessarily city centers), and several differ substantially from that same place's other recorded coordinates elsewhere in the material — treated as additional, separately-labeled data points rather than merged into a single "the" coordinate for each place (see `encodings.json`).

## 13. `Luminacion Register [Code].xlsx`
**Type:** spreadsheet, three sheets (`NPC`, `Code`, `Taterzen`). Per the user, this is lore, of a split kind: a **narrative layer** (named characters, their home localities, their roles, and in several cases a described route or errand) and a **technical layer** ("a mysterious formula that defines the bounds of reality and the way it behaves, which is only understandable by some") that is not being interpreted here.

The narrative layer: ~40 named inhabitants (e.g. Bardaglis the musician, Dägna the barkeeper, Kristok Jakur the blacksmith, Trifolis the architect — mostly based in Gorff, with others in Lundria, Puente Continental, Terfila, Sid Nalta-Terfila, and Khol Moshin), each with a locality, an NPC "type" (Static/Dynamic/Hybrid), and often a role. A number of entries describe named travelers with a specific route and mode of transport — airplanes for long hauls (Galandis flies Nvhi→Khan Ice, Gizen flies Gorff→Catraniz), boats for water routes (Murunu, Gorff→Ciudad Dragon), griffons and camelbacks for shorter/local ones (Kjon and Kjon-Ukk ride griffons Khan Ice→Gorff; Saltamontabiras rides a camelback from Tyrnea). This mix of transport technology (cars, airplanes) alongside creature-mounts (griffons, camelbacks) is not described in any narrative prose source — it's only visible here. Full roster in `encodings.json`'s `characters.named_inhabitants`.

The technical layer: a `Code` sheet of generated mocap-trigger commands keyed to `Clock worldTime` scoreboard values, and a `Taterzen` sheet of in-progress Taterzens setup commands (movement-mode switching by player distance, Blabber dialogue-start commands referencing real UUIDs and dialogue JSON filenames like `daegna001.json`, `nerkeli001–003.json`). Left undeciphered — see `unknowns.md`.

## 14. `Terraforming Regions Purge Register.xlsx`
**Type:** spreadsheet, four sheets (`Assorted Regions`, `North West Regions`, `South Regions`, `Roads`). Also treated as lore's technical layer per the user, rather than excluded. On its face it is a checklist of Minecraft region files (`.mca`, each a 512×512-block area) with pass/fail flags, evidently used to track which regions had been reviewed for a terrain "purge" (deletion/regeneration of unused chunks) across two passes ("First Try"/"Second Try"). Its `Roads` sheet duplicates the same waypoint data as `Cartography...xlsx`'s "Ruta Puente Intercontinental - Nvhi (M7)," apparently kept here as a reference so road-adjacent chunks wouldn't be purged. The bounding coordinates covered are very large (region indices from roughly -21 to 4, i.e. tens of thousands of blocks across), consistent with a large, sparsely-built explored area rather than a tightly-bounded "home" region. No named characters or events here — if this file encodes narrative meaning at all, it hasn't surfaced from a literal reading; left as unread technical substrate, not discarded.

---

## 15. `El Antiguo Continente de Milkan - Mapa del Milenio.png`
**Type:** a wide (3100×1248) top-down terrain render, purely visual, no text labels baked into the image. Title translates to **"The Old Continent of Milkan — Map of the Millennium."** Flagged by the user as apparently the most recent piece in the collection (file timestamp 2026-07-24, well after everything else).

The rendered landmass shape matches the continent enclosed by the yellow outline in entry 19 below (the "Milka Oceans Plan and Continent Outline" map) — i.e. this is very likely a finished/high-detail terrain render of that same outlined continent. Two markers are visible with no explanation: a small magenta/pink dot roughly centered on the landmass, and a yellow line tracing a specific north–south path through the lower-middle of the map (possibly a specific highlighted route, though it isn't captioned and doesn't obviously match any of the named routes in `Cartography...xlsx`).

**"Milkan"** is yet another spelling of the region name (joining Milkäan/Milkaan/Milkantis/Milkäntis/Milkantida). **"Milenio"** (Millennium) directly echoes `ENSAYO I`'s own era 10, "Predicciones para el año 1000 d.V. (agosto 2026)" — the in-world millennial year. This file being the most recently added, and the *only* file in the whole set to use the word "Milenio," makes a plausible connection to that specific in-world milestone (a "millennium map" made for or around that occasion) — not confirmed by any text in the file itself, since it carries no text.

**Possible resolution to the open "Continente: Antiguo" question** (see `unknowns.md`): the Catastro spreadsheet tags all 38 of its rows with `Continente: Antiguo`. This file's title, "El Antiguo Continente de Milkan," is the first source to actually use "Antiguo" as part of a proper name for a specific, mapped continent — the one containing Milkäan and (per the yellow outline) apparently Platinhëa as well. This is suggestive that "Antiguo" names *this* continent specifically, in contrast to a separate "new" continent (plausibly the one Därnis reaches south of Sindäara in `ensayo_i` era 9) — but this is an inference from a title, not a stated fact, and the user's own answer to the original question was "not sure yet."

## 16. `Khan Ice (WP 17.11.2020).png`
**Type:** a zoomed web-map style render (browser map plugin screenshot — road/plot outlines in brown, structure footprints rendered in flat color blocks, consistent with a Dynmap or BlueMap capture rather than a Chunky-style photorealistic render). Shows a dense, gridded city built around a river delta, snow-capped terrain to the north, and a large circular structure (matching the colosseum visible in `Khan Ice 2 (26.08.2020).png`). The **"WP"** in the filename is not explained anywhere in the material — possibly "waypoint," possibly a map-plugin/export label; not resolved.

## 17. `Sid Nalta (WP 17.11.2020).png`
**Type:** same web-map style as entry 16, same date. First visual documentation of **Sid Nalta/Sit:Nâlta** as a built location (previously only known by name and disputed coordinates). Shows three connected built areas: a walled/bordered zone with a small village on pale terrain (left), a larger tan/desert-toned area with dense structures and an octagonal stadium-like building (center), and a grey, partly snow-capped rocky area with a circular dish/observatory-like structure (right). The center and left areas are linked by a long, straight teal double-line (a bridge or rail line).

## 18. `Milka General Map (17.11.2020).png`
**Type:** a full terrain render (2048×1587) with unexplored/unrendered chunks shown as solid black — effectively a snapshot of how much of the world had been explored/rendered as of 17 November 2020. Same date as entries 16–17, likely from the same mapping session. No text labels. One small orange/red mesa-toned patch appears in the upper-right area of the rendered landmass; otherwise the terrain is unremarkable green/tan/white biome coloring, consistent with the other terrain renders in this set.

## 19. `Milka Oceans Plan and Continent Outline (18.11.2020).png`
**Type:** a very high-resolution (4630×4627) version of the same labeled grid map embedded as `image7.png` in `Libro de los Tiempos...` — same coordinate table (Khan Ice, Khol Moshin, Khan Ae Mogulac, Catraniz, Puerto del Norte, Puerto del Este, Puerto Pastizal, Fuerte Fabian, Tyrnea, Terfila, Gorff, Sid Nalta, Milkantida, Salthos Cruzados, Balem, Nvhi, Isla Tortuga, Peninsula Dragon, Aldea De Selenne, transcribed in full in entry 5 above), reproduced identically here. Its title closely matches the caption found in `Libro` ("Milka Oceans Plan and Continents Outline"), one month apart in date (18.10.2020 in `Libro`'s caption vs. 18.11.2020 in this file's own name) — see the correction note in entry 5 above; this is almost certainly what that caption refers to, not `image6.png`.

This higher-resolution copy reveals overlay detail invisible in the compressed embedded version:
- A **thick yellow outline** tracing the full landmass — very likely the literal "Continent Outline" the title refers to, and the same shape as the terrain rendered in entry 15's "Mapa del Milenio."
- **Two separate orange-outlined regions**, smaller polygons overlaid on the yellow one — one in the north (roughly grid -3,-4) and one near the center (roughly grid -1,1 to 0,1). Neither is labeled.
- Roughly ten **white triangle markers** scattered across the continent, and **two small red dot markers** (near grid 9,1 and grid 4,6) — none captioned. Style matches the white triangles seen in entry 20 below.

None of these overlay elements (yellow outline aside) are explained by any label in this or any other source.

## 20. `Ruta Lundria-Salthos Cruzados.png`
**Type:** a cropped web-map screenshot (same Dynmap/BlueMap style as entries 16–17), showing a **thick yellow border**, a **purple traced line** running diagonally across the frame, a smaller **orange-outlined region** (top right), and several unlabeled **white triangle markers** — visually the same marker/outline vocabulary as entry 19, suggesting these screenshots are the working source material from which that grid map's overlays (and possibly the `Cartography...xlsx` route data) were digitized.

The filename, **"Ruta Lundria-Salthos Cruzados"** ("Lundria–Sälthos Cruzados Route"), names a route not present anywhere else in the material — it does not match any of the named highways (M7/M9/A33/P-33) or train segments (Gorff–Khan Ice, Khan Ice–Puerto del Norte, Khol Moshin, Khan Ice–Balhâm, Balhâm–Salthos Cruzados) already catalogued from `Cartography...xlsx`. The purple line in the image is presumably this route's path, but no coordinates accompany it here.

---

## 21. `ENSAYO I (Final Version).pdf`
**Type:** a later edition of entry 4's `ENSAYO I.pdf`, dropped into `_lore/material/` 2026-07-26. Cited below as `ensayo_i_final`, against `ensayo_i` for the November 2025 edition.

**Title page changes.** Subtitle shortened from "ACERCA DE LAS HISTORIAS DE MILKÄAN Y PLATHINËA" to **"ACERCA DE LAS HISTORIAS DE MILKÄNTIS"** — the "Milkäan y Plathinëa" regional pairing is dropped in favor of the whole-world name "Milkäntis" as the essay's stated subject. Byline expands from "Por Iläria desde Lündria" to **"Por Iläria Astraëa desde la lejana ciudad de Lündria"** — a surname, Astraëa, appears for the first time, plus the "lejana" (distant/far-off) qualifier on Lündria. Update date moves from noviembre 2025 to **julio 2026**. The time-metric key at the top (20 min/1 mes/1 año, epoch 0 = 1 enero 2013, a.V./d.V.) is unchanged verbatim — until era 9 introduces a second, later metric (see below).

**Per-era parenthetical tags.** Every one of eras 1–6 now carries a short parenthetical tag after its date range, absent from `ensayo_i`: era 1 "(Cuadro de la isla com living)", era 2 "(antepasado de Gorff)", era 3 "(loot)", era 4 "(cofre con materiales)", era 5 "(mimiatura)" (very likely a typo for "miniatura"), era 6 "(" — left empty/unclosed, apparently not yet filled in. Eras 7–10 carry none. These read as labels for a physical artifact or exhibit item associated with each era — plausibly tied to some in-world museum/exhibit context — but none of the tags are explained anywhere in the document itself; transcribed as-extracted, not interpreted further here.

**Era 1 date split.** `ensayo_i`'s era 1 range is a clean "-96 a.V. - 0 a.V." (octubre 2011 - diciembre 2012). `ensayo_i_final` renders it as "-96 - 30 a.V. - 0 a.V." against a real-date range of "octubre 2011-julio 2012 - diciembre 2012" — an extra breakpoint at 30 a.V. / julio 2012 is inserted mid-era, splitting what was one continuous span into two. Nothing in the prose explains what happens at that midpoint; the era's narrative content is otherwise identical. Flagged in `unknowns.md`.

**Era 8 — the örikal passage moves and changes character.** `ensayo_i` ties the örikal discovery to the "Para 900 d.V." paragraph: archaeologists find forgotten documents revealing "un antiguo poder de manifestación que podría traer nuevos minerales teóricos, como el örikal y la magia" — hedged, speculative, undated more precisely than "para 900 d.V.", and that same paragraph also credits a group of artists/architects (inspired by Forlän/Forlîas legends) with rebuilding the war-torn zones around creativity. `ensayo_i_final` moves the örikal material fifteen-plus years earlier, folding it into the 882 d.V. sentence instead: "Documentos olvidados que revelan **el proceso de manifestación de un nuevo mineral, el örikal**" — stated as settled fact, not hedged, and no longer paired with "la magia" in the same breath. The artists/architects sentence is dropped entirely from the 900 d.V. paragraph, which now reads only "Para 900 d.V. las zonas destruidas durante las guerras de Görff, experimenta un renacimiento. Se refacciona la antigua encrucijada y Khol Moshin." Both accounts are kept on record; see `CONFLICT-17`.

**Era 9 — village rename, frontier expansion, and a new founding.** `ensayo_i`: "Se funda (aldea Camilo Ricarda) quienes descubren que existe en Milkantis un hechizo que fuerza a vivir en subsistencia desde la frontera norte hacia las tierras desconocidas tras el muro." `ensayo_i_final`: "En 952 d.V. llega una nueva jugadora y se funda **Humucherry**. Se descubre que existe en Milkantis un hechizo que fuerza a vivir en subsistencia desde la frontera **norte y oeste** hacia las tierras desconocidas tras el muro." Two changes: the village's name is now given as Humucherry rather than the parenthetical "(aldea Camilo Ricarda)" — which is also the name on file in the Catastro (`Pueblo Camilo Ricarda`, start 2025) — see `CONFLICT-15`; and the spell's frontier is widened from "norte" alone to "norte y oeste". The Därnis passage is reproduced verbatim, with one addition at the very end: **"Es aqui donde fundan Auräli."** — `ensayo_i` ends the passage at "...había llegado al nuevo continente," with no settlement named. Auräli is therefore a new fact, not present in the November 2025 edition.

**Era 9 — a wholly new closing arc, absent from `ensayo_i` entirely.** After the Auräli sentence, `ensayo_i_final` continues with content that does not exist in the November 2025 edition at all:

> "En 964 d.V. (enero de 2026) se ralentizó el tiempo y los días pasaron a durar 30 minutos al igual que las noches. Esto divide por tres la métrica a partir de ahora en adelante, las cuales quedarían: 60 min Real = 1 dia y una noche en Minecraft / 1 Mes Real = 2 años en Tiempo de Minecraft / 1 Año Real = 24 años en Tiempo de Minecraft."

This is a second, later time-metric conversion table, a 3x slowdown from the original 20-min-real/1-day ratio to 60-min-real/1-day, dated to 964 d.V. (enero de 2026). This lines up closely with `timelines_py`'s previously-unexplained "Eras After the Seasons" threshold (`Ox = 2025-12-31`, also a 3x day-length slowdown) — see the updated `seasons_eas` concept and `CONFLICT-12`.

The prose continues past the new metric: "Comienza la época del World Edit. Se funda de Kursuviros, y comienza la construcción del Puerto de las Lunas y su terminal de carga. Llega un nuevo jugador al mundo que inicia su aventura cerca de las ruinas de Sit:Nalta, fundando Shonogami en 966 d.V. se construye la primera prision en una isla al oeste de Milkán. En 968 d.V. se construye el terminal de pasajeros del Puerto de las Lunas y el gran Faro. En el nuevo continente, en 968 d.V se funda Tax de rich. En 970 d.V. se mapea completamente todo el nuevo continente, se prohíbeme la manipulación del dia y la noche y se instaura el survival mas alla de los limites del océano del antiguo continente." — new places: Kursuviros, Puerto de las Lunas (with a cargo terminal, then a 968 d.V. passenger terminal and "el gran Faro"), Shonogami (founded 966 d.V. near the Sit:Nalta ruins by an unnamed new player), an unnamed first prison (966 d.V., an island west of Milkán), and Tax de rich (968 d.V., on the new continent — name transcribed as-extracted, unexplained).

Finally: "Hacia el 980 d.V. comenzó a construirse la Feria del Milenio, con sus 5 pabellones, la cual es inaugurada el 26 de julio de 2026, celebrando los 1000 años SBW (Since the Begining of the World)." This is the first *objective-record* confirmation of the Feria del Milenio's construction start (~980 d.V.), pavilion count (5), and inauguration date (26 julio 2026) — previously the Feria was known only through `hearsay.md` entries from played dialogues. It also confirms `ensayo_i_final` itself now uses the "SBW" abbreviation, previously seen only in `libro`/`book_of_inventions` (entry 5, line 143) and never in `ensayo_i`'s original edition. See new concept `feria_del_milenio`.

**Era 10 — a different date and an entirely different predictions list.** `ensayo_i`'s era 10 is headed "PREDICCIONES PARA EL AÑO 1000 d.V (agosto 2026)" and lists four proposed new cities: Arkän, Prismätika, Mirage Citadel, Zafiria. `ensayo_i_final`'s era 10 is headed "PREDICCIONES PARA EL AÑO 1000 d.V (**26 julio 2026**)" — the exact date now matches the Feria's own stated inauguration date, given two sentences earlier — and lists five entirely different, non-overlapping predictions: (1) El auge del Orikäl, (2) La resurrección de Tÿrnia y Têrfyla, (3) El colapso del muro del norte, (4) La construcción del Museo de las Estructuras y el Jardín de las Naciones, (5) El Ministerio del Tiempo funcionando. None of the four originally-proposed city names carry over. Both lists are kept on record as two states of the same document's predictions, seven-plus months apart; see `CONFLICT-16`.

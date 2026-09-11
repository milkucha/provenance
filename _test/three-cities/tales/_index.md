# Tale — Told Directly

This is a third source of truth for Milkantis, alongside the **objective record**
(`_lore/material/_context.md` → `_lore/encodings.json`) and the **in-fiction subjective
record** (`_lore/characters/hearsay.md` — what a *character* said inside a played dialogue, never
merged into the objective arrays). A tale is told directly by the user, the world's author, outside
of any character's mouth and outside of any excavated document — whether narrated as a story or
stated plainly as a fact now known. Deliberately not distinguishing those with a fact/fiction label on
individual entries — a tale can be partly true, the way a real legend often is, and that ambiguity is
the point. It is treated as genuine, on-par source material: folded into `encodings.json`'s objective arrays
(`locations`, `characters`, `concepts`, `routes`, `time_systems`) wherever its content overlaps an
existing entry, the same way a newly-analysed `_lore/material/` file is folded in per
`.claude/skills/integrate/SKILL.md` Pass 1 — new entries can be added, a disagreement gets a
`conflicts` entry (never silently resolved), but no existing entry is ever overwritten to make room
for a tale.

Populated by the `/tell` skill (`.claude/skills/tell/SKILL.md`). One file per tale, named for its
slug (`<slug>.md`). Every tale also gets an entry in `encodings.json`'s `tales.entries[]` array — see
that array's own `_method_note` for the exact shape and what `touches` means.

Every tale distinguishes two different provenance questions. **`told_by`** (optional, lives in
`encodings.json` — it's lore, and can be sampled) is who is credited *in-fiction* with this telling,
if the tale itself is framed that way; most tales leave it unset, since a tale is normally just told
directly with no in-world frame. **`responsible`** (mandatory, lives in `_lore/tales/_authors.md` —
never in `encodings.json`) is which *real-world user* told the system this tale. That field has no
in-fiction meaning at all and is walled off from `scripts/lore/sample_lore_knowledge.py`'s reach on
purpose, the same way `_lore/facts/facts.json` is — see that file's own `_comment`.

Like every source in this world, this one is partial too — a person only ever tells part of what they
know, at whatever moment they choose to tell it. A tale left unfinished, or one that raises a question
it doesn't answer, is not a defect; the gap is logged in `_lore/unknowns.md` like any other.

## Tales on record

| Told | Title | Told by | Responsible | File | Touches |
|---|---|---|---|---|---|
| 2026-07-30 | The Peregrins | — | milkucha | `peregrins.md` | new concept `peregrins`; annotated the existing bare "Peregrin"/"Peregrins" census role tags (Terfila, Gorff) |
| 2026-07-30 | Creepers and Night Monsters | no one; simply now known | milkucha | `creepers_and_night_monsters.md` | new concept `world_hazards` |
| 2026-07-30 | Redstone and Basic Needs | no one; simply now known | milkucha | `redstone_and_basic_needs.md` | new concepts `redstone`, `basic_needs` |
| 2026-08-31 | Salthos Cruzados | — | milkucha | `salthos_cruzados.md` | new location `salthos_cruzados` |
| 2026-08-31 | Terfila | — | milkucha | `terfila.md` | new location `terfila` |
| 2026-08-31 | Gorff | — | milkucha | `gorff.md` | new location `gorff` |
| 2026-08-31 | The Gorff Ledger of the Crossing War | Gorff's keepers of record | milkucha | `gorff_ledger_crossing_war.md` | new concepts `crossing_toll_dispute`, `temple_of_the_crossing`, `salthos_mediator_line`; new conflicts `CONFLICT-01`, `CONFLICT-02`, `CONFLICT-03` |
| 2026-08-31 | The Merchant-House Log of Forliamus | the merchant-house of Forliamus, Terfila | milkucha | `forliamus_log_crossing_war.md` | concepts `crossing_toll_dispute`, `temple_of_the_crossing`, `salthos_mediator_line`; conflicts `CONFLICT-01`, `CONFLICT-02`, `CONFLICT-03` |
| 2026-08-31 | The Crossing Market's Roof | — | milkucha | `crossing_market_roof.md` | new concept `crossing_market_roof` |
| 2026-08-31 | The Toll Ledger's Arrears | the Salthos house's own toll tally | milkucha | `toll_ledger_arrears.md` | new concept `toll_ledger_arrears` |
| 2026-08-31 | A New Betrothal Offer | the Forliamus house | milkucha | `forliamus_betrothal_offer.md` | new concept `forliamus_betrothal_offer` |
| 2026-08-31 | The Birth of Nierius | no one; simply now known | milkucha | `birth_of_nierius.md` | none |
| 2026-08-31 | The Birth of Darnus | no one; simply now known | milkucha | `birth_of_darnus.md` | none |
| 2026-08-31 | The Birth of Darika | no one; simply now known | milkucha | `birth_of_darika.md` | none |
| 2026-08-31 | The Birth of Niergus | no one; simply now known | milkucha | `birth_of_niergus.md` | none |
| 2026-08-31 | The Birth of Niemius | no one; simply now known | milkucha | `birth_of_niemius.md` | none |
| 2026-08-31 | The Birth of Darnakus | no one; simply now known | milkucha | `birth_of_darnakus.md` | none |
| 2026-08-31 | The Death of Darius | no one; simply now known | milkucha | `death_of_darius.md` | none |
| 2026-08-31 | The Birth of Dorakus | no one; simply now known | milkucha | `birth_of_dorakus.md` | none |
| 2026-08-31 | The Birth of Fenrius | no one; simply now known | milkucha | `birth_of_fenrius.md` | none |
| 2026-08-31 | The Birth of Darnukas | no one; simply now known | milkucha | `birth_of_darnukas.md` | none |
| 2026-08-31 | The Birth of Niemoran | no one; simply now known | milkucha | `birth_of_niemoran.md` | none |
| 2026-08-31 | The Birth of Niekus | no one; simply now known | milkucha | `birth_of_niekus.md` | none |
| 2026-08-31 | The Birth of Dornakus | no one; simply now known | milkucha | `birth_of_dornakus.md` | none |
| 2026-08-31 | The Death of Niemus | no one; simply now known | milkucha | `death_of_niemus.md` | none |
| 2026-08-31 | The Birth of Nieragus | no one; simply now known | milkucha | `birth_of_nieragus.md` | none |
| 2026-08-31 | The Birth of Nakoran | no one; simply now known | milkucha | `birth_of_nakoran.md` | none |
| 2026-08-31 | The Death of Magus | no one; simply now known | milkucha | `death_of_magus.md` | none |
| 2026-08-31 | The Birth of Dorukus | no one; simply now known | milkucha | `birth_of_dorukus.md` | none |
| 2026-08-31 | The Death of Prince Doran | no one; simply now known | milkucha | `death_of_prince_doran.md` | none |
| 2026-08-31 | The Death of Nakus | no one; simply now known | milkucha | `death_of_nakus.md` | none |
| 2026-08-31 | The Birth of Fenarnus | no one; simply now known | milkucha | `birth_of_fenarnus.md` | none |
| 2026-08-31 | The Birth of Darnarika | no one; simply now known | milkucha | `birth_of_darnarika.md` | none |
| 2026-08-31 | The Birth of Doraknus | no one; simply now known | milkucha | `birth_of_doraknus.md` | none |
| 2026-08-31 | The Death of Niergus | no one; simply now known | milkucha | `death_of_niergus.md` | none |
| 2026-08-31 | The Birth of Fenriukas | no one; simply now known | milkucha | `birth_of_fenriukas.md` | none |
| 2026-08-31 | The Birth of Nieragan | no one; simply now known | milkucha | `birth_of_nieragan.md` | none |
| 2026-08-31 | The Birth of Nakorika | no one; simply now known | milkucha | `birth_of_nakorika.md` | none |
| 2026-08-31 | The Birth of Dornarika | no one; simply now known | milkucha | `birth_of_dornarika.md` | none |
| 2026-08-31 | The Death of Darnus | no one; simply now known | milkucha | `death_of_darnus.md` | none |
| 2026-08-31 | The Birth of Dornarius | no one; simply now known | milkucha | `birth_of_dornarius.md` | none |
| 2026-08-31 | The Birth of Nieradus | no one; simply now known | milkucha | `birth_of_nieradus.md` | none |
| 2026-08-31 | The Birth of Fenekus | no one; simply now known | milkucha | `birth_of_fenekus.md` | none |
| 2026-08-31 | The Death of Dorakus | no one; simply now known | milkucha | `death_of_dorakus.md` | none |
| 2026-08-31 | The Death of Fenserika | no one; simply now known | milkucha | `death_of_fenserika.md` | none |
| 2026-08-31 | The Death of Niemius | no one; simply now known | milkucha | `death_of_niemius.md` | none |
| 2026-08-31 | The Birth of Darinak | no one; simply now known | milkucha | `birth_of_darinak.md` | none |
| 2026-08-31 | The Birth of Niemornak | no one; simply now known | milkucha | `birth_of_niemornak.md` | none |
| 2026-08-31 | The Death of Darnukas | no one; simply now known | milkucha | `death_of_darnukas.md` | none |
| 2026-08-31 | The Death of Darnakus | no one; simply now known | milkucha | `death_of_darnakus.md` | none |
| 2026-08-31 | The Birth of Niemoruk | no one; simply now known | milkucha | `birth_of_niemoruk.md` | none |
| 2026-08-31 | The Death of Darika | no one; simply now known | milkucha | `death_of_darika.md` | none |
| 2026-08-31 | The Birth of Nierakus | no one; simply now known | milkucha | `birth_of_nierakus.md` | none |
| 2026-08-31 | The Death of Niemoran | no one; simply now known | milkucha | `death_of_niemoran.md` | none |
| 2026-08-31 | The Birth of Dornaknis | no one; simply now known | milkucha | `birth_of_dornaknis.md` | none |
| 2026-08-31 | The Death of Darius | no one; simply now known | milkucha | `death_of_darius.md` | none |
| 2026-08-31 | The Death of Niemus | no one; simply now known | milkucha | `death_of_niemus.md` | none |
| 2026-08-31 | The Death of Magus | no one; simply now known | milkucha | `death_of_magus.md` | none |
| 2026-08-31 | The Death of Prince Doran | no one; simply now known | milkucha | `death_of_prince_doran.md` | none |
| 2026-08-31 | The Death of Nakus | no one; simply now known | milkucha | `death_of_nakus.md` | none |
| 2026-08-31 | The Death of Fenserika | no one; simply now known | milkucha | `death_of_fenserika.md` | none |
| 2026-08-31 | The Birth of Farmuken | no one; simply now known | milkucha | `birth_of_farmuken.md` | none |
| 2026-08-31 | The Birth of Forliazco | no one; simply now known | milkucha | `birth_of_forliazco.md` | none |
| 2026-08-31 | The Birth of Tamuzco | no one; simply now known | milkucha | `birth_of_tamuzco.md` | none |
| 2026-08-31 | The Birth of Forliarlo | no one; simply now known | milkucha | `birth_of_forliarlo.md` | none |
| 2026-08-31 | The Birth of Forliuken | no one; simply now known | milkucha | `birth_of_forliuken.md` | none |
| 2026-08-31 | The Birth of Farliazco | no one; simply now known | milkucha | `birth_of_farliazco.md` | none |
| 2026-08-31 | The Death of Tamuken | no one; simply now known | milkucha | `death_of_tamuken.md` | none |
| 2026-08-31 | The Birth of Forliamuk | no one; simply now known | milkucha | `birth_of_forliamuk.md` | none |
| 2026-08-31 | The Death of Forliamus | no one; simply now known | milkucha | `death_of_forliamus.md` | none |
| 2026-08-31 | The Birth of Forliukar | no one; simply now known | milkucha | `birth_of_forliukar.md` | none |
| 2026-08-31 | The Birth of Trezarlo | no one; simply now known | milkucha | `birth_of_trezarlo.md` | none |
| 2026-08-31 | The Death of Farlo | no one; simply now known | milkucha | `death_of_farlo.md` | none |
| 2026-08-31 | The Death of Trezco | no one; simply now known | milkucha | `death_of_trezco.md` | none |
| 2026-08-31 | The Birth of Forliauzco | no one; simply now known | milkucha | `birth_of_forliauzco.md` | none |
| 2026-08-31 | The Birth of Farliukar | no one; simply now known | milkucha | `birth_of_farliukar.md` | none |
| 2026-08-31 | The Death of Forliuken | no one; simply now known | milkucha | `death_of_forliuken.md` | none |
| 2026-08-31 | The Death of Forliarlo | no one; simply now known | milkucha | `death_of_forliarlo.md` | none |
| 2026-08-31 | The Birth of Farliauzco | no one; simply now known | milkucha | `birth_of_farliauzco.md` | none |
| 2026-08-31 | The Birth of Forliauken | no one; simply now known | milkucha | `birth_of_forliauken.md` | none |
| 2026-08-31 | The Birth of Tamuzaken | no one; simply now known | milkucha | `birth_of_tamuzaken.md` | none |
| 2026-08-31 | The Birth of Trezukar | no one; simply now known | milkucha | `birth_of_trezukar.md` | none |
| 2026-08-31 | The Birth of Forliuzazco | no one; simply now known | milkucha | `birth_of_forliuzazco.md` | none |
| 2026-08-31 | The Birth of Tamuzarlo | no one; simply now known | milkucha | `birth_of_tamuzarlo.md` | none |
| 2026-08-31 | The Death of Trezarlo | no one; simply now known | milkucha | `death_of_trezarlo.md` | none |
| 2026-08-31 | The Birth of Forliaukar | no one; simply now known | milkucha | `birth_of_forliaukar.md` | none |
| 2026-08-31 | The Birth of Farliuzco | no one; simply now known | milkucha | `birth_of_farliuzco.md` | none |
| 2026-08-31 | The Death of Forliazco | no one; simply now known | milkucha | `death_of_forliazco.md` | none |
| 2026-08-31 | The Birth of Tamuzmuken | no one; simply now known | milkucha | `birth_of_tamuzmuken.md` | none |
| 2026-08-31 | The Death of Forliamuk | no one; simply now known | milkucha | `death_of_forliamuk.md` | none |
| 2026-08-31 | The Birth of Trezukuzco | no one; simply now known | milkucha | `birth_of_trezukuzco.md` | none |
| 2026-08-31 | The Death of Tamuzco | no one; simply now known | milkucha | `death_of_tamuzco.md` | none |
| 2026-08-31 | The Birth of Tamuzukar | no one; simply now known | milkucha | `birth_of_tamuzukar.md` | none |
| 2026-08-31 | The Birth of Farliauzar | no one; simply now known | milkucha | `birth_of_farliauzar.md` | none |
| 2026-08-31 | The Birth of Tamuzakar | no one; simply now known | milkucha | `birth_of_tamuzakar.md` | none |
| 2026-08-31 | The Birth of Farliazuzco | no one; simply now known | milkucha | `birth_of_farliazuzco.md` | none |
| 2026-08-31 | The Birth of Forliaukarla | no one; simply now known | milkucha | `birth_of_forliaukarla.md` | none |
| 2026-08-31 | The Birth of Trezukaken | no one; simply now known | milkucha | `birth_of_trezukaken.md` | none |
| 2026-08-31 | The Birth of Forliaukarli | no one; simply now known | milkucha | `birth_of_forliaukarli.md` | none |
| 2026-08-31 | The Birth of Tamuzauzco | no one; simply now known | milkucha | `birth_of_tamuzauzco.md` | none |
| 2026-08-31 | The Death of Farliazco | no one; simply now known | milkucha | `death_of_farliazco.md` | none |
| 2026-08-31 | The Birth of Tamuzukauk | no one; simply now known | milkucha | `birth_of_tamuzukauk.md` | none |
| 2026-08-31 | The Death of Darius | no one; simply now known | milkucha | `death_of_darius.md` | none |
| 2026-08-31 | The Death of Niemus | no one; simply now known | milkucha | `death_of_niemus.md` | none |
| 2026-08-31 | The Death of Magus | no one; simply now known | milkucha | `death_of_magus.md` | none |
| 2026-08-31 | The Death of Prince Doran | no one; simply now known | milkucha | `death_of_prince_doran.md` | none |
| 2026-08-31 | The Death of Nakus | no one; simply now known | milkucha | `death_of_nakus.md` | none |
| 2026-08-31 | The Death of Fenserika | no one; simply now known | milkucha | `death_of_fenserika.md` | none |
| 2026-08-31 | The Birth of Aureluko | no one; simply now known | milkucha | `birth_of_aureluko.md` | none |
| 2026-08-31 | The Birth of Mekoboro | no one; simply now known | milkucha | `birth_of_mekoboro.md` | none |
| 2026-08-31 | The Birth of Khaubalo | no one; simply now known | milkucha | `birth_of_khaubalo.md` | none |
| 2026-08-31 | The Birth of Aureboro | no one; simply now known | milkucha | `birth_of_aureboro.md` | none |
| 2026-08-31 | The Birth of Mekaluko | no one; simply now known | milkucha | `birth_of_mekaluko.md` | none |
| 2026-08-31 | The Birth of Khaoboro | no one; simply now known | milkucha | `birth_of_khaoboro.md` | none |
| 2026-08-31 | The Birth of Khaubestro | no one; simply now known | milkucha | `birth_of_khaubestro.md` | none |
| 2026-08-31 | The Death of Khaus | no one; simply now known | milkucha | `death_of_khaus.md` | none |
| 2026-08-31 | The Birth of Aurebako | no one; simply now known | milkucha | `birth_of_aurebako.md` | none |
| 2026-08-31 | The Birth of Aurekobo | no one; simply now known | milkucha | `birth_of_aurekobo.md` | none |
| 2026-08-31 | The Birth of Khaumestro | no one; simply now known | milkucha | `birth_of_khaumestro.md` | none |
| 2026-08-31 | The Birth of Mekhaubo | no one; simply now known | milkucha | `birth_of_mekhaubo.md` | none |
| 2026-08-31 | The Death of Mekestros | no one; simply now known | milkucha | `death_of_mekestros.md` | none |
| 2026-08-31 | The Birth of Aurekhobo | no one; simply now known | milkucha | `birth_of_aurekhobo.md` | none |
| 2026-08-31 | The Birth of Merkhaubo | no one; simply now known | milkucha | `birth_of_merkhaubo.md` | none |
| 2026-08-31 | The Death of Auroboro | no one; simply now known | milkucha | `death_of_auroboro.md` | none |
| 2026-08-31 | The Birth of Khaubaluk | no one; simply now known | milkucha | `birth_of_khaubaluk.md` | none |
| 2026-08-31 | The Death of Aurebalo | no one; simply now known | milkucha | `death_of_aurebalo.md` | none |
| 2026-08-31 | The Death of Merluko | no one; simply now known | milkucha | `death_of_merluko.md` | none |
| 2026-08-31 | The Birth of Mekhaurel | no one; simply now known | milkucha | `birth_of_mekhaurel.md` | none |
| 2026-08-31 | The Death of Mekaluko | no one; simply now known | milkucha | `death_of_mekaluko.md` | none |
| 2026-08-31 | The Birth of Khaobako | no one; simply now known | milkucha | `birth_of_khaobako.md` | none |
| 2026-08-31 | The Death of Khaubalo | no one; simply now known | milkucha | `death_of_khaubalo.md` | none |
| 2026-08-31 | The Birth of Aurelkhau | no one; simply now known | milkucha | `birth_of_aurelkhau.md` | none |
| 2026-08-31 | The Death of Khaoboro | no one; simply now known | milkucha | `death_of_khaoboro.md` | none |
| 2026-08-31 | The Birth of Mekobaluk | no one; simply now known | milkucha | `birth_of_mekobaluk.md` | none |
| 2026-08-31 | The Birth of Aurekomest | no one; simply now known | milkucha | `birth_of_aurekomest.md` | none |
| 2026-08-31 | The Birth of Mekaurelo | no one; simply now known | milkucha | `birth_of_mekaurelo.md` | none |
| 2026-08-31 | The Birth of Mekhaubest | no one; simply now known | milkucha | `birth_of_mekhaubest.md` | none |
| 2026-08-31 | The Birth of Mekhaobako | no one; simply now known | milkucha | `birth_of_mekhaobako.md` | none |
| 2026-08-31 | The Birth of Aurelkomest | no one; simply now known | milkucha | `birth_of_aurelkomest.md` | none |
| 2026-08-31 | The Birth of Khaubomest | no one; simply now known | milkucha | `birth_of_khaubomest.md` | none |
| 2026-08-31 | The Death of Aureboro | no one; simply now known | milkucha | `death_of_aureboro.md` | none |
| 2026-08-31 | The Birth of Aureskomest | no one; simply now known | milkucha | `birth_of_aureskomest.md` | none |
| 2026-08-31 | The Death of Mekoboro | no one; simply now known | milkucha | `death_of_mekoboro.md` | none |
| 2026-08-31 | The Birth of Khaubekho | no one; simply now known | milkucha | `birth_of_khaubekho.md` | none |
| 2026-08-31 | The Birth of Mekhaobera | no one; simply now known | milkucha | `birth_of_mekhaobera.md` | none |
| 2026-08-31 | The Birth of Mekaurelu | no one; simply now known | milkucha | `birth_of_mekaurelu.md` | none |
| 2026-08-31 | The Birth of Mekaurobal | no one; simply now known | milkucha | `birth_of_mekaurobal.md` | none |
| 2026-08-31 | The Death of Khaubestro | no one; simply now known | milkucha | `death_of_khaubestro.md` | none |
| 2026-08-31 | The Birth of Khaubomako | no one; simply now known | milkucha | `birth_of_khaubomako.md` | none |

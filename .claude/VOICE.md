# Author's voice

Read by every skill and session in this project, alongside `PRINCIPLES.md` — this is the house
rule for one specific thing: how prose gets *written*, not what gets decided.

**Any prose written for this project in the author's own register — README, TODO, LAB_REPORT,
commit messages, in-repo notes, and any other first-person or documentation writing — should sound
like the author, not like default assistant prose.** That means imitating their actual recurring
vocabulary and rhetorical habits, not approximating "casual tone" in generic terms. This does not
apply to *lore/character content* (dialogue, hearsay, tales) — that already has its own rule, author
primacy on user-supplied wording, and its own voice per character; this file is about the project's
own documentation and meta-writing.

Two registers show up in the source material, and they should not be blended:

- **Working voice** — planning, system design, technical discussion, project docs (README, TODOs,
  SKILL.md prose, this file). Mostly English.
- **World voice** — in-character dialogue, lore prose, character backstories. Freely bilingual
  (English/Spanish), warmer, more poetic.

This file accumulates over sessions. Append a new dated bullet under "Session log" below whenever
a session reveals another verbatim tic or phrase — don't treat the analysis below as finished, and
don't invent "quirks" that weren't actually observed.

## Working voice

**Hedge before asserting.** Claims arrive wrapped in uncertainty markers, not stated flat:
"I'm not sure", "My intuition is...", "I suppose", "correct me if I'm wrong", "Or am I wrong?".
The hedge is an invitation to be corrected, not false modesty — use it in drafted text when a
design choice is still open, rather than presenting it as settled.

**Actively solicit pushback.** Recurring, near-verbatim: "tell me what you think", "does this make
sense?", "feel free to push back if you want", "Got a pushback on that?", and the reverse — "I
gotta push back there", "I don't buy it". Text in this voice treats disagreement as productive,
not as friction to smooth over.

**Reason by analogy, reached from outside the system.** Abstract design points get grounded in a
concrete, often literary or art-historical image:
- "Like a good painting, which doesn't need to paint every detail of something, but rather only
  needs to insinuate the existence of it, so imagination does the rest."
- Troy, as the distinction between *material* (the legend of a place) and *grounding* (whether the
  ruins are actually there): "The idea of Troy... is what goes on material. The actual existence
  of the ruins of Troy in the real world is what exists in grounding."
- "sort of like putting a seed for world generation in Minecraft" (for non-determinism as a
  feature, not a bug)
- Mythemes explicitly framed via Lévi-Strauss, then qualified past him: "a little bit different
  because he talked about pairs of oppositions... it's rather a different paradigms of existence
  that I'm layering on top of, juxtaposing one another."

When writing design rationale for this project, reach for one grounding image like this rather
than staying in pure systems vocabulary.

**Enumerate when responding to multiple points.** "For number one... For number two... Number
three, it's all good. Number four..." — mirrors back the structure of what was asked before
answering it. Use numbered call-and-response when a text is itself replying to a multi-part
question. Related: stacks several related questions into one paragraph rather than asking one at a
time (e.g. "Is there any recollection...? And if not...? anything else?").

**Ask for less, explicitly.** Recurring requests to compress: "short answer", "briefly and in
simple terms", "don't spit at me a lot of specific information... let's take a more generalist
point of view", "in simple words, we can expand on the details later". Default to compression;
earn length by first establishing that more detail is wanted.

**Revise in the open.** Doesn't erase a false start — builds on top of it: "That's alright... So
maybe that makes me rethink my first answer..." A first pass gets stated, then corrected on the
page rather than silently replaced. Related: self-correcting repetition, restating a word/phrase
immediately before moving on, e.g. "a certain — a certain expressions that I use," "I I wanted to
sound." This stutter-restart cadence is part of the voice, not a typo to silently smooth over when
imitating it.

**States the meta-goal directly rather than implying it.** "I want to experiment with that," "I
want to see also how the structure of the text actually also changes."

**"okay?" dropped mid-paragraph** as a check-in / breath marker before continuing.

**Close a deliberation with a terse go-ahead.** After a long exploratory passage, the turn ends
abruptly: "Let's do it.", "Please implement.", "Perfect. We can commit now.", "Yes. Complete the
entire task please." Don't let closing lines run long — the payoff of a discussion is a short
directive.

**Mix engineering pragmatism with the philosophical register in the same breath.** Token cost,
worktree permissions, and "is this scriptable to save tokens" sit right next to questions about
epistemic architecture and culture-as-ecosystem, in the same message, without a tonal seam. Don't
silo "practical" writing away from "conceptual" writing in this project — they're one voice here.

### Recurring diction (working voice)

- **basically** — the single most common connective filler; used to restate/simplify a claim
  mid-sentence, not to hedge. Also shows up as a closing hedge/summarizer at the end of a clause.
- **organic**, **emergent / emergence**, **ecosystem** — the vocabulary for "not hand-authored,
  but produced by the interaction of simpler rules."
- **slop** — pejorative, specifically for content invented without grounding in the established
  corpus: "not based on slop, only on what is there."
- **lean**, **granular** — the vocabulary of parsimony in system design: exhaustive but not
  bloated ("granular enough to capture the distinctiveness... not more than that... make the
  system lean").
- **let's put a pin on it / let's pin that for now** — defer, don't drop.
- **ponder** — "come and ponder with me", "don't implement, only ponder" — thinking-out-loud mode,
  explicitly distinguished from build mode.
- **Correct?** — appended to the end of a summarizing statement, turning it into a check rather
  than an assertion.
- **sweetspot**, **juxtaposing**, **axioms** (for author-supplied worldbuilding constraints),
  **anchors** (for the fixed points a character's criterion is derived against).
- **dialogic** — a specific recurring keyword for this project; treat it as load-bearing, not a
  one-off.

## World voice (lore prose, in-character dialogue)

Freely code-switches to Spanish for anything spoken *as* a character or *to* one — Spanish is not
a translation layer here, it's the native register for warmth, courtesy, and philosophical
aside. Tone is unhurried, sensory, a little playful, comfortable with silence and gesture.

- Stage directions live in parentheses, sparse and present-tense: "(mira al cielo, y piensa)",
  "(guiño)", "(me cruzo de brazos)", "(I vanish)".
- Trailing, unfinished thought via ellipsis is a deliberate rhetorical move, not just a filler:
  "Tal vez el hecho de que era muy bello... Continuemos."
- Warm, slightly formal courtesy in farewells: "Ha sido un gusto conocerte, Gok."
- Philosophical rhetorical questions dropped into casual dialogue: "¿No somos todos reflejos de
  aquellas cosas que no queremos perder?"
- Concrete, textured worldbuilding nouns preferred over generic ones — named biomes, named eras,
  named artifacts: *la Feria del Milenio, el Espiral de las Eras, Guerras de Gorff, Grandes
  Juegos, lazulis.* Real-world geography/architecture terms are reused as in-world proper nouns
  rather than invented from scratch.
- Backstory and knowledge specs are written as compact, concrete percentage breakdowns, not prose
  summaries: "he knows 29% of the knowledge, 12% from hearsay, 5% from matter adjacent to economy
  and commerce... 4% random." Keep this format when drafting character sheets.
- Dialogue-only rule: when a scene calls for it, "No action cues, only dialog" — the line itself
  has to carry tone without a narrator's stage direction outside of the sparse parentheticals
  above.

## Project lexicon

Use these terms as-is; they are load-bearing vocabulary for this project, not generic synonyms to
vary for style: *mytheme, hearsay, criterion, arc, encodings, grounding, material, tale(s), fact(s),
discovery/discoveries, routine, embodiment, shock, drift, synthesis, reflection, temperament,
corpus of knowledge, epistemic architecture, culture engine, provenance, metabolization of
incompleteness.*

## What not to imitate

A large share of the raw source material is voice-dictated (speech-to-text), which introduces
filler ("um", "uh"), word repetition, and abandoned clauses that are transcription artifacts, not
style: e.g. "Do do I have a toggle?", "do you do you do you know what I mean?". **Do not reproduce
disfluency.** What's real signal from the dictated passages is the *underlying move* — associative
reasoning that circles a topic from several angles before landing, reaching for an analogy,
inviting pushback — not the stutter it arrived in. Write the clean version of that same move.
(Exception: the self-correcting stutter-restart noted above under "Revise in the open" is a
genuine rhetorical habit, not disfluency to strip — the distinction is whether the repetition
*revises* a claim or just stalls before one.)

Likewise, single-word or command-style utterances ("Yes", "Continue please", "1", "/enact") are
utility, not voice — they say nothing about register and shouldn't be treated as a model for
terse prose; the *closing directive* pattern above (a short imperative ending a longer
deliberation) is the real pattern worth keeping.

## Session log

Dated entries for verbal patterns observed in later sessions, additive to the analysis above.

- **2026-08-27** — initial pass folding a full history read into the sections above (see Working
  voice, World voice, Project lexicon, What not to imitate).

**Caveat:** the analysis above is built from a limited sample. Don't over-fit prose to these exact
tics. Keep adding real examples as the author writes more, and let this file grow before leaning
on any one pattern too hard.

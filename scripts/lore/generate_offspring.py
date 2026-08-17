"""
Generate a new character as a genuine mutation of two parents - design debrief 2026-08-10, knowledge
inheritance retuned 2026-08-11. Not an average: every inherited field is either copied whole from a
randomly-chosen parent, or drawn as a randomized subset of a pool. Which specific combination a given
child ends up with is itself the randomness - two agreeing parents can still produce a child who
inherits one's `standard` and the other's `distrusts`, a combination neither parent would have
authored, without any text being freely invented to make it happen.

What's inherited and how:
- `criterion` - **mechanically re-derived, not copied (2026-08-17)**. A straight coin-flip copy
  from one parent (the original 2026-08-10 design, `origin: "inherited"`) meant a whole fast-cycling
  lineage kept a byte-identical criterion generation after generation - confirmed producing exactly
  that in a real 2000-pass run (see LAB_REPORT.md Run 4). A real /character Step 4 derivation is a
  judgment call and can't run here as a subagent: criterion is read SYNCHRONOUSLY the moment a later
  generation reproduces, so deferring it to an end-of-run batch (the way arc/name authoring already
  is) would leave every intervening generation's reproduction/arc-gate decisions made off a
  placeholder no later pass could retroactively fix. So this derivation is mechanical instead:
  `compose_backstory()` first seeds a real (if plain) backstory from one of the child's own
  newly-drawn knowledge items, which guarantees that item collides with it; `find_collision_items()`
  then runs the actual Step 4a scan (word-overlap against backstory OR city, deliberately blind - no
  preference for a city match over a backstory-only one) across the child's FULL knowledge sample,
  `derive_criterion_mechanical()` picks a random item from whatever collides as the anchor and
  composes `wasted_life`/`standard` from a template keyed to it, and `trusts`/`distrusts` come from
  `anchor_epistemology.py`'s real provenance signal (imported directly, not shelled out to) exactly
  as Step 4d prescribes. `origin` is `"derived"` when something collided, `"uncollided"` (blank
  standard/wasted_life/trusts/distrusts) when nothing did - same two values Step 4 itself uses, not
  a third "inherited" value anymore. An internal-only coin-flipped `skew_criterion` (not persisted)
  still exists solely to weight the general-knowledge draw below, same as the old inherited criterion
  used to. See the module-level note above `BACKSTORY_TEMPLATES` for the full reasoning.
- `knowledge.education.items` - three layers, all from _lore/tuning.json's `offspring_knowledge`:
  1. A random subset of the UNION of both parents' own items, floored at
     `parent_education_min_fraction` (default 50%) rather than the old 2026-08-10 version's
     unfloored 1-to-100% draw - a child could previously inherit as little as a single fact from two
     well-read parents; the floor makes "parents' knowledge survives, at least partially" reliable
     instead of a coin flip. `percent`/`mode`/`topic` copied whole from a coin-flipped parent, since
     those describe how the ORIGINAL sample was drawn, not this child's content.
  2. A small amount of genuinely NEW material neither parent had, drawn from _lore/encodings.json's
     own world-lore pools (`concepts`, `locations`, `conflicts`, `characters.named_inhabitants`) -
     the shared setting record that exists independently of any character, so a large enough cast
     can eventually know more than the founding population ever did, rather than every generation
     only ever recombining the same original items forever. Sized as a random fraction (from
     `general_knowledge_fraction_range`, default 15-45%) of however many items step 1 produced, so
     the new material stays proportionate to what was inherited rather than swamping it - a small,
     bounded expansion per generation, not a jump to encyclopedic knowledge. Weighted-sampled without
     replacement, favoring (not restricted to) entries whose own text shares vocabulary with the
     child's own criterion (`criterion_skew_weight`, default 3x) - a child inherits an interest in
     roughly the shape of what they'll come to value, without it being deterministic.
  3. Already-present items are excluded from step 2's draw (no point in "discovering" something a
     parent already knew).
- `knowledge.experience` - previously started empty outright ("the child hasn't lived either
  parent's experience"), which is still true - but some of what a parent lived can still reach a
  child as family lore, the way an actual family passes stories down. A random fraction
  (`parent_experience_fraction_range`, default 10-35%) of the union of both parents' own
  `knowledge.experience` entries is copied over, each wrapped as `"Grew up hearing: <original
  text>"` so it stays legible as secondhand, not the child's own lived action - any `about` tag on
  the original entry is preserved unchanged, so these can still participate honestly in a future
  arc's Step 8 gate-check the same way a genuinely lived experience would.
- `routines` - a random-sized random subset of the union of both parents' routine entries, weights
  renormalized to sum to 100. Still a placeholder in the sense that routines are meant to be
  hand-authored (see _lore/contexts.json) - there's no author present mid-run, so this is the
  honest fallback, not a substitute for eventually hand-revising a child's routines. Not touched by
  this knowledge-inheritance retune - the union-of-both-parents' logic here was never the part that
  needed fixing.
- `arc` - none at birth. Seeded the normal way (context + routine_actions + criterion) the first
  time this character is actually a scene's home_frame - the fallback path (as of 2026-08-16, a
  hand-authored character gets `arc` at creation instead; a newborn still can't, since nothing is
  present to compose one at the moment of birth - see TODO.md's "arc at birth" open question).
- `city` - copied whole from a coin-flipped parent.
- `backstory` - **templated, not just "Child of X and Y." (2026-08-17)** - see `compose_backstory()`
  and the module-level note above `BACKSTORY_TEMPLATES`. Still mechanical, still cruder than a human/
  `/character` session would write, and still open for later enrichment - but now carries a real
  seeded knowledge item so Step 4a's collision-finding has something to work with. Falls back to the
  plain "Child of X and Y." only if the child ended up with no knowledge items at all to seed from.
- `life.span` - freshly rolled via the same range as any character (_lore/tuning.json's
  lifespan_range - not inherited from either parent) - open question left in the original design
  sketch, resolved here as "fresh roll" rather than "heritable trait" for now.

Cooldowns (both from _lore/tuning.json, and deliberately distinct from each other): a **parent**
can't reproduce again for `parent_cooldown_passes` (checked by the caller before this script ever
runs, using `last_reproduced_pass` this script writes) - this stays separate from how soon the
**child** themselves enters `pick_pair.py`'s pool, `child_cooldown_passes` after `birth_pass`
(printed by this script, so the caller never needs to duplicate the number).

Who learns of it, mirroring record_death.py's own circle-notification pattern (per the original
design sketch: "the parents' circles get told immediately, so others know them before they know
them"):
- Both **parents** get a plain `knowledge.experience` line recording the birth directly - this was
  missing from the first version of this script and is not optional; the two people it happened to
  are not "circle" members, they're the event itself.
- The **circle** - reusing notify_death.py's own logic, unioned across both parents (everyone
  either parent has shared a scene with, or is named in either parent's backstory), minus the
  parents and the child themselves - gets the same 30%-sampled, immediate-notification treatment
  a death gets. Everyone else outside that 30% may still hear later the ordinary way (a future
  hearsay draw), same as death's own "remainder" tier.

What this script deliberately does NOT decide: the child's **name**. That's the one place in this
whole mechanism where a model's judgment is the right tool, not a dice roll - composing a name that
reads as a plausible blend of both parents' names isn't something word-overlap or random sampling
can do coherently. Pass the model-composed name in with --name (see roll_reproduction.py's
`name_lead` output for the one piece of that decision that IS dice-driven - which parent's name
leads the blend). The slug is derived from --name automatically (same convention as
record_death.py's own slugify), not a second thing the caller has to decide separately.

Usage:
    py scripts/lore/generate_offspring.py --parent-a khaoe --parent-b gondarfolas \\
        --name "Khordarel" --pass-number 63
"""

import argparse
import json
import random
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import anchor_epistemology as ae  # noqa: E402  (sibling module, sys.path adjusted above)
import notify_death  # noqa: E402
import tuning  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent.parent
CHAR_DIR = ROOT / "_lore" / "characters"
LIFESPANS_PATH = CHAR_DIR / "lifespans.json"
ENCODINGS_PATH = ROOT / "_lore" / "encodings.json"
TALES_DIR = ROOT / "_lore" / "tales"
AUTHORS_PATH = TALES_DIR / "_authors.md"
INDEX_PATH = TALES_DIR / "_index.md"
_TUNING = tuning.load()
SPAN_MIN, SPAN_MAX = _TUNING["lifespan_range"]["min"], _TUNING["lifespan_range"]["max"]
CHILD_COOLDOWN_PASSES = _TUNING["child_cooldown_passes"]
_OK = _TUNING["offspring_knowledge"]
PARENT_EDU_MIN_FRACTION = _OK["parent_education_min_fraction"]
PARENT_EXP_FRACTION_RANGE = _OK["parent_experience_fraction_range"]
GENERAL_KNOWLEDGE_FRACTION_RANGE = _OK["general_knowledge_fraction_range"]
CRITERION_SKEW_WEIGHT = _OK["criterion_skew_weight"]

_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "of", "in", "on", "at", "to", "for", "with", "that",
    "this", "is", "are", "was", "were", "be", "been", "it", "its", "his", "her", "their", "he",
    "she", "they", "not", "no", "who", "what", "when", "where", "which", "one", "only", "own",
    "as", "by", "from", "has", "have", "had", "will", "would", "can", "could", "if", "than",
    "then", "so", "such", "most", "more", "less", "least", "still", "just", "also", "too",
    "very", "already", "never", "always", "every", "each", "any", "some", "without", "before",
    "after", "because", "though", "although", "while", "until", "since", "once", "first",
    "last", "new", "old", "same", "other", "into", "out", "over", "under", "about", "him",
}


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return "_".join(words)


def git_user_name() -> str:
    import subprocess
    try:
        return subprocess.check_output(["git", "config", "user.name"], cwd=ROOT, text=True).strip() or "unknown"
    except Exception:
        return "unknown"


def write_birth_tale(key: str, name: str, parent_names: list) -> str:
    """Writes a real tales[] entry for this birth, mirroring record_death.py's own tale-writing
    exactly - added 2026-08-11, on user correction: a birth is a discrete event, same shape as a
    death, and belongs in tales.entries, not as an ad-hoc "concept: X_birth" hearsay tag with no
    real backing entry (which is what every birth before this fix had been given, entirely by
    convention in scene-writing, never by this script - see LAB_REPORT.md for the retroactive
    cleanup this replaces going forward). Returns the new tale's id so the caller can hand it to
    whoever writes the birth-announcement hearsay claim, tagged `about: "tale: <id>"`."""
    slug = f"birth_of_{key}"
    base_slug, n = slug, 2
    while (TALES_DIR / f"{slug}.md").exists():
        slug = f"{base_slug}_{n}"
        n += 1

    told_date = date.today().isoformat()
    responsible = git_user_name()
    parent_text = " and ".join(parent_names) if parent_names else "unrecorded parents"
    telling = f"{name} was born, child of {parent_text}."

    content = f"""# The Birth of {name}

**Responsible:** {responsible} - real-world provenance only, never an in-fiction detail (also recorded in `_lore/tales/_authors.md`)
**Told by:** no one; simply now known
**Told on:** {told_date}
**Encodings id:** `tales.entries[].id = "{slug}"`

## The tale

{telling}

## Where this lands in the record

- Touches: none
- Conflicts raised: none
- Open questions logged: none
"""
    (TALES_DIR / f"{slug}.md").write_text(content, encoding="utf-8")

    with open(ENCODINGS_PATH, encoding="utf-8") as f:
        encodings = json.load(f)
    encodings["tales"]["entries"].append({
        "id": slug,
        "source_file": f"_lore/tales/{slug}.md",
        "told_date": told_date,
        "told_by": None,
        "summary": telling,
        "touches": [],
    })
    with open(ENCODINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(encodings, f, indent=2, ensure_ascii=False)
        f.write("\n")

    with open(AUTHORS_PATH, "a", encoding="utf-8") as f:
        f.write(f"| `{slug}` | {responsible} | {told_date} |\n")
    with open(INDEX_PATH, "a", encoding="utf-8") as f:
        f.write(f"| {told_date} | The Birth of {name} | no one; simply now known | {responsible} | `{slug}.md` | none |\n")

    return slug


def load_char(key: str) -> dict:
    path = CHAR_DIR / f"{key}.json"
    if not path.exists():
        raise SystemExit(f"No character file for '{key}'.")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_char(key: str, character: dict) -> None:
    path = CHAR_DIR / f"{key}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(character, f, indent=2, ensure_ascii=False)
        f.write("\n")


def coin(a, b):
    return random.choice([a, b])


def sample_union(pool_a: list, pool_b: list, min_fraction: float = 0.0) -> list:
    union = list(dict.fromkeys(pool_a + pool_b))  # de-duplicated, order-preserving
    if not union:
        return []
    floor = max(1, round(min_fraction * len(union)))
    size = random.randint(min(floor, len(union)), len(union))
    return random.sample(union, size)


def extract_keywords(text: str) -> set:
    words = re.findall(r"[a-zà-ÿ]+", (text or "").lower())
    return {w for w in words if len(w) > 3 and w not in _STOPWORDS}


def skew_score(keywords: set, text: str) -> int:
    text_l = (text or "").lower()
    return sum(1 for kw in keywords if kw in text_l)


def weighted_sample_without_replacement(pool: list, weights: list, k: int) -> list:
    pool, weights = list(pool), list(weights)
    chosen = []
    for _ in range(min(k, len(pool))):
        total = sum(weights)
        r = random.uniform(0, total) if total > 0 else 0
        upto = 0.0
        idx = len(pool) - 1
        for i, w in enumerate(weights):
            upto += w
            if upto >= r:
                idx = i
                break
        chosen.append(pool.pop(idx))
        weights.pop(idx)
    return chosen


def load_encodings() -> dict:
    with open(ENCODINGS_PATH, encoding="utf-8") as f:
        return json.load(f)


def general_knowledge_pool(enc: dict) -> list:
    """Returns [(item_tag, searchable_text), ...] from ALL of encodings.json's own pools - not just
    the static pre-run world-lore categories, the growing ones too. Per design debrief 2026-08-11
    (user correction: "when I say general knowledge, I mean ALL of the encodings"):
    hearsay.entries (every claim from every pass any /simulate or /enact session has ever recorded,
    via record_hearsay.py - the actual living lore record, not just pre-run material, and usually
    the largest single pool by far), concepts, locations, conflicts, tales.entries,
    characters.named_inhabitants, characters.in_world_or_legendary,
    characters.real_world_authors_and_players (this project's own established convention already
    treats these as in-fiction-knowable - e.g. Khaoe's own recorded experience of walking the
    gardens with Milkucha), routes.highways/trains/airports/named_but_unplotted, and
    time_systems.ensayo_i_eras (the one era-timeline sub-structure shaped as a plain flat list;
    the other three era systems are each a differently-shaped one-off nested structure cataloguing
    conflicting source material rather than atomic knowable facts, and are deliberately not parsed
    here - flag it if that scoping call should change). All independent of any specific character's
    own file - this is what lets a large enough population's knowledge grow past what the founding
    cast started with."""
    pool = []
    for entry in enc.get("hearsay", {}).get("entries", []):
        eid = entry.get("id")
        if not eid:
            continue
        summary = entry.get("summary") or ""
        for i, claim in enumerate(entry.get("claims", []), start=1):
            text = f"{claim.get('text') or ''} {summary}"
            pool.append((f"hearsay: {eid}#{i}", text))
    for c in enc.get("concepts", []):
        cid = c.get("id")
        if not cid:
            continue
        text = " ".join([c.get("description") or ""] + (c.get("names") or []))
        pool.append((f"concept: {cid}", text))
    for loc in enc.get("locations", []):
        lid = loc.get("id")
        if not lid:
            continue
        text = " ".join([loc.get("region") or "", loc.get("type_catastro") or ""] + (loc.get("names") or []))
        pool.append((f"location: {lid}", text))
    for cf in enc.get("conflicts", []):
        cfid = cf.get("id")
        if not cfid:
            continue
        text = " ".join([cf.get("topic") or "", cf.get("detail") or ""])
        pool.append((f"conflict: {cfid}", text))
    for tale in enc.get("tales", {}).get("entries", []):
        tid = tale.get("id")
        if not tid:
            continue
        pool.append((f"tale: {tid}", tale.get("summary") or ""))
    by_locality = enc.get("characters", {}).get("named_inhabitants", {}).get("by_locality", {})
    for locality, inhabitants in by_locality.items():
        for person in inhabitants:
            if isinstance(person, dict):
                name, role = person.get("name"), person.get("role") or ""
            else:
                name, role = person, ""
            if not name:
                continue
            pool.append((f"inhabitant: {name} ({locality})", f"{role} {locality}"))
    for legendary in enc.get("characters", {}).get("in_world_or_legendary", []):
        lid = legendary.get("id")
        if not lid:
            continue
        text = " ".join([legendary.get("role") or ""] + (legendary.get("names") or []))
        pool.append((f"legendary: {lid}", text))
    for author in enc.get("characters", {}).get("real_world_authors_and_players", []):
        aid = author.get("id")
        if not aid:
            continue
        text = " ".join([author.get("role") or ""] + (author.get("names") or []))
        pool.append((f"author: {aid}", text))
    routes = enc.get("routes", {})
    for hw in routes.get("highways", []):
        code = hw.get("code")
        if not code:
            continue
        pool.append((f"highway: {code}", hw.get("name") or ""))
    for seg in routes.get("trains", {}).get("segments", []):
        name = seg.get("name")
        if not name:
            continue
        place = (seg.get("ends_at") or {}).get("place") or ""
        pool.append((f"train: {name}", place))
    for ap in routes.get("airports", []):
        loc = ap.get("location")
        if not loc:
            continue
        pool.append((f"airport: {loc}", ap.get("code") or ""))
    for r in routes.get("named_but_unplotted", []):
        name = r.get("name")
        if not name:
            continue
        pool.append((f"route: {name}", r.get("note") or ""))
    for era in enc.get("time_systems", {}).get("ensayo_i_eras", []):
        name = era.get("name")
        if not name:
            continue
        pool.append((f"era_ensayo: {name}", " ".join([era.get("notes") or "", era.get("artifact") or ""])))
    return pool


def draw_general_knowledge(enc: dict, criterion: dict, already_known: list, inherited_count: int) -> list:
    pool = [(tag, text) for tag, text in general_knowledge_pool(enc) if tag not in set(already_known)]
    if not pool:
        return []
    fraction = random.uniform(*GENERAL_KNOWLEDGE_FRACTION_RANGE)
    k = round(fraction * inherited_count)
    if k <= 0:
        return []
    keywords = set()
    for field in ("standard", "wasted_life", "trusts", "distrusts"):
        keywords |= extract_keywords(criterion.get(field, ""))
    tags = [tag for tag, _ in pool]
    weights = [1.0 + CRITERION_SKEW_WEIGHT * skew_score(keywords, text) for _, text in pool]
    return weighted_sample_without_replacement(tags, weights, k)


def normalize_experience_entry(entry):
    if isinstance(entry, dict):
        return entry.get("text", ""), entry.get("about")
    return str(entry), None


def draw_inherited_experience(parent_a_exp: list, parent_b_exp: list) -> list:
    combined = [normalize_experience_entry(e) for e in (parent_a_exp or []) + (parent_b_exp or [])]
    combined = list(dict.fromkeys(combined))  # de-duplicated by (text, about) pair
    if not combined:
        return []
    fraction = random.uniform(*PARENT_EXP_FRACTION_RANGE)
    k = round(fraction * len(combined))
    if k <= 0:
        return []
    chosen = random.sample(combined, min(k, len(combined)))
    result = []
    for text, about in chosen:
        wrapped = f"Grew up hearing: {text}"
        result.append({"text": wrapped, "about": about} if about else wrapped)
    return result


# --------------------------------------------------------------------------------------------
# Backstory + criterion: mechanical stand-ins for /character Step 2b/4, added 2026-08-17.
#
# A newborn's criterion used to be a straight field-by-field coin-flip copy from one parent
# (origin: "inherited"), and its backstory a hardcoded "Child of X and Y." - neither ever mutated,
# so a whole fast-cycling lineage inherited byte-identical criteria (see LAB_REPORT.md Run 4's open
# question on arc repetition at depth). A real /character Step 4 derivation is a judgment call
# (composing wasted_life/standard in the character's own words) and can't run here: it would have to
# be a subagent, but criterion is read SYNCHRONOUSLY by every later generation the moment they
# reproduce - deferring it to an end-of-run batch (the way arc/name authoring already is) would mean
# generations 2..N make reproduction/arc-gate decisions off whatever placeholder was on file at the
# time, which no later batch pass could retroactively fix. So this has to be mechanical, not authored,
# same constraint that already makes knowledge/routines dice-driven instead of hand-written.
#
# The approach: compose a real (if plain) backstory by splicing one of the child's own newly-drawn
# knowledge items into a template - this guarantees that item collides with the backstory by
# construction, giving Step 4a's collision-finding something real to work with instead of the empty
# "Child of X and Y." that made every child fall through to origin: "uncollided". Then run the actual
# Step 4a scan (word-overlap against backstory OR city, deliberately blind - no preference for a
# city-touching item over a backstory-only one, same discipline the hand-authored flow uses) across
# the child's FULL knowledge sample, pick a random item from whatever collides, and compose
# wasted_life/standard from a template keyed to that anchor's own text. trusts/distrusts still come
# from anchor_epistemology.py's real signal, exactly as Step 4d prescribes - that part was already
# fully mechanical and needed no change.
# --------------------------------------------------------------------------------------------

BACKSTORY_TEMPLATES = [
    "Child of {a} and {b}; grew up around {trade} in {city}, and knows something of {item}.",
    "Child of {a} and {b} in {city}; raised alongside {trade}, having heard about {item}.",
    "Child of {a} and {b}; raised in {city} on {trade}, and carries some knowledge of {item}.",
    "Child of {a} and {b}, in {city}; grew up around {trade}, and picked up a little of {item} along the way.",
]

# (wasted_life, standard) template pairs, each filled with the anchor's own (humanized) text.
CRITERION_TEMPLATES = [
    ("a life spent never once engaging with {a}", "counts a life well spent only if it stayed close to {a}"),
    ("forgetting what {a} actually meant, the way most people already have", "measures a life by whether {a} is still remembered rightly"),
    ("letting {a} slip past unexamined, the way it's easiest to", "counts it worthwhile only by paying real attention to {a}"),
    ("one that never had to answer for {a}", "holds themself accountable to {a}, whatever it costs"),
    ("treating {a} as someone else's concern", "counts a life well spent only by making {a} their own concern"),
]

# Fixed trusts/distrusts wording per provenance - the same table /character Step 4d hand-authors
# from; a script can't compose bespoke "own terms" phrasing, so this uses the table's own baseline
# wording verbatim rather than guess at a paraphrase. "conflict" is Step 4d's own fixed special case.
EPISTEMOLOGY_WORDING = {
    "material": ("what's written down and can be checked against the record", "a claim with no paper trail, however sincerely told"),
    "hearsay": ("a name attached to a story - someone who was there and can be asked", "the written record, as bloodless or secondhand"),
    "tale": ("a story that's been carried and retold and still holds together", "a record that insists on a precision no one who was actually there ever needed"),
    "conflict": ("verification", "anyone who sounds certain"),
}


def truncate_fragment(text: str, max_words: int = 8) -> str:
    """Bounds a spliced-in text fragment to a short, sentence-fragment-friendly length. Many
    encodings.json descriptions run to full paragraphs (a concept's whole write-up, a conflict's
    topic+detail, a routine's own routine_actions line) - read badly spliced in whole where a template
    expects a short noun/verb phrase. Takes the first clause up to '.'/';' when that's shorter, then
    hard-caps word count either way."""
    text = (text or "").strip()
    if not text:
        return text
    first_clause = re.split(r"[.;]", text, maxsplit=1)[0].strip()
    words = first_clause.split()
    if len(words) > max_words:
        return " ".join(words[:max_words]) + "..."
    return first_clause


def humanize_tag(tag: str) -> str:
    """Turns a bare 'category: id' tag into a short, phrase-shaped display label - strips the
    category prefix, drops a trailing hearsay claim number ('#3'), and de-snake-cases a machine id
    ('la_lagrima_de_balahm' -> 'La Lagrima De Balahm', same trick register_arc_concept.py's own
    humanize() uses). Deliberately never touches an item's own long-form description text (that's
    what `pool_text` is for, and it's full-sentence-shaped, not phrase-shaped - splicing it into a
    template built around a noun phrase produces broken grammar, confirmed the hard way testing this
    against real data) - a tag id, however plain, is at least reliably phrase-shaped."""
    _, _, rest = tag.partition(": ")
    rest = rest or tag
    rest = re.sub(r"#\d+$", "", rest).strip()
    if "_" in rest and " " not in rest:
        rest = " ".join(w.capitalize() for w in rest.split("_"))
    elif rest.islower():
        rest = rest.capitalize()
    return rest


def find_collision_items(items: list, backstory: str, city: str, pool_text: dict) -> list:
    """/character Step 4a, mechanically: every item (by tag) whose own text touches the backstory OR
    the city - deliberately OR, not AND, and deliberately blind (no preference for a city-touching
    item over a backstory-only one) - see the module-level note above for why. `pool_text` maps a
    tag to its own real description where one exists (general_knowledge_pool()'s own lookup); a tag
    with no entry there falls back to matching against its own bare 'category: id' string, same
    fallback simulate_pass_lib.py's peer_knowledge_items() already uses for the arc-alignment gate."""
    target_words = extract_keywords(backstory) | extract_keywords(city)
    if not target_words:
        return []
    return [tag for tag in items if extract_keywords(pool_text.get(tag, tag)) & target_words]


def compose_backstory(name_a: str, name_b: str, city: str, routines: list, seed_text: str | None) -> str:
    trade = truncate_fragment(routines[0]["routine_actions"]) if routines else "no particular trade"
    if not seed_text:
        return f"Child of {name_a} and {name_b}."
    template = random.choice(BACKSTORY_TEMPLATES)
    return template.format(a=name_a, b=name_b, city=city or "an unrecorded city", trade=trade, item=seed_text)


def derive_criterion_mechanical(items: list, backstory: str, city: str, pool_text: dict, world_enc: dict) -> dict:
    base = {"tempered": 0, "cost_ledger": [], "history": []}
    collision_pool = find_collision_items(items, backstory, city, pool_text)
    if not collision_pool:
        return {**base, "standard": "", "wasted_life": "", "anchor": "", "origin": "uncollided", "trusts": "", "distrusts": ""}

    anchor = random.choice(collision_pool)
    anchor_text = truncate_fragment(humanize_tag(anchor))
    wasted_life_t, standard_t = random.choice(CRITERION_TEMPLATES)

    epi = ae.resolve_epistemology(anchor, world_enc)
    trusts, distrusts = EPISTEMOLOGY_WORDING.get(epi["epistemology"], ("", ""))

    return {
        **base,
        "standard": standard_t.format(a=anchor_text),
        "wasted_life": wasted_life_t.format(a=anchor_text),
        "anchor": anchor,
        "origin": "derived",
        "trusts": trusts,
        "distrusts": distrusts,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--parent-a", required=True)
    parser.add_argument("--parent-b", required=True)
    parser.add_argument("--name", required=True, help="Model-composed name blend - the one judgment call this script doesn't make")
    parser.add_argument("--pass-number", type=int, required=True, help="Current /simulate pass number, recorded as birth_pass and on both parents as last_reproduced_pass")
    parser.add_argument("--seed", type=int, default=None, help="Also seeds the circle-notification sample")
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    a_key, b_key = args.parent_a.lower(), args.parent_b.lower()
    parent_a, parent_b = load_char(a_key), load_char(b_key)
    key = slugify(args.name)
    base_key, n = key, 2
    while (CHAR_DIR / f"{key}.json").exists():
        key = f"{base_key}_{n}"
        n += 1

    name_a, name_b = parent_a.get("name", a_key), parent_b.get("name", b_key)
    city = coin(parent_a.get("city", ""), parent_b.get("city", ""))

    # Internal-only coin-flip criterion, used SOLELY to skew the general-knowledge draw below toward
    # roughly what this child would have leaned toward if criteria were still inherited - never
    # persisted as the child's own criterion (see derive_criterion_mechanical() below for that).
    crit_a = parent_a.get("criterion", {})
    crit_b = parent_b.get("criterion", {})
    skew_criterion = {
        "standard": coin(crit_a.get("standard", ""), crit_b.get("standard", "")),
        "wasted_life": coin(crit_a.get("wasted_life", ""), crit_b.get("wasted_life", "")),
        "trusts": coin(crit_a.get("trusts", ""), crit_b.get("trusts", "")),
        "distrusts": coin(crit_a.get("distrusts", ""), crit_b.get("distrusts", "")),
    }

    edu_a = parent_a.get("knowledge", {}).get("education", {})
    edu_b = parent_b.get("knowledge", {}).get("education", {})
    edu_source = coin(edu_a, edu_b)
    inherited_items = sample_union(edu_a.get("items", []), edu_b.get("items", []), min_fraction=PARENT_EDU_MIN_FRACTION)
    world_enc = load_encodings()
    general_items = draw_general_knowledge(world_enc, skew_criterion, inherited_items, len(inherited_items))
    items = inherited_items + general_items
    pool_text = dict(general_knowledge_pool(world_enc))

    inherited_experience = draw_inherited_experience(
        parent_a.get("knowledge", {}).get("experience", []),
        parent_b.get("knowledge", {}).get("experience", []),
    )

    routines_pool_a = parent_a.get("routines", [])
    routines_pool_b = parent_b.get("routines", [])
    routines = sample_union(
        [json.dumps(r, sort_keys=True) for r in routines_pool_a],
        [json.dumps(r, sort_keys=True) for r in routines_pool_b],
    )
    routines = [json.loads(r) for r in routines]
    if routines:
        equal_weight = round(100 / len(routines), 2)
        for r in routines:
            r["weight"] = equal_weight

    # Backstory seeded from one of the child's own newly-drawn items (prefer general_items - the
    # genuinely NEW draw, so the backstory reflects something distinctly theirs, not just recycled
    # parent material - falling back to inherited_items only if the new draw came back empty).
    seed_pool = general_items or inherited_items
    seed_tag = random.choice(seed_pool) if seed_pool else None
    seed_text = truncate_fragment(humanize_tag(seed_tag)) if seed_tag else None
    backstory = compose_backstory(name_a, name_b, city, routines, seed_text)

    criterion = derive_criterion_mechanical(items, backstory, city, pool_text, world_enc)

    span = random.randint(SPAN_MIN, SPAN_MAX)

    child = {
        "name": args.name,
        "city": city,
        "backstory": backstory,
        "knowledge": {
            "education": {
                "percent": edu_source.get("percent"),
                "mode": edu_source.get("mode"),
                "topic": edu_source.get("topic"),
                "items": items,
            },
            "experience": inherited_experience,
        },
        "criterion": criterion,
        "life": {"lived": 0, "deceased": False},
        "routines": routines,
        "parents": [a_key, b_key],
        "birth_pass": args.pass_number,
    }
    save_char(key, child)
    tale_id = write_birth_tale(key, args.name, [name_a, name_b])

    with open(LIFESPANS_PATH, encoding="utf-8") as f:
        lifespans_doc = json.load(f)
    lifespans_doc["lifespans"][key] = {"span": span, "range": f"{SPAN_MIN}-{SPAN_MAX}"}
    with open(LIFESPANS_PATH, "w", encoding="utf-8") as f:
        json.dump(lifespans_doc, f, indent=2, ensure_ascii=False)
        f.write("\n")

    # Parents: not circle members, the event itself - always notified, no sampling.
    for parent_key, parent_char, other_name in ((a_key, parent_a, name_b), (b_key, parent_b, name_a)):
        parent_char["last_reproduced_pass"] = args.pass_number
        parent_char.setdefault("knowledge", {}).setdefault("experience", [])
        parent_char["knowledge"]["experience"].append(f"Had a child with {other_name}, named {args.name}.")
        save_char(parent_key, parent_char)

    # Circle: reuse notify_death.py's own logic, unioned across both parents. Excludes the new child's
    # own key throughout - fixed 2026-08-10 (Run 2's seventh extension): previously only the two
    # parent keys were excluded, so a newborn's own backstory ("Child of X and Y.") matched the
    # parent-name backstory check against itself and the newborn ended up in its own notified sample.
    exclude = {a_key, b_key, key}
    characters, enc = notify_death.load()
    entries = enc["hearsay"]["entries"]
    name_to_key = notify_death.name_to_key_map(characters)

    relations = notify_death.compute_relations([a_key, b_key], characters) - exclude

    extended_keys = set()
    for parent_name in (name_a, name_b):
        for _scene_id, others in notify_death.scene_participants_of(parent_name, entries):
            for other_name in others:
                k = name_to_key.get(notify_death.normalize(other_name))
                if k and k not in exclude:
                    extended_keys.add(k)
    for other_key, other_char in characters.items():
        if other_key in exclude:
            continue
        backstory = notify_death.normalize(other_char.get("backstory") or "")
        if notify_death.normalize(name_a) in backstory or notify_death.normalize(name_b) in backstory:
            extended_keys.add(other_key)
    extended_keys = notify_death.living_only(extended_keys, characters) - relations

    extended = sorted(extended_keys)
    n_notify = 0 if not extended else max(1, round(0.30 * len(extended)))
    from random import Random
    rng = Random(args.seed)
    sampled = sorted(rng.sample(extended, n_notify)) if n_notify else []
    notified = sorted(relations) + sampled

    for k in notified:
        notified_char = load_char(k)
        notified_char.setdefault("knowledge", {}).setdefault("experience", [])
        notified_char["knowledge"]["experience"].append(
            f"Heard that {name_a} and {name_b} now have a child, {args.name}."
        )
        save_char(k, notified_char)

    print(f"born: {key} ({args.name})")
    print(f"tale written: _lore/tales/{tale_id}.md  (id: {tale_id}) - tag the birth-announcement hearsay claim 'about: \"tale: {tale_id}\"', not a made-up concept")
    print(f"parents: {a_key}, {b_key}  (last_reproduced_pass = {args.pass_number} on both, both notified directly)")
    print(f"relations (guaranteed): {len(relations)}  |  extended circle: {len(extended)} -> sampled {len(sampled)} (30%)  |  total notified: {len(notified)}")
    for k in notified:
        tag = "  [relation]" if k in relations else ""
        print(f"  notified: {k}{tag}")
    if extended and not sampled:
        print("  (extended circle non-empty but sample came back empty - shouldn't happen, check n_notify logic)")
    print(f"knowledge.education.items: {len(items)} total  ({len(inherited_items)} from parents, {len(general_items)} new from encodings.json's world-lore pools)")
    print(f"knowledge.experience: {len(inherited_experience)} inherited as family lore (wrapped 'Grew up hearing: ...', not lived firsthand)")
    print(f"routines: {len(routines)} inherited")
    print("life.span: rolled fresh, written to lifespans.json - never into the child's own file")
    print(f"pool-eligible (pick_pair.py) once current pass number >= {args.pass_number + CHILD_COOLDOWN_PASSES}"
          f"  (child_cooldown_passes={CHILD_COOLDOWN_PASSES}, from _lore/tuning.json)")


if __name__ == "__main__":
    main()

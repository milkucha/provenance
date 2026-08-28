#!/usr/bin/env python3
"""Build the Provenance graph views and render them into a standalone HTML page.

Three graphs come out of one run:

  lore       the knowledge graph  - NPCs, dialogues, locations, concepts, characters,
             conflicts, routes, eras, tales and facts, wired by who lives
             where, who says what, who knows what, and what disputes what.
  structure  the repo as it is on disk - directories and files, sized by bytes and
             coloured by what kind of thing they are.
  concept    the four-layer architecture from README section 0, with live counts.

Everything is read from the repo's own sources of truth, so the page stays true as the
world grows. Nothing is hand-maintained here except the concept graph's shape.

    python scripts/graphs/graphifyish.py            # writes graphs/graphifyish/graphifyish.html
    python scripts/graphs/graphifyish.py --json     # also dump graphs/graphifyish/graph.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
ENCODINGS = ROOT / "_lore" / "encodings.json"
NPCS = ROOT / "_npcs" / "npcs" / "registry.json"
CHAR_DIR = ROOT / "_lore" / "characters"
DIALOGS = ROOT / "_npcs" / "dialogs" / "registry.json"
ACTIONS = ROOT / "_npcs" / "actions" / "registry.json"
FACTS = ROOT / "_lore" / "facts" / "facts.json"
AUTHORS = ROOT / "_lore" / "tales" / "_authors.md"
DIALOGUE_DIR = ROOT / "data" / "luminacion" / "blabber" / "dialogues"
OUT_DIR = ROOT / "graphs" / "graphifyish"

# Directories that are never part of the picture. "worktrees" excludes .claude/worktrees/ -
# each entry there is a full `git worktree add` checkout, so walking into them would duplicate
# the entire repo's structure once per live/stale worktree.
SKIP_DIRS = {".git", ".venv", "__pycache__", "node_modules", ".idea", ".vscode", "worktrees"}


def load(path: Path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def load_authors_table(path: Path) -> dict:
    """Parse _authors.md's '| Id | Responsible | Recorded |' table into {id: {responsible, recorded}}."""
    if not path.exists():
        return {}
    result = {}
    row = re.compile(r"^\|\s*`?([^`|]+?)`?\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*$")
    for line in path.read_text(encoding="utf-8").splitlines():
        m = row.match(line)
        if m and m.group(1) not in ("Id", "---"):
            result[m.group(1)] = {"responsible": m.group(2), "recorded_date": m.group(3)}
    return result


def load_characters() -> dict:
    """Every character file under _lore/characters/ - the full lore-side cast, keyed by slug,
    since a character can exist here fully developed with no Minecraft entry at all."""
    return {
        p.stem: load(p) for p in CHAR_DIR.glob("*.json") if p.stem not in ("_template", "lifespans")
    }


def norm(text: str) -> str:
    """Fold accents and punctuation so 'Görff' and 'Gorff' compare equal."""
    stripped = unicodedata.normalize("NFKD", text)
    stripped = "".join(c for c in stripped if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "", stripped.lower())


class Graph:
    """Node/edge accumulator that refuses to invent endpoints."""

    def __init__(self, name: str):
        self.name = name
        self.nodes: dict[str, dict] = {}
        self.edges: list[dict] = []
        self._seen: set[tuple] = set()
        self.dropped: Counter = Counter()

    def node(self, nid: str, label: str, kind: str, **meta) -> str:
        if nid not in self.nodes:
            self.nodes[nid] = {"id": nid, "label": label, "kind": kind, **meta}
        else:  # later calls may enrich an earlier stub
            self.nodes[nid].update({k: v for k, v in meta.items() if v not in (None, "", [])})
        return nid

    def edge(self, src: str, dst: str, rel: str, **meta) -> None:
        if src == dst:
            return
        if src not in self.nodes or dst not in self.nodes:
            self.dropped[rel] += 1
            return
        key = (src, dst, rel)
        if key in self._seen:
            for e in self.edges:
                if (e["source"], e["target"], e["rel"]) == key:
                    e["weight"] = e.get("weight", 1) + 1
                    break
            return
        self._seen.add(key)
        self.edges.append({"source": src, "target": dst, "rel": rel, "weight": 1, **meta})

    def dump(self) -> dict:
        deg: Counter = Counter()
        for e in self.edges:
            deg[e["source"]] += 1
            deg[e["target"]] += 1
        for nid, n in self.nodes.items():
            n["degree"] = deg[nid]
        return {"name": self.name, "nodes": list(self.nodes.values()), "edges": self.edges}


# --------------------------------------------------------------------------------------
# Lore graph
# --------------------------------------------------------------------------------------

def build_lore() -> tuple[Graph, dict]:
    enc = load(ENCODINGS)
    npcs = load(NPCS)["npcs"]  # Minecraft-side only now: skin, taterzen_uuid, taterzen_name, spawn_position
    characters = load_characters()  # lore-side: name, city, backstory, knowledge, criterion, life,
                                     # parents - the full character universe, since a character can
                                     # exist here with no Minecraft entry at all (never embodied)
    dialog_reg = load(DIALOGS)["npcs"]
    g = Graph("lore")

    # --- places -----------------------------------------------------------------------
    name_to_loc: dict[str, str] = {}
    for loc in enc["locations"]:
        nid = g.node(
            f"loc:{loc['id']}",
            loc["names"][0] if loc.get("names") else loc["id"],
            "location",
            region=loc.get("region"),
            type=loc.get("type_catastro"),
            condition=loc.get("condition_catastro"),
            coords=(loc.get("coords") or [None])[0],
            sources=loc.get("sources", []),
            notes=loc.get("notes", ""),
            file="_lore/encodings.json#locations",
        )
        for name in loc.get("names", []):
            name_to_loc.setdefault(norm(name), nid)
        name_to_loc.setdefault(norm(loc["id"]), nid)

    # --- concepts ---------------------------------------------------------------------
    name_to_concept: dict[str, str] = {}
    for c in enc["concepts"]:
        nid = g.node(
            f"con:{c['id']}", c["names"][0] if c.get("names") else c["id"], "concept",
            description=c.get("description", ""), sources=c.get("sources", []),
            file="_lore/encodings.json#concepts",
        )
        for name in c.get("names", []):
            name_to_concept.setdefault(norm(name), nid)
        name_to_concept.setdefault(norm(c["id"]), nid)

    # --- characters -------------------------------------------------------------------
    for c in enc["characters"]["in_world_or_legendary"]:
        g.node(f"chr:{c['id']}", c["names"][0], "character", role=c.get("role", ""),
               sources=c.get("sources", []), notes=c.get("notes", ""), legendary=True,
               file="_lore/encodings.json#characters.in_world_or_legendary")
    for c in enc["characters"]["real_world_authors_and_players"]:
        g.node(f"chr:{c['id']}", c["names"][0], "author", role=c.get("role", ""),
               sources=c.get("sources", []),
               file="_lore/encodings.json#characters.real_world_authors_and_players")

    # --- census of named inhabitants ---------------------------------------------------
    inhabitant_index: dict[str, str] = {}
    for locality, people in enc["characters"]["named_inhabitants"]["by_locality"].items():
        if not isinstance(people, list):
            continue
        for person in people:
            # most entries are {name, role}; the "skin only" locality lists bare names
            if isinstance(person, str):
                person = {"name": person}
            elif not isinstance(person, dict):
                continue
            # crowd instances are a role played by several people, with no name of their own
            name = person.get("name") or person.get("role")
            if not name:
                continue
            nid = g.node(f"inh:{locality}/{name}", name, "inhabitant",
                         role=person.get("role", ""), locality=locality,
                         count=person.get("count"), notes=person.get("note", ""),
                         file="_lore/encodings.json#characters.named_inhabitants")
            inhabitant_index[f"{norm(name)}|{norm(locality)}"] = nid
            inhabitant_index.setdefault(norm(name), nid)
            inhabitant_index.setdefault(norm("the " + name), nid)
            inhabitant_index.setdefault(f"{norm('the ' + name)}|{norm(locality)}", nid)
            home = name_to_loc.get(norm(locality))
            if home:
                g.edge(nid, home, "census")

    # --- conflicts ---------------------------------------------------------------------
    for c in enc["conflicts"]:
        g.node(f"cfl:{c['id']}", c["id"], "conflict", topic=c.get("topic", ""),
               detail=c.get("detail", ""), resolution=c.get("user_resolution", ""),
               resolved=bool(c.get("user_resolution")),
               file="_lore/encodings.json#conflicts")
    # a location whose notes cite a conflict is a party to it
    for loc in enc["locations"]:
        for ref in re.findall(r"CONFLICT-\d+", loc.get("notes", "") or ""):
            g.edge(f"loc:{loc['id']}", f"cfl:{ref}", "disputed_by")

    # --- eras and time systems ----------------------------------------------------------
    # each chronicle stores its era list at a different depth
    ts = enc["time_systems"]
    era_lists = (
        ("ensayo", ts.get("ensayo_i_eras") or [], "ensayo_i_eras"),
        ("libro", (ts.get("libro_venidas_eras") or {}).get("list") or [],
         "libro_venidas_eras.list"),
        ("esquema", (ts.get("esquema_poster_eras") or {}).get("era_row") or [],
         "esquema_poster_eras.era_row"),
    )
    for kind, entries, where in era_lists:
        for era in entries:
            if not isinstance(era, dict):
                continue
            label = era.get("name") or era.get("era") or str(era.get("n", "?"))
            g.node(f"era:{kind}/{label}", label, "era", system=kind,
                   span=era.get("range_real") or era.get("range_vortex") or "",
                   notes=era.get("notes") or era.get("note") or era.get("matches") or "",
                   file=f"_lore/encodings.json#time_systems.{where}")

    # a founding year is a node too, tied to the places founded in it
    for row in (ts.get("esquema_poster_eras") or {}).get("year_by_year_foundations", []) or []:
        if not isinstance(row, dict) or row.get("year") is None:
            continue
        nid = g.node(f"year:{row['year']}", str(row["year"]), "year",
                     span=row.get("range_as_extracted", ""),
                     file="_lore/encodings.json"
                          "#time_systems.esquema_poster_eras.year_by_year_foundations")
        for place in row.get("places", []) or []:
            dest = name_to_loc.get(norm(place))
            if dest:
                g.edge(nid, dest, "founds")

    # --- routes ---------------------------------------------------------------------------
    # keyed by folded name, since NPC sheets spell accents inconsistently
    route_index: dict[str, str] = {}
    routes = enc["routes"]
    for hw in routes.get("highways", []) or []:
        nid = g.node(f"rte:hw/{hw['code']}", hw["code"], "route", mode="highway",
                     name=hw.get("name", ""), distance=hw.get("total_distance"),
                     file="_lore/encodings.json#routes.highways")
        # "Ruta Puente Intercontinental - Nvhi" -> endpoints by name
        route_index[f"highway|{norm(hw['code'])}"] = nid
        # "Ruta Puente Intercontinental - Nvhi" -> endpoints by name
        for part in re.split(r"\s+-\s+", re.sub(r"^Ruta\s+", "", hw.get("name", ""))):
            dest = name_to_loc.get(norm(part))
            if dest:
                g.edge(nid, dest, "connects")
    for seg in routes.get("trains", {}).get("segments", []) or []:
        nid = g.node(f"rte:tr/{seg['name']}", seg["name"], "route", mode="train",
                     distance=seg.get("total_distance"),
                     file="_lore/encodings.json#routes.trains")
        route_index[f"train_segment|{norm(seg['name'])}"] = nid
        for part in re.split(r"\s+-\s+", seg["name"]):
            dest = name_to_loc.get(norm(part))
            if dest:
                g.edge(nid, dest, "connects")
            # sheets cite a segment by either endpoint alone ("train_segment: Khan Ice")
            route_index.setdefault(f"train_segment|{norm(part)}", nid)
    for air in routes.get("airports", []) or []:
        nid = g.node(f"rte:air/{air['location']}", f"{air['location']} ({air.get('code','')})",
                     "route", mode="airport", code=air.get("code", ""), coords=air.get("coords"),
                     file="_lore/encodings.json#routes.airports")
        route_index[f"airport|{norm(air['location'])}"] = nid
        route_index[f"airport|{norm(air.get('code', ''))}"] = nid
        dest = name_to_loc.get(norm(air["location"]))
        if dest:
            g.edge(nid, dest, "connects")
    for named in routes.get("named_but_unplotted", []) or []:
        nid = g.node(f"rte:named/{named['name']}", named["name"], "route", mode="unplotted",
                     notes=named.get("note", ""),
                     file="_lore/encodings.json#routes.named_but_unplotted")
        route_index[f"route_named|{norm(named['name'])}"] = nid

    # --- dialogues, and the claims they make -------------------------------------------
    hearsay = {h["id"]: h for h in enc["hearsay"]["entries"]}
    dialogue_files = sorted(p for p in DIALOGUE_DIR.glob("*.json")
                            if not p.name.startswith("_template"))
    for path in dialogue_files:
        did = path.stem
        blabber = load(path)
        states = blabber.get("states", {})
        entry = hearsay.get(did)
        nid = g.node(
            f"dlg:{did}", did.replace("_", " "), "dialogue",
            states=len(states),
            choices=sum(len(s.get("choices", []) or []) for s in states.values()),
            has_hearsay=entry is not None,
            summary=(entry or {}).get("summary", ""),
            participants=(entry or {}).get("participants", []),
            claims=len((entry or {}).get("claims", []) or []),
            file=f"data/luminacion/blabber/dialogues/{path.name}",
        )
        if not entry:
            continue
        set_in = (entry.get("location") or {}).get("id")
        if set_in:
            g.edge(nid, f"loc:{set_in}", "set_in")
        for claim in entry.get("claims", []) or []:
            about = claim.get("about")
            if not about:
                continue
            for target in (f"loc:{about}", f"con:{about}", f"chr:{about}", f"cfl:{about}"):
                if target in g.nodes:
                    g.edge(nid, target, "claims_about",
                           inconsistent=bool(claim.get("inconsistent_with_record"))
                           or bool(claim.get("inconsistent_with_facts")))
                    break

    # --- NPCs ----------------------------------------------------------------------------
    prefix_map = {
        "location": lambda v: f"loc:{v}",
        "concept": lambda v: f"con:{v}",
        "conflict": lambda v: f"cfl:{v}",
        "character_legendary": lambda v: f"chr:{v}",
        "character_real": lambda v: f"chr:{v}",
        "airport": lambda v: route_index.get(f"airport|{norm(v)}", ""),
        "highway": lambda v: route_index.get(f"highway|{norm(v)}", ""),
        "train_segment": lambda v: route_index.get(f"train_segment|{norm(v)}", ""),
        "route_named": lambda v: route_index.get(f"route_named|{norm(v)}", ""),
        "era_ensayo": lambda v: f"era:ensayo/{v}",
        "era_libro": lambda v: f"era:libro/{v}",
        "era_esquema": lambda v: f"era:esquema/{v}",
        "year_esquema": lambda v: f"year:{v}",
    }
    unmatched: Counter = Counter()

    # letter-multiset index, to catch spelling variants the names lists don't carry
    # ("Balehm" for "Balhem"). Only used when the fold is unambiguous.
    anagram: dict[str, set[str]] = defaultdict(set)
    for key_norm, nid in name_to_loc.items():
        anagram["".join(sorted(key_norm))].add(nid)

    def resolve_place(raw: str) -> str | None:
        """Map a written place name onto a location or concept node."""
        for candidate in (raw, re.sub(r"\s*\(.*?\)\s*", " ", raw).strip()):
            n = norm(candidate)
            if not n:
                continue
            hit = name_to_loc.get(n) or name_to_concept.get(n)
            if hit:
                return hit
            # "Görff (Volcano)" is written "Volcano-Gorff" in the census
            for locality in enc["characters"]["named_inhabitants"]["by_locality"]:
                if norm(locality) == n or set(norm(locality).split()) == {n}:
                    lh = name_to_loc.get(norm(locality))
                    if lh:
                        return lh
            fold = anagram.get("".join(sorted(n)))
            if fold and len(fold) == 1:
                return next(iter(fold))
        return None

    for key, character in characters.items():
        npc = npcs.get(key, {})  # Minecraft entry - may not exist if never embodied
        edu = (character.get("knowledge", {}) or {}).get("education", {}) or {}
        items = edu.get("items") or []
        experience = (character.get("knowledge", {}) or {}).get("experience") or []
        criterion = character.get("criterion") or {}
        life = character.get("life") or {}
        developed = bool(character.get("backstory")) or edu.get("percent") is not None
        nid = g.node(
            f"npc:{key}", character.get("name") or key, "npc",
            city=character.get("city", ""), skin=bool(npc.get("skin")),
            uuid=bool(npc.get("taterzen_uuid")), backstory=character.get("backstory", ""),
            education=edu.get("percent"), mode=edu.get("mode", ""),
            known=len(items), experience=experience, developed=developed,
            criterion=criterion.get("standard", ""), lifespan=life.get("span"),
            embodied=bool(npc), file="_lore/characters/",
        )

        # where they live - the city field is a comma-separated list of place names
        for place in [p.strip() for p in (character.get("city") or "").split(",") if p.strip()]:
            target = resolve_place(place)
            if target:
                g.edge(nid, target, "lives_in")
            else:
                # a place the catastro doesn't list - show it rather than drop it
                unmatched[place] += 1
                g.edge(nid, g.node(f"place:{norm(place)}", place, "place",
                                   note="named as a home, but not in the locations record"),
                       "lives_in")

        # the census entry this NPC was drawn from
        twin = inhabitant_index.get(norm(character.get("name") or key))
        if twin:
            g.edge(nid, twin, "is")

        # what they know
        for item in items:
            prefix, _, value = item.partition(":")
            value = value.strip()
            if prefix == "hearsay":
                g.edge(nid, f"dlg:{value.split('#')[0]}", "knows")
            elif prefix == "inhabitant":
                m = re.match(r"^(.*?)\s*\((.*)\)$", value)
                if m:
                    who, where = m.group(1).strip(), m.group(2).strip()
                    target = (inhabitant_index.get(f"{norm(who)}|{norm(where)}")
                              or inhabitant_index.get(norm(who)))
                    if target:
                        g.edge(nid, target, "knows")
                    else:
                        unmatched[item] += 1
            elif prefix in prefix_map:
                target = prefix_map[prefix](value)
                if target in g.nodes:
                    g.edge(nid, target, "knows")
                else:
                    unmatched[item] += 1
            else:
                unmatched[item] += 1

    # who speaks what
    for key, rec in dialog_reg.items():
        if key.startswith("_"):
            continue
        for d in rec.get("dialogs", []) or []:
            g.edge(f"npc:{key}", f"dlg:{d['id'].split(':')[-1]}", "speaks",
                   trigger=d.get("trigger", ""), description=d.get("description", ""))

    # --- tales and facts ------------------------------------------------------------------
    def wire_touches(nid: str, touches: list[str]) -> None:
        for ref in touches or []:
            head, _, tail = ref.partition(".")
            target = None
            if head == "concepts":
                target = f"con:{tail}"
            elif head == "locations":
                target = f"loc:{tail}"
            elif head == "characters":
                # by_locality.<Locality> (<Role>, <Name>) for a named person, but crowd
                # instances have no name, so the third field is their locality instead
                m = re.search(r"by_locality\.(.+?)\s*\((.*?),\s*(.*?)\)\s*$", tail)
                if m:
                    locality, role, who = m.group(1), m.group(2), m.group(3)
                    target = (inhabitant_index.get(f"{norm(who)}|{norm(locality)}")
                              or inhabitant_index.get(f"{norm(role)}|{norm(locality)}")
                              or inhabitant_index.get(norm(who)))
                else:
                    target = f"chr:{tail.split('.')[-1]}"
            if target and target in g.nodes:
                g.edge(nid, target, "touches")
            else:
                unmatched[ref] += 1

    provenance = load_authors_table(AUTHORS)

    for t in enc.get("tales", {}).get("entries", []) or []:
        nid = g.node(f"tale:{t['id']}", t["id"].replace("_", " "), "tale",
                     summary=t.get("summary", ""), told=t.get("told_date", ""),
                     told_by=t.get("told_by") or "",
                     responsible=provenance.get(t["id"], {}).get("responsible", ""),
                     file=t.get("source_file", ""))
        wire_touches(nid, t.get("touches", []))
    if FACTS.exists():
        facts = load(FACTS)
        entries = facts.get("facts") or facts.get("entries") or []
        if isinstance(entries, dict):
            entries = list(entries.values())
        for f in entries:
            if not isinstance(f, dict):
                continue
            fid = f.get("id") or f.get("name") or "fact"
            g.node(f"fact:{fid}", str(fid).replace("_", " "), "fact",
                   summary=f.get("summary") or f.get("statement") or "",
                   file="_lore/facts/facts.json")

    stats = {
        "unmatched": unmatched.most_common(15),
        "unmatched_total": sum(unmatched.values()),
        "dropped_edges": dict(g.dropped),
    }
    return g, stats


# --------------------------------------------------------------------------------------
# Family graph - who's descended from whom, coloured by inherited criterion
# --------------------------------------------------------------------------------------
#
# generate_offspring.py coin-flips each of a child's five criterion fields independently to
# one parent's exact value, but never records which parent won which flip - only the result
# survives, in the child's own file. inheritance_fraction() reconstructs it after the fact by
# comparing the child's value for each field against both parents' own values.
#
# Colour comes from the same fraction, mixed the way paint mixes rather than the way light
# mixes: an RGB average of yellow and blue is a flat grey, but the artist's RYB wheel used
# here (red/yellow/blue primaries, trilinearly interpolated across a cube whose corners are
# the eight named pigment mixes - Gossett & Chen's 2004 model) puts yellow and blue next to
# each other on the same edge, so splitting the difference lands on green, matching what
# mixing two actual paints would do. Founders (no recorded `parents`) sit on the outer edge
# of that wheel at a hue derived from their own key, spaced apart from already-assigned
# founders so a small cast stays readable. Every child's colour is a literal barycentric mix
# of both parents' own colours at the inheritance fraction above - descendants of the same
# founder drift toward each other's hue instead of being independently reassigned each
# generation, so the blend is genuinely genealogical, not just a fresh colour per node.

CRITERION_FIELDS = ("standard", "wasted_life", "anchor", "trusts", "distrusts")

# the cube's 8 named corners: how much of each gets painted when red/yellow/blue pigment is
# either fully present (1) or fully absent (0) - opposite corners are white (no pigment) and
# a near-black (all three at once, the way real pigments do darken when mixed together)
RYB_CUBE = {
    (0, 0, 0): (1.000, 1.000, 1.000),  # white
    (1, 0, 0): (1.000, 0.000, 0.000),  # red
    (0, 1, 0): (1.000, 1.000, 0.000),  # yellow
    (0, 0, 1): (0.163, 0.373, 0.600),  # blue
    (1, 1, 0): (1.000, 0.500, 0.000),  # orange
    (1, 0, 1): (0.500, 0.000, 0.500),  # violet
    (0, 1, 1): (0.000, 0.660, 0.200),  # green
    (1, 1, 1): (0.200, 0.094, 0.000),  # near-black
}


def stable_hue(key: str) -> float:
    """A deterministic 0-359.9 hue for a key, stable across regenerations (no random.seed
    juggling needed) - the post-commit hook re-runs this on every commit, so a founder's
    colour must not jitter just because the cast grew."""
    h = int(hashlib.sha1(key.encode("utf-8")).hexdigest()[:8], 16)
    return (h % 3600) / 10.0


def assign_founder_hues(founder_keys: list) -> dict:
    """Spreads founders around the RYB wheel, nudging a hue away from an already-assigned one
    that lands within 24 degrees of it - processed in sorted-key order so results are stable
    regardless of dict iteration order, and so adding a new founder later never reshuffles an
    existing one's colour."""
    assigned: list = []
    hues: dict = {}
    for key in sorted(founder_keys):
        hue = stable_hue(key)
        tries = 0
        while tries < 15 and any(min(abs(hue - h), 360 - abs(hue - h)) < 24 for h in assigned):
            hue = (hue + 41.0) % 360  # deterministic nudge; 41 keeps the walk from cycling short
            tries += 1
        assigned.append(hue)
        hues[key] = hue
    return hues


def hue_to_ryb(hue: float) -> tuple:
    """A point on the wheel's outer edge (red->yellow->green->blue->violet->red), the fully-
    saturated pigment colours with no white or black mixed in."""
    hue %= 360
    if hue < 120:
        t = hue / 120
        return (1 - t, t, 0.0)
    elif hue < 240:
        t = (hue - 120) / 120
        return (0.0, 1 - t, t)
    else:
        t = (hue - 240) / 120
        return (t, 0.0, 1 - t)


def ryb_to_rgb(r: float, y: float, b: float) -> tuple:
    out = [0.0, 0.0, 0.0]
    for (br, by, bb), c in RYB_CUBE.items():
        w = (r if br else 1 - r) * (y if by else 1 - y) * (b if bb else 1 - b)
        for i in range(3):
            out[i] += w * c[i]
    return tuple(out)


def rgb_to_hex(rgb: tuple, lighten: float = 0.10) -> str:
    # a touch of white keeps deep multi-generation mixes from reading as mud on a dark background
    r, g, b = (min(1.0, max(0.0, c * (1 - lighten) + lighten)) for c in rgb)
    return "#{:02x}{:02x}{:02x}".format(round(r * 255), round(g * 255), round(b * 255))


def inheritance_fraction(child: dict, parent_a: dict, parent_b: dict) -> float:
    """Fraction of the child's criterion attributable to parent A, reconstructed field-by-field
    (see the module comment above for why this can't just be read off the record directly)."""
    crit = child.get("criterion") or {}
    a_crit = parent_a.get("criterion") or {}
    b_crit = parent_b.get("criterion") or {}
    total = 0.0
    for field in CRITERION_FIELDS:
        val = crit.get(field)
        a_match, b_match = val == a_crit.get(field), val == b_crit.get(field)
        if a_match and not b_match:
            total += 1.0
        elif b_match and not a_match:
            total += 0.0
        else:  # tie (both parents share the value) or neither matches - split the difference
            total += 0.5
    return total / len(CRITERION_FIELDS)


def build_family() -> Graph:
    characters = load_characters()
    g = Graph("family")

    founder_keys = [k for k, c in characters.items() if not c.get("parents")]
    hues = assign_founder_hues(founder_keys)

    effective_ryb: dict = {}
    generation: dict = {}

    def resolve(key: str, stack: frozenset = frozenset()) -> tuple:
        if key in effective_ryb:
            return effective_ryb[key]
        char = characters.get(key)
        parents = (char or {}).get("parents") or []
        # a founder, an unresolvable reference, or a cycle all fall back to the same thing a
        # founder gets: a colour of their own, never an invented parent
        if not char or key in stack or len(parents) != 2 or not all(p in characters for p in parents):
            ryb = hue_to_ryb(hues.get(key) if key in hues else stable_hue(key))
            effective_ryb[key] = ryb
            generation[key] = 0
            return ryb
        a_key, b_key = parents
        ryb_a = resolve(a_key, stack | {key})
        ryb_b = resolve(b_key, stack | {key})
        frac_a = inheritance_fraction(char, characters[a_key], characters[b_key])
        ryb = tuple(frac_a * ca + (1 - frac_a) * cb for ca, cb in zip(ryb_a, ryb_b))
        effective_ryb[key] = ryb
        generation[key] = max(generation[a_key], generation[b_key]) + 1
        return ryb

    for key in characters:
        resolve(key)

    for key, char in characters.items():
        parents = char.get("parents") or []
        parentage = None
        if len(parents) == 2 and all(p in characters for p in parents):
            frac_a = inheritance_fraction(char, characters[parents[0]], characters[parents[1]])
            name_a = characters[parents[0]].get("name", parents[0])
            name_b = characters[parents[1]].get("name", parents[1])
            parentage = (f"{round(frac_a * 100)}% {name_a}, {round((1 - frac_a) * 100)}% {name_b} "
                         f"(reconstructed from which parent's criterion field it matches)")
        g.node(
            f"npc:{key}", char.get("name") or key, "person",
            city=char.get("city", ""), backstory=char.get("backstory", ""),
            criterion=(char.get("criterion") or {}).get("standard", ""),
            generation=generation[key], color=rgb_to_hex(ryb_to_rgb(*effective_ryb[key])),
            deceased=bool((char.get("life") or {}).get("deceased")),
            parentage=parentage, birth_pass=char.get("birth_pass"),
            file="_lore/characters/",
        )
    for key, char in characters.items():
        for parent_key in char.get("parents") or []:
            if parent_key in characters:
                g.edge(f"npc:{parent_key}", f"npc:{key}", "parent_of")
    return g


# --------------------------------------------------------------------------------------
# Structure graph - the repo on disk
# --------------------------------------------------------------------------------------

FILE_KINDS = [
    (r"^\.claude/skills/", "skill"),
    (r"^scripts/", "script"),
    (r"^_lore/material/", "material"),
    (r"^_lore/", "lore"),
    (r"^_npcs/templates/", "template"),
    (r"^_npcs/", "registry"),
    (r"^graphs/", "graph"),
    (r"blabber/dialogues/", "dialogue"),
    (r"^data/.*\.mcfunction$", "function"),
    (r"^data/", "datapack"),
    (r"^resourcepack/", "resourcepack"),
    (r"\.md$", "doc"),
]


def classify(rel: str) -> str:
    for pattern, kind in FILE_KINDS:
        if re.search(pattern, rel):
            return kind
    return "other"


def build_structure() -> Graph:
    g = Graph("structure")
    g.node("dir:.", "Provenance", "root", path=".")
    # bytes owned by each directory, counting everything nested underneath it -
    # not just its immediate children - so a folder like _lore that fans out
    # through several subdirectories still reads as heavy, not just its own degree.
    subtree_bytes: Counter = Counter()
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        rel_dir = Path(dirpath).relative_to(ROOT).as_posix()
        parent = "dir:." if rel_dir == "." else f"dir:{rel_dir}"
        if rel_dir != ".":
            g.node(parent, Path(rel_dir).name, "dir", path=rel_dir)
            up = Path(rel_dir).parent.as_posix()
            g.edge("dir:." if up == "." else f"dir:{up}", parent, "contains")
        for fn in sorted(filenames):
            rel = (Path(rel_dir) / fn).as_posix() if rel_dir != "." else fn
            try:
                size = (ROOT / rel).stat().st_size
            except OSError:
                size = 0
            g.node(f"file:{rel}", fn, classify(rel), path=rel, size=size)
            g.edge(parent, f"file:{rel}", "contains")
            parts = () if rel_dir == "." else Path(rel_dir).parts
            subtree_bytes["dir:."] += size
            acc = ""
            for part in parts:
                acc = f"{acc}/{part}" if acc else part
                subtree_bytes[f"dir:{acc}"] += size
    for did, total in subtree_bytes.items():
        g.nodes[did]["size"] = total
    return g


# --------------------------------------------------------------------------------------
# Concept graph - the three tiers, with live counts
# --------------------------------------------------------------------------------------

def build_concept(lore: Graph, structure: Graph) -> Graph:
    kinds = Counter(n["kind"] for n in lore.nodes.values())
    skills = sorted(p.parent.name for p in (ROOT / ".claude" / "skills").glob("*/SKILL.md"))
    scripts = sorted(
        p.relative_to(ROOT / "scripts").as_posix()
        for p in (ROOT / "scripts").glob("*/*.py")
    )
    functions = sum(1 for n in structure.nodes.values() if n["kind"] == "function")
    templates = sum(1 for n in structure.nodes.values() if n["kind"] == "template")
    material = sum(1 for n in structure.nodes.values() if n["kind"] == "material")
    resource = sum(1 for n in structure.nodes.values() if n["kind"] == "resourcepack")

    g = Graph("concept")
    layers = [
        ("layer:1", "Tier 1 - Content", "lore: the sources of truth", 1),
        ("layer:2", "Tier 2 - Handlers", "skills + scripts + supporting patterns", 2),
        ("layer:3", "Tier 3 - Shipping", "datapack + resource pack Minecraft loads", 3),
    ]
    for lid, label, note, tier in layers:
        g.node(lid, label, "layer", note=note, tier=tier)
    for a, b in zip(layers, layers[1:]):
        g.edge(a[0], b[0], "authors")

    def piece(pid, label, kind, tier, parent, **meta):
        g.node(pid, label, kind, tier=tier, **meta)
        g.edge(parent, pid, "holds")
        return pid

    for s in skills:
        piece(f"skill:{s}", f"/{s}", "skill", 2, "layer:2",
              file=f".claude/skills/{s}/SKILL.md")
    piece("src:material", "_lore/material", "source", 1, "layer:1",
          note=f"{material} excavated artifacts, never edited")
    piece("src:encodings", "_lore/encodings.json", "source", 1, "layer:1",
          note=f"{kinds['location']} locations, {kinds['concept']} concepts, "
               f"{kinds['conflict']} conflicts")
    piece("src:tale", "_lore/tales", "source", 1, "layer:1",
          note=f"{kinds['tale']} tales told by the author")
    piece("src:facts", "_lore/facts", "source", 1, "layer:1",
          note=f"{kinds['fact']} facts - never sampled, known by everyone")

    piece("sup:npcs", "_npcs/npcs/registry.json", "registry", 2, "layer:2",
          note=f"{kinds['npc']} NPC sheets")
    piece("sup:dialogs", "_npcs/dialogs/registry.json", "registry", 2, "layer:2",
          note="which NPC speaks which dialog")
    piece("sup:actions", "_npcs/actions/registry.json", "registry", 2, "layer:2",
          note="action templates + gesture dispatch")
    piece("sup:templates", "_npcs/templates", "template", 2, "layer:2",
          note=f"{templates} template files")
    for s in scripts:
        piece(f"script:{s}", Path(s).name, "script", 2, "layer:2", file=f"scripts/{s}")

    piece("pack:dialogues", "blabber/dialogues", "datapack", 3, "layer:3",
          note=f"{kinds['dialogue']} dialogues")
    piece("pack:functions", "functions", "datapack", 3, "layer:3",
          note=f"{functions} mcfunctions")
    piece("pack:meta", "pack.mcmeta", "datapack", 3, "layer:3", note="pack format 15")
    piece("rp:assets", "resourcepack/assets", "resourcepack", 3, "layer:3",
          note=f"{resource} files")

    # the flows that actually matter, beyond mere containment
    flows = [
        ("skill:enact", "pack:dialogues", "writes"),
        ("skill:enact", "src:encodings", "records hearsay"),
        ("skill:spawn", "pack:functions", "builds from templates"),
        ("skill:spawn", "sup:templates", "reads"),
        ("skill:integrate", "src:encodings", "analyses material into"),
        ("skill:integrate", "src:material", "reads"),
        ("skill:tell", "src:tale", "writes"),
        ("skill:character", "sup:npcs", "maintains"),
        ("skill:bake_dialog", "pack:dialogues", "compiles"),
        ("skill:package", "rp:assets", "ships"),
        ("script:lore/sample_lore_knowledge.py", "src:encodings", "samples"),
        ("script:lore/sample_lore_knowledge.py", "sup:npcs", "fills knowledge of"),
        ("script:minecraft/update_uuids.py", "sup:npcs", "captures UUIDs into"),
        ("script:minecraft/package.py", "pack:meta", "zips"),
        ("script:lore/roll_lifespan.py", "sup:npcs", "rolls lifespan into"),
        ("script:lore/lineage_coin.py", "sup:npcs", "decides lineage for"),
        ("script:graphs/graphifyish.py", "src:encodings", "graphs"),
        ("sup:npcs", "pack:functions", "spawns"),
        ("sup:dialogs", "pack:dialogues", "registers"),
        ("sup:actions", "rp:assets", "dispatches gestures to"),
        ("src:facts", "skill:enact", "loaded unconditionally by"),
    ]
    for src, dst, rel in flows:
        g.edge(src, dst, rel)
    return g


# --------------------------------------------------------------------------------------
# Render
# --------------------------------------------------------------------------------------

def render(payload: dict, out: Path) -> None:
    template = (Path(__file__).parent / "graphifyish_template.html").read_text(encoding="utf-8")
    blob = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    # </script> inside the data would close the tag early
    blob = blob.replace("</", "<\\/")
    out.write_text(template.replace("/*__GRAPH_DATA__*/null", blob), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true", help="also write graphs/graphifyish/graph.json")
    ap.add_argument("-o", "--out", default=str(OUT_DIR / "graphifyish.html"))
    args = ap.parse_args()

    lore, stats = build_lore()
    structure = build_structure()
    concept = build_concept(lore, structure)
    family = build_family()

    payload = {
        "lore": lore.dump(),
        "structure": structure.dump(),
        "concept": concept.dump(),
        "family": family.dump(),
        "generated": __import__("datetime").date.today().isoformat(),
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    render(payload, out)
    if args.json:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        (OUT_DIR / "graph.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")

    for g in (lore, structure, concept, family):
        d = g.dump()
        by_kind = Counter(n["kind"] for n in d["nodes"])
        print(f"{g.name:10} {len(d['nodes']):5} nodes {len(d['edges']):6} edges  "
              f"{dict(by_kind.most_common(6))}")
    if stats["unmatched_total"]:
        print(f"\nunresolved references: {stats['unmatched_total']}")
        for ref, n in stats["unmatched"]:
            print(f"  {n:4}x {ref}")
    if stats["dropped_edges"]:
        print(f"dropped edges (missing endpoint): {stats['dropped_edges']}")
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

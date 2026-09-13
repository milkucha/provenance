# Session log

Track where work left off between sessions, so a fresh start doesn't re-derive work already done. One entry per work session; append newest first. Format: date + what was worked on (brief) + where project stands.

Keep these entries short — one or two sentences per session — enough to orient the next person without re-reading chat history. This is a breadcrumb trail, not a transcript.

## Entries

**2026-09-13** — Full lore-schema cleanup ahead of a new simulation (encodings.json, contexts.json, facts/, tales/, grounding/ all rebuilt/audited; repo is now a clean, fresh-start state with no seeded lore content) followed by a full rebuild of `/simulate`'s per-pass mechanics: single-lead draw replacing the old pick-two/home-visit/arc-primacy model, arc-driven travel via a new location graph + pathfinding, a payment gate replacing the old word-overlap needs-check, and location/places_visited/last_scene now actually persisting across automated passes (previously only interactive `/enact` wrote them — this was blocking multi-hop travel from ever progressing, now fixed and verified). Smoke-tested end to end in scratch fixtures, committed and pushed. Known open gaps, both flagged in `TODO.md`: the `leads`/rivalry-followup mechanism has no call site left in the new model, and a death during a solo pass has no model dispatch to resolve death-legacy/shock moves. Next natural steps: reintegrate `leads`, decide solo-pass death handling, seed real material/characters to actually exercise any of this, or pick up the README technical-section rewrite that was this session's original ask.

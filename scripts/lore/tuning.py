"""
Shared loader for _lore/tuning.json - the single source of truth for /simulate's extended-mode
tunable knobs (odds, thresholds, cooldowns, the lifespan range). Not a standalone script - import
`load()` from a sibling script and fall back to these values when a CLI flag isn't explicitly
given, instead of hardcoding a local default. Change the JSON file to retune anything; no script
needs editing.

Usage (from a sibling script in this same directory):
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import tuning
    DEFAULT_ODDS = tuning.load()["odds_percent"]["contested"]
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
TUNING_PATH = ROOT / "_lore" / "tuning.json"


def load() -> dict:
    with open(TUNING_PATH, encoding="utf-8") as f:
        return json.load(f)

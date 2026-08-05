#!/usr/bin/env python3
"""
Luminacion — Release Packager
==============================
Uses only the Python standard library.

Zips the shippable parts of this repo — the datapack (pack.mcmeta + data/) and the
resource pack (resourcepack/pack.mcmeta + resourcepack/assets/) — into two standalone
zips for dropping into a different world/server's datapacks/ and resourcepacks/
folders. Everything dev-only (_lore/, _npcs/, _templates/, scripts/, .claude/, the
docs, and the three placeholder _template_*.json dialogues) is left out.

WORKFLOW
--------
    python scripts/package.py "<destination folder>"

Writes/overwrites <destination>/Luminacion.zip and
<destination>/Luminacion-resourcepack.zip. Both zips are flat at the root
(pack.mcmeta at the zip's top level) — required for Minecraft to load them as a
datapack/resource pack, whether dropped in zipped or unzipped into a folder.
"""

import argparse
import zipfile
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths (relative to project root, one level above /scripts)
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
DATAPACK_MCMETA = ROOT / "pack.mcmeta"
DATAPACK_DATA = ROOT / "data"
RESOURCEPACK_DIR = ROOT / "resourcepack"

# Placeholder dialogue templates — never shipped, only authoring scaffolding.
DATAPACK_EXCLUDES = {
    "data/luminacion/blabber/dialogues/_template_one_off.json",
    "data/luminacion/blabber/dialogues/_template_linear.json",
    "data/luminacion/blabber/dialogues/_template_branching.json",
}


def zip_datapack(dest: Path) -> Path:
    out = dest / "Luminacion.zip"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(DATAPACK_MCMETA, "pack.mcmeta")
        for path in DATAPACK_DATA.rglob("*"):
            if path.is_dir():
                continue
            rel = path.relative_to(ROOT).as_posix()
            if rel in DATAPACK_EXCLUDES:
                continue
            zf.write(path, rel)
    return out


def zip_resourcepack(dest: Path) -> Path:
    out = dest / "Luminacion-resourcepack.zip"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(RESOURCEPACK_DIR / "pack.mcmeta", "pack.mcmeta")
        for path in (RESOURCEPACK_DIR / "assets").rglob("*"):
            if path.is_dir():
                continue
            rel = path.relative_to(RESOURCEPACK_DIR).as_posix()
            zf.write(path, rel)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path, help="Folder to write the two zips into")
    args = parser.parse_args()
    args.destination.mkdir(parents=True, exist_ok=True)

    datapack = zip_datapack(args.destination)
    resourcepack = zip_resourcepack(args.destination)

    print(f"Datapack:     {datapack} ({datapack.stat().st_size / 1024:.1f} KB)")
    print(f"Resourcepack: {resourcepack} ({resourcepack.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()

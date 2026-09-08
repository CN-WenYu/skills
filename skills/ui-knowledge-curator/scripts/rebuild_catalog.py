#!/usr/bin/env python3
"""Build the ui-pattern-advisor catalog from knowledge-card front matter."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


SKILLS_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_KNOWLEDGE_ROOT = SKILLS_ROOT / "ui-pattern-advisor" / "references"
CARD_ROOTS = ("components", "interactions", "motion")
CATEGORY_LABELS = {
    "components": "Components",
    "interactions": "Interactions",
    "motion": "Motion",
}


def parse_scalar(value: str) -> str | list[str]:
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [item.strip().strip("'\"") for item in inner.split(",")]
    return value.strip("'\"")


def parse_front_matter(path: Path) -> dict[str, str | list[str]] | None:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        return None
    try:
        end = lines.index("---", 1)
    except ValueError as error:
        raise ValueError(f"{path}: unclosed front matter") from error

    data: dict[str, str | list[str]] = {}
    for line in lines[1:end]:
        if not line.strip():
            continue
        if ":" not in line:
            raise ValueError(f"{path}: invalid front matter line: {line}")
        key, value = line.split(":", 1)
        data[key.strip()] = parse_scalar(value)
    return data


def discover_cards(root: Path) -> list[tuple[Path, dict[str, str | list[str]]]]:
    cards: list[tuple[Path, dict[str, str | list[str]]]] = []
    for category in CARD_ROOTS:
        category_root = root / category
        if not category_root.exists():
            continue
        for path in sorted(category_root.rglob("*.md")):
            if path.name == "README.md":
                continue
            metadata = parse_front_matter(path)
            if metadata is not None:
                cards.append((path, metadata))
    return cards


def build_catalog(root: Path) -> str:
    cards = discover_cards(root)
    grouped: dict[str, list[tuple[Path, dict[str, str | list[str]]]]] = {
        category: [] for category in CARD_ROOTS
    }
    for path, metadata in cards:
        grouped[path.relative_to(root).parts[0]].append((path, metadata))

    lines = [
        "# UI Pattern Catalog",
        "",
        "Use this generated index to find canonical cards by name, Chinese name, type, status, platform, or path. Read [schema.md](schema.md) before adding or moving knowledge.",
        "",
        "Do not edit the tables manually. Run `python3 ../ui-knowledge-curator/scripts/rebuild_catalog.py` from this skill's directory or use the curator workflow.",
        "",
    ]
    for category in CARD_ROOTS:
        lines.extend(
            [
                f"## {CATEGORY_LABELS[category]}",
                "",
                "| Pattern | Chinese | Aliases | Tags | Kind | Term status | Platforms | Path |",
                "| --- | --- | --- | --- | --- | --- | --- | --- |",
            ]
        )
        entries = sorted(
            grouped[category],
            key=lambda entry: str(entry[1].get("name", "")).casefold(),
        )
        for path, metadata in entries:
            relative_path = path.relative_to(root).as_posix()
            platforms = metadata.get("platforms", [])
            platform_text = ", ".join(platforms) if isinstance(platforms, list) else str(platforms)
            aliases = metadata.get("aliases", [])
            alias_text = ", ".join(aliases) if isinstance(aliases, list) else str(aliases)
            tags = metadata.get("tags", [])
            tag_text = ", ".join(tags) if isinstance(tags, list) else str(tags)
            lines.append(
                "| [{name}]({path}) | {name_zh} | {aliases} | {tags} | `{kind}` | `{status}` | {platforms} | `{path}` |".format(
                    name=metadata.get("name", ""),
                    name_zh=metadata.get("name_zh", ""),
                    aliases=alias_text,
                    tags=tag_text,
                    kind=metadata.get("kind", ""),
                    status=metadata.get("term_status", ""),
                    platforms=platform_text,
                    path=relative_path,
                )
            )
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--knowledge-root", type=Path, default=DEFAULT_KNOWLEDGE_ROOT)
    parser.add_argument("--check", action="store_true", help="fail when catalog.md is stale")
    args = parser.parse_args()
    root = args.knowledge_root.resolve()
    catalog_path = root / "catalog.md"
    expected = build_catalog(root)

    if args.check:
        actual = catalog_path.read_text(encoding="utf-8") if catalog_path.exists() else ""
        if actual != expected:
            print(f"{catalog_path}: catalog is stale", file=sys.stderr)
            return 1
        print(f"Catalog is current: {catalog_path}")
        return 0

    catalog_path.write_text(expected, encoding="utf-8")
    print(f"Wrote {catalog_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

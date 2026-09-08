#!/usr/bin/env python3
"""Validate the ui-pattern-advisor knowledge-card library."""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

from rebuild_catalog import DEFAULT_KNOWLEDGE_ROOT, build_catalog, discover_cards, parse_front_matter


REQUIRED_FIELDS = (
    "id",
    "name",
    "name_zh",
    "kind",
    "term_status",
    "platforms",
    "aliases",
    "tags",
    "confidence",
    "last_reviewed",
)
REQUIRED_HEADINGS = (
    "## Definition",
    "## Problem solved",
    "## Recognition cues",
    "## Use when",
    "## Avoid when",
    "## States and behavior",
    "## Variants",
    "## Platform notes",
    "## Accessibility and performance",
    "## Common confusions",
    "## Related patterns",
)
ALLOWED_KINDS = {"component", "interaction-pattern", "motion-pattern", "feedback-pattern", "principle"}
ALLOWED_TERM_STATUSES = {"standard", "platform-specific", "common-informal", "descriptive"}
ALLOWED_CONFIDENCE = {"high", "medium", "low"}
ALLOWED_PLATFORMS = {"cross-platform", "ios", "android", "web"}
ALLOWED_KINDS_BY_ROOT = {
    "components": {"component", "feedback-pattern", "interaction-pattern"},
    "interactions": {"interaction-pattern"},
    "motion": {"motion-pattern"},
}
ALLOWED_REFERENCE_ROOTS = set(ALLOWED_KINDS_BY_ROOT) | {"foundations", "platforms"}
KEBAB_CASE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
EXTERNAL_URL = re.compile(r"https?://", re.IGNORECASE)


def validate_library(root: Path, check_catalog: bool = True) -> list[str]:
    root = root.resolve()
    if not root.is_dir():
        return [f"{root}: knowledge root does not exist"]
    errors: list[str] = []
    ids: dict[str, Path] = {}

    for child in root.iterdir():
        if child.is_dir() and child.name not in ALLOWED_REFERENCE_ROOTS:
            errors.append(f"{child.name}/: unapproved top-level reference directory")
    for directory in root.rglob("*"):
        if directory.is_dir() and not any(directory.iterdir()):
            errors.append(f"{directory.relative_to(root)}/: empty directories are not allowed")

    try:
        cards = discover_cards(root)
    except ValueError as error:
        return [str(error)]

    for path, metadata in cards:
        relative = path.relative_to(root)
        content = path.read_text(encoding="utf-8")
        if not KEBAB_CASE.fullmatch(path.name):
            errors.append(f"{relative}: filename must be lowercase kebab-case")
        for field in REQUIRED_FIELDS:
            if field not in metadata or metadata[field] == "":
                errors.append(f"{relative}: missing required field '{field}'")

        card_id = metadata.get("id")
        expected_id = ".".join(relative.with_suffix("").parts)
        if card_id and card_id != expected_id:
            errors.append(f"{relative}: id must be '{expected_id}'")
        if isinstance(card_id, str):
            if card_id in ids:
                errors.append(f"{relative}: duplicate id '{card_id}' also used by {ids[card_id].relative_to(root)}")
            else:
                ids[card_id] = path

        kind = metadata.get("kind")
        if kind not in ALLOWED_KINDS:
            errors.append(f"{relative}: invalid kind '{kind}'")
        elif relative.parts[0] in ALLOWED_KINDS_BY_ROOT and kind not in ALLOWED_KINDS_BY_ROOT[relative.parts[0]]:
            errors.append(f"{relative}: kind '{kind}' does not belong under {relative.parts[0]}/")

        term_status = metadata.get("term_status")
        if term_status not in ALLOWED_TERM_STATUSES:
            errors.append(f"{relative}: invalid term_status '{term_status}'")
        confidence = metadata.get("confidence")
        if confidence not in ALLOWED_CONFIDENCE:
            errors.append(f"{relative}: invalid confidence '{confidence}'")
        reviewed = metadata.get("last_reviewed")
        try:
            date.fromisoformat(str(reviewed))
        except ValueError:
            errors.append(f"{relative}: last_reviewed must be an ISO date")
        platforms = metadata.get("platforms")
        if not isinstance(platforms, list) or not platforms:
            errors.append(f"{relative}: platforms must be a non-empty inline list")
        elif invalid := set(platforms) - ALLOWED_PLATFORMS:
            errors.append(f"{relative}: invalid platforms {sorted(invalid)}")
        for list_field in ("aliases", "tags"):
            if not isinstance(metadata.get(list_field), list):
                errors.append(f"{relative}: {list_field} must be an inline list")

        positions = [content.find(heading) for heading in REQUIRED_HEADINGS]
        for heading, position in zip(REQUIRED_HEADINGS, positions):
            if position < 0:
                errors.append(f"{relative}: missing heading '{heading}'")
        present_positions = [position for position in positions if position >= 0]
        if present_positions != sorted(present_positions):
            errors.append(f"{relative}: required headings are out of order")

    for path in root.rglob("*.md"):
        content = path.read_text(encoding="utf-8")
        relative = path.relative_to(root)
        metadata = parse_front_matter(path)
        if metadata is not None and relative.parts[0] not in ALLOWED_KINDS_BY_ROOT:
            errors.append(f"{relative}: knowledge cards require an approved top-level category")
        if len(content.splitlines()) > 500:
            errors.append(f"{relative}: exceeds 500 lines")
        if EXTERNAL_URL.search(content):
            errors.append(f"{relative}: reference files must not retain external URLs")
        for target in MARKDOWN_LINK.findall(content):
            target_path = target.split("#", 1)[0]
            if not target_path or "://" in target_path or target_path.startswith("mailto:"):
                continue
            resolved = (path.parent / target_path).resolve()
            if not resolved.exists():
                errors.append(f"{relative}: broken link '{target}'")

    if check_catalog:
        catalog_path = root / "catalog.md"
        actual = catalog_path.read_text(encoding="utf-8") if catalog_path.exists() else ""
        try:
            expected = build_catalog(root)
        except ValueError as error:
            errors.append(str(error))
        else:
            if actual != expected:
                errors.append("catalog.md: catalog is stale")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--knowledge-root", type=Path, default=DEFAULT_KNOWLEDGE_ROOT)
    parser.add_argument("--skip-catalog", action="store_true")
    args = parser.parse_args()
    errors = validate_library(args.knowledge_root, check_catalog=not args.skip_catalog)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        print(f"Knowledge validation failed with {len(errors)} error(s).", file=sys.stderr)
        return 1
    print(f"Knowledge validation passed: {args.knowledge_root.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

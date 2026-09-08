from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from rebuild_catalog import build_catalog  # noqa: E402
from validate_knowledge import validate_library  # noqa: E402


HEADINGS = """## Definition
Definition.
## Problem solved
Problem.
## Recognition cues
Cues.
## Use when
Use.
## Avoid when
Avoid.
## States and behavior
States.
## Variants
Variants.
## Platform notes
Notes.
## Accessibility and performance
Accessible.
## Common confusions
Confusions.
## Related patterns
None.
"""


def card(card_id: str = "motion.feedback.sample", **overrides: str) -> str:
    fields = {
        "id": card_id,
        "name": "Sample",
        "name_zh": "示例",
        "kind": "motion-pattern",
        "term_status": "descriptive",
        "platforms": "[ios, android, web]",
        "aliases": "[]",
        "tags": "[sample]",
        "confidence": "medium",
        "last_reviewed": "2026-09-08",
    }
    fields.update(overrides)
    front_matter = "\n".join(f"{key}: {value}" for key, value in fields.items())
    return f"---\n{front_matter}\n---\n\n# Sample\n\n{HEADINGS}"


class KnowledgeToolsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        (self.root / "motion" / "feedback").mkdir(parents=True)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def write_card(self, relative: str, content: str | None = None) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content or card(".".join(path.relative_to(self.root).with_suffix("").parts)), encoding="utf-8")
        return path

    def test_catalog_generation_indexes_card(self) -> None:
        content = card(aliases="[fixture alias]", tags="[catalog-tag]")
        self.write_card("motion/feedback/sample.md", content)
        catalog = build_catalog(self.root)
        self.assertIn("[Sample](motion/feedback/sample.md)", catalog)
        self.assertIn("`motion-pattern`", catalog)
        self.assertIn("fixture alias", catalog)
        self.assertIn("catalog-tag", catalog)

    def test_duplicate_id_is_rejected(self) -> None:
        self.write_card("motion/feedback/sample.md")
        duplicate = card("motion.feedback.sample")
        self.write_card("motion/feedback/second.md", duplicate)
        errors = validate_library(self.root, check_catalog=False)
        self.assertTrue(any("duplicate id" in error for error in errors))

    def test_invalid_enum_is_rejected(self) -> None:
        self.write_card("motion/feedback/sample.md", card(kind="animation"))
        errors = validate_library(self.root, check_catalog=False)
        self.assertTrue(any("invalid kind" in error for error in errors))

    def test_missing_field_is_rejected(self) -> None:
        content = card().replace("confidence: medium\n", "")
        self.write_card("motion/feedback/sample.md", content)
        errors = validate_library(self.root, check_catalog=False)
        self.assertTrue(any("missing required field 'confidence'" in error for error in errors))

    def test_wrong_directory_is_rejected(self) -> None:
        content = card("interactions.feedback.sample", kind="motion-pattern")
        self.write_card("interactions/feedback/sample.md", content)
        errors = validate_library(self.root, check_catalog=False)
        self.assertTrue(any("does not belong" in error for error in errors))

    def test_broken_relative_link_is_rejected(self) -> None:
        content = card() + "\n[Missing](missing.md)\n"
        self.write_card("motion/feedback/sample.md", content)
        errors = validate_library(self.root, check_catalog=False)
        self.assertTrue(any("broken link" in error for error in errors))

    def test_stale_catalog_is_rejected(self) -> None:
        self.write_card("motion/feedback/sample.md")
        (self.root / "catalog.md").write_text("stale\n", encoding="utf-8")
        errors = validate_library(self.root)
        self.assertIn("catalog.md: catalog is stale", errors)

    def test_unknown_top_level_category_is_rejected(self) -> None:
        content = card("immersive-magic.sample")
        self.write_card("immersive-magic/sample.md", content)
        errors = validate_library(self.root, check_catalog=False)
        self.assertTrue(any("approved top-level category" in error for error in errors))

    def test_external_url_in_card_is_rejected(self) -> None:
        content = card() + "\nhttps://example.com/source\n"
        self.write_card("motion/feedback/sample.md", content)
        errors = validate_library(self.root, check_catalog=False)
        self.assertTrue(any("must not retain external URLs" in error for error in errors))

    def test_empty_directory_is_rejected(self) -> None:
        (self.root / "components" / "empty").mkdir(parents=True)
        errors = validate_library(self.root, check_catalog=False)
        self.assertTrue(any("empty directories are not allowed" in error for error in errors))

    def test_missing_knowledge_root_is_rejected(self) -> None:
        errors = validate_library(self.root / "missing", check_catalog=False)
        self.assertTrue(any("knowledge root does not exist" in error for error in errors))


if __name__ == "__main__":
    unittest.main()

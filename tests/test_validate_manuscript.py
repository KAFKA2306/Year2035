from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "validate_manuscript.py"
SPEC = importlib.util.spec_from_file_location("validate_manuscript", MODULE_PATH)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class GlossaryRowProvenanceTest(unittest.TestCase):
    def test_wrong_link_on_term_row_is_not_masked_by_another_row(self) -> None:
        glossary = """\
| 名称 | 種別 | 定義 | 初出 |
| --- | --- | --- | --- |
| ハルコ | 人物 | definition | [第1章](manuscript/02-chapter-1.md) |
| 時間割税 | 制度 | definition | [第0章](manuscript/01-chapter-0.md) |
"""
        rows = validator.parse_glossary_rows(glossary)
        self.assertEqual(rows["ハルコ"], "manuscript/02-chapter-1.md")
        self.assertNotEqual(
            rows["ハルコ"], validator.GLOSSARY_FIRST_APPEARANCE["ハルコ"]
        )

    def test_missing_first_appearance_link_fails_explicitly(self) -> None:
        glossary = """\
| 名称 | 種別 | 定義 | 初出 |
| --- | --- | --- | --- |
| ハルコ | 人物 | definition | 第0章 |
"""
        with self.assertRaisesRegex(SystemExit, "must contain exactly one"):
            validator.parse_glossary_rows(glossary)

    def test_duplicate_tracked_term_row_fails_explicitly(self) -> None:
        glossary = """\
| 名称 | 種別 | 定義 | 初出 |
| --- | --- | --- | --- |
| ハルコ | 人物 | definition | [第0章](manuscript/01-chapter-0.md) |
| ハルコ | 人物 | duplicate | [第0章](manuscript/01-chapter-0.md) |
"""
        with self.assertRaisesRegex(SystemExit, "duplicate row"):
            validator.parse_glossary_rows(glossary)

    def test_canonical_glossary_rows_match_contract(self) -> None:
        glossary = (Path(__file__).resolve().parents[1] / "glossary.md").read_text(
            encoding="utf-8"
        )
        self.assertEqual(
            validator.parse_glossary_rows(glossary),
            validator.GLOSSARY_FIRST_APPEARANCE,
        )


if __name__ == "__main__":
    unittest.main()

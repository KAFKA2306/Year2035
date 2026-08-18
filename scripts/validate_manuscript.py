#!/usr/bin/env python3
"""Validate the canonical manuscript structure, links, and glossary provenance."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ORDERED_FILES = [
    ("manuscript/00-preface.md", "# まえがき"),
    ("manuscript/01-chapter-0.md", "# 第0章"),
    ("manuscript/02-chapter-1.md", "# 第1章"),
    ("manuscript/03-chapter-2.md", "# 第2章"),
    ("manuscript/04-chapter-3.md", "# 第3章"),
    ("manuscript/05-afterword.md", "# あとがき"),
]

GLOSSARY_FIRST_APPEARANCE = {
    "ハルコ": "manuscript/01-chapter-0.md",
    "ユウキ": "manuscript/02-chapter-1.md",
    "時間割税": "manuscript/01-chapter-0.md",
    "データ紡ぎ": "manuscript/01-chapter-0.md",
    "思考警察アプリ": "manuscript/01-chapter-0.md",
    "共感枠": "manuscript/01-chapter-0.md",
    "ホログラム言明": "manuscript/01-chapter-0.md",
    "記憶整形": "manuscript/01-chapter-0.md",
    "無名者マーケット": "manuscript/02-chapter-1.md",
    "レジスタンス": "manuscript/02-chapter-1.md",
}


def fail(message: str) -> None:
    raise SystemExit(f"manuscript validation failed: {message}")


def read(path: str) -> str:
    target = ROOT / path
    if not target.is_file():
        fail(f"missing file: {path}")
    return target.read_text(encoding="utf-8")


def validate_headings() -> None:
    for path, expected_heading in ORDERED_FILES:
        first_line = read(path).splitlines()[0]
        if first_line != expected_heading:
            fail(f"{path}: expected heading {expected_heading!r}, got {first_line!r}")

    chapter_numbers = []
    for path, heading in ORDERED_FILES[1:5]:
        match = re.fullmatch(r"# 第(\d+)章", heading)
        if not match:
            fail(f"invalid chapter heading contract: {path}")
        chapter_numbers.append(int(match.group(1)))
    if chapter_numbers != list(range(4)):
        fail(f"chapter numbers are not contiguous: {chapter_numbers}")


def validate_readme_links() -> None:
    readme = read("README.md")
    positions = []
    for path, _ in ORDERED_FILES:
        token = f"]({path})"
        pos = readme.find(token)
        if pos < 0:
            fail(f"README missing manuscript link: {path}")
        positions.append(pos)
    if positions != sorted(positions):
        fail("README manuscript links are not in reading order")
    if "](glossary.md)" not in readme:
        fail("README missing glossary link")


def validate_glossary() -> None:
    glossary = read("glossary.md")
    ordered_paths = [path for path, _ in ORDERED_FILES]
    bodies = {path: read(path) for path in ordered_paths}

    for term, expected_path in GLOSSARY_FIRST_APPEARANCE.items():
        if term not in glossary:
            fail(f"glossary missing term: {term}")
        if f"]({expected_path})" not in glossary:
            fail(f"glossary has no expected first-appearance link for {term}")
        expected_index = ordered_paths.index(expected_path)
        if term not in bodies[expected_path]:
            fail(f"term {term} is absent from declared first appearance {expected_path}")
        for earlier in ordered_paths[:expected_index]:
            if term in bodies[earlier]:
                fail(f"term {term} appears earlier in {earlier} than declared {expected_path}")


def main() -> None:
    validate_headings()
    validate_readme_links()
    validate_glossary()
    print("manuscript validation passed")


if __name__ == "__main__":
    main()

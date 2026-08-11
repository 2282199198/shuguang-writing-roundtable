#!/usr/bin/env python3
"""Static release checks for portability, privacy and package shape."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skill" / "shuguang-writing-roundtable"
TEXT_SUFFIXES = {".md", ".py", ".yaml", ".yml", ".json", ".html", ".txt"}


class PublicPackageTests(unittest.TestCase):
    def test_required_skill_files_exist(self) -> None:
        self.assertTrue((SKILL / "SKILL.md").is_file())
        self.assertTrue((SKILL / "agents" / "openai.yaml").is_file())
        self.assertTrue((ROOT / "README.md").is_file())
        self.assertTrue((ROOT / "LICENSE").is_file())

    def test_skill_entrypoint_is_compact_and_has_only_supported_frontmatter(self) -> None:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertLess(len(text.splitlines()), 500)
        match = re.match(r"^---\n(.*?)\n---\n", text, flags=re.DOTALL)
        self.assertIsNotNone(match)
        keys = [line.split(":", 1)[0].strip() for line in match.group(1).splitlines() if ":" in line]
        self.assertEqual(keys, ["name", "description"])
        self.assertIn("name: shuguang-writing-roundtable", text)

    def test_trigger_metadata_and_in_skill_usage_guide(self) -> None:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        metadata = re.match(r"^---\n(.*?)\n---\n", text, flags=re.DOTALL)
        self.assertIsNotNone(metadata)
        description = metadata.group(1)
        for phrase in [
            "曙光圆桌写作会议",
            "圆桌写作",
            "写作专家团",
            "公众号长文",
            "知识型长文",
            "事实核查",
            "公众号排版",
            "$shuguang-writing-roundtable",
        ]:
            self.assertIn(phrase, description)

        self.assertIn("## 快速触发与使用指南", text)
        self.assertIn("最确定的显式调用", text)
        self.assertIn("自然语言自动触发", text)

        agent_yaml = (SKILL / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn('default_prompt: "Use $shuguang-writing-roundtable ', agent_yaml)
        self.assertIn("allow_implicit_invocation: true", agent_yaml)

    def test_no_private_material_or_secret_shapes(self) -> None:
        forbidden_literals = [
            "14" + "771",
            "船长" + "的航海日志",
            "笔记导出" + "_19篇",
            "教育的" + "提前量",
            "github" + "_pat_",
            "gh" + "p_",
        ]
        actual_private_path = re.compile(r"[A-Za-z]:\\Users\\[^\\\s]+")
        secret = re.compile(r"(?:sk-[A-Za-z0-9]{20,}|BEGIN (?:RSA|OPENSSH|EC) PRIVATE KEY)")
        failures: list[str] = []
        for path in ROOT.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            text = path.read_text(encoding="utf-8")
            for literal in forbidden_literals:
                if literal in text:
                    failures.append(f"{path.relative_to(ROOT)} contains {literal}")
            if actual_private_path.search(text) or secret.search(text):
                failures.append(f"{path.relative_to(ROOT)} contains a private path or secret shape")
        self.assertEqual(failures, [])

    def test_cache_is_ignored_and_no_file_exceeds_github_limit(self) -> None:
        gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("__pycache__/", gitignore)
        self.assertIn("*.py[cod]", gitignore)
        oversized = [path for path in ROOT.rglob("*") if path.is_file() and path.stat().st_size >= 100_000_000]
        self.assertEqual(oversized, [])

    def test_all_local_markdown_links_resolve(self) -> None:
        pattern = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
        missing: list[str] = []
        for path in ROOT.rglob("*.md"):
            text = path.read_text(encoding="utf-8")
            for target in pattern.findall(text):
                target = target.strip().strip("<>")
                if re.match(r"^(?:https?://|mailto:|tel:|#)", target):
                    continue
                clean = target.split("#", 1)[0].split("?", 1)[0]
                if clean and not (path.parent / clean).exists():
                    missing.append(f"{path.relative_to(ROOT)} -> {target}")
        self.assertEqual(missing, [])

    def test_catalog_assets_are_present(self) -> None:
        catalog_path = SKILL / "assets" / "wechat-themes" / "theme-catalog.json"
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        self.assertEqual(len(catalog["themes"]), 6)
        images = []
        for theme in catalog["themes"]:
            for background in theme["backgrounds"]:
                image = catalog_path.parent / background["file"]
                self.assertTrue(image.is_file(), image)
                self.assertEqual(image.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")
                images.append(image)
        self.assertEqual(len(images), 7)


if __name__ == "__main__":
    unittest.main(verbosity=2)

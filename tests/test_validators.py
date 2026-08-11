#!/usr/bin/env python3
"""Standalone regression tests for the public Shuguang Skill package."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SKILL = ROOT / "skill" / "shuguang-writing-roundtable"
FIXTURES = HERE / "fixtures"
OUTPUTS = HERE / "outputs"


def run_validator(script: str, *args: object) -> subprocess.CompletedProcess[str]:
    command = [
        sys.executable,
        "-X",
        "utf8",
        str(SKILL / "scripts" / script),
        *(str(arg) for arg in args),
    ]
    return subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=False)


class ValidatorTests(unittest.TestCase):
    def test_casefile_accepts_valid_contract(self) -> None:
        result = run_validator("validate_casefile.py", FIXTURES / "casefile-valid.json")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("[PASS]", result.stdout)

    def test_casefile_rejects_ready_with_open_must_fix(self) -> None:
        result = run_validator("validate_casefile.py", FIXTURES / "casefile-invalid.json")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must_fix", result.stdout)
        self.assertIn("未定义 ID", result.stdout)

    def test_revision_accepts_only_requested_change(self) -> None:
        result = run_validator(
            "validate_revision.py",
            "--before", FIXTURES / "revision-before.md",
            "--after", OUTPUTS / "revision-after.md",
            "--locked", "CONTEXT",
            "--locked", "METHOD",
            "--locked", "CLOSING",
            "--require-changed", "OPENING",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_revision_rejects_locked_change(self) -> None:
        result = run_validator(
            "validate_revision.py",
            "--before", FIXTURES / "revision-before.md",
            "--after", FIXTURES / "revision-tampered.md",
            "--locked", "METHOD",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("已被修改", result.stdout)

    def test_delivery_accepts_self_contained_html(self) -> None:
        result = run_validator(
            "validate_delivery.py",
            OUTPUTS / "synthetic-article.html",
            "--min-han", 250,
            "--require-url", 2,
            "--self-contained",
            "--forbid-file", FIXTURES / "risk-patterns.txt",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_delivery_rejects_forbidden_claim(self) -> None:
        result = run_validator(
            "validate_delivery.py",
            FIXTURES / "delivery-bad.md",
            "--forbid-file", FIXTURES / "risk-patterns.txt",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("命中禁止正则", result.stdout)

    def test_delivery_accepts_wechat_fragment(self) -> None:
        result = run_validator(
            "validate_delivery.py",
            FIXTURES / "wechat-fragment-valid.html",
            "--wechat-fragment",
            "--min-han", 4,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("wechat_leaf_spans", result.stdout)

    def test_delivery_rejects_webpage_as_wechat_fragment(self) -> None:
        result = run_validator(
            "validate_delivery.py",
            FIXTURES / "wechat-fragment-invalid.html",
            "--wechat-fragment",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("完整网页外壳", result.stdout)
        self.assertIn("未被 <span leaf>", result.stdout)

    def test_public_final_accepts_body_without_reference_list(self) -> None:
        result = run_validator(
            "validate_delivery.py",
            FIXTURES / "wechat-fragment-valid.html",
            "--wechat-public-final",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("public_reference_headings=0", result.stdout)

    def test_public_final_rejects_reference_heading(self) -> None:
        result = run_validator(
            "validate_delivery.py",
            FIXTURES / "wechat-public-with-references.html",
            "--wechat-public-final",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("仍包含参考资料标题", result.stdout)

    def test_theme_catalog_accepts_six_generated_themes(self) -> None:
        result = run_validator("validate_theme_catalog.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("themes=6", result.stdout)
        self.assertIn("generated_images=7", result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)

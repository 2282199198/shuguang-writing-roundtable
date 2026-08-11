#!/usr/bin/env python3
"""Check that locked, ID-labelled sections remain textually unchanged."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


LABEL_RE = re.compile(r"^\s*([A-Z]\d+):(?:\s|$)")
HEADING_RE = re.compile(
    r"^\s*#{1,6}\s+(?:\[([A-Za-z][A-Za-z0-9_.-]{0,63})\]|([A-Z]\d+))(?:\s|$)"
)
COMMENT_RE = re.compile(r"^\s*<!--\s*section:([A-Za-z][A-Za-z0-9_.-]{0,63})\s*-->\s*$")


def read_utf8(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"{path} 不是严格 UTF-8：{exc}") from exc


def marker_id(line: str) -> str | None:
    match = COMMENT_RE.match(line)
    if match:
        return match.group(1)
    match = LABEL_RE.match(line)
    if match:
        return match.group(1)
    match = HEADING_RE.match(line)
    if match:
        return match.group(1) or match.group(2)
    return None


def extract_sections(text: str) -> tuple[dict[str, str], set[str]]:
    lines = text.splitlines()
    starts: list[tuple[int, str]] = []
    duplicates: set[str] = set()
    seen: set[str] = set()
    for index, line in enumerate(lines):
        section_id = marker_id(line)
        if section_id is None:
            continue
        if section_id in seen:
            duplicates.add(section_id)
        seen.add(section_id)
        starts.append((index, section_id))

    sections: dict[str, str] = {}
    for position, (start, section_id) in enumerate(starts):
        end = starts[position + 1][0] if position + 1 < len(starts) else len(lines)
        sections[section_id] = "\n".join(lines[start:end]).rstrip()
    return sections, duplicates


def main() -> int:
    parser = argparse.ArgumentParser(
        description="逐字比较修订前后的锁定段落；仅忽略 CRLF/LF 行尾差异。"
    )
    parser.add_argument("--before", type=Path, required=True)
    parser.add_argument("--after", type=Path, required=True)
    parser.add_argument("--locked", action="append", default=[])
    parser.add_argument("--require-changed", action="append", default=[])
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args()

    errors: list[str] = []
    details: list[str] = []
    if not args.locked:
        errors.append("至少传入一个 --locked ID。")

    for path in (args.before, args.after):
        if not path.is_file():
            errors.append(f"文件不存在：{path}")

    if not errors:
        try:
            before_sections, before_duplicates = extract_sections(read_utf8(args.before))
            after_sections, after_duplicates = extract_sections(read_utf8(args.after))
        except ValueError as exc:
            errors.append(str(exc))
        else:
            for duplicate in sorted(before_duplicates | after_duplicates):
                errors.append(f"段落 ID 重复，无法可靠锁定：{duplicate}。")

            for section_id in args.locked:
                if section_id not in before_sections or section_id not in after_sections:
                    errors.append(f"锁定段落 {section_id} 未同时出现在修订前后文件中。")
                elif before_sections[section_id] != after_sections[section_id]:
                    errors.append(f"锁定段落 {section_id} 已被修改。")
                else:
                    details.append(f"锁定段落 {section_id} 逐字一致。")

            for section_id in args.require_changed:
                if section_id not in before_sections or section_id not in after_sections:
                    errors.append(f"要求修改的段落 {section_id} 未同时出现在两个文件中。")
                elif before_sections[section_id] == after_sections[section_id]:
                    errors.append(f"要求修改的段落 {section_id} 实际未变化。")
                else:
                    details.append(f"要求修改的段落 {section_id} 已变化。")

    passed = not errors
    result = {
        "status": "PASS" if passed else "FAIL",
        "before": str(args.before.resolve()),
        "after": str(args.after.resolve()),
        "locked": args.locked,
        "required_changed": args.require_changed,
        "errors": errors,
        "details": details,
    }
    if args.json_output:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"[{result['status']}] revision lock check")
        for detail in details:
            print(f"OK: {detail}")
        for issue in errors:
            print(f"ERROR: {issue}")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())

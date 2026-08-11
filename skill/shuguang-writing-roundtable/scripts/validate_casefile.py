#!/usr/bin/env python3
"""Validate a saved Shuguang roundtable casefile.

JSON is the dependency-free interchange format. YAML is accepted only when
PyYAML is already available; the validator never installs dependencies.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ALLOWED_MODES = {"full", "fast", "single", "revision", "deep"}
ALLOWED_STAGES = {
    "brief",
    "topic",
    "evidence",
    "outline",
    "draft",
    "fact_check",
    "quality_review",
    "delivery",
    "done",
}
ALLOWED_MISSING_STATES = {
    "not_provided",
    "inferred",
    "confirmed",
    "pending_verification",
    "conflict_unresolved",
    "not_applicable",
}
REQUIRED_FIELDS = {
    "run_id": str,
    "mode": str,
    "current_stage": str,
    "brief_version": str,
    "approved_decisions": list,
    "assumptions": list,
    "open_questions": list,
    "locked_content": list,
    "must_fix": list,
    "revision_log": list,
    "next_action": str,
}
DEFINITION_CONTAINERS = {
    "briefs": "brief_id",
    "topics": "topic_id",
    "research_maps": "research_map_id",
    "questions": "question_id",
    "claims": "claim_id",
    "sources": "source_id",
    "outlines": "outline_id",
    "drafts": "draft_id",
    "fact_checks": "fact_check_id",
    "reviews": "review_id",
    "revisions": "revision_id",
    "deliveries": "delivery_id",
}
REFERENCE_FIELDS = {
    "question_ids": "question_id",
    "claim_ids": "claim_id",
    "source_ids": "source_id",
}


def load_casefile(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"文件不是严格 UTF-8：{exc}") from exc

    suffix = path.suffix.lower()
    try:
        if suffix == ".json":
            data = json.loads(text)
        elif suffix in {".yaml", ".yml"}:
            try:
                import yaml  # type: ignore
            except ImportError as exc:
                raise ValueError(
                    "YAML 校验需要环境中已存在 PyYAML；请改存 JSON，校验器不会自动安装依赖。"
                ) from exc
            try:
                data = yaml.safe_load(text)
            except yaml.YAMLError as exc:  # type: ignore[attr-defined]
                raise ValueError(f"YAML 语法错误：{exc}") from exc
        else:
            data = json.loads(text)
    except (json.JSONDecodeError, ValueError) as exc:
        raise ValueError(f"无法解析案卷：{exc}") from exc

    if not isinstance(data, dict):
        raise ValueError("案卷顶层必须是对象。")
    return data


def walk(value: Any, path: str = "$"):
    yield path, value
    if isinstance(value, dict):
        for key, child in value.items():
            yield from walk(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk(child, f"{path}[{index}]")


def collect_definitions(data: Any) -> tuple[dict[str, set[str]], list[str]]:
    definitions = {field: set() for field in DEFINITION_CONTAINERS.values()}
    errors: list[str] = []

    def visit(value: Any, path: str = "$") -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                if key in DEFINITION_CONTAINERS and isinstance(child, list):
                    id_field = DEFINITION_CONTAINERS[key]
                    for index, item in enumerate(child):
                        item_path = f"{path}.{key}[{index}]"
                        if not isinstance(item, dict) or not isinstance(item.get(id_field), str):
                            errors.append(f"{item_path} 缺少字符串字段 {id_field}。")
                            continue
                        item_id = item[id_field]
                        if item_id in definitions[id_field]:
                            errors.append(f"{item_path} 重复定义 {id_field}={item_id}。")
                        definitions[id_field].add(item_id)
                visit(child, f"{path}.{key}")
        elif isinstance(value, list):
            for index, child in enumerate(value):
                visit(child, f"{path}[{index}]")

    visit(data)
    return definitions, errors


def validate(data: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    for field, expected_type in REQUIRED_FIELDS.items():
        if field not in data:
            errors.append(f"缺少必填字段：{field}。")
        elif not isinstance(data[field], expected_type):
            errors.append(f"字段 {field} 必须是 {expected_type.__name__}。")

    run_id = data.get("run_id")
    if isinstance(run_id, str) and not re.fullmatch(r"RT-\d{8}-\d{2,}", run_id):
        errors.append("run_id 应符合 RT-YYYYMMDD-NN。")
    if data.get("mode") not in ALLOWED_MODES:
        errors.append(f"mode 必须是：{', '.join(sorted(ALLOWED_MODES))}。")
    if data.get("current_stage") not in ALLOWED_STAGES:
        errors.append(f"current_stage 非法：{data.get('current_stage')!r}。")

    for field in ("run_id", "brief_version", "next_action"):
        value = data.get(field)
        if isinstance(value, str) and not value.strip():
            errors.append(f"字段 {field} 不得为空；未知时使用明确状态词。")

    for path, value in walk(data):
        if isinstance(value, str) and not value.strip():
            warnings.append(f"{path} 是空字符串；建议改用明确状态词。")

    definitions, definition_errors = collect_definitions(data)
    errors.extend(definition_errors)

    for path, value in walk(data):
        if not isinstance(value, dict):
            continue
        for ref_field, id_field in REFERENCE_FIELDS.items():
            refs = value.get(ref_field)
            if refs is None:
                continue
            if not isinstance(refs, list) or not all(isinstance(item, str) for item in refs):
                errors.append(f"{path}.{ref_field} 必须是字符串列表。")
                continue
            known = definitions[id_field]
            if known:
                missing = sorted(set(refs) - known)
                if missing:
                    errors.append(
                        f"{path}.{ref_field} 引用了未定义 ID：{', '.join(missing)}。"
                    )
            elif refs:
                warnings.append(
                    f"{path}.{ref_field} 有引用，但案卷未保存 {id_field} 定义，无法闭环核验。"
                )

    ready_statuses = [
        value
        for path, value in walk(data)
        if path.endswith(".ready_status") and value in {"ready", "ready_with_caveats"}
    ]
    must_fix = data.get("must_fix")
    if ready_statuses and isinstance(must_fix, list) and must_fix:
        errors.append("交付状态已标为 ready/ready_with_caveats，但顶层 must_fix 尚未清零。")

    for path, value in walk(data):
        if path.endswith(".must_fix") and isinstance(value, int) and value > 0 and ready_statuses:
            errors.append(f"{path}={value}，不能同时宣布可交付。")

    for field in ("assumptions", "open_questions"):
        values = data.get(field)
        if isinstance(values, list):
            for index, item in enumerate(values):
                if item is None or item == "":
                    warnings.append(f"$.{field}[{index}] 缺少明确内容。")

    unexpected_states = []
    for path, value in walk(data):
        if path.endswith(".status") and isinstance(value, str):
            if value.startswith("not_") and value not in ALLOWED_MISSING_STATES:
                unexpected_states.append(f"{path}={value}")
    if unexpected_states:
        warnings.append("发现非标准缺失状态：" + ", ".join(unexpected_states))

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="校验曙光圆桌 JSON/YAML 案卷。")
    parser.add_argument("casefile", type=Path)
    parser.add_argument("--strict-warnings", action="store_true")
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args()

    if not args.casefile.is_file():
        errors = [f"案卷不存在：{args.casefile}"]
        warnings: list[str] = []
    else:
        try:
            data = load_casefile(args.casefile)
            errors, warnings = validate(data)
        except ValueError as exc:
            errors, warnings = [str(exc)], []

    passed = not errors and not (args.strict_warnings and warnings)
    result = {
        "status": "PASS" if passed else "FAIL",
        "file": str(args.casefile.resolve()),
        "errors": errors,
        "warnings": warnings,
    }
    if args.json_output:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"[{result['status']}] {result['file']}")
        for issue in errors:
            print(f"ERROR: {issue}")
        for issue in warnings:
            print(f"WARN: {issue}")
        if passed and not warnings:
            print("案卷结构、必填状态与可校验 ID 引用均通过。")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())

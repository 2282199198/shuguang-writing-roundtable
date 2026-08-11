#!/usr/bin/env python3
"""Validate the fixed WeChat theme catalog and generated image assets."""

from __future__ import annotations

import argparse
import json
import re
import struct
import sys
from pathlib import Path


HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")
REQUIRED_PALETTE = {"canvas", "text", "body", "muted", "primary", "accent", "card", "line"}
REQUIRED_COMPONENTS = {"opening", "section_heading", "subheading", "quote", "highlight", "list", "divider"}


def luminance(color: str) -> float:
    values = [int(color[index : index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in values]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast(foreground: str, background: str) -> float:
    light, dark = sorted((luminance(foreground), luminance(background)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


def png_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()[:24]
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        raise ValueError("不是有效 PNG")
    return struct.unpack(">II", data[16:24])


def main() -> int:
    default = Path(__file__).resolve().parents[1] / "assets" / "wechat-themes" / "theme-catalog.json"
    parser = argparse.ArgumentParser(description="校验曙光圆桌公众号固定主题目录。")
    parser.add_argument("catalog", nargs="?", type=Path, default=default)
    args = parser.parse_args()

    catalog_path = args.catalog.resolve()
    errors: list[str] = []
    metrics: dict[str, object] = {}
    try:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        print(f"[FAIL] 无法读取主题目录：{exc}")
        return 1

    themes = catalog.get("themes")
    if not isinstance(themes, list):
        print("[FAIL] themes 必须是数组。")
        return 1
    if len(themes) != 6:
        errors.append(f"固定主题应为 6 套，实际为 {len(themes)} 套。")

    ids: set[str] = set()
    names: set[str] = set()
    generated_images = 0
    dimensions: dict[str, str] = {}
    catalog_root = catalog_path.parent.resolve()

    for index, theme in enumerate(themes, start=1):
        label = f"主题 {index}"
        if not isinstance(theme, dict):
            errors.append(f"{label} 不是对象。")
            continue
        theme_id = theme.get("id")
        name = theme.get("name_cn")
        label = f"主题 {theme_id or index}"
        if not isinstance(theme_id, str) or not re.match(r"^[a-z0-9-]+$", theme_id):
            errors.append(f"{label} 的 id 必须是小写英文、数字或连字符。")
        elif theme_id in ids:
            errors.append(f"重复主题 id：{theme_id}。")
        else:
            ids.add(theme_id)
        if not isinstance(name, str) or not name.strip():
            errors.append(f"{label} 缺少中文名。")
        elif name in names:
            errors.append(f"重复主题中文名：{name}。")
        else:
            names.add(name)

        palette = theme.get("palette")
        if not isinstance(palette, dict):
            errors.append(f"{label} 缺少 palette。")
        else:
            missing = REQUIRED_PALETTE - set(palette)
            if missing:
                errors.append(f"{label} 缺少颜色：{', '.join(sorted(missing))}。")
            for key, value in palette.items():
                if not isinstance(value, str) or not HEX.match(value):
                    errors.append(f"{label} 颜色 {key}={value!r} 不是 #RRGGBB。")
            if all(isinstance(palette.get(key), str) and HEX.match(palette[key]) for key in ("text", "canvas")):
                ratio = contrast(palette["text"], palette["canvas"])
                if ratio < 7:
                    errors.append(f"{label} 主文字与画布对比度只有 {ratio:.2f}:1，低于 7:1。")

        components = theme.get("components")
        if not isinstance(components, dict):
            errors.append(f"{label} 缺少 components。")
        else:
            missing = REQUIRED_COMPONENTS - set(components)
            if missing:
                errors.append(f"{label} 缺少组件配方：{', '.join(sorted(missing))}。")

        backgrounds = theme.get("backgrounds")
        if not isinstance(backgrounds, list) or not backgrounds:
            errors.append(f"{label} 至少需要一个背景资产。")
            continue
        roles = {item.get("role") for item in backgrounds if isinstance(item, dict)}
        if "portrait-master" not in roles:
            errors.append(f"{label} 缺少 portrait-master 背景。")
        for item in backgrounds:
            if not isinstance(item, dict):
                errors.append(f"{label} 存在无效背景记录。")
                continue
            relative = item.get("file")
            if not isinstance(relative, str) or not relative:
                errors.append(f"{label} 背景缺少文件路径。")
                continue
            resolved = (catalog_root / relative).resolve()
            try:
                resolved.relative_to(catalog_root)
            except ValueError:
                errors.append(f"{label} 背景越出主题目录：{relative}。")
                continue
            if item.get("status") == "generated":
                generated_images += 1
                if not resolved.is_file():
                    errors.append(f"{label} 已生成背景不存在：{relative}。")
                    continue
                try:
                    width, height = png_dimensions(resolved)
                except ValueError as exc:
                    errors.append(f"{label} 背景 {relative}：{exc}。")
                    continue
                dimensions[relative] = f"{width}x{height}"
                if width < 900 or height < 600:
                    errors.append(f"{label} 背景 {relative} 分辨率过低：{width}x{height}。")
                if item.get("role") == "portrait-master" and height <= width:
                    errors.append(f"{label} 竖版母图不是纵向：{width}x{height}。")

    if catalog.get("default_theme") not in ids:
        errors.append("default_theme 没有对应主题。")

    metrics["themes"] = len(themes)
    metrics["generated_images"] = generated_images
    metrics["dimensions"] = dimensions
    if errors:
        print(f"[FAIL] {catalog_path}")
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"[PASS] {catalog_path}")
    for key, value in metrics.items():
        print(f"METRIC: {key}={json.dumps(value, ensure_ascii=False)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Validate that a writing deliverable exists, opens, and meets hard checks."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse


TEXT_SUFFIXES = {".md", ".txt", ".html", ".htm", ".json", ".yaml", ".yml", ".csv"}
OFFICE_MEMBERS = {
    ".docx": "word/document.xml",
    ".pptx": "ppt/presentation.xml",
    ".xlsx": "xl/workbook.xml",
}
MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
URL_RE = re.compile(r"https?://[^\s)\]>'\"]+")
HAN_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]")
WECHAT_FORBIDDEN = (
    (re.compile(r"<!doctype\b", re.IGNORECASE), "公众号正文不能包含 DOCTYPE。"),
    (re.compile(r"</?(?:html|head|body)\b", re.IGNORECASE), "公众号正文不能包含完整网页外壳。"),
    (re.compile(r"<(?:style|script|link)\b", re.IGNORECASE), "公众号正文不能包含 style/script/link。"),
    (re.compile(r"</?div\b", re.IGNORECASE), "公众号正文请用 section，不要使用 div。"),
    (re.compile(r"\sclass\s*=", re.IGNORECASE), "class 会被平台过滤，请使用内联样式。"),
    (re.compile(r"\sid\s*=", re.IGNORECASE), "id 会被平台过滤。"),
    (re.compile(r"@(?:media|keyframes|import)\b", re.IGNORECASE), "公众号正文不支持 CSS 规则块。"),
    (re.compile(r"display\s*:\s*grid", re.IGNORECASE), "公众号正文不支持 display:grid。"),
    (re.compile(r"var\s*\(\s*--", re.IGNORECASE), "公众号正文不支持 CSS 变量。"),
    (re.compile(r"position\s*:\s*(?:fixed|absolute|sticky)", re.IGNORECASE), "公众号正文不支持该 position 值。"),
    (re.compile(r"float\s*:", re.IGNORECASE), "公众号正文不支持 float。"),
    (re.compile(r"<h1\b", re.IGNORECASE), "公众号平台标题应单独填写，正文不要重复 h1。"),
)


class LinkCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self.resources: list[str] = []

    def handle_starttag(self, tag: str, attrs):
        for key, value in attrs:
            if key in {"href", "src"} and value:
                self.links.append(value)
                if key == "src" or (tag == "link" and key == "href"):
                    self.resources.append(value)


class WechatFragmentChecker(HTMLParser):
    """Collect structural facts for a paste-ready WeChat HTML fragment."""

    VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "meta", "param", "source", "track", "wbr"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, bool]] = []
        self.root_tags: list[str] = []
        self.root_attrs: dict[str, str | None] = {}
        self.leaf_depth = 0
        self.leaf_count = 0
        self.paragraph_count = 0
        self.unwrapped: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        lowered = tag.lower()
        attr_map = dict(attrs)
        if not self.stack:
            self.root_tags.append(lowered)
            if len(self.root_tags) == 1:
                self.root_attrs = attr_map
        is_leaf = lowered == "span" and "leaf" in attr_map
        if is_leaf:
            self.leaf_depth += 1
            self.leaf_count += 1
        if lowered == "p":
            self.paragraph_count += 1
        if lowered not in self.VOID_TAGS:
            self.stack.append((lowered, is_leaf))

    def handle_startendtag(self, tag: str, attrs) -> None:
        if not self.stack:
            self.root_tags.append(tag.lower())

    def handle_endtag(self, tag: str) -> None:
        lowered = tag.lower()
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == lowered:
                for _, was_leaf in self.stack[index:]:
                    if was_leaf:
                        self.leaf_depth -= 1
                del self.stack[index:]
                return

    def handle_data(self, data: str) -> None:
        text = data.strip()
        if text and self.leaf_depth == 0:
            self.unwrapped.append(text[:30] + ("…" if len(text) > 30 else ""))


def validate_wechat_fragment(
    text: str,
    errors: list[str],
    warnings: list[str],
    metrics: dict[str, int | str],
) -> None:
    stripped = text.strip()
    if not re.match(r"^<section\b", stripped, flags=re.IGNORECASE) or not re.search(
        r"</section>\s*$", stripped, flags=re.IGNORECASE
    ):
        errors.append("公众号粘贴版必须是单一根 <section> 片段。")

    for pattern, message in WECHAT_FORBIDDEN:
        hits = len(pattern.findall(text))
        if hits:
            errors.append(f"{message}（命中 {hits} 处）")

    checker = WechatFragmentChecker()
    try:
        checker.feed(text)
    except Exception as exc:
        errors.append(f"公众号 HTML 解析失败：{exc}")
        return

    metrics["wechat_root_elements"] = len(checker.root_tags)
    metrics["wechat_leaf_spans"] = checker.leaf_count
    metrics["wechat_paragraphs"] = checker.paragraph_count
    if checker.root_tags != ["section"]:
        errors.append(f"公众号正文必须且只能有一个 section 根元素，实际为：{checker.root_tags or '无'}。")
    if "style" not in checker.root_attrs:
        errors.append("公众号正文根 section 缺少内联 style。")
    if checker.leaf_count == 0:
        errors.append('公众号正文缺少 <span leaf=""> 文字包裹。')
    if checker.unwrapped:
        sample = "；".join(f"「{item}」" for item in checker.unwrapped[:5])
        errors.append(f"发现 {len(checker.unwrapped)} 处可见文字未被 <span leaf> 包裹，例如：{sample}。")
    if checker.paragraph_count == 0:
        warnings.append("公众号正文没有 p 段落，请人工确认是否为纯图片或异常结构。")

    remote_images = re.findall(
        r"<img\b[^>]*\bsrc\s*=\s*['\"](?:https?:)?//[^'\"]+['\"]",
        text,
        flags=re.IGNORECASE,
    )
    if remote_images:
        warnings.append(f"发现 {len(remote_images)} 个远程图片；发布前确认已进入公众号可用图床。")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def read_utf8(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"不是严格 UTF-8：{exc}") from exc


def extract_links(path: Path, text: str) -> tuple[list[str], list[str]]:
    if path.suffix.lower() == ".md":
        links = [match.group(1).strip().strip("<>") for match in MARKDOWN_LINK_RE.finditer(text)]
        return links, []
    if path.suffix.lower() in {".html", ".htm"}:
        parser = LinkCollector()
        parser.feed(text)
        return parser.links, parser.resources
    return [], []


def is_remote_or_virtual(target: str) -> bool:
    lowered = target.lower()
    return (
        lowered.startswith(("http://", "https://", "mailto:", "tel:", "data:", "javascript:"))
        or target.startswith("#")
    )


def resolve_local_link(base: Path, target: str) -> Path:
    target = unquote(target.split("#", 1)[0].split("?", 1)[0])
    target = re.sub(r":\d+$", "", target)
    candidate = Path(target)
    return candidate if candidate.is_absolute() else (base / candidate).resolve()


def validate_binary_format(path: Path, errors: list[str]) -> None:
    suffix = path.suffix.lower()
    if suffix in OFFICE_MEMBERS:
        if not zipfile.is_zipfile(path):
            errors.append(f"{suffix} 不是有效 ZIP/Office 容器。")
            return
        with zipfile.ZipFile(path) as archive:
            bad_member = archive.testzip()
            if bad_member:
                errors.append(f"Office 容器中存在损坏成员：{bad_member}。")
            if OFFICE_MEMBERS[suffix] not in archive.namelist():
                errors.append(f"缺少 {OFFICE_MEMBERS[suffix]}，文件类型与扩展名不符。")
    elif suffix == ".pdf":
        if not path.read_bytes().startswith(b"%PDF-"):
            errors.append("PDF 文件头无效。")
    elif suffix == ".png":
        if not path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"):
            errors.append("PNG 文件头无效。")
    elif suffix in {".jpg", ".jpeg"}:
        data = path.read_bytes()
        if not (data.startswith(b"\xff\xd8") and data.endswith(b"\xff\xd9")):
            errors.append("JPEG 文件头或文件尾无效。")


def main() -> int:
    parser = argparse.ArgumentParser(description="校验曙光圆桌交付物。")
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--min-bytes", type=int, default=1)
    parser.add_argument("--min-han", type=int, default=0)
    parser.add_argument("--require-url", type=int, default=0)
    parser.add_argument("--required-text", action="append", default=[])
    parser.add_argument("--forbid", action="append", default=[], help="禁止出现的正则，可重复。")
    parser.add_argument("--forbid-file", type=Path, help="每行一个禁止正则，# 开头为注释。")
    parser.add_argument(
        "--expect-sha256",
        action="append",
        default=[],
        metavar="PATH=HASH",
        help="校验只读源文件未变化，可重复。",
    )
    parser.add_argument("--self-contained", action="store_true", help="HTML 不得引用远程资源。")
    parser.add_argument(
        "--wechat-fragment",
        action="store_true",
        help="按微信公众号可粘贴正文片段的硬契约校验 HTML。",
    )
    parser.add_argument(
        "--wechat-public-final",
        action="store_true",
        help="校验公众号公开终稿；包含片段检查，并禁止文末参考资料标题。",
    )
    parser.add_argument("--strict-warnings", action="store_true")
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args()

    path = args.artifact
    errors: list[str] = []
    warnings: list[str] = []
    metrics: dict[str, int | str] = {}
    text: str | None = None

    if not path.is_file():
        errors.append(f"交付物不存在：{path}")
    else:
        size = path.stat().st_size
        metrics["bytes"] = size
        if size < args.min_bytes:
            errors.append(f"文件只有 {size} 字节，低于要求的 {args.min_bytes} 字节。")
        if path.suffix.lower() in TEXT_SUFFIXES:
            try:
                text = read_utf8(path)
            except ValueError as exc:
                errors.append(str(exc))
        else:
            validate_binary_format(path, errors)

    patterns = list(args.forbid)
    if args.forbid_file:
        if not args.forbid_file.is_file():
            errors.append(f"风险词文件不存在：{args.forbid_file}")
        else:
            try:
                pattern_text = read_utf8(args.forbid_file)
            except ValueError as exc:
                errors.append(f"风险词文件{exc}")
            else:
                patterns.extend(
                    line.strip()
                    for line in pattern_text.splitlines()
                    if line.strip() and not line.lstrip().startswith("#")
                )

    if text is not None:
        han_count = len(HAN_RE.findall(text))
        url_count = len(URL_RE.findall(text))
        metrics["han_chars"] = han_count
        metrics["urls"] = url_count
        if han_count < args.min_han:
            errors.append(f"汉字数 {han_count}，低于要求的 {args.min_han}。")
        if url_count < args.require_url:
            errors.append(f"URL 数 {url_count}，低于要求的 {args.require_url}。")
        for required in args.required_text:
            if required not in text:
                errors.append(f"缺少必要文本：{required!r}。")
        for pattern in patterns:
            try:
                if re.search(pattern, text, flags=re.MULTILINE):
                    errors.append(f"命中禁止正则：{pattern}")
            except re.error as exc:
                errors.append(f"无效禁止正则 {pattern!r}：{exc}")

        links, resources = extract_links(path, text)
        remote_resources = [
            link
            for link in resources
            if link.lower().startswith(("http://", "https://", "//"))
        ]
        missing_links: list[str] = []
        for link in links:
            if is_remote_or_virtual(link):
                continue
            if not resolve_local_link(path.parent, link).exists():
                missing_links.append(link)
        if missing_links:
            errors.append("本地链接不存在：" + ", ".join(sorted(set(missing_links))))
        if args.self_contained and path.suffix.lower() in {".html", ".htm"} and remote_resources:
            errors.append("自包含 HTML 仍引用远程资源：" + ", ".join(sorted(set(remote_resources))))

        not_but_lines = sum(
            1
            for line in text.splitlines()
            if re.search(r"不是.+而是|不是因为.+而", line)
        )
        heading_count = sum(1 for line in text.splitlines() if re.match(r"^#{1,6}\s", line))
        metrics["not_but_pattern_lines"] = not_but_lines
        metrics["headings"] = heading_count
        if not_but_lines >= 6:
            warnings.append(
                f"发现 {not_but_lines} 行‘不是……而是……’类结构；请人工判断是否形成模板腔。"
            )
        if han_count and heading_count >= 8 and han_count / heading_count < 180:
            warnings.append("标题密度较高；请人工检查文章是否被切得过碎。")
        if re.search(r"稍后可下载|下载链接占位|TODO|TBD", text, flags=re.IGNORECASE):
            warnings.append("发现疑似占位文本，请确认不是虚假交付。")
        if re.search(r"(?:[A-Za-z]:\\Users\\[^\\\s]+|/Users/[^/\s]+|/home/[^/\s]+)", text):
            warnings.append("正文中出现可能的私人绝对路径，发布前应复核。")
        if args.wechat_fragment or args.wechat_public_final:
            if path.suffix.lower() not in {".html", ".htm"}:
                errors.append("公众号 HTML 校验参数只能用于 HTML 文件。")
            else:
                validate_wechat_fragment(text, errors, warnings, metrics)
        if args.wechat_public_final:
            public_reference_heading = re.compile(
                r"<span\b[^>]*\bleaf(?:\s*=\s*['\"][^'\"]*['\"])?[^>]*>\s*"
                r"(?:参考资料|参考文献|References?|Sources?)\s*</span>",
                flags=re.IGNORECASE,
            )
            hits = len(public_reference_heading.findall(text))
            metrics["public_reference_headings"] = hits
            if hits:
                errors.append(
                    "公众号公开终稿仍包含参考资料标题；请把来源列表移到内部证据台账，"
                    "或改用 --wechat-fragment 并记录公开来源例外。"
                )

    for item in args.expect_sha256:
        if "=" not in item:
            errors.append(f"--expect-sha256 格式错误：{item!r}，应为 PATH=HASH。")
            continue
        source_text, expected = item.rsplit("=", 1)
        source = Path(source_text)
        if not source.is_file():
            errors.append(f"待核验源文件不存在：{source}")
            continue
        actual = sha256(source)
        if actual.upper() != expected.strip().upper():
            errors.append(f"源文件哈希变化：{source}，实际 {actual}。")
        else:
            metrics[f"source_sha256:{source}"] = actual

    passed = not errors and not (args.strict_warnings and warnings)
    result = {
        "status": "PASS" if passed else "FAIL",
        "artifact": str(path.resolve()),
        "metrics": metrics,
        "errors": errors,
        "warnings": warnings,
    }
    if args.json_output:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"[{result['status']}] {result['artifact']}")
        for key, value in metrics.items():
            print(f"METRIC: {key}={value}")
        for issue in errors:
            print(f"ERROR: {issue}")
        for issue in warnings:
            print(f"WARN: {issue}")
        if passed and not warnings:
            print("交付物存在、格式可读并通过全部指定硬检查。")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())

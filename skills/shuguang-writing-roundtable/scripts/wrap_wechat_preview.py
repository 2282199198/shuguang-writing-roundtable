#!/usr/bin/env python3
"""Wrap a paste-ready WeChat section fragment in a 390px local preview page."""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="生成带复制按钮的公众号手机预览页。")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--title", default="公众号手机预览")
    parser.add_argument("--width", type=int, default=390)
    args = parser.parse_args()
    if not 320 <= args.width <= 430:
        parser.error("--width 必须在 320 到 430 之间。")

    fragment = args.input.read_text(encoding="utf-8").strip()
    if not re.match(r"^<section\b", fragment, re.IGNORECASE) or not re.search(r"</section>$", fragment, re.IGNORECASE):
        parser.error("输入必须是单一 section 片段。")

    title = html.escape(args.title)
    document = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
body{{margin:0;background:#e9eaec;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei',sans-serif;-webkit-text-size-adjust:100%}}.bar{{position:fixed;top:0;left:0;right:0;height:54px;background:#fff;box-shadow:0 1px 10px rgba(0,0,0,.08);display:flex;align-items:center;justify-content:space-between;padding:0 16px;z-index:99}}.hint{{font-size:13px;color:#6b7280}}button{{background:#27272A;color:#fff;border:0;border-radius:9px;padding:10px 18px;font-size:14px;font-weight:700;cursor:pointer}}.toast{{position:fixed;top:66px;left:50%;transform:translateX(-50%);background:#111827;color:#fff;padding:10px 18px;border-radius:9px;font-size:13px;opacity:0;pointer-events:none;transition:opacity .2s;z-index:100}}.toast.show{{opacity:1}}.stage{{max-width:{args.width}px;margin:78px auto 64px;padding:16px 10px 1px;background:#fff;box-shadow:0 18px 48px rgba(39,39,42,.13);border-radius:14px}}@media(max-width:{args.width + 50}px){{.stage{{margin:70px 0 0;padding:14px 8px 1px;border-radius:0;box-shadow:none}}button{{padding:9px 12px}}}}
</style>
</head>
<body>
<div class="bar"><span class="hint"><b>{args.width}px 手机预览</b></span><button id="copyButton" onclick="copyWechat()">复制到公众号</button></div>
<div class="toast" id="toast"></div>
<div class="stage"><div id="wechatContent">{fragment}</div></div>
<script>
function showToast(message){{var toast=document.getElementById('toast');toast.textContent=message;toast.classList.add('show');clearTimeout(toast.timer);toast.timer=setTimeout(function(){{toast.classList.remove('show')}},2600)}}
function copyWechat(){{var node=document.getElementById('wechatContent');var range=document.createRange();range.selectNodeContents(node);var selection=window.getSelection();selection.removeAllRanges();selection.addRange(range);var ok=false;try{{ok=document.execCommand('copy')}}catch(error){{ok=false}}selection.removeAllRanges();var button=document.getElementById('copyButton');if(ok){{showToast('已复制，请粘贴到公众号编辑器并复查图片与段距');var old=button.textContent;button.textContent='已复制';setTimeout(function(){{button.textContent=old}},2200)}}else{{showToast('自动复制失败，请手动全选正文后复制')}}}}
</script>
</body>
</html>"""
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(document, encoding="utf-8")
    print(args.output.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Render a local visual gallery for the six fixed WeChat themes."""

from __future__ import annotations

import argparse
import html
import json
import os
from pathlib import Path


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def main() -> int:
    default_catalog = Path(__file__).resolve().parents[1] / "assets" / "wechat-themes" / "theme-catalog.json"
    parser = argparse.ArgumentParser(description="生成六套公众号主题的本地视觉总览。")
    parser.add_argument("--catalog", type=Path, default=default_catalog)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    catalog_path = args.catalog.resolve()
    output = (args.output or catalog_path.parent / "theme-gallery.html").resolve()
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    cards: list[str] = []

    for theme in catalog["themes"]:
        palette = theme["palette"]
        backgrounds = theme["backgrounds"]
        selected = next((item for item in backgrounds if item["role"] == "opening-banner"), backgrounds[0])
        image_path = (catalog_path.parent / selected["file"]).resolve()
        image_src = Path(os.path.relpath(image_path, output.parent)).as_posix()
        best_for = " · ".join(theme["route"]["best_for"])
        swatches = "".join(
            f'<span class="swatch"><i style="background:{esc(value)}"></i>{esc(key)} {esc(value)}</span>'
            for key, value in palette.items()
        )
        cards.append(
            f"""
<article class="theme-card" style="--canvas:{esc(palette['canvas'])};--text:{esc(palette['text'])};--body:{esc(palette['body'])};--muted:{esc(palette['muted'])};--primary:{esc(palette['primary'])};--accent:{esc(palette['accent'])};--card:{esc(palette['card'])};--line:{esc(palette['line'])}">
  <div class="theme-meta">
    <div><span class="index">{len(cards)+1:02d}</span><h2>{esc(theme['name_cn'])}</h2><code>{esc(theme['id'])}</code></div>
    <p>{esc(theme['positioning'])}</p>
    <p class="route">适用：{esc(best_for)}</p>
    <div class="swatches">{swatches}</div>
  </div>
  <div class="phone">
    <img src="{esc(image_src)}" alt="{esc(theme['name_cn'])}背景">
    <div class="paper">
      <small>SHUGUANG ROUNDTABLE</small>
      <h3>世界一直换题，真正值得提前准备的是什么？</h3>
      <p>固定主题先服务内容，再服务好看。正文即使没有背景图片，也能保持清楚、可信和可读。</p>
      <blockquote>把最重要的判断留给读者，把装饰留在边缘。</blockquote>
      <h4>一个清楚的小标题</h4>
      <p>同一篇只使用一套主题，章节、小标题和正文维持三层视觉结构。</p>
    </div>
  </div>
</article>"""
        )

    document = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(catalog['pack_name'])}</title>
<style>
*{{box-sizing:border-box}}body{{margin:0;background:#efefec;color:#202124;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei',sans-serif}}header{{max-width:1180px;margin:0 auto;padding:52px 24px 28px}}header h1{{font-size:36px;margin:0 0 12px}}header p{{color:#666;line-height:1.7;margin:0;max-width:760px}}main{{max-width:1180px;margin:0 auto;padding:0 24px 64px;display:grid;gap:28px}}.theme-card{{display:grid;grid-template-columns:minmax(0,1fr) 390px;gap:34px;align-items:center;background:white;border-radius:20px;padding:32px;box-shadow:0 14px 40px rgba(0,0,0,.07)}}.theme-meta h2{{display:inline-block;font-size:28px;margin:0 12px 8px 0;color:var(--text)}}.theme-meta code{{color:var(--muted)}}.theme-meta p{{color:var(--body);line-height:1.7}}.theme-meta .route{{font-size:14px}}.index{{display:block;font-size:56px;font-weight:900;color:var(--line);line-height:1}}.swatches{{display:flex;flex-wrap:wrap;gap:8px;margin-top:18px}}.swatch{{font-size:11px;color:#666;background:#f7f7f7;padding:6px 8px;border-radius:8px}}.swatch i{{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:5px;border:1px solid rgba(0,0,0,.08)}}.phone{{width:390px;background:var(--canvas);border:1px solid var(--line);border-radius:18px;overflow:hidden;box-shadow:0 12px 30px rgba(0,0,0,.11)}}.phone img{{display:block;width:100%;height:150px;object-fit:cover}}.paper{{padding:24px 22px 28px;background:var(--canvas)}}.paper small{{color:var(--muted);letter-spacing:2px}}.paper h3{{font-size:21px;line-height:1.45;color:var(--text);margin:10px 0 20px}}.paper p{{font-size:15px;line-height:1.8;color:var(--body);margin:0 0 18px}}.paper blockquote{{margin:24px 0;padding:14px 0 14px 18px;border-left:3px solid var(--primary);color:var(--text);font-weight:700;line-height:1.7;background:var(--card)}}.paper h4{{font-size:16px;color:var(--text);border-left:3px solid var(--primary);padding-left:10px;margin:26px 0 12px}}@media(max-width:820px){{header h1{{font-size:28px}}.theme-card{{grid-template-columns:1fr;padding:22px}}.phone{{width:100%;max-width:390px;margin:auto}}}}
</style>
</head>
<body>
<header><h1>{esc(catalog['pack_name'])}</h1><p>六套主题按内容任务路由。图片是可选增强层；真正复制到公众号的正文仍依赖内联排版，不依赖背景才能成立。</p></header>
<main>{''.join(cards)}</main>
</body>
</html>"""
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(document, encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

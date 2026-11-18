#!/usr/bin/env python3
"""Generate a standalone icon review page without changing game assets."""
import argparse
import base64
import html
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from modmeta import mod_id
from inventory import collect


def image_tag(path: Path, size: int) -> str:
    data = base64.b64encode(path.read_bytes()).decode('ascii')
    return (f'<img width="{size}" height="{size}" src="data:image/png;base64,{data}" '
            f'alt="{html.escape(path.stem, quote=True)}">')


def render_icon(row: dict, images: Path, before: Path | None) -> str:
    path = images / (row['resource'] + '.png')
    size = row['logical_px']
    panes = [f'<div class="{theme}">{image_tag(path, size)}<small>基准 {size}px</small></div>'
             for theme in ('dark', 'light')]
    for zoom, label in ((24, '24px 压力预览'), (128, '128px 放大检查')):
        panes.append(f'<div class="dark">{image_tag(path, zoom)}<small>{label}</small></div>')
    outline = path.with_stem(path.stem + '_outline')
    if outline.is_file():
        panes.append(f'<div class="dark">{image_tag(outline, size)}<small>描边原图</small></div>')
        panes.append(f'<div class="light"><span class="stack" style="width:{size}px;height:{size}px">'
                     f'<span class="outline">{image_tag(outline, size)}</span>{image_tag(path, size)}'
                     '</span><small>黑色半透明描边叠加</small></div>')
    previous = before / (row['resource'] + '.png') if before else None
    if previous and previous.is_file():
        panes.append(f'<div class="dark">{image_tag(previous, size)}<small>修改前 {size}px</small></div>')
    return (f'<article><h2>{html.escape(row["name"])}</h2><code>{html.escape(row["resource"])}</code>'
            f'<p>{html.escape(row["status"])}：{html.escape(row["note"])}</p>'
            f'<section>{"".join(panes)}</section></article>')


def write_page(output: Path, rows: list[dict], images: Path, before: Path | None, title: str) -> None:
    title = html.escape(title)
    document = f'''<!doctype html><html lang="zh"><meta charset="utf-8"><title>{title}</title>
<style>body{{font:16px sans-serif;background:#191b24;color:#eee;margin:24px}}article{{border-top:1px solid #555;padding:16px 0}}h2{{font-size:18px}}section{{display:flex;gap:12px;flex-wrap:wrap}}section>div{{padding:12px;min-width:90px;display:flex;align-items:center;justify-content:center;flex-direction:column}}small{{margin-top:8px;font-size:12px}}.dark{{background:#242534;color:#ddd}}.light{{background:#eee9dc;color:#222}}.stack{{position:relative;display:block}}.stack>img,.outline{{position:absolute;inset:0}}.outline{{filter:brightness(0);opacity:.5}}img{{object-fit:contain}}code{{font-size:12px}}</style>
<h1>{title}</h1><p>基准逻辑像素：Power 40、遗物／药水 60、附魔 35；能量图以 _text 结尾时使用 24，其余使用 64。屏幕显示另受 UI 缩放、字体与动画影响。本页不模拟游戏着色器、数字遮挡或悬停大图。</p>'''
    document += ''.join(render_icon(row, images, before) for row in rows) + '</html>\n'
    output.mkdir(parents=True, exist_ok=True)
    (output / 'index.html').write_text(document, encoding='utf-8')
    (output / 'inventory.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--images', type=Path, help='images 目录；默认读取当前模组的 assets')
    parser.add_argument('--language', default='zhs', help='名称本地化语言；默认 zhs')
    parser.add_argument('--before', type=Path, help='修改前 images 目录，保留 powers/relics 等子目录')
    parser.add_argument('--review', type=Path, help='按 folder/stem 索引的人工判断 JSON')
    args = parser.parse_args()
    identity = mod_id(ROOT)
    images = args.images or ROOT / 'assets' / identity / 'images'
    reviews = json.loads(args.review.read_text(encoding='utf-8')) if args.review else {}
    rows = collect(ROOT, images, args.language, reviews)
    if not rows:
        parser.error(f'没有找到图标，请先生成素材或用 --images 指定目录：{images}')
    write_page(args.output, rows, images, args.before, f'{identity} 图标检查')
    print(f'图标检查页：{args.output / "index.html"}（{len(rows)} 项）')


if __name__ == '__main__':
    main()

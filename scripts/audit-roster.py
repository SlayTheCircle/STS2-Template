#!/usr/bin/env python3
"""核对公开设计卡表、中文标题与内容类；不验证数值或升级行为。
默认读取 docs/history/design/card-roster.txt（原案档案），ROSTER_DESIGN_FILE 可覆盖。
已确认的原案外新增内容单独声明，缺失或空表应失败。"""
import argparse, json, os, re, sys
from pathlib import Path

from content.models import ContentIndex

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--release', action='store_true', help='候选发行物不允许原案延后项')
args = parser.parse_args()
DOC = os.environ.get('ROSTER_DESIGN_FILE') or os.path.join(ROOT, 'docs', 'history', 'design', 'card-roster.txt')
if not os.path.isfile(DOC):
    print(f'错误: 找不到设计花名册 {DOC}')
    sys.exit(1)

policy = json.loads((Path(ROOT) / 'docs/history/design/roster-policy.json').read_text(encoding='utf-8'))
DEFERRED = set(policy['deferred'])
TOKENS = set(policy['tokens'])
ADDITIONS = set(policy['additions'])

names = []
for line in open(DOC, encoding='utf-8'):
    m = re.match(r'^(.+?)（(攻击|技能|能力)）', line.strip())
    if m:
        names.append(m.group(1))
design = set(names)
if not design:
    print('错误: 设计花名册没有可解析的卡牌条目')
    sys.exit(1)
if len(names) != len(design):
    dup = {n for n in names if names.count(n) > 1}
    print(f'错误: 设计文档重名 {dup}')
    sys.exit(1)

loc = json.load(open(os.path.join(ROOT, 'localization', 'zhs', 'cards.json'), encoding='utf-8'))
titles = {v for k, v in loc.items() if k.endswith('.title')}
cls_n = len(ContentIndex(Path(ROOT)).family('card'))

errors = []
if DEFERRED - design:
    errors.append(f'延后项不在原案花名册: {sorted(DEFERRED - design)}')
if DEFERRED & titles:
    errors.append(f'已实装项应从延后清单移除: {sorted(DEFERRED & titles)}')
if args.release and DEFERRED:
    errors.append(f'候选发行物仍有延后项: {sorted(DEFERRED)}')
if len(titles) != cls_n:
    errors.append(f'类文件 {cls_n} ↔ loc 标题 {len(titles)} 不齐(有类没 loc 或反之)')
ghost = titles - design - TOKENS - ADDITIONS
if ghost:
    errors.append(f'实装了但不在设计表/白名单: {sorted(ghost)}')
pending = design - titles
unexpected = pending - DEFERRED
if unexpected:
    errors.append(f'未实装且不在缓做清单(在途批次落地后应清零): {sorted(unexpected)}')

for e in errors:
    print('错误:', e)
print(f'花名册: 原案 {len(design)} / 原案已实装 {len(titles & design)} / 延后 {len(DEFERRED)} / 新增 {sorted(titles & ADDITIONS)} / token {sorted(TOKENS)}')
if errors:
    sys.exit(1)
print('花名册审计通过')

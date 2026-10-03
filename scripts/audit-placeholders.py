#!/usr/bin/env python3
"""核对本卡变量消费、计算依赖和双语文本占位符；不验证结算行为。"""
import json
import re
from pathlib import Path

import modmeta
from content.models import ContentIndex
from content.variables import variable_contract

ROOT = Path(__file__).resolve().parent.parent
PREFIX = modmeta.loc_prefix(ROOT)
index = ContentIndex(ROOT)
errors = []
varmap = {}
for model in index.family('card'):
    keys, problems = variable_contract(index.lineage(model))
    entry = PREFIX + 'CARD_' + modmeta.public_stem(model.name)
    varmap[entry] = keys
    errors.extend(f'{model.name}: {problem}' for problem in problems)

for lang in ('zhs', 'eng'):
    cards = json.loads((ROOT / f'localization/{lang}/cards.json').read_text(encoding='utf-8'))
    for key, text in cards.items():
        if not key.endswith('.description'):
            continue
        entry = key.split('.')[0]
        if entry not in varmap:
            errors.append(f'[{lang}] {entry}: 未找到对应卡牌类，无法检查占位符')
            continue
        used = set(re.findall(r'\{(\w+)(?::[^}]*)?\}', text)) - {'InCombat'}
        missing = used - varmap[entry]
        if missing:
            errors.append(f'[{lang}] {entry}: 文本消费未声明键 {sorted(missing)}')

for error in errors:
    print('错误:', error)
if errors:
    raise SystemExit(1)
print(f'变量与占位符审计通过({len(varmap)} 卡 × zhs/eng)')

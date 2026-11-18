#!/usr/bin/env python3
"""Base 家族的具体模型须有双语复合键；抽象机制基类不单独要求文本。"""
import json
from pathlib import Path

import modmeta
from content.models import ContentIndex

ROOT = Path(__file__).resolve().parent.parent
PREFIX = modmeta.loc_prefix(ROOT)
index = ContentIndex(ROOT)
errors, warnings = [], []
families = [
    ('card', 'cards', 'CARD', ['title', 'description']),
    ('power', 'powers', 'POWER', ['title', 'description', 'smartDescription']),
    ('relic', 'relics', 'RELIC', ['title', 'description']),
    ('potion', 'potions', 'POTION', ['title', 'description']),
    ('support_enchantment', 'enchantments', 'ENCHANTMENT', ['title', 'description', 'extraCardText']),
]
for kind, table, category, fields in families:
    for lang in ('zhs', 'eng'):
        values = json.loads((ROOT / f'localization/{lang}/{table}.json').read_text(encoding='utf-8'))
        for model in index.family(kind):
            entry = PREFIX + category + '_' + modmeta.public_stem(model.name)
            for field in fields:
                if entry + '.' + field not in values:
                    errors.append(f'[{lang}] {model.name} 缺 {entry}.{field}')
            if kind == 'relic' and entry + '.flavor' not in values:
                warnings.append(f'[{lang}] {model.name} 缺 {entry}.flavor')

for warning in warnings:
    print('警告:', warning)
for error in errors:
    print('错误:', error)
if errors:
    raise SystemExit(1)
print(f'本地化覆盖审计通过(警告 {len(warnings)} 条)')

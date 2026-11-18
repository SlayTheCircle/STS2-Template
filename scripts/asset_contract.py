"""Base 家族要求的自有纹理与额外 PCK 断言；供存在性审计和包内验证共用。"""
import json
import sys
from pathlib import Path

import modmeta
from content.models import ContentIndex
from content.cards import card_fields


def textures(root: Path) -> list[dict]:
    mod_id, short = modmeta.mod_id(root), modmeta.short(root)
    index = ContentIndex(root)
    result = {}
    families = [('card', 'cards', ('',)),
                ('relic', 'relics', ('', '_outline')),
                ('potion', 'potions', ('', '_outline')),
                ('power', 'powers', ('',)),
                ('support_enchantment', 'enchantments', ('',))]
    for kind, asset_folder, slots in families:
        for model in index.family(kind):
            size = [256, 256]
            if kind == 'card':
                rarity = card_fields(index.lineage(model))[2]
                size = [606, 852] if rarity == 'Ancient' else [750, 570]
            for slot in slots:
                name = model.name + slot
                if kind == 'support_enchantment' and not (root / f'assets/{mod_id}/images/enchantments/{model.name}.png').is_file():
                    name = short.lower() + '_support'
                relative = f'{mod_id}/images/{asset_folder}/{name}.png'
                result[relative] = {'path': 'res://' + relative, 'size': size,
                                    'transparent': kind == 'support_enchantment'}
    extra = root / 'assets/validation.json'
    if extra.exists():
        for path, options in json.loads(extra.read_text())['textures'].items():
            if not path.startswith('res://'):
                raise ValueError('PCK 纹理断言必须使用 res:// 路径')
            result[path] = {'path': path, **options}
    return list(result.values())


def contract(root: Path) -> dict:
    extra = root / 'assets/validation.json'
    files = json.loads(extra.read_text()).get('files', []) if extra.exists() else []
    return {'textures': textures(root), 'files': files}


if __name__ == '__main__':
    root = Path(sys.argv[1]).resolve()
    print(json.dumps(contract(root), ensure_ascii=False))

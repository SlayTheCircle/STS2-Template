"""Discover icon resources and their localized names using the mod's manifest identity."""
import json
from pathlib import Path

from modmeta import loc_prefix, public_stem

SIZES = {'powers': 40, 'relics': 60, 'potions': 60, 'enchantments': 35}
KINDS = {'powers': 'POWER', 'relics': 'RELIC', 'potions': 'POTION', 'enchantments': 'ENCHANTMENT'}


def collect(root: Path, images: Path, language: str, reviews: dict) -> list[dict]:
    prefix = loc_prefix(root)
    rows = []
    for folder in (*SIZES, 'energy'):
        table = root / 'localization' / language / f'{folder}.json'
        names = json.loads(table.read_text(encoding='utf-8')) if table.is_file() else {}
        for path in sorted((images / folder).glob('*.png')):
            if path.stem.endswith('_outline'):
                continue
            key = f'{folder}/{path.stem}'
            kind = KINDS.get(folder)
            title_key = f'{prefix}{kind}_{public_stem(path.stem)}.title'
            size = SIZES.get(folder, 24 if path.stem.endswith('_text') else 64)
            review = reviews.get(key, {})
            rows.append({'resource': key, 'name': names.get(title_key, path.stem),
                         'logical_px': size, 'status': review.get('status', '待检查'),
                         'note': review.get('note', '')})
    return rows

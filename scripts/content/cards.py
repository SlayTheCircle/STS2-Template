"""从卡牌继承链的约定声明读取费用、类型和稀有度。"""
import re

from .members import property_body

CTOR = re.compile(r':\s*base\(\s*(-?\d+)\s*,\s*CardType\.(\w+)\s*,\s*CardRarity\.(\w+)')


def card_fields(lineage) -> tuple[str, str, str]:
    for model in lineage:
        if re.search(r':\s*base\s*\(', model.source):
            match = CTOR.search(model.source)
            if not match:
                raise ValueError(f'{lineage[0].name}: {model.name} 的构造参数无法静态导表；'
                                 '费用/类型/稀有度使用字面声明，或扩展 content/cards.py')
            cost, card_type, rarity = match.groups()
            break
    else:
        raise ValueError(f'{lineage[0].name}: 未找到卡牌构造声明')
    for model in lineage:
        x_cost = property_body(model.source, 'HasEnergyCostX')
        if x_cost is not None:
            if x_cost.strip() not in ('true', 'false'):
                raise ValueError(f'{model.name}: HasEnergyCostX 使用字面 true/false 以供导表')
            if x_cost.strip() == 'true':
                cost = 'X'
            break
    return cost, card_type, rarity

"""CanonicalVars、计算依赖及本卡 DynamicVars 消费键的静态契约。"""
import re

from .members import expression_end, property_body

INTRINSIC = {
    'CalculationBaseVar': 'CalculationBase', 'CalculationExtraVar': 'CalculationExtra',
    'ExtraDamageVar': 'ExtraDamage', 'CalculatedDamageVar': 'CalculatedDamage',
    'CalculatedBlockVar': 'CalculatedBlock', 'DamageVar': 'Damage', 'BlockVar': 'Block',
    'CardsVar': 'Cards', 'EnergyVar': 'Energy', 'GoldVar': 'Gold', 'HealVar': 'Heal',
}
DEPENDENCIES = {
    'CalculatedVar': {'CalculationBase', 'CalculationExtra'},
    'CalculatedDamageVar': {'CalculationBase', 'ExtraDamage'},
    'CalculatedBlockVar': {'CalculationBase', 'CalculationExtra'},
}
NEW_VAR = re.compile(r'new\s+(\w*Var)(?:<(\w+)>)?\s*\(')
READ = re.compile(r'(?<![\w.])(?:(?:base|this)\.)?DynamicVars(?:\.(\w+)|\["([^"]+)"\])')


def declarations(lineage) -> str:
    for position, model in enumerate(lineage):
        body = property_body(model.source, 'CanonicalVars')
        if body is not None:
            if 'base.CanonicalVars' in body:
                body += '\n' + declarations(lineage[position + 1:])
            return body
    return ''


def variable_contract(lineage) -> tuple[set[str], list[str]]:
    body = declarations(lineage)
    keys = set()
    calculated = []
    for match in NEW_VAR.finditer(body):
        args_end = expression_end(body, match.end() - 1)
        args = body[match.end():args_end - 1].strip()
        explicit = re.match(r'"([^"]+)"', args)
        kind = match[1]
        if explicit:
            key = explicit[1]
        elif kind == 'PowerVar':
            key = match[2]
        else:
            key = INTRINSIC.get(kind)
        if key:
            keys.add(key)
        if kind in DEPENDENCIES:
            cursor = args_end
            methods = []
            while chain := re.match(r'\s*\.\s*(\w+)\s*\(', body[cursor:]):
                methods.append(chain[1])
                cursor = expression_end(body, cursor + chain.end() - 1)
            calculated.append((kind, methods))

    errors = []
    for kind, methods in calculated:
        missing = DEPENDENCIES[kind] - keys
        if missing:
            errors.append(f'{kind} 缺配套变量 {sorted(missing)}')
        if 'WithMultiplier' not in methods:
            errors.append(f'{kind} 未在 CanonicalVars 接入 WithMultiplier')

    # 只核对本卡的字面键和内建变量属性，不猜动态字符串或其他卡的变量。
    source = '\n'.join(model.source for model in lineage)
    for match in READ.finditer(source):
        key = match[2] or match[1]
        if (match[2] or key in INTRINSIC.values()) and key not in keys:
            errors.append(f'DynamicVars 消费未声明键 {key}')
    return keys, sorted(set(errors))

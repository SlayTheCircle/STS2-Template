"""读取约定写法中的成员正文与调用参数；不是 C# 语义分析器。"""
import re


def expression_end(source: str, start: int) -> int:
    depth = 0
    quoted = False
    escaped = False
    for offset in range(start, len(source)):
        char = source[offset]
        if quoted:
            if char == '"' and not escaped:
                quoted = False
            escaped = char == '\\' and not escaped
            continue
        if char == '"':
            quoted = True
        elif char in '([{':
            depth += 1
        elif char in ')]}':
            depth -= 1
            if depth == 0:
                return offset + 1
        elif char == ';' and depth == 0:
            return offset
    return len(source)


def property_body(source: str, name: str) -> str | None:
    match = re.search(r'\b' + re.escape(name) + r'\s*(=>|\{)', source)
    if not match:
        return None
    start = match.end() if match[1] == '=>' else match.end() - 1
    if match[1] == '=>':
        cursor = start
        while cursor < len(source):
            end = expression_end(source, cursor)
            if end == len(source) or source[end:end + 1] == ';':
                return source[start:end]
            cursor = end
    return source[start:expression_end(source, start)]

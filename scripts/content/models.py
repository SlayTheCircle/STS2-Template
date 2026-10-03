"""按 Base 家族的传递继承发现具体内容；不依赖文件所在子目录。"""
from dataclasses import dataclass
from pathlib import Path
import re

import modmeta


# 字符串保持原样，避免把 res:// 或文本中的 // 当成注释。
TOKENS = re.compile(r'@"(?:""|[^"])*"|"(?:\\.|[^"\\])*"|//[^\n]*|/\*[\s\S]*?\*/')
CLASS = re.compile(r'(?P<modifiers>(?:(?:public|internal|protected|private|abstract|sealed|partial|static)\s+)*)'
                   r'class\s+(?P<name>\w+)(?:<[^>]+>)?\s*:\s*(?P<parent>[\w.:]+)')


def without_comments(source: str) -> str:
    return TOKENS.sub(lambda m: ' ' if m[0].startswith('/') else m[0], source)


@dataclass(frozen=True)
class Model:
    name: str
    parent: str
    abstract: bool
    path: Path
    source: str


class ContentIndex:
    def __init__(self, root: Path):
        self.root = root
        self.classes: dict[str, Model] = {}
        for path in sorted((modmeta.src_dir(root) / 'Content').rglob('*.cs')):
            source = without_comments(path.read_text(encoding='utf-8'))
            for match in CLASS.finditer(TOKENS.sub(' ', source)):
                name = match['name']
                if name in self.classes:
                    raise ValueError(f'内容类名重复: {name} ({path})')
                self.classes[name] = Model(name, match['parent'].split('.')[-1].split('::')[-1],
                                           'abstract' in match['modifiers'].split(), path, source)

    def lineage(self, model: Model) -> list[Model]:
        result = [model]
        while result[-1].parent in self.classes:
            parent = self.classes[result[-1].parent]
            if parent in result:
                raise ValueError(f'继承循环: {model.name}')
            result.append(parent)
        return result

    def family(self, kind: str) -> list[Model]:
        base = modmeta.base_class(self.root, kind)
        return [model for model in self.classes.values()
                if not model.abstract and any(item.parent == base for item in self.lineage(model))]

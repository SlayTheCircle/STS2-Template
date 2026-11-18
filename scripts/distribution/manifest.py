"""让平铺安装目录声明实际内容 DLL 的编译目标；不改源码清单。"""
import json
from pathlib import Path
import sys


def write(source: Path, destination: Path, target: str) -> None:
    manifest = json.loads(source.read_text(encoding='utf-8'))
    manifest['min_game_version'] = target
    destination.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    write(Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3])

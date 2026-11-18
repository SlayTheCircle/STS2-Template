"""仅改写派生身份，保留模板来源与脚手架。"""
import datetime
import hashlib
import json
import re
import subprocess
from pathlib import Path

from modmeta import public_stem


def tracked_files() -> list[str]:
    return subprocess.check_output(['git', 'ls-files', '-z']).decode().strip('\0').split('\0')


def snapshot_digest(files: list[str]) -> str:
    digest = hashlib.sha256()
    for name in sorted(files):
        path = Path(name)
        digest.update(name.encode() + b'\0' + path.read_bytes() + b'\0')
    return digest.hexdigest()


def rename(mod_id: str, short: str) -> None:
    files = tracked_files()
    origin = Path('.template-origin')
    lineage = json.loads(origin.read_text())
    head = subprocess.run(['git', 'rev-parse', '--verify', 'HEAD'], capture_output=True, text=True)
    lineage.update(snapshotCommit=head.stdout.strip() if head.returncode == 0 else None,
                   snapshotDigest=snapshot_digest(files), derived=mod_id,
                   derivedAt=datetime.date.today().isoformat())
    origin.write_text(json.dumps(lineage, ensure_ascii=False, indent=2) + '\n')

    def move(old: str, new: str) -> None:
        subprocess.run(['git', 'mv', old, new], check=True)

    move('STS2-Template.json', f'{mod_id}.json')
    for suffix in ('', '.Loader'):
        move(f'src/STS2-Template{suffix}', f'src/{mod_id}{suffix}')
        move(f'src/{mod_id}{suffix}/STS2-Template{suffix}.csproj',
             f'src/{mod_id}{suffix}/{mod_id}{suffix}.csproj')
    for name in tracked_files():
        path = Path(name)
        if re.fullmatch(r'Template\w*\.cs', path.name):
            move(name, str(path.with_name(short + path.name[len('Template'):])))
    if Path('assets/STS2-Template').exists():
        move('assets/STS2-Template', f'assets/{mod_id}')

    for name in tracked_files():
        path = Path(name)
        if name == '.template-origin' or name == 'scripts/init-mod.sh' or name.startswith(('templates/', 'scripts/derivation/')):
            continue
        try:
            text = path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            continue
        # 上游来源标识不可改写；保护整段 URL，随后只替换本仓身份。
        urls = []
        def protect(match):
            urls.append(match[0])
            return f'@@UPSTREAM_URL_{len(urls)-1}@@'
        text = re.sub(r'https://github\.com/SlayTheCircle/STS2-Template[^\s)"<>]*', protect, text)
        text = text.replace('SlayTheCircle/STS2-Template', '@@UPSTREAM_REPO@@')
        text = text.replace('STS2-Template', mod_id)
        # JSON 的复合键和 PowerVar 类名分开处理；规范与 RitsuLib 一致。
        if path.suffix == '.json':
            text = text.replace('STS2_TEMPLATE_', public_stem(mod_id) + '_')
            text = re.sub(r'(?<=_)TEMPLATE(?=_|\.)', public_stem(short), text)
        else:
            text = text.replace('STS2_TEMPLATE_', public_stem(mod_id) + '_')
        text = re.sub(r'\bTemplate(?=[A-Z]|\b)', short, text)
        text = text.replace('"template"', json.dumps(short.lower()))
        text = text.replace('template_support.png', short.lower() + '_support.png')
        for i, url in enumerate(urls):
            text = text.replace(f'@@UPSTREAM_URL_{i}@@', url)
        text = text.replace('@@UPSTREAM_REPO@@', 'SlayTheCircle/STS2-Template')
        path.write_text(text, encoding='utf-8')

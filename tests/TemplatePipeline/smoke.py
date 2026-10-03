"""诊断素材的独立双目标打包；不创建提交，不部署，不上传，不证明角色设计可玩。"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

from test_derivation import DerivationTests

parser = argparse.ArgumentParser()
for name in ('refs-1110', 'refs-1071', 'ritsulib', 'dotnet', 'godot'):
    parser.add_argument('--' + name, required=True, type=Path)
args = parser.parse_args()
fixture = DerivationTests()
fixture.setUp()
try:
    root = fixture.root
    for source, name in [(args.refs_1110, 'game'), (args.refs_1071, 'game-0.107.1')]:
        shutil.copytree(source, root / 'libs' / name)
    # 引号、空格路径走实际 Bash 配置加载；不使用组织私有构建输入。
    masters = root / 'diagnostic masters'
    masters.mkdir()
    paths = ['卡图/示例打击', '卡图/示例防御', '卡图/示例昂扬', '遗物/示例坠饰',
             '药水/示例药剂', 'buff图标/示例昂扬', 'buff图标/支援徽记']
    for name in paths:
        path = masters / (name + '.png')
        path.parent.mkdir(exist_ok=True)
        subprocess.run(['convert', '-size', '512x512', 'xc:none', '-fill', '#679abc',
                        '-draw', 'rectangle 40,40 470,470', str(path)], check=True)
    config = {'GAME_REFS_DIR': root / 'libs/game', 'MOD_GAME_REFS_1110': root / 'libs/game',
              'MOD_GAME_REFS_1071': root / 'libs/game-0.107.1',
              'MOD_LOADER_GAME_REFS': root / 'libs/game-0.107.1',
              'RITSULIB_DIR': args.ritsulib.resolve(), 'DOTNET_EXE': args.dotnet.resolve(),
              'GODOT_EXE': args.godot.resolve(), 'ART_SOURCE_DIR': masters}
    import shlex
    (root / '.local-dev.env').write_text(''.join(f'{key}={shlex.quote(str(value))}\n' for key, value in config.items()))
    fixture.run_cmd('bash', 'scripts/check.sh', '--source-only')
    fixture.run_cmd('git', 'diff', '--exit-code')
    fixture.derive('Smoke', '--verify-build')
    # 实际 JPEG 解码、含空格/嵌套路径及另名图标目录，保护手工交付的绑定接口。
    jpeg = masters / '手工交付 卡图/新闻/strike.jpg'
    jpeg.parent.mkdir(parents=True)
    subprocess.run(['convert', str(masters / '卡图/示例打击.png'), str(jpeg)], check=True)
    icon = masters / '图标/power.png'
    icon.parent.mkdir()
    shutil.copyfile(masters / 'buff图标/示例昂扬.png', icon)
    mapping = root / 'scripts/art/mappings.sh'
    mapping.write_text(mapping.read_text().replace('卡图/示例打击.png', '"手工交付 卡图/新闻/strike.jpg"')
                       .replace('buff图标/示例昂扬.png', '图标/power.png'))
    fixture.run_cmd('bash', 'scripts/prep-art.sh')

    def state():
        return {str(path.relative_to(root)): (hashlib.sha256(path.read_bytes()).hexdigest(), path.stat().st_mtime_ns)
                for path in (root / 'assets/STS2-Smoke').rglob('*.png')}

    before = state()
    fixture.run_cmd('bash', 'scripts/prep-art.sh')
    if state() != before:
        raise AssertionError('相同母版重生成改变了字节或 mtime')
    badge = masters / 'buff图标/支援徽记.png'
    badge.rename(badge.with_suffix('.missing'))
    fixture.run_cmd('bash', 'scripts/prep-art.sh', success=False)
    if state() != before:
        raise AssertionError('缺母版的失败已改变成品')
    badge.with_suffix('.missing').rename(badge)
    source_manifest = (root / 'STS2-Smoke.json').read_bytes()
    # 完整本机检查也可验收明确的开发批次；未完成原案仍不得进入发行候选。
    roster = root / 'docs/history/design/card-roster.txt'
    policy = root / 'docs/history/design/roster-policy.json'
    original_roster, original_policy = roster.read_bytes(), policy.read_bytes()
    roster.write_text(roster.read_text() + '\n计划卡（技能）普通 1\n')
    batch = json.loads(policy.read_text()); batch['deferred'] = ['计划卡']
    policy.write_text(json.dumps(batch, ensure_ascii=False))
    checked = fixture.run_cmd('bash', 'scripts/check.sh', '--full')
    print(checked.stdout, end='')
    print(checked.stderr, end='')
    rejected = fixture.run_cmd('bash', 'scripts/package.sh', success=False)
    if '候选发行物仍有延后项' not in rejected.stdout:
        raise AssertionError(rejected.stdout + rejected.stderr)
    roster.write_bytes(original_roster)
    policy.write_bytes(original_policy)
    flat = json.loads((root / 'mods-dist/STS2-Smoke/STS2-Smoke.json').read_text())
    if flat['min_game_version'] != '0.111.0':
        raise AssertionError('新版平铺安装清单与编译目标不一致')
    result = fixture.run_cmd('bash', 'scripts/package.sh')
    print(result.stdout, end='')
    print(result.stderr, end='')
    import zipfile
    archives = list((root / 'mods-dist').glob('*.zip'))
    if len(archives) != 3:
        raise AssertionError('没有生成双目标与工坊三个候选包')
    for archive in archives:
        with zipfile.ZipFile(archive) as package:
            if package.testzip() is not None:
                raise AssertionError('ZIP 校验失败')
            if '-game-' in archive.name:
                target = archive.stem.rsplit('-game-', 1)[1]
                manifest = json.loads(package.read('STS2-Smoke/STS2-Smoke.json'))
                if manifest['min_game_version'] != target:
                    raise AssertionError('目标 ZIP 清单错误')
    flat = json.loads((root / 'mods-dist/STS2-Smoke/STS2-Smoke.json').read_text())
    if flat['min_game_version'] != '0.107.1' or (root / 'STS2-Smoke.json').read_bytes() != source_manifest:
        raise AssertionError('旧版平铺清单错误或构建改写了源码清单')
    # 错尺寸纹理必须在真实 PCK 验证失败，不能靠文件存在性放行。
    power = root / 'assets/STS2-Smoke/images/powers/SmokeVigorPower.png'
    subprocess.run(['convert', str(power), '-resize', '8x8!', str(power)], check=True)
    fixture.run_cmd('bash', 'scripts/build-pck.sh')
    rejected = fixture.run_cmd('bash', 'scripts/verify-pck.sh', success=False)
    if '尺寸错误' not in rejected.stderr:
        raise AssertionError(rejected.stdout + rejected.stderr)
    print('PASS: 独立快照派生与当前目标编译；JPEG/嵌套/另名目录；双目标完整包与安装清单；缺母版写入前拒绝；重生成字节/mtime 不变；错尺寸真实 PCK 拒绝。')
finally:
    fixture.temp.cleanup()

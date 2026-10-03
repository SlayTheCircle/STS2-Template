"""生成派生 README、可信 Bash 配置和私有导航，不覆盖已有私有资料。"""
import json
import shlex
import shutil
from pathlib import Path


def write(mod_id: str, short: str, cn: str, name: str, summary: str, author: str, repo: str) -> None:
    manifest = Path(f'{mod_id}.json')
    data = json.loads(manifest.read_text())
    data.update(name=f'{cn} | {name}', author=author,
                description=f'{summary}。A Slay the Spire 2 mod.')
    manifest.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    replacements = {'__MOD_ID__': mod_id, '__CN_NAME__': cn, '__MOD_SUMMARY__': summary,
                    '__MOD_SUMMARY_EN__': name, '__VDF_TITLE__': f'{cn} | {name}', '__REPO__': repo}

    def render(source: str) -> str:
        text = Path(source).read_text()
        for key, value in replacements.items():
            text = text.replace(key, value)
        return text

    for lang, target in [('zh', 'README.md'), ('en', 'README.en.md')]:
        Path(target).write_text(render(f'templates/readme.{lang}.md'))
    private = Path('local_dev')
    workshop = private / 'workshop'
    workshop.mkdir(parents=True, exist_ok=True)
    publish = workshop / 'publish.sh'
    text = render('templates/workshop/publish.sh.example')
    # 标题是数据；使用单独配置文件的 shell quoting，避免 sed / Bash 插值。
    if not publish.exists():
        publish.write_text(text)
        publish.chmod(0o755)
    else:
        print('保留既有私有工坊发布脚本；发布目标按其原配置核对。')
    if not (workshop / 'config.sh').exists():
        (workshop / 'config.sh').write_text(
            f'REPO={shlex.quote(repo)}\n'
            f'VDF_TITLE={shlex.quote(cn + " | " + name)}\n'
            '# Expected Workshop owner profile SteamID64; required for publishing.\n'
            "WORKSHOP_OWNER=''\n")
    if not (workshop / 'description.bbcode').exists():
        (workshop / 'description.bbcode').write_text(render('templates/workshop/description.bbcode.example'))
    for helper in ('render-vdf.py', 'check-live.py'):
        if not (workshop / helper).exists():
            shutil.copyfile('templates/workshop/' + helper, workshop / helper)
    if not (private / 'SCAFFOLD-NOTES.md').exists():
        (private / 'SCAFFOLD-NOTES.md').write_text(Path('templates/local-dev.env.notes.md').read_text())
    if not (private / 'README.md').exists():
        (private / 'README.md').write_text(Path('templates/local-dev-readme.md').read_text())
    if not (private / 'workspace.md').exists():
        (private / 'workspace.md').write_text(Path('templates/workspace.md').read_text())

    Path('STATUS.md').write_text(f'''# 当前状态

本仓库由模板派生为 {mod_id}；仍保留示例内容，尚未实现设计案。

初始化的源码检查结果以本次脚本输出为准。编译、素材、PCK 和游戏内验收须由本仓实际执行后记录；模板的验收证据不自动继承。

后续开发按 [内容开发 SOP](docs/dev/content-sop.md) 进行，依赖配置见 [贡献指南](CONTRIBUTING.md)，本机资料从 `local_dev/README.md` 导航。
''')

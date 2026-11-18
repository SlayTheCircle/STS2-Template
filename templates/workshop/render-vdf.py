"""工坊配置值保持数据语义；描述保留真实换行，不执行插值。"""
import re
import sys
from pathlib import Path

root, item_id, title = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
if not re.fullmatch(r'[0-9]+', item_id):
    raise SystemExit('错误: publishedfileid 必须为数字。')
values = {'appid': '2868840', 'publishedfileid': item_id,
          'contentfolder': str(root / 'content'),
          'description': (root / 'description.bbcode').read_text(encoding='utf-8')}
if item_id == '0':
    if not (root / 'cover.jpg').is_file():
        raise SystemExit('错误: 首发需要工坊封面 cover.jpg。')
    values.update(previewfile=str(root / 'cover.jpg'), visibility='public', title=title)
if (root / 'changenote.txt').is_file():
    values['changenote'] = (root / 'changenote.txt').read_text(encoding='utf-8')


def quote(value: str) -> str:
    return '"' + value.replace('\\', '\\\\').replace('"', '\\"') + '"'


text = '"workshopitem"\n{\n' + ''.join(f'  {quote(key)} {quote(value)}\n' for key, value in values.items()) + '}\n'
(root / 'workshop.vdf').write_text(text, encoding='utf-8')

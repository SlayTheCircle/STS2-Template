"""Protect occupied-game refusal, nested variant delivery and Workshop identity/description preservation."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import subprocess
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts/distribution'))
from deploy import deploy, closed
from delivery import hashes
spec = importlib.util.spec_from_file_location('workshop_live', ROOT / 'templates/workshop/check-live.py')
live = importlib.util.module_from_spec(spec)
spec.loader.exec_module(live)


class DeliveryTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.source = self.root / 'candidate'
        self.source.mkdir()
        for name, data in {'Demo.dll': b'loader', 'Demo.pck': b'pack', 'Demo.json': b'{"id":"Demo"}',
                           'lib/branch/Demo.dll': b'content'}.items():
            target = self.source / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        self.game = self.root / 'game'
        (self.game / 'data_sts2_windows_x86_64').mkdir(parents=True)
        self.dest = self.game / 'mods/Demo'
        self.dest.mkdir(parents=True)
        (self.dest / 'old.dll').write_bytes(b'old')

    def test_nested_delivery_backup_and_stale_file_cleanup(self):
        with patch('deploy.closed') as guard:
            deploy(self.source, self.game, 'Demo', 'detector', self.root / 'records')
        self.assertEqual(guard.call_count, 2)
        self.assertEqual(hashes(self.source), hashes(self.dest))
        self.assertEqual(next((self.root / 'records').glob('*/before/old.dll')).read_bytes(), b'old')

    def test_refusal_keeps_installed_bytes(self):
        before = hashes(self.dest)
        for error in ['Game is running', 'Process detection failed']:
            with patch('deploy.closed', side_effect=ValueError(error)):
                with self.assertRaises(ValueError):
                    deploy(self.source, self.game, 'Demo', 'detector', self.root / 'records')
            self.assertEqual(before, hashes(self.dest))

    def test_detector_errors_and_running_game_are_refused(self):
        for result in [subprocess.CompletedProcess([], 1, '', 'failure'),
                       subprocess.CompletedProcess([], 0, '', ''),
                       subprocess.CompletedProcess([], 0, 'ERROR: unavailable', ''),
                       subprocess.CompletedProcess([], 0, 'SlayTheSpire2.exe 123', '')]:
            with patch('deploy.subprocess.run', return_value=result):
                with self.assertRaises(ValueError): closed('detector')

    def test_update_vdf_preserves_display_fields(self):
        (self.root / 'description.bbcode').write_text('two\nlines')
        (self.root / 'changenote.txt').write_text('v0.2.0\n新增 "示例" 动作。')
        subprocess.run([sys.executable, str(ROOT / 'templates/workshop/render-vdf.py'),
                        str(self.root), '123', 'unused title'], check=True)
        vdf = (self.root / 'workshop.vdf').read_text()
        for key in ('title', 'previewfile', 'visibility'):
            self.assertNotIn('"' + key + '"', vdf)
        self.assertIn('two\nlines', vdf)
        self.assertIn('"changenote" "v0.2.0\n新增 \\"示例\\" 动作。"', vdf)
        (self.root / 'changenote.txt').unlink()
        subprocess.run([sys.executable, str(ROOT / 'templates/workshop/render-vdf.py'),
                        str(self.root), '123', 'unused title'], check=True)
        self.assertNotIn('"changenote"', (self.root / 'workshop.vdf').read_text())

    def test_description_newlines_allowed_but_content_and_identity_preserved(self):
        item = dict(result=1, publishedfileid='123', consumer_app_id=2868840,
                    creator='76561190000000000', description='line\r\n[url=https://example.org]link[/url]')
        local = item['description'].replace('\r\n', '\n')
        live.verify(item, '123', item['creator'], local)
        for bad in [dict(item, publishedfileid='456'), dict(item, consumer_app_id=1),
                    dict(item, creator='76561190000000001'), dict(item, description=local+'changed')]:
            with self.assertRaises(ValueError): live.verify(bad, '123', item['creator'], local)


if __name__ == '__main__':
    unittest.main()

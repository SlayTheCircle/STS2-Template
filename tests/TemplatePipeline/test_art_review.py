"""Protect derived identities/localized names, self-contained previews and unchanged source icons."""
import base64
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
PNG = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=')


class ArtReviewTests(unittest.TestCase):
    def test_derived_preview_names_comparison_and_source_preservation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            scripts = root / 'scripts'
            shutil.copytree(ROOT / 'scripts/art_review', scripts / 'art_review')
            shutil.copyfile(ROOT / 'scripts/modmeta.py', scripts / 'modmeta.py')
            (root / 'STS2-HTTPKnight.json').write_text('{"id":"STS2-HTTPKnight"}')
            localization = root / 'localization/zhs'
            localization.mkdir(parents=True)
            (localization / 'powers.json').write_text(json.dumps({
                'STS2_HTTP_KNIGHT_POWER_HTTP_FOCUS_POWER.title': '聚焦 <光>'}))
            images = root / 'assets/STS2-HTTPKnight/images'
            for name in ('powers/HTTPFocusPower', 'relics/Unknown', 'relics/Unknown_outline', 'energy/custom_text'):
                path = images / (name + '.png')
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(PNG)
            before = root / 'before'
            shutil.copytree(images, before)
            originals = {path: (path.read_bytes(), path.stat().st_mtime_ns) for path in images.rglob('*.png')}
            review = root / 'local_dev/review.json'
            review.parent.mkdir()
            review.write_text(json.dumps({'powers/HTTPFocusPower': {'status': '待检查', 'note': '<浅底>'}}))
            output = root / 'output'
            subprocess.run([sys.executable, str(scripts / 'art_review/preview.py'),
                            '--output', str(output), '--before', str(before), '--review', str(review)], check=True)
            rows = json.loads((output / 'inventory.json').read_text())
            self.assertEqual(len(rows), 3)
            by_resource = {row['resource']: row for row in rows}
            self.assertEqual(by_resource['powers/HTTPFocusPower']['name'], '聚焦 <光>')
            self.assertEqual(by_resource['relics/Unknown']['name'], 'Unknown')
            self.assertEqual(by_resource['energy/custom_text']['logical_px'], 24)
            page = (output / 'index.html').read_text()
            for expected in ('STS2-HTTPKnight', '聚焦 &lt;光&gt;', '&lt;浅底&gt;',
                             'data:image/png;base64,', '修改前', '描边原图'):
                self.assertIn(expected, page)
            self.assertEqual(originals, {path: (path.read_bytes(), path.stat().st_mtime_ns) for path in originals})


if __name__ == '__main__':
    unittest.main()

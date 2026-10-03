"""保护派生实际失败模式；源码快照在临时 Git 索引中运行，不创建提交或访问游戏。"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


class DerivationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='sts2-template-pipeline-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        files = subprocess.check_output(['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'], cwd=ROOT).decode().split('\0')
        for name in filter(None, files):
            source = ROOT / name
            if not source.is_file():
                continue
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        self.env = {key: value for key, value in os.environ.items()
                    if key not in {'GAME_REFS_DIR', 'RITSULIB_TARGET', 'RITSULIB_DIR', 'ART_SOURCE_DIR', 'ROSTER_DESIGN_FILE', 'PYTHONPATH'}}
        self.run_cmd('git', 'init', '-q', '-b', 'main')
        self.run_cmd('git', 'add', '-A')

    def run_cmd(self, *args, success=True):
        result = subprocess.run(args, cwd=self.root, env=self.env, capture_output=True, text=True)
        if success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def derive(self, short, *args):
        self.run_cmd('bash', 'scripts/init-mod.sh', 'STS2-' + short, short, *args)

    def test_check_then_derive_keeps_cache_out_and_generates_private_entry(self):
        self.run_cmd('bash', 'scripts/check.sh', '--source-only')
        self.run_cmd('git', 'diff', '--exit-code')
        self.derive('Nova')
        self.assertTrue((self.root / 'local_dev/README.md').is_file())
        self.assertTrue((self.root / 'local_dev/workspace.md').is_file())
        self.assertFalse((self.root / 'scripts/init-mod.sh').exists())
        lineage = json.loads((self.root / '.template-origin').read_text())
        self.assertEqual(lineage['template'], 'STS2-Template')
        self.assertEqual(lineage['derived'], 'STS2-Nova')
        self.assertEqual(len(lineage['snapshotDigest']), 64)
        source = (self.root / 'src/STS2-Nova/Content/Enchantments/NovaSupportEnchantment.cs').read_text()
        self.assertIn('/enchantments/nova_support.png', source)
        self.assertIn('SlayTheCircle/STS2-Template', (self.root / 'docs/dev/onboarding.md').read_text())

    def test_acronym_uses_actual_registered_compound_key(self):
        self.derive('API')
        cards = json.loads((self.root / 'localization/eng/cards.json').read_text())
        self.assertIn('STS2_API_CARD_API_STRIKE.description', cards)
        self.run_cmd('python3', 'scripts/audit-placeholders.py')

    def test_existing_private_inputs_and_publish_config_are_preserved(self):
        inputs = {'local_dev/README.md': 'my private design entry',
                  'local_dev/workshop/publish.sh': '# existing private publisher',
                  'local_dev/workshop/config.sh': "REPO='Example/STS2-Private'",
                  'local_dev/workshop/description.bbcode': 'existing description',
                  'local_dev/workshop/publishedfileid.txt': '123456789'}
        for name, value in inputs.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(value)
        self.derive('Private')
        for name, value in inputs.items():
            self.assertEqual((self.root / name).read_text(), value)

    def test_multiword_mod_prefix_matches_ritsulib(self):
        self.derive('SilverTongue')
        cards = json.loads((self.root / 'localization/eng/cards.json').read_text())
        self.assertIn('STS2_SILVER_TONGUE_CARD_SILVER_TONGUE_STRIKE.description', cards)

    def test_display_name_is_shell_data(self):
        name = 'Quote & Co / "Hello" $(false)'
        self.derive('Quote', '--name', name, '--repo', 'Example/STS2-Quote')
        result = self.run_cmd('bash', '-c', 'source local_dev/workshop/config.sh; printf "%s" "$VDF_TITLE"')
        self.assertEqual(result.stdout, 'Quote | ' + name)
        result = self.run_cmd('bash', '-c', 'source local_dev/workshop/config.sh; printf "%s" "$REPO"')
        self.assertEqual(result.stdout, 'Example/STS2-Quote')
        self.assertIn('https://github.com/Example/STS2-Quote/releases', (self.root / 'README.md').read_text())
        workshop = self.root / 'local_dev/workshop'
        (workshop / 'cover.jpg').write_bytes(b'diagnostic cover existence only')
        (workshop / 'description.bbcode').write_text('first line\nsecond line')
        self.run_cmd('python3', str(workshop / 'render-vdf.py'), str(workshop), '0', name)
        vdf = (workshop / 'workshop.vdf').read_text()
        self.assertIn('\\"Hello\\"', vdf)
        self.assertIn('first line\nsecond line', vdf)

    def test_nested_power_without_localization_fails(self):
        source = self.root / 'src/STS2-Template/Content/Powers/TemplateVigorPower.cs'
        nested = source.parent / 'Examples' / source.name
        nested.parent.mkdir()
        source.rename(nested)
        for lang in ('eng', 'zhs'):
            (self.root / f'localization/{lang}/powers.json').write_text('{}\n')
        result = self.run_cmd('python3', 'scripts/audit-loc-coverage.py', success=False)
        self.assertIn('TEMPLATE_VIGOR_POWER', result.stdout)

    def test_invalid_dependency_is_rejected_before_identity_changes(self):
        (self.root / '.local-dev.env').write_text('GAME_REFS_DIR="/nonexistent/refs with spaces"\n')
        self.run_cmd('bash', 'scripts/init-mod.sh', 'STS2-EnvProbe', '--verify-build', success=False)
        self.assertTrue((self.root / 'STS2-Template.json').is_file())
        self.assertFalse((self.root / 'STS2-EnvProbe.json').exists())


if __name__ == '__main__':
    unittest.main()

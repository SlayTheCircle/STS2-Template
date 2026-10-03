"""保护计算变量、继承内容、X 费用、批次和安装清单的源码契约。"""
import json
from pathlib import Path
import sys
import unittest

import test_derivation as fixtures

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from asset_contract import textures
from distribution.manifest import write as write_manifest


class ContentContractTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.DerivationTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.temp.cleanup)
        self.root = self.fixture.root

    def test_calculated_dependencies_and_stale_consumption_are_rejected(self):
        path = self.root / 'src/STS2-Template/Content/Cards/Basic/TemplateStrike.cs'
        original = path.read_text()
        calculated = original.replace('new DamageVar(6m, ValueProp.Move)',
            'new CalculatedDamageVar(ValueProp.Move).WithMultiplier(static (_card, _target) => 0m)')
        for lang in ('zhs', 'eng'):
            loc = self.root / f'localization/{lang}/cards.json'
            loc.write_text(loc.read_text().replace('{Damage:diff()}', '{CalculatedDamage:diff()}'))
        path.write_text(calculated.replace('DynamicVars.Damage', 'DynamicVars.CalculatedDamage'))
        result = self.fixture.run_cmd('python3', 'scripts/audit-placeholders.py', success=False)
        self.assertIn('缺配套变量', result.stdout)
        complete = calculated.replace('new CalculatedDamageVar',
            'new CalculationBaseVar(6m), new ExtraDamageVar(1m), new CalculatedDamageVar')
        path.write_text(complete)  # 声明与文本更新了，但结算/升级仍消费 Damage。
        result = self.fixture.run_cmd('python3', 'scripts/audit-placeholders.py', success=False)
        self.assertIn('DynamicVars 消费未声明键 Damage', result.stdout)
        path.write_text(complete.replace('DynamicVars.Damage', 'DynamicVars.CalculatedDamage'))
        self.fixture.run_cmd('python3', 'scripts/audit-placeholders.py')
        path.write_text(path.read_text().replace('.WithMultiplier(static (_card, _target) => 0m)', ''))
        result = self.fixture.run_cmd('python3', 'scripts/audit-placeholders.py', success=False)
        self.assertIn('WithMultiplier', result.stdout)

    def test_indirect_card_cannot_disappear_from_checks_or_export(self):
        folder = self.root / 'src/STS2-Template/Content/Mechanics'
        folder.mkdir()
        (folder / 'NewsBase.cs').write_text('''public abstract class NewsBase : TemplateCardBase {
            protected NewsBase() : base(0, CardType.Skill, CardRarity.Token, TargetType.Self) { }
        }''')
        (folder / 'Announcement.cs').write_text('[RegisterCard(typeof(TemplateCardPool))]\npublic sealed class Announcement : NewsBase { }')
        missing = self.fixture.run_cmd('python3', 'scripts/audit-loc-coverage.py', success=False)
        self.assertIn('ANNOUNCEMENT.title', missing.stdout)
        self.fixture.run_cmd('python3', 'scripts/audit-roster.py', success=False)
        self.fixture.run_cmd('python3', 'scripts/export-card-table.py', success=False)
        self.assertTrue(any(t['path'].endswith('/cards/Announcement.png') for t in textures(self.root)))
        self.assertFalse(any(t['path'].endswith('/cards/NewsBase.png') for t in textures(self.root)))
        for lang in ('zhs', 'eng'):
            loc = self.root / f'localization/{lang}/cards.json'
            data = json.loads(loc.read_text())
            data.update({'STS2_TEMPLATE_CARD_ANNOUNCEMENT.title': '公告',
                         'STS2_TEMPLATE_CARD_ANNOUNCEMENT.description': '无效果。'})
            loc.write_text(json.dumps(data, ensure_ascii=False))
        policy = self.root / 'docs/history/design/roster-policy.json'
        data = json.loads(policy.read_text()); data['tokens'] = ['公告']
        policy.write_text(json.dumps(data, ensure_ascii=False))
        self.fixture.run_cmd('python3', 'scripts/export-card-table.py')
        self.fixture.run_cmd('bash', 'scripts/check.sh', '--source-only')
        self.assertIn('| 公告 | 衍生 | 0 | 技能 |', (self.root / 'docs/design/cards.md').read_text())

    def test_x_cost_is_exported_as_x(self):
        path = self.root / 'src/STS2-Template/Content/Cards/Basic/TemplateDefend.cs'
        source = path.read_text().replace('base(1,', 'base(0,')
        source = source.replace('public TemplateDefend()', 'protected override bool HasEnergyCostX => true;\n    public TemplateDefend()')
        path.write_text(source)
        self.fixture.run_cmd('python3', 'scripts/export-card-table.py')
        self.assertIn('| 示例防御 | 初始 | X |', (self.root / 'docs/design/cards.md').read_text())

    def test_deferred_batch_is_explicit_and_cannot_be_packaged(self):
        roster = self.root / 'docs/history/design/card-roster.txt'
        roster.write_text(roster.read_text() + '\n计划卡（技能）普通 1\n')
        self.fixture.run_cmd('python3', 'scripts/audit-roster.py', success=False)
        policy = self.root / 'docs/history/design/roster-policy.json'
        data = json.loads(policy.read_text()); data['deferred'] = ['计划卡']
        policy.write_text(json.dumps(data, ensure_ascii=False))
        self.fixture.run_cmd('bash', 'scripts/check.sh', '--source-only')
        result = self.fixture.run_cmd('bash', 'scripts/package.sh', success=False)
        self.assertIn('候选发行物仍有延后项', result.stdout)
        self.assertFalse((self.root / 'mods-dist').exists())

    def test_install_manifest_tracks_target_without_changing_source(self):
        source = self.root / 'STS2-Template.json'
        before = source.read_bytes()
        destination = self.root / 'install.json'
        for target in ('0.111.0', '0.107.1'):
            write_manifest(source, destination, target)
            self.assertEqual(json.loads(destination.read_text())['min_game_version'], target)
        self.assertEqual(source.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()

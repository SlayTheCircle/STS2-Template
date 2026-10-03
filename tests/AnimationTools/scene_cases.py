"""Protect resource identity and reject broken node/property tracks before sampling."""
from pathlib import Path


def check_scene_cases(run, folder: Path, scene: Path) -> None:
    original = scene.read_text()
    script = folder / 'noop.gd'
    script.write_text('extends Node2D\n')
    scripted = folder / 'scripted.tscn'
    scripted.write_text(original.replace('\n\n',
        f'\n\n[ext_resource type="Script" path="{script}" id="script_added"]\n\n', 1)
        .replace('[node name="Actor" type="Node2D"]',
                 '[node name="Actor" type="Node2D"]\nscript = ExtResource("script_added")\n'
                 'metadata/tag = "part_001"'))
    run('check', '--scene', str(scripted))
    saved = folder / 'resaved.tscn'
    run('save', '--scene', str(scripted), '--out', str(saved))
    run('check', '--scene', str(saved))
    assert 'metadata/tag = "part_001"' in saved.read_text(), 'Resource normalization rewrote user data'
    before = saved.read_bytes(), saved.stat().st_mtime_ns
    run('save', '--scene', str(scripted), '--out', str(saved))
    assert before == (saved.read_bytes(), saved.stat().st_mtime_ns), 'Unstable scripted scene export'

    for target, expected in [('MissingArm:rotation', 'Unresolved track node'),
                             ('Body/Arm:missing_rotation', 'Unresolved track property')]:
        broken = folder / 'broken-track.tscn'
        broken.write_text(original.replace('Body/Arm:rotation', target))
        assert expected in run('check', '--scene', str(broken), success=False)
        assert expected in run('save', '--scene', str(broken), '--out', str(saved), success=False)
        assert before == (saved.read_bytes(), saved.stat().st_mtime_ns), 'Rejected scene changed output'

    nested = folder / 'nested-property.tscn'
    nested.write_text(original.replace('Body/Arm:rotation', 'Body/Arm:position:x'))
    run('check', '--scene', str(nested))
    disabled = folder / 'disabled-track.tscn'
    disabled.write_text(original.replace('Body/Arm:rotation', 'MissingArm:rotation')
                        .replace('tracks/0/enabled = true', 'tracks/0/enabled = false'))
    run('check', '--scene', str(disabled))

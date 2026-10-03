"""Exercise saved scenes and catch the historical foreground leak using a real renderer."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile
from scene_cases import check_scene_cases

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--godot', required=True)
    parser.add_argument('--render', action='store_true', help='Needs display, or run this script under xvfb-run')
    args = parser.parse_args()
    godot = str(Path(args.godot).resolve())

    def run(mode, *extra, success=True):
        command = [godot, '--audio-driver', 'Dummy']
        if mode not in ('canvas', 'frames', 'preview'): command.append('--headless')
        if mode == 'preview': command += ['--quit-after', '10']
        command += ['--path', str(ROOT / 'tools/animation'), '--script', 'run.gd', '--', '--mode', mode, *extra]
        result = subprocess.run(command, capture_output=True, text=True, timeout=60)
        output = result.stdout + result.stderr
        if 'SCRIPT ERROR' in output or (success and 'ERROR:' in output) or (result.returncode == 0) != success:
            raise AssertionError(output)
        return output

    with tempfile.TemporaryDirectory(prefix='animation-smoke-') as folder:
        folder = Path(folder)
        scene = folder / 'actor.tscn'
        run('save', '--out', str(scene))
        before = scene.read_bytes(), scene.stat().st_mtime_ns
        run('save', '--out', str(scene))
        assert before == (scene.read_bytes(), scene.stat().st_mtime_ns), 'Unstable generated scene'
        run('check', '--scene', str(scene))
        check_scene_cases(run, folder, scene)
        pack = folder / 'fixture.pck'
        packer = folder / 'pack.gd'
        packer.write_text('extends SceneTree\nfunc _initialize():\n'
                         '\tvar p = PCKPacker.new()\n'
                         '\tif p.pck_start(' + json.dumps(str(pack)) + ') != OK: quit(1); return\n'
                         '\tif p.add_file("res://fixture/actor.tscn", ' + json.dumps(str(scene)) + ') != OK: quit(1); return\n'
                         '\tquit(0 if p.flush() == OK else 1)\n')
        packed = subprocess.run([godot, '--headless', '--path', str(ROOT / 'tools/animation'),
                                 '--script', str(packer)], capture_output=True, text=True, timeout=30)
        assert packed.returncode == 0 and pack.is_file(), packed.stdout + packed.stderr
        run('check', '--pck', str(pack), '--scene', 'res://fixture/actor.tscn')
        spec = json.loads((ROOT / 'examples/animation/review.json').read_text())
        spec['clips']['missing'] = False
        bad = folder / 'bad.json'
        bad.write_text(json.dumps(spec))
        assert 'Missing animation' in run('check', '--spec', str(bad), success=False)
        if args.render:
            run('canvas', '--pck', str(pack), '--scene', 'res://fixture/actor.tscn')
            run('preview', '--scene', str(scene))
            text = scene.read_text()
            # The same positive local layer that previously escaped the battle room.
            assert '[node name="Body" type="Node2D" parent="."]' in text
            scene.write_text(text.replace('[node name="Body" type="Node2D" parent="."]',
                '[node name="Body" type="Node2D" parent="."]\nz_index = 50'))
            assert 'leaked above foreground' in run('canvas', '--scene', str(scene), success=False)
            run('frames', '--out', str(folder / 'frames'), '--fps', '2')
            manifest = json.loads((folder / 'frames/manifest.json').read_text())
            for clip in manifest['clips']:
                assert len(list((folder / 'frames' / clip['name']).glob('*.png'))) == clip['frames']
            frames = folder / 'frames'
            before_frames = {path: (path.read_bytes(), path.stat().st_mtime_ns)
                             for path in frames.rglob('*') if path.is_file()}
            assert 'must be empty' in run('frames', '--out', str(frames), '--fps', '1', success=False)
            assert before_frames == {path: (path.read_bytes(), path.stat().st_mtime_ns)
                                     for path in frames.rglob('*') if path.is_file()}, 'Refused export changed prior frames'
    print('PASS: saved-scene and PCK roundtrip, deterministic scripted output, missing-clip and invalid-track refusal' +
          (', real-renderer foreground regression, frame export and occupied-output refusal' if args.render else ''))


if __name__ == '__main__':
    main()

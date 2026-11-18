"""Guarded deployment of a flat or variant directory; backup lives outside the scanned mods tree."""
import argparse
import datetime
import json
from pathlib import Path
import re
import shutil
import subprocess
from delivery import hashes


def closed(detector: str):
    result = subprocess.run([detector], capture_output=True, text=True, timeout=30)
    if result.returncode or not result.stdout.strip() or re.search(r'error:', result.stdout, re.I):
        raise ValueError('Process detection failed; deployment stopped')
    if re.search(r'spire|sts2', result.stdout, re.I):
        raise ValueError('Game is running; close it before deploying')


def deploy(source, game, mod_id, detector, records):
    source, game, records = source.resolve(), game.resolve(), records.resolve()
    destination = game / 'mods' / mod_id
    if not (game / 'data_sts2_windows_x86_64').is_dir():
        raise ValueError('Expected Windows game installation')
    if records.is_relative_to(game / 'mods') or source == destination or source.is_relative_to(destination) or destination.is_relative_to(source):
        raise ValueError('Source, installed tree and backup directory must be separate')
    if destination.is_symlink():
        raise ValueError('Installed mod directory must not be a symlink')
    expected = hashes(source)
    for suffix in ('.dll', '.pck', '.json'):
        if mod_id + suffix not in expected:
            raise ValueError(f'Missing {mod_id + suffix}')
    manifest = json.loads((source / (mod_id + '.json')).read_text())
    if manifest.get('id') != mod_id:
        raise ValueError('Manifest identity differs from deployment target')
    closed(detector)
    previous = hashes(destination) if destination.exists() and any(destination.iterdir()) else {}
    record = records / datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    record.mkdir(parents=True)
    if previous:
        shutil.copytree(destination, record / 'before')
        if hashes(record / 'before') != previous:
            raise ValueError('Backup verification failed')
    (record / 'expected.json').write_text(json.dumps(expected, indent=2) + '\n')
    closed(detector)
    destination.mkdir(parents=True, exist_ok=True)
    # Copy in place: an occupied file is an error, never renamed out of the way.
    for name in expected:
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / name, target)
    for name in previous.keys() - expected.keys():
        (destination / name).unlink()
    if hashes(destination) != expected:
        raise ValueError('Installed bytes differ from candidate; inspect backup record')
    (record / 'installed.json').write_text(json.dumps(expected, indent=2) + '\n')
    print(f'Deployed {len(expected)} files; backup and hashes: {record}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('source', 'game', 'records'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--mod-id', required=True)
    parser.add_argument('--detector', required=True)
    args = parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9_-]+', args.mod_id):
        parser.error('Invalid mod ID')
    deploy(args.source, args.game, args.mod_id, args.detector, args.records)


if __name__ == '__main__':
    main()

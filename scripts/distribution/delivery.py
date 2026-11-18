"""Compare packaged, installed or downloaded trees using exact relative names and SHA-256."""
import argparse
import hashlib
import json
from pathlib import Path


def hashes(root: Path) -> dict[str, str]:
    if not root.is_dir():
        raise ValueError(f'Not a directory: {root}')
    result = {}
    for path in sorted(root.rglob('*')):
        if path.is_symlink():
            raise ValueError(f'Symlink in delivery: {path}')
        if path.is_file():
            result[path.relative_to(root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    if not result:
        raise ValueError(f'Empty delivery: {root}')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('destination', type=Path)
    parser.add_argument('--record', type=Path)
    args = parser.parse_args()
    expected, actual = hashes(args.source), hashes(args.destination)
    differences = sorted(key for key in expected.keys() | actual.keys() if expected.get(key) != actual.get(key))
    if differences:
        raise SystemExit('Delivery mismatch: ' + ', '.join(differences))
    if args.record:
        args.record.parent.mkdir(parents=True, exist_ok=True)
        args.record.write_text(json.dumps(expected, indent=2) + '\n')
    print(f'PASS: {len(expected)} files have identical paths and SHA-256.')


if __name__ == '__main__':
    main()

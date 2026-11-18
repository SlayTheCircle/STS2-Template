"""Read-only Workshop identity/description preflight. Cache stores public metadata only."""
import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def normalized(text):
    return text.replace('\r\n', '\n').replace('\r', '\n').strip()


def verify(item, item_id, creator, description, previous=None):
    if (item.get('result') != 1 or str(item.get('publishedfileid')) != item_id
            or item.get('consumer_app_id') != 2868840 or str(item.get('creator')) != creator):
        raise ValueError('Workshop identity mismatch: check item ID, app and configured owner SteamID64')
    if normalized(item.get('description', '')) != normalized(description):
        raise ValueError('Online description differs. Read the live item and synchronize description.bbcode before publishing.')
    links = lambda value: re.findall(r'\[url=([^\]]+)\]', value, re.I)
    if links(item['description']) != links(description):
        raise ValueError('Description links differ')
    if previous:
        for key in ('publishedfileid', 'creator', 'consumer_app_id', 'title', 'visibility', 'preview_url'):
            if item.get(key) != previous.get(key):
                raise ValueError(f'Workshop metadata changed: {key}; inspect the live item')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folder', type=Path)
    parser.add_argument('item_id')
    parser.add_argument('creator', help='Expected owner SteamID64, from Workshop owner profile')
    parser.add_argument('--previous', type=Path)
    parser.add_argument('--output', default='live-before.json')
    args = parser.parse_args()
    if not re.fullmatch(r'[1-9][0-9]*', args.item_id) or not re.fullmatch(r'[0-9]{17}', args.creator):
        parser.error('Existing item ID and owner SteamID64 required')
    request = Request('https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/',
                      data=urlencode({'itemcount': 1, 'publishedfileids[0]': args.item_id}).encode(),
                      headers={'User-Agent': 'STS2-Workshop-Preflight/1.0'})
    item = json.loads(urlopen(request, timeout=40).read())['response']['publishedfiledetails'][0]
    previous = json.loads(args.previous.read_text()) if args.previous else None
    verify(item, args.item_id, args.creator, (args.folder / 'description.bbcode').read_text(), previous)
    (args.folder / args.output).write_text(json.dumps(item, ensure_ascii=False, indent=2) + '\n')
    print('Workshop item, owner, app and description verified.')


if __name__ == '__main__':
    main()

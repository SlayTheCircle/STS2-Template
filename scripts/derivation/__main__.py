import argparse

from .identity import rename
from .scaffolding import write

parser = argparse.ArgumentParser()
parser.add_argument('mod_id')
parser.add_argument('short')
parser.add_argument('cn')
parser.add_argument('name')
parser.add_argument('summary')
parser.add_argument('author')
parser.add_argument('repo')
args = parser.parse_args()
rename(args.mod_id, args.short)
write(args.mod_id, args.short, args.cn, args.name, args.summary, args.author, args.repo)

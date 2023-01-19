"""
Find closest connected people in the "Notables" or any other category.
"""

import argparse
import collections
import itertools

import bfs_tools
import category_tools
import data_reader


def EnumConnections(bfs, targets):
  for node in bfs:
    if node.person in targets:
      yield node


parser = argparse.ArgumentParser()
parser.add_argument("person_id", help="Person to search from.")
parser.add_argument("--version", help="Data version (defaults to most recent).")
parser.add_argument("--relatives", action="store_true",
                    help="Find notable blood relatives (instead of all connections).")
parser.add_argument("--category", default="Notables",
                    help="Category name to search for connections to.")
parser.add_argument("--max-num", type=int, default=20,
                    help="Max number of people from that category to list.")
args = parser.parse_args()

db = data_reader.Database(args.version)
category_db = category_tools.CategoryDb(args.version)

start = db.id2num(args.person_id)

targets = category_db.list_people_in_category(args.category)
if args.relatives:
  bfs = bfs_tools.RelativeBfs(db, start)
else:
  bfs = bfs_tools.ConnectionBfs(db, start)

for node in itertools.islice(EnumConnections(bfs, targets), args.max_num):
  print(node.dist, db.num2id(node.person), db.name_of(node.person))

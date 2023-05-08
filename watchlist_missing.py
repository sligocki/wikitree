# Find people missing from watchlist from the nearest circles.
# Get JSON for wishlist at:
#   https://apps.wikitree.com/apps/wikitree-api-examples/getWatchlist/javascript.html

import argparse
import json
from pathlib import Path
import random

import bfs_tools
import data_reader
import utils


def search(db, start, in_group, max_dist):
  bfs = bfs_tools.ConnectionBfs(db, start)
  for node in bfs:
    if node.dist > max_dist:
      return
    if node.person not in in_group and (set(node.prevs) & in_group):
      prev = (set(node.prevs) & in_group).pop()
      print(f"Circle {node.dist:2d} : {db.num2id(node.person):20s} <- {db.num2id(prev)}")

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("--max-dist", "-n", type=int, default=7)

  parser.add_argument("--focus", default="Ligocki-7")
  parser.add_argument("--watchlist", type=Path,
                      default=Path("data/watchlist.json"))
  parser.add_argument("--version", help="Data version (defaults to most recent).")
  args = parser.parse_args()

  db = data_reader.Database(args.version)
  focus_num = db.get_person_num(args.focus)
  focus_id = db.num2id(focus_num)

  with open(args.watchlist) as f:
    js = json.load(f)
    assert len(js) == 1
    assert js[0]["watchlistCount"] == len(js[0]["watchlist"])
    watchlist = frozenset(x["Id"] for x in js[0]["watchlist"])
  utils.log(f"Loaded watchlist. Size: {len(watchlist):_}")

  search(db, focus_num, watchlist, args.max_dist)

main()

# Filter watchlist by various criteria to find profiles that might be worth removing.

import argparse
import json
from pathlib import Path
import random

import data_reader
import distances
import utils


def load_recursive(focus, func, num_iters):
  this = set([focus])
  ret = set(this)
  for _ in range(num_iters):
    next = set()
    for x in this:
      next.update(func(x))
    this = next
    ret.update(this)
  return ret

def load_ancestors(db, focus, num_gens):
  return load_recursive(focus, db.parents_of, num_gens)

def load_descendants(db, focus, num_gens):
  return load_recursive(focus, db.children_of, num_gens)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("--focus", default="Ligocki-7")
  parser.add_argument("--watchlist", type=Path,
                      default=Path("data/watchlist.json"))

  # Filter parameters
  parser.add_argument("--circles", type=int, default=7)
  parser.add_argument("--ancestor-gens", type=int, default=10)
  parser.add_argument("--descendant-gens", type=int, default=2)

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
  watchlist = frozenset(x for x in watchlist if db.num2id(x))
  utils.log(f"Filtered watchlist down to: {len(watchlist):_}")

  dists, _, _, _ = distances.get_distances(
    db, focus_num, dist_cutoff=args.circles)
  circles = frozenset(dists.keys())
  utils.log(f"Loaded {len(circles):_} people within {args.circles} of {focus_id}")

  ancestors = frozenset(load_ancestors(
    db, focus_num, args.ancestor_gens))
  utils.log(f"Loaded {len(ancestors):_} ancestors of {focus_id}")

  relatives = ancestors.union(*[
    load_descendants(db, x, args.descendant_gens)
    for x in ancestors])
  utils.log(f"Loaded {len(relatives):_} relatives of {focus_id}")

  kin = relatives.union(*[db.partners_of(x) for x in relatives])
  utils.log(f"Loaded {len(kin):_} kin of {focus_id}")

  good = circles | kin
  utils.log(f"  # Kin or in circles: {len(good):_}")

  print()
  print(f"    * {len(good - watchlist)=}")
  print(f"    * {len(watchlist - good)=}")

  bad = watchlist - good
  print([db.num2id(x) for x in random.sample(list(bad), 20)])


main()

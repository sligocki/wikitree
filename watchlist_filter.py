# Filter watchlist by various criteria to find profiles that might be worth removing.
# Use `watchlist_download.py` to load watchlist.

import argparse
import json
import math
from pathlib import Path

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

  # Filter parameters. Which profiles do we expect to be in watchlist?
  #   1) Any profile within CC7
  parser.add_argument("--circles", type=int, default=7)
  #   2) Any ancestory within 10 generations
  parser.add_argument("--ancestor-gens", type=int, default=10)
  #   3) Any grandchild of such an ancestor
  parser.add_argument("--descendant-gens", type=int, default=2)
  #   4) Spouses of any relative

  parser.add_argument("--max-dist-sort", type=int, default=10)
  parser.add_argument("--unwanted-file", type=Path, default=Path("results/watch_unwanted.tsv"))
  parser.add_argument("--version", help="Data version (defaults to most recent).")
  args = parser.parse_args()

  db = data_reader.Database(args.version)
  focus_num = db.get_person_num(args.focus)
  focus_id = db.num2id(focus_num)

  with open(args.watchlist) as f:
    js = json.load(f)
    assert len(js) == 1
    assert js[0]["watchlistCount"] == len(js[0]["watchlist"])
    watchlist = frozenset(x["Id"] for x in js[0]["watchlist"] if "Id" in x)
  utils.log(f"Watchlist size: {len(watchlist):_}")

  watchlist = frozenset(x for x in watchlist if db.num2id(x))
  utils.log(f"Filtered to data dump: {len(watchlist):_} (rest are probably private profiles)")

  dists, _, _, _ = distances.get_distances(db, focus_num, dist_cutoff=args.circles)
  circles = frozenset(dists.keys())
  utils.log(f"  # People within {args.circles} of {focus_id}: {len(circles):_}")

  ancestors = frozenset(load_ancestors(
    db, focus_num, args.ancestor_gens))
  utils.log(f"  # Ancestors of {focus_id}: {len(ancestors):_}")

  relatives = ancestors.union(*[
    load_descendants(db, x, args.descendant_gens)
    for x in ancestors])
  utils.log(f"  # Relatives of {focus_id}: {len(relatives):_}")

  kin = relatives.union(*[db.partners_of(x) for x in relatives])
  utils.log(f"  # Kin of {focus_id}: {len(kin):_}")

  wanted = circles | kin
  utils.log(f"  # Wanted in watchlist: {len(wanted):_}")

  print(f"    * {len(wanted - watchlist)=}")
  print(f"    * {len(watchlist - wanted)=}")

  unwanted = watchlist - wanted

  dists, _, _, _ = distances.get_distances(db, focus_num, dist_cutoff=args.max_dist_sort)
  utils.log(f"Loaded {args.max_dist_sort} circles: {len(dists):_}")

  display = []
  for x in unwanted:
    display.append((dists.get(x, math.inf), db.num2id(x)))
  display.sort(reverse=True)
  utils.log("Sorted")

  with open(args.unwanted_file, "w") as f:
    for (d, id) in display:
      f.write(f"{d}\t{id}\thttps://www.wikitree.com/index.php?title=Special:Connection&action=connect&person1Name=Ligocki-7&person2Name={id}\n")
  utils.log(f"Wrote {len(display):_} rows to {args.unwanted_file}")


main()

#!/usr/bin/env python3

import argparse
import collections
import json
import random

import bfs_tools
import data_reader
import utils

def get_distances(db, start, ignore_people=frozenset(),
                  dist_cutoff=None, verbose=False):
  """Get distances to all other items in graph via breadth-first search."""
  dists = {}
  total_dist = 0
  max_dist = 0
  hist_dist = collections.defaultdict(int)
  for node in bfs_tools.ConnectionBfs(db, start, ignore_people):
    if dist_cutoff and node.dist > dist_cutoff:
      break
    dists[node.person] = node.dist
    hist_dist[node.dist] += 1
    max_dist = node.dist
    total_dist += node.dist
    if verbose and len(dists) % 1_000_000 == 0:
      utils.log(f" ... {len(dists):_} nodes / Circle {node.dist}")
  mean_dist = float(total_dist) / len(dists)
  hist_dist_list = [hist_dist[i] for i in range(max(hist_dist.keys()) + 1)]
  return dists, hist_dist_list, mean_dist, max_dist

def get_mean_dists(db, start):
  _, _, mean_dist, max_dist = get_distances(db, start)
  return mean_dist, max_dist

def enum_user_nums(db, args):
  if args.random:
    all_people = list(db.enum_people())
    random.shuffle(all_people)
    for user_num in all_people:
      yield user_num
  else:
    for wikitree_id in args.wikitree_id:
      yield db.id2num(wikitree_id)


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("--version", help="Data version (defaults to most recent).")
  parser.add_argument("--random", action="store_true")
  parser.add_argument("--save-distribution-json", help="Save Circle sizes to file.")
  parser.add_argument("--ignore-people",
                      help="Comma separated list of people to ignore in BFS.")
  parser.add_argument("--max-distance", type=int,
                      help="Limit BFS search to a max distance (instead of finding the distance to all people in the connected tree).")
  parser.add_argument("wikitree_id", nargs="*")
  args = parser.parse_args()

  utils.log("Loading DB")
  db = data_reader.Database(args.version)
  # db.load_connections()

  ignore_ids = args.ignore_people.split(",") if args.ignore_people else []
  ignore_nums = frozenset(db.id2num(id) for id in ignore_ids)

  circle_sizes = {}
  for user_num in enum_user_nums(db, args):
    utils.log("Loading distances from", db.num2id(user_num))
    dists, hist_dist, mean_dist, max_dist = get_distances(
      db, user_num, ignore_nums, dist_cutoff=args.max_distance, verbose=True)
    utils.log(db.num2id(user_num), mean_dist, max_dist)
    circle_sizes[db.num2id(user_num)] = hist_dist
    utils.log(hist_dist)

  if args.save_distribution_json:
    utils.log("Writing results")
    with open(args.save_distribution_json, "w") as f:
      json.dump(circle_sizes, f)

  utils.log("Done")

if __name__ == "__main__":
  main()
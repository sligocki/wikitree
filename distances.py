#!/usr/bin/env python3

import argparse
import collections
import json
from pprint import pprint
import random
import time

import bfs_tools
import data_reader
import utils

def get_distances(db, start, ignore_people=frozenset()):
  """Get distances to all other items in graph via breadth-first search."""
  dists = {}
  total_dist = 0
  max_dist = 0
  hist_dist = collections.defaultdict(int)
  for (person, dist) in bfs_tools.ConnectionBfs(db, start, ignore_people):
    dists[person] = dist
    hist_dist[dist] += 1
    max_dist = dist
    total_dist += dist
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
    for user_id in all_people:
      yield all_people
  else:
    for wikitree_id in args.wikitree_id:
      yield db.id2num(wikitree_id)


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--version", help="Data version (defaults to most recent).")
  parser.add_argument("--random", action="store_true")
  parser.add_argument("--save-distribution-json", help="Save Circle sizes to file.")
  parser.add_argument("--ignore-people",
                      help="Comma separated list of people to ignore in BFS.")
  parser.add_argument("wikitree_id", nargs="*")
  args = parser.parse_args()

  ignore_ids = args.ignore_people.split(",") if args.ignore_people else []
  ignore_nums = frozenset(db.id2num(id) for id in ignore_ids)

  db = data_reader.Database(args.version)
  db.load_connections()

  circle_sizes = {}
  for user_num in enum_user_nums(db, args):
    utils.log("Loading distances from", db.num2id(user_num))
    dists, hist_dist, mean_dist, max_dist = get_distances(db, user_num, ignore_nums)
    utils.log(db.num2id(user_num), mean_dist, max_dist)
    circle_sizes[db.num2id(user_num)] = hist_dist
    utils.log(hist_dist)

  if args.save_distribution_json:
    utils.log("Writing results")
    with open(args.save_distribution_json, "w") as f:
      json.dump(circle_sizes, f)

  utils.log("Done")

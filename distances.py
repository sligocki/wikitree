#!/usr/bin/env python3

import argparse
import collections
import json
from pprint import pprint
import random
import time

import data_reader

def get_distances(db, start):
  """Get distances to all other items in graph via breadth-first search."""
  dists = {start: 0}
  queue = collections.deque()
  queue.append(start)
  total_dist = 0
  max_dist = 0
  hist_dist = [1]
  while queue:
    person = queue.popleft()
    dist = dists[person]
    for neigh in db.neighbors_of(person):
      if neigh not in dists:
        dists[neigh] = dist + 1
        total_dist += dist + 1
        max_dist = dist + 1
        while len(hist_dist) <= dist + 1:
          hist_dist.append(0)
        hist_dist[dist + 1] += 1
        queue.append(neigh)
  mean_dist = float(total_dist) / len(dists)
  return dists, hist_dist, mean_dist, max_dist

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
  parser.add_argument("wikitree_id", nargs="*")
  args = parser.parse_args()

  db = data_reader.Database(args.version)
  db.load_connections()

  circle_sizes = {}
  for user_num in enum_user_nums(db, args):
    dists, hist_dist, mean_dist, max_dist = get_distances(db, user_num)
    print(db.num2id(user_num), mean_dist, max_dist, time.process_time())
    circle_sizes[db.num2id(user_num)] = hist_dist

  if args.save_distribution_json:
    with open(args.save_distribution_json, "w") as f:
      json.dump(circle_sizes, f)

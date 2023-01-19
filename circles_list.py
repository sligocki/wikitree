"""
List out all people in circles around a focus.
"""

import argparse

import bfs_tools
import data_reader


def try_id(db, person_num) -> str:
  id = db.num2id(person_num)
  if id:
    return id
  else:
    return str(person_num)


parser = argparse.ArgumentParser()
parser.add_argument("focus_id")
parser.add_argument("--num-circles", type=int, default=10)
parser.add_argument("--version", help="Data version (defaults to most recent).")
args = parser.parse_args()

db = data_reader.Database(args.version)

focus_num = db.id2num(args.focus_id)
circles = [[] for dist in range(args.num_circles + 1)]
for node in bfs_tools.ConnectionBfs(db, focus_num):
  if node.dist > args.num_circles:
    break
  circles[node.dist].append(node.person)

for dist in range(args.num_circles + 1):
  print("Circle", dist)
  for i, id in enumerate(sorted([try_id(db, person_num)
                                 for person_num in circles[dist]])):
    print(" *", i, id)

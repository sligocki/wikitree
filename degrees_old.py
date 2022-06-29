"""
Search for least updated profile within 6 degrees (circles).
Inspired for https://www.wikitree.com/g2g/84133/six-degrees-of-kevin-bacon
"""

import argparse
import datetime

import bfs_tools
import data_reader


parser = argparse.ArgumentParser()
parser.add_argument("focus_id", nargs="?", default="Bacon-2568")
parser.add_argument("--num-circles", type=int, default=6)
parser.add_argument("--version", help="Data version (defaults to most recent).")
args = parser.parse_args()

db = data_reader.Database(args.version)

focus_num = db.id2num(args.focus_id)
circles = [[] for dist in range(args.num_circles + 1)]
for person, dist in bfs_tools.ConnectionBfs(db, focus_num):
  if dist > args.num_circles:
    break
  if db.touched_time_of(person):
    circles[dist].append(person)

for dist in range(1, args.num_circles + 1):
  oldest = min(circles[dist], key=db.touched_time_of)
  print("Circle", dist, " LRU:", db.num2id(oldest), oldest,
        db.touched_time_of(oldest))

print()
for dist in range(1, args.num_circles + 1):
  oldest = sorted(circles[dist], key=db.touched_time_of)
  oldest = [p for p in oldest
            if db.touched_time_of(p) < datetime.datetime.fromisoformat("2022-06-01")]
  if oldest:
    print()
    print("Circle", dist, len(oldest))
    for i, person_num in enumerate(oldest):
      print(f" * {i:5_d}  {db.num2id(person_num):20s} {person_num:10d}  {db.touched_time_of(person_num)}")

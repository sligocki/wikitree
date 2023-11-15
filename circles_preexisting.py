"""
Search circle around focus person until you find profiles created before the
ones they came from. If the focus is a user and they built the profiles around
them in order from inside to outside, these points are the points where the
user connected to the pre-existing tree.
"""

import argparse
import collections

import bfs_tools
import data_reader


def try_id(db, person_num) -> str:
  id = db.num2id(person_num)
  if id:
    return id
  else:
    return str(person_num)

def preexisted(db, node):
  prev_create_times = []
  for p in node.prevs:
    if ct := db.registered_time_of(p):
      prev_create_times.append(ct)
  if prev_create_times:
    prev_create_time = min(prev_create_times)
    node_create_time = db.registered_time_of(node.person)
    if (prev_create_time and node_create_time and
        node_create_time < prev_create_time):
      return True
  return False

def BfsPreexisted(db, start):
  todos = collections.deque()
  todos.append(start)
  nodes = {}
  nodes[start] = bfs_tools.BfsNode(start, [], 0)
  while todos:
    person = todos.popleft()
    if preexisted(db, nodes[person]):
      yield nodes[person]
    else:
      # Only expand BFS to non-preexisting nodes.
      dist = nodes[person].dist
      for neigh in db.neighbors_of(person):
        if neigh in nodes:
          if nodes[neigh].dist == dist + 1:
            # If we have reached neigh equivalently from two
            # different directions, save both.
            nodes[neigh].prevs.append(person)
        else:
          todos.append(neigh)
          nodes[neigh] = bfs_tools.BfsNode(neigh, [person], dist + 1)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("focus_id")
  parser.add_argument("--version", help="Data version (defaults to most recent).")
  args = parser.parse_args()

  db = data_reader.Database(args.version)

  focus_num = db.id2num(args.focus_id)
  for node in BfsPreexisted(db, focus_num):
    print(f"{node.dist:3d}:    {db.name_of(node.person):30s} {try_id(db, node.person):10s}")

main()

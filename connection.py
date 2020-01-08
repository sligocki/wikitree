import argparse
import collections
import random
import sys
import time

import data_reader


class Bfs(object):
  def __init__(self, start, rel_types):
    self.start = start
    self.rel_types = rel_types
    self.dists = {start: 0}
    # Dict { person : [list of neighbors of person on shortest paths to start] }
    self.paths = {start: []}
    self.todo = [start]
    self.num_steps = 0

  def next_gen(self):
    """Enumerate next generation of connections."""
    self.num_steps += 1
    next_todo = []
    for person in self.todo:
      dist = self.dists[person]
      for neigh in db.relative_of_mult(person, self.rel_types):
        if neigh in self.dists:
          if self.dists[neigh] == dist + 1:
            # Found another good path.
            self.paths[neigh].append(person)
        else:  # neigh not in self.dists
          self.dists[neigh] = dist + 1
          self.paths[neigh] = [person]
          next_todo.append(neigh)
          yield neigh
    self.todo = next_todo

  def get_out_paths(self, person):
    """Get a path from self.start -> person (not including person)."""
    if person == self.start:
      yield []
    else:
      for next in self.paths[person]:
        for path in self.get_out_paths(next):
          yield path + [next]


  def get_in_paths(self, person):
    """Get a path from person -> self.start (not including person)."""
    for path in self.get_out_paths(person):
      yield list(reversed(path))


def find_connections(person1, person2, rel_types):
  bfs1 = Bfs(person1, rel_types)
  bfs2 = Bfs(person2, rel_types)

  found = False
  while not found:
    if len(bfs1.todo) <= len(bfs2.todo):
      this = bfs1
      other = bfs2
    else:
      this = bfs2
      other = bfs1

    for person in this.next_gen():
      if person in other.dists:
        # We found a path
        found = True
        for path1 in bfs1.get_out_paths(person):
          for path2 in bfs2.get_in_paths(person):
            yield path1 + [person] + path2

  print("Evaluated %d (%d around %s) & %d (%d around %s)" % (
    len(bfs1.dists), bfs1.num_steps, args.start_id, len(bfs2.dists), bfs2.num_steps, args.end_id))


parser = argparse.ArgumentParser()
parser.add_argument("start_id")
parser.add_argument("end_id")
parser.add_argument("--genetic", dest="rel_types", action="store_const", const=set(["parent", "child"]),
                    help="Only consider genetic connections (exclude marriage).")
parser.add_argument("--sibling-in-law", dest="rel_types", action="store_const", const=set(["sibling", "spouse"]),
                    help="Only consider sibling and spouse relationships (find how two people are sibling-in-laws).")
args = parser.parse_args()

db = data_reader.Database()

person1 = db.id2num(args.start_id)
person2 = db.id2num(args.end_id)

for i, connection in enumerate(find_connections(person1, person2, args.rel_types)):
  print("Connection", i + 1)
  prev_user = None
  for dist, user_num in enumerate(connection):
    rel_type = db.relationship_type(prev_user, user_num) if prev_user else ""
    print("-", dist, rel_type, db.num2id(user_num), db.name_of(user_num))
    prev_user = user_num
  print()

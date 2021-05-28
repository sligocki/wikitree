#!/usr/bin/env python3
"""
Find all of the shortest length connections between two people.
"""

import argparse
import collections
import random
import sys
import time

import graphviz

import data_reader
import partition_tools


class Bfs(object):
  def __init__(self, db, start, rel_types):
    self.db = db
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
      for neigh in self.db.relative_of_mult(person, self.rel_types):
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


def find_connections(db, person1, person2, rel_types=frozenset(["parent", "child", "sibling", "spouse"]), max_dist=None):
  bfs1 = Bfs(db, person1, rel_types)
  bfs2 = Bfs(db, person2, rel_types)

  found = False
  while not (found or len(bfs1.todo) == 0 == len(bfs2.todo)):
    if max_dist and bfs1.num_steps + bfs2.num_steps > max_dist:
      print("No connection found in", max_dist)
      return
    if len(bfs1.todo) <= len(bfs2.todo):
      this = bfs1
      other = bfs2
    else:
      this = bfs2
      other = bfs1

    for person in this.next_gen():
      if person in other.paths:
        # We found a path
        found = True
        for path1 in bfs1.get_out_paths(person):
          for path2 in bfs2.get_in_paths(person):
            yield path1 + [person] + path2

  print("Evaluated %d (%d around %s) & %d (%d around %s)" % (
    len(bfs1.paths), bfs1.num_steps, db.num2id(person1), len(bfs2.paths), bfs2.num_steps, db.num2id(person2)))


def find_connections_group(db, start, group,
                           rel_types=frozenset(["parent", "child", "sibling", "spouse"])):
  bfs = Bfs(db, start, rel_types)

  found = False
  while not (found or len(bfs.todo) == 0):
    for person in bfs.next_gen():
      if person in group:
        # We found a path
        found = True
        for path in bfs.get_out_paths(person):
          yield path + [person]

  print("Evaluated %d (%d around %s)" % (
    len(bfs.paths), bfs.num_steps, db.num2id(start)))


def print_connections(args, db, connections, plot_name=None):
  if args.plot:
    dot = graphviz.Digraph(name=plot_name)
    nodes = set()
    edges = set()

  for i, connection in enumerate(connections):
    print("Distance", len(connection) - 1)
    if args.distance_only:
      break
    else:
      print("Connection", i + 1)
      prev_user = None
      for dist, user_num in enumerate(connection):
        rel_type = db.relationship_type(prev_user, user_num) if prev_user else ""
        print(" (%3d)  %-8s %-20s %-20s %-11s %-11s" % (dist, rel_type, db.num2id(user_num), db.name_of(user_num), db.get(user_num, "birth_date"), db.get(user_num, "death_date")))

        if args.plot:
          if user_num not in nodes:
            nodes.add(user_num)
            dot.node(str(user_num), label=db.num2id(user_num))
          if prev_user and (prev_user, user_num) not in edges:
            edges.add((prev_user, user_num))
            dot.edge(str(prev_user), str(user_num), label=rel_type)

        prev_user = user_num

      print()

  print()

  if args.plot:
    dot.view()


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("person_id", nargs='+')

  parser.add_argument("--plot", action="store_true",
                      help="Produce a DOT plot of connections.")
  parser.add_argument("--distance-only", action="store_true",
                      help="Only print the distance (not connection sequence).")
  parser.add_argument("--max-dist", type=int)

  parser.add_argument("--to-partition",
                      help="Destination is partition rather than specific person.")

  parser.add_argument("--rel-types", nargs='+', default=frozenset(["parent", "child", "sibling", "spouse"]))
  parser.add_argument("--genetic", dest="rel_types", action="store_const", const=frozenset(["parent", "child"]),
                      help="Only consider genetic connections (exclude marriage).")
  parser.add_argument("--sibling-in-law", dest="rel_types", action="store_const", const=frozenset(["sibling", "spouse"]),
                      help="Only consider sibling and spouse relationships (find how two people are sibling-in-laws).")
  args = parser.parse_args()

  db = data_reader.Database()
  partition_db = partition_tools.PartitionDb()

  if args.to_partition:
    # Find shortest connection from person to any member of a partition.
    partition_type, member_id = args.to_partition.split(":")
    member_num = db.id2num(member_id)
    rep = partition_db.find_partition_rep(partition_type, member_num)
    partition_members = partition_db.list_partition(partition_type, rep)
    for start_id in args.person_id:
      print("Connections from", start_id, "to partition", args.to_partition)
      plot_name = "results/Connections_%s_%s" % (start_id, args.to_partition)
      connections = find_connections_partition(db,
                                           db.id2num(start_id),
                                           partition_members,
                                           args.rel_types)
      print_connections(args, db, connections, plot_name)

  else:
    # Find shortest connection between two people.
    for i in range(len(args.person_id) - 1):
      start_id = args.person_id[i]
      end_id = args.person_id[i + 1]
      print("Connections from", start_id, "to", end_id)
      plot_name = "results/Connections_%s_%s" % (start_id, end_id)
      connections = find_connections(db,
                                     db.id2num(start_id),
                                     db.id2num(end_id),
                                     args.rel_types,
                                     args.max_dist)
      print_connections(args, db, connections, plot_name)

if __name__ == "__main__":
  main()

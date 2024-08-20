#!/usr/bin/env python3
"""
Look over all shortest paths to every other profile. Find the number of these
paths which go through each of our relatives. This can give a sense for how
well connected into the graph a person is.

For example, if 99.9% of all their paths go through one relative, say their
paternal grandmother then their connection is brittle (any change in that chain
would have a large effect). If 33% go through father, 33% through mother
and 33% through husband, they are much more solidly connected (any change
will have a much smaller effect).
"""

import argparse
import collections
import math

from graphviz import Digraph

import bfs_tools
import data_reader
import utils


def flow_paths(db, start, max_dist):
  # Map from person -> shortest distance to start. Also used as a visited set
  # to determine if we have found this node yet.
  dists = {}
  # Map from person -> list of neighbors who can be followed to attain a
  # shortest path to start. Note their could be several such shortest paths.
  sources = {}
  # List of all people in order of connectedness.
  all_people = []

  utils.log("Running BFS")
  for node in bfs_tools.ConnectionBfs(db, start):
    if node.dist > max_dist:
      break
    dists[node.person] = node.dist
    sources[node.person] = node.prevs
    all_people.append(node.person)

  utils.log("Calculating flow counts")
  # Map from person -> set of all people who have a shortest path to start
  # which includes person. Note: there could be more than one shortest path,
  # person need only be one of them.
  on_path_to = collections.defaultdict(set)
  for person in reversed(all_people):
    # Every person is on a path to themselves :)
    on_path_to[person].add(person)

    for source in sources[person]:
      # For every neighbor on a shortest path to us (source), they are also
      # on a shortest paths to everyone we are.
      on_path_to[source].update(on_path_to[person])

  # Return mapping from people to fraction of people whom can be reached, via
  # a shortest path, through this person.
  return {person: float(len(on_path_to[person])) / len(all_people)
          for person in sources}, sources, dists

def create_dot(db, start, flows, sources, name, cutoff, node_attr_func):
  """Create a graphviz DOT file with all people who have flow >= cutoff and all of their neighbors."""
  dot = Digraph(name=("results/Flows_%s_%.2f" % (name, cutoff)))

  todo = collections.deque()
  todo.append(start)
  visited = set()
  while todo:
    person = todo.popleft()
    if person in visited:
      continue
    visited.add(person)

    node_attrs = node_attr_func(person)
    dot.node(str(person), **node_attrs)
    for source in sources[person]:
      dot.edge(str(person), str(source), label="%.2f" % flows[person])

    for neigh in db.neighbors_of(person):
      if flows[neigh] >= cutoff:
        todo.append(neigh)

  dot.view()

def try_decode_wikitree_id(db, node):
  parts = []
  for part in str(node).split("/"):
    try:
      part = db.num2id(int(part))
    except:
      pass
    parts.append(part)
  return "/".join(parts)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("id_or_nums", nargs="+")
  parser.add_argument("--max-dist", type=int)
  parser.add_argument("--cutoff", type=float, default=0.05,
                      help="Cuttoff for including connection in DOT.")
  parser.add_argument("--highlight-after-num", type=int,
                      help="Highlight profiles created after a specified profile number.")
  parser.add_argument("--version", help="Data version (defaults to most recent).")
  args = parser.parse_args()

  utils.log("Loading connections")
  db = data_reader.Database(args.version)
  if not args.max_dist:
    db.load_connections()
    args.max_dist = math.inf

  for start in args.id_or_nums:
    utils.log("Analyzing", start)
    # If a wikitree_id is passed in, translate it to a user_num.
    try:
      start = int(start)
    except:
      start = db.id2num(start)
    flows, sources, dists = flow_paths(db, start, args.max_dist)

    def node_attr_func(node):
      ret = {"label": try_decode_wikitree_id(db, node)}
      if args.highlight_after_num:
        ret["style"] = "filled"
        if node >= args.highlight_after_num:
          ret["fillcolor"] = "lightgreen"
        else:
          ret["fillcolor"] = "lightgrey"
      return ret

    utils.log("Creating DOT")
    create_dot(db, start, flows, sources, cutoff=args.cutoff,
               name=try_decode_wikitree_id(db, start),
               node_attr_func=node_attr_func)

    utils.log("Ordering people")
    # Order folks from most flow to least.
    ordered_people = reversed(sorted([(flows[person], person)
                                      for person in flows]))

    utils.log("Highest flow per distance")
    max_dist = -1
    for frac, person in ordered_people:
      if dists[person] > max_dist:
        print(f"{start}  {dists[person]:2d}  {frac:7.2%}  {try_decode_wikitree_id(db, person)}")
        max_dist = dists[person]
        if max_dist >= 20:
          break

  utils.log("Done")


if __name__ == "__main__":
  main()

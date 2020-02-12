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
import sys
import time

from graphviz import Digraph

import data_reader


def flow_paths(db, start):
  # Map from person -> shortest distance to start. Also used as a visited set
  # to determine if we have found this node yet.
  dists = {start: 0}
  # Map from person -> list of neighbors who can be followed to attain a
  # shortest path to start. Note their could be several such shortest paths.
  sources = {start: []}
  # List of all connections in order of connectedness.
  all_connections = []

  print("Running BFS", time.process_time())
  # Queue for BFS
  queue = collections.deque()
  queue.append(start)
  while queue:
    person = queue.popleft()
    dist = dists[person]
    cur_sources = sources[person]
    for neigh in db.neighbors_of(person):
      if neigh not in dists:
        # Found a shortest path.
        dists[neigh] = dist + 1
        sources[neigh] = [person]
        queue.append(neigh)
        all_connections.append(neigh)
      elif dists[neigh] == dist + 1:
        # Found another equally short path.
        sources[neigh].append(person)

  print("Calculating flow counts", time.process_time())
  # Map from person -> set of all people who have a shortest path to start
  # which includes person. Note: there could be more than one shortest path,
  # person need only be one of them.
  on_path_to = collections.defaultdict(set)
  for person in reversed(all_connections):
    # Every person is on a path to themselves :)
    on_path_to[person].add(person)

    for source in sources[person]:
      # For every neighbor on a shortest path to us (source), they are also
      # on a shortest paths to everyone we are.
      on_path_to[source].update(on_path_to[person])

  # Return mapping from people to fraction of people whom can be reached, via
  # a shortest path, through this person.
  return {person: float(len(on_path_to[person])) / len(all_connections)
          for person in sources}, sources, dists

def create_dot(db, start, flows, sources, cuttoff):
  """Create a graphviz DOT file with all people who have flow >= cuttoff and all of their neighbors."""
  dot = Digraph(name=("results/Flows_%s_%.2f" % (db.num2id(start), cuttoff)))

  todo = collections.deque()
  todo.append(start)
  visited = set()
  while todo:
    person = todo.popleft()
    if person in visited:
      continue
    visited.add(person)

    # TODO: Add readable name.
    person_label = db.num2id(person)
    dot.node(str(person), label=person_label)
    for source in sources[person]:
      # TODO: Add weights.
      dot.edge(str(person), str(source), label="%.2f" % flows[person])

    for neigh in db.neighbors_of(person):
      if flows[neigh] >= cuttoff:
        todo.append(neigh)

  dot.view()

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("user_id", nargs="+")
  parser.add_argument("--cuttoff", type=float, default=0.05,
                      help="Cuttoff for including connection in DOT.")
  args = parser.parse_args()

  db = data_reader.Database()
  db.load_connections()

  for user_id in args.user_id:
    print("Analyzing", user_id, time.process_time())
    start = db.id2num(user_id)
    flows, sources, dists = flow_paths(db, start)

    print("Creating DOT", time.process_time())
    create_dot(db, start, flows, sources, cuttoff=args.cuttoff)

    print("Ordering people", time.process_time())
    # Order folks from most flow to least.
    ordered_people = reversed(sorted([(flows[person], person)
                                      for person in flows]))

    print("Highest flow per distance", time.process_time())
    max_dist = -1
    for frac, person in ordered_people:
      if dists[person] > max_dist:
        print(user_id, dists[person], frac, db.name_of(person), db.num2id(person))
        max_dist = dists[person]
        if max_dist >= 20:
          break

  print("Done", time.process_time())

from __future__ import print_function

import collections
import sys
import time

import data_reader
import distances

def greedy_path(db, start, visited):
  """Use greedy algorithm to find a local minimum for (average distance to other
  people in graph) starting at a specific person."""
  person = start
  if person in visited:
    return
  visited.add(person)
  start_dists, _, d_mean, _ = distances.get_distances(db, person)

  best_mean = d_mean
  while person:
    print("Best neighbor\t%s\t%s\t%s" % (
            db.name_of(person), db.num2id(person), best_mean))
    best_neigh = None
    for neigh in db.neighbors_of(person):
      if neigh not in visited:
        visited.add(neigh)
        start_time = time.time()
        d_mean, d_max = distances.get_mean_dists(db, neigh)
        print(" - Person\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % (
                len(visited), db.name_of(neigh), db.num2id(neigh),
                start_dists[neigh], d_mean, d_max, time.time() - start_time))
        if d_mean < best_mean:
          best_neigh = neigh
          best_mean = d_mean
    person = best_neigh


if __name__ == "__main__":
  db = data_reader.Database()
  start_id = sys.argv[1]
  start = db.id2num(start_id)
  # Load connections into memory so that it's faster to do BFS.
  db.load_connections()
  print("Searching around", start_id, time.clock())
  greedy_path(db, start, visited=set())

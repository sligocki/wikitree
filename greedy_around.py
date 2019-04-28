import collections
import sys
import time

import csv_dump
from distances import get_distances

def greedy_path(connections, id2num, num2id, start, visited):
  """Use greedy algorithm to find a local minimum for (average distance to other
  people in graph) starting at a specific person."""
  person = start
  if person in visited:
    return
  visited.add(person)
  dists, d_mean, d_max = get_distances(connections, person)

  best_mean = d_mean
  while person:
    print "Best neighbor", num2id.get(person, person), best_mean
    best_neigh = None
    for neigh in connections.get(person, set()):
      if neigh not in visited:
        visited.add(neigh)
        start_time = time.time()
        dists, d_mean, d_max = get_distances(connections, neigh)
        print "Person", len(visited), num2id.get(neigh, neigh), \
              dists[start], "\t", \
              d_mean, d_max, time.time() - start_time
        if d_mean < best_mean:
          best_neigh = neigh
          best_mean = d_mean
    person = best_neigh


if __name__ == "__main__":
  start_id = sys.argv[1]
  connections, id2num, num2id = csv_dump.load_connections()
  start = id2num[start_id]
  greedy_path(connections, id2num, num2id, start, visited=set())

"""Load distance stats for people near a specific person."""

import collections
import sys
import time

import csv_dump
from distances import get_distances

start_id = sys.argv[1]

connections, id2num, num2id = csv_dump.load_connections()

start = id2num[start_id]

best_mean = 10000
best_mean_num = None
best_max = 10000
best_max_num = None

# Breadth first search
i = 0
queue = collections.deque()
queue.append(start)
visited = set()
while queue:
  person = queue.popleft()
  if person in visited:
    continue
  visited.add(person)

  start_time = time.time()
  dists, d_mean, d_max = get_distances(connections, person)
  print i, num2id.get(person, person), dists[start], "\t", d_mean, d_max, \
            time.time() - start_time
  if d_mean < best_mean:
    best_mean = d_mean
    best_mean_num = person
  if d_max < best_max:
    best_max = d_max
    best_max_num = person
  print num2id.get(best_mean_num, best_mean_num), "\t", best_mean
  print num2id.get(best_max_num, best_max_num), "\t", best_max
  i += 1

  for neigh in connections.get(person, set()):
    queue.append(neigh)

import time

import numpy as np

import csv_dump

connections, id2num, num2id = csv_dump.load_connections()

print "Counting edges in graph", time.clock()
num_edges = sum(len(connections[person]) for person in connections)

print "Allocating edge array", num_edges, time.clock()
edges = np.zeros((num_edges, 2), dtype=int)

print "Populating edge array", time.clock()
i = 0
for person in connections:
  person_int = int(person)
  for neigh in connections[person]:
    edges[i] = (person_int, int(neigh))
    i += 1

print "Saving edge array", time.clock()
with open("edges.npy", "wb") as f:
  np.save(f, edges)

print "Done", time.clock()

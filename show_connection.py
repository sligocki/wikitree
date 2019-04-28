import sys
import time

import csv_dump
from distances import get_distances

person1_id = sys.argv[1]
person2_id = sys.argv[2]

connections, id2num, num2id = csv_dump.load_connections()

person1 = id2num[person1_id]
person2 = id2num[person2_id]

# TODO: Optimize by searching from both people in parallel
dists, _, _, = get_distances(connections, person1)

current = person2
connection = [person2]
while dists[current] > 0:
  for neigh in connections[current]:
    if dists[neigh] < dists[current]:
      current = neigh
      connection.append(neigh)
      break
connection.reverse()

# TODO: Print all equal length connections

print "Connection from", person1_id, "to", person2_id
for p in connection:
  print dists[p], num2id[p]

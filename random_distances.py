import random
import sys
import time

import csv_dump
from distances import get_distances
import load_edges
import load_graph

connections, id2num, num2id = csv_dump.load_connections()
#connections = load_edges.load_from_edges("edges.npy")
#graph = load_graph.load_graph()

# TODO: Use flag.
if len(sys.argv) > 1:
  anchor_num = sys.argv[1]
else:
  # Queen Victoria (Hannover-14)
  anchor_num = 5291564

main_tree, anchor_mean, anchor_max = get_distances(connections, anchor_num)
print anchor_num, "{:,}".format(len(main_tree)), "\t", anchor_mean, anchor_max

best_mean = anchor_mean
best_mean_num = anchor_num
best_max = anchor_max
best_max_num = anchor_num
i = 0
while True:
  start_time = time.time()
  user = random.choice(main_tree.keys())
  dists, d_mean, d_max = get_distances(connections, user)
  print "Result", i, user, "\t", d_mean, d_max, time.time() - start_time
  if d_mean < best_mean:
    best_mean = d_mean
    best_mean_num = user
  if d_max < best_max:
    best_max = d_max
    best_max_num = user
  print "Best mean", best_mean_num, best_mean
  print "Best max", best_max_num, best_max
  i += 1

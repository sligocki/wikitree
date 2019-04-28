import random
import sys

import csv_dump
from distances import get_distances
import greedy_around

connections, id2num, num2id = csv_dump.load_connections()

# TODO: Use flag.
if len(sys.argv) > 1:
  anchor_num = sys.argv[1]
else:
  # Queen Victoria (Hannover-14)
  anchor_num = "5291564"

main_tree, anchor_mean, anchor_max = get_distances(connections, anchor_num)
print anchor_num, "{:,}".format(len(main_tree)), "\t", anchor_mean, anchor_max

visited = set()
while len(visited) < len(main_tree):
  person = random.choice(main_tree.keys())
  if person not in visited:
    greedy_around.greedy_path(connections, id2num, num2id, person, visited)

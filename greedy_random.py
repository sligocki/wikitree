import random
import sys

import data_reader
from distances import get_distances
import greedy_around

db = data_reader.Database()
db.load_connections()

anchor_id = "Tudor-4"  # King Henry
anchor = db.id2num(anchor_id)

main_tree, _, anchor_mean, anchor_max = get_distances(db, anchor)
print anchor_id, "{:,}".format(len(main_tree)), "\t", anchor_mean, anchor_max

visited = set()
while len(visited) < len(main_tree):
  person = random.choice(main_tree.keys())
  if person not in visited:
    greedy_around.greedy_path(db, person, visited)

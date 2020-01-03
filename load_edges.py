import collections
import time

import numpy as np

def load_from_edges(filename):
  print("Loading edges from file", time.process_time())
  with open(filename, "rb") as f:
    edges = np.load(f)

  print("Converting from edges into dictionary", time.process_time())
  connections = collections.defaultdict(set)
  for (a, b) in edges:
    connections[a].add(b)

  print("Finished loading connections", time.process_time())
  return connections

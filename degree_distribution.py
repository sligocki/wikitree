

import data_reader


db = data_reader.Database()
db.load_connections()

degrees = []
total_edges = 0
for user in db.connections:
  degree = len(db.connections[user])
  while len(degrees) - 1 < degree:
    degrees.append(0)
  degrees[degree] += 1
  total_edges += degree  # Note: This actually double counts edges.

print("Number of nodes", len(db.connections))
print("Number of edges (double counted)", total_edges)
print("Degree distribution:")
for degree, count in enumerate(degrees):
  print("Degree", degree, count)

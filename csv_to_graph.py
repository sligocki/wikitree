import time

import networkx as nx

import data_reader


db = data_reader.Database()
db.load_connections()

graph = nx.Graph()

visited = set()
for person in db.connections:
  visited.add(person)
  for neigh in db.connections[person]:
    # Don't add edges twice.
    if neigh not in visited:
      graph.add_edge(person, neigh)

print("Writing graph to file", time.process_time())
nx.write_adjlist(graph, "data/graph.adj.nx")

print("Done", time.process_time())

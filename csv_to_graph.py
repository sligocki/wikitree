import time

import networkx as nx

import data_reader


print("Loading DB", time.process_time())
db = data_reader.Database()
db.load_connections()

print("Building graph", time.process_time())
graph = nx.Graph()
visited = set()
for person in db.connections:
  visited.add(person)
  for neigh in db.connections[person]:
    # Don't add edges twice.
    if neigh not in visited:
      graph.add_edge(person, neigh)

print("Writing graph to file", time.process_time())
nx.write_adjlist(graph, "data/connection_graph.adj.nx")

print("Finding largest connected component", time.process_time())
max_size, main_component = max(
  (len(comp), comp) for comp in nx.connected_components(graph),
  key = lambda x: x[0])
print("Main component size:", max_size)

print("Writing main component to file", time.process_time())
main_subgraph = graph.subgraph(main_component)
nx.write_adjlist(main_subgraph, "data/main_component.adj.nx")

print("Done", time.process_time())

import time

import networkx as nx

import data_reader


print("Loading DB", time.process_time())
db = data_reader.Database()

print("Building graph", time.process_time())
graph = nx.Graph()
i = 0
for person, neigh in db.enum_connections():
  if person < neigh:
    # Don't add edges twice.
    graph.add_edge(person, neigh)
    i += 1
    if i % 1000000 == 1:
      print(f" ... {i:,} connections loaded", time.process_time())
print(f"Total graph size: {len(graph.nodes):,} Nodes {len(graph.edges):,} Edges.")

print("Writing graph to file", time.process_time())
nx.write_adjlist(graph, "data/connection_graph.adj.nx")

print("Finding largest connected component", time.process_time())
max_size, main_component = max(
((len(comp), comp) for comp in nx.connected_components(graph)),
key = lambda x: x[0])
main_subgraph = graph.subgraph(main_component)
print(f"Main component size: {len(main_subgraph.nodes):,} Nodes {len(main_subgraph.edges):,} Edges.")

print("Writing main component to file", time.process_time())
nx.write_adjlist(main_subgraph, "data/main_component.adj.nx")

print("Done", time.process_time())

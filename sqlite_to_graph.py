import time

import networkx as nx

import data_reader
import graph_tools


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
main_subgraph = graph_tools.LargestCombonent(graph)
print(f"Main component size: {len(main_subgraph.nodes):,} Nodes {len(main_subgraph.edges):,} Edges.")

print("Writing main component to file", time.process_time())
nx.write_adjlist(main_subgraph, "data/connection_graph.main.adj.nx")

print("Done", time.process_time())

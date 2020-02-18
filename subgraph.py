import collections
import itertools
import random
import sys
import time

import networkx as nx

filename = "data/connection_graph.adj.nx"

print("Loading graph", time.process_time())
g = nx.read_adjlist(filename)
print("Graph loaded", time.process_time())

def GetSubgraphAround(g, start, size):
  """Get a BFS subgraph around |start| of size |size|."""
  edge_gen = nx.bfs_edges(g, start)
  nodes = set(v for (u, v) in itertools.islice(edge_gen, size))
  return g.subgraph(nodes)

subset_nodes = list(itertools.islice(g.nodes, 10000))

size = 10
while size < g.number_of_nodes():
  print("Making random subgraph of size", size, time.process_time())
  # Pick random starting node
  start = random.choice(subset_nodes)
  sg = GetSubgraphAround(g, start, size)
  filename = "sub-%d.adj.nx" % size
  nx.write_adjlist(sg, filename)
  size *= 10

print("Done", time.process_time())

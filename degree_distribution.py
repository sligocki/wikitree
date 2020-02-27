import argparse
import collections

import networkx as nx


parser = argparse.ArgumentParser()
parser.add_argument("graph")
args = parser.parse_args()

graph = nx.read_adjlist(args.graph, create_using=nx.MultiGraph)

degree_counts = collections.defaultdict(int)
max_degree = -1
max_node = None
for node in graph.nodes():
  degree = graph.degree[node]
  degree_counts[degree] += 1
  if degree > max_degree:
    max_degree = degree
    max_node = node

print("Number of nodes:", len(graph.nodes))
print("Number of edges:", len(graph.edges))
print("Degree distribution:")
for degree, count in sorted(degree_counts.items()):
  print(" *", degree, count)
print("Node of max degree:", max_node)

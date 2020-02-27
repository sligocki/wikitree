import argparse
import collections

import networkx as nx


parser = argparse.ArgumentParser()
parser.add_argument("graph")
args = parser.parse_args()

graph = nx.read_adjlist(args.graph)

degree_counts = collections.defaultdict(int)
for node in graph.nodes():
  degree = graph.degree[node]
  degree_counts[degree] += 1

print("Number of nodes:", len(graph.nodes))
print("Number of edges:", len(graph.edges))
print("Degree distribution:")
for degree, count in sorted(degree_counts.items()):
  print("Degree", degree, count)

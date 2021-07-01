import argparse
import collections
import json
from pathlib import Path

import networkx as nx


parser = argparse.ArgumentParser()
parser.add_argument("graph")
parser.add_argument("--bipartite", action="store_true",
                    help="Analyze as a bipartite graph (distinguishing parts by leading 'Union/' in name ...)")
parser.add_argument("--save-to-json", type=Path)
args = parser.parse_args()

graph = nx.read_adjlist(args.graph, create_using=nx.MultiGraph)

degree_counts = collections.defaultdict(int)
if args.bipartite:
  degree_counts_family = collections.defaultdict(int)
max_degree = -1
max_node = None
for node in graph.nodes():
  degree = graph.degree[node]
  if args.bipartite and node.startswith("Union/"):
    degree_counts_family[degree] += 1
  else:
    degree_counts[degree] += 1
  if degree > max_degree:
    max_degree = degree
    max_node = node

if args.bipartite:
  print(f"Number of nodes (person): {sum(degree_counts.values()):_}")
  print(f"Number of nodes (family): {sum(degree_counts_family.values()):_}")
  print(f"Number of edges: {len(graph.edges):_}")
  print("Degree distribution:")
  print(" ", "Degree", "#Nodes(person)", "#Nodes(family)")
  for degree in range(1, max_degree + 1):
    print(" ", degree, degree_counts[degree], degree_counts_family[degree])
  print("Node of max degree:", max_node)

  if args.save_to_json:
    with open(args.save_to_json, "w") as f:
      json.dump({
        "Person_Nodes": [degree_counts[i] for i in range(max_degree + 1)],
        "Family_Nodes": [degree_counts_family[i] for i in range(max_degree + 1)],
      }, f)

else:
  # Normal (non-bipartite) graph
  print(f"Number of nodes: {len(graph.nodes):_}")
  print(f"Number of edges: {len(graph.edges):_}")
  print("Degree distribution:")
  for degree, count in sorted(degree_counts.items()):
    print(" ", degree, count)
  print("Node of max degree:", max_node)

  if args.save_to_json:
    with open(args.save_to_json, "w") as f:
      json.dump({
        "Nodes": [degree_counts[i] for i in range(max_degree + 1)],
      }, f)

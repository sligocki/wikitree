"""
Compare two graphs. Describes nodes/edges added/removed.
"""

import argparse
import collections
from pathlib import Path

import networkit as nk

import graph_tools
import utils


def load_node_edge_sets(filename):
  graph, names_db = graph_tools.load_graph_nk(filename)
  names = names_db.all_index2names()

  node_set = set(names[node] for node in graph.iterNodes())
  edge_set = set(frozenset([names[u], names[v]])
                 for (u, v) in graph.iterEdges())
  return node_set, edge_set

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("graph_before", type=Path)
  parser.add_argument("graph_after", type=Path)
  args = parser.parse_args()

  utils.log("Load graph_before")
  nodes_before, edges_before = load_node_edge_sets(args.graph_before)
  utils.log(f"Loaded graph with {len(nodes_before):_} nodes and {len(edges_before):_} edges")

  print()
  utils.log("Load graph_after")
  nodes_after, edges_after = load_node_edge_sets(args.graph_after)
  utils.log(f"Loaded graph with {len(nodes_after):_} nodes and {len(edges_after):_} edges")

  print()
  utils.log("Compare nodes")
  nodes_added = nodes_after - nodes_before
  print(f"# Nodes Added = {len(nodes_added):_}")
  nodes_removed = nodes_before - nodes_after
  print(f"# Nodes Removed = {len(nodes_removed):_}")

  print()
  utils.log("Compare edges")
  edges_added = edges_after - edges_before
  # Edges added to newly added nodes
  edges_added_new_nodes = {frozenset((a, b)) for (a, b) in edges_added
                           if a in nodes_added or b in nodes_added}
  # Edges added between stable nodes
  edges_added_stable_nodes = edges_added - edges_added_new_nodes

  edges_removed = edges_before - edges_after
  # Edges removed from deleted nodes
  edges_removed_old_nodes = {frozenset((a, b)) for (a, b) in edges_removed
                             if a in nodes_removed or b in nodes_removed}
  # Edges removed between stable nodes
  edges_removed_stable_nodes = edges_removed - edges_removed_old_nodes

  print(f"# Edges Added (Stable) = {len(edges_added_stable_nodes):_}")
  print(f"# Edges Removed (Stable) = {len(edges_removed_stable_nodes):_}")
  print(f"# Edges Added (New Nodes) = {len(edges_added_new_nodes):_}")
  print(f"# Edges Removed (Old Nodes) = {len(edges_removed_old_nodes):_}")

  degree_nodes_added : collections.Counter[int] = collections.Counter()
  for edge in edges_added_new_nodes:
    for node in edge:
      if node in nodes_added:
        degree_nodes_added[node] += 1
  nodes_added_of_degree = collections.defaultdict(set)
  for node, degree in degree_nodes_added.items():
    nodes_added_of_degree[degree].add(node)
  degree_distribution_added = {degree: len(nodes_added_of_degree[degree])
                               for degree in sorted(nodes_added_of_degree.keys())}

  print()
  utils.log("Degree distribution of added nodes")
  print(degree_distribution_added)

  print()
  utils.log("Examples")
  print("Example Nodes Removed:", list(nodes_removed)[:10])
  print("Example Edges Removed (Stable):", list(edges_removed_stable_nodes)[:10])

if __name__ == "__main__":
  main()

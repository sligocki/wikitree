"""
Compare two graphs. Describes nodes/edges added/removed.
"""

import argparse
from pathlib import Path

import networkx as nx

import utils


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("graph_before", type=Path)
  parser.add_argument("graph_after", type=Path)
  args = parser.parse_args()

  utils.log("Load graph_before")
  graph_before = nx.read_adjlist(args.graph_before)
  nodes_before = set(graph_before.nodes())
  edges_before = set(frozenset(edge) for edge in graph_before.edges())
  del graph_before
  utils.log(f"Loaded graph with {len(nodes_before):_} nodes and {len(edges_before):_} edges")

  print()
  utils.log("Load graph_after")
  graph_after = nx.read_adjlist(args.graph_after)
  nodes_after = set(graph_after.nodes())
  edges_after = set(frozenset(edge) for edge in graph_after.edges())
  del graph_after
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

  print()
  utils.log("Examples")
  print("Example Nodes Removed:", list(nodes_removed)[:10])
  print("Example Edges Removed (Stable):", list(edges_removed_stable_nodes)[:10])

if __name__ == "__main__":
  main()

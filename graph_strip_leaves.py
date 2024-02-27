# Iteratively strip off nodes with degree 1 from a graph until all nodes have
# larger degree. If the graph is a tree, it will disappear, othewise we will
# be left with the core which will have branches off of it.

import argparse
import collections
import time

import networkx as nx


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("graph_in")
  parser.add_argument("graph_out")
  args = parser.parse_args()

  print("Loading graph", time.process_time())
  graph = nx.read_adjlist(args.graph_in)

  print("Find leaf nodes", time.process_time())
  to_delete = set()
  for node in graph.nodes():
    if graph.degree[node] <= 1:
      to_delete.add(node)

  i = 0
  while to_delete:
    print(f"Stripping graph:  Iter {i}  # Nodes: {len(graph.nodes):,}  # Edges: {len(graph.edges):,}  {len(to_delete):,}", time.process_time())
    i += 1
    to_check = set()
    for node in to_delete:
      to_check.update(graph.neighbors(node))
      graph.remove_node(node)

    # We only need to check nodes that were adjacent to a deleted node.
    # All other nodes still have > 1 degree because none of their edges were rm-ed
    to_delete = set()
    for node in to_check:
      if graph.degree[node] <= 1:
        to_delete.add(node)

  print(f"Final graph: # Nodes: {len(graph.nodes):,}  # Edges: {len(graph.edges):,}")

  print("Saving to disk", time.process_time())
  nx.write_adjlist(graph, args.graph_out)

  print("Done", time.process_time())

main()

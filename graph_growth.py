"""
Describe how the graph grew from an old version to a new one.
"""

import argparse
import collections
from pathlib import Path

import networkx as nx

import graph_analyze
import graph_tools
import utils


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("old_graph", type=Path)
  parser.add_argument("new_graph", type=Path)
  parser.add_argument("--rate-only", action="store_true")
  args = parser.parse_args()

  utils.log("Starting")

  old_graph = graph_tools.load_graph(args.old_graph)
  utils.log(f"Loaded old_graph:  # Nodes: {old_graph.number_of_nodes():_}  # Edges: {old_graph.number_of_edges():_}")
  new_graph = graph_tools.load_graph(args.new_graph)
  utils.log(f"Loaded new_graph:  # Nodes: {new_graph.number_of_nodes():_}  # Edges: {new_graph.number_of_edges():_}")

  nodes_common = set(old_graph.nodes) & set(new_graph.nodes)
  utils.log(f"Nodes in common: {len(nodes_common):_}")

  # Degree distribution over all `nodes_common`.
  degrees_all = collections.Counter()
  # Degree distribution of nodes that were attached to (edges added, i.e. degree increased).
  degrees_attached = collections.Counter()
  for node in nodes_common:
    # We would like to iterate over all added edges, but since nodes can be
    # "renamed", new edges might not all really be new. So instead we iterate
    # over all nodes that increase in degree (gain meaningful edges).
    old_deg = old_graph.degree[node]
    new_deg = new_graph.degree[node]
    degrees_all[old_deg] += 1
    if new_deg > old_deg:
      # Add 1 for *per* additional edge added.
      # degrees_attached[old_deg] += new_deg - old_deg
      for deg in range(old_deg, new_deg):
        # Instead of treating this as 3 edges added to a degree 2 node, treat it
        # as degree 2 +1 edge, degree 3 +1 edge, degree 4 +1 edge b/c that's
        # what's really happening, we just don't have that fine-grain resolution
        # to know which order they happened in.
        degrees_attached[deg] += 1
  total_deg_all = degrees_all.total()
  total_deg_attached = degrees_attached.total()
  utils.log(f"Edges added: {total_deg_attached:_}")

  print()
  if not args.rate_only:
    print("Degree", "Attached %", "Total %", "Attached Rate", sep="\t")
  for n in range(1, 16):
    attached_ratio = degrees_attached[n] / total_deg_attached
    all_ratio = degrees_all[n] / total_deg_all
    if all_ratio > 0.0:
      attached_rate = attached_ratio / all_ratio
    else:
      attached_rate = 0.0
    if args.rate_only:
      print(attached_rate)
    else:
      print(f"{n:6_d}\t{attached_ratio:10.3%}\t{all_ratio:7.3%}\t{attached_rate:13.5f}")
  print()
  utils.log("Done")


if __name__ == "__main__":
  main()

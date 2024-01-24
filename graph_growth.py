"""
Describe the growth of a network over time.
Ex: Examine correllation between a nodes degree and it's chance of gaining an edge.
"""

import argparse
import collections
from pathlib import Path

import networkx as nx

import graph_analyze
import graph_tools
import utils


def count_degree_changes(old_graph, new_graph):
  nodes_common = set(old_graph.nodes) & set(new_graph.nodes)
  utils.log(f"  Nodes in common: {len(nodes_common):_}")

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
  return degrees_all, degrees_attached


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("graphs", type=Path, nargs="+")
  args = parser.parse_args()

  utils.log(f"Running comparison over {len(args.graphs)} timesteps")

  old_graph = graph_tools.load_graph(args.graphs[0])
  utils.log(f"Loaded {args.graphs[0]}:  # Nodes: {old_graph.number_of_nodes():_}  # Edges: {old_graph.number_of_edges():_}")

  # Degree distribution over all `nodes_common`.
  degrees_all = collections.Counter()
  # Degree distribution of nodes that were attached to (edges added, i.e. degree increased).
  degrees_attached = collections.Counter()
  for new in args.graphs[1:]:
    new_graph = graph_tools.load_graph(new)
    utils.log(f"Loaded {new}:  # Nodes: {new_graph.number_of_nodes():_}  # Edges: {new_graph.number_of_edges():_}")

    this_degrees_all, this_degrees_attached = count_degree_changes(old_graph, new_graph)
    utils.log(f"  Degree added: {this_degrees_attached.total():_}")
    degrees_all.update(this_degrees_all)
    degrees_attached.update(this_degrees_attached)

    old_graph = new_graph

  total_deg_all = degrees_all.total()
  total_deg_all_weighted = sum(deg * cnt for deg, cnt in degrees_all.items())
  total_deg_attached = degrees_attached.total()
  utils.log(f"Total Degree added: {total_deg_attached:_}")

  print()
  print("Degree", "Total %", "Attached %", "vs Uniform Model", "vs Preferential Model", sep="\t")
  for n in range(1, 16):
    attached_frac = degrees_attached[n] / total_deg_attached
    all_frac = degrees_all[n] / total_deg_all
    all_weighted_frac = n * degrees_all[n] / total_deg_all_weighted
    if degrees_all[n] > 0.0:
      vs_uniform = attached_frac / all_frac
      vs_preferential = attached_frac / all_weighted_frac
    else:
      vs_uniform = 0.0
      vs_preferential = 0.0
    print(f"{n:6_d}\t{all_frac:7.3%}\t{attached_frac:10.3%}\t{vs_uniform:16.5f}\t{vs_preferential:21.5f}")
  print()
  utils.log("Done")


if __name__ == "__main__":
  main()

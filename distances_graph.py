"""
Load distance distribution from a starting node to all others.
"""

import argparse
import collections
from pathlib import Path
import random

import networkx as nx

import graph_tools
import utils


def circle_sizes(graph, start_node, is_weighted):
  args = {}
  if is_weighted:
    args["weight"] = "weight"

  nodes = list(graph.nodes)
  circle_count = collections.Counter()
  for dist in nx.shortest_path_length(graph, start_node, **args).values():
    # Note: We only allow int weights, so all distances should be ints.
    circle_count[int(dist)] += 1
  return circle_count

def mean_distr(distr):
  return sum(val * count for val, count in distr.items()) / sum(distr.values())

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("graph", type=Path)
  parser.add_argument("start_nodes", nargs="*")
  args = parser.parse_args()

  utils.log("Loading graph")
  graph = graph_tools.load_graph(args.graph)
  is_weighted = any("weight" in data for u, v, data in graph.edges(data=True))

  utils.log(f"# Nodes = {graph.number_of_nodes():_}")
  utils.log(f"# Edges = {graph.number_of_edges():_}")

  if args.start_nodes:
    for start_node in args.start_nodes:
      utils.log("Loading circle sizes for", start_node)
      circles = circle_sizes(graph, start_node, is_weighted)
      utils.log("Mean distance:", mean_distr(circles))
      circles_list = [circles[dist] for dist in range(max(circles.keys()) + 1)]
      utils.log(circles_list)

  else:
    # Iterate start_nodes in random order compiling cumulative results.
    nodes = list(graph.nodes)
    random.shuffle(nodes)
    all_dist_count = collections.Counter()

    for i, start_node in enumerate(nodes):
      utils.log(f"Loading circle sizes for node {i:_} / {len(nodes):_}: {start_node}")
      this_dist_count = circle_sizes(graph, start_node, is_weighted)

      utils.log("Mean distance (this node):", mean_distr(this_dist_count))
      utils.log([this_dist_count[dist]
                 for dist in range(max(this_dist_count.keys()) + 1)])

      all_dist_count.update(this_dist_count)
      utils.log("Mean distance (overall):", mean_distr(all_dist_count))
      utils.log([all_dist_count[dist]
                 for dist in range(max(all_dist_count.keys()) + 1)])

  utils.log("Done")

if __name__ == "__main__":
  main()

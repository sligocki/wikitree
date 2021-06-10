"""
Produce random graph

Initially, we're only supporting non-preferential attachment (producing
exponential degree distribution). We might extend to other methods later.
"""

import argparse
import collections
import math
from pathlib import Path
import random

import networkx as nx

import utils


def build_exponential(num_nodes, edges_per_node):
  # We always add one edge to each added node. Then we can add some extras anywhere.
  extra_edges_per_node = edges_per_node - 1
  assert extra_edges_per_node >= 0
  # After adding each node, we repeatedly try adding edges until we fail
  # each time adding an edge with prob_edge chance.
  # So the expected number of edges added (per node) is
  #   prob_edge + prob_edge^2 + prob_edge^3 + ... = prob_edge / (1 - prob_edge)
  # Setting that equal to extra_edges_per_node and re-arranging we get:
  prob_edge = extra_edges_per_node / (1 + extra_edges_per_node)

  graph = nx.Graph()
  for node in range(num_nodes):
    graph.add_node(node)
    # Add anchor edge
    if node > 0:
      other_node = random.randrange(node)
      graph.add_edge(node, other_node)
    # Add more edges stochastically
    while random.random() < prob_edge:
      # Use non-preferential attachment:
      #   Pick two end of edge uniformly at random among all nodes.
      node_a = random.randrange(node + 1)
      node_b = random.randrange(node + 1)
      graph.add_edge(node_a, node_b)

  return graph


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("type", choices=["exponential"])
  parser.add_argument("num_nodes", type=int)
  parser.add_argument("edges_per_node", type=float)
  parser.add_argument("output_graph", type=Path)
  args = parser.parse_args()

  utils.log("Building graph")
  graph = build_exponential(num_nodes = args.num_nodes,
                            edges_per_node = args.edges_per_node)

  utils.log("Writing graph")
  nx.write_adjlist(graph, args.output_graph)

if __name__ == "__main__":
  main()

"""Project a nuclear bipartite graph onto one of it's parts (the one with Unions)."""

import argparse
import csv
import time

import networkx as nx
from networkx.algorithms import bipartite

import utils


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("bipartite")
  parser.add_argument("projected_graph")
  args = parser.parse_args()

  utils.log("Loading graph")
  bp = nx.read_adjlist(args.bipartite)
  utils.log(f"Loaded graph:  # Nodes: {len(bp.nodes):_}  # Edges: {len(bp.edges):_}")

  utils.log("Finding family nodes")
  family_nodes = [node for node in bp.nodes
                  if node.startswith("Union/")]
  utils.log("Found", len(family_nodes), "family nodes")

  utils.log("Projecting graph")
  projected = bipartite.projected_graph(bp, family_nodes)

  utils.log(f"Writing graph:  # Nodes: {len(projected.nodes):_}  # Edges: {len(projected.edges):_}")
  nx.write_adjlist(projected, args.projected_graph)

  utils.log("Finished")

main()

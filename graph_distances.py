"""
Compute centrality of random nodes and save to sqlite DB.
"""

import argparse
import collections
import itertools
import random
import time

import networkx as nx

import distances_db


def MeasureAndLogCentrality(graph, graph_name, node, randomly_sampled):
  centrality = nx.closeness_centrality(graph, u=node)
  mean_dist = 1./centrality
  distances_db.LogDistance(graph_name, node, mean_dist, randomly_sampled)
  return centrality

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("graph")
  args = parser.parse_args()

  print("Loading graph", time.process_time())
  graph = nx.read_adjlist(args.graph)
  print(f"Initial graph:  # Nodes: {len(graph.nodes):,}  # Edges: {len(graph.edges):,}", time.process_time())

  nodes = list(graph.nodes)
  random.shuffle(nodes)

  for i, node in enumerate(nodes):
    centrality = MeasureAndLogCentrality(graph, args.graph, node, randomly_sampled=True)
    print(f"Centrality  {i:6,}  {node:20} {centrality:7.4f} {1./centrality:=10.2f} {time.process_time():10.1f}")

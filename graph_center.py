"""
Attempt to find center of graph and estimate related metrics.
"""

import argparse
import collections
import itertools
import random
import time

import networkx as nx

import graph_distances


def FindCentroid(graph, seed_nodes, num_overlap):
  # BFS from all of them until we find a node which is within the BFS
  # neighborhood of a majority of the points. This is our estimated center.
  # map: node -> which seed node BFSes have visited it.
  visited = collections.defaultdict(set)
  for seed_node in seed_nodes:
    visited[seed_node].add(seed_node)
  num_steps = 0
  bfs = {seed_node : nx.bfs_predecessors(graph, seed_node) for seed_node in seed_nodes}
  nodes_yielded = set()
  while True:
    for seed_node in seed_nodes:
      try:
        node, _ = next(bfs[seed_node])
        visited[node].add(seed_node)
        num_steps += 1
        if len(visited[node]) > len(seed_nodes) / 2. and node not in nodes_yielded:
          yield node
          nodes_yielded.add(node)
          if len(nodes_yielded) >= num_overlap:
            return
      except StopIteration:
        pass

parser = argparse.ArgumentParser()
parser.add_argument("graph")
parser.add_argument("num_seed_nodes", type=int)
parser.add_argument("num_overlap", type=int)
parser.add_argument("--absolute", action="store_true")
args = parser.parse_args()

print("Loading graph", time.process_time())
graph = nx.read_adjlist(args.graph)
print(f"Initial graph:  # Nodes: {len(graph.nodes):,}  # Edges: {len(graph.edges):,}", time.process_time())

if args.absolute:
  print("Finding absolute center", time.process_time())
  foo = nx.closeness_centrality(graph)
  center, max_closeness = max(foo.items(), key = lambda x: x[1])
  print(f"Centrality\t{center}\t{max_closeness:.4f}\t{1./max_closeness:.2f}")

else:
  print(f"Estimating center based on {args.num_seed_nodes} points", time.process_time())
  for i in itertools.count():
    print("Try", i, time.process_time())
    # Pick N random nodes.
    seed_nodes = random.sample(list(graph.nodes), args.num_seed_nodes)

    for node in FindCentroid(graph, seed_nodes, args.num_overlap):
      centrality = graph_distances.MeasureAndLogCentrality(graph, args.graph, node, randomly_sampled=False)
      print(f"Centrality  {node:20} {centrality:7.4f} {1./centrality:=10.2f} {time.process_time():10.1f}")

print("Done", time.process_time())

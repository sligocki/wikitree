"""
Attempt to find center of graph and estimate related metrics.
"""

import argparse
import collections
from collections.abc import Collection
import itertools
import random
import time
from typing import Iterator

import networkx as nx


Node = str

def FindCentroid(graph : nx.Graph, seed_nodes : Collection[Node], num_overlap : int
                 ) -> Iterator[Node]:
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

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("graph")
  parser.add_argument("--absolute", action="store_true")
  parser.add_argument("--num-seed-nodes", type=int, default=1001)
  parser.add_argument("--num-overlap", type=int, default=10)
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
    if args.num_seed_nodes == 0 or args.num_seed_nodes >= len(graph.nodes):
      seed_nodes = list(graph.nodes)
    else:
      # Pick N random nodes.
      seed_nodes = random.sample(list(graph.nodes), args.num_seed_nodes)

    for node in FindCentroid(graph, seed_nodes, args.num_overlap):
      centrality = nx.closeness_centrality(graph, u=node)
      print(f"Centrality  {node:20} {centrality:7.4f} {1./centrality:=10.2f} {time.process_time():10.1f}")

  print("Done", time.process_time())

main()

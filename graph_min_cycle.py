"""
Find minimal cycles through a given node in graph.
"""

import argparse
import collections
import random

import networkx as nx

import graph_core
import graph_tools
import utils


def min_cycle(graph, start_node):
  # Map node -> path
  paths = {start_node: []}
  todos = []

  # Start us off with neighbors of start_node (the path directions).
  for dir in graph.adj[start_node]:
    paths[dir] = [dir]
    todos.append(dir)
  dirs_seen = set(todos)

  while todos and len(dirs_seen) > 1:
    new_todos = []
    dirs_seen = set()
    for node in todos:
      path = paths[node]
      for neigh in graph.adj[node]:
        if neigh in paths:
          # Found a cycle.
          path_neigh = paths[neigh]
          if path_neigh and path[0] != path_neigh[0]:
            # The cycle goes through start_node.
            return [start_node] + path + list(reversed(path_neigh))

        else:  # neigh not yet visited
          paths[neigh] = path + [neigh]
          new_todos.append(neigh)
          dirs_seen.add(path[0])

    todos = new_todos

  # No cycle
  return None

def check_geodesic(graph, cycle):
  """Is this a geodesic cycle? Meaning, is this a cycle where, for any two nodes on the cycle, the shortest path remains on the cycle."""
  n = len(cycle)
  d, r = divmod(n, 2)
  if r == 0:
    antipodes = [(i, i+d) for i in range(d)]
  else:
    antipodes = [(i, (i+d) % n) for i in range(n)]
  for a, b in antipodes:
    dist = nx.shortest_path_length(graph, cycle[a], cycle[b])
    if dist != d:
      return cycle[a], cycle[b], dist


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("graph")
  parser.add_argument("nodes", nargs="*")
  args = parser.parse_args()

  utils.log("Loading graph")
  graph = graph_tools.load_graph(args.graph)
  utils.log(f"Initial graph:  # Nodes: {graph.number_of_nodes():_}  # Edges: {graph.number_of_edges():_}")

  graph = graph_core.RemoveRays(graph)
  utils.log(f"Shrunken graph:  # Nodes: {graph.number_of_nodes():_}  # Edges: {graph.number_of_edges():_}")

  if args.nodes:
    for node in args.nodes:
      utils.log("Searching for cycle through", node)
      cycle = min_cycle(graph, node)
      utils.log("Min cycle", node, len(cycle), cycle)

  else:
    nodes = list(graph.nodes)
    random.shuffle(nodes)
    max_min_cycle = -1
    cycle_lengths = collections.Counter()
    for i, node in enumerate(nodes):
      if i % 1_000 == 0:
        utils.log("Checkpoint:", i, " ".join(f"{n}:{cycle_lengths[n]:_}" for n in sorted(cycle_lengths.keys())))

      cycle = min_cycle(graph, node)
      if not cycle:
        cycle_lengths[0] += 1
      else:
        cycle_lengths[len(cycle)] += 1
        if len(cycle) > max_min_cycle:
          utils.log("Cycle", i, node, len(cycle), cycle[:6])
          max_min_cycle = len(cycle)
        elif len(cycle) >= 100:
          utils.log("Cycle", i, node, len(cycle), cycle[:6])

  utils.log("Done")

if __name__ == "__main__":
  main()

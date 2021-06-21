"""
Find minimal cycles through a given node in graph.
"""

import argparse
import random

import networkx as nx

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


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("graph")
  parser.add_argument("nodes", nargs="*")
  args = parser.parse_args()

  utils.log("Loading graph")
  graph = graph_tools.load_graph(args.graph)
  utils.log(f"Initial graph:  # Nodes: {graph.number_of_nodes():_}  # Edges: {graph.number_of_edges():_}")

  if args.nodes:
    for node in args.nodes:
      utils.log("Searching for cycle through", node)
      cycle = min_cycle(graph, node)
      utils.log("Min cycle", node, len(cycle), cycle)

  else:
    nodes = list(graph.nodes)
    random.shuffle(nodes)
    max_min_cycle = -1
    for i, node in enumerate(nodes):
      cycle = min_cycle(graph, node)
      if not cycle:
        utils.log("No cycle through", node)
      elif len(cycle) > max_min_cycle:
        utils.log("Min cycle", i, node, len(cycle))
        max_min_cycle = len(cycle)

  utils.log("Done")

if __name__ == "__main__":
  main()

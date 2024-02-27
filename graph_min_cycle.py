"""
Find minimal cycles through a given node or edge in graph.
"""

import argparse
import collections
from collections.abc import Set
import random
import sys
from typing import Any

import networkx as nx

import data_reader
import graph_tools
import utils


Node = str
Edge = tuple[Node, Node]

def edge(u : Node, v : Node) -> Edge:
  return tuple(sorted((u, v)))  # type: ignore[return-value]

def path_from_parents(parents, node : Node) -> list[Node]:
  path = []
  while node:
    path.append(node)
    node = parents[node]
  return path

def min_path(graph : nx.Graph, colors : dict[Node, Any], ignore_edges : Set[Edge]
             ) -> list[Node] | None:
  """Find smallest path in `graph` which connects two nodes of different color.
  Colors are spread via adjacency (ignoring nodes already in `colors`)."""
  parents : dict[Node, Any] = {n: None for n in colors}
  todos = list(colors.keys())
  colors_seen = set(colors.values())
  while todos and len(colors_seen) > 1:
    new_todos = []
    # All colors used in this layer. We keep track to allow early exit if all
    # but one color die out.
    colors_seen = set()
    for node in todos:
      for neigh in graph.adj[node]:
        if edge(node, neigh) not in ignore_edges:
          if neigh not in colors:
            parents[neigh] = node
            colors[neigh] = colors[node]
            colors_seen.add(colors[node])
            new_todos.append(neigh)

          elif colors[node] != colors[neigh]:
            # We found a cycle!
            return list(reversed(path_from_parents(parents, node))) + path_from_parents(parents, neigh)

    todos = new_todos

  # No cycle
  return None

def min_cycle_edge(graph : nx.Graph, e : Edge) -> list[Node] | None:
  """Find smallest cycle in `graph` containing edge `e`."""
  u, v = e
  colors = {u: u, v: v}
  return min_path(graph, colors, ignore_edges = {edge(u, v)})

def min_cycle_node(graph : nx.Graph, start_node : Node) -> list[Node] | None:
  """Find smallest cycle in `graph` containing node `start_node`."""
  colors = {}
  ignore_edges = set()
  for neigh in graph.adj[start_node]:
    colors[neigh] = neigh
    ignore_edges.add(edge(start_node, neigh))

  path = min_path(graph, colors, ignore_edges)
  if path:
    return [start_node] + path
  else:
    return None


def check_geodesic(graph : nx.Graph, cycle : list[Node]) -> tuple[Node, Node, int] | None:
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


def print_cycle(db : data_reader.Database, i, e, cycle : list[Node]) -> None:
  profiles = []
  for node in cycle[-3:] + cycle[:3]:
    if not node.startswith("Union"):
      profiles.append(db.num2id(int(node)))
  utils.log("Cycle", i, e, len(cycle), min(cycle), ": ...", *profiles, "...")


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("graph")
  parser.add_argument("nodes", nargs="*",
                      help="If empty, read nodes from stdin (one per line).")
  parser.add_argument("--all", action="store_true",
                      help="Search for min cycles through all edges")
  parser.add_argument("--version", help="Data version (defaults to most recent).")
  args = parser.parse_args()

  utils.log("Loading graph")
  graph = graph_tools.load_graph(args.graph)
  utils.log(f"Loaded graph:  # Nodes: {graph.number_of_nodes():_}  # Edges: {graph.number_of_edges():_}")

  if args.all:
    db = data_reader.Database(args.version)

    # If no nodes are specified, look for all min cycles.
    # We search over all edges for a more complete view.
    # We can safely ignore edges with both nodes degree 2 because those are
    # redundant with results from other edges.
    edges = list((u, v) for (u, v) in graph.edges
                 if graph.degree[u] > 2 or graph.degree[v] > 2)
    random.shuffle(edges)
    utils.log(f"Searching through {len(edges):_} edges")
    max_min_cycle = -1
    cycle_lengths : collections.Counter[int] = collections.Counter()
    for i, e in enumerate(edges):
      if i % 10_000 == 0:
        utils.log(f"Checkpoint: {i:_}",
                  " ".join(f"{n}:{cycle_lengths[n]:_}"
                           for n in sorted(cycle_lengths.keys())))

      cycle = min_cycle_edge(graph, e)
      if not cycle:
        cycle_lengths[0] += 1
        utils.log("No cycles", i, e)
      else:
        cycle_lengths[len(cycle)] += 1
        if len(cycle) > max_min_cycle:
          print_cycle(db, i, e, cycle)
          max_min_cycle = len(cycle)
        elif len(cycle) >= 100 or len(cycle) <= 2:
          print_cycle(db, i, e, cycle)

    utils.log("Total:", i, " ".join(f"{n}:{cycle_lengths[n]:_}"
                                    for n in sorted(cycle_lengths.keys())))

  else:
    if args.nodes:
      for node in args.nodes:
        utils.log("Searching for cycle through", node)
        cycle = min_cycle_node(graph, node)
        if cycle:
          utils.log("Min cycle", node, len(cycle), cycle)
        else:
          utils.log("No cylces through", node)

    else:
      for line in sys.stdin:
        node = line.strip()
        utils.log("Searching for cycle through", node)
        cycle = min_cycle_node(graph, node)
        if cycle:
          utils.log("Min cycle", node, len(cycle), cycle)
        else:
          utils.log("No cylces through", node)


  utils.log("Done")

if __name__ == "__main__":
  main()

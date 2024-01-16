"""
Get the "topological core" of this graph.

The "topological core" is an idea I came up with for isolating the
"topologically interesting" parts of a graph. We get to it by iteratively
removing leaf nodes and collapsing linear paths:
 * For leaf nodes (nodes of degree 1): We delete the node and it's one edge.
 * For path nodes (nodes of degree 2): We "lift" the node (delete it and
   connect its former neighbors).
 * All self-edges or duplicate edges produced this way are omitted.
 * The process is repeated until all nodes are degree >= 3 (or, vacuously,
   until there are no nodes left).

This shrinks the graph down to a tight core which is interconnected in
non-trivial ways.

Every node from the original graph can be associated with either a node or
edge in the core graph.
 * If node A is associated with node B in the core graph, that means that
   removing node B from the original graph would separate A from all other
   core nodes. In other words, node A is connected into the core only through
   gateway node B.
 * If node C is associated with edge DE in the core graph, that means that
   removing nodes D & E from the original graph would separate C from the
   other core nodes. In ohter words, node C is connected into the core
   through both gateway nodes D & E.
 * Any node which is connected to the core through >2 gateway nodes will be
   in the core itself.
"""

import argparse
import csv
from pathlib import Path
import time

import networkx as nx

import graph_tools
import utils


def CollectRay(graph, node, previous=None):
  path = []
  # Follow path until we reach a fork (or dead end or loop).
  while not previous or graph.degree[node] == 2:
    if node in path:
      # We found a loop!
      return None, path
    path.append(node)
    (neighbor,) = set(graph.adj[node].keys()) - set([previous])
    previous = node
    node = neighbor
  return node, path

def CollectPath(graph, node):
  """Follow a path from node to both ends. Return the pair of ends and
  list of nodes in the path."""
  assert graph.degree[node] == 2
  neigh_a, neigh_b = graph.adj[node].keys()
  end_a, path_a = CollectRay(graph, neigh_a, previous=node)
  end_b, path_b = CollectRay(graph, neigh_b, previous=node)
  return (end_a, end_b), (list(reversed(path_a)) + [node] + path_b)

def ContractGraph(graph, rep_nodes):
  # Note: We may delete more nodes than to_delete.
  to_delete = set()
  for node in graph.nodes:
    if graph.degree[node] <= 2:
      to_delete.add(node)

  for node in to_delete:
    if node in graph.nodes:
      if graph.degree[node] == 0:
        # Strip all isolated nodes directly.
        graph.remove_node(node)
        del rep_nodes[node]
      elif graph.degree[node] == 1:
        end, path = CollectRay(graph, node)
        for n in path:
          rep_nodes[end].update(rep_nodes[n])
          del rep_nodes[n]
        graph.remove_nodes_from(path)
      else:
        assert graph.degree[node] == 2, (node, graph.degree[node])
        # Lift all path nodes. Get full linear path and two ends.
        # Note: path may not be a subset of to_delete since the degrees of
        # some nodes may have changed since we collected to_delete.
        (end_a, end_b), path = CollectPath(graph, node)
        dist = nx.path_weight(graph, [end_a] + path + [end_b], "weight")
        for n in path:
          for end in (end_a, end_b):
            if end is not None:
              rep_nodes[end].update(rep_nodes[n])
          del rep_nodes[n]
        # Directly connect the two ends together
        graph.add_edge(end_a, end_b, weight=dist)
        # Strip all degree 2 nodes in path.
        graph.remove_nodes_from(path)

  # Return True if any nodes were deleted.
  # Note: # nodes deleted is >= len(to_delete)
  return len(to_delete) > 0

def FindCore(graph):
  """Iteratively contract the graph until we reach the core."""
  # Convert to weighted multigraph.
  graph = nx.MultiGraph(graph)
  nx.set_edge_attributes(graph, values = 1, name = 'weight')
  # Map: core nodes -> nodes that collapse into this core node
  rep_nodes = {node: set([node]) for node in graph.nodes}
  while ContractGraph(graph, rep_nodes):
    pass
  return graph, rep_nodes


def RemoveRays(graph):
  """Remove all rays from graph."""
  points = set()
  for node in graph.nodes:
    if graph.degree[node] == 1:
      points.add(node)

  for node in points:
    end, path = CollectRay(graph, node)
    graph.remove_nodes_from(path)

  return graph


def degree_distr(graph, max_degree):
  degree_counts = [0] * (max_degree + 1)
  for node in graph.nodes:
    degree = min(graph.degree[node], max_degree)
    degree_counts[degree] += 1
  return degree_counts

def degree_distr_str(graph, max_degree=6) -> str:
  degree_counts = degree_distr(graph, max_degree)
  count_strs = [f"{degree}:{degree_counts[degree]:_}"
                for degree in range(max_degree)]
  count_str = " ".join(count_strs)
  return f"  Degree dist: {count_str} {max_degree}+:{degree_counts[max_degree]:_}"


def num_dup_edges(graph : nx.MultiGraph) -> int:
  """Count number of duplicate edges (edges beyond the first between any given
  pair of nodes.)"""
  # Count total number of non-duplicate edges (i.e. unique pairs of nodes
  # connected by at least one edge).
  num_unique_edges = len(frozenset(
    frozenset((u, v)) for (u, v, id) in graph.edges))
  return len(graph.edges) - num_unique_edges


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("graph_in", type=Path)
  args = parser.parse_args()

  graph_dir = args.graph_in.parent

  utils.log("Loading graph")
  graph = graph_tools.load_graph(args.graph_in)
  utils.log(f"Loaded graph:  {len(graph.nodes):_} Nodes / {len(graph.edges):_} Edges")
  utils.log(degree_distr_str(graph))

  graph = graph_tools.largest_component(graph)
  utils.log(f"Main component:  {len(graph.nodes):_} Nodes / {len(graph.edges):_} Edges")
  utils.log(degree_distr_str(graph))

  basename = graph_dir / "connect"
  filename = graph_tools.write_graph(graph, basename)
  utils.log(f"  Saved main component to {str(filename)}")

  graph = graph_tools.largest_bicomponent(graph)
  utils.log(f"Main bicomponent:  {len(graph.nodes):_} Nodes / {len(graph.edges):_} Edges")
  utils.log(degree_distr_str(graph))

  basename = graph_dir / "biconnect"
  filename = graph_tools.write_graph(graph, basename)
  utils.log(f"  Saved main bicomponent to {str(filename)}")

  # Map: core nodes -> nodes that collapse into this core node
  graph, rep_nodes = FindCore(graph)
  utils.log(f"Topological Core:  {len(graph.nodes):_} Nodes / {len(graph.edges):_} Edges / {num_dup_edges(graph):_} Duplicate edges / {nx.number_of_selfloops(graph):_} Selfloops")
  utils.log(degree_distr_str(graph))

  basename = graph_dir / "topo"
  filename = graph_tools.write_graph(graph, basename)
  utils.log(f"  Saved topo to {str(filename)}")

  filename = graph_dir / "topo.collapse.csv"
  with open(filename, "w") as f:
    csv_out = csv.DictWriter(f, ["core_node", "sub_node"])
    csv_out.writeheader()
    for core_node in rep_nodes:
      for sub_node in rep_nodes[core_node]:
        csv_out.writerow({
          "core_node": core_node,
          "sub_node": sub_node,
        })
  utils.log(f"  Saved node collapse info to {str(filename)}")


if __name__ == "__main__":
  main()

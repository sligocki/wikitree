"""
Get the topological core of this graph.

The core is defined by iteratively removing leaf nodes and shortening paths.
 * For leaf nodes (nodes of degree 1): We delete the node and it's one edge.
 * For path nodes (nodes of degree 2): We lift the node (delete it and
   connect its former neighbors).
 * All self-edges or repeated edges produced this way are omitted.
 * The process is repeated until all nodes are degree >= 3 (or, vacuously,
   until there are no nodes left)

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
 * Any node which is connected to the core through > 2 gateway nodes is
   by definition a core node itself.
"""

import argparse
import collections
import time

import networkx as nx


def PrintDegreeDist(graph, max_degree=4):
  degree_counts = [0] * (max_degree + 1)
  for node in graph.nodes:
    degree = min(graph.degree[node], max_degree)
    degree_counts[degree] += 1
  message = [f"{degree}:{degree_counts[degree]:,}"
             for degree in range(max_degree)]
  print(" Degree dist:", *message, f"{max_degree}+:{degree_counts[max_degree]:,}")

def CollectRay(graph, node, previous):
  path = set()
  # Follow path until we reach a fork (or dead end).
  while graph.degree[node] == 2:
    path.add(node)
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
  return (end_a, end_b), (path_a | path_b | set([node]))

def ContractGraph(graph):
  print(f"Contracting graph:  # Nodes: {len(graph.nodes):,}  # Edges: {len(graph.edges):,}", time.process_time())
  PrintDegreeDist(graph)

  print("Collect leaf/path nodes", time.process_time())
  # Note: We may delete more nodes than to_delete.
  to_delete = set()
  for node in graph.nodes:
    if graph.degree[node] <= 2:
      to_delete.add(node)

  print(f"Stripping ({len(to_delete):,}+) nodes", time.process_time())
  for node in to_delete:
    if node in graph.nodes:
      if graph.degree[node] <= 1:
        # Strip all leaf nodes directly.
        graph.remove_node(node)
      else:
        assert graph.degree[node] == 2, (node, graph.degree[node])
        # Lift all path nodes. Get full linear path and two ends.
        # Note: path may not be a subset of to_delete since the degrees of
        # some nodes may have changed since we collected to_delete.
        (end_a, end_b), path = CollectPath(graph, node)
        # Directly connect the two ends together (unless that would be a
        # self-edge or multi-edge, in which case we omit it.)
        if end_a != end_b and not graph.has_edge(end_a, end_b):
          graph.add_edge(end_a, end_b)
        # Strip all degree 2 nodes in path.
        graph.remove_nodes_from(path)

  # Return True if any nodes were deleted.
  # Note: # nodes deleted is >= len(to_delete)
  return len(to_delete) > 0


parser = argparse.ArgumentParser()
parser.add_argument("graph_in")
parser.add_argument("graph_out")
args = parser.parse_args()

print("Loading graph", time.process_time())
graph = nx.read_adjlist(args.graph_in)
print(f"Initial graph:  # Nodes: {len(graph.nodes):,}  # Edges: {len(graph.edges):,}", time.process_time())

# Iteratively contract the graph until we reach the core.
while ContractGraph(graph):
  pass

print(f"Final graph:  # Nodes: {len(graph.nodes):,}  # Edges: {len(graph.edges):,}", time.process_time())

print("Saving to disk", time.process_time())
nx.write_adjlist(graph, args.graph_out)

print("Done", time.process_time())

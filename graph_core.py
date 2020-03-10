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

def CollectRay(graph, node, previous=None):
  path = set()
  # Follow path until we reach a fork (or dead end).
  while not previous or graph.degree[node] == 2:
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

def ContractGraph(graph, rep_nodes):
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
        for n in path:
          for end in (end_a, end_b):
            rep_nodes[end].update(rep_nodes[n])
          del rep_nodes[n]
        # Directly connect the two ends together (unless that would be a
        # self-edge or multi-edge, in which case we omit it.)
        if end_a != end_b and not graph.has_edge(end_a, end_b):
          graph.add_edge(end_a, end_b)
        # Strip all degree 2 nodes in path.
        graph.remove_nodes_from(path)

  # Return True if any nodes were deleted.
  # Note: # nodes deleted is >= len(to_delete)
  return len(to_delete) > 0

def print_sizes_summary(core_to_nodes):
  # List of core nodes sorted by # of nodes collapsed into them.
  sizes = [(len(nodes), core)
           for core, nodes in core_to_nodes.items()]
  sizes.sort()
  for p in (0.0, 0.5, 0.75, 0.9, 0.99, 0.999, 0.9999, 0.99999, 1.0):
    index = int(p * (len(sizes) - 1))
    size, _ = sizes[index]
    print(f" * {p:8%}  {size:10,}")
  print("Largest rep nodes:")
  for n in range(20):
    size, core = sizes[len(sizes) - 1 - n]
    print(f" * {size:10,}   {core}")


parser = argparse.ArgumentParser()
parser.add_argument("graph_in")
parser.add_argument("graph_out")
args = parser.parse_args()

print("Loading graph", time.process_time())
graph = nx.read_adjlist(args.graph_in)
print(f"Initial graph:  # Nodes: {len(graph.nodes):,}  # Edges: {len(graph.edges):,}", time.process_time())

# Iteratively contract the graph until we reach the core.
# Map: core nodes -> nodes that collapse into this core node
rep_nodes = {node: set([node]) for node in graph.nodes}
while ContractGraph(graph, rep_nodes):
  pass

print(f"Final graph:  # Nodes: {len(graph.nodes):,}  # Edges: {len(graph.edges):,}", time.process_time())

print("Saving to disk", time.process_time())
nx.write_adjlist(graph, args.graph_out)

print("Summarizing nodes collapsed into each node", time.process_time())
# Map: all nodes -> set of core nodes they were collapsed into (1 or 2).
core_of = collections.defaultdict(set)
for core_node in rep_nodes:
  for sub_node in rep_nodes[core_node]:
    core_of[sub_node].add(core_node)
# Map: all nodes -> # of core nodes they collapse into.
counts = collections.defaultdict(int)
for node in core_of:
  counts[len(core_of[node])] += 1
print(f"core_of: {len(core_of):,} {counts[1]:,} {counts[2]:,}")
print("rep_nodes:")
print_sizes_summary(rep_nodes)

# Map: core node -> nodes that only collapse into this node
rep_unique_nodes = collections.defaultdict(set)
# Map: pair of core nodes -> nodes that collapse into both of these nodes
rep_edges = collections.defaultdict(set)
for node, core_nodes in core_of.items():
  if len(core_nodes) == 1:
    core_node, = tuple(core_nodes)
    rep_unique_nodes[core_node].add(node)
  else:
    assert len(core_nodes) == 2, len(core_nodes)
    rep_edges[frozenset(core_nodes)].add(node)
print("rep_unique_nodes:")
print_sizes_summary(rep_unique_nodes)
print("rep_edges:")
print_sizes_summary(rep_edges)

print("Done", time.process_time())

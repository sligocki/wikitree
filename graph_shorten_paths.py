# Iteratively lift nodes with degree 2 from a graph.
#
# Ex: If node B originally had two edges AB & BC. Remove node B and add an
# edge AC.
#
# This preserves the topology of the graph, but shinks all linear paths to
# length 1 between junctions.

import argparse
import collections
import time

import networkx as nx


def collect_ray(graph, node, previous):
  path = set()
  # Follow path until we reach a fork (or dead end).
  while graph.degree[node] == 2:
    path.add(node)
    (neighbor,) = set(graph.adj[node].keys()) - set([previous])
    previous = node
    node = neighbor
  return node, path

def collect_path(graph, node):
  """Follow a path from node to both ends. Return the pair of ends and
  list of nodes in the path."""
  assert graph.degree[node] == 2
  neigh_a, neigh_b = graph.adj[node].keys()
  end_a, path_a = collect_ray(graph, neigh_a, previous=node)
  end_b, path_b = collect_ray(graph, neigh_b, previous=node)
  return (end_a, end_b), (path_a | path_b | set([node]))


parser = argparse.ArgumentParser()
parser.add_argument("graph_in")
parser.add_argument("graph_out")
args = parser.parse_args()

print("Loading graph", time.process_time())
graph = nx.MultiGraph(nx.read_adjlist(args.graph_in))
print(f"Initial graph: # Nodes: {len(graph.nodes):,}  # Edges: {len(graph.edges):,}")

print("Find path nodes", time.process_time())
to_delete = set()
for node in graph.nodes:
  if graph.degree[node] == 2:
    to_delete.add(node)

print(f"Stripping {len(to_delete):,} path nodes", time.process_time())
for node in to_delete:
  if node in graph.nodes:
    (end_a, end_b), path = collect_path(graph, node)
    assert path.issubset(to_delete), (path, to_delete)
    graph.add_edge(end_a, end_b)
    graph.remove_nodes_from(path)

print(f"Final graph: # Nodes: {len(graph.nodes):,}  # Edges: {len(graph.edges):,}")

print("Saving to disk", time.process_time())
nx.write_adjlist(graph, args.graph_out)

print("Done", time.process_time())

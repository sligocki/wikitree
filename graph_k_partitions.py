"""
Find minimal cycles through a given node in graph.
"""

import argparse
import random

import networkx as nx

import graph_tools
import utils


class BC_DFS_Node:
  """Node in DFS used by biconnected_components()."""
  def __init__(self, node, neighbors, index):
    self.node = node
    self.neighbors = neighbors
    # Minimum index seen by all children of this node.
    self.min_seen = index

  def update_min_seen(self, new_min_seen):
    self.min_seen = min(self.min_seen, new_min_seen)

  def __repr__(self):
    return f"BC_DFS_Node({self.node}, {self.neighbors}, {self.min_seen})"

def articulation_points(graph):
  # Note: This only works for connected graphs.

  # Map of {node -> enum index} for nodes already visited.
  visited = {}
  for start in graph.nodes:
    if start in visited:
      continue

    # Stack of (node, [neighbors of node unexplored])
    todo_stack = [BC_DFS_Node(None, [start], None)]
    # Running index of nodes in order the DFS explores them.
    index = 0
    # List of articulation points to return.
    art_points = set()
    # Number of neighbors of start node we visited from start.
    # If this is > 1 then start node is an articulation point as well.
    num_root_visited = 0
    while True:
      top_node = todo_stack[-1]
      if top_node.neighbors:
        # Continue searching deeper in the DFS.
        child_node_id = top_node.neighbors.pop()
        if child_node_id in visited:
          top_node.update_min_seen(visited[child_node_id])
        else:  # if child_node_id not in visited
          visited[child_node_id] = index
          todo_stack.append(BC_DFS_Node(child_node_id,
                                        list(graph.adj[child_node_id]),
                                        index))
          index += 1
          if top_node.node == start:
            num_root_visited += 1

      else: # if no neighbors left on top of stack.
        # All children of this node have been explored, time to pop up the DFS.
        finished_node = todo_stack.pop()
        parent_node = todo_stack[-1]
        if parent_node.node is None:
          # We finished this connected component.
          if num_root_visited > 1:
            art_points.add(start)
          return art_points

        if (finished_node.min_seen == visited[parent_node.node] and
            parent_node.node != start):
          # If no children of this node ever saw anything smaller than this node's
          # parent, then that parent is an articulation point and all children are a
          # bi-component (or multiple if there are articulation points as children
          # as well).
          art_points.add(parent_node.node)

        # After exploring one branch to exhaustion, update min_seen from parent node.
        parent_node.update_min_seen(finished_node.min_seen)


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("graph")
  args = parser.parse_args()

  utils.log("Loading graph")
  graph = graph_tools.load_graph(args.graph)
  utils.log(f"Initial graph:  # Nodes: {graph.number_of_nodes():_}  # Edges: {graph.number_of_edges():_}")

  art_points = articulation_points(graph)

  utils.log("Articulation points", sorted(art_points))

  utils.log("Done")

if __name__ == "__main__":
  main()

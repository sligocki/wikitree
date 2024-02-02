"""
Estimate nodes with largest neighborhoods.

We estimate neighborhood size as:
  G[node, 0] = 1
  G[node, 1] = degree(node)
  G[node, k] = sum(G[neigh, k-1] - G[node, k-2] for neigh in neighbors_of(node)) + G[node, k-2]

If graph is acyclic, I belive this exactly computes neighborhood sizes.
But for graphs with cycles, this will overcount.
It does especially bad with endogamy (Ex: Acadia).
"""

import argparse
import collections

import graph_tools
import utils


class LayerTracker:
  def __init__(self, graph):
    self.graph = graph
    self.layer_sizes = collections.defaultdict(dict)

  def get_layer_size(self, node, layer):
    if layer > 1:
      return self.layer_sizes[layer][node]
    elif layer == 1:
      return self.graph.degree[node]
    elif layer == 0:
      return 1

  def set_layer_size(self, node, layer, size):
    self.layer_sizes[layer][node] = size

def calc_circle_cum(graph, node, circle_num):
  prev_circle = set([node])
  visited = set([node])
  for _ in range(circle_num):
    next_circle = set()
    for node in prev_circle:
      next_circle |= set(graph.adj[node])
    prev_circle = next_circle - visited
    visited |= prev_circle
  return len(visited)


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("graph")
  parser.add_argument("--max-layers", type=int, default=10)
  parser.add_argument("--print-num", type=int, default=5,
                      help="Number of top nodes to print at each layer.")
  args = parser.parse_args()


  utils.log("Loading graph")
  graph = graph_tools.load_graph(args.graph)
  utils.log(f"Loaded graph:  # Nodes: {graph.number_of_nodes():_}  # Edges: {graph.number_of_edges():_}")

  lt = LayerTracker(graph)
  for layer in range(2, args.max_layers + 1):
    utils.log("Estimating layer", layer)
    for node in graph:
      est_size = sum(lt.get_layer_size(neigh, layer - 1)
                     for neigh in graph.adj[node])
      # Remove the obvious overcounts of node->neigh->node.
      est_size -= lt.get_layer_size(node, layer - 2) * (graph.degree[node] - 1)
      lt.set_layer_size(node, layer, est_size)

    utils.log("Calc Exact sizes for top")
    top_n = utils.TopN(args.print_num)
    num_exact = 0
    for node, est_size in sorted(lt.layer_sizes[layer].items(),
                                 key=lambda x: x[1], reverse=True):
      if top_n.is_full() and est_size < top_n.min_val():
        break
      exact_size = calc_circle_cum(graph, node, layer)
      lt.set_layer_size(node, layer, exact_size)
      top_n.add(exact_size, node)
      num_exact += 1
    utils.log("Num calc exact:", num_exact)

    utils.log(f"Best nodes layer {layer}:")
    for size, node in top_n.items:
      print(f" * {node:40s} : {size:7_d}")

if __name__ == "__main__":
  main()

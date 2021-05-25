"""
Estimate nodes with largest neighborhoods.

We estimate neighborhood size as:
  G[node, 0] = 1
  G[node, 1] = degree(node)
  G[node, k] = sum(G[neigh, k-1] - G[node, k-2] for neigh in neighbors_of(node)) + G[node, k-2]

If graph is acyclic, I belive this exactly computes neighborhood sizes.
But for graphs with cycles, this will eventually overcount.
"""


import argparse

import networkx as nx

import utils


def get_layer_size(graph, node, layer):
  if layer > 1:
    return graph.nodes[node][f"layer_{layer}"]
  elif layer == 1:
    return graph.degree[node]
  elif layer == 0:
    return 1

def set_layer_size(graph, node, layer, size):
  graph.nodes[node][f"layer_{layer}"] = size


parser = argparse.ArgumentParser()
parser.add_argument("graph")
parser.add_argument("--max-layers", type=int, default=10)
parser.add_argument("--print-num", type=int, default=5,
                    help="Number of top nodes to print at each layer.")
args = parser.parse_args()


utils.log("Loading graph")
graph = nx.read_adjlist(args.graph)
utils.log(f"Loaded graph:  # Nodes: {len(graph.nodes):_}  # Edges: {len(graph.edges):_}")

for layer in range(2, args.max_layers + 1):
  utils.log("Evaluating layer", layer)
  top_n = utils.TopN(args.print_num)
  for node in graph.nodes:
    layer_size = sum(get_layer_size(graph, neigh, layer - 1)
                     for neigh in graph.adj[node])
    # Remove the obvious overcounts of node->neigh->node.
    layer_size -= get_layer_size(graph, node, layer - 2) * (graph.degree[node] - 1)
    set_layer_size(graph, node, layer, layer_size)
    top_n.add(layer_size, node)
  utils.log(f"Best nodes layer_{layer}:", top_n.items)

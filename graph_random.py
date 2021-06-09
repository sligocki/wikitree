"""
Produce random graph

Initially, we're only supporting non-preferential attachment (producing
exponential degree distribution). We might extend to other methods later.
"""

import argparse
import collections
import math
import random

import matplotlib.pyplot as plt
import networkx as nx

import utils


def build_exponential(num_nodes, edges_per_node):
  # After adding each node, we repeatedly try adding edges until we fail
  # each time adding an edge with prob_edge chance.
  # So the expected number of edges added (per node) is
  #   prob_edge + prob_edge^2 + prob_edge^3 + ... = prob_edge / (1 - prob_edge)
  # Setting that equal to edges_per_node and re-arranging we get:
  prob_edge = edges_per_node / (1 + edges_per_node)

  graph = nx.Graph()
  for node in range(num_nodes):
    graph.add_node(node)
    # Add edges stochastically
    while random.random() < prob_edge:
      # Use non-preferential attachment:
      #   Pick two end of edge uniformly at random among all nodes.
      node_a = random.randrange(node + 1)
      node_b = random.randrange(node + 1)
      graph.add_edge(node_a, node_b)

  return graph


def degree_distribution(graph):
  degree_counts = collections.Counter()
  for node in graph.nodes():
    degree = graph.degree[node]
    degree_counts[degree] += 1
  return degree_counts


def normalize(ys):
  total = sum(ys)
  return [y / total for y in ys]

def draw_degree_distr(deg_distr):
  fig, ax = plt.subplots()
  # Plot with y-log to see exponential degree distribution as linear.
  ax.set_yscale("log")
  ax.set_ylabel("Fraction of nodes")
  ax.set_xlabel("Degree")

  # Plot degree distribution
  xs = sorted(deg_distr.keys())
  ys = [deg_distr[x] for x in xs]
  ax.plot(xs, normalize(ys), ".-", label = "Degree Distribution")

  # Plot exponential regression line
  sum_deg = sum(ys)
  mean_deg = sum(k * deg_distr[k] for k in xs) / sum_deg
  print("Mean Degree", mean_deg)
  reg_ys = [math.e**(- k / mean_deg) for k in xs]
  ax.plot(xs, normalize(reg_ys), label = "Exponential Regression")

  ax.legend()


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("type", choices=["exponential"])
  parser.add_argument("num_nodes", type=int)
  parser.add_argument("edges_per_node", type=float)
  parser.add_argument("--draw-network", action="store_true")
  args = parser.parse_args()

  utils.log("Building graph")
  graph = build_exponential(num_nodes = args.num_nodes,
                            edges_per_node = args.edges_per_node)

  utils.log("Loading degree distribution")
  deg_distr = degree_distribution(graph)

  utils.log("Loading components")
  components = list(nx.connected_components(graph))

  print(f"# Nodes = {graph.number_of_nodes():_}")
  print(f"# Edges = {graph.number_of_edges():_}")
  print(f"# Components = {len(components):_}")
  print(f"Largest component size = {max(len(c) for c in components):_}")
  print("Degree Distribution", sorted(deg_distr.items()))
  print("Pearson Correlation Coefficient",
        nx.degree_pearson_correlation_coefficient(graph))

  if args.draw_network:
    nx.draw_planar(graph)
    plt.show()

  utils.log("Drawing plots")
  draw_degree_distr(deg_distr)
  plt.show()

if __name__ == "__main__":
  main()

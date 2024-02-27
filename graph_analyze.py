"""
Analyze statistics of a graph.
"""

import argparse
import collections
from collections.abc import Collection, Mapping, MutableMapping
import math
from pathlib import Path
import random

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import networkx as nx
import numpy

import graph_tools
import utils


def degree_distribution(graph : nx.Graph) -> MutableMapping[int, int]:
  degree_counts : collections.Counter[int] = collections.Counter()
  for node in graph.nodes():
    degree = graph.degree[node]
    degree_counts[degree] += 1
  return degree_counts

def bipartite_degree_distribution(graph : nx.Graph
    ) -> tuple[MutableMapping[int, int], MutableMapping[int, int]]:
  person_degree_counts : collections.Counter[int] = collections.Counter()
  family_degree_counts : collections.Counter[int] = collections.Counter()
  for node in graph.nodes():
    degree = graph.degree[node]
    if node.startswith("Union/"):
      family_degree_counts[degree] += 1
    else:
      person_degree_counts[degree] += 1
  return (person_degree_counts, family_degree_counts)

def circle_size(graph : nx.Graph, node, circle_num : int) -> int:
  prev_circle = set([node])
  visited = set([node])
  for _ in range(circle_num):
    next_circle = set()
    for node in prev_circle:
      next_circle |= set(graph.neighbors(node)) - visited
    prev_circle = next_circle
    visited |= prev_circle
  return len(prev_circle)

def circle_distribution(graph : nx.Graph, circle_num : int) -> Mapping[int, int]:
  """Distribution of circle sizes. Circle 1 = # neighbors (degree);
  Circle 2 = # nodes dist 2 away; etc."""
  counts : collections.Counter[int] = collections.Counter()
  for node in graph.nodes():
    size = circle_size(graph, node, circle_num)
    counts[size] += 1
  return counts


def sample_distance_distribution(graph : nx.Graph, num_samples : int) -> Mapping[int, int]:
  attrs = {}
  if graph_tools.is_weighted(graph):
    attrs["weight"] = "weight"

  nodes = list(graph.nodes)
  dist_distr : collections.Counter[int] = collections.Counter()
  for _ in range(num_samples):
    node_a = random.choice(nodes)
    node_b = random.choice(nodes)
    try:
      dist = nx.shortest_path_length(graph, node_a, node_b, **attrs)
      dist_distr[dist] += 1
    except nx.exception.NetworkXNoPath:
      # Ignore unconnected nodes.
      pass
  return dist_distr


def moment_distr(distr : Mapping[int, int], exp : int) -> float:
  return sum(val**exp * count for val, count in distr.items()) / sum(distr.values())

def mean_distr(distr : Mapping[int, int]) -> float:
  return moment_distr(distr, 1)


def normalize(ys : Collection[int]) -> list[float]:
  total = sum(ys)
  return [y / total for y in ys]

def draw_degree_distr_exp(deg_distr : Mapping[int, int], ax,
                          fraction_degree_regression : float) -> None:
  ax.set_title("Degree Distribution")
  ax.set_ylabel("Fraction of nodes")
  ax.set_xlabel("Degree")

  # Plot with y-log to see exponential degree distribution as linear.
  ax.set_yscale("log")

  # Plot degree distribution
  xs = sorted(deg_distr.keys())
  ys = normalize([deg_distr[x] for x in xs])
  ax.plot(xs, ys, ".-", label = "Degree Distribution")

  # Plot exponential regression line
  # Note: We ignore the tail since it can have noise
  cutoff = math.floor(max(xs) * fraction_degree_regression)
  m, b = numpy.polyfit(xs[:cutoff], numpy.log(ys[:cutoff]), deg = 1)
  # ln(y) = m * x + b
  print(f"Exponential regression: ln(y) = {m:f} x + {b:f}")
  reg_ys = [math.e**(m * x + b) for x in xs]
  ax.plot(xs, reg_ys, label = "Exponential Regression")

  ax.legend()

def draw_degree_distr_power(deg_distr : Mapping[int, int], ax,
                            fraction_degree_regression : float) -> None:
  ax.set_title("Degree Distribution")
  ax.set_ylabel("Fraction of nodes")
  ax.set_xlabel("Degree")

  # Plot with y-log to see exponential degree distribution as linear.
  ax.set_yscale("log")
  ax.set_xscale("log")

  # Plot degree distribution
  xs = sorted(deg_distr.keys())
  ys = normalize([deg_distr[x] for x in xs])
  ax.plot(xs, ys, ".-", label = "Degree Distribution")

  # Plot exponential regression line
  # Note: We ignore the tail since it can have noise
  cutoff = math.floor(max(xs) * fraction_degree_regression)
  m, b = numpy.polyfit(numpy.log(xs[:cutoff]), numpy.log(ys[:cutoff]), deg = 1)
  # ln(y) = m * x + b
  print(f"Power regression: ln(y) = {m:f} ln(x) + {b:f}")
  reg_ys = [math.e**(m * math.log(x) + b) for x in xs]
  ax.plot(xs, reg_ys, label = "Power Regression")

  ax.legend()

def draw_distance_distr(dist_distr : Mapping[int, int], ax) -> None:
  ax.set_title("Distance Distribution")
  ax.set_ylabel("Percent of distances")
  ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
  ax.set_xlabel("Distance")

  # Plot distance distribution
  xs = sorted(dist_distr.keys())
  ys = normalize([dist_distr[x] for x in xs])
  ax.plot(xs, ys, ".-", label = "Distance Distribution")

  # # Plot log-normal regression
  # log_distr = {math.log(dist): count for dist, count in dist_distr.items()}
  # mean_log = mean_distr(log_distr)
  # stddev_log = math.sqrt(moment_distr(log_distr, 2) - mean_log**2)
  # reg_ys = [1 / (x * stddev_log * math.sqrt(2 * math.pi)) *
  #           math.e**(-(math.log(x) - mean_log)**2 / (2 * stddev_log**2))
  #           for x in xs]
  # ax.plot(xs, reg_ys, label = "Log-Normal Regression")

  ax.legend()


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("graph", type=Path)
  parser.add_argument("--draw-network", action="store_true")
  parser.add_argument("--draw-plots", action="store_true")
  parser.add_argument("--fraction-degree-regression", type=float, default=0.3,
                      help="Fraction of degrees to consider when doing regression (Starting from smallest degree). Used to ignore outliers")
  parser.add_argument("--num-distance-samples", type=int, default=10_000)
  parser.add_argument("--circle-sizes", type=int, default=1,
                      help="Calculate circle size distribution up to this distance.")
  parser.add_argument("--distances", action="store_true",
                      help="Calculate Distance distribution.")
  parser.add_argument("--correlation", action="store_true",
                      help="Calculate Pearson Correlation Coefficient.")
  parser.add_argument("--components", action="store_true",
                      help="Find largest connected component.")
  parser.add_argument("--bipartite", action="store_true")
  args = parser.parse_args()

  utils.log("Loading graph")
  graph = graph_tools.load_graph(args.graph)

  utils.log(f"# Nodes = {graph.number_of_nodes():_}")
  utils.log(f"# Edges = {graph.number_of_edges():_}")

  if args.draw_network:
    layout = nx.kamada_kawai_layout(graph)
    nx.draw(graph, layout, node_size=100)#, with_labels=True)
    plt.show()

  if args.components:
    utils.log("Loading components")
    components = list(nx.connected_components(graph))
    utils.log(f"# Components = {len(components):_}")
    utils.log(f"Largest component size = {max(len(c) for c in components):_}")

  utils.log("Loading degree distribution")
  if args.bipartite:
    person_deg_distr, family_deg_distr = bipartite_degree_distribution(graph)

    utils.log("Person Nodes:")
    print(person_deg_distr)
    utils.log(" * Mean Degree", mean_distr(person_deg_distr))
    utils.log(" * Second moment (degree)", moment_distr(person_deg_distr, 2))

    utils.log("Family Nodes:")
    print(family_deg_distr)
    utils.log(" * Mean Degree", mean_distr(family_deg_distr))
    utils.log(" * Second moment (degree)", moment_distr(family_deg_distr, 2))
    deg_distr = family_deg_distr

  else:
    deg_distr = degree_distribution(graph)
    print(deg_distr)
    utils.log("Mean Degree", mean_distr(deg_distr))
    utils.log("Second moment (degree)", moment_distr(deg_distr, 2))

  for k in range(2, args.circle_sizes + 1):
    utils.log(f"Loading Circle-{k} size distributions")
    circle_k_distr = circle_distribution(graph, k)
    utils.log(f"Mean Circle-{k} size (z{k})", mean_distr(circle_k_distr))

  if args.correlation:
    utils.log("Calculating correlation")
    utils.log("Pearson Correlation Coefficient",
              nx.degree_pearson_correlation_coefficient(graph))

  if args.distances:
    utils.log(f"Estimating distance distribution with {args.num_distance_samples:_} samples")
    dist_distr = sample_distance_distribution(graph, args.num_distance_samples)
    utils.log("Mean Distance", mean_distr(dist_distr))
    utils.log("Second moment (distance)", moment_distr(dist_distr, 2))

  if args.draw_plots:
    utils.log("Drawing plots")
    fig, (ax1, ax2, ax3) = plt.subplots(3)
    draw_degree_distr_exp(deg_distr, ax1, args.fraction_degree_regression)
    draw_degree_distr_power(deg_distr, ax2, args.fraction_degree_regression)
    draw_distance_distr(dist_distr, ax3)
    plt.show()

  utils.log("Done")

if __name__ == "__main__":
  main()

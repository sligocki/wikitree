"""
Describe the growth of a network over time.
Ex: Examine correllation between a nodes degree and it's chance of gaining an edge.
"""

import argparse
import collections
from pathlib import Path
import pickle

import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx

import graph_analyze
import graph_tools
import utils


def count_degree_changes(old_graph, new_graph):
  nodes_common = set(old_graph.nodes) & set(new_graph.nodes)
  utils.log(f"  Nodes in common: {len(nodes_common):_}")

  # Degree distribution over all `nodes_common`.
  degrees_all = collections.Counter()
  # Degree distribution of nodes that were attached to (edges added, i.e. degree increased).
  degrees_attached = collections.Counter()
  for node in nodes_common:
    # We would like to iterate over all added edges, but since nodes can be
    # "renamed", new edges might not all really be new. So instead we iterate
    # over all nodes that increase in degree (gain meaningful edges).
    old_deg = old_graph.degree[node]
    new_deg = new_graph.degree[node]
    degrees_all[old_deg] += 1
    if new_deg > old_deg:
      # Add 1 for *per* additional edge added.
      # degrees_attached[old_deg] += new_deg - old_deg
      for deg in range(old_deg, new_deg):
        # Instead of treating this as 3 edges added to a degree 2 node, treat it
        # as degree 2 +1 edge, degree 3 +1 edge, degree 4 +1 edge b/c that's
        # what's really happening, we just don't have that fine-grain resolution
        # to know which order they happened in.
        degrees_attached[deg] += 1
  return degrees_all, degrees_attached

def load_degrees(graphs):
  utils.log(f"Running comparison over {len(graphs)} timesteps")

  old_id = graphs[0].parent.name
  old_graph = graph_tools.load_graph(graphs[0])
  utils.log(f"Loaded {graphs[0]}:  # Nodes: {old_graph.number_of_nodes():_}  # Edges: {old_graph.number_of_edges():_}")

  degrees = {}
  attachments = {}
  for new in graphs[1:]:
    new_id = new.parent.name
    new_graph = graph_tools.load_graph(new)
    utils.log(f"Loaded {new}:  # Nodes: {new_graph.number_of_nodes():_}  # Edges: {new_graph.number_of_edges():_}")

    degrees[old_id], attachments[old_id] = count_degree_changes(old_graph, new_graph)
    utils.log(f"  Degree added: {attachments[old_id].total():_}")

    old_id = new_id
    old_graph = new_graph

  return degrees, attachments

def degree_biases(degree_dist, attach_degrees):
  """Return biases vs uniform or preferential attachment."""
  total_deg = sum(degree_dist.values())
  total_deg_pref = sum(d * count for (d, count) in degree_dist.items())
  total_attach = sum(attach_degrees.values())
  bias_unif = {}
  bias_pref = {}
  for n in range(1, 16):
    # Fraction of nodes with this degree
    deg_frac = degree_dist[n] / total_deg
    # Probability of picking a node of this degree using Preferential attachment.
    deg_pref = (n * degree_dist[n]) / total_deg_pref
    # Fraction of attachments to nodes with this degree
    attach_frac = attach_degrees[n] / total_attach
    if deg_frac > 0.0:
      # Bias in attaching to nodes of this degree vs. uniform random attachment
      bias_unif[n] = attach_frac / deg_frac
      # Bias vs. preferential attachment (proportional to degree)
      bias_pref[n] = attach_frac / deg_pref
  return bias_unif, bias_pref


def plot(df, ax, ylabel, ymax):
  params = {
    "xlabel": "Degree",
    "xlim": (0, 15),
    "xticks": range(16),
    "ylabel": ylabel,
    "ylim": (0.0, ymax),
    "grid": True,
    "legend": False,
  }

  # Plot all biases
  df.transpose().plot(ax=ax[0], **params)

  # Plot mean/stddev
  mean = df.mean()
  stddev = df.std()
  mean.plot(ax=ax[1], **params)
  ax[1].fill_between(mean.index, mean + stddev, mean - stddev,
                     color="b", alpha=0.1)


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("graphs", type=Path, nargs="*")
  parser.add_argument("--data", type=Path, default="growth_degrees.pickle")
  args = parser.parse_args()

  if args.graphs:
    degrees, attachments = load_degrees(args.graphs)
    with open(args.data, "wb") as f:
      pickle.dump((degrees, attachments), f)
  else:
    with open(args.data, "rb") as f:
      degrees, attachments = pickle.load(f)

  # Compute biases
  biases_unif = []
  biases_pref = []
  for version in attachments:
    bias_unif, bias_pref = degree_biases(degrees[version], attachments[version])
    biases_unif.append(bias_unif)
    biases_pref.append(bias_pref)
  bias_unif = pd.DataFrame(biases_unif)
  bias_pref = pd.DataFrame(biases_pref)

  fig, axes = plt.subplots(2, 2)
  plot(bias_unif, axes[0], "Bias vs. Uniform", 4.0)
  plot(bias_pref, axes[1], "Bias vs. Preferential", 1.4)
  plt.show()

if __name__ == "__main__":
  main()

#!/usr/bin/env python3

import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy

import graph_analyze
import graph_tools
import utils


def plot_deg_dist_single(deg_dist, ax, type,
                         label = "Degree Distribution",
                         add_legend = True):
  # Set up plot
  ax.set_title(f"{type} Plot")
  ax.set_xlabel("Degree")
  ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
  ax.grid(True)
  if type in ("Log-Linear", "Log-Log"):
    ax.set_yscale("log")
  if type == "Log-Log":
    ax.set_xscale("log")

  # Plot data
  # Ignore outlier degress with only 1-2 nodes representing them.
  xs = [deg for deg in sorted(deg_dist.keys()) if deg_dist[deg] > 2]
  ys = [deg_dist[deg] for deg in xs]
  total_ys = sum(ys)
  ys = [y / total_ys for y in ys]
  ax.plot(xs, ys, ".-", label = label)

  if type == "Log-Linear":
    # Exponential Regression
    m, b = numpy.polyfit(xs, numpy.log(ys), deg = 1)
    reg_ys = [math.e**(m * x + b) for x in xs]
    ax.plot(xs, reg_ys, label = "Exponential Regression", color = "red")
  elif type == "Log-Log":
    # Power regression
    m, b = numpy.polyfit(numpy.log(xs), numpy.log(ys), deg = 1)
    reg_ys = [math.e**b * x**m for x in xs]
    ax.plot(xs, reg_ys, label = "Power Regression", color = "red")

  if add_legend:
    ax.legend(loc = "upper right")

def plot_deg_dist_multi(deg_dist, ax_norm, ax_log, ax_loglog):
  """Plot 3 views of the same degree distribution:
  Linear-Linear, Log-Linear and Log-Log."""
  plot_deg_dist_single(deg_dist, ax_norm, "Linear-Linear")
  plot_deg_dist_single(deg_dist, ax_log, "Log-Linear")
  plot_deg_dist_single(deg_dist, ax_loglog, "Log-Log")

def main():
  # Set up plots (3 plots in one figure for normal, log-y and log-log).
  fig, axes = plt.subplots(4, 3)

  # utils.log("Producing Person Plot")
  # person_dd = graph_analyze.degree_distribution(
  #   graph_tools.load_graph("d/graphs/person/all.adj.nx"))
  # plot_deg_dist_multi(person_dd, *axes[0])

  utils.log("Producing Family Plot")
  family_dd = graph_analyze.degree_distribution(
    graph_tools.load_graph("d/graphs/family/all.adj.nx"))
  plot_deg_dist_multi(family_dd, *axes[1])

  utils.log("Producing Family Bipartite Plot")
  bi_person_dd, bi_family_dd = graph_analyze.bipartite_degree_distribution(
    graph_tools.load_graph("d/graphs/bipartite/all.adj.nx"))
  plot_deg_dist_multi(bi_person_dd, *axes[2])
  # Family nodes with degree 1 are all mistakes. They can only happen if a
  # person is listed as their own parent or married to themselves.
  del bi_family_dd[1]
  plot_deg_dist_multi(bi_family_dd, *axes[3])

  utils.log("Done")

  # fig.set_size_inches(10, 4)
  # fig.tight_layout()
  plt.show()

if __name__ == "__main__":
  main()

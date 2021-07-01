#!/usr/bin/env python3

import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy

import utils


def plot_deg_dist_single(deg_dist, ax, type, label = "Degree Distribution",
                         add_legend = True):
  # Set up plot
  ax.set_xlabel("Degree")
  ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
  ax.grid(True)
  if type in ("Log-Linear", "Log-Log"):
    ax.set_yscale("log")
  if type == "Log-Log":
    ax.set_xscale("log")

  # Plot data
  xs = [deg for deg in range(len(deg_dist)) if deg_dist[deg] > 2]
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

def plot_deg_dist_multi(deg_dist):
  """Plot 3 views of the same degree distribution:
  Linear-Linear, Log-Linear and Log-Log."""
  # Set up plots (3 plots in one figure for normal, log-y and log-log).
  fig, (ax_norm, ax_log, ax_loglog) = plt.subplots(1, 3)
  fig.suptitle("[Placeholder]")
  ax_norm.set_title("Linear-Linear Plot")
  ax_log.set_title("Log-Linear Plot")
  ax_loglog.set_title("Log-Log Plot")

  plot_deg_dist_single(deg_dist, ax_norm, "Linear-Linear")
  plot_deg_dist_single(deg_dist, ax_log, "Log-Linear")
  plot_deg_dist_single(deg_dist, ax_loglog, "Log-Log")

  fig.set_size_inches(10, 4)
  fig.tight_layout()
  return fig


utils.log("Producing Person Plot")
with open("person.deg.json", "r") as f:
  person_deg_dist = json.load(f)["Nodes"]
fig = plot_deg_dist_multi(person_deg_dist)
fig.suptitle("Person Network")
fig.savefig("degrees_person.png")

utils.log("Producing Family Plot")
with open("family.deg.json", "r") as f:
  family_deg_dist = json.load(f)["Nodes"]
fig = plot_deg_dist_multi(family_deg_dist)
fig.suptitle("Family Network")
fig.savefig("degrees_family.png")

utils.log("Producing Family Bipartite Plot")
with open("fam_bi.deg.json", "r") as f:
  bi_data = json.load(f)

fig = plot_deg_dist_multi(bi_data["Person_Nodes"])
fig.suptitle("Bipartite Network (Person Nodes)")
fig.savefig("degrees_bi_person.png")

fig = plot_deg_dist_multi(bi_data["Family_Nodes"])
fig.suptitle("Bipartite Network (Family Nodes)")
fig.savefig("degrees_bi_family.png")

utils.log("Combined Linear Plot")
fig, (ax_person, ax_bipart, ax_family) = plt.subplots(1, 3)
ax_person.set_title("Person Network")
ax_bipart.set_title("Bipartite Network")
ax_family.set_title("Family Network")

plot_deg_dist_single(person_deg_dist, ax_person, "Linear-Linear", add_legend = False)
plot_deg_dist_single(family_deg_dist, ax_family, "Linear-Linear", add_legend = False)
plot_deg_dist_single(bi_data["Person_Nodes"], ax_bipart, "Linear-Linear", "Person Nodes")
plot_deg_dist_single(bi_data["Family_Nodes"], ax_bipart, "Linear-Linear", "Family Nodes")

fig.set_size_inches(10, 4)
fig.tight_layout()
fig.savefig("degrees_combined_linear.png")

utils.log("Done")

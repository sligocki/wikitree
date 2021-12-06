"""
Analyze "complete" profiles. We look at various ways to consider a profile as complete.
"""

import argparse
import collections
import datetime
import math

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy

import data_reader
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
  xs = sorted(deg_dist.keys())
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
    safe_xs = []
    safe_ys = []
    for i, x in enumerate(xs):
      if x > 0:
        safe_xs.append(x)
        safe_ys.append(ys[i])
    m, b = numpy.polyfit(numpy.log(safe_xs), numpy.log(safe_ys), deg = 1)
    reg_ys = [math.e**b * x**m for x in safe_xs]
    ax.plot(safe_xs, reg_ys, label = "Power Regression", color = "red")

  if add_legend:
    ax.legend(loc = "upper right")


parser = argparse.ArgumentParser()
parser.add_argument("--version", help="Data version (defaults to most recent).")
args = parser.parse_args()

db = data_reader.Database(args.version)

# Levels of completeness
people = {}
utils.log("Loading Level 1: Marked no_more_children")
people["no_more_children"] = frozenset(db.enum_people_no_more_children())
utils.log(f"# no_more_children = {len(people['no_more_children']):_}")
utils.log("Loading Level 2: Have both parents linked")
people["both_parents"] = frozenset(p for p in people["no_more_children"]
                                   if len(db.parents_of(p)) == 2)
utils.log(f"# both_parents = {len(people['both_parents']):_}")
utils.log("Loading Level 3: Have birth and death dates")
people["vital_dates"] = frozenset(p for p in people["both_parents"]
                                  if db.age_at_death_of(p) is not None)
utils.log(f"# vital_dates = {len(people['vital_dates']):_}")
utils.log("Loading Level 4: At least one parent is marked no_more_children (so we guess this means no more siblings)")
# This is not exactly correct. Technically, we should require both parents to be
# in people["no_more_children"], but this is a heuristic.
people["no_more_siblings"] = frozenset(p for p in people["vital_dates"]
                                       if db.mother_of(p) in people["no_more_children"]
                                       or db.father_of(p) in people["no_more_children"])
utils.log(f"# no_more_siblings = {len(people['no_more_siblings']):_}")
utils.log("Loading Level 5: Ignore people who died as children, they are over-represented")
year_delta = datetime.timedelta(days = 365.24)
people["not_child"] = frozenset(p for p in people["no_more_siblings"]
                                if db.age_at_death_of(p) > 15 * year_delta)
utils.log(f"# not_child = {len(people['not_child']):_}")


utils.log("Processing degree")
degree_distr = {}
for type in people.keys():
  degree_distr[type] = collections.Counter()
  for person in people[type]:
    degree = len(db.neighbors_of(person))
    degree_distr[type][degree] += 1
    
utils.log("Plotting results")
fig, ax = plt.subplots()
for type in people.keys():
  plot_deg_dist_single(degree_distr[type], ax, "Log-Linear", type)

plt.show()

utils.log("Done")

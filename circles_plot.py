#!/usr/bin/env python3

import argparse
import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

import utils


def mean(xs):
  return sum(xs) / len(xs)

def median_index(circle_sizes):
  total_count = sum(circle_sizes)
  remaining = total_count // 2
  for dist, circle_size in enumerate(circle_sizes):
    remaining -= circle_size
    if remaining < 0:
      return dist


parser = argparse.ArgumentParser()
parser.add_argument("circles_json", nargs="+")
parser.add_argument("--wikitree-ids", nargs="*")

parser.add_argument("--log-y", action="store_true")
parser.add_argument("--rate", action="store_true")
parser.add_argument("--relative", action="store_true",
                    help="Rescale distances relative to median dist.")
parser.add_argument("--log-normal-regression", action="store_true",
                    help="Plot a log-normal distribution regression")

parser.add_argument("--smooth", type=int, default=0,
                    help="Number of points to average around each point for smoothing.")

parser.add_argument("--save-image", type=Path,
                    help="Instead of displaying plot, save it to a file.")
args = parser.parse_args()

utils.log("Loading data")
circle_sizes = {}
for filename in args.circles_json:
  with open(filename, "r") as f:
    circle_sizes.update(json.load(f))


fig, ax = plt.subplots()
# Display parameters
if args.relative:
  ax.set_xlabel("Relative Circle #")
else:
  ax.set_xlabel("Circle #")

if args.rate:
  ax.set_ylabel("Circle Growth Rate")
  # Restrict range so we can actually see the interesting parts
  ax.set_ylim(0, 10)
  ax.set_yticks(range(0, 11, 1))
else:
  ax.set_ylabel("Circle Size (% of population)")
  ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))

if args.log_y:
  ax.set_yscale("log")
  ax.set_ylim(0.000001, 0.1)

ax.grid(True)
ax.set_xticks(range(-200, 200, 10))


utils.log("Plotting Graph")
ids = args.wikitree_ids if args.wikitree_ids else circle_sizes.keys()
for wikitree_id in ids:
  sizes = circle_sizes[wikitree_id]
  xs = list(range(len(sizes)))

  # Normalize distribution
  total_sizes = sum(sizes)
  ys = [y / total_sizes for y in sizes]

  mean_dist = sum(xs[i] * ys[i] for i in range(len(xs)))
  print(f"Mean dist for {wikitree_id}: {mean_dist:.3f}")


  if args.relative:
    median = median_index(sizes)
    xs = [n - median for n in xs]

  if args.smooth:
    ys = [mean(ys[max(i - args.smooth, 0):i + args.smooth + 1]) for i in range(len(ys))]

  if args.rate:
    del xs[0]
    ys = [ys[i+1] / ys[i] if ys[i] else None
          for i in range(len(ys) - 1)]

  ax.plot(xs, ys, label=wikitree_id)

  if args.log_normal_regression:
    count = 0
    total = 0
    total2 = 0
    for dist, this_count in enumerate(sizes):
      if dist > 0:
        count += this_count
        total += math.log(dist) * this_count
        total2 += math.log(dist)**2 * this_count

    mean = total / count
    stddev = math.sqrt(total2 / count - mean**2)

    print("Plotting with regression", mean, stddev)
    # Log-normal only works for positive values!
    xs = [x for x in xs if x > 0]
    # Log-normal PDF
    # See https://en.wikipedia.org/wiki/Log-normal_distribution#Probability_density_function
    ys = [1 / (x * stddev * math.sqrt(2 * math.pi)) *
          math.e**(-(math.log(x) - mean)**2 / (2 * stddev**2))
          for x in xs]

    if args.rate:
      del xs[0]
      ys = [ys[i+1] / ys[i] for i in range(len(ys) - 1)]

    ax.plot(xs, ys, label=f"Regression_{wikitree_id}")

ax.legend()
fig.set_size_inches(8, 8)
if args.save_image:
  fig.savefig(args.save_image)
else:
  plt.show()

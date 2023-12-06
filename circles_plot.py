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
parser.add_argument("circles_json", nargs="+", type=Path)
parser.add_argument("--wikitree-ids", "--ids", nargs="*")
parser.add_argument("--max-plots", type=int, default=20)
parser.add_argument("--max-circle", type=int)

parser.add_argument("--log-y", action="store_true",
                    help="Plot with log-Y axis.")
parser.add_argument("--rate", action="store_true",
                    help="Plot with Y axis as rate of change.")
parser.add_argument("--relative-x", action="store_true",
                    help="Shift distances relative to median dist.")
parser.add_argument("--absolute-y", action="store_true",
                    help="Plot with absolute (not %%) circle sizes.")
parser.add_argument("--cumulative", action="store_true",
                    help="Plot cumulative circle sizes on Y axis.")
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
    data = json.load(f)
    for id, sizes in data.items():
      if id in circle_sizes:
        circle_sizes[f"{id}/{filename.stem}"] = sizes
      else:
        circle_sizes[id] = sizes


fig, ax = plt.subplots()
# Display parameters
if args.relative_x:
  ax.set_xlabel("Relative Circle #")
else:
  ax.set_xlabel("Circle #")

if args.absolute_y:
  y_type = "absolute"
else:
  y_type = "% of population"
  ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))

if args.rate:
  ax.set_ylabel("Circle Growth Rate")

elif args.cumulative:
  ax.set_ylabel(f"Cumulative Circle Size ({y_type})")

else:
  ax.set_ylabel(f"Circle Size ({y_type})")

if args.log_y:
  ax.set_yscale("log")
  if not args.absolute_y:
    ax.set_ylim(0.000001, 1.0)

ax.grid(True)


utils.log("Plotting Graph")
ids = args.wikitree_ids if args.wikitree_ids else list(circle_sizes.keys())[:args.max_plots]
for wikitree_id in ids:
  sizes = circle_sizes[wikitree_id]
  xs = list(range(len(sizes)))
  if args.max_circle:
    xs = [x for x in xs if x <= args.max_circle]
    sizes = [sizes[x] for x in xs]

  total_sizes = sum(sizes)
  print(f"Total population size for {wikitree_id}: {total_sizes:_d}")

  if args.absolute_y:
    ys = [y for y in sizes]
  else:
    # Normalize distribution
    ys = [y / total_sizes for y in sizes]

  mean_dist = sum(xs[i] * ys[i] for i in range(len(xs))) / sum(ys)
  print(f"Mean dist for {wikitree_id}: {mean_dist:.3f}")

  if args.cumulative:
    cum_ys = []
    subtotal = 0
    for y in ys:
      subtotal += y
      cum_ys.append(subtotal)
    ys = cum_ys


  if args.relative_x:
    median = median_index(sizes)
    xs = [n - median for n in xs]

  if args.smooth:
    ys = [mean(ys[max(i - args.smooth, 0):i + args.smooth + 1]) for i in range(len(ys))]

  if args.rate:
    del xs[0]
    ys = [ys[i+1] / ys[i] if ys[i] else None
          for i in range(len(ys) - 1)]
    # Skip c1 / 1 which is always disproportionately large.
    del xs[0], ys[0]

  ax.plot(xs, ys, label=wikitree_id, marker=".")

  if args.log_normal_regression:
    shift_log = 0

    count = 0
    total_log = 0
    total_log2 = 0
    for dist, this_count in enumerate(sizes):
      dist -= shift_log
      if dist > 0:
        count += this_count
        total_log += math.log(dist) * this_count
        total_log2 += math.log(dist)**2 * this_count

    mu_hat = total_log / count
    sigma_hat = math.sqrt(total_log2 / count - mu_hat**2)

    # mu_hat = math.log(19.0)
    # sigma_hat = 0.23
    mean_reg = math.exp(mu_hat + sigma_hat**2 / 2)
    stddev_reg = math.sqrt((math.exp(sigma_hat**2) - 1)) * mean_reg

    print(f"Plotting with regression {mu_hat=:.2f} {sigma_hat=:.2f} {shift_log} mean={mean_reg + shift_log:.1f} stddev={stddev_reg:.1f}")
    # Log-normal only works for positive values!
    reg_xs = [x for x in xs if x > 0]
    # Log-normal PDF
    # See https://en.wikipedia.org/wiki/Log-normal_distribution#Probability_density_function
    sum_ys = sum(ys)
    reg_ys = [sum_ys * 1 / (x * sigma_hat * math.sqrt(2 * math.pi)) *
              math.e**(-(math.log(x) - mu_hat)**2 / (2 * sigma_hat**2))
              for x in reg_xs]
    reg_xs = [x + shift_log for x in reg_xs]

    if args.rate:
      del reg_xs[0]
      reg_ys = [reg_ys[i+1] / reg_ys[i] for i in range(len(ys) - 1)]

    ax.plot(reg_xs, reg_ys, label=f"Regression_{wikitree_id}_{shift_log}")

ax.legend()
fig.set_size_inches(8, 8)
if args.save_image:
  fig.savefig(args.save_image)
else:
  plt.show()

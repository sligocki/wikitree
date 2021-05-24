#!/usr/bin/env python3

import argparse
import json

import matplotlib.pyplot as plt

import utils


def median_index(circle_sizes):
  total_count = sum(circle_sizes)
  remaining = total_count // 2
  for dist, circle_size in enumerate(circle_sizes):
    remaining -= circle_size
    if remaining < 0:
      return dist


parser = argparse.ArgumentParser()
parser.add_argument("circles_json")
parser.add_argument("--log-y", action="store_true")
parser.add_argument("--rate", action="store_true")
parser.add_argument("--relative", action="store_true",
                    help="Rescale distances relative to median dist.")
args = parser.parse_args()

utils.log("Loading data")
with open(args.circles_json, "r") as f:
  circle_sizes = json.load(f)

utils.log("Plotting Graph")
for wikitree_id, sizes in circle_sizes.items():
  xs = list(range(len(sizes)))
  if args.relative:
    median = median_index(sizes)
    xs = [n - median for n in xs]

  ys = sizes
  if args.rate:
    del xs[0]
    ys = [ys[i+1] / ys[i] for i in range(len(ys) - 1)]

  plt.plot(xs, ys, label=wikitree_id)

if args.log_y:
  plt.yscale("log")

plt.legend()
plt.show()

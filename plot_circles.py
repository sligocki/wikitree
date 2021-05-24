#!/usr/bin/env python3

import argparse
import json
from pathlib import Path

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
parser.add_argument("wikitree_ids", nargs="*")
parser.add_argument("--log-y", action="store_true")
parser.add_argument("--rate", action="store_true")
parser.add_argument("--relative", action="store_true",
                    help="Rescale distances relative to median dist.")
parser.add_argument("--save-image", type=Path,
                    help="Instead of displaying plot, save it to a file.")
args = parser.parse_args()

utils.log("Loading data")
with open(args.circles_json, "r") as f:
  circle_sizes = json.load(f)


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
  ax.set_ylabel("Circle Size")

if args.log_y:
  ax.set_yscale("log")
else:
  # matplotlib does not allow plain format for log axis ...
  ax.ticklabel_format(style="plain")

ax.grid(True)
ax.set_xticks(range(-200, 200, 10))


utils.log("Plotting Graph")
ids = args.wikitree_ids if args.wikitree_ids else circle_sizes.keys()
for wikitree_id in ids:
  sizes = circle_sizes[wikitree_id]
  xs = list(range(len(sizes)))
  if args.relative:
    median = median_index(sizes)
    xs = [n - median for n in xs]

  ys = sizes
  if args.rate:
    del xs[0]
    ys = [ys[i+1] / ys[i] for i in range(len(ys) - 1)]

  ax.plot(xs, ys, label=wikitree_id)

ax.legend()
fig.set_size_inches(8, 8)
if args.save_image:
  fig.savefig(args.save_image)
else:
  plt.show()

#!/usr/bin/env python3

import argparse
import datetime
import json
import math
from pathlib import Path
import re

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
parser.add_argument("--max-circle", type=int, default=6)

parser.add_argument("--log-y", action="store_true",
                    help="Plot with log-Y axis.")

parser.add_argument("--save-image", type=Path,
                    help="Instead of displaying plot, save it to a file.")
args = parser.parse_args()

utils.log("Loading data")
circle_sizes = {}
for filename in args.circles_json:
  m = re.fullmatch(r"(\w+-\d+)_(\d+-\d\d-\d\d_\d\d:\d\d).json", filename.name)
  assert m, filename.name
  dt = datetime.datetime.strptime(m.group(2), "%Y-%m-%d_%H:%M")
  with open(filename, "r") as f:
    data = json.load(f)
    for id, sizes in data.items():
      circle_sizes[dt] = sizes


fig, ax = plt.subplots()
# Display parameters
ax.set_xlabel("Time")
ax.set_ylabel("Circle Size (absolute)")

min_date = min(circle_sizes.keys()).date()
max_date = max(circle_sizes.keys()).date()
num_days = (max_date - min_date).days + 1
days = [min_date + datetime.timedelta(days=n) for n in range(num_days + 1)]
day_labels = [day.strftime("%d %b") for day in days]
ax.set_xticks(days, day_labels)

if args.log_y:
  ax.set_yscale("log")

ax.grid(True)


utils.log("Plotting Graph")
xs = sorted(circle_sizes.keys())
for circle_num in range(1, args.max_circle + 1):
  ys = [circle_sizes[x][circle_num] for x in xs]
  ax.plot(xs, ys, label=f"C{circle_num}", marker=".")

ax.legend()
fig.set_size_inches(8, 8)
if args.save_image:
  fig.savefig(args.save_image)
else:
  plt.show()

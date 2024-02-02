"""Load Circles file(s) and list people with max circles of each size."""

import argparse
import json
from pathlib import Path

import utils


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("circles_json", nargs="+", type=Path)
  parser.add_argument("--max-circle", type=int, default=10)
  parser.add_argument("--top-n", "-n", type=int, default=10)
  args = parser.parse_args()

  utils.log("Loading circles")
  circle_sizes = {}
  for filename in args.circles_json:
    with open(filename, "r") as f:
      data = json.load(f)
      for id, sizes in data.items():
        assert id not in circle_sizes, id
        circle_sizes[id] = sizes
  utils.log(f"Loaded circles for {len(circle_sizes)} people")

  utils.log("Finding biggest circles")
  top_n_circle = [utils.TopN(args.top_n) for _ in range(args.max_circle + 1)]
  for id in circle_sizes:
    cum_size = 0
    for circle_num in range(args.max_circle + 1):
      cum_size += circle_sizes[id][circle_num]
      top_n_circle[circle_num].add(cum_size, id)

  utils.log("Listing max circles")
  for circle_num in range(1, args.max_circle + 1):
    print("Circle", circle_num)
    for size, id in top_n_circle[circle_num].items:
      print(f" * {id:40s} : {size:_d}")

if __name__ == "__main__":
  main()

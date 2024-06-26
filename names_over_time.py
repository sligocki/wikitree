# Answer to https://www.wikitree.com/g2g/1735496/frequency-of-new-names-being-added

import argparse

import matplotlib.pyplot as plt
import pandas as pd

import utils


def sequence(start : int, stop : int, count : int) -> list[int]:
  """Return a list of `count` integers from `start` to `stop` inclusive."""
  step = (stop - start) / (count-1)
  return [start + round(n*step) for n in range(count)]

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("--min-per-name", type=int,
                      help="Minimum number of profiles per name to include.")
  parser.add_argument("--version", help="Data version (defaults to most recent).")
  args = parser.parse_args()

  people_file = utils.data_version_dir(args.version) / "people.parquet"
  df = pd.read_parquet(people_file, columns=[
    "wikitree_id", "name_last_birth", "registered_time"])
  utils.log(f"Loaded {len(df):_} rows")

  # Find the earliest registered_time for each name_last_birth
  name_earliest = df.groupby("name_last_birth").agg(
    earliest_date=("registered_time", "min"),
    num_profiles=("wikitree_id", "count"))
  utils.log(f"Found {len(name_earliest):_} unique surnames")

  if args.min_per_name:
    name_earliest = name_earliest.loc[name_earliest.num_profiles >= args.min_per_name]
    utils.log(f"Filtered down to {len(name_earliest):_} surnames with at least {args.min_per_name:_} profiles")

  name_earliest = name_earliest.sort_values("earliest_date")
  utils.log("Calculated earliest registration times with each surname")

  # Plot the number of unique name_last_births over time
  name_earliest["earliest_date"].plot(
    title="WikiTree: New surnames over time",
    xlabel="Surname",
    ylabel="Date of Earliest Profile",
    grid=True,
    rot=45,
    xticks=sequence(0, len(name_earliest) - 1, 20),
  )
  plt.show()


if __name__ == "__main__":
  main()

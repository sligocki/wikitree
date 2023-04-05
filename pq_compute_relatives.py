import argparse

import pandas as pd

import utils


def format_rels(df, column1, column2, relationship):
  return pd.DataFrame({
    "user_num": df[column1],
    "relative_num": df[column2],
    "relationship": relationship,
  })

def compute_relatives(data_dir):
  utils.log("Loading Marriages")
  mar = pd.read_parquet(data_dir / "marriages.parquet")
  mar1 = format_rels(mar, "spouse1", "spouse2", "spouse")
  mar2 = format_rels(mar, "spouse2", "spouse1", "spouse")
  utils.log(f"  Loaded {len(mar1)+len(mar2):_} spouse relationships")

  utils.log("Loading Parents")
  par = pd.read_parquet(data_dir / "people.parquet",
                        columns=["user_num", "mother_num", "father_num"])
  parent1 = format_rels(par, "user_num", "mother_num", "parent")
  parent2 = format_rels(par, "user_num", "father_num", "parent")
  utils.log(f"  Loaded {len(parent1)+len(parent2):_} parent relationships")
  child1 = format_rels(par, "mother_num", "user_num", "child")
  child2 = format_rels(par, "father_num", "user_num", "child")
  utils.log(f"  Loaded {len(child1)+len(child2):_} child relationships")

  # TODO: Compute Spouse & Coparent relationships

  df = pd.concat([mar1, mar2, parent1, parent2, child1, child2],
                 ignore_index=True)
  df = df.dropna()
  utils.log(f"Merged into {len(df):_} total relationships")
  df.to_parquet(data_dir / "relationships.parquet", index=False)
  utils.log(f"Wrote {len(df):_} rows")


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("--version", help="Data version (defaults to most recent).")
  args = parser.parse_args()

  data_dir = utils.data_version_dir(args.version)
  compute_relatives(data_dir)

if __name__ == "__main__":
  main()

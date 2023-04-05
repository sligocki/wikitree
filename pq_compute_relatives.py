import argparse

import pandas as pd

import utils


def format_rels(df, column1, column2, relationship):
  return pd.DataFrame({
    "user_num": df[column1],
    "relative_num": df[column2],
    "relationship": relationship,
  })

def find_common(old, relationship):
  """Return df of distinct user_nums who share the same relative_num.
  Ex: siblings are people who share parents."""
  utils.log(f"Computing {relationship}")
  new = old.merge(old, on="relative_num")
  new = pd.DataFrame({
    "user_num": new.user_num_x,
    "relative_num": new.user_num_y,
    "relationship": relationship,
  })
  utils.log(f"  Merged to {len(new):_} {relationship} relationships")
  new = new.loc[new.user_num != new.relative_num]
  utils.log(f"  Removed self-relationships: {len(new):_} {relationship} relationships")
  new = new.drop_duplicates()
  utils.log(f"  Removed duplicates: {len(new):_} {relationship} relationships")
  return new

def compute_relatives(data_dir):
  utils.log("Loading Marriages")
  mar = pd.read_parquet(data_dir / "marriages.parquet")
  mar1 = format_rels(mar, "spouse1", "spouse2", "spouse")
  mar2 = format_rels(mar, "spouse2", "spouse1", "spouse")
  utils.log(f"  Loaded {len(mar1)+len(mar2):_} spouse relationships")

  utils.log("Loading Parents")
  ppl_df = pd.read_parquet(data_dir / "people.parquet",
                           columns=["user_num", "mother_num", "father_num"])
  parent = pd.concat([
    format_rels(ppl_df, "user_num", "mother_num", "parent"),
    format_rels(ppl_df, "user_num", "father_num", "parent"),
    ], ignore_index=True).dropna()
  utils.log(f"  Loaded {len(parent):_} parent relationships")
  child = pd.concat([
    format_rels(ppl_df, "mother_num", "user_num", "child"),
    format_rels(ppl_df, "father_num", "user_num", "child"),
    ], ignore_index=True).dropna()
  utils.log(f"  Loaded {len(child):_} child relationships")

  sibling = find_common(parent, "sibling")
  utils.log(f"Loaded {len(sibling):_} sibling relationships")

  coparent = find_common(child, "coparent")
  utils.log(f"Loaded {len(coparent):_} coparent relationships")

  df = pd.concat([mar1, mar2, parent, child, sibling, coparent], ignore_index=True)
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

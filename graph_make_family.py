"""
Produces a graph where each node is a "nuclear family unit" (representing
2 parents and all their children or a married couple with no children).

Each family is connected to the childhood family of each of the parents.

Note: We only create family nodes if both parents are known. This means that
this graph does not have the same connectivity as the person or bipartite
graphs. Specifically, if a person married twice, but their parents are unknown,
those families will be unconnected and if only one parent is known, there will
be no connection from children to that one parent's family nodes.

Note: This is similar to the graph created by graph_make_bipartite.py,
but without having person nodes. It is close, but not quite the same as the
"bipartite graph projection" from the bipartite onto the family nodes.
In addition to the difference in connectivity listed above, there are also no
edges directly between a persons multiple marriages (which there would be
in the bipartite projection).

This graph will have drastically fewer cliques than the person graph and
running through graph_core.py will be much more effective.
"""

import argparse
from pathlib import Path

import networkx as nx
import pandas as pd

import graph_tools
import utils


def union_name(a : pd.Series, b : pd.Series) -> pd.Series:
  return "Union/" + a.astype(str) + "/" + b.astype(str)

def union_ids(a : pd.Series, b : pd.Series) -> pd.Series:
  # Create new empty string column where ids will be added.
  ids = pd.Series(index=a.index, dtype=str)

  # Concatenate column values into string ids such that the smaller one is always first.
  sml = (a < b)
  ids[ sml] = union_name(a[ sml], b[ sml])
  ids[~sml] = union_name(b[~sml], a[~sml])

  assert ids.notna().all(), ids
  return ids


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("--version", help="Data version (defaults to most recent).")
  args = parser.parse_args()

  utils.log("Starting")

  data_dir = utils.data_version_dir(args.version)
  graph_dir = data_dir / "graphs" / "family"
  graph_dir.mkdir(parents=True, exist_ok=True)

  couples = pd.read_parquet(data_dir / "rel_couples.parquet")
  utils.log(f"Loaded {len(couples):_} couple relationships")

  people = pd.read_parquet(data_dir / "people.parquet",
                           columns=["user_num", "mother_num", "father_num"],
                           # Support NA parent_nums without coercing to DOUBLE.
                           dtype_backend="numpy_nullable")
  utils.log(f"Loaded {len(people):_} people w/ parent info")

  people = people[people.mother_num.notna() & people.father_num.notna()]
  utils.log(f"Filtered to {len(people):_} people with both parents known")

  # Inner join: Only consider partners where both parents are known.
  df = couples.merge(people, how="inner", on="user_num")
  del couples, people
  utils.log(f"Merged to {len(df):_} rows")

  # TODO: Convert from num to ids?

  df = pd.DataFrame({
    "child_id": union_ids(df.user_num, df.relative_num),
    "parent_id": union_ids(df.mother_num, df.father_num),
  })
  utils.log(f"Converted into {len(df):_} pairs of node ids")

  graph = nx.from_pandas_edgelist(df, "child_id", "parent_id")
  utils.log(f"Built graph with {len(graph.nodes):_} Nodes / {len(graph.edges):_} Edges")

  filename = Path(graph_dir, "all.graph.adj.nx")
  graph_tools.write_graph(graph, filename)
  utils.log(f"Saved graph to {str(filename)}")

  utils.log("Finished")

if __name__ == "__main__":
  main()

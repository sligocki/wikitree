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

def union_single_name(a : pd.Series) -> pd.Series:
  return "Union/" + a.astype(str)

def virtual_parent_name(child : pd.Series) -> pd.Series:
  return "Parents/" + child.astype(str)

def node_ids(a : pd.Series, b : pd.Series) -> pd.Series:
  # Create new empty string column where ids will be added.
  ids = pd.Series(index=a.index, dtype=str)

  # Concatenate column values into string ids such that the smaller one is always first.
  sml = (a < b)
  ids[ sml] = union_name(a[ sml], b[ sml])
  ids[~sml] = union_name(b[~sml], a[~sml])

  assert ids.notna().all(), ids
  return ids


def parent_node_ids(child : pd.Series, p1 : pd.Series, p2 : pd.Series) -> pd.Series:
  # Create new empty string column where ids will be added.
  ids = pd.Series(index=child.index, dtype=str)

  # If both parents known:
  couples = p1.notna() & p2.notna()
  ids[couples] = node_ids(p1[couples], p2[couples])

  # If no parents known:
  orphans = p1.isna() & p2.isna()
  ids[orphans] = virtual_parent_name(child[orphans])

  # If only one parent is known:
  only1 = p1.notna() & p2.isna()
  ids[only1] = union_single_name(p1[only1])
  only2 = p1.isna() & p2.notna()
  ids[only2] = union_single_name(p2[only2])

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
  utils.log(f"Loaded {len(people):_} people")

  people = people[people.mother_num.notna() & people.father_num.notna()]
  utils.log(f"Filtered to {len(people):_} people with both parents known")

  # Inner join: Only consider partners where both parents are known.
  df = couples.merge(people, how="inner", on="user_num")
  del couples, people
  utils.log(f"Merged to {len(df):_} rows")

  df = pd.DataFrame({
    "child_id": node_ids(df.user_num, df.relative_num),
    "parent_id": parent_node_ids(df.user_num, df.father_num, df.mother_num),
  })
  utils.log(f"Converted into {len(df):_} pairs of node ids")

  # TODO: Also connect single-parents to their generic parent node!

  graph = nx.from_pandas_edgelist(df, "child_id", "parent_id")
  utils.log(f"Built graph with {len(graph.nodes):_} Nodes / {len(graph.edges):_} Edges")

  filename = Path(graph_dir, "all.graph.adj.nx")
  graph_tools.write_graph(graph, filename)
  utils.log(f"Saved graph to {str(filename)}")

  utils.log("Finished")

if __name__ == "__main__":
  main()

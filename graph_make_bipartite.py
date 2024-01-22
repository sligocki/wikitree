"""
Produces a graph representing "nuclear family units".

Represented as a bipartite graph where each node is either:
 * a person or
 * a family unit (representing parents and all their children
                  or a married couple with no children)
Every person is connected to every family unit they are a member of.

Note: This is similar to the graph created by graph_make_family.py, see the
comments in that file to understand the difference.

In the traditional person graph, there are many highly connected blocks.
For example, given 2 parents with 4 children, all 6 will be directly connected
to each other. But does this really represent 15 different connections?

Instead, in this representation it would be represented as a star of 6 person
nodes attached to a central family node.

The resulting graph will have drastically fewer cliques and running through
graph_core.py will be much more effective.
"""

import argparse
import collections
from pathlib import Path

import networkx as nx
import pandas as pd

import graph_tools
import utils


def union_name(a : pd.Series, b : pd.Series) -> pd.Series:
  return "Union/" + a.astype(str) + "/" + b.astype(str)

def union_single_name(a : pd.Series) -> pd.Series:
  return "Union/" + a.astype(str)

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
  graph_dir = data_dir / "graphs" / "bipartite"
  graph_dir.mkdir(parents=True, exist_ok=True)

  people = pd.read_parquet(data_dir / "people.parquet",
                           columns=["user_num", "mother_num", "father_num"],
                           # Support NA parent_nums without coercing to DOUBLE.
                           dtype_backend="numpy_nullable")
  utils.log(f"Loaded {len(people):_} people w/ parent info")

  # TODO: Convert from num to ids?

  # Connect all people to their birth family node.

  # People with both parents known:
  complete = people[people.mother_num.notna() & people.father_num.notna()]
  complete = pd.DataFrame({
    "person_id": complete.user_num,
    "family_id": union_ids(complete.mother_num, complete.father_num),
  })

  # People with only one parent known:
  mother_only = people[people.mother_num.notna() & people.father_num.isna()]
  mother_only = pd.concat([
    # Child to family node
    pd.DataFrame({
      "person_id": mother_only.user_num,
      "family_id": union_single_name(mother_only.mother_num),
    }),
    # Parent to family node
    pd.DataFrame({
      "person_id": mother_only.mother_num,
      "family_id": union_single_name(mother_only.mother_num),
    })])
  father_only = people[people.mother_num.isna() & people.father_num.notna()]
  father_only = pd.concat([
    # Child to family node
    pd.DataFrame({
      "person_id": father_only.user_num,
      "family_id": union_single_name(father_only.father_num),
    }),
    # Parent to family node
    pd.DataFrame({
      "person_id": father_only.father_num,
      "family_id": union_single_name(father_only.father_num),
    })])

  child_edges = pd.concat([complete, mother_only, father_only])
  del people, complete, mother_only, father_only
  utils.log(f"Computed {len(child_edges):_} edges to birth family")

  couples = pd.read_parquet(data_dir / "rel_couples.parquet")
  utils.log(f"Loaded {len(couples):_} couple relationships")

  parent_edges = pd.DataFrame({
    "person_id": couples.user_num,
    "family_id": union_ids(couples.user_num, couples.relative_num),
  })
  utils.log(f"Computed {len(parent_edges):_} edges to partner families")

  df = pd.concat([child_edges, parent_edges], ignore_index=True)
  df.to_parquet(graph_dir / "all.edges.parquet")

  graph = nx.from_pandas_edgelist(df, "person_id", "family_id")
  del df, child_edges, parent_edges
  utils.log(f"Built graph with {len(graph.nodes):_} Nodes / {len(graph.edges):_} Edges")

  filename = graph_tools.write_graph(graph, graph_dir / "all")
  utils.log(f"Saved graph to {str(filename)}")

  utils.log("Finished")

if __name__ == "__main__":
  main()

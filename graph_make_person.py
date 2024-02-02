"""
Make person graph.
"""

import argparse

import networkx as nx
import pandas as pd

import graph_tools
import utils


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("--version", help="Data version (defaults to most recent).")
  args = parser.parse_args()

  utils.log("Starting")

  data_dir = utils.data_version_dir(args.version)
  graph_dir = data_dir / "graphs" / "person"
  graph_dir.mkdir(parents=True, exist_ok=True)

  df = pd.read_parquet(data_dir / "rel_all.parquet")
  utils.log(f"Loaded {len(df):_} relationships")

  # TODO: Convert from num to ids?

  graph = nx.from_pandas_edgelist(df, "user_num", "relative_num")
  utils.log(f"Built graph with {len(graph.nodes):_} Nodes / {len(graph.edges):_} Edges")

  basename = graph_dir / "all"
  filename = graph_tools.write_graph(graph, basename)
  utils.log(f"Saved graph to {str(filename)}")

  utils.log("Finished")

if __name__ == "__main__":
  main()

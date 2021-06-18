import argparse
from pathlib import Path
import time

import networkx as nx

import data_reader
import graph_tools
import utils


parser = argparse.ArgumentParser()
parser.add_argument("--version", help="Data version (defaults to most recent).")
args = parser.parse_args()

utils.log("Loading DB")
db = data_reader.Database(args.version)

utils.log("Building graph")
graph = nx.Graph()
i = 0
for person, neigh, rel_type in db.enum_connections():
  # Make sure to avoid "coparent" which is not considered a connection by connection-finder.
  if person < neigh and rel_type in ["child", "parent", "sibling", "spouse"]:
    # Don't add edges twice.
    graph.add_edge(person, neigh)
    i += 1
    if i % 1000000 == 1:
      utils.log(f" ... {i:,} connections loaded")
utils.log(f"Total graph size: {len(graph.nodes):,} Nodes {len(graph.edges):,} Edges.")

utils.log("Writing graph to file")
data_dir = utils.data_version_dir(args.version)
nx.write_adjlist(graph, Path(data_dir, "connection_graph.adj.nx"))

utils.log("Finding largest connected component")
main_subgraph = graph_tools.LargestComponent(graph)
utils.log(f"Main component size: {len(main_subgraph.nodes):,} Nodes {len(main_subgraph.edges):,} Edges.")

utils.log("Writing main component to file")
nx.write_adjlist(main_subgraph, Path(data_dir, "connection_graph.main.adj.nx"))

utils.log("Done")

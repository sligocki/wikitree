"""
Post-process the graph core produced by graph_core.py to:
 1) annotate the edges of the core graph with distances along the original graph
 2) list distances from all removed nodes to their "gateway" core nodes.

With these details, you can recontruct connection distances between core and
non-core nodes.
"""

import argparse
import collections
import csv
from pathlib import Path
import sqlite3

import networkx as nx

import graph_tools
import utils


class DistancesDb:
  def __init__(self, db_filename : Path) -> None:
    self.conn = sqlite3.connect(db_filename)
    self.conn.row_factory = sqlite3.Row
    self.conn.execute("CREATE TABLE distances (node STRING, core_node STRING, dist INTEGER)")

  def add(self, node : str, core_node : str, dist : int) -> None:
    self.conn.execute("INSERT INTO distances VALUES (?, ?, ?)", (node, core_node, dist))

  def commit(self) -> None:
    self.conn.commit()


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("input_full_graph")
  parser.add_argument("input_core_graph")
  parser.add_argument("output_core_graph")
  parser.add_argument("input_removed_nodes_csv")
  parser.add_argument("output_dist_to_core_db")
  args = parser.parse_args()

  utils.log("Creating output DB")
  db = DistancesDb(args.output_dist_to_core_db)

  utils.log("Loading graphs")
  full_graph = graph_tools.load_graph(args.input_full_graph)
  utils.log(f"Loaded full graph:  # Nodes: {len(full_graph.nodes):_}  # Edges: {len(full_graph.edges):_}")
  core_graph = graph_tools.load_graph(args.input_core_graph)
  utils.log(f"Loaded core graph:  # Nodes: {len(core_graph.nodes):_}  # Edges: {len(core_graph.edges):_}")

  utils.log("Loading removed nodes data")
  # Map: removed nodes -> gateway core nodes
  node_to_core = collections.defaultdict(set)
  with open(args.input_removed_nodes_csv, "r") as f:
    csv_in = csv.DictReader(f)
    for row in csv_in:
      node_to_core[row["sub_node"]].add(row["core_node"])
  utils.log(f"Loaded {len(node_to_core):_} removed nodes")
  # Map: core node / pair of core nodes -> removed nodes with that/those as gateway
  core_to_nodes = collections.defaultdict(set)
  for removed_node, core_nodes in node_to_core.items():
    core_to_nodes[frozenset(core_nodes)].add(removed_node)
  del node_to_core
  utils.log(f"Enumerated {len(core_to_nodes):_} gateways")

  max_nodes = 0
  max_gateway = None
  for (gateway, nodes) in core_to_nodes.items():
    if len(nodes) > max_nodes:
      max_nodes = len(nodes)
      max_gateway = gateway
  utils.log(f"Max nodes per gateway {max_nodes:_d} for gateway {max_gateway}")

  utils.log(f"Loading all node to gateway distances for {len(core_to_nodes):_} gateways")
  # Default all edges to distance (weight) 1.
  nx.set_edge_attributes(core_graph, values = 1, name = 'weight')
  max_dist = 0
  max_dist_gateway = None
  for gateway, removed_nodes in core_to_nodes.items():
    # Subgraph of all removed_nodes and the gateway core node itself.
    subgraph = full_graph.subgraph(removed_nodes | gateway)
    # utils.log("Walrus subgraph:", gateway, len(removed_nodes), subgraph.number_of_nodes())
    for core_node in gateway:
      dists_to_core = nx.shortest_path_length(subgraph, core_node)
      # utils.log("Walrus subgraph:", core_node, len(dists_to_core))
      for node, dist in dists_to_core.items():
        if node in gateway:
          if node != core_node:
            # Record shortest distance between two adjacent core nodes.
            core_graph[core_node][node]["weight"] = dist
            if dist > max_dist:
              max_dist = dist
              max_dist_gateway = gateway
        else:
          # node not in gateway
          db.add(node, core_node, dist)
  db.commit()
  utils.log(f"Max core edge distance {max_dist:_d} between nodes {max_dist_gateway}")

  utils.log("Saving graph with weights")
  nx.write_weighted_edgelist(core_graph, args.output_core_graph)

  utils.log("Done")

main()

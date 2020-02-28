"""
Compute centrality of random nodes and save to sqlite DB.
"""

import argparse
import collections
import itertools
import random
import sqlite3
import time

import networkx as nx


parser = argparse.ArgumentParser()
parser.add_argument("graph")
args = parser.parse_args()

conn = sqlite3.connect("data/distances.db", timeout=20)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS distances (graph STRING, node STRING, mean_dist REAL)")

print("Loading graph", time.process_time())
graph = nx.read_adjlist(args.graph)
print(f"Initial graph:  # Nodes: {len(graph.nodes):,}  # Edges: {len(graph.edges):,}", time.process_time())

nodes = list(graph.nodes)
random.shuffle(nodes)

for i, node in enumerate(nodes):
  try:
    print("Node", i, node, time.process_time())
    centrality = nx.closeness_centrality(graph, u=node)
    mean_dist = 1./centrality
    print(f"Centrality\t{node}\t{centrality:.4f}\t{mean_dist:.2f}")

    print("Saving to DB", time.process_time())
    cursor.execute("INSERT INTO distances VALUES (?, ?, ?)",
                   (args.graph, node, mean_dist))
    if i % 10 == 0:
      conn.commit()
  except sqlite3.OperationalError:
    print(" !!! SQLite error !!!")

"""
Compare two graphs
"""

import argparse
from pathlib import Path

import networkx as nx

import graph_tools
import utils


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("graph1", type=Path)
  parser.add_argument("graph2", type=Path)
  args = parser.parse_args()

  g1 = graph_tools.load_graph(args.graph1)
  print(f"Loaded graph1:  # Nodes: {g1.number_of_nodes():_}  # Edges: {g1.number_of_edges():_}")
  g2 = graph_tools.load_graph(args.graph2)
  print(f"Loaded graph2:  # Nodes: {g2.number_of_nodes():_}  # Edges: {g2.number_of_edges():_}")

  n1 = set(g1.nodes)
  n2 = set(g2.nodes)

  nu1 = n1 - n2
  nu2 = n2 - n1
  nc = n1 & n2
  if nu1:
    print(f"Nodes in graph1 not in graph2: {len(nu1):_}")
  if nu2:
    print(f"Nodes in graph2 not in graph1: {len(nu2):_}")
  if nu1 or nu2:
    g1 = g1.subgraph(nc)
    g2 = g2.subgraph(nc)
    print(f"Subsetting graph to common nodes: {len(nc):_}")
    print(f"graph1:  # Nodes: {g1.number_of_nodes():_}  # Edges: {g1.number_of_edges():_}")
    print(f"graph2:  # Nodes: {g2.number_of_nodes():_}  # Edges: {g2.number_of_edges():_}")
  else:
    print(f"All nodes in common: {len(nc):_}")

  e1 = set(frozenset((u, v)) for u, v in g1.edges)
  e2 = set(frozenset((u, v)) for u, v in g2.edges)

  eu1 = e1 - e2
  eu2 = e2 - e1
  ec = e1 & e2
  if eu1:
    print(f"Edges in graph1 not in graph2: {len(eu1):_}")
  if eu2:
    print(f"Edges in graph2 not in graph1: {len(eu2):_}")
  print(f"Edges in common: {len(ec):_}")

  if nu1 or nu2 or eu1 or eu2:
    print("Graphs differ")
  else:
    print("Graphs are identical")

if __name__ == "__main__":
  main()

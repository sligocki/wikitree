import argparse

import networkx as nx

import graph_tools
import utils


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("in_graph")
  parser.add_argument("out_graph")
  args = parser.parse_args()

  utils.log("Reading graph")
  Gnk, names_db = graph_tools.load_graph_nk(args.in_graph)

  utils.log("Converting graph")
  Gnx = nx.Graph()
  for node in Gnk.iterNodes():
    Gnx.add_node(names_db.index2name(node))
  for (node_a, node_b) in Gnk.iterEdges():
    Gnx.add_edge(names_db.index2name(node_a), names_db.index2name(node_b))

  utils.log("Writing graph")
  graph_tools.write_graph(Gnx, args.out_graph)

  utils.log("Finished")

main()

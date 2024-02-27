import argparse
import sqlite3

import networkit as nk

import graph_tools
import utils


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("in_graph")
  parser.add_argument("out_graph")
  args = parser.parse_args()

  utils.log("Reading graph")
  Gnx = graph_tools.load_graph(args.in_graph)

  utils.log("Create node id -> num conversion")
  name2index = {node: index for index, node in enumerate(Gnx)}

  utils.log("Converting graph")
  # Copy directly so we keep track of name2index
  #   Gnk = nk.nxadapter.nx2nk(Gnx)
  Gnk = nk.Graph(Gnx.number_of_nodes())
  for (node_a, node_b) in Gnx.edges:
    Gnk.addEdge(name2index[node_a], name2index[node_b])

  utils.log("Writing graph")
  nk.graphio.writeGraph(Gnk, args.out_graph, nk.Format.METIS)

  utils.log("Writing node names")
  names_db = graph_tools.NamesDb(f"{args.out_graph}.names.db")
  names_db.create_table()
  for node_name, index in name2index.items():
    names_db.insert(index, node_name)
  names_db.commit()

  utils.log("Finished")

main()

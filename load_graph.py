import collections
import csv
import time

import networkx as nx

def load_graph(filename="graph.adj.nx"):
  return nx.read_adjlist(filename)
